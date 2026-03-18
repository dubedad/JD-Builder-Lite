"""
CLI command to refresh DIM_OCCUPATIONAL table from TBS sources.

Usage:
    python -m src.cli.refresh_occupational
    python -m src.cli.refresh_occupational --dry-run
    python -m src.cli.refresh_occupational --verbose

This script:
1. Scrapes TBS occupational groups table and definitions
2. Validates all data per DAMA-DMBOK 2.0
3. Archives raw HTML for provenance
4. Loads to SQLite database (atomic transaction)
5. Reports statistics

Rate limited to 1 request/second as per government site etiquette.

Per CONTEXT.md decisions:
- "Manual trigger only (admin/developer runs refresh command)"
- "Fail explicitly, keep existing data (log error, don't update that group, alert operator)"
"""

import sys
import argparse
from datetime import datetime


def main():
    """Main entry point for the refresh_occupational CLI command."""
    parser = argparse.ArgumentParser(
        description="Refresh DIM_OCCUPATIONAL table from TBS sources",
        epilog="Rate limited to 1 request/second. Full scrape takes ~5 seconds.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and parse without loading to database",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed progress and stack traces on error",
    )

    args = parser.parse_args()

    print("=== TBS Occupational Data Refresh ===")
    print(f"Started: {datetime.now().isoformat()}")
    print()

    try:
        if args.dry_run:
            return run_dry_run(args.verbose)
        else:
            return run_full_scrape(args.verbose)

    except KeyboardInterrupt:
        print("\nAborted by user")
        return 130

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def run_dry_run(verbose: bool) -> int:
    """Run in dry-run mode (validate without loading).

    Args:
        verbose: Whether to show detailed output

    Returns:
        Exit code (0 for success)
    """
    print("DRY RUN MODE - No database changes")
    print()

    from src.scrapers.http_client import TBSHttpClient
    from src.scrapers.tbs_parser import (
        parse_occupational_groups_table,
        parse_definition_page,
    )
    from src.scrapers.validation import validate_or_raise, ValidationError

    client = TBSHttpClient()

    print("Fetching pages (rate limited)...")
    table_html, table_meta = client.fetch_occupational_groups_table()
    if verbose:
        print(f"  Table: {len(table_html)} bytes from {table_meta['url']}")

    defn_html, defn_meta = client.fetch_definitions_page()
    if verbose:
        print(f"  Definitions: {len(defn_html)} bytes from {defn_meta['url']}")

    print("Parsing...")
    table_groups = parse_occupational_groups_table(table_html)
    definitions = parse_definition_page(defn_html)

    if verbose:
        print(f"  Table rows: {len(table_groups)}")
        print(f"  Raw definitions: {len(definitions)}")

    # Filter out groups with empty definitions (same as full scrape logic)
    # These would fail validation anyway - better to warn and skip
    valid_definitions = []
    skipped = []
    for defn in definitions:
        definition_text = defn.get("definition", "")
        if not definition_text or not definition_text.strip():
            skipped.append(f"{defn.get('group_code')}/{defn.get('subgroup')}")
        else:
            valid_definitions.append(defn)

    if skipped:
        print(f"  Skipping {len(skipped)} groups with empty definitions:")
        for s in skipped[:5]:
            print(f"    - {s}")
        if len(skipped) > 5:
            print(f"    ... and {len(skipped) - 5} more")

    print("Validating...")
    try:
        validate_or_raise(valid_definitions)
    except ValidationError as e:
        print()
        print("VALIDATION FAILED:")
        for error in e.errors[:10]:  # Show first 10 errors
            print(f"  - {error}")
        if len(e.errors) > 10:
            print(f"  ... and {len(e.errors) - 10} more errors")
        return 1

    # Calculate totals
    total_incl = sum(len(d.get("inclusions", [])) for d in valid_definitions)
    total_excl = sum(len(d.get("exclusions", [])) for d in valid_definitions)

    print()
    print("Would load:")
    print(f"  - {len(table_groups)} groups from table")
    print(f"  - {len(valid_definitions)} definitions (valid)")
    print(f"  - {total_incl} inclusions")
    print(f"  - {total_excl} exclusions")
    if skipped:
        print(f"  - {len(skipped)} groups skipped (empty definitions)")
    print()
    print("Validation PASSED")
    print()
    print(f"Completed: {datetime.now().isoformat()}")

    return 0


def run_full_scrape(verbose: bool) -> int:
    """Run full scrape and load to database.

    Args:
        verbose: Whether to show detailed output

    Returns:
        Exit code (0 for success)
    """
    from src.scrapers.tbs_scraper import scrape_all_occupational_groups
    from src.scrapers.validation import ValidationError

    if verbose:
        # Enable debug logging
        import logging
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        )

    print("Running full scrape...")
    print()

    try:
        stats = scrape_all_occupational_groups()
    except ValidationError as e:
        print()
        print("VALIDATION FAILED:")
        for error in e.errors[:10]:
            print(f"  - {error}")
        if len(e.errors) > 10:
            print(f"  ... and {len(e.errors) - 10} more errors")
        print()
        print("Database unchanged (validation failed before load)")
        return 1

    if stats.get("skipped"):
        print(f"Skipped: {stats.get('reason')}")
        print("Content unchanged since last scrape - no database changes needed")
    else:
        print()
        print("=== Results ===")
        print(f"Groups loaded: {stats.get('groups', 0)}")
        print(f"Inclusions loaded: {stats.get('inclusions', 0)}")
        print(f"Exclusions loaded: {stats.get('exclusions', 0)}")
        print(f"Concordance entries: {stats.get('concordance', 0)}")

    print()
    print(f"Completed: {datetime.now().isoformat()}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
