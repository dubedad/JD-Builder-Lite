---
status: diagnosed
phase: 09-data-migration
source: [09-01-SUMMARY.md]
started: 2026-03-28T22:35:00Z
updated: 2026-03-28T22:40:00Z
---

## Current Test

[testing complete]

## Tests

### 1. Cold Start Smoke Test
expected: Kill any running server. Delete careers.sqlite entirely (or rename it). Re-run the migration from scratch — `cd ps_careers_site && python pipeline/migrate_v11.py`. Script completes without errors, prints verified counts (22 functions, 209 families, 1989 enriched rows). No tracebacks.
result: issue
reported: "sqlite3.OperationalError: no such table: careers — script crashes when careers.sqlite does not exist (no pre-existing DB)"
severity: major

### 2. Test suite passes
expected: Running `cd ps_careers_site && python -m pytest pipeline/test_migrate_v11.py -v` exits 0. All 10 tests are listed as PASSED. No failures, no errors, no skips.
result: pass

### 3. job_functions table — 22 rows with slugs
expected: Querying `SELECT COUNT(*), COUNT(job_function_slug) FROM job_functions` returns 22, 22. All rows have non-null, non-blank slugs. Sample query `SELECT job_function_slug, job_function FROM job_functions LIMIT 5` returns readable slug + name pairs (e.g., "information-technology", "Information Technology").
result: pass

### 4. job_families table — 209 rows, no orphans
expected: `SELECT COUNT(*) FROM job_families` returns 209. `SELECT COUNT(*) FROM job_families jf LEFT JOIN job_functions jfn ON jf.job_function_slug=jfn.job_function_slug WHERE jfn.job_function_slug IS NULL` returns 0 (no orphaned families).
result: pass

### 5. careers enrichment — 0 NULLs on all 4 columns
expected: Each of these returns 0: `SELECT COUNT(*) FROM careers WHERE key_responsibilities IS NULL`, `... required_skills IS NULL`, `... typical_education IS NULL`, `... job_title_description IS NULL`. All 1989 rows have content in every enrichment column.
result: pass

### 6. Migration idempotency
expected: Re-running `python pipeline/migrate_v11.py` a second time (on an already-migrated DB) completes without errors. Counts remain identical: 22 functions, 209 families, 1989 enriched rows. No duplicate rows, no "UNIQUE constraint failed" errors.
result: pass

## Summary

total: 6
passed: 5
issues: 1
pending: 0
skipped: 0
blocked: 0

## Gaps

- truth: "Running migrate_v11.py on a fresh system (no pre-existing careers.sqlite) should either succeed or give a clear actionable error message"
  status: failed
  reason: "User reported: sqlite3.OperationalError: no such table: careers — script crashes when careers.sqlite does not exist"
  severity: major
  test: 1
  artifacts: [ps_careers_site/pipeline/migrate_v11.py]
  missing: ["Guard clause or clear error message when careers table is absent — e.g. 'careers.sqlite not found or careers table missing — run ingest.py first'"]
