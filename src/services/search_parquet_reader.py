"""SearchParquetReader: sub-second parquet search with five-tier relevance scoring.

Reads three gold parquet files (element_labels, element_lead_statement,
element_example_titles) and applies tiered relevance scoring to return a
list of EnrichedSearchResult.

Return semantics:
  None  -> any parquet file failed to load (triggers OASIS fallback in route)
  []    -> files loaded but query matches nothing (also triggers fallback)
  list  -> matches found, sorted by relevance_score descending

Satisfies SRCH-01 (sub-second parquet search) and SRCH-02 (tiered scoring).
"""

import logging
import re
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

from src.config import JOBFORGE_GOLD_PATH, OASIS_BASE_URL, OASIS_VERSION
from src.models.noc import BROAD_CATEGORIES, EnrichedSearchResult
from src.models.parquet import CoverageStatus
from src.services.parquet_reader import read_parquet_safe

logger = logging.getLogger(__name__)

_LABELS_FILE = "element_labels.parquet"
_LEAD_FILE = "element_lead_statement.parquet"
_TITLES_FILE = "element_example_titles.parquet"


def _stem_word(word: str) -> str:
    """Strip common English suffixes for fuzzy matching.

    Mirrors the logic in src/routes/api.py so parquet and OASIS searches
    produce consistent stem-based scoring.

    Example: "engineers" -> "engineer", "printing" -> "print"
    """
    stemmed = re.sub(r"(ers?|ing|tion|ment|ed|ly|s)$", "", word, count=1)
    return stemmed if len(stemmed) >= 3 else word


def _normalize_plural(text: str) -> str:
    """Normalize plural suffixes for near-exact title comparison.

    Mirrors the logic in src/routes/api.py.
    Example: "software engineers" -> "software engineer"
    """
    words = text.lower().split()
    out = []
    for w in words:
        if w.endswith("ies") and len(w) > 4:
            out.append(w[:-3] + "y")
        elif w.endswith("es") and len(w) > 3:
            out.append(w[:-2])
        elif w.endswith("s") and len(w) > 2 and not w.endswith("ss"):
            out.append(w[:-1])
        else:
            out.append(w)
    return " ".join(out)


class SearchParquetReader:
    """Search across gold parquet files with five-tier relevance scoring.

    Tier  Score  Condition
    ----  -----  ---------
    Code   100   query matches unit_group_id exactly (code search path)
    T1     100   normalized query == normalized Label (near-exact title)
    T2      95   query is substring of Label (title contains query)
    T3      90   stemmed query appears in Label (stem in title)
    T4      80   query or stem appears in any example Job title text
    T5      50   query or stem appears in Lead statement

    Returns None when any parquet file is unavailable (triggers OASIS
    fallback). Returns [] when files load but nothing matches (also
    triggers fallback). Returns list[EnrichedSearchResult] on match.
    """

    def __init__(self) -> None:
        self._labels_df: Optional[pd.DataFrame] = None
        self._lead_df: Optional[pd.DataFrame] = None
        self._titles_df: Optional[pd.DataFrame] = None
        self._loaded: bool = False
        self._load_failed: bool = False

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_parquets(self) -> bool:
        """Load all three parquet files. Returns True on success.

        Results are cached in instance variables. If any file fails,
        sets _load_failed=True and returns False.
        """
        if self._loaded:
            return True
        if self._load_failed:
            return False

        gold = Path(JOBFORGE_GOLD_PATH)

        labels_result = read_parquet_safe(gold / _LABELS_FILE)
        if labels_result.status == CoverageStatus.LOAD_ERROR:
            logger.warning(
                "SearchParquetReader: %s unavailable — %s",
                _LABELS_FILE,
                labels_result.error,
            )
            self._load_failed = True
            return False

        lead_result = read_parquet_safe(gold / _LEAD_FILE)
        if lead_result.status == CoverageStatus.LOAD_ERROR:
            logger.warning(
                "SearchParquetReader: %s unavailable — %s",
                _LEAD_FILE,
                lead_result.error,
            )
            self._load_failed = True
            return False

        titles_result = read_parquet_safe(gold / _TITLES_FILE)
        if titles_result.status == CoverageStatus.LOAD_ERROR:
            logger.warning(
                "SearchParquetReader: %s unavailable — %s",
                _TITLES_FILE,
                titles_result.error,
            )
            self._load_failed = True
            return False

        self._labels_df = labels_result.data
        self._lead_df = lead_result.data
        self._titles_df = titles_result.data
        self._loaded = True
        return True

    def _build_result(
        self,
        row: pd.Series,
        score: int,
        reason: str,
        lead_map: dict[str, str],
    ) -> EnrichedSearchResult:
        """Construct an EnrichedSearchResult from a labels DataFrame row."""
        noc_code = str(row["unit_group_id"])
        title = str(row["Label"])
        url = (
            f"{OASIS_BASE_URL}/OASIS/OASISOccProfile"
            f"?code={noc_code}.00&version={OASIS_VERSION}"
        )
        lead_statement = lead_map.get(noc_code)

        broad_category: Optional[int] = None
        broad_category_name: Optional[str] = None
        if noc_code:
            try:
                cat_digit = int(noc_code[0])
                broad_category = cat_digit
                broad_category_name = BROAD_CATEGORIES.get(cat_digit)
            except (ValueError, IndexError):
                pass

        sub_major_group = noc_code[:3] if len(noc_code) >= 3 else None
        unit_group = noc_code[:4] if len(noc_code) >= 4 else None

        return EnrichedSearchResult(
            noc_code=noc_code,
            title=title,
            url=url,
            lead_statement=lead_statement,
            broad_category=broad_category,
            broad_category_name=broad_category_name,
            sub_major_group=sub_major_group,
            unit_group=unit_group,
            relevance_score=score,
            match_reason=reason,
        )

    # ------------------------------------------------------------------
    # Public search interface
    # ------------------------------------------------------------------

    def search(
        self, query: str, search_type: str = "Keyword"
    ) -> Optional[list[EnrichedSearchResult]]:
        """Search parquet files and return scored results.

        Args:
            query: User-supplied search query (keyword string or 5-digit code).
            search_type: "Keyword" (default) or "Code".

        Returns:
            None  if any parquet file could not be loaded.
            []    if files loaded but no rows matched the query.
            list  of EnrichedSearchResult sorted by relevance_score desc.
        """
        try:
            return self._search_impl(query, search_type)
        except Exception:
            logger.warning(
                "SearchParquetReader.search() raised unexpectedly for query=%r",
                query,
                exc_info=True,
            )
            return None

    def _search_impl(
        self, query: str, search_type: str
    ) -> Optional[list[EnrichedSearchResult]]:
        """Core search logic. Exceptions propagate to search() which catches them."""
        if not self._load_parquets():
            return None

        labels_df = self._labels_df
        lead_df = self._lead_df
        titles_df = self._titles_df

        # Build a lead statement lookup dict once: noc_code -> lead text
        lead_map: dict[str, str] = {}
        for _, row in lead_df.iterrows():
            lead_map[str(row["unit_group_id"])] = str(row.get("Lead statement", "") or "")

        # ------------------------------------------------------------------
        # Code search path: exact 5-digit NOC code match
        # ------------------------------------------------------------------
        if search_type == "Code" or re.match(r"^\d{5}$", query.strip()):
            code = query.strip()
            matches = labels_df[labels_df["unit_group_id"] == code]
            if matches.empty:
                return []
            row = matches.iloc[0]
            result = self._build_result(
                row,
                score=100,
                reason=f"Exact NOC code: {code}",
                lead_map=lead_map,
            )
            return [result]

        # ------------------------------------------------------------------
        # Keyword search path: five-tier vectorized scoring
        # ------------------------------------------------------------------
        query_lower = query.strip().lower()
        query_stems = [_stem_word(w) for w in query_lower.split()]
        query_stem = " ".join(query_stems)
        query_norm = _normalize_plural(query_lower)

        # Build working DataFrame fresh (avoids pandas chained-assignment warnings).
        title_lower_series = labels_df["Label"].str.lower().fillna("")
        working = pd.DataFrame(
            {
                "unit_group_id": labels_df["unit_group_id"].values,
                "Label": labels_df["Label"].values,
                "_title_lower": title_lower_series.values,
                "_title_norm": title_lower_series.apply(_normalize_plural).values,
            }
        )

        # Vectorized tier masks (T1, T2, T3)
        mask_t1 = working["_title_norm"] == query_norm
        mask_t2 = (~mask_t1) & working["_title_lower"].str.contains(
            re.escape(query_lower), na=False
        )

        # T3: query_stem as phrase OR any individual stem appears in title
        mask_t3_phrase = working["_title_lower"].str.contains(
            re.escape(query_stem), na=False
        )
        mask_t3_any = working["_title_lower"].apply(
            lambda t: any(s in t for s in query_stems)
        )
        mask_t3 = (~mask_t1) & (~mask_t2) & (mask_t3_phrase | mask_t3_any)

        # Assign scores array
        scores = np.zeros(len(working), dtype=int)
        reasons = np.empty(len(working), dtype=object)

        scores[mask_t1.values] = 100
        reasons[mask_t1.values] = f'Exact title match: "{query}"'

        scores[mask_t2.values] = 95
        reasons[mask_t2.values] = f'Title contains "{query}"'

        scores[mask_t3.values] = 90
        reasons[mask_t3.values] = f'Title contains stem of "{query}"'

        # T4: example job title match (score 80)
        # Build a set of unit_group_ids whose example titles match.
        jt_lower_series = titles_df["Job title text"].str.lower().fillna("")
        titles_working = pd.DataFrame(
            {
                "unit_group_id": titles_df["unit_group_id"].values,
                "_jt_lower": jt_lower_series.values,
            }
        )
        t4_phrase = titles_working["_jt_lower"].str.contains(
            re.escape(query_lower), na=False
        )
        t4_stem = titles_working["_jt_lower"].apply(
            lambda t: any(s in t for s in query_stems)
        )
        t4_matched_ids = set(
            titles_working.loc[t4_phrase | t4_stem, "unit_group_id"].astype(str)
        )

        if t4_matched_ids:
            mask_t4_candidates = (
                working["unit_group_id"].astype(str).isin(t4_matched_ids)
            )
            # Only apply T4 to rows that haven't scored yet
            mask_t4 = mask_t4_candidates & (scores == 0)
            scores[mask_t4.values] = 80
            reasons[mask_t4.values] = f'Example title contains "{query}"'

        # T5: lead statement match (score 50)
        lead_series = working["unit_group_id"].astype(str).map(lead_map).fillna("")
        lead_lower = lead_series.str.lower()
        t5_phrase = lead_lower.str.contains(re.escape(query_lower), na=False)
        t5_stem = lead_lower.apply(lambda t: any(s in t for s in query_stems))
        mask_t5 = (t5_phrase | t5_stem) & (scores == 0)
        scores[mask_t5.values] = 50
        reasons[mask_t5.values] = f'Lead statement mentions "{query}"'

        # Assign scores/reasons as new Series to avoid chained-assignment warnings.
        working = working.assign(_score=scores, _reason=reasons)

        # Filter to rows that matched any tier
        matched = working[working["_score"] > 0].copy()

        if matched.empty:
            return []

        # Sort by score descending
        matched = matched.sort_values("_score", ascending=False)

        # Build result objects
        results: list[EnrichedSearchResult] = []
        for _, row in matched.iterrows():
            full_row = labels_df[
                labels_df["unit_group_id"] == row["unit_group_id"]
            ].iloc[0]
            result = self._build_result(
                full_row,
                score=int(row["_score"]),
                reason=str(row["_reason"]),
                lead_map=lead_map,
            )
            results.append(result)

        return results


# Module-level singleton — imported directly by api.py in Plan 02.
search_parquet_reader = SearchParquetReader()
