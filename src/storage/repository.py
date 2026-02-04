"""Repository for occupational group data access.

Provides validated CRUD operations with parameterized queries,
temporal versioning support, and content hash lookup for change detection.
"""

import sqlite3
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

from .db_manager import get_db


class OccupationalGroupRepository:
    """Data access layer for occupational group reference data.

    Provides validated insert operations with parameterized queries,
    temporal versioning support, and content hash lookup for change detection.

    All INSERT/UPDATE operations use parameterized queries (? placeholders)
    to prevent SQL injection.
    """

    # Required fields for provenance records
    PROVENANCE_REQUIRED_FIELDS = [
        "url",
        "scraped_at",
        "http_status",
        "content_hash",
        "archive_path",
        "parser_version",
    ]

    def __init__(self, conn: Optional[sqlite3.Connection] = None):
        """Initialize repository.

        Args:
            conn: Optional connection for transaction reuse.
                  If None, methods will use get_db() context manager.
        """
        self._conn = conn
        self._owns_connection = conn is None

    def _get_conn(self) -> sqlite3.Connection:
        """Get connection, creating one if needed."""
        if self._conn is not None:
            return self._conn
        raise RuntimeError(
            "No connection provided. Use 'with get_db() as conn: repo = Repository(conn)'"
        )

    def insert_provenance(self, provenance_data: Dict[str, Any]) -> int:
        """Insert a new provenance record.

        Args:
            provenance_data: Dict with keys:
                - url (required): Source URL
                - scraped_at (required): ISO 8601 UTC timestamp
                - http_status (required): HTTP status code
                - content_hash (required): SHA-256 hash
                - archive_path (required): Path to saved HTML
                - parser_version (required): Parser version string
                - http_headers (optional): JSON string of headers

        Returns:
            Inserted provenance ID

        Raises:
            ValueError: If required fields are missing or empty
        """
        # Validate required fields
        for field in self.PROVENANCE_REQUIRED_FIELDS:
            if field not in provenance_data or not provenance_data[field]:
                raise ValueError(f"Missing required field: {field}")

        conn = self._get_conn()

        try:
            cursor = conn.execute(
                """
                INSERT INTO scrape_provenance
                (url, scraped_at, http_status, http_headers, content_hash, archive_path, parser_version)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    provenance_data["url"],
                    provenance_data["scraped_at"],
                    provenance_data["http_status"],
                    provenance_data.get("http_headers"),  # Optional
                    provenance_data["content_hash"],
                    provenance_data["archive_path"],
                    provenance_data["parser_version"],
                ),
            )
            return cursor.lastrowid
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to insert provenance: {e}") from e

    def insert_group(self, group_data: Dict[str, Any], provenance_id: int) -> int:
        """Insert a new occupational group.

        Args:
            group_data: Dict with keys:
                - group_code (required): e.g., "AI", "CP"
                - definition (required): Group definition text
                - effective_from (required): ISO 8601 UTC timestamp
                - subgroup (optional): e.g., "Non-Operational"
                - qualification_standard_url (optional)
                - rates_of_pay_represented_url (optional)
                - rates_of_pay_unrepresented_url (optional)
            provenance_id: FK to scrape_provenance

        Returns:
            Inserted group ID

        Raises:
            ValueError: If required fields are missing or empty
        """
        # Validate required fields
        if not group_data.get("group_code"):
            raise ValueError("Missing required field: group_code")
        if not group_data.get("definition"):
            raise ValueError("Missing required field: definition")
        if not group_data.get("effective_from"):
            raise ValueError("Missing required field: effective_from")

        conn = self._get_conn()

        try:
            cursor = conn.execute(
                """
                INSERT INTO dim_occupational_group
                (group_code, subgroup, definition, qualification_standard_url,
                 rates_of_pay_represented_url, rates_of_pay_unrepresented_url,
                 effective_from, effective_to, source_provenance_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, NULL, ?)
                """,
                (
                    group_data["group_code"],
                    group_data.get("subgroup"),
                    group_data["definition"],
                    group_data.get("qualification_standard_url"),
                    group_data.get("rates_of_pay_represented_url"),
                    group_data.get("rates_of_pay_unrepresented_url"),
                    group_data["effective_from"],
                    provenance_id,
                ),
            )
            return cursor.lastrowid
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to insert group: {e}") from e

    def insert_inclusion(
        self,
        group_id: int,
        statement: str,
        order_num: int,
        provenance_id: int,
        paragraph_label: Optional[str] = None,
    ) -> int:
        """Insert an inclusion statement for a group.

        Args:
            group_id: FK to dim_occupational_group
            statement: Inclusion statement text
            order_num: Original list position (1-based)
            provenance_id: FK to scrape_provenance
            paragraph_label: Optional label (e.g., "I1", "I2")

        Returns:
            Inserted inclusion ID

        Raises:
            ValueError: If statement is empty
        """
        if not statement or not statement.strip():
            raise ValueError("Inclusion statement cannot be empty")

        conn = self._get_conn()

        try:
            cursor = conn.execute(
                """
                INSERT INTO dim_occupational_inclusion
                (group_id, statement, order_num, paragraph_label, source_provenance_id)
                VALUES (?, ?, ?, ?, ?)
                """,
                (group_id, statement, order_num, paragraph_label, provenance_id),
            )
            return cursor.lastrowid
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to insert inclusion: {e}") from e

    def insert_exclusion(
        self,
        group_id: int,
        statement: str,
        order_num: int,
        provenance_id: int,
        paragraph_label: Optional[str] = None,
    ) -> int:
        """Insert an exclusion statement for a group.

        Args:
            group_id: FK to dim_occupational_group
            statement: Exclusion statement text
            order_num: Original list position (1-based)
            provenance_id: FK to scrape_provenance
            paragraph_label: Optional label (e.g., "E1", "E2")

        Returns:
            Inserted exclusion ID

        Raises:
            ValueError: If statement is empty
        """
        if not statement or not statement.strip():
            raise ValueError("Exclusion statement cannot be empty")

        conn = self._get_conn()

        try:
            cursor = conn.execute(
                """
                INSERT INTO dim_occupational_exclusion
                (group_id, statement, order_num, paragraph_label, source_provenance_id)
                VALUES (?, ?, ?, ?, ?)
                """,
                (group_id, statement, order_num, paragraph_label, provenance_id),
            )
            return cursor.lastrowid
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to insert exclusion: {e}") from e

    def insert_concordance(
        self,
        group_code: str,
        job_eval_url: Optional[str],
        provenance_id: int,
        effective_from: str,
    ) -> int:
        """Insert a concordance record linking group to evaluation standard.

        Args:
            group_code: Occupational group code
            job_eval_url: URL to job evaluation standard (may be None)
            provenance_id: FK to scrape_provenance
            effective_from: ISO 8601 UTC timestamp

        Returns:
            Inserted concordance ID
        """
        conn = self._get_conn()

        try:
            cursor = conn.execute(
                """
                INSERT INTO table_of_concordance
                (group_code, job_evaluation_standard_url, effective_from, effective_to, source_provenance_id)
                VALUES (?, ?, ?, NULL, ?)
                """,
                (group_code, job_eval_url, effective_from, provenance_id),
            )
            return cursor.lastrowid
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to insert concordance: {e}") from e

    def get_current_groups(self) -> List[Dict[str, Any]]:
        """Get all currently valid occupational groups.

        Returns:
            List of dicts with group data from v_current_occupational_groups view
        """
        conn = self._get_conn()

        try:
            cursor = conn.execute("SELECT * FROM v_current_occupational_groups")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to get current groups: {e}") from e

    def get_last_content_hash(self, url: str) -> Optional[str]:
        """Get the most recent content hash for a URL.

        Args:
            url: Source URL to look up

        Returns:
            SHA-256 hash string, or None if URL never scraped
        """
        conn = self._get_conn()

        try:
            cursor = conn.execute(
                """
                SELECT content_hash
                FROM scrape_provenance
                WHERE url = ?
                ORDER BY scraped_at DESC
                LIMIT 1
                """,
                (url,),
            )
            row = cursor.fetchone()
            return row["content_hash"] if row else None
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to get content hash: {e}") from e

    def expire_group(self, group_id: int, effective_to: str) -> None:
        """Mark a group as expired (no longer currently valid).

        Used for temporal versioning when content changes.

        Args:
            group_id: ID of group to expire
            effective_to: ISO 8601 UTC timestamp of expiration
        """
        conn = self._get_conn()

        try:
            conn.execute(
                """
                UPDATE dim_occupational_group
                SET effective_to = ?
                WHERE id = ?
                """,
                (effective_to, group_id),
            )
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to expire group: {e}") from e

    def record_verification(
        self, group_id: int, verified_by: str, notes: Optional[str] = None
    ) -> int:
        """Record a human verification event for a group.

        Args:
            group_id: FK to dim_occupational_group
            verified_by: Username or email of verifier
            notes: Optional verification notes

        Returns:
            Inserted verification event ID
        """
        conn = self._get_conn()
        verified_at = datetime.now(timezone.utc).isoformat()

        try:
            cursor = conn.execute(
                """
                INSERT INTO verification_event
                (group_id, verified_at, verified_by, verification_notes)
                VALUES (?, ?, ?, ?)
                """,
                (group_id, verified_at, verified_by, notes),
            )
            return cursor.lastrowid
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to record verification: {e}") from e
