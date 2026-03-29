---
gsd_state_version: 1.0
milestone: v1.1
milestone_name: Full Browse Experience
status: verifying
stopped_at: Completed 13-01-PLAN.md — fix image URL wiring in all 3 browse templates
last_updated: "2026-03-29T15:05:55.156Z"
last_activity: 2026-03-29
progress:
  total_phases: 7
  completed_phases: 5
  total_plans: 7
  completed_plans: 7
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-28 for v1.1 milestone)

**Core value:** A job seeker can find a DND civilian career, understand it, and know how to enter it — without HR help.
**Current focus:** Phase 13 — fix-image-url-wiring

## Current Position

Phase: 13 (fix-image-url-wiring) — EXECUTING
Plan: 1 of 1
Status: Phase complete — ready for verification
Last activity: 2026-03-29

## Progress Bar

```
v1.1: [ ] Phase 9  [ ] Phase 10  [ ] Phase 11  [ ] Phase 12
       0/4 phases complete
```

## Accumulated Context

### Decisions

All decisions logged in PROJECT.md Key Decisions table.

- [Phase 09-data-migration]: Actual CSV has 22 job functions and 209 job families (research stated 23/210) — tests corrected to match reality
- [Phase 09-data-migration]: Unconditional UPDATE from CSV for enrichment columns ensures CSV is authoritative on every migration run
- [Phase 09-data-migration]: Lazy import inside pytest fixture enables TDD RED phase collection before implementation exists
- [Phase 10-image-pipeline]: Used 160deg gradient angle matching existing .card-no-image for visual consistency across card types
- [Phase 10-image-pipeline]: Unsplash attribution placed in footer-bottom flex row between social icons and terms links (D-04 compliance)
- [Phase 10-image-pipeline]: WorkItem._subdir uses explicit dict mapping for correct plural subdirs (families not familys)
- [Phase 10-image-pipeline]: fetch_images.py: 429 not marked done (retry on next run), zero-result marked done (no infinite retry)
- [Phase 11]: Route ordering: /careers/{function_slug}/{family_slug} declared BEFORE /careers/{function_slug} to prevent FastAPI path shadowing
- [Phase 11]: Gradient fallback at L2/L3: family/title cards inherit per-function gradient since images not yet fetched for sub-levels
- [Phase 12]: LEFT JOIN job_families + job_functions in career_detail route provides function_slug/function_name for 4-level breadcrumb with orphan fallback
- [Phase 12]: Family badge link updated to /careers/{function_slug}/{family_slug} to match v1.1 navigation structure
- [Phase 09-data-migration]: Pre-flight guard placed before sqlite3.connect in migrate_v11.py so missing-file case never opens a DB connection
- [Phase 09-data-migration]: RuntimeError guard removed from migrate_v11.py try block — superseded by pre-flight sys.exit(1) check
- [Phase 13-fix-image-url-wiring]: DB image_path is relative to static/images/ not static/; url_for must prepend 'images/' to resolve to correct file path

### Design Principle (established v1.1)

**CAF format parity:** Whatever the CAF Careers website shows, the civilian site shows the same format. Same CSS values, card dimensions, card grid layouts, overlay gradients, typography. Only images and words differ. This is a binding constraint on all UI phases in v1.1+.

Reference: `ps_careers_site/CAF-CAREERS-SITE-REFERENCE.md`

### Data Source (v1.1)

**`enriched_job_architecture.csv`** at `C:\Users\Administrator\Projects\jobforge\data\reference\enriched_job_architecture.csv`

- 1,989 rows, canonical source for all job architecture data
- Contains: `Job_Function_Description`, `Job_Family_Description`, `Job_Title_Description`, `Key_Responsibilities`, `Required_Skills`, `Typical_Education`
- These fields do NOT exist in the current `careers.sqlite` schema — Phase 9 migrates them in

### Phase Dependency Chain

```
Phase 9 (Data Migration)
  → Phase 10 (Image Pipeline) — needs job_functions/job_families tables
  → Phase 11 (Navigation Restructure) — needs data; image fallback allows partial overlap with Phase 10
  → Phase 12 (Enhanced Detail Page) — needs Phase 9 columns and Phase 11 breadcrumb hierarchy
```

### Priority Tech Debt

- **DB_PATH divergence** — `main.py` reads from `pipeline/careers.sqlite`; pipeline scripts write to root `careers.sqlite`. Resolve in Phase 9 data migration.
- **Horticulture Specialist orphaned row** — no `job_family` assigned; does not surface in navigation. Resolve in Phase 9 or data quality audit.

### Blockers/Concerns

None — v1.0 site is fully functional. v1.1 is additive restructure.

## Session Continuity

Last session: 2026-03-29T15:05:54.919Z
Stopped at: Completed 13-01-PLAN.md — fix image URL wiring in all 3 browse templates
Resume: Run `/gsd:plan-phase 9` to begin planning Phase 9 (Data Migration)
