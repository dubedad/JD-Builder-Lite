# Retrospective: DND Civilian Careers Site

---

## Milestone: v1.0 — MVP

**Shipped:** 2026-03-18
**Phases:** 8 | **Plans:** 10 | **Timeline:** 18 days (2026-02-27 → 2026-03-18)

### What Was Built

1. TBS ingest pipeline — 1,989 job titles, 210 families, 23 functions into careers.sqlite with idempotent UPSERT and URL-safe slugs
2. LLM enrichment — all 1,989 titles AI-enriched with overview, training, entry plans, part-time content via Claude Haiku (concurrent, resumable)
3. CAF bridge — 433 civilian titles linked to 88 military occupations via bridge_caf_ja parquet
4. FastAPI + Jinja2 app with full GC FIP chrome on every page (Canada wordmark, Exo 2 fonts, sticky header, 5-column footer)
5. L1 card grid (12 families), L2 job family listings (NOC badges, metadata, excerpts), L3 5-tab career profiles (LLM content, CAF bridge links, action buttons)
6. Client-side filtering: Job Function dropdown + keyword search bar with intersection logic, no page reload

### What Worked

- **Pipeline-first architecture** — building the data layer completely before the app made the UI phases fast and predictable; no data uncertainty during template work
- **Phase isolation** — each phase had a tight scope; the L2 and L3 pages were 10–12 min to execute because the data was clean and the route was already in place
- **Pre-existing work detection** — phases 6, 7, and 8 all found routes pre-built from prior sessions; the plan verification scripts confirmed them and phases proceeded without unnecessary re-work
- **Claude Haiku for bulk enrichment** — cost-effective at ~2,000 API calls; quality was sufficient for draft content; resume logic handled the 109-row failure on first run cleanly
- **Audit-before-complete** — running `/gsd:audit-milestone` before completion surfaced the DB_PATH divergence tech debt proactively; nothing was missed

### What Was Inefficient

- **DB_PATH divergence** was introduced silently — pipeline writes to root `careers.sqlite` but main.py was set to read from `pipeline/careers.sqlite`. Both happened to be identical at ship time but this will cause a silent staleness bug on next pipeline re-run. Should have been caught in Phase 4 plan review.
- **CARD_IMAGE_STATIC gap** — Phase 5 shipped without the normalization dict in main.py, requiring a gap-closure plan (05-02). The plan verification script should have checked for the dict presence in main.py from the start.
- **Phases 1–4 pre-date GSD verification** — no VERIFICATION.md or VALIDATION.md files exist for the pipeline and app foundation phases. The integration checker confirmed everything is wired, but retroactive verification would improve confidence for future pipeline re-runs.
- **Blank Job Function dropdown** — 1 row with `job_function=''` in the DB produces a blank option. Simple WHERE filter was never applied to the DISTINCT query. Minor but visible to users.

### Patterns Established

- `CARD_IMAGE_STATIC` normalization dict in the route handler — maps raw DB keys to filesystem-safe filenames; extend for new card families in v1.1
- `data-*` attribute pattern for client-side filtering — embed JSON on DOM elements, JS reads `dataset.*`; no endpoint needed for small datasets
- `GROUP_CONCAT` with `|||` separator for multi-value server-side data — avoids JSON quoting complexity at the SQL layer
- `(column or '')[:N]` null-safe Jinja2/Python excerpts — never crashes on empty LLM content
- Phase gap closure via decimal plan (05-02) — clean way to close a verification gap without replanning

### Key Lessons

1. **Check DB_PATH at app foundation time** — the path the app reads from must be the same path the pipeline writes to. Verify this in Phase 4 verification, not at audit time.
2. **CARD_IMAGE_STATIC (or equivalent normalization)** should be part of the plan spec for any phase that maps raw DB keys to static file URLs.
3. **GSD verification workflow pays off fast** — phases 5–8 with VERIFICATION.md caught the sticky-nav CSS space bug and the image URL gap immediately; phases 1–4 without it required integration checker to confirm coverage retroactively.
4. **Resume logic is non-negotiable for bulk LLM jobs** — 109 failures on first run would have been catastrophic without it. Always design bulk API scripts with resume-from-checkpoint logic.

### Cost Observations

- Model mix: ~100% Haiku for enrichment (1,989 API calls), Sonnet for planning/verification
- Sessions: ~8 across 18 days
- Notable: LLM enrichment took ~78 min wall-clock for 1,877 titles at concurrency=5; retry run for 109 failures took ~4 min

---

## Cross-Milestone Trends

| Metric | v1.0 |
|--------|------|
| Phases | 8 |
| Plans | 10 |
| Timeline (days) | 18 |
| LOC at ship | ~1,782 |
| Requirements met | 29/29 |
| Tech debt items | 5 |
| Nyquist compliance | 0/8 phases |

### Recurring Patterns

| Pattern | v1.0 |
|---------|------|
| Pre-existing route detected | ✓ (phases 6, 7, 8) |
| Gap closure plan needed | ✓ (phase 5-02) |
| Resume logic saved a run | ✓ (enrichment phase) |
| DB path divergence risk | ✓ (present at ship) |
