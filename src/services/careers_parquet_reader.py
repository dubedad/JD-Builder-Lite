"""CareersParquetReader: reads job_architecture and bridge_caf_ja parquet files
for the DND Civilian Careers site browse experience (L1 + L2 surfaces).

L3 enriched content (overview, training, entry_plans) is still sourced from
careers.sqlite until that data is promoted into the JobForge gold layer.
"""

import logging
import re
from pathlib import Path
from typing import Optional

import pandas as pd

from src.config import JOBFORGE_GOLD_PATH

logger = logging.getLogger(__name__)

_JA_FILE = "job_architecture.parquet"
_CAF_BRIDGE_FILE = "bridge_caf_ja.parquet"

CARD_IMAGE_MAP = {
    "Administrative Support": "administrative-support.webp",
    "Artificial Intelligence Strategy & Integration": "ai-strategy-integration.webp",
    "Data Management": "data-management.webp",
    "Database Administration": "database-administration.png",
    "Electronic Engineering": "electronic-engineering.jpg",
    "Enterprise Architecture": "enterprise-architecture.png",
    "Food Services": "food-services.jpg",
    "Information and Data Architecture": "information-data-architecture.jpg",
    "Innovation and Change Management": "innovation-change-management.jpg",
    "Nursing": "nursing.jpg",
    "Organizational Design and Classification": "organizational-design-classification.jpg",
    "Project Management": "project-management.jpg",
    "Artificial Intelligence Strategy and Integration": "ai-strategy-integration.webp",
}


def _slugify(text: str) -> str:
    """Convert a display name to a URL-safe slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text


class CareersParquetReader:
    """Reads JobForge gold parquet files for the careers browse experience."""

    def __init__(self) -> None:
        self._ja_df: Optional[pd.DataFrame] = None
        self._bridge_df: Optional[pd.DataFrame] = None
        self._loaded: bool = False
        self._load_failed: bool = False

    def _load(self) -> bool:
        if self._loaded:
            return True
        if self._load_failed:
            return False

        gold = Path(JOBFORGE_GOLD_PATH)

        try:
            self._ja_df = pd.read_parquet(gold / _JA_FILE)
            logger.info("CareersParquetReader: loaded %d job titles", len(self._ja_df))
        except Exception as e:
            logger.error("CareersParquetReader: failed to load %s — %s", _JA_FILE, e)
            self._load_failed = True
            return False

        try:
            self._bridge_df = pd.read_parquet(gold / _CAF_BRIDGE_FILE)
            logger.info("CareersParquetReader: loaded %d CAF bridge rows", len(self._bridge_df))
        except Exception as e:
            logger.warning("CareersParquetReader: CAF bridge unavailable — %s", e)
            self._bridge_df = None

        self._loaded = True
        return True

    def get_families(self) -> list[dict]:
        """Return one record per job family for the L1 card grid.

        Each record has: name, slug, function, image_file (or None).
        """
        if not self._load():
            return []

        df = self._ja_df.copy()
        df = df[df["job_family_en"].notna() & (df["job_family_en"] != "")]

        seen = {}
        for _, row in df.iterrows():
            family = str(row["job_family_en"]).strip()
            if family in seen:
                continue
            seen[family] = {
                "name": family,
                "slug": _slugify(family),
                "function": str(row.get("job_function_en") or "").strip(),
                "image_file": CARD_IMAGE_MAP.get(family),
            }

        return sorted(seen.values(), key=lambda r: r["name"])

    def get_job_functions(self) -> list[str]:
        """Return sorted list of unique job function names."""
        if not self._load():
            return []
        fns = self._ja_df["job_function_en"].dropna().unique().tolist()
        return sorted(str(f).strip() for f in fns if str(f).strip())

    def get_titles_by_family_slug(self) -> dict[str, list[str]]:
        """Return mapping of family_slug -> list of lowercase job titles (for search)."""
        if not self._load():
            return {}

        result: dict[str, list[str]] = {}
        for _, row in self._ja_df.iterrows():
            family = str(row.get("job_family_en") or "").strip()
            title = str(row.get("job_title_en") or "").strip()
            if not family or not title:
                continue
            slug = _slugify(family)
            result.setdefault(slug, []).append(title.lower())
        return result

    def get_jobs_for_family(self, family_slug: str) -> tuple[Optional[str], list[dict]]:
        """Return (family_name, jobs) for the L2 family page.

        Each job has: title, slug, noc_uid, noc_title, managerial_level, digital, excerpt.
        Returns (None, []) if family_slug not found.
        """
        if not self._load():
            return None, []

        df = self._ja_df.copy()
        df = df[df["job_family_en"].notna()]
        df["_slug"] = df["job_family_en"].apply(lambda x: _slugify(str(x)))
        matches = df[df["_slug"] == family_slug]

        if matches.empty:
            return None, []

        family_name = str(matches.iloc[0]["job_family_en"]).strip()
        jobs = []
        for _, row in matches.sort_values("job_title_en").iterrows():
            title = str(row.get("job_title_en") or "").strip()
            noc_uid = row.get("noc_2021_uid")
            noc_uid_str = str(int(float(noc_uid))).zfill(5) if pd.notna(noc_uid) else None
            jobs.append({
                "title": title,
                "slug": _slugify(title),
                "noc_uid": noc_uid_str,
                "noc_title": str(row.get("noc_2021_title") or "").strip(),
                "managerial_level": str(row.get("managerial_level_en") or "").strip(),
                "digital": None,
                "excerpt": "",
            })

        return family_name, jobs

    def get_job_by_title_slug(self, title_slug: str) -> Optional[dict]:
        """Return basic job record for the L3 detail page (structure only).

        Enriched content (overview, training, etc.) must be joined from careers.sqlite.
        Returns None if not found.
        """
        if not self._load():
            return None

        df = self._ja_df.copy()
        df = df[df["job_title_en"].notna()]
        df["_slug"] = df["job_title_en"].apply(lambda x: _slugify(str(x)))
        matches = df[df["_slug"] == title_slug]

        if matches.empty:
            return None

        row = matches.iloc[0]
        family = str(row.get("job_family_en") or "").strip()
        noc_uid = row.get("noc_2021_uid")
        noc_uid_str = str(int(float(noc_uid))).zfill(5) if pd.notna(noc_uid) else None

        caf_slugs = []
        if self._bridge_df is not None:
            jt_id = row.get("jt_id")
            if pd.notna(jt_id):
                bridge_matches = self._bridge_df[
                    self._bridge_df["ja_job_title_id"] == int(jt_id)
                ]
                caf_slugs = bridge_matches["caf_occupation_id"].dropna().tolist()

        return {
            "title":            str(row.get("job_title_en") or "").strip(),
            "slug":             title_slug,
            "family":           family,
            "family_slug":      _slugify(family),
            "function":         str(row.get("job_function_en") or "").strip(),
            "managerial_level": str(row.get("managerial_level_en") or "").strip(),
            "noc_uid":          noc_uid_str,
            "noc_title":        str(row.get("noc_2021_title") or "").strip(),
            "digital":          None,
            "overview":         "",
            "training":         "",
            "entry_plans":      "",
            "part_time":        "",
            "caf_slugs":        caf_slugs,
            "related_raw":      [],
        }


careers_parquet_reader = CareersParquetReader()
