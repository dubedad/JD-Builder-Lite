"""Vocabulary module for NOC term validation and coverage analysis.

This module provides vocabulary indexing from JobForge parquet files,
text validation against NOC vocabulary, and hot-reload file watching.
"""

from src.vocabulary.index import VocabularyIndex
from src.vocabulary.validator import VocabularyValidator

# start_vocabulary_watcher will be added in Task 3

__all__ = [
    "VocabularyIndex",
    "VocabularyValidator",
]
