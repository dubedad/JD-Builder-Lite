"""File watcher for hot-reloading vocabulary when parquet files change."""

import os
from typing import Set

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    HAS_WATCHDOG = True
except ImportError:
    HAS_WATCHDOG = False
    Observer = object
    FileSystemEventHandler = object

from src.vocabulary.index import VocabularyIndex


class VocabularyFileHandler(FileSystemEventHandler):
    """Watches for parquet file changes and triggers vocabulary reload.

    Monitors the JobForge bronze directory for modifications to OASIS
    parquet files and automatically reloads the vocabulary index.

    Attributes:
        vocab_index: VocabularyIndex instance to reload on file changes
    """

    # Parquet files to monitor for changes
    PARQUET_FILES: Set[str] = {
        "oasis_abilities.parquet",
        "oasis_skills.parquet",
        "oasis_knowledges.parquet",
        "oasis_workactivities.parquet",
    }

    def __init__(self, vocab_index: VocabularyIndex) -> None:
        """Initialize handler with vocabulary index reference.

        Args:
            vocab_index: VocabularyIndex instance to reload on changes
        """
        super().__init__()
        self.vocab_index = vocab_index

    def on_modified(self, event) -> None:
        """Handle file modification events.

        Reloads vocabulary if a monitored parquet file was modified.

        Args:
            event: FileSystemEvent from watchdog
        """
        if event.is_directory:
            return

        # Get just the filename from the path
        filename = os.path.basename(event.src_path)

        if filename in self.PARQUET_FILES:
            print(f"[Vocabulary] Detected change in {filename}, reloading...")
            try:
                self.vocab_index.reload()
                print(f"[Vocabulary] Reloaded: {self.vocab_index.get_term_count()} terms")
            except Exception as e:
                print(f"[Vocabulary] Reload failed: {e}")


def start_vocabulary_watcher(vocab_index: VocabularyIndex, bronze_path: str):
    """Start file watcher for vocabulary hot-reload.

    Creates an Observer that monitors the bronze directory for changes
    to OASIS parquet files and triggers vocabulary reload.

    Args:
        vocab_index: VocabularyIndex instance to reload on changes
        bronze_path: Path to JobForge bronze data directory

    Returns:
        Observer instance (call observer.stop() to cleanup), or None if watchdog unavailable
    """
    if not HAS_WATCHDOG:
        print("[Vocabulary] watchdog not available — hot-reload disabled")
        return None

    handler = VocabularyFileHandler(vocab_index)
    observer = Observer()
    observer.schedule(handler, bronze_path, recursive=False)
    observer.start()

    print(f"[Vocabulary] File watcher started for: {bronze_path}")
    return observer
