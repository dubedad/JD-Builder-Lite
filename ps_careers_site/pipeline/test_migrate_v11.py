"""
Tests for migrate_v11.py — covers all DATA-* requirements + idempotency.

RED phase: all tests will fail until migrate_v11.py is created (Task 2).
The lazy import inside the migrated_db fixture allows pytest --co to collect
tests even before migrate_v11.py exists.
"""

import shutil
import sqlite3
from pathlib import Path

import pytest

# Module-level constant — canonical CSV path in JobForge repo
CSV_PATH = Path(r"C:\Users\Administrator\Projects\jobforge\data\reference\enriched_job_architecture.csv")

# Path to source DB (copied into tmp for each test run)
_HERE = Path(__file__).parent.parent  # ps_careers_site/
SOURCE_DB = _HERE / "careers.sqlite"


@pytest.fixture(scope="session")
def migrated_db(tmp_path_factory):
    """
    Copy the real careers.sqlite into a temp dir, run migration against the
    copy, and return the path. Session-scoped so migration runs once per test
    session.

    CRITICAL: The import of run_migration is LAZY (inside this fixture body),
    not at module top level. This allows pytest --co to collect tests even
    before migrate_v11.py exists (RED phase). A top-level import would cause
    ModuleNotFoundError at collection time.
    """
    from pipeline.migrate_v11 import run_migration  # noqa: PLC0415 — intentional lazy import

    tmp_path = tmp_path_factory.mktemp("db")
    db_copy = tmp_path / "careers.sqlite"
    shutil.copy(SOURCE_DB, db_copy)
    run_migration(db_path=db_copy, csv_path=CSV_PATH)
    return db_copy


@pytest.fixture(scope="session")
def db_conn(migrated_db):
    """Open a sqlite3 connection to the migrated DB. Session-scoped."""
    conn = sqlite3.connect(str(migrated_db))
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


# ---------------------------------------------------------------------------
# Schema tests
# ---------------------------------------------------------------------------

def test_job_functions_table_schema(db_conn):
    """job_functions must have exactly the expected columns with correct types."""
    cols = {row["name"]: row for row in db_conn.execute("PRAGMA table_info(job_functions)").fetchall()}
    assert "job_function_slug" in cols, "Missing column: job_function_slug"
    assert "job_function" in cols, "Missing column: job_function"
    assert "job_function_description" in cols, "Missing column: job_function_description"
    assert "image_path" in cols, "Missing column: image_path"
    # job_function_slug must be the primary key
    assert cols["job_function_slug"]["pk"] == 1, "job_function_slug must be PRIMARY KEY"


def test_job_families_table_schema(db_conn):
    """job_families must have exactly the expected columns with correct types."""
    cols = {row["name"]: row for row in db_conn.execute("PRAGMA table_info(job_families)").fetchall()}
    assert "job_family_slug" in cols, "Missing column: job_family_slug"
    assert "job_family" in cols, "Missing column: job_family"
    assert "job_function_slug" in cols, "Missing column: job_function_slug (FK)"
    assert "job_family_description" in cols, "Missing column: job_family_description"
    assert "image_path" in cols, "Missing column: image_path"
    # job_family_slug must be the primary key
    assert cols["job_family_slug"]["pk"] == 1, "job_family_slug must be PRIMARY KEY"


def test_careers_new_columns(db_conn):
    """careers table must include the 5 new v1.1 columns."""
    col_names = {row["name"] for row in db_conn.execute("PRAGMA table_info(careers)").fetchall()}
    for expected_col in [
        "job_title_description",
        "key_responsibilities",
        "required_skills",
        "typical_education",
        "image_path",
    ]:
        assert expected_col in col_names, f"Missing column in careers: {expected_col}"


# ---------------------------------------------------------------------------
# Row count tests
# ---------------------------------------------------------------------------

def test_job_functions_count(db_conn):
    """Must have exactly 22 job function rows (22 distinct non-blank functions in CSV)."""
    count = db_conn.execute("SELECT COUNT(*) FROM job_functions").fetchone()[0]
    assert count == 22, f"Expected 22 job_functions rows, got {count}"


def test_job_functions_have_slugs(db_conn):
    """Every job_function row must have a non-null, non-empty slug."""
    count = db_conn.execute(
        "SELECT COUNT(*) FROM job_functions WHERE job_function_slug IS NULL OR job_function_slug = ''"
    ).fetchone()[0]
    assert count == 0, f"Found {count} job_functions rows with missing slug"


def test_job_families_count(db_conn):
    """Must have exactly 209 job family rows (209 distinct families with non-blank function in CSV)."""
    count = db_conn.execute("SELECT COUNT(*) FROM job_families").fetchone()[0]
    assert count == 209, f"Expected 209 job_families rows, got {count}"


def test_job_families_fk_integrity(db_conn):
    """Every job_families.job_function_slug must have a matching job_functions row."""
    orphan_count = db_conn.execute("""
        SELECT COUNT(*)
        FROM job_families jf
        LEFT JOIN job_functions jfn ON jf.job_function_slug = jfn.job_function_slug
        WHERE jfn.job_function_slug IS NULL
    """).fetchone()[0]
    assert orphan_count == 0, f"Found {orphan_count} orphaned job_families (no matching job_functions FK)"


# ---------------------------------------------------------------------------
# Enrichment tests
# ---------------------------------------------------------------------------

def test_careers_enriched(db_conn):
    """All 4 enrichment columns must be non-null across all careers rows."""
    for col in ["job_title_description", "key_responsibilities", "required_skills", "typical_education"]:
        null_count = db_conn.execute(
            f"SELECT COUNT(*) FROM careers WHERE {col} IS NULL"
        ).fetchone()[0]
        assert null_count == 0, f"careers.{col} has {null_count} NULL rows (expected 0)"


# ---------------------------------------------------------------------------
# Idempotency test
# ---------------------------------------------------------------------------

def test_idempotent(tmp_path):
    """Running migration twice produces identical counts and no errors."""
    from pipeline.migrate_v11 import run_migration  # noqa: PLC0415 — intentional lazy import

    db_copy = tmp_path / "careers.sqlite"
    shutil.copy(SOURCE_DB, db_copy)

    # First run
    run_migration(db_path=db_copy, csv_path=CSV_PATH)

    conn = sqlite3.connect(str(db_copy))
    fn1 = conn.execute("SELECT COUNT(*) FROM job_functions").fetchone()[0]
    fam1 = conn.execute("SELECT COUNT(*) FROM job_families").fetchone()[0]
    enriched1 = conn.execute(
        "SELECT COUNT(*) FROM careers WHERE job_title_description IS NOT NULL"
    ).fetchone()[0]
    conn.close()

    # Second run — must not raise, must not duplicate
    run_migration(db_path=db_copy, csv_path=CSV_PATH)

    conn = sqlite3.connect(str(db_copy))
    fn2 = conn.execute("SELECT COUNT(*) FROM job_functions").fetchone()[0]
    fam2 = conn.execute("SELECT COUNT(*) FROM job_families").fetchone()[0]
    enriched2 = conn.execute(
        "SELECT COUNT(*) FROM careers WHERE job_title_description IS NOT NULL"
    ).fetchone()[0]
    conn.close()

    assert fn2 == fn1 == 22, f"job_functions count changed on re-run: {fn1} → {fn2}"
    assert fam2 == fam1 == 209, f"job_families count changed on re-run: {fam1} → {fam2}"
    assert enriched2 == enriched1 == 1989, f"enriched careers count changed on re-run: {enriched1} → {enriched2}"


# ---------------------------------------------------------------------------
# Horticulture Specialist edge case
# ---------------------------------------------------------------------------

def test_horticulture_specialist(db_conn):
    """
    JT_ID=1933 (Horticulture Specialist) has blank Job_Function and Job_Family in CSV.
    It must receive enrichment columns (key_responsibilities etc.) but must NOT
    produce entries in job_functions or job_families from its blank-function rows.

    Note: A legitimate "Horticulture" family and Environmental Services function exist
    from OTHER rows in the CSV (e.g. JT_ID=421, 430, etc.). The test verifies that
    JT_ID=1933 itself has enrichment data, and that blank-function rows do not inflate
    the function/family counts (verified by the 22/209 count tests above).
    """
    # Has enrichment data
    row = db_conn.execute(
        "SELECT job_title, key_responsibilities FROM careers WHERE jt_id = 1933"
    ).fetchone()
    assert row is not None, "JT_ID=1933 not found in careers table"
    assert row["key_responsibilities"] is not None, "Horticulture Specialist must have key_responsibilities"

    # job_functions must NOT contain a row from a blank function name (confirmed by count=22)
    # There is no job_function with empty or null slug
    fn_blank = db_conn.execute(
        "SELECT COUNT(*) FROM job_functions WHERE job_function_slug IS NULL OR job_function_slug = ''"
    ).fetchone()[0]
    assert fn_blank == 0, f"Found {fn_blank} job_functions rows with blank slug (from blank Job_Function rows)"

    # job_families must NOT contain a row with a blank function slug FK
    fam_blank_fk = db_conn.execute(
        "SELECT COUNT(*) FROM job_families WHERE job_function_slug IS NULL OR job_function_slug = ''"
    ).fetchone()[0]
    assert fam_blank_fk == 0, f"Found {fam_blank_fk} job_families rows with blank function FK"


# ---------------------------------------------------------------------------
# Guard clause tests (UAT gap closure — 09-02)
# ---------------------------------------------------------------------------

def test_guard_missing_db(tmp_path):
    """Guard must fire when careers.sqlite does not exist at the given path."""
    from pipeline.migrate_v11 import run_migration  # noqa: PLC0415

    missing_db = tmp_path / "nonexistent.sqlite"
    # DB path does not exist — guard must sys.exit(1), not raise OperationalError
    with pytest.raises(SystemExit) as exc_info:
        run_migration(db_path=missing_db, csv_path=CSV_PATH)
    assert exc_info.value.code == 1, f"Expected exit code 1, got {exc_info.value.code}"


def test_guard_empty_db(tmp_path):
    """Guard must fire when careers.sqlite exists but has no careers table."""
    from pipeline.migrate_v11 import run_migration  # noqa: PLC0415

    empty_db = tmp_path / "empty.sqlite"
    # Create an empty SQLite file with no tables
    conn = sqlite3.connect(str(empty_db))
    conn.close()

    with pytest.raises(SystemExit) as exc_info:
        run_migration(db_path=empty_db, csv_path=CSV_PATH)
    assert exc_info.value.code == 1, f"Expected exit code 1, got {exc_info.value.code}"
