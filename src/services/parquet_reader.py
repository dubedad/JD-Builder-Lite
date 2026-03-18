"""Parquet reader service with CoverageStatus error handling.

Wraps pandas read_parquet with three-state error handling (LOAD_ERROR,
NOT_FOUND, FOUND) and warning logging on every failure path.
"""

import logging
from pathlib import Path
from typing import Optional

import pandas as pd

from src.models.parquet import CoverageStatus, ParquetResult

logger = logging.getLogger(__name__)

# Module-level cache: path string -> DataFrame. Loaded once per process.
_cache: dict[str, pd.DataFrame] = {}


def read_parquet_safe(path: Path) -> ParquetResult[pd.DataFrame]:
    """Read a parquet file safely, returning a CoverageStatus-tagged result.

    On success the DataFrame is cached by path so subsequent calls skip disk
    I/O. Column names are stripped of surrounding whitespace at read time.

    Args:
        path: Absolute or relative path to the parquet file.

    Returns:
        ParquetResult with status FOUND (and DataFrame in .data) on success,
        or LOAD_ERROR (with .error message) if the file is missing or corrupt.
    """
    path_key = str(path)

    if path_key in _cache:
        return ParquetResult(status=CoverageStatus.FOUND, data=_cache[path_key])

    if not path.exists():
        logger.warning("Parquet file not found: %s", path)
        return ParquetResult(
            status=CoverageStatus.LOAD_ERROR,
            error=f"File not found: {path}",
        )

    try:
        df = pd.read_parquet(path)
    except Exception as e:
        logger.warning("Failed to read parquet file %s: %s", path, str(e))
        return ParquetResult(
            status=CoverageStatus.LOAD_ERROR,
            error=str(e),
        )

    # Strip whitespace from all column names once at read time.
    df.columns = df.columns.str.strip()

    _cache[path_key] = df
    return ParquetResult(status=CoverageStatus.FOUND, data=df)


def lookup_profile(
    path: Path,
    code_col: str,
    profile_code: str,
    data_cols: Optional[list[str]] = None,
) -> ParquetResult[pd.DataFrame]:
    """Look up rows for a specific profile code in a parquet file.

    Args:
        path: Path to the parquet file.
        code_col: Name of the column containing profile codes.
        profile_code: The profile code to look up.
        data_cols: Optional list of column names to return; all columns
                   returned when None.

    Returns:
        ParquetResult with:
        - LOAD_ERROR if the file cannot be read (propagated from read_parquet_safe)
        - NOT_FOUND if the file loaded but no rows match profile_code
        - FOUND with matching rows in .data on success
    """
    read_result = read_parquet_safe(path)

    if read_result.status != CoverageStatus.FOUND:
        # Propagate LOAD_ERROR (already logged by read_parquet_safe).
        return read_result

    df = read_result.data
    matches = df[df[code_col] == profile_code]

    if matches.empty:
        logger.warning(
            "Profile %s not found in %s (column: %s)",
            profile_code,
            path.name,
            code_col,
        )
        return ParquetResult(
            status=CoverageStatus.NOT_FOUND,
            error=f"Profile {profile_code} not found in {path.name}",
        )

    if data_cols is not None:
        matches = matches[data_cols]

    return ParquetResult(status=CoverageStatus.FOUND, data=matches)
