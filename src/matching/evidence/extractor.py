"""Extract and locate evidence spans from JD text.

Per CONTEXT.md: Evidence linking with "text spans, field references,
and highlighted excerpts"

NOTE per CONTEXT.md decision: "Inclusion statements: Use for shortlisting
candidates only, not for scoring or evidence"

Therefore, evidence should come from JD text matching DEFINITIONS,
not from inclusion statement matches.
"""

import re
from difflib import SequenceMatcher
from typing import Dict, List, Optional, Tuple


class EvidenceExtractor:
    """Extract and locate evidence spans from JD text.

    Per CONTEXT.md: Evidence linking with "text spans, field references,
    and highlighted excerpts"

    NOTE per CONTEXT.md decision: "Inclusion statements: Use for shortlisting
    candidates only, not for scoring or evidence"

    Therefore, evidence should come from JD text matching DEFINITIONS,
    not from inclusion statement matches.
    """

    def extract_evidence_spans(
        self, jd_data: Dict, evidence_quotes: List[str]
    ) -> List[Dict]:
        """Find quoted evidence in original JD and return with positions.

        Args:
            jd_data: Original JD dict with fields:
                - client_service_results: str
                - key_activities: List[str]
                - position_title: str (optional)
            evidence_quotes: List of text quotes from LLM reasoning

        Returns:
            List of dicts:
            {
                'text': original quote,
                'matched_text': text found in JD (may differ slightly),
                'field': field reference (e.g., "Client-Service Results", "Key Activity 3"),
                'start_char': int or None,
                'end_char': int or None,
                'match_confidence': float (1.0 = exact, <1.0 = fuzzy)
            }

        Per RESEARCH.md Pitfall 4:
        - LLMs may paraphrase instead of exact quote
        - Implement fuzzy matching with normalization
        - Accept that some evidence won't link - include anyway
        """
        # Build field boundaries for position mapping
        field_boundaries = self._build_field_boundaries(jd_data)

        results = []
        for quote in evidence_quotes:
            if not quote or not quote.strip():
                continue

            # Try to find the quote in the full text
            result = self._find_quote_in_fields(quote, jd_data, field_boundaries)
            results.append(result)

        return results

    def _build_field_boundaries(self, jd_data: Dict) -> List[Dict]:
        """Build field boundaries from jd_data structure.

        Returns:
            List of dicts with:
            - field_name: str
            - start_char: int
            - end_char: int
            - content: str
        """
        boundaries = []
        char_pos = 0

        # Position title (if present)
        if "position_title" in jd_data and jd_data["position_title"]:
            content = jd_data["position_title"]
            boundaries.append(
                {
                    "field_name": "Position Title",
                    "start_char": char_pos,
                    "end_char": char_pos + len(content),
                    "content": content,
                }
            )
            char_pos += len(content) + 1  # +1 for newline

        # Client-Service Results
        if "client_service_results" in jd_data and jd_data["client_service_results"]:
            content = jd_data["client_service_results"]
            boundaries.append(
                {
                    "field_name": "Client-Service Results",
                    "start_char": char_pos,
                    "end_char": char_pos + len(content),
                    "content": content,
                }
            )
            char_pos += len(content) + 1  # +1 for newline

        # Key Activities
        if "key_activities" in jd_data and jd_data["key_activities"]:
            for idx, activity in enumerate(jd_data["key_activities"], 1):
                if activity:
                    boundaries.append(
                        {
                            "field_name": f"Key Activity {idx}",
                            "start_char": char_pos,
                            "end_char": char_pos + len(activity),
                            "content": activity,
                        }
                    )
                    char_pos += len(activity) + 1  # +1 for newline

        return boundaries

    def _find_quote_in_fields(
        self, quote: str, jd_data: Dict, field_boundaries: List[Dict]
    ) -> Dict:
        """Find quote in JD fields using exact and fuzzy matching.

        Args:
            quote: Text to find
            jd_data: Original JD data
            field_boundaries: Pre-computed field boundaries

        Returns:
            Evidence span dict (may have None for position fields if not found)
        """
        # Try exact match first (with normalization)
        normalized_quote = self._normalize_text(quote)

        for field in field_boundaries:
            normalized_content = self._normalize_text(field["content"])

            # Try exact match in normalized text
            if normalized_quote in normalized_content:
                # Find position in original content
                start_pos = field["content"].lower().find(quote.lower())
                if start_pos >= 0:
                    return {
                        "text": quote,
                        "matched_text": field["content"][
                            start_pos : start_pos + len(quote)
                        ],
                        "field": field["field_name"],
                        "start_char": field["start_char"] + start_pos,
                        "end_char": field["start_char"] + start_pos + len(quote),
                        "match_confidence": 1.0,
                    }

            # Try fuzzy match
            fuzzy_result = self._fuzzy_find(quote, field["content"], threshold=0.8)
            if fuzzy_result:
                start_pos, end_pos, confidence = fuzzy_result
                return {
                    "text": quote,
                    "matched_text": field["content"][start_pos:end_pos],
                    "field": field["field_name"],
                    "start_char": field["start_char"] + start_pos,
                    "end_char": field["start_char"] + end_pos,
                    "match_confidence": confidence,
                }

        # No match found - return text-only evidence
        # Per RESEARCH.md: "Accept that some evidence won't link - include anyway"
        return {
            "text": quote,
            "matched_text": None,
            "field": None,
            "start_char": None,
            "end_char": None,
            "match_confidence": 0.0,
        }

    def _normalize_text(self, text: str) -> str:
        """Normalize whitespace and case for matching.

        Args:
            text: Text to normalize

        Returns:
            Normalized text (lowercase, single spaces)
        """
        # Convert to lowercase
        text = text.lower()
        # Replace multiple whitespace with single space
        text = re.sub(r"\s+", " ", text)
        # Strip leading/trailing whitespace
        text = text.strip()
        return text

    def _fuzzy_find(
        self, quote: str, text: str, threshold: float = 0.8
    ) -> Optional[Tuple[int, int, float]]:
        """Find approximate match for quote in text.

        Uses simple character-level similarity, not embedding similarity.

        Args:
            quote: Text to find
            text: Text to search in
            threshold: Minimum similarity score (0.0-1.0)

        Returns:
            Tuple of (start, end, confidence) or None if below threshold
        """
        if not quote or not text:
            return None

        quote = quote.strip()
        quote_len = len(quote)

        # Normalize for comparison
        normalized_quote = self._normalize_text(quote)

        best_match = None
        best_ratio = 0.0

        # Sliding window approach
        for i in range(len(text) - quote_len + 1):
            window = text[i : i + quote_len]
            normalized_window = self._normalize_text(window)

            # Calculate similarity using SequenceMatcher
            ratio = SequenceMatcher(
                None, normalized_quote, normalized_window
            ).ratio()

            if ratio > best_ratio:
                best_ratio = ratio
                best_match = (i, i + quote_len)

            # Also try slightly larger and smaller windows
            for offset in [-10, -5, 5, 10]:
                end_pos = i + quote_len + offset
                if end_pos <= len(text):
                    window = text[i:end_pos]
                    normalized_window = self._normalize_text(window)
                    ratio = SequenceMatcher(
                        None, normalized_quote, normalized_window
                    ).ratio()

                    if ratio > best_ratio:
                        best_ratio = ratio
                        best_match = (i, end_pos)

        # Return best match if above threshold
        if best_match and best_ratio >= threshold:
            return (best_match[0], best_match[1], best_ratio)

        return None

    def _identify_field(self, jd_data: Dict, char_pos: int) -> str:
        """Identify which JD field contains the given character position.

        Builds field boundaries from jd_data structure.

        Args:
            jd_data: Original JD data
            char_pos: Character position in concatenated text

        Returns:
            Field name like "Client-Service Results" or "Key Activity 3"
        """
        field_boundaries = self._build_field_boundaries(jd_data)

        for field in field_boundaries:
            if field["start_char"] <= char_pos < field["end_char"]:
                return field["field_name"]

        return "Unknown"


def extract_evidence_spans(jd_data: Dict, evidence_quotes: List[str]) -> List[Dict]:
    """Convenience function for extracting evidence spans.

    Wraps EvidenceExtractor.extract_evidence_spans() for simple usage.

    Args:
        jd_data: Original JD dict with fields
        evidence_quotes: List of text quotes from LLM reasoning

    Returns:
        List of evidence span dicts
    """
    extractor = EvidenceExtractor()
    return extractor.extract_evidence_spans(jd_data, evidence_quotes)
