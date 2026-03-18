# Milestones

## v1.0 MVP (Shipped: 2026-03-18)

**Phases completed:** 8 phases (Phases 1–8), 10 plans
**Timeline:** 2026-02-27 → 2026-03-18 (18 days)
**Codebase:** ~1,782 LOC (Python + Jinja2 HTML), 36 files changed

**Delivered:** A fully browsable DND Civilian Careers site — pipeline ingests 1,989 TBS job titles, AI-enriches all of them, and serves a 3-level browseable site with filtering, metadata badges, and CAF military career links.

**Key accomplishments:**
1. Ingested all 1,989 TBS job titles into careers.sqlite with URL-safe slugs and idempotent UPSERT (210 families, 23 functions, 0 slug collisions)
2. AI-enriched all 1,989 job titles with overview, training, entry plans, and part-time content via Claude Haiku (concurrent 5-worker pipeline, resumable on failure, 0 empty rows remaining)
3. Linked 433/1,989 civilian titles to 88 CAF military occupations via bridge_caf_ja parquet (21.8% coverage, confidence threshold ≥ 0.70)
4. Launched FastAPI + Jinja2 app with full GC FIP chrome on every page (Canada wordmark, Exo 2 + Roboto fonts, sticky nav header, 5-column footer)
5. Delivered complete 3-level browsable site: L1 card grid (12 families, CAF-matched design) → L2 job family listings (NOC badge, level tag, digital flag, 150-char excerpt) → L3 5-tab career profile (Overview, Training, Entry Plans, Part-Time, Related Careers)
6. Added client-side Job Function dropdown (22 values) and keyword search bar with intersection filtering and no page reload

**Archives:**
- `.planning/milestones/v1.0-ROADMAP.md` — full phase details
- `.planning/milestones/v1.0-REQUIREMENTS.md` — requirements with outcomes
- `.planning/milestones/v1.0-MILESTONE-AUDIT.md` — audit: 29/29 requirements, 5 tech debt items

---

