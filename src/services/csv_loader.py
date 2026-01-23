"""OASIS guide.csv loader with O(1) lookups and category mapping."""

import csv
import logging
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Maps JD Element names (used in code) to guide.csv category values
CATEGORY_MAPPING = {
    # JD Element name -> guide.csv category value
    "key_activities": "Work Activities",
    "work_activities": "Work Activities",
    "skills": "Skills",
    "abilities": "Abilities",
    "knowledge": "Knowledge",
    "effort": "Work Context",           # Work Context contains effort items
    "responsibility": "Work Context",   # Work Context contains responsibility items
    "working_conditions": "Work Context",
    "work_context": "Work Context",
    "personal_attributes": "Personal Attributes",
}

# OASIS scale meanings from official documentation
# Source: https://open.canada.ca/data/en/dataset/eeb3e442-9f19-4d12-8b38-c488fe4f6e5e
SCALE_MEANINGS = {
    "skills": {
        1: "1 - Lowest Level",
        2: "2 - Low Level",
        3: "3 - Moderate Level",
        4: "4 - High Level",
        5: "5 - Highest Level",
        "max": 5,
        "dimension": "Proficiency"
    },
    "abilities": {
        1: "1 - Lowest Level",
        2: "2 - Low Level",
        3: "3 - Moderate Level",
        4: "4 - High Level",
        5: "5 - Highest Level",
        "max": 5,
        "dimension": "Proficiency"
    },
    "knowledge": {
        1: "1 - Basic",
        2: "2 - Intermediate",
        3: "3 - Advanced",
        "max": 3,
        "dimension": "Knowledge Level"
    },
    "work_activities": {
        1: "1 - Lowest Complexity",
        2: "2 - Low Complexity",
        3: "3 - Moderate Complexity",
        4: "4 - High Complexity",
        5: "5 - Highest Complexity",
        "max": 5,
        "dimension": "Complexity"
    },
    "personal_attributes": {
        1: "1 - Lowest Importance",
        2: "2 - Low Importance",
        3: "3 - Moderate Importance",
        4: "4 - High Importance",
        5: "5 - Highest Importance",
        "max": 5,
        "dimension": "Importance"
    },
    # Work Context dimension-specific scales
    "work_context_frequency": {
        1: "Once a year or more but not every month",
        2: "Once a month or more but not every week",
        3: "Once a week or more but not every day",
        4: "Every day, a few times per day",
        5: "Every day, many times per day",
        "max": 5,
        "dimension": "Frequency"
    },
    "work_context_duration": {
        1: "Very little time",
        2: "Less than half the time",
        3: "About half the time",
        4: "More than half the time",
        5: "All the time, or almost all the time",
        "max": 5,
        "dimension": "Duration"
    }
}

# NOC TEER (Training, Education, Experience, Responsibilities) categories
# Source: https://noc.esdc.gc.ca/Structure/Matrix
TEER_CATEGORIES = {
    0: "Management occupations",
    1: "University degree usually required",
    2: "College diploma or apprenticeship (2+ years), or supervisory",
    3: "College diploma or apprenticeship (<2 years), or 6+ months training",
    4: "High school diploma or several weeks training",
    5: "Short-term work demonstration, no formal education"
}


class GuideCSVLoader:
    """Singleton CSV loader with O(1) lookups for OASIS guide data."""

    def __init__(self):
        """Initialize empty lookup dicts and stats."""
        self._by_element_id: Dict[str, dict] = {}
        self._by_title: Dict[str, dict] = {}
        self._loaded_at: Optional[str] = None
        self._stats = {
            "id_matches": 0,
            "title_fallbacks": 0,
            "missing": 0
        }

    def load(self, path: Path):
        """Load CSV with utf-8-sig encoding (handles Windows BOM).

        Args:
            path: Path to guide.csv file
        """
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)

            # Log column names for debugging
            columns = reader.fieldnames or []
            logger.info(f"Loading guide.csv with columns: {columns}")

            # Check for expected columns
            expected = {"element_id", "title", "description", "category", "category_definition"}
            missing = expected - set(columns)
            if missing:
                logger.warning(f"Expected columns missing from guide.csv: {missing}")

            # Build lookup dictionaries
            for row in reader:
                element_id = row.get("element_id", "").strip()
                title = row.get("title", "").strip()

                if element_id:
                    self._by_element_id[element_id] = row
                if title:
                    # Case-insensitive title lookup
                    self._by_title[title.lower()] = row

            self._loaded_at = datetime.utcnow().isoformat()
            logger.info(f"Loaded {len(self._by_element_id)} elements from guide.csv")

    def lookup(self, element_id: str = None, title: str = None) -> Optional[dict]:
        """Lookup by element_id (primary) or title (fallback).

        Args:
            element_id: OASIS element ID (e.g., "1.A.1")
            title: Element title for fallback lookup

        Returns:
            Row dict with all CSV columns, or None if not found
        """
        # Try element_id first (primary key)
        if element_id and element_id in self._by_element_id:
            self._stats["id_matches"] += 1
            return self._by_element_id[element_id]

        # Fallback to title (case-insensitive)
        if title and title.lower() in self._by_title:
            self._stats["title_fallbacks"] += 1
            return self._by_title[title.lower()]

        # Not found
        self._stats["missing"] += 1
        return None

    def get_category_definition(self, category: str) -> Optional[str]:
        """Get category definition from guide.csv.

        Args:
            category: JD Element name (e.g., 'key_activities', 'skills')

        Returns:
            Category definition string, or None if not found
        """
        # Map JD element name to CSV category
        csv_category = CATEGORY_MAPPING.get(category.lower(), category)

        # Find first row with this category and return its category_definition
        for row in self._by_element_id.values():
            if row.get('category', '').strip() == csv_category:
                return row.get('category_definition', '').strip() or None

        # Fallback: try direct match (in case CSV uses JD names)
        for row in self._by_element_id.values():
            if row.get('category', '').lower().strip() == category.lower():
                return row.get('category_definition', '').strip() or None

        return None

    def get_stats(self) -> dict:
        """Return match statistics.

        Returns:
            Dict with id_matches, title_fallbacks, missing counts
        """
        return self._stats.copy()

    def get_loaded_at(self) -> Optional[str]:
        """Return load timestamp.

        Returns:
            ISO timestamp string, or None if not loaded
        """
        return self._loaded_at

    def get_scale_meaning(self, category: str, level: int) -> Optional[dict]:
        """Get scale meaning for a category and level.

        Args:
            category: Category name (e.g., 'skills', 'knowledge', 'work_activities')
            level: Level value (1-5 for most, 1-3 for knowledge)

        Returns:
            Dict with level, max, label, dimension, or None if not found
        """
        scale = SCALE_MEANINGS.get(category.lower())
        if not scale:
            return None

        # Get max level for this category
        max_level = scale.get("max", 5)

        # Check if level is valid
        if level < 1 or level > max_level:
            return None

        # Get label and dimension
        label = scale.get(level)
        dimension = scale.get("dimension", "Level")

        if not label:
            return None

        return {
            "level": level,
            "max": max_level,
            "label": label,
            "dimension": dimension
        }


# Module-level singleton
guide_csv = GuideCSVLoader()

# Load on module import
_data_path = Path(__file__).parent.parent / 'data' / 'guide.csv'
if _data_path.exists():
    guide_csv.load(_data_path)
else:
    logger.warning(f"guide.csv not found at {_data_path}")
