# Phase 9: Data Migration - Research

**Researched:** 2026-03-28
**Domain:** SQLite schema migration, CSV import, idempotent data pipeline (Python + sqlite3)
**Confidence:** HIGH

---

## Summary

Phase 9 is a pure data engineering task: extend `careers.sqlite` with two new tables (`job_functions`, `job_families`) and four new columns on the existing `careers` table, then load all content from the pre-existing `enriched_job_architecture.csv`. No web framework changes, no UI. The migration is the foundation every downstream phase depends on.

The source CSV (`enriched_job_architecture.csv`, 1,989 rows, zero nulls in the four key fields) lives in the JobForge repo at `C:\Users\Administrator\Projects\jobforge\data\reference\`. It contains every field needed: `Job_Function_Description`, `Job_Family_Description`, `Job_Title_Description`, `Key_Responsibilities`, `Required_Skills`, `Typical_Education`. All 1,989 CSV JT_IDs exactly match the DB. There are 23 distinct job functions and 210 distinct job families — exactly the counts the success criteria require.

The project has one structural tech debt item that MUST be resolved in this phase: `main.py` points to `ps_careers_site/careers.sqlite` (root); all pipeline scripts (`ingest.py`, `enrich.py`, `bridge.py`) also default to `ps_careers_site/careers.sqlite` (root, via `_HERE = Path(__file__).parent.parent`). There is also a duplicate at `ps_careers_site/pipeline/careers.sqlite`. At this moment both files are byte-for-byte identical (1,989 rows, all draft status), but the pipeline duplicate must be formally acknowledged and the canonical path confirmed before writing migration scripts.

**Primary recommendation:** Write a single self-contained `pipeline/migrate_v11.py` script using SQLite `ALTER TABLE IF NOT EXISTS` pattern + `INSERT OR IGNORE` for new-table rows + `UPDATE … WHERE column IS NULL` for careers columns. Run from the `ps_careers_site/` directory against `careers.sqlite` (root, same path `main.py` uses). The pipeline DB copy can be left as a stale artifact or deleted — the canonical DB is the root one.

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| DATA-01 | `careers.sqlite` extended with `job_functions` table (`job_function`, `job_function_slug`, `job_function_description`, `image_path`) | CSV has `Job_Function` + `Job_Function_Description`; slug derivation uses existing `make_slug()` from `ingest.py`; `image_path` NULL at this stage (Phase 10 fills it) |
| DATA-02 | `careers.sqlite` extended with `job_families` table (`job_family`, `job_family_slug`, `job_function` FK, `job_family_description`, `image_path`) | CSV has `Job_Family` + `Job_Family_Description` + `Job_Function`; no cross-function slug collisions; `image_path` NULL at this stage |
| DATA-03 | `careers` table extended with `job_title_description`, `key_responsibilities`, `required_skills`, `typical_education`, `image_path` columns | All 4 text fields are non-null in the CSV; `image_path` NULL at this stage; use `ALTER TABLE … ADD COLUMN IF NOT EXISTS` pattern |
| DATA-04 | All 23 job functions imported from CSV with descriptions and slugs | Verified: 23 distinct non-blank `Job_Function` values; one row (JT_ID=1933 Horticulture Specialist) has blank function — excluded from `job_functions` table; slugs are collision-free |
| DATA-05 | All 210 job families imported from CSV with descriptions, function relationships, and slugs | Verified: 210 distinct (function, family) pairs; no slug collisions within-function or cross-function; FK to `job_functions.job_function_slug` |
| DATA-06 | All 1,989 job titles updated with `job_title_description`, `key_responsibilities`, `required_skills`, `typical_education` | All 1,989 CSV JT_IDs match DB; all 4 fields fully populated in CSV; use parameterized UPDATE with `jt_id` as key |
</phase_requirements>

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `sqlite3` | stdlib | DB access | Already used throughout the pipeline; no new dependency |
| `csv` | stdlib | Read CSV | Already used/understood; handles the utf-8-sig BOM in this CSV |
| `pathlib.Path` | stdlib | File paths | Project convention — all pipeline scripts use it |
| `argparse` | stdlib | CLI flags | Project convention — all pipeline scripts use it |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `re` | stdlib | Slug generation | `make_slug()` pattern already in `ingest.py` — copy it |

**No new packages required.** This phase is pure stdlib Python.

**Installation:** nothing to install.

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| stdlib `sqlite3` | SQLAlchemy / Alembic | Overkill; project uses raw sqlite3 everywhere |
| Custom migration script | Alembic migrations | No ORM in this project; adds unnecessary complexity |
| CSV import | Re-running ingest.py | Ingest only populates taxonomy fields, not the new enrichment columns |

---

## Architecture Patterns

### Recommended Project Structure

```
ps_careers_site/
├── careers.sqlite          ← canonical DB (main.py + all pipeline scripts)
├── pipeline/
│   ├── ingest.py           ← v1.0 (do not modify)
│   ├── enrich.py           ← v1.0 (do not modify)
│   ├── bridge.py           ← v1.0 (do not modify)
│   ├── fetch_images.py     ← v1.0 (do not modify)
│   └── migrate_v11.py      ← NEW: Phase 9 migration script
```

### Pattern 1: Idempotent ALTER TABLE

SQLite does not support `ADD COLUMN IF NOT EXISTS` natively until SQLite 3.37.
The safe pattern is to query `PRAGMA table_info(table_name)` first, then add only missing columns.

```python
# Source: SQLite docs + stdlib pattern used in ingest.py
def _column_exists(conn: sqlite3.Connection, table: str, column: str) -> bool:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return any(row[1] == column for row in rows)

def add_column_if_missing(conn, table, column, col_type):
    if not _column_exists(conn, table, column):
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")
```

### Pattern 2: Idempotent Table Creation

```python
# Source: SQLite docs
CREATE TABLE IF NOT EXISTS job_functions (
    job_function_slug       TEXT PRIMARY KEY,
    job_function            TEXT NOT NULL UNIQUE,
    job_function_description TEXT,
    image_path              TEXT
);

CREATE TABLE IF NOT EXISTS job_families (
    job_family_slug         TEXT PRIMARY KEY,
    job_family              TEXT NOT NULL UNIQUE,
    job_function_slug       TEXT NOT NULL REFERENCES job_functions(job_function_slug),
    job_family_description  TEXT,
    image_path              TEXT
);
```

### Pattern 3: Idempotent Row Insert

```python
# INSERT OR IGNORE preserves existing rows on re-run
conn.execute("""
    INSERT OR IGNORE INTO job_functions
        (job_function_slug, job_function, job_function_description)
    VALUES (?, ?, ?)
""", (slug, name, desc))
```

### Pattern 4: Idempotent Column Update (careers table)

Only overwrite NULL — preserves any values already set by a previous run or manual edit:

```python
conn.execute("""
    UPDATE careers SET
        job_title_description = ?,
        key_responsibilities  = ?,
        required_skills       = ?,
        typical_education     = ?
    WHERE jt_id = ?
      AND (job_title_description IS NULL
           OR key_responsibilities IS NULL
           OR required_skills IS NULL
           OR typical_education IS NULL)
""", (jtd, kr, rs, te, jt_id))
```

**Alternative safer approach** (always update from CSV — source of truth is the CSV):

```python
UPDATE careers SET
    job_title_description = ?,
    key_responsibilities  = ?,
    required_skills       = ?,
    typical_education     = ?
WHERE jt_id = ?
```

This is also idempotent (same value written every run) and avoids partial-update edge cases. Recommended because the CSV is the canonical source, not the DB.

### Pattern 5: Slug Derivation

Copy `make_slug()` from `ingest.py` — it is the established project standard:

```python
import re

def make_slug(text: str) -> str:
    s = text.lower()
    s = s.replace("&", "and")
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"[\s]+", "-", s.strip())
    return s.strip("-")
```

Verified: no slug collisions among the 23 function names or 210 family names.

### Anti-Patterns to Avoid

- **Suffix-based collision handling for functions/families:** The title-level `make_slug(text, suffix=str(jt_id))` pattern from `ingest.py` is NOT needed here — no collisions exist at function or family level. Don't add it.
- **Dropping and recreating tables:** Destroys data on re-run; use `CREATE TABLE IF NOT EXISTS` + `INSERT OR IGNORE`.
- **Reading the CSV into memory twice:** Build the deduplicated function/family rows in one pass over the CSV, then do DB writes in a second pass.
- **Hardcoding the CSV path:** Accept it as a CLI arg with a sensible default pointing to the jobforge repo, same pattern as other pipeline scripts.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead |
|---------|-------------|-------------|
| Slug generation | Custom regex | Copy `make_slug()` from `ingest.py` |
| Idempotent upsert | Manual SELECT + INSERT/UPDATE | `INSERT OR IGNORE` for new tables; unconditional UPDATE for careers columns |
| Column existence check | Try/except on ALTER | `PRAGMA table_info()` query |
| CSV BOM handling | Manual strip | `open(path, encoding='utf-8-sig')` |

---

## Runtime State Inventory

> Included because this is a schema migration / data import phase.

| Category | Items Found | Action Required |
|----------|-------------|-----------------|
| Stored data | `careers.sqlite` (root, 1,989 rows, `careers` table only); `pipeline/careers.sqlite` (identical copy, 1,989 rows) | Migration script writes to root `careers.sqlite` only. Pipeline copy is stale artifact — document but do not delete in this phase (Phase 10 pipeline scripts may reference it). |
| Live service config | FastAPI dev server (`main.py`) reads `DB_PATH = os.path.join(os.path.dirname(__file__), "careers.sqlite")` — already points to root DB | No change needed for `main.py`. Pipeline scripts default to root DB via `_HERE = Path(__file__).parent.parent`. Both are consistent. |
| OS-registered state | None — no Task Scheduler, pm2, or service registration observed | None |
| Secrets/env vars | `ANTHROPIC_API_KEY` used by `enrich.py` — not relevant to this phase | None |
| Build artifacts | `pipeline/__pycache__/` — auto-regenerated; no stale artifact risk | None |

**DB_PATH status (resolved):** `main.py` line 19 sets `DB_PATH = os.path.join(os.path.dirname(__file__), "careers.sqlite")` which resolves to `ps_careers_site/careers.sqlite`. All pipeline scripts use `_HERE = Path(__file__).parent.parent / "careers.sqlite"` which also resolves to `ps_careers_site/careers.sqlite`. The two databases were byte-for-byte identical at research time. The "divergence" noted in STATE.md is not currently a data divergence — it is a documentation concern. The canonical DB for both the app and the migration script is `ps_careers_site/careers.sqlite`.

---

## Data Quality Findings

### Horticulture Specialist (JT_ID=1933)

This row has a blank `Job_Function` and blank `Job_Family` in the CSV (and in the DB). It has LLM-enriched `overview`, `training`, `entry_plans`, `part_time` content and `content_status='draft'`.

**Impact on this phase:**
- It will NOT appear in `job_functions` (blank function name — excluded from the 23-row insert)
- It will NOT appear in `job_families` (blank family name — excluded from the 210-row insert)
- It WILL receive the 4 new column values (`job_title_description`, `key_responsibilities`, `required_skills`, `typical_education`) since its JT_ID=1933 matches in the CSV
- Its `job_family_slug` in the DB is `''` (empty string) — it will not link to any family FK

**Decision required from planner:** The migration script should skip JT_ID=1933 for `job_functions`/`job_families` inserts (natural behaviour of blank-name guard) and include it for careers column updates (it has valid enrichment data). No special handling needed beyond a NULL/empty guard on function name.

### CSV Field Completeness

All 4 target fields are 100% populated across all 1,989 rows:
- `Job_Title_Description`: 0 empty
- `Key_Responsibilities`: 0 empty
- `Required_Skills`: 0 empty
- `Typical_Education`: 0 empty

No NULL handling or fallback logic is needed in the CSV import.

### JT_ID Alignment

All 1,989 CSV JT_IDs are present in the DB. No orphaned CSV rows. No DB rows missing from CSV. The UPDATE pass will match every single row.

---

## Common Pitfalls

### Pitfall 1: SQLite ALTER TABLE is additive-only

**What goes wrong:** Attempting to rename or drop columns in SQLite requires table recreation. The migration only adds columns — this is safe. But if a developer tries to rename an existing column with ALTER TABLE, it will fail on SQLite < 3.35.
**Why it happens:** SQLite's ALTER TABLE is intentionally limited.
**How to avoid:** Only use `ADD COLUMN` in this migration. Never rename/drop in the same script.
**Warning signs:** `sqlite3.OperationalError: near "RENAME": syntax error`

### Pitfall 2: Running migration against the wrong DB file

**What goes wrong:** Developer runs the script from the `pipeline/` directory, causing `_HERE` resolution to be wrong, or they pass `--db pipeline/careers.sqlite` instead of the root DB.
**Why it happens:** Two `careers.sqlite` files exist; the developer may not know which is canonical.
**How to avoid:** Set default DB path explicitly to `ps_careers_site/careers.sqlite`. Print the resolved absolute path at script start. Add a warning if the DB row count is not 1,989.
**Warning signs:** Script reports success but `main.py` still shows old schema.

### Pitfall 3: utf-8-sig BOM in CSV

**What goes wrong:** Opening the CSV with `encoding='utf-8'` leaves a `\ufeff` BOM in the first column header (`'\ufeffJT_ID'` instead of `'JT_ID'`), causing KeyError on `row['JT_ID']`.
**Why it happens:** The CSV was saved from Excel with a BOM.
**How to avoid:** Always open with `encoding='utf-8-sig'`.
**Warning signs:** `KeyError: 'JT_ID'` on first data access.

### Pitfall 4: Family slug FK integrity

**What goes wrong:** `job_families.job_function_slug` FK points to a function slug that does not exist in `job_functions` because the function was excluded (e.g., blank name) or a slug typo.
**Why it happens:** SQLite does not enforce FK constraints by default (`PRAGMA foreign_keys = OFF` by default).
**How to avoid:** Run `PRAGMA foreign_keys = ON` in the migration connection. Alternatively, validate that every family function slug has a matching row in `job_functions` before committing.
**Warning signs:** Silent data inconsistency; families orphaned from functions.

### Pitfall 5: Non-unique job_family names across functions

**What goes wrong:** Assuming `job_family_slug` is globally unique and using it as a PRIMARY KEY. Research confirmed all 210 family slugs ARE globally unique (no two functions share a family name). But if the CSV ever changes this is a hidden assumption.
**Why it happens:** The uniqueness was verified programmatically but not documented.
**How to avoid:** Add a UNIQUE constraint on `job_family_slug` and let the insert fail loudly if violated.
**Warning signs:** `UNIQUE constraint failed: job_families.job_family_slug`

---

## Code Examples

### Migration Script Skeleton

```python
# pipeline/migrate_v11.py
"""
v1.1 Data Migration: extend careers.sqlite with job_functions,
job_families tables and new columns on careers.

Usage (from ps_careers_site/ directory):
    python pipeline/migrate_v11.py
    python pipeline/migrate_v11.py --csv "C:/path/to/enriched_job_architecture.csv" --db careers.sqlite
"""

import argparse
import csv
import re
import sqlite3
from pathlib import Path

_HERE = Path(__file__).parent.parent  # ps_careers_site/
DEFAULT_DB = _HERE / "careers.sqlite"
DEFAULT_CSV = Path(r"C:\Users\Administrator\Projects\jobforge\data\reference\enriched_job_architecture.csv")


def make_slug(text: str) -> str:
    """Identical to ingest.py make_slug() — project standard."""
    s = text.lower().replace("&", "and")
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"[\s]+", "-", s.strip())
    return s.strip("-")


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

NEW_CAREERS_COLUMNS = [
    ("job_title_description", "TEXT"),
    ("key_responsibilities",  "TEXT"),
    ("required_skills",       "TEXT"),
    ("typical_education",     "TEXT"),
    ("image_path",            "TEXT"),
]


def column_exists(conn, table, column):
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return any(row[1] == column for row in rows)


def run_migration(db_path: Path, csv_path: Path) -> None:
    print(f"DB  : {db_path.resolve()}")
    print(f"CSV : {csv_path.resolve()}")

    # --- Read CSV ---
    with open(csv_path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    print(f"CSV rows: {len(rows)}")

    # Build deduplicated function + family dicts
    functions = {}   # slug -> (name, description)
    families  = {}   # slug -> (name, fn_slug, description)
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
                (fam_name, make_slug(fn_name), row["Job_Family_Description"].strip())
            )

    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        # 1. Create new tables
        conn.execute(DDL_JOB_FUNCTIONS)
        conn.execute(DDL_JOB_FAMILIES)

        # 2. Add new columns to careers
        for col_name, col_type in NEW_CAREERS_COLUMNS:
            if not column_exists(conn, "careers", col_name):
                conn.execute(f"ALTER TABLE careers ADD COLUMN {col_name} {col_type}")
                print(f"  Added column: careers.{col_name}")

        # 3. Insert job_functions (idempotent)
        for fn_slug, (fn_name, fn_desc) in functions.items():
            conn.execute(
                "INSERT OR IGNORE INTO job_functions "
                "(job_function_slug, job_function, job_function_description) VALUES (?,?,?)",
                (fn_slug, fn_name, fn_desc)
            )

        # 4. Insert job_families (idempotent)
        for fam_slug, (fam_name, fn_slug, fam_desc) in families.items():
            conn.execute(
                "INSERT OR IGNORE INTO job_families "
                "(job_family_slug, job_family, job_function_slug, job_family_description) VALUES (?,?,?,?)",
                (fam_slug, fam_name, fn_slug, fam_desc)
            )

        # 5. Update careers rows (unconditional — CSV is source of truth)
        updated = 0
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
                )
            )
            updated += conn.execute("SELECT changes()").fetchone()[0]

        conn.commit()

        # --- Verification ---
        fn_count  = conn.execute("SELECT COUNT(*) FROM job_functions").fetchone()[0]
        fam_count = conn.execute("SELECT COUNT(*) FROM job_families").fetchone()[0]
        filled    = conn.execute(
            "SELECT COUNT(*) FROM careers WHERE job_title_description IS NOT NULL"
        ).fetchone()[0]

        print(f"\nMigration complete")
        print(f"  job_functions rows : {fn_count}  (expected 23)")
        print(f"  job_families rows  : {fam_count}  (expected 210)")
        print(f"  careers rows with job_title_description : {filled}  (expected 1989)")

        if fn_count != 23:
            print(f"  WARNING: Expected 23 job_functions, got {fn_count}")
        if fam_count != 210:
            print(f"  WARNING: Expected 210 job_families, got {fam_count}")
        if filled != 1989:
            print(f"  WARNING: Expected 1989 careers rows filled, got {filled}")

    finally:
        conn.close()
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Alembic-style versioned migrations | Inline `CREATE IF NOT EXISTS` + `ALTER TABLE` guard | Always the project pattern | No migration registry needed at this scale |
| SQLite `REPLACE INTO` | `INSERT OR IGNORE` for new rows | v1.0 ingest uses `INSERT … ON CONFLICT DO UPDATE` | `INSERT OR IGNORE` is simpler for reference tables with no update needed |

---

## Open Questions

1. **Pipeline DB copy (`pipeline/careers.sqlite`)**
   - What we know: Identical to root DB at research time
   - What's unclear: Should it be deleted, or kept as a working copy for pipeline development?
   - Recommendation: Leave as-is for now; the migration script targets root DB explicitly. Document in PLAN.md that this file is a stale artifact.

2. **FK enforcement on `job_families.job_function_slug`**
   - What we know: SQLite FK enforcement is off by default; all 210 families map to valid functions
   - What's unclear: Should the migration script enable FK enforcement globally or just verify post-migration?
   - Recommendation: Enable `PRAGMA foreign_keys = ON` in the migration connection only, and add a post-migration verification query.

3. **Horticulture Specialist classification**
   - What we know: JT_ID=1933 has blank `Job_Function` and `Job_Family` in both CSV and DB
   - What's unclear: Is this a data quality error (should be assigned to a function) or intentional?
   - Recommendation: Leave it orphaned for this phase. Assign to a function in a follow-up data quality task after v1.1 ships.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.x | Migration script | Yes | 3.13 | — |
| `sqlite3` stdlib | DB access | Yes | bundled | — |
| `csv` stdlib | CSV reading | Yes | bundled | — |
| `enriched_job_architecture.csv` | DATA-04/05/06 | Yes | 1,989 rows, 0 nulls | — |
| `careers.sqlite` (root) | All DATA-* | Yes | 1,989 rows, all draft | — |

**Missing dependencies with no fallback:** None.

---

## Validation Architecture

> `workflow.nyquist_validation` not set to `false` in config.json — section included.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (standard; no pytest.ini detected — Wave 0 creates it) |
| Config file | none — `pytest.ini` or `pyproject.toml [tool.pytest]` needed |
| Quick run command | `pytest pipeline/test_migrate_v11.py -x -q` |
| Full suite command | `pytest pipeline/ -q` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| DATA-01 | `job_functions` table created with correct schema | unit | `pytest pipeline/test_migrate_v11.py::test_job_functions_table_exists -x` | Wave 0 |
| DATA-02 | `job_families` table created with correct schema and FK | unit | `pytest pipeline/test_migrate_v11.py::test_job_families_table_exists -x` | Wave 0 |
| DATA-03 | `careers` table has 5 new columns | unit | `pytest pipeline/test_migrate_v11.py::test_careers_new_columns -x` | Wave 0 |
| DATA-04 | 23 job function rows, all with slug and non-null description | unit | `pytest pipeline/test_migrate_v11.py::test_job_functions_count -x` | Wave 0 |
| DATA-05 | 210 job family rows, all linked to a valid function FK | unit | `pytest pipeline/test_migrate_v11.py::test_job_families_count -x` | Wave 0 |
| DATA-06 | All 1,989 careers rows have non-null enrichment columns | unit | `pytest pipeline/test_migrate_v11.py::test_careers_enriched -x` | Wave 0 |
| Idempotency | Second run produces identical row counts, no errors | unit | `pytest pipeline/test_migrate_v11.py::test_idempotent -x` | Wave 0 |

### Sampling Rate

- **Per task commit:** `pytest pipeline/test_migrate_v11.py -x -q`
- **Per wave merge:** `pytest pipeline/ -q`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `pipeline/test_migrate_v11.py` — covers all DATA-* requirements + idempotency
- [ ] `pytest.ini` or `pyproject.toml [tool.pytest.ini_options]` — test configuration
- [ ] Framework install check: `python -m pytest --version` (pytest likely not installed; add to `requirements.txt`)

---

## Sources

### Primary (HIGH confidence)

- Direct DB introspection (`PRAGMA table_info`, row counts) — schema verified
- Direct CSV inspection (`csv.DictReader` on `enriched_job_architecture.csv`) — columns, row counts, null checks verified
- `pipeline/ingest.py` — `make_slug()` function, project conventions, UPSERT pattern
- `pipeline/enrich.py` — DB path convention (`_HERE = Path(__file__).parent.parent`)
- `pipeline/bridge.py` — DB path convention
- `main.py` lines 1–20 — `DB_PATH` definition

### Secondary (MEDIUM confidence)

- SQLite official docs: `CREATE TABLE IF NOT EXISTS`, `INSERT OR IGNORE`, `PRAGMA table_info`, `PRAGMA foreign_keys`
- Python stdlib docs: `csv.DictReader` with `encoding='utf-8-sig'` for BOM handling

### Tertiary (LOW confidence)

- None

---

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH — verified against existing codebase; no new libraries
- Architecture patterns: HIGH — verified against existing pipeline scripts and SQLite stdlib
- Data quality findings: HIGH — verified by running Python against actual files
- Pitfalls: HIGH — derived from direct inspection of file encoding, DB structure, and path resolution

**Research date:** 2026-03-28
**Valid until:** 2026-05-28 (stable domain — SQLite stdlib, no external services)
