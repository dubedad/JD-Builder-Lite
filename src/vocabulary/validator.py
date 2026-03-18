"""VocabularyValidator class for text validation against NOC vocabulary."""

import re
from typing import Dict, List

from src.vocabulary.index import VocabularyIndex


class VocabularyValidator:
    """Validates text against NOC vocabulary and calculates coverage.

    Tokenizes input text, filters stop words, and checks each remaining
    word against the vocabulary index to determine NOC coverage.

    Attributes:
        vocab_index: VocabularyIndex instance for term lookup
    """

    # Common stop words to exclude from coverage calculation
    STOP_WORDS = {
        "the", "a", "an", "and", "or", "of", "to", "in", "for", "on",
        "with", "is", "are", "was", "were", "be", "been", "being",
        "by", "as", "at", "from", "that", "this", "it"
    }

    def __init__(self, vocab_index: VocabularyIndex) -> None:
        """Initialize validator with vocabulary index.

        Args:
            vocab_index: VocabularyIndex instance for term lookup
        """
        self.vocab_index = vocab_index

    def validate_text(self, text: str) -> Dict:
        """Validate text against NOC vocabulary.

        Tokenizes text, filters stop words, and checks remaining words
        against the vocabulary index.

        Args:
            text: Text to validate

        Returns:
            Dict with:
                - coverage_percentage: float (NOC words / total * 100, 2 decimals)
                - total_words: int (count excluding stop words)
                - noc_words: int (count of words in NOC vocabulary)
                - non_noc_words: List[str] (words not in NOC vocabulary)
        """
        # Handle empty text
        if not text or not text.strip():
            return {
                "coverage_percentage": 0.0,
                "total_words": 0,
                "noc_words": 0,
                "non_noc_words": []
            }

        # Tokenize using word boundary regex
        words = re.findall(r'\b\w+\b', text)

        # Filter stop words (case-insensitive)
        content_words = [
            word for word in words
            if word.casefold() not in self.STOP_WORDS
        ]

        # Check each word against vocabulary
        noc_count = 0
        non_noc_words: List[str] = []

        for word in content_words:
            if self.vocab_index.is_noc_term(word):
                noc_count += 1
            else:
                non_noc_words.append(word)

        # Calculate coverage percentage
        total = len(content_words)
        if total == 0:
            coverage = 0.0
        else:
            coverage = round((noc_count / total) * 100, 2)

        return {
            "coverage_percentage": coverage,
            "total_words": total,
            "noc_words": noc_count,
            "non_noc_words": non_noc_words
        }
