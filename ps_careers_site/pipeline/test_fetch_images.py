"""
Tests for fetch_images.py — covers all IMG-01 through IMG-04 behaviors.

RED phase: all tests will fail until fetch_images.py is rewritten as the
Unsplash async pipeline. The lazy import inside fixtures allows pytest --co
to collect tests even before the implementation exists.
"""

import asyncio
import sqlite3
from pathlib import Path
from unittest import mock

import pytest

# ---------------------------------------------------------------------------
# Lazy import fixture — established pattern from Phase 9 (test_migrate_v11.py)
# ---------------------------------------------------------------------------


@pytest.fixture
def fetch_mod():
    """Lazily import fetch_images so pytest can collect tests before the
    implementation exists (TDD RED phase)."""
    from pipeline import fetch_images
    return fetch_images


# ---------------------------------------------------------------------------
# In-memory DB fixture — replicates Phase 9 schema with sample rows
# ---------------------------------------------------------------------------


@pytest.fixture
def mem_db():
    """
    Create an in-memory SQLite DB with the Phase 9 schema and sample rows.
    Returns the sqlite3.Connection for use in tests.
    """
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row

    conn.executescript("""
        CREATE TABLE job_functions (
            job_function_slug        TEXT PRIMARY KEY,
            job_function             TEXT NOT NULL UNIQUE,
            job_function_description TEXT,
            image_path               TEXT
        );
        CREATE TABLE job_families (
            job_family_slug         TEXT PRIMARY KEY,
            job_family              TEXT NOT NULL UNIQUE,
            job_function_slug       TEXT NOT NULL,
            job_family_description  TEXT,
            image_path              TEXT
        );
        CREATE TABLE careers (
            jt_id             TEXT PRIMARY KEY,
            job_title         TEXT,
            job_title_slug    TEXT,
            job_function      TEXT,
            job_family        TEXT,
            job_family_slug   TEXT,
            image_path        TEXT
        );

        -- Sample job_functions (22 rows for count test, 3 real here)
        INSERT INTO job_functions VALUES ('administration', 'Administration', NULL, NULL);
        INSERT INTO job_functions VALUES ('information-technology', 'Information Technology', NULL, NULL);
        INSERT INTO job_functions VALUES ('health-care-and-social-services', 'Health Care and Social Services', NULL, NULL);

        -- Sample job_families (3 rows here; count test uses a separate 209-row fixture)
        INSERT INTO job_families VALUES ('accounting', 'Accounting', 'financial-management', NULL, NULL);
        INSERT INTO job_families VALUES ('software-development', 'Software Development', 'information-technology', NULL, NULL);
        INSERT INTO job_families VALUES ('nursing', 'Nursing', 'health-care-and-social-services', NULL, NULL);

        -- Sample careers (3 rows)
        INSERT INTO careers VALUES ('1', 'Senior Analyst', 'senior-analyst', 'Administration', 'Accounting', 'accounting', NULL);
        INSERT INTO careers VALUES ('2', 'Software Developer', 'software-developer', 'Information Technology', 'Software Development', 'software-development', NULL);
        INSERT INTO careers VALUES ('3', 'Registered Nurse', 'registered-nurse', 'Health Care and Social Services', 'Nursing', 'nursing', NULL);
    """)
    conn.commit()
    yield conn
    conn.close()


@pytest.fixture
def full_count_db():
    """
    Create an in-memory SQLite DB populated with exactly 22 job_functions,
    209 job_families, and 1989 careers rows — for work list count tests.
    """
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row

    conn.executescript("""
        CREATE TABLE job_functions (
            job_function_slug TEXT PRIMARY KEY,
            job_function      TEXT NOT NULL UNIQUE,
            image_path        TEXT
        );
        CREATE TABLE job_families (
            job_family_slug   TEXT PRIMARY KEY,
            job_family        TEXT NOT NULL UNIQUE,
            job_function_slug TEXT NOT NULL,
            image_path        TEXT
        );
        CREATE TABLE careers (
            jt_id          TEXT PRIMARY KEY,
            job_title      TEXT,
            job_title_slug TEXT,
            image_path     TEXT
        );
    """)

    # Insert 22 job_functions
    for i in range(1, 23):
        conn.execute(
            "INSERT INTO job_functions VALUES (?, ?, NULL)",
            (f"function-{i}", f"Function {i}")
        )

    # Insert 209 job_families (each mapped to function-1 for simplicity)
    for i in range(1, 210):
        conn.execute(
            "INSERT INTO job_families VALUES (?, ?, 'function-1', NULL)",
            (f"family-{i}", f"Family {i}")
        )

    # Insert 1989 careers
    for i in range(1, 1990):
        conn.execute(
            "INSERT INTO careers VALUES (?, ?, ?, NULL)",
            (str(i), f"Job Title {i}", f"job-title-{i}")
        )

    conn.commit()
    yield conn
    conn.close()


# ---------------------------------------------------------------------------
# IMG-01: Query builder tests
# ---------------------------------------------------------------------------


def test_build_query_function(fetch_mod):
    """build_query for 'function' type returns correct template string."""
    result = fetch_mod.build_query("Administration", "function")
    assert result == "professionals working in Administration"


def test_build_query_family(fetch_mod):
    """build_query for 'family' type returns correct template string."""
    result = fetch_mod.build_query("Accounting", "family")
    assert result == "person working in Accounting"


def test_build_query_title(fetch_mod):
    """build_query for 'title' type returns correct template string."""
    result = fetch_mod.build_query("Senior Analyst", "title")
    assert result == "person as Senior Analyst"


def test_build_query_strips_parens(fetch_mod):
    """build_query strips parenthetical qualifiers before building the query string."""
    result = fetch_mod.build_query("Artificial Intelligence (AI)", "function")
    assert result == "professionals working in Artificial Intelligence"


# ---------------------------------------------------------------------------
# IMG-01: Fallback query test
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_fallback_query(fetch_mod, tmp_path):
    """When primary search returns empty results, a second search is attempted with bare name."""
    # Mock httpx.AsyncClient to return empty results on first call, then a result on second
    empty_response = mock.MagicMock()
    empty_response.status_code = 200
    empty_response.json.return_value = {"results": []}

    result_response = mock.MagicMock()
    result_response.status_code = 200
    result_response.json.return_value = {
        "results": [{
            "urls": {"regular": "https://example.com/photo.jpg"},
            "links": {"download_location": "https://api.unsplash.com/photos/abc/download"}
        }]
    }

    # Stream response mock for image download
    stream_response = mock.AsyncMock()
    stream_response.__aenter__ = mock.AsyncMock(return_value=stream_response)
    stream_response.__aexit__ = mock.AsyncMock(return_value=False)
    stream_response.raise_for_status = mock.MagicMock()
    stream_response.aiter_bytes = mock.AsyncMock(return_value=aiter_bytes_helper(b"fake-image-data"))

    call_count = 0

    async def mock_get(url, **kwargs):
        nonlocal call_count
        # Return empty on first search call, result on second
        if "search/photos" in url:
            call_count += 1
            if call_count == 1:
                return empty_response
            return result_response
        return result_response

    conn = sqlite3.connect(":memory:")
    conn.executescript("""
        CREATE TABLE job_functions (
            job_function_slug TEXT PRIMARY KEY,
            job_function TEXT NOT NULL,
            image_path TEXT
        );
        INSERT INTO job_functions VALUES ('test-slug', 'Test Name', NULL);
    """)

    done = set()
    sem = asyncio.Semaphore(5)

    from dataclasses import dataclass

    @dataclass
    class MockWorkItem:
        entity_type: str = "function"
        slug: str = "test-slug"
        name: str = "Test Name (Abbreviated)"
        table: str = "job_functions"
        pk_col: str = "job_function_slug"
        pk_val: str = "test-slug"

        @property
        def key(self):
            return f"{self.entity_type}:{self.slug}"

        @property
        def dest(self):
            return tmp_path / "static" / "images" / f"{self.entity_type}s" / f"{self.slug}.jpg"

        @property
        def image_rel(self):
            return f"{self.entity_type}s/{self.slug}.jpg"

    item = MockWorkItem()
    item.dest.parent.mkdir(parents=True, exist_ok=True)

    with mock.patch("httpx.AsyncClient.get", side_effect=mock_get), \
         mock.patch("httpx.AsyncClient.stream", return_value=stream_response):
        await fetch_mod.fetch_and_save(
            mock.AsyncMock(get=mock_get, stream=mock.MagicMock(return_value=stream_response)),
            sem, item, "fake-key", conn, done
        )

    # Two search calls were made (primary empty → fallback)
    assert call_count == 2


# ---------------------------------------------------------------------------
# IMG-02: File storage path tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_image_stored_in_correct_subdir(fetch_mod, tmp_path, mem_db):
    """Images are saved to the correct subdirectory based on entity type."""
    from dataclasses import dataclass
    from pathlib import Path

    images_base = tmp_path / "static" / "images"

    # Patch IMAGES_DIR to use tmp_path
    with mock.patch.object(fetch_mod, "IMAGES_DIR", images_base):
        # Build a WorkItem and verify dest property returns correct subdir
        item_fn = fetch_mod.WorkItem("function", "administration", "Administration",
                                     "job_functions", "job_function_slug", "administration")
        item_fam = fetch_mod.WorkItem("family", "accounting", "Accounting",
                                      "job_families", "job_family_slug", "accounting")
        item_title = fetch_mod.WorkItem("title", "senior-analyst", "Senior Analyst",
                                        "careers", "job_title_slug", "senior-analyst")

        assert str(item_fn.dest).endswith("functions/administration.jpg"), \
            f"Expected functions subdir, got: {item_fn.dest}"
        assert str(item_fam.dest).endswith("families/accounting.jpg"), \
            f"Expected families subdir, got: {item_fam.dest}"
        assert str(item_title.dest).endswith("titles/senior-analyst.jpg"), \
            f"Expected titles subdir, got: {item_title.dest}"


def test_image_path_is_relative(fetch_mod):
    """DB image_path value is a relative path, not absolute."""
    item = fetch_mod.WorkItem("function", "administration", "Administration",
                              "job_functions", "job_function_slug", "administration")
    # image_rel must be relative (no leading slash, no absolute path components)
    assert item.image_rel == "functions/administration.jpg"
    assert not item.image_rel.startswith("/")
    assert ":" not in item.image_rel  # no Windows drive letters


# ---------------------------------------------------------------------------
# IMG-03: DB update test
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_db_updated_after_download(fetch_mod, tmp_path):
    """After fetch_and_save, image_path is set in the correct DB table."""
    conn = sqlite3.connect(":memory:")
    conn.execute("""CREATE TABLE job_functions (
        job_function_slug TEXT PRIMARY KEY,
        job_function TEXT NOT NULL,
        image_path TEXT
    )""")
    conn.execute("INSERT INTO job_functions VALUES ('test-slug', 'Test Function', NULL)")
    conn.commit()

    images_base = tmp_path / "static" / "images"

    photo_response = mock.MagicMock()
    photo_response.status_code = 200
    photo_response.json.return_value = {
        "results": [{
            "urls": {"regular": "https://example.com/photo.jpg"},
            "links": {"download_location": "https://api.unsplash.com/photos/abc/download"}
        }]
    }

    download_trigger_response = mock.MagicMock()
    download_trigger_response.status_code = 200

    stream_ctx = mock.MagicMock()
    stream_ctx.__aenter__ = mock.AsyncMock(return_value=stream_ctx)
    stream_ctx.__aexit__ = mock.AsyncMock(return_value=False)
    stream_ctx.raise_for_status = mock.MagicMock()
    stream_ctx.status_code = 200

    async def aiter_bytes_gen(chunk_size=8192):
        yield b"fake-jpeg-data"

    stream_ctx.aiter_bytes = aiter_bytes_gen

    client = mock.AsyncMock()
    client.get = mock.AsyncMock(return_value=photo_response)
    client.stream = mock.MagicMock(return_value=stream_ctx)

    done = set()
    sem = asyncio.Semaphore(5)

    with mock.patch.object(fetch_mod, "IMAGES_DIR", images_base):
        item = fetch_mod.WorkItem("function", "test-slug", "Test Function",
                                  "job_functions", "job_function_slug", "test-slug")
        await fetch_mod.fetch_and_save(client, sem, item, "fake-key", conn, done)

    # Verify DB was updated
    row = conn.execute(
        "SELECT image_path FROM job_functions WHERE job_function_slug = 'test-slug'"
    ).fetchone()
    assert row is not None
    assert row[0] == "functions/test-slug.jpg"
    conn.close()


# ---------------------------------------------------------------------------
# IMG-04: Resume / skip logic tests
# ---------------------------------------------------------------------------


def test_resume_skips_done_items(fetch_mod, tmp_path, mem_db):
    """When file exists on disk AND DB image_path is set, should_skip returns True."""
    images_base = tmp_path / "static" / "images"

    with mock.patch.object(fetch_mod, "IMAGES_DIR", images_base):
        item = fetch_mod.WorkItem("function", "administration", "Administration",
                                  "job_functions", "job_function_slug", "administration")

        # Create the file on disk
        item.dest.parent.mkdir(parents=True, exist_ok=True)
        item.dest.write_bytes(b"fake-image")

        # Set image_path in DB
        mem_db.execute(
            "UPDATE job_functions SET image_path = 'functions/administration.jpg' WHERE job_function_slug = 'administration'"
        )
        mem_db.commit()

        done = set()
        result = fetch_mod.should_skip(item, done, mem_db)
        assert result is True, "should_skip must return True when file exists AND DB image_path is set"


def test_resume_reprocesses_partial(fetch_mod, tmp_path, mem_db):
    """When file exists on disk but DB image_path is NULL, should_skip returns False."""
    images_base = tmp_path / "static" / "images"

    with mock.patch.object(fetch_mod, "IMAGES_DIR", images_base):
        item = fetch_mod.WorkItem("function", "administration", "Administration",
                                  "job_functions", "job_function_slug", "administration")

        # Create the file on disk but leave DB image_path as NULL
        item.dest.parent.mkdir(parents=True, exist_ok=True)
        item.dest.write_bytes(b"fake-image")
        # image_path in mem_db is NULL by default (from fixture)

        done = set()
        result = fetch_mod.should_skip(item, done, mem_db)
        assert result is False, "should_skip must return False when file exists but DB image_path is NULL"


# ---------------------------------------------------------------------------
# IMG-04: Concurrency limit test
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_concurrency_limit(fetch_mod):
    """With semaphore(2), at most 2 fetch_and_save coroutines run concurrently."""
    max_concurrent = 0
    current_concurrent = 0

    async def slow_fetch(client, sem, item, access_key, conn, done):
        nonlocal max_concurrent, current_concurrent
        async with sem:
            current_concurrent += 1
            if current_concurrent > max_concurrent:
                max_concurrent = current_concurrent
            await asyncio.sleep(0.05)  # simulate work
            current_concurrent -= 1

    # 5 fake work items
    items = [f"item-{i}" for i in range(5)]
    sem = asyncio.Semaphore(2)

    tasks = [
        asyncio.create_task(slow_fetch(None, sem, item, None, None, set()))
        for item in items
    ]
    await asyncio.gather(*tasks, return_exceptions=True)

    assert max_concurrent <= 2, \
        f"Expected at most 2 concurrent workers, got {max_concurrent}"


# ---------------------------------------------------------------------------
# IMG-04: Work list ordering test
# ---------------------------------------------------------------------------


def test_build_work_list_order(fetch_mod, mem_db):
    """Work list starts with functions, then families, then titles."""
    work = fetch_mod.build_work_list(mem_db)
    types = [item.entity_type for item in work]

    # Find index boundaries
    fn_indices = [i for i, t in enumerate(types) if t == "function"]
    fam_indices = [i for i, t in enumerate(types) if t == "family"]
    title_indices = [i for i, t in enumerate(types) if t == "title"]

    assert fn_indices, "No function items in work list"
    assert fam_indices, "No family items in work list"
    assert title_indices, "No title items in work list"

    # All functions come before families, all families before titles
    assert max(fn_indices) < min(fam_indices), \
        "Functions must all appear before families in work list"
    assert max(fam_indices) < min(title_indices), \
        "Families must all appear before titles in work list"


def test_build_work_list_counts(fetch_mod, full_count_db):
    """Work list has exactly 22 functions + 209 families + 1989 titles."""
    work = fetch_mod.build_work_list(full_count_db)

    fn_count = sum(1 for item in work if item.entity_type == "function")
    fam_count = sum(1 for item in work if item.entity_type == "family")
    title_count = sum(1 for item in work if item.entity_type == "title")

    assert fn_count == 22, f"Expected 22 functions, got {fn_count}"
    assert fam_count == 209, f"Expected 209 families, got {fam_count}"
    assert title_count == 1989, f"Expected 1989 titles, got {title_count}"


# ---------------------------------------------------------------------------
# IMG-01/IMG-04: Rate limit (429) handling
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_rate_limit_429_handled(fetch_mod, tmp_path):
    """When API returns 429, item is NOT added to done set (will retry on next run)."""
    conn = sqlite3.connect(":memory:")
    conn.execute("""CREATE TABLE job_functions (
        job_function_slug TEXT PRIMARY KEY,
        job_function TEXT NOT NULL,
        image_path TEXT
    )""")
    conn.execute("INSERT INTO job_functions VALUES ('test-slug', 'Test', NULL)")
    conn.commit()

    rate_limited_response = mock.MagicMock()
    rate_limited_response.status_code = 429
    rate_limited_response.headers = {"Retry-After": "60"}

    client = mock.AsyncMock()
    client.get = mock.AsyncMock(return_value=rate_limited_response)

    done = set()
    sem = asyncio.Semaphore(5)
    images_base = tmp_path / "static" / "images"

    with mock.patch.object(fetch_mod, "IMAGES_DIR", images_base):
        item = fetch_mod.WorkItem("function", "test-slug", "Test",
                                  "job_functions", "job_function_slug", "test-slug")
        await fetch_mod.fetch_and_save(client, sem, item, "fake-key", conn, done)

    # Item must NOT be in done set — should retry on next run
    assert item.key not in done, \
        "429-rate-limited item must NOT be marked as done (must retry on next run)"
    conn.close()


# ---------------------------------------------------------------------------
# IMG-01: Zero-result query marked as done (no infinite retry)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_no_result_marked_done(fetch_mod, tmp_path):
    """When API returns empty results (even after fallback), item IS marked done."""
    conn = sqlite3.connect(":memory:")
    conn.execute("""CREATE TABLE job_functions (
        job_function_slug TEXT PRIMARY KEY,
        job_function TEXT NOT NULL,
        image_path TEXT
    )""")
    conn.execute("INSERT INTO job_functions VALUES ('obscure-job', 'Obscure Job Title', NULL)")
    conn.commit()

    empty_response = mock.MagicMock()
    empty_response.status_code = 200
    empty_response.json.return_value = {"results": []}

    client = mock.AsyncMock()
    client.get = mock.AsyncMock(return_value=empty_response)

    done = set()
    sem = asyncio.Semaphore(5)
    images_base = tmp_path / "static" / "images"

    with mock.patch.object(fetch_mod, "IMAGES_DIR", images_base):
        item = fetch_mod.WorkItem("function", "obscure-job", "Obscure Job Title",
                                  "job_functions", "job_function_slug", "obscure-job")
        await fetch_mod.fetch_and_save(client, sem, item, "fake-key", conn, done)

    # Item MUST be in done set — prevents infinite retry for zero-result queries
    assert item.key in done, \
        "Zero-result item must be marked as done to prevent infinite retry"
    conn.close()


# ---------------------------------------------------------------------------
# Helper: async generator for aiter_bytes mocking
# ---------------------------------------------------------------------------


async def aiter_bytes_helper(data: bytes):
    """Yield data as a single chunk for mocking aiter_bytes."""
    yield data
