# Project Milestones: JD Builder Lite

## v5.0 JobForge 2.0 Integration (Shipped: 2026-03-10)

**Delivered:** Replaced live OASIS scraping with JobForge 2.0 gold parquet as the primary data source for search and profile data, delivering sub-second search (155-234ms vs 5-60s OASIS) and parquet-served profile tabs for all 900 profiles, with full TBS Directive compliance and transparent OASIS fallback.

**Phases completed:** 21-25 (10 plans total)

**Key accomplishments:**

- Inventoried all 25 JobForge gold parquet files and produced explicit gap analysis (5 gaps, 13 covered fields); established CoverageStatus type with mandatory warning logging across all data load paths
- Profile tabs (Skills, Abilities, Knowledge, Work Activities, Work Context) now served from parquet for all 900 profiles with source provenance badges (green "JobForge" / grey "OASIS")
- Sub-second parquet search (155-234ms cold, 75-124ms warm) with five-tier relevance scoring — replacing 5-60s OASIS path; transparent fallback on zero results
- Fixed pre-existing OASIS profile URL breakage discovered during Phase 23; OASIS-down fallback in /api/profile ensures parquet tabs served even when OASIS unreachable
- Per-section provenance in exported JD: all 5 JD element sections record source ("jobforge" vs "oasis") in TBS Directive 6.2.3 compliance appendix
- Logging and exception handling cleanup: print() → logger.info(), bare except → typed exceptions, scoring symmetry between OASIS and parquet search paths

**Stats:**

- 47 files changed, 6,007 insertions, 271 deletions
- ~35,196 lines of Python + HTML/CSS/JS (total codebase)
- 5 phases, 10 plans
- 4 days (2026-03-07 → 2026-03-10)

**Git range:** `feat(21-01)` → `docs(25)`

**What's next:** v5.1 for Main Duties ETL integration and P2 search features unlocked by parquet

---

## v4.0 Occupational Group Allocation (Shipped: 2026-02-04)

**Delivered:** Classification Step 1 — matching engine that compares job descriptions against TBS occupational group definitions using the prescribed allocation method with full policy provenance, confidence scoring, and evidence linking.

**Phases completed:** 14-17 (13 plans total)

**Key accomplishments:**

- DIM_OCCUPATIONAL data layer with 426 groups, 900 inclusions, 330 exclusions scraped from TBS
- OccupationalGroupAllocator with semantic shortlisting (sentence-transformers) and LLM classification (instructor)
- Multi-factor confidence scoring (60% definition fit, 30% semantic similarity, 10% labels boost)
- POST /api/allocate endpoint with full provenance map and edge case handling
- Recommendation cards UI with confidence bars, expandable rationale, and evidence highlighting
- Policy provenance chain traceable to TBS Classification Policy and DADM

**Stats:**

- 89 files created/modified
- 12,030 lines of Python (total codebase)
- 4 phases, 13 plans, 38 requirements
- 1 day from milestone start to ship (2026-02-04)

**Git range:** `feat(14-01)` → `feat(17-03)`

**What's next:** v5.0 for Classification Step 2 (Job Evaluation Standards scoring)

---

## v3.0 Style-Enhanced Writing (Shipped: 2026-02-03)

**Delivered:** Vocabulary-constrained generation using JobForge parquet data, style analysis pipeline, and differentiated AI disclosure with dual-format display in PDF/DOCX exports.

**Phases completed:** 09-13 (11 plans total)

**Key accomplishments:**

- Vocabulary foundation with 50,000+ terms from JobForge parquet files
- Style analysis pipeline with few-shot prompting and vocabulary validation
- Extended provenance architecture with differentiated AI disclosure
- Constrained generation with retry logic and vocabulary audit
- Enhanced PDF/DOCX export with dual-format styled content

**Stats:**

- 4 phases, 11 plans
- Shipped: 2026-02-03

**Git range:** `feat(09-01)` → `feat(13-03)`

**What's next:** v4.0 Occupational Group Allocation

---

## v2.0 UI Redesign (Shipped: 2026-01-25)

**Delivered:** Complete UI redesign mirroring OaSIS website interface with Keyword/Code search toggle, OaSIS-style result cards, LLM-powered profile headers, ARIA-compliant tab navigation, and accessible statement selection with tooltips.

**Phases completed:** 08-A through 08-D (8 plans total)

**Key accomplishments:**

- Search bar redesign with Keyword/Code pill toggle and authoritative sources footnote
- OaSIS-style search result cards with 6 data points extracted from search HTML
- Minor Unit Group filtering with derived NOC code categories
- LLM-powered occupation icons (16 semantic categories) and AI-generated descriptions
- ARIA-compliant horizontal Job Header tabs with keyboard navigation
- CSS tooltips for statement descriptions with WCAG 2.1 accessibility and single Create button

**Stats:**

- 47 commits in milestone
- 10,370 lines of Python, HTML, CSS, JS (total codebase)
- 4 phases, 8 plans, 17 requirements
- 1 day from milestone start to ship (2026-01-24 to 2026-01-25)

**Git range:** `feat(08-A-01)` → `docs(08-D)`

**What's next:** v2.1 for UI polish, additional filters, and visual scale distinctions

---

## v1.1 Enhanced Data Display + Export (Shipped: 2026-01-23)

**Delivered:** Enriched statement display with OASIS metadata (proficiency levels, descriptions, scale meanings), NOC hierarchy breakdown, Work Context classification, grid view toggle, and PDF/DOCX export with Annex section for unused NOC reference attributes.

**Phases completed:** 5-7 (11 plans total)

**Key accomplishments:**

- Data enrichment pipeline with guide.csv - Category definitions, statement descriptions, and scale meanings loaded via singleton with UTF-8-sig encoding
- NOC hierarchy and reference attributes - TEER breakdown, broad/major/minor categories, career mobility, example titles, interests extracted from OASIS
- Work Context classification - Pattern-based filtering for responsibilities and effort statements with LLM fallback for descriptions
- OASIS-style proficiency circles - Unicode circles (●○) with WCAG 2.1 Level AA compliance including Escape key tooltip dismissal
- Search results grid view - Card/table toggle with NOC codes displayed and localStorage persistence
- PDF + DOCX export with Annex - Word export using python-docx with Annex section for unused NOC reference attributes

**Stats:**

- 39 files created/modified
- 7,868 lines of Python, HTML, CSS, JS (total codebase)
- 3 phases, 11 plans
- 1 day from milestone start to ship (2026-01-22 to 2026-01-23)

**Git range:** `feat(05-01)` to `feat(07-04)`

**What's next:** v1.2 for additional search filters, visual scale distinctions, or custom export options

---

## v1.0 MVP (Shipped: 2026-01-22)

**Delivered:** Compliance-focused job description builder demonstrating TBS Directive 32592 compliance with full provenance tracking from NOC/OASIS data through human selection to AI-assisted export.

**Phases completed:** 1-4 (9 plans total)

**Key accomplishments:**

- Flask backend with live OASIS scraping - search and profile endpoints returning structured NOC data with full provenance
- Interactive accordion UI with multi-select - NOC statements organized by JD Elements with localStorage persistence
- OpenAI-powered General Overview generation - SSE streaming with modification tracking and AI badge states
- Audit-ready PDF export with compliance metadata - Full TBS Directive sections (6.2.3, 6.2.7, 6.3.5)
- Complete provenance chain - Every statement traceable from OASIS scrape through human selection to PDF export

**Stats:**

- 81 files created/modified
- 5,130 lines of Python, HTML, CSS, JS
- 4 phases, 9 plans
- 2 days from initialization to ship (2026-01-21 to 2026-01-22)

**Git range:** `feat(01-02)` to `feat(04-02)`

**What's next:** Demo validation with stakeholders, potential v1.1 for additional NOC sections (Annex data) or UI polish

---

*Milestone record created: 2026-01-22*

---

## v5.1 UI Overhaul (Shipped: 2026-03-13)

**Delivered:** Complete visual and UX overhaul of the JD Builder interface across all 5 steps — Search, Build, Classify, Generate, and Export. Implemented 30 phases covering new navigation stepper, card-based search results, tabbed profile view, selections drawer, preview modal, classify page with TBS alignment scores, generate page with additional context input, and a new Export page with PDF/Word/JSON download capabilities and embedded compliance metadata.

**Key accomplishments:**
- 5-step linear workflow with persistent stepper nav and step gating
- Tabbed Build step (Key Activities, Skills, Abilities, Knowledge, Effort, Responsibilities, Core Competencies)
- Selections sidebar drawer with live JD preview
- Classify step with occupation group recommendations and TBS alignment scoring
- Generate step with AI-written position overview and provenance tracking
- Export step with full provenance annex, audit trail, compliance cards (DAMA/TBS/Lineage)
- PDF/Word exports restructured: Position Overview → Key Duties → Qualifications → Effort → Responsibilities → Classification → Appendix A/B/C
- New JSON audit trail export endpoint (`POST /api/export/json`)
- WeasyPrint system dependency fix documented (requires `brew install pango cairo gdk-pixbuf`)

**Phases completed:** 26 through 30 (Plans 26-01 through 30-03, 14 plans total; Plan 29-04 confirmed implemented)

**Post-shipment UAT fixes (2026-03-13):**
- HF-01: WeasyPrint system dependency fix (`brew install pango cairo gdk-pixbuf`)
- HF-02/03/04: OCHRO Job Architecture filter fully implemented — Managerial Level + hierarchical Job Function → Job Family; parent checkbox and count-mismatch bugs resolved

**Note:** Formal GSD milestone verification not yet run as of 2026-03-16. Informal browser UAT confirmed core workflow and all three exports (PDF/Word/JSON) working.

*Milestone record updated: 2026-03-16*
