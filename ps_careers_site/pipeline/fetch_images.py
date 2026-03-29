#!/usr/bin/env python3
"""
fetch_images.py — Async Unsplash image pipeline for DND Civilian Careers.

Usage (from ps_careers_site/ directory):
    python pipeline/fetch_images.py                     # fetch all 2,221 images
    python pipeline/fetch_images.py --type function     # fetch 22 function images only (safe for Demo key)
    python pipeline/fetch_images.py --limit 5           # fetch first 5 items only
    python pipeline/fetch_images.py --dry-run           # print work list, no API calls

Requirements:
    - Set UNSPLASH_ACCESS_KEY environment variable (Demo: 50 req/hr, Production: 1,000 req/hr)
    - pip install httpx (already installed as FastAPI dependency)

Resume:
    Completed items tracked in pipeline/fetch_images_progress.json.
    Re-running skips items where local file exists AND DB image_path is set.

Rate limits:
    Demo key: 50 req/hr — use --type function (22 items) or --limit N for testing.
    Production key: 1,000 req/hr — safe for all 2,221 items at 5 concurrent workers.
    On HTTP 429: logs Retry-After, does NOT mark item as done, exits cleanly.
"""

import argparse
import asyncio
import json
import logging
import os
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path

import httpx

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).parent.parent  # ps_careers_site/
DB_PATH = BASE_DIR / "careers.sqlite"
IMAGES_DIR = BASE_DIR / "static" / "images"
PROGRESS_FILE = Path(__file__).parent / "fetch_images_progress.json"
UNSPLASH_SEARCH_URL = "https://api.unsplash.com/search/photos"


# ---------------------------------------------------------------------------
# WorkItem dataclass
# ---------------------------------------------------------------------------


@dataclass
class WorkItem:
    """Represents a single entity to fetch an image for."""
    entity_type: str  # "function", "family", "title"
    slug: str
    name: str
    table: str         # "job_functions", "job_families", "careers"
    pk_col: str        # "job_function_slug", "job_family_slug", "job_title_slug"
    pk_val: str

    @property
    def key(self) -> str:
        """Unique progress key for this work item."""
        return f"{self.entity_type}:{self.slug}"

    @property
    def _subdir(self) -> str:
        """Subdirectory name for this entity type (handles irregular plural 'families')."""
        return {"function": "functions", "family": "families", "title": "titles"}[self.entity_type]

    @property
    def dest(self) -> Path:
        """Absolute path where the image file should be saved."""
        return IMAGES_DIR / self._subdir / f"{self.slug}.jpg"

    @property
    def image_rel(self) -> str:
        """Relative path stored in DB (relative to static/images/)."""
        return f"{self._subdir}/{self.slug}.jpg"


# ---------------------------------------------------------------------------
# Query builders
# ---------------------------------------------------------------------------


def build_query(name: str, entity_type: str) -> str:
    """
    Build a job-relevant Unsplash search query for the given entity.

    Strips parenthetical qualifiers (e.g., "(AI)") before building the query.
    Templates per entity type:
    - function: "professionals working in {name}"
    - family:   "person working in {name}"
    - title:    "person as {name}"
    """
    clean = re.sub(r"\s*\([^)]*\)", "", name).strip()
    if entity_type == "title":
        return f"person as {clean}"
    elif entity_type == "family":
        return f"person working in {clean}"
    else:  # function
        return f"professionals working in {clean}"


def fallback_query(name: str) -> str:
    """Simpler bare-name fallback when the primary query returns no results."""
    return re.sub(r"\s*\([^)]*\)", "", name).strip()


# ---------------------------------------------------------------------------
# Unsplash API helpers
# ---------------------------------------------------------------------------


async def search_unsplash(
    client: httpx.AsyncClient,
    query: str,
    access_key: str,
) -> dict | None:
    """
    Search Unsplash for a landscape photo matching query.

    Returns the first result dict (with urls/links keys) or None.
    Caller handles 429 status — this function raises for other HTTP errors.
    """
    resp = await client.get(
        UNSPLASH_SEARCH_URL,
        headers={"Authorization": f"Client-ID {access_key}"},
        params={
            "query": query,
            "per_page": 5,
            "orientation": "landscape",
            "content_filter": "high",
        },
    )
    if resp.status_code == 429:
        return resp  # Return response object so caller can read Retry-After header
    resp.raise_for_status()
    results = resp.json().get("results", [])
    return results[0] if results else None


async def trigger_download(
    client: httpx.AsyncClient,
    download_location: str,
    access_key: str,
) -> None:
    """
    Fire-and-forget download tracking call required by Unsplash ToS.

    Must be called when a photo is saved. Non-fatal if it fails.
    """
    try:
        await client.get(
            download_location,
            headers={"Authorization": f"Client-ID {access_key}"},
        )
    except Exception:
        pass  # Non-fatal — do not block image save


# ---------------------------------------------------------------------------
# Skip logic (resume)
# ---------------------------------------------------------------------------


def should_skip(item: WorkItem, done: set, conn: sqlite3.Connection) -> bool:
    """
    Determine whether an item should be skipped (already complete).

    Skip condition requires BOTH:
    - Local image file exists on disk, AND
    - DB image_path is not NULL

    If only one condition is true (partial state), return False to reprocess.
    This ensures consistency between file system and DB (per D-05).
    """
    if item.key in done:
        return True
    if item.dest.exists():
        row = conn.execute(
            f"SELECT image_path FROM {item.table} WHERE {item.pk_col} = ?",
            (item.pk_val,),
        ).fetchone()
        if row and row[0]:
            done.add(item.key)  # Sync progress set
            return True
    return False


# ---------------------------------------------------------------------------
# Main fetch-and-save coroutine
# ---------------------------------------------------------------------------


async def fetch_and_save(
    client: httpx.AsyncClient,
    sem: asyncio.Semaphore,
    item: WorkItem,
    access_key: str,
    conn: sqlite3.Connection,
    done: set,
) -> None:
    """
    Fetch an image from Unsplash and save it locally, then update the DB.

    Uses the semaphore to limit concurrent requests to `workers` at a time.
    Handles:
    - 429 rate limit: logs Retry-After, does NOT mark done (retries on next run)
    - Empty results: tries fallback query; if still empty, marks done (no infinite retry)
    - Successful fetch: saves file, updates DB, adds to done set
    """
    async with sem:
        # --- Primary search ---
        primary_query = build_query(item.name, item.entity_type)
        result = await search_unsplash(client, primary_query, access_key)

        # --- Handle 429 ---
        if hasattr(result, "status_code") and result.status_code == 429:
            retry_after = result.headers.get("Retry-After", "unknown")
            logger.warning(
                "Rate limited (429) for %s:%s — Retry-After: %ss. Item NOT marked done.",
                item.entity_type, item.slug, retry_after
            )
            return  # Do NOT add to done set — will retry on next run

        # --- Fallback query if no results ---
        if result is None:
            fb_query = fallback_query(item.name)
            if fb_query and fb_query != primary_query:
                logger.info(
                    "No results for primary query %r — retrying with fallback %r",
                    primary_query, fb_query
                )
                result = await search_unsplash(client, fb_query, access_key)

                # Check fallback for 429 too
                if hasattr(result, "status_code") and result.status_code == 429:
                    retry_after = result.headers.get("Retry-After", "unknown")
                    logger.warning(
                        "Rate limited (429) on fallback for %s:%s — Retry-After: %ss.",
                        item.entity_type, item.slug, retry_after
                    )
                    return  # Do NOT add to done set

        # --- Still no results after fallback ---
        if result is None:
            logger.warning("No photo found for %s:%s — marking done (no infinite retry)", item.entity_type, item.slug)
            done.add(item.key)
            save_progress(done)
            return

        photo = result

        # --- Trigger download (Unsplash ToS requirement) ---
        await trigger_download(client, photo["links"]["download_location"], access_key)

        # --- Download image ---
        async with client.stream("GET", photo["urls"]["regular"]) as img_resp:
            img_resp.raise_for_status()
            data = b""
            async for chunk in img_resp.aiter_bytes(8192):
                data += chunk

        # --- Save to disk (blocking I/O in thread pool) ---
        await asyncio.to_thread(item.dest.parent.mkdir, parents=True, exist_ok=True)
        await asyncio.to_thread(item.dest.write_bytes, data)

        # --- Update DB ---
        conn.execute(
            f"UPDATE {item.table} SET image_path = ? WHERE {item.pk_col} = ?",
            (item.image_rel, item.pk_val),
        )
        conn.commit()

        # --- Mark done (AFTER DB commit, per Pitfall 3) ---
        done.add(item.key)
        save_progress(done)

        logger.info("OK  %s:%s -> %s", item.entity_type, item.slug, item.image_rel)


# ---------------------------------------------------------------------------
# Work list builder
# ---------------------------------------------------------------------------


def build_work_list(conn: sqlite3.Connection) -> list[WorkItem]:
    """
    Build the ordered work list: functions first, then families, then titles.

    Reads from the new Phase 9 tables (job_functions, job_families) rather than
    querying DISTINCT from careers — these are the authoritative tables.
    """
    work = []

    # Functions (22) — from job_functions table
    for row in conn.execute(
        "SELECT job_function_slug, job_function FROM job_functions ORDER BY job_function"
    ):
        work.append(WorkItem(
            entity_type="function",
            slug=row[0],
            name=row[1],
            table="job_functions",
            pk_col="job_function_slug",
            pk_val=row[0],
        ))

    # Families (209) — from job_families table
    for row in conn.execute(
        "SELECT job_family_slug, job_family FROM job_families ORDER BY job_family"
    ):
        work.append(WorkItem(
            entity_type="family",
            slug=row[0],
            name=row[1],
            table="job_families",
            pk_col="job_family_slug",
            pk_val=row[0],
        ))

    # Titles (1,989) — from careers table
    for row in conn.execute(
        "SELECT job_title_slug, job_title FROM careers ORDER BY job_title"
    ):
        work.append(WorkItem(
            entity_type="title",
            slug=row[0],
            name=row[1],
            table="careers",
            pk_col="job_title_slug",
            pk_val=row[0],
        ))

    return work


# ---------------------------------------------------------------------------
# Progress tracking
# ---------------------------------------------------------------------------


def load_progress() -> set:
    """Load the set of completed item keys from the progress JSON file."""
    if PROGRESS_FILE.exists():
        data = json.loads(PROGRESS_FILE.read_text())
        return set(data.get("done", []))
    return set()


def save_progress(done: set) -> None:
    """Persist the completed item keys set to the progress JSON file."""
    PROGRESS_FILE.write_text(json.dumps({"done": sorted(done)}, indent=2))


# ---------------------------------------------------------------------------
# Pipeline runner
# ---------------------------------------------------------------------------


async def run_pipeline(
    entity_type: str = "all",
    workers: int = 5,
    limit: int | None = None,
    dry_run: bool = False,
) -> None:
    """
    Run the Unsplash image fetch pipeline.

    Args:
        entity_type: "function", "family", "title", or "all"
        workers: max concurrent API requests (semaphore bound)
        limit: process only first N items (useful for Demo key testing)
        dry_run: print work list without making any API calls
    """
    # Validate env
    access_key = os.environ.get("UNSPLASH_ACCESS_KEY")
    if not access_key:
        raise RuntimeError(
            "Set UNSPLASH_ACCESS_KEY environment variable.\n"
            "Get your key at: https://unsplash.com/oauth/applications"
        )

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row

    work = build_work_list(conn)

    # Filter by entity type if requested
    if entity_type != "all":
        work = [item for item in work if item.entity_type == entity_type]

    done = load_progress()

    # Filter to items not already done
    remaining = [item for item in work if not should_skip(item, done, conn)]

    if limit is not None:
        remaining = remaining[:limit]

    total = len(work)
    skipped = total - len(remaining) if entity_type == "all" else len(work) - len(remaining)

    if dry_run:
        logger.info("DRY RUN — %d items would be processed:", len(remaining))
        for item in remaining:
            logger.info("  %s:%s  (%s)", item.entity_type, item.slug, item.name)
        conn.close()
        return

    logger.info(
        "Total: %d | Skipped (done): %d | To process: %d | Workers: %d",
        total, len(done), len(remaining), workers
    )
    logger.info("Images → %s", IMAGES_DIR)
    logger.info("Progress saved to %s (safe to Ctrl+C and resume)", PROGRESS_FILE)
    logger.info("-" * 60)

    sem = asyncio.Semaphore(workers)

    async with httpx.AsyncClient(timeout=30.0) as client:
        tasks = [
            asyncio.create_task(
                fetch_and_save(client, sem, item, access_key, conn, done)
            )
            for item in remaining
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    # Log any unhandled exceptions
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error("Task %d failed: %s", i, result)

    conn.close()
    logger.info("=" * 60)
    logger.info("Complete. %d items in done set.", len(done))


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """Command-line entry point."""
    parser = argparse.ArgumentParser(
        description="Bulk Unsplash image downloader for DND Civilian Careers site"
    )
    parser.add_argument(
        "--type",
        choices=["function", "family", "title", "all"],
        default="all",
        help="Which entity type to process (default: all). Use 'function' for Demo key testing (22 items).",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=5,
        help="Number of concurrent download workers (default: 5)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Process only the first N items (useful for Demo key testing)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Print work list without making any API calls",
    )
    args = parser.parse_args()

    asyncio.run(run_pipeline(
        entity_type=args.type,
        workers=args.workers,
        limit=args.limit,
        dry_run=args.dry_run,
    ))


if __name__ == "__main__":
    main()
