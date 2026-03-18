"""ProfileParquetReader: reads 5 oasis_* parquet files for profile tabs.

Provides parquet-sourced data for Skills, Abilities, Knowledge,
Work Activities, and Work Context tabs. Returns CoverageStatus-tagged
results and converts dimension ratings to list-of-dict form for mapper.py.

CRITICAL: All 5 oasis_* files use column `oasis_code` as the lookup key.
Profile codes are like "21211.00" -- NOC code "21211" becomes candidates
["21211.00", "21211.01"].
"""

import logging
from pathlib import Path
from typing import Optional

import pandas as pd

from src.config import JOBFORGE_GOLD_PATH
from src.models.parquet import CoverageStatus, ParquetResult
from src.services.parquet_reader import lookup_profile

logger = logging.getLogger(__name__)

# The lookup column for ALL 5 oasis_* parquet files.
OASIS_CODE_COL = "oasis_code"

# Map tab key -> parquet filename under JOBFORGE_GOLD_PATH.
OASIS_FILES: dict[str, str] = {
    "skills": "oasis_skills.parquet",
    "abilities": "oasis_abilities.parquet",
    "knowledge": "oasis_knowledges.parquet",
    "work_activities": "oasis_workactivities.parquet",
    "work_context": "oasis_workcontext.parquet",
}

# Metadata/infrastructure columns to exclude when extracting dimension ratings.
METADATA_COLS: set[str] = {
    "unit_group_id",
    "noc_element_code",
    "oasis_code",
    "oasis_label",
    "_source_file",
    "_ingested_at",
    "_batch_id",
    "_layer",
}


def noc_to_oasis_code(noc_code: str) -> list[str]:
    """Convert a 5-digit NOC code to candidate oasis_code values.

    Args:
        noc_code: NOC unit group code, e.g. '21211' or '21211.00'.

    Returns:
        List of candidate oasis_code strings, e.g. ['21211.00', '21211.01'].
        Try in order; first non-empty FOUND result wins.
    """
    base = noc_code.split(".")[0]
    return [f"{base}.00", f"{base}.01"]


def get_profile_tab(tab_key: str, oasis_profile_code: str) -> ParquetResult[pd.DataFrame]:
    """Look up a single tab's data for a specific oasis profile code.

    Args:
        tab_key: One of 'skills', 'abilities', 'knowledge',
                 'work_activities', 'work_context'.
        oasis_profile_code: Oasis code like '21211.00'.

    Returns:
        ParquetResult with:
        - LOAD_ERROR if file missing/corrupt (already logged)
        - NOT_FOUND if no row matches oasis_profile_code
        - FOUND with single-row DataFrame in .data on success
    """
    if tab_key not in OASIS_FILES:
        logger.warning("Unknown tab_key '%s'; valid keys: %s", tab_key, list(OASIS_FILES))
        return ParquetResult(
            status=CoverageStatus.LOAD_ERROR,
            error=f"Unknown tab_key: {tab_key}",
        )

    path = Path(JOBFORGE_GOLD_PATH) / OASIS_FILES[tab_key]
    return lookup_profile(path, OASIS_CODE_COL, oasis_profile_code)


def extract_dimension_ratings(df_row: pd.DataFrame, tab_key: str) -> list[dict]:
    """Extract non-zero dimension ratings from a FOUND parquet row.

    Args:
        df_row: DataFrame containing the profile row (1+ rows expected).
        tab_key: Tab key (unused currently, reserved for future filtering).

    Returns:
        List of {'name': str, 'level': int} dicts sorted by level descending.
        Returns empty list when all dimension columns are zero or null.
    """
    ratings = []

    for col in df_row.columns:
        if col in METADATA_COLS:
            continue

        # Take the first row's value (there should only be one row per oasis_code).
        val = df_row[col].iloc[0]

        # Skip null/None.
        if pd.isna(val):
            continue

        try:
            level = int(val)
        except (TypeError, ValueError):
            continue

        if level <= 0:
            continue

        ratings.append({"name": col, "level": level})

    # Sort highest importance first.
    ratings.sort(key=lambda r: r["level"], reverse=True)
    return ratings


def get_all_profile_tabs(noc_code: str) -> dict[str, tuple[list[dict], str]]:
    """Return parquet dimension ratings for all 5 profile tabs.

    For each tab, tries candidate oasis_codes derived from noc_code.
    Falls back to ("oasis") source signal when parquet lookup fails or
    returns empty ratings.

    Args:
        noc_code: NOC unit group code, e.g. '21211'.

    Returns:
        Dict mapping tab_key -> (ratings_list, data_source_str).
        data_source_str is 'jobforge' when parquet data was found,
        'oasis' when the caller should fall back to OASIS scraping.

        Example:
            {
                'skills': ([{'name': 'Reading Comprehension', 'level': 4}, ...], 'jobforge'),
                'abilities': ([], 'oasis'),
                ...
            }
    """
    candidates = noc_to_oasis_code(noc_code)
    result: dict[str, tuple[list[dict], str]] = {}

    for tab_key in OASIS_FILES:
        found_ratings: Optional[list[dict]] = None

        for candidate in candidates:
            tab_result = get_profile_tab(tab_key, candidate)

            if tab_result.status == CoverageStatus.LOAD_ERROR:
                logger.warning(
                    "LOAD_ERROR for tab '%s', noc_code=%s: %s",
                    tab_key, noc_code, tab_result.error,
                )
                # File-level error: no point trying other candidates.
                break

            if tab_result.status == CoverageStatus.NOT_FOUND:
                # Try next candidate (e.g. .01 variant).
                continue

            # Status is FOUND: extract ratings.
            ratings = extract_dimension_ratings(tab_result.data, tab_key)
            if ratings:
                found_ratings = ratings
                break
            # FOUND but all-zero: treat as effectively not found -- fall back to OASIS.

        if found_ratings is not None:
            result[tab_key] = (found_ratings, "jobforge")
        else:
            result[tab_key] = ([], "oasis")

    return result
