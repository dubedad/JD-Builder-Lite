"""
v1.1 Data Migration: extend careers.sqlite with job_functions, job_families tables
and new columns on careers.

Usage (from ps_careers_site/ directory):
    python pipeline/migrate_v11.py
    python pipeline/migrate_v11.py --csv "C:/path/to/enriched_job_architecture.csv" --db careers.sqlite
"""

import argparse
import csv
import re
import sqlite3
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths (relative to ps_careers_site/ which is the script's parent dir)
# ---------------------------------------------------------------------------
_HERE = Path(__file__).parent.parent  # ps_careers_site/
DEFAULT_DB = _HERE / "careers.sqlite"
DEFAULT_CSV = Path(r"C:\Users\Administrator\Projects\jobforge\data\reference\enriched_job_architecture.csv")

# ---------------------------------------------------------------------------
# DDL
# ---------------------------------------------------------------------------
DDL_JOB_FUNCTIONS = """
CREATE TABLE IF NOT EXISTS job_functions (
    job_function_slug        TEXT PRIMARY KEY,
    job_function             TEXT NOT NULL UNIQUE,
    job_function_description TEXT,
    image_path               TEXT
);
"""

DDL_JOB_FAMILIES = """
CREATE TABLE IF NOT EXISTS job_families (
    job_family_slug         TEXT PRIMARY KEY,
    job_family              TEXT NOT NULL UNIQUE,
    job_function_slug       TEXT NOT NULL REFERENCES job_functions(job_function_slug),
    job_family_description  TEXT,
    image_path              TEXT
);
"""

# New columns to add to the careers table
NEW_CAREERS_COLUMNS = [
    ("job_title_description", "TEXT"),
    ("key_responsibilities",  "TEXT"),
    ("required_skills",       "TEXT"),
    ("typical_education",     "TEXT"),
    ("image_path",            "TEXT"),
]


# ---------------------------------------------------------------------------
# Slug utility — identical to ingest.py make_slug() (project standard)
# ---------------------------------------------------------------------------
def make_slug(text: str) -> str:
    s = text.lower().replace("&", "and")
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"[\s]+", "-", s.strip())
    return s.strip("-")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def column_exists(conn: sqlite3.Connection, table: str, column: str) -> bool:
    """Return True if `column` exists in `table`."""
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return any(row[1] == column for row in rows)


# ---------------------------------------------------------------------------
# Migration
# ---------------------------------------------------------------------------
def run_migration(db_path: Path, csv_path: Path) -> None:
    """
    Idempotent migration: create job_functions and job_families tables,
    add 5 new columns to careers, populate all rows from the CSV.

    Safe to run multiple times — uses CREATE TABLE IF NOT EXISTS,
    INSERT OR IGNORE, and unconditional UPDATE (CSV is source of truth).
    """
    db_path = Path(db_path)
    csv_path = Path(csv_path)

    print(f"DB  : {db_path.resolve()}")
    print(f"CSV : {csv_path.resolve()}")

    # Pre-flight: DB file and careers table must exist (populated by ingest.py)
    if not db_path.exists():
        print(
            f"\nERROR: Database file not found: {db_path.resolve()}\n"
            "       Run pipeline/ingest.py first to create and populate careers.sqlite.",
            flush=True,
        )
        sys.exit(1)

    _check = sqlite3.connect(str(db_path))
    _has_careers = _check.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='careers'"
    ).fetchone()
    _check.close()
    if not _has_careers:
        print(
            f"\nERROR: 'careers' table not found in {db_path.resolve()}\n"
            "       Run pipeline/ingest.py first to initialize the database.",
            flush=True,
        )
        sys.exit(1)

    # --- Read CSV (utf-8-sig handles Excel BOM) ---
    with open(csv_path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    print(f"CSV rows: {len(rows)}")

    # Single pass: build deduplicated function and family dicts
    functions = {}   # fn_slug -> (fn_name, fn_desc)
    families = {}    # fam_slug -> (fam_name, fn_slug, fam_desc)

    for row in rows:
        fn_name = row["Job_Function"].strip()
        fam_name = row["Job_Family"].strip()

        if fn_name:
            fn_slug = make_slug(fn_name)
            functions.setdefault(fn_slug, (fn_name, row["Job_Function_Description"].strip()))

        if fn_name and fam_name:
            fam_slug = make_slug(fam_name)
            families.setdefault(
                fam_slug,
                (fam_name, make_slug(fn_name), row["Job_Family_Description"].strip()),
            )

    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON")

    try:
        # 1. Create new tables
        conn.execute(DDL_JOB_FUNCTIONS)
        conn.execute(DDL_JOB_FAMILIES)

        # 2. Add new columns to careers (guard prevents re-add on idempotent run)
        for col_name, col_type in NEW_CAREERS_COLUMNS:
            if not column_exists(conn, "careers", col_name):
                conn.execute(f"ALTER TABLE careers ADD COLUMN {col_name} {col_type}")
                print(f"  Added column: careers.{col_name}")

        # 4. INSERT OR IGNORE into job_functions (idempotent)
        for fn_slug, (fn_name, fn_desc) in functions.items():
            conn.execute(
                "INSERT OR IGNORE INTO job_functions "
                "(job_function_slug, job_function, job_function_description) VALUES (?, ?, ?)",
                (fn_slug, fn_name, fn_desc),
            )

        # 5. INSERT OR IGNORE into job_families (idempotent)
        for fam_slug, (fam_name, fn_slug, fam_desc) in families.items():
            conn.execute(
                "INSERT OR IGNORE INTO job_families "
                "(job_family_slug, job_family, job_function_slug, job_family_description) VALUES (?, ?, ?, ?)",
                (fam_slug, fam_name, fn_slug, fam_desc),
            )

        # 6. UPDATE careers rows — unconditional (CSV is source of truth, makes run idempotent)
        for row in rows:
            jt_id = int(row["JT_ID"])
            conn.execute(
                """UPDATE careers SET
                       job_title_description = ?,
                       key_responsibilities  = ?,
                       required_skills       = ?,
                       typical_education     = ?
                   WHERE jt_id = ?""",
                (
                    row["Job_Title_Description"].strip(),
                    row["Key_Responsibilities"].strip(),
                    row["Required_Skills"].strip(),
                    row["Typical_Education"].strip(),
                    jt_id,
                ),
            )

        conn.commit()

        # --- Verification summary ---
        fn_count = conn.execute("SELECT COUNT(*) FROM job_functions").fetchone()[0]
        fam_count = conn.execute("SELECT COUNT(*) FROM job_families").fetchone()[0]
        filled = conn.execute(
            "SELECT COUNT(*) FROM careers WHERE job_title_description IS NOT NULL"
        ).fetchone()[0]
        null_kr = conn.execute(
            "SELECT COUNT(*) FROM careers WHERE key_responsibilities IS NULL"
        ).fetchone()[0]

        print("\nMigration complete")
        print(f"  job_functions rows : {fn_count}  (expected 22)")
        print(f"  job_families rows  : {fam_count}  (expected 209)")
        print(f"  careers rows with job_title_description : {filled}  (expected 1989)")
        print(f"  careers rows with NULL key_responsibilities : {null_kr}  (expected 0)")

        if fn_count != 22:
            print(f"  WARNING: Expected 22 job_functions, got {fn_count}")
        if fam_count != 209:
            print(f"  WARNING: Expected 209 job_families, got {fam_count}")
        if filled != 1989:
            print(f"  WARNING: Expected 1989 careers rows filled, got {filled}")
        if null_kr != 0:
            print(f"  WARNING: Expected 0 NULL key_responsibilities rows, got {null_kr}")

    finally:
        conn.close()


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="v1.1 Data Migration: extend careers.sqlite with job_functions and job_families."
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB,
        help=f"Path to careers.sqlite (default: {DEFAULT_DB})",
    )
    parser.add_argument(
        "--csv",
        type=Path,
        default=DEFAULT_CSV,
        help=f"Path to enriched_job_architecture.csv (default: {DEFAULT_CSV})",
    )
    args = parser.parse_args()
    run_migration(db_path=args.db, csv_path=args.csv)
