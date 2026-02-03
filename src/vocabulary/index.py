"""VocabularyIndex class for loading and querying NOC vocabulary from parquet files."""

import os
from typing import Set

import pandas as pd


class VocabularyIndex:
    """Index of NOC vocabulary terms loaded from JobForge parquet files.

    Loads column names from 4 OASIS parquet files (abilities, skills,
    knowledges, workactivities) and provides case-insensitive lookup.

    Attributes:
        bronze_path: Path to JobForge bronze data directory
        vocabulary: Set of normalized vocabulary terms (casefolded)
    """

    # Parquet files to load vocabulary from
    PARQUET_FILES = [
        "oasis_abilities.parquet",
        "oasis_skills.parquet",
        "oasis_knowledges.parquet",
        "oasis_workactivities.parquet",
    ]

    # Columns to exclude (metadata, not vocabulary terms)
    EXCLUDED_COLUMNS = {"oasis_code", "oasis_label"}

    def __init__(self, bronze_path: str) -> None:
        """Initialize vocabulary index from parquet files.

        Args:
            bronze_path: Path to JobForge bronze data directory

        Raises:
            FileNotFoundError: If any required parquet file is missing
        """
        self.bronze_path = bronze_path
        self.vocabulary: Set[str] = set()
        self._load_vocabulary()

    def _load_vocabulary(self) -> None:
        """Load vocabulary terms from parquet file columns.

        Extracts column names from each parquet file, filters out metadata
        columns, normalizes terms using casefold(), and indexes individual
        words from multi-word phrases.

        Raises:
            FileNotFoundError: If any required parquet file is missing
        """
        self.vocabulary.clear()

        for filename in self.PARQUET_FILES:
            filepath = os.path.join(self.bronze_path, filename)

            # Check file exists before attempting to read
            if not os.path.exists(filepath):
                raise FileNotFoundError(
                    f"Required vocabulary file not found: {filename}\n"
                    f"Full path checked: {filepath}"
                )

            # Read parquet and extract column names
            df = pd.read_parquet(filepath)
            columns = df.columns.tolist()

            for col in columns:
                # Skip metadata columns
                if col in self.EXCLUDED_COLUMNS or col.startswith("_"):
                    continue

                # Normalize the full term
                normalized = col.strip().casefold()
                self.vocabulary.add(normalized)

                # Also index individual words from multi-word phrases
                # e.g., "Active Listening" -> add "active", "listening"
                words = normalized.split()
                for word in words:
                    word = word.strip()
                    if word:
                        self.vocabulary.add(word)

        # Verify we loaded something
        if not self.vocabulary:
            raise ValueError(
                "Vocabulary loaded but is empty. "
                "Check that parquet files contain valid column names."
            )

    def reload(self) -> None:
        """Reload vocabulary from parquet files.

        Useful for hot-reload when parquet files are updated.
        """
        self._load_vocabulary()

    def is_noc_term(self, word: str) -> bool:
        """Check if a word exists in the NOC vocabulary.

        Args:
            word: Word to check (case-insensitive)

        Returns:
            True if word is in NOC vocabulary, False otherwise
        """
        return word.strip().casefold() in self.vocabulary

    def get_term_count(self) -> int:
        """Get the total number of terms in the vocabulary.

        Returns:
            Number of unique terms (including individual words from phrases)
        """
        return len(self.vocabulary)
