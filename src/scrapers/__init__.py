"""TBS Occupational Groups scraping infrastructure.

Provides HTTP client with rate limiting and retry logic,
HTML archiving for provenance, and parsers for TBS pages.
"""

__all__ = [
    # HTTP client
    "TBSHttpClient",
    "create_scraping_session",
    # HTML archiver
    "archive_html",
    "calculate_content_hash",
    "get_archived_content",
    # Parsers
    "parse_occupational_groups_table",
    "parse_definition_page",
    "parse_allocation_guide",
    "validate_parsed_group",
]


# Lazy imports to avoid import errors during incremental development
def __getattr__(name):
    """Lazy import for module components."""
    if name in ("TBSHttpClient", "create_scraping_session"):
        from .http_client import TBSHttpClient, create_scraping_session
        globals()["TBSHttpClient"] = TBSHttpClient
        globals()["create_scraping_session"] = create_scraping_session
        return globals()[name]

    if name in ("archive_html", "calculate_content_hash", "get_archived_content"):
        from .html_archiver import archive_html, calculate_content_hash, get_archived_content
        globals()["archive_html"] = archive_html
        globals()["calculate_content_hash"] = calculate_content_hash
        globals()["get_archived_content"] = get_archived_content
        return globals()[name]

    if name in (
        "parse_occupational_groups_table",
        "parse_definition_page",
        "parse_allocation_guide",
        "validate_parsed_group",
    ):
        from .tbs_parser import (
            parse_occupational_groups_table,
            parse_definition_page,
            parse_allocation_guide,
            validate_parsed_group,
        )
        globals()["parse_occupational_groups_table"] = parse_occupational_groups_table
        globals()["parse_definition_page"] = parse_definition_page
        globals()["parse_allocation_guide"] = parse_allocation_guide
        globals()["validate_parsed_group"] = validate_parsed_group
        return globals()[name]

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
