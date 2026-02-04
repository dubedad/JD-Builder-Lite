"""ETL orchestrator for TBS occupational group data.

Ties together HTTP client, parsers, validators, and repository
to populate DIM_OCCUPATIONAL with full provenance tracking.

Implements Extract-Transform-Load with atomic transactions
per DAMA-DMBOK 2.0 reference data management practices.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

from .http_client import TBSHttpClient
from .html_archiver import archive_html, content_changed
from .tbs_parser import parse_occupational_groups_table, parse_definition_page
from .validation import validate_or_raise


logger = logging.getLogger(__name__)

# Parser version for provenance tracking
# Increment when parsing logic changes to enable audit
PARSER_VERSION = "1.0.0"


class TBSScraper:
    """ETL orchestrator for TBS occupational group data.

    Coordinates fetching, parsing, validating, and loading
    occupational group reference data from TBS sources.

    Implements atomic transactions - either all data loads
    or the database remains unchanged (no partial updates).

    Example:
        scraper = TBSScraper()
        stats = scraper.scrape_occupational_groups()
        print(f"Loaded {stats['groups']} groups")
    """

    def __init__(self, client: Optional[TBSHttpClient] = None):
        """Initialize the scraper.

        Args:
            client: Optional pre-configured HTTP client.
                If None, creates one with default configuration.
        """
        self.client = client if client else TBSHttpClient()
        logger.info("TBSScraper initialized with parser version %s", PARSER_VERSION)

    def scrape_occupational_groups(self) -> Dict[str, Any]:
        """Full ETL pipeline for occupational groups.

        Executes the complete Extract-Transform-Load cycle:
        1. EXTRACT: Fetch HTML from TBS servers
        2. Archive: Save raw HTML for provenance
        3. TRANSFORM: Parse HTML to structured data
        4. VALIDATE: Check data quality per DAMA-DMBOK
        5. LOAD: Insert to database in atomic transaction

        Returns:
            Dict with stats:
                - groups: Number of groups loaded
                - inclusions: Number of inclusions loaded
                - exclusions: Number of exclusions loaded
                - concordance: Number of concordance entries
                OR
                - skipped: True
                - reason: Why skipped (e.g., 'content_unchanged')

        Raises:
            ValidationError: If data fails validation
            RuntimeError: If database transaction fails
        """
        from src.storage.db_manager import get_db, init_db
        from src.storage.repository import OccupationalGroupRepository

        # Capture single timestamp for entire scrape
        # Per RESEARCH.md Pitfall 6: Use consistent timestamp across batch
        scrape_timestamp = datetime.now(timezone.utc).isoformat()
        logger.info("Starting scrape at %s", scrape_timestamp)

        # Initialize database if needed
        init_db()

        # EXTRACT: Fetch HTML from TBS
        print("Fetching occupational groups table...")
        logger.info("Fetching occupational groups table")
        table_html, table_meta = self.client.fetch_occupational_groups_table()
        logger.info(
            "Fetched table: %d bytes, status %d",
            len(table_html), table_meta["status"]
        )

        print("Fetching definitions page...")
        logger.info("Fetching definitions page")
        defn_html, defn_meta = self.client.fetch_definitions_page()
        logger.info(
            "Fetched definitions: %d bytes, status %d",
            len(defn_html), defn_meta["status"]
        )

        # Archive HTML for provenance (before any transformation)
        print("Archiving HTML...")
        table_archive = archive_html(table_html, table_meta["url"], scrape_timestamp)
        defn_archive = archive_html(defn_html, defn_meta["url"], scrape_timestamp)
        logger.info("Archived table to %s", table_archive["archive_path"])
        logger.info("Archived definitions to %s", defn_archive["archive_path"])

        # TRANSFORM: Parse HTML to structured data
        print("Parsing table...")
        table_groups = parse_occupational_groups_table(table_html)
        logger.info("Parsed %d groups from table", len(table_groups))

        print("Parsing definitions...")
        definitions = parse_definition_page(defn_html)
        logger.info("Parsed %d definitions", len(definitions))

        # Merge table data with definitions
        print("Merging data...")
        merged_groups = self._merge_table_and_definitions(table_groups, definitions)
        logger.info("Merged into %d groups", len(merged_groups))

        # VALIDATE: Check all data before loading
        # Per CONTEXT.md: "Never insert partial or corrupt data"
        print("Validating data...")
        validate_or_raise(merged_groups)
        logger.info("Validation passed for all groups")

        # LOAD: Atomic transaction
        stats = {"groups": 0, "inclusions": 0, "exclusions": 0, "concordance": 0}

        with get_db() as conn:
            repo = OccupationalGroupRepository(conn)

            # Check if content changed (skip if unchanged)
            if not content_changed(table_meta["url"], table_html, repo):
                print("Content unchanged, skipping load")
                logger.info("Content unchanged since last scrape, skipping load")
                return {"skipped": True, "reason": "content_unchanged"}

            try:
                print("Loading to database...")

                # Insert provenance records first (for FK references)
                table_prov_id = repo.insert_provenance({
                    "url": table_meta["url"],
                    "scraped_at": scrape_timestamp,
                    "http_status": table_meta["status"],
                    "http_headers": json.dumps(table_meta["headers"]),
                    "content_hash": table_archive["content_hash"],
                    "archive_path": table_archive["archive_path"],
                    "parser_version": PARSER_VERSION,
                })
                logger.info("Inserted table provenance: id=%d", table_prov_id)

                defn_prov_id = repo.insert_provenance({
                    "url": defn_meta["url"],
                    "scraped_at": scrape_timestamp,
                    "http_status": defn_meta["status"],
                    "http_headers": json.dumps(defn_meta["headers"]),
                    "content_hash": defn_archive["content_hash"],
                    "archive_path": defn_archive["archive_path"],
                    "parser_version": PARSER_VERSION,
                })
                logger.info("Inserted definitions provenance: id=%d", defn_prov_id)

                # Insert groups with inclusions/exclusions
                for group in merged_groups:
                    group_id = repo.insert_group(
                        {
                            "group_code": group["group_code"],
                            "subgroup": group.get("subgroup"),
                            "definition": group["definition"],
                            "qualification_standard_url": group.get("qualification_standard_url"),
                            "rates_of_pay_represented_url": group.get("rates_of_pay_represented_url"),
                            "rates_of_pay_unrepresented_url": group.get("rates_of_pay_unrepresented_url"),
                            "effective_from": scrape_timestamp,
                        },
                        defn_prov_id,
                    )
                    stats["groups"] += 1

                    # Insert inclusions
                    for incl in group.get("inclusions", []):
                        repo.insert_inclusion(
                            group_id,
                            incl["statement"],
                            incl["order"],
                            defn_prov_id,
                            f"I{incl['order']}",
                        )
                        stats["inclusions"] += 1

                    # Insert exclusions
                    for excl in group.get("exclusions", []):
                        repo.insert_exclusion(
                            group_id,
                            excl["statement"],
                            excl["order"],
                            defn_prov_id,
                            f"E{excl['order']}",
                        )
                        stats["exclusions"] += 1

                    # Insert concordance (job evaluation standard link)
                    if group.get("job_evaluation_standard_url"):
                        repo.insert_concordance(
                            group["group_code"],
                            group["job_evaluation_standard_url"],
                            table_prov_id,
                            scrape_timestamp,
                        )
                        stats["concordance"] += 1

                # Commit transaction
                conn.commit()
                logger.info("Transaction committed: %s", stats)
                print(f"Loaded: {stats}")
                return stats

            except Exception as e:
                # Rollback on any error (atomic transaction)
                conn.rollback()
                logger.error("Transaction failed, rolled back: %s", e)
                print(f"Transaction failed, rolled back: {e}")
                raise

    def _merge_table_and_definitions(
        self, table_groups: List[Dict], definitions: List[Dict]
    ) -> List[Dict[str, Any]]:
        """Merge data from table and definitions page.

        Combines URLs from the concordance table with
        definitions/inclusions/exclusions from the definitions page.

        Args:
            table_groups: Groups parsed from concordance table
            definitions: Groups parsed from definitions page

        Returns:
            Merged list of group dicts ready for validation
        """
        # Create lookup by group_code+subgroup from definitions
        defn_lookup: Dict[str, Dict] = {}
        for defn in definitions:
            code = defn.get("group_code", "")
            subgroup = defn.get("subgroup")
            key = f"{code}|{subgroup or ''}"
            defn_lookup[key] = defn

        merged = []

        for table_group in table_groups:
            code = table_group.get("group_code", "")
            subgroup = table_group.get("subgroup")
            key = f"{code}|{subgroup or ''}"

            # Try to find matching definition
            defn = defn_lookup.get(key)

            if defn:
                # Merge table URLs with definition content
                merged.append({
                    "group_code": code,
                    "subgroup": subgroup,
                    "definition": defn.get("definition", ""),
                    "inclusions": defn.get("inclusions", []),
                    "exclusions": defn.get("exclusions", []),
                    # URLs from table
                    "qualification_standard_url": table_group.get("qualification_standard_url"),
                    "rates_of_pay_represented_url": table_group.get("rates_of_pay_represented_url"),
                    "rates_of_pay_unrepresented_url": table_group.get("rates_of_pay_unrepresented_url"),
                    "job_evaluation_standard_url": table_group.get("job_evaluation_standard_url"),
                })
            else:
                # No definition found - log warning but include with empty definition
                # This allows the data to be captured even if definition page is incomplete
                logger.warning(
                    "No definition found for %s%s",
                    code, f"/{subgroup}" if subgroup else ""
                )
                # Skip groups without definitions (can't pass validation anyway)
                # Per CONTEXT.md: "Never insert partial or corrupt data"

        # Also check for definitions not in table (orphan definitions)
        table_keys = {f"{g.get('group_code', '')}|{g.get('subgroup') or ''}" for g in table_groups}
        for key, defn in defn_lookup.items():
            if key not in table_keys:
                logger.warning(
                    "Definition found without table entry: %s",
                    defn.get("group_code")
                )

        return merged


def scrape_all_occupational_groups() -> Dict[str, Any]:
    """Convenience function for CLI usage.

    Creates a TBSScraper and runs the full ETL pipeline.

    Returns:
        Stats dict from scrape_occupational_groups()
    """
    scraper = TBSScraper()
    return scraper.scrape_occupational_groups()
