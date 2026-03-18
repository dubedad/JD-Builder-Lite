"""Link classification decisions to TBS source documents.

Per CONTEXT.md: "Full provenance with links to specific TBS page/paragraph"

Provenance is critical: every decision must trace back to authoritative TBS source.
"""

from typing import Dict, List, Optional

from src.storage.db_manager import get_db
from src.storage.repository import OccupationalGroupRepository


class ProvenanceLinker:
    """Link classification decisions to TBS source documents.

    Per CONTEXT.md: "Full provenance with links to specific TBS page/paragraph"
    """

    def __init__(self, repository: Optional[OccupationalGroupRepository] = None):
        """Initialize with optional repository for database lookups.

        If repository not provided, uses get_db() context manager.

        Args:
            repository: Optional OccupationalGroupRepository instance
        """
        self._repo = repository

    def link_to_tbs_provenance(
        self, group_id: int, paragraph_label: Optional[str] = None
    ) -> Dict:
        """Create provenance link for a group recommendation.

        Args:
            group_id: FK to dim_occupational_group
            paragraph_label: Optional specific paragraph (e.g., "I1", "E2", "Definition")

        Returns:
            Dict with provenance data:
            {
                'group_id': int,
                'source_type': 'TBS Occupational Group Definition',
                'url': str (TBS source URL),
                'paragraph': str or None,
                'scraped_at': str (ISO 8601),
                'content_hash': str (for verification),
                'archive_path': str (local backup)
            }
        """
        # Get provenance from repository
        if self._repo:
            prov = self._repo.get_group_provenance(group_id)
        else:
            # Use context manager if no repo provided
            with get_db() as conn:
                repo = OccupationalGroupRepository(conn)
                prov = repo.get_group_provenance(group_id)

        if not prov:
            # Graceful handling of missing provenance
            return {
                "group_id": group_id,
                "source_type": "TBS Occupational Group Definition",
                "url": None,
                "paragraph": paragraph_label,
                "scraped_at": None,
                "content_hash": None,
                "archive_path": None,
                "warning": "Provenance data not found for group",
            }

        # Build full provenance record
        return {
            "group_id": group_id,
            "source_type": "TBS Occupational Group Definition",
            "url": prov["url"],
            "paragraph": paragraph_label,
            "scraped_at": prov["scraped_at"],
            "content_hash": prov["content_hash"],
            "archive_path": prov["archive_path"],
        }

    def link_multiple(self, group_ids: List[int]) -> Dict[int, Dict]:
        """Get provenance for multiple groups efficiently.

        Args:
            group_ids: List of group IDs

        Returns:
            Dict mapping group_id -> provenance dict
        """
        results = {}

        # Use single connection for all lookups
        if self._repo:
            for group_id in group_ids:
                results[group_id] = self.link_to_tbs_provenance(group_id)
        else:
            with get_db() as conn:
                repo = OccupationalGroupRepository(conn)
                linker = ProvenanceLinker(repo)
                for group_id in group_ids:
                    results[group_id] = linker.link_to_tbs_provenance(group_id)

        return results

    def get_definition_url(self, group_code: str) -> Optional[str]:
        """Get the TBS definition page URL for a group code.

        Queries v_current_occupational_groups for source_url.

        Args:
            group_code: Occupational group code (e.g., "AI", "CS")

        Returns:
            TBS source URL or None if not found
        """
        if self._repo:
            conn = self._repo._get_conn()
        else:
            # Use context manager if no repo provided
            with get_db() as conn:
                cursor = conn.execute(
                    """
                    SELECT source_url
                    FROM v_current_occupational_groups
                    WHERE group_code = ?
                    LIMIT 1
                    """,
                    (group_code,),
                )
                row = cursor.fetchone()
                return row["source_url"] if row else None

        # If we have a repo, use its connection
        cursor = conn.execute(
            """
            SELECT source_url
            FROM v_current_occupational_groups
            WHERE group_code = ?
            LIMIT 1
            """,
            (group_code,),
        )
        row = cursor.fetchone()
        return row["source_url"] if row else None


def link_to_tbs_provenance(
    group_id: int, paragraph_label: Optional[str] = None
) -> Dict:
    """Convenience function for linking to TBS provenance.

    Wraps ProvenanceLinker.link_to_tbs_provenance() for simple usage.

    Args:
        group_id: FK to dim_occupational_group
        paragraph_label: Optional specific paragraph (e.g., "I1", "E2", "Definition")

    Returns:
        Dict with provenance data
    """
    linker = ProvenanceLinker()
    return linker.link_to_tbs_provenance(group_id, paragraph_label)
