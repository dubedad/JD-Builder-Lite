"""Labels.csv integration for confidence boost.

Provides confidence boost when existing labels from JobForge 2.0 support a group match.

NOTE: labels_loader uses OaSIS profile codes (e.g., "21211.00"), not TBS group codes.
For v4.0, we gracefully degrade if no OaSIS->TBS mapping exists.
Future: Add explicit TBS group -> OaSIS code mapping table.
"""

from typing import Dict, List


class LabelsBooster:
    """Provide confidence boost when existing labels support a group match."""

    def __init__(self):
        """Initialize labels booster with labels_loader integration."""
        try:
            from src.services.labels_loader import labels_loader
            self.labels_loader = labels_loader
            self._has_labels_loader = True
        except ImportError:
            self.labels_loader = None
            self._has_labels_loader = False

        self._group_to_labels: Dict[str, List[str]] = {}  # Cache

    def load_group_label_mappings(self) -> None:
        """
        Build mapping from group codes to associated labels.

        NOTE: labels_loader uses OaSIS profile codes, not TBS group codes.
        We need a mapping strategy:

        Option A: If labels contain group code references, extract them
        Option B: Use semantic similarity between labels and group definitions
        Option C: Return empty mapping if no clear connection exists

        For v4.0, use Option C - return 0 boost if we can't establish mapping.
        Future: Add explicit TBS group -> OaSIS code mapping table.
        """
        # For v4.0: No OaSIS->TBS mapping available
        # Return empty mapping - labels feature gracefully degrades
        self._group_to_labels = {}

    def get_boost(self, group_code: str, jd_text: str) -> float:
        """
        Return confidence boost (0.0 to 0.1) if labels support this group.

        Per CONTEXT.md: "boost confidence if labels.csv supports the match"
        Max boost: 0.1 (10%)

        Returns 0.0 if:
        - No labels mapping established
        - Group not in mapping
        - Labels don't semantically match JD text

        Args:
            group_code: TBS group code (e.g., "CS", "PM")
            jd_text: Job description text

        Returns:
            Boost value between 0.0 and 0.1
        """
        if not self._has_labels_loader:
            return 0.0

        # For v4.0: No OaSIS->TBS mapping available
        # Return 0.0 boost (labels feature gracefully degrades)
        # This is expected and not an error - core matching uses semantic similarity

        # Future enhancement: If we establish TBS group -> OaSIS code mapping:
        # 1. Map group_code to OaSIS code(s)
        # 2. Get labels for OaSIS code(s)
        # 3. Compute semantic similarity between labels and jd_text
        # 4. Return 0.0-0.1 boost based on label match strength

        return 0.0


def get_labels_boost(group_code: str, jd_text: str) -> float:
    """
    Convenience function to get labels boost for a group.

    Args:
        group_code: TBS group code (e.g., "CS", "PM")
        jd_text: Job description text

    Returns:
        Boost value between 0.0 and 0.1
    """
    booster = LabelsBooster()
    return booster.get_boost(group_code, jd_text)


__all__ = ['LabelsBooster', 'get_labels_boost']
