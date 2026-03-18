"""Content-addressed HTML archiving for provenance tracking.

Archives raw HTML with SHA-256 content hashing, enabling
change detection and full audit trail for scraped data.
"""

import hashlib
import re
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timezone


# Archive directory
ARCHIVE_DIR = Path("data/html_archive")


def calculate_content_hash(content: bytes) -> str:
    """Calculate SHA-256 hash of content.

    Args:
        content: Raw bytes to hash

    Returns:
        Hex digest string (64 characters)
    """
    return hashlib.sha256(content).hexdigest()


def _sanitize_url_slug(url: str) -> str:
    """Convert URL path to filesystem-safe slug.

    Args:
        url: Full URL or URL path

    Returns:
        Sanitized slug for filename use
    """
    # Extract path portion
    if "://" in url:
        path = url.split("://", 1)[1]
        if "/" in path:
            path = path.split("/", 1)[1]
        else:
            path = ""
    else:
        path = url

    # Remove leading/trailing slashes
    path = path.strip("/")

    # Remove .html extension
    if path.endswith(".html"):
        path = path[:-5]

    # Replace path separators with dashes
    slug = path.replace("/", "-")

    # Remove any non-alphanumeric characters except dashes
    slug = re.sub(r"[^a-zA-Z0-9-]", "", slug)

    # Collapse multiple dashes
    slug = re.sub(r"-+", "-", slug)

    # Truncate to reasonable length
    if len(slug) > 60:
        slug = slug[:60]

    return slug or "root"


def _sanitize_timestamp(timestamp: str) -> str:
    """Convert ISO timestamp to filesystem-safe format.

    Replaces colons with dashes for Windows compatibility.

    Args:
        timestamp: ISO 8601 timestamp

    Returns:
        Filesystem-safe timestamp string
    """
    return timestamp.replace(":", "-")


def archive_html(content: bytes, url: str, timestamp: str) -> Dict[str, Any]:
    """Archive raw HTML content with provenance metadata.

    Creates archive directory if needed, saves content with
    hash-based filename, and returns provenance metadata.

    Args:
        content: Raw HTML bytes
        url: Source URL
        timestamp: ISO 8601 scrape timestamp

    Returns:
        Dict with provenance metadata:
            - url: Source URL
            - scraped_at: Timestamp
            - content_hash: SHA-256 hex digest
            - archive_path: Path to saved file
            - file_size_bytes: Content length
    """
    # Calculate content hash
    content_hash = calculate_content_hash(content)

    # Generate filename components
    url_slug = _sanitize_url_slug(url)
    safe_timestamp = _sanitize_timestamp(timestamp)
    hash_prefix = content_hash[:8]

    # Build filename: {url_slug}-{timestamp}-{hash[:8]}.html
    filename = f"{url_slug}-{safe_timestamp}-{hash_prefix}.html"

    # Ensure archive directory exists
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    # Write content (binary mode preserves encoding)
    archive_path = ARCHIVE_DIR / filename
    archive_path.write_bytes(content)

    return {
        "url": url,
        "scraped_at": timestamp,
        "content_hash": content_hash,
        "archive_path": str(archive_path),
        "file_size_bytes": len(content),
    }


def content_changed(url: str, new_content: bytes, repository) -> bool:
    """Check if content has changed since last scrape.

    Compares new content hash against the last recorded hash
    for this URL in the database.

    Args:
        url: Source URL
        new_content: Newly fetched content
        repository: OccupationalGroupRepository instance with
            get_last_content_hash method

    Returns:
        True if content is different or never scraped before,
        False if content matches last scrape
    """
    new_hash = calculate_content_hash(new_content)
    last_hash = repository.get_last_content_hash(url)

    if last_hash is None:
        # First time scraping this URL
        return True

    return new_hash != last_hash


def get_archived_content(archive_path: str) -> bytes:
    """Read archived HTML content from disk.

    Useful for re-parsing after code changes without
    re-scraping from the source.

    Args:
        archive_path: Path to archived HTML file

    Returns:
        Raw HTML bytes

    Raises:
        FileNotFoundError: If archive file doesn't exist
    """
    path = Path(archive_path)
    return path.read_bytes()


def get_archive_metadata(archive_path: str) -> Optional[Dict[str, Any]]:
    """Extract metadata from archive filename.

    Parses the archive filename to recover URL slug, timestamp,
    and hash prefix. Useful for inventory/audit purposes.

    Args:
        archive_path: Path to archived HTML file

    Returns:
        Dict with extracted metadata, or None if parse fails:
            - filename: Original filename
            - url_slug: URL path slug
            - timestamp: Sanitized timestamp
            - hash_prefix: First 8 chars of content hash
            - file_size_bytes: File size
    """
    path = Path(archive_path)
    if not path.exists():
        return None

    filename = path.name
    # Remove .html extension
    if filename.endswith(".html"):
        base = filename[:-5]
    else:
        base = filename

    # Split on last two dashes (hash-prefix is 8 chars)
    # Format: {url_slug}-{timestamp}-{hash_prefix}
    parts = base.rsplit("-", 1)
    if len(parts) != 2 or len(parts[1]) != 8:
        return None

    hash_prefix = parts[1]
    remainder = parts[0]

    # Find timestamp (ISO format with dashes instead of colons)
    # Pattern: YYYY-MM-DDTHH-MM-SS
    timestamp_pattern = r"-(\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}[^-]*)$"
    match = re.search(timestamp_pattern, remainder)
    if not match:
        return None

    timestamp = match.group(1)
    url_slug = remainder[: match.start()]

    return {
        "filename": filename,
        "url_slug": url_slug,
        "timestamp": timestamp,
        "hash_prefix": hash_prefix,
        "file_size_bytes": path.stat().st_size,
    }
