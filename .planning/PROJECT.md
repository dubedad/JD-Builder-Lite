# JD Builder Lite

## What This Is

A demo web application that helps managers create job descriptions by selecting content from Canada's official National Occupational Classification (NOC) database. Content is served from JobForge 2.0 gold parquet files (sub-second search, 900 profiles) with automatic OASIS fallback for data not yet covered by parquet. The tool demonstrates compliance with the Directive on Automated Decision-Making with full provenance, traceability, and audit trails — including per-section source distinction between JobForge parquet and live OASIS scraping. Features an OaSIS-mirrored interface with Keyword/Code search toggle, result cards with 6 data points, LLM-powered profile headers with occupation icons, tabbed Job Header navigation, and accessible statement selection with tooltips. Exports to PDF/DOCX with full compliance metadata, Annex sections, and per-section provenance badges.

## Core Value

Every piece of content in the final job description can be traced back to its authoritative source (JobForge parquet or OASIS), with clear documentation of human decisions and AI involvement — demonstrating compliant, transparent, accountable job description creation.

## Current Milestone: v5.1 UI Overhaul

**Goal:** Redesign the entire application UI to match the JobForge reference prototype — new global chrome, 5-step stepper, redesigned search/build/classify pages, and two new functional pages (Generate, Export) with restructured PDF/DOCX/JSON output.

**Target features:**
- Global chrome: Government of Canada header, dark navy JobForge app bar, data source pills, 5-step stepper, Selections drawer, compliance footer
- Search: "Find your Job" layout, new occupation cards, 6-group filter panel
- Build: dark navy occupation header card, icons on tabs, section description boxes, level-grouped items, Core Competencies selectable, Key Activities two-list split, blue dot ratings retained
- Navigation: 3-button bar, selection persistence, Preview modal, Selections right-drawer
- Classification: re-styled in new chrome, Statement Alignment Comparison, Key Evidence, Caveats sections
- Generate (new page): DADM compliance badges, OpenAI generation with "Generate with AI" button
- Export (new page): JD preview, compliance cards, Download PDF / Word / JSON
- New PDF format: restructured with Data Provenance & Compliance + Policy Provenance table

## Requirements

### Validated

**v1.0 MVP:**
- ✓ SRCH-01: Manager can search OASIS for matching profiles — v1.0
- ✓ SRCH-02: App displays search results with NOC codes and titles — v1.0
- ✓ SRCH-03: Manager can select a profile from results — v1.0
- ✓ DATA-01: App scrapes all relevant NOC data (Overview, Work Characteristics, Skills & Abilities, Interests, Employment Requirements, Skills for Success) — v1.0
- ✓ DATA-02: App extracts and stores metadata (NOC code, profile URL, retrieval timestamp, version) — v1.0
- ✓ DISP-01: App presents NOC data organized by JD Element headers — v1.0
- ✓ DISP-02: Manager can select multiple statements under each JD Element header — v1.0
- ✓ DISP-03: App tracks which NOC source attribute each statement came from — v1.0
- ✓ AI-01: App generates General Overview using OpenAI API, informed by all selected statements — v1.0
- ✓ AI-02: App records AI generation metadata (model, timestamp, input statements) — v1.0
- ✓ OUT-01: App displays preview of assembled job description — v1.0
- ✓ OUT-02: Manager can export final JD to PDF — v1.0
- ✓ OUT-03: Final JD includes compliance metadata block (NOC code, source URLs, retrieval timestamp) — v1.0
- ✓ OUT-04: Final JD includes full audit trail (manager selections per JD Element, traced to NOC source) — v1.0
- ✓ OUT-05: Final JD includes AI disclosure (General Overview marked as AI-generated, inputs listed, model and timestamp) — v1.0

**v1.1 Enhanced Data Display + Export:**
- ✓ SRCH-04: Search results show grid view toggle (card vs table) — v1.1
- ✓ SRCH-05: Search results display NOC code next to profile title — v1.1
- ✓ DISP-04: Each JD Element section shows category definition at top (from guide.csv) — v1.1
- ✓ DISP-05: Each statement includes OASIS label description (from guide.csv lookup) — v1.1
- ✓ DISP-06: Statements display proficiency/complexity level as circles (1-5) — v1.1
- ✓ DISP-07: Circle ratings include scale meaning label (e.g., "5 - Highest Level" for Skills) — v1.1
- ✓ DISP-08: Work Context statements show dimension type (Frequency, Duration, Degree of responsibility, etc.) — v1.1
- ✓ DATA-03: Responsibilities header populated with Work Context items containing "responsib" or "decision" — v1.1
- ✓ DATA-04: Effort header captures all Work Context items containing "effort" — v1.1
- ✓ DATA-05: Work Context scraping extracts complete data from OASIS — v1.1
- ✓ DISP-09: Profile page shows NOC code prominently under title — v1.1
- ✓ DISP-10: Profile page displays NOC hierarchical breakdown (TEER, broad category, major group) — v1.1
- ✓ DISP-11: Profile page displays reference NOC attributes (job requirements, career mobility, example titles, interests, personal attributes) — v1.1
- ✓ OUT-06: Manager can export final JD to Word/DOCX format — v1.1
- ✓ OUT-07: PDF export includes Annex section with unused NOC reference attributes — v1.1
- ✓ OUT-08: DOCX export includes Annex section with unused NOC reference attributes — v1.1

**v2.0 UI Redesign:**
- ✓ SRCH-10: Search bar with pill toggle for Keyword/Code search modes — v2.0
- ✓ SRCH-11: Authoritative sources footnote below search bar — v2.0
- ✓ SRCH-12: Removed advanced search and A-Z links — v2.0
- ✓ DISP-20: Card view with 6 data points (lead statement, TEER, broad category, matching criteria) — v2.0
- ✓ DISP-21: Grid view with custom columns — v2.0
- ✓ DISP-22: Custom filters (Minor Unit Group, Feeder Mobility UI, Career Progression UI) — v2.0
- ✓ DISP-23: Card/grid click navigation to profile page — v2.0
- ✓ DISP-30: Profile header with LLM-driven occupation icon — v2.0
- ✓ DISP-31: OaSIS code badge below title — v2.0
- ✓ DISP-32: LLM-generated paragraph description above tabs — v2.0
- ✓ DISP-33: Horizontal Job Header tabs with ARIA navigation — v2.0
- ✓ DISP-34: Tab content mapping (Key Activities, Skills, Effort, Responsibility, Career) — v2.0
- ✓ SRCH-13: Search results scored by confidence % with rationale explaining each match, sorted best-first — v2.0
- ✓ SEL-01: Checkboxes on all statements in all tabs — v2.0
- ✓ SEL-02: Proficiency circles display (filled/empty) — v2.0
- ✓ SEL-03: Provenance labels always visible — v2.0
- ✓ SEL-04: Description tooltip on hover with keyboard accessibility — v2.0
- ✓ SEL-05: Single Create JD button with selection count — v2.0

**v3.0 Style-Enhanced Writing (SHIPPED 2026-02-03):**
- ✓ Style Infrastructure: Vocabulary index from JobForge parquet, style analysis pipeline — v3.0
- ✓ Constrained Generation: Few-shot styling with vocabulary validation and retry — v3.0
- ✓ Compliance: Extended provenance, differentiated AI disclosure, vocabulary audit — v3.0
- ✓ Export: Styled PDF/DOCX with dual-format display and compliance metadata — v3.0

**v4.0 Occupational Group Allocation (SHIPPED 2026-02-04):**
- ✓ DATA-01 through DATA-05: DIM_OCCUPATIONAL table with 426 groups, 900 inclusions, 330 exclusions — v4.0
- ✓ MATCH-01 through MATCH-08: OccupationalGroupAllocator with semantic shortlisting and LLM classification — v4.0
- ✓ OUT-01 through OUT-07: Ranked recommendations with confidence, rationale, evidence — v4.0
- ✓ PROV-01 through PROV-05: Policy provenance traceable to TBS Classification Policy and DADM — v4.0
- ✓ API-01 through API-04: POST /api/allocate with provenance map and edge case handling — v4.0
- ✓ UI-01 through UI-05: Recommendation cards with confidence bars, expandable details, evidence highlighting — v4.0
- ✓ EDGE-01 through EDGE-04: AP/TC disambiguation, split duties, invalid combination detection — v4.0

**v4.1 Polish (SHIPPED 2026-02-07):**
- ✓ TAB-01 through TAB-06: Split Skills into Skills/Abilities/Knowledge, Core Competencies own tab, consolidate Overview — v4.1
- ✓ NAV-01 through NAV-03: Classify from preview, Return to Builder from classification, fix Back to Edit — v4.1
- ✓ UX-01 through UX-04: Coaching tone for Invalid Combination, dimension type labels on circles, filter hierarchy headings — v4.1
- ✓ EXP-01 through EXP-02: Classification results exportable — v4.1
- ✓ DOC-01: GitHub README update — v4.1
- Note: Phase 20 (Evidence & Provenance Display) deferred indefinitely

**v5.0 JobForge 2.0 Integration (SHIPPED 2026-03-10):**
- ✓ DATA-01: Structured inventory of 25 gold parquet files with schema, row counts, OASIS mapping — v5.0
- ✓ DATA-02: Explicit gap analysis with 5 named gaps (Main Duties, Interests, Personal Attributes, Core Competencies, Career Mobility) — v5.0
- ✓ DATA-03: CoverageStatus(str, Enum) with LOAD_ERROR/NOT_FOUND/FOUND — three distinct failure modes — v5.0
- ✓ DATA-04: logger.warning() on all data load failure paths (24 in labels_loader.py, 3 in vocabulary/index.py) — v5.0
- ✓ PROF-01: Profile tabs (Skills, Abilities, Knowledge, Work Activities, Work Context) from parquet for all 900 profiles — v5.0
- ✓ PROF-02: Transparent OASIS fallback for Key Activities, Interests, Core Competencies — v5.0
- ✓ PROF-03: Per-section provenance in exported JD (all 5 sections in compliance appendix, including working_conditions) — v5.0
- ✓ PROF-04: Column whitespace stripped at read_parquet_safe time — v5.0
- ✓ SRCH-01: Sub-second parquet search (155-234ms cold, 75-124ms warm) — v5.0
- ✓ SRCH-02: Five-tier relevance scoring (100/95/90/80/50) from parquet — v5.0
- ✓ SRCH-03: Transparent OASIS fallback on parquet unavailability or zero results — v5.0

### Active

**v5.1 UI Overhaul (current milestone):**
- [ ] Full UI redesign matching JobForge reference prototype (screenshots in `.planning/ui-walkthrough-v5.1/`)
- [ ] New global chrome across all pages (GoC header, dark navy app bar, stepper, drawer, footer)
- [ ] Search page: "Find your Job" layout + new cards + 6-group filter panel
- [ ] Build page: occupation header card, tab icons, section description boxes, level grouping, inline sub-descriptions
- [ ] Core Competencies selectable; Key Activities retains Main Duties / Work Activities split
- [ ] Navigation: 3-button bar, selection persistence, Preview modal, Selections drawer
- [ ] Classification page re-styled; post-analysis adds Statement Alignment Comparison, Key Evidence, Caveats
- [ ] Generate page (new): DADM badges, OpenAI generation, Regenerate
- [ ] Export page (new): JD preview, compliance cards, Download PDF / Word / JSON
- [ ] New PDF format: Data Provenance & Compliance + Policy Provenance table

**v6.0 Classification Step 2 (Deferred):**
- Job Evaluation Standards scoring
- Benchmark position comparison UI
- Manager consultation workflow

**Deferred:**
- SRCH-06: Grid view shows columns: Broad category, Training/Education, Lead statement
- SRCH-07: Filter items by Job Family
- SRCH-08: Filter items by Organizational Unit
- SRCH-09: Filter items by Digital Competencies
- DISP-12: Visual scale distinction by category type (different colors/styles)
- DISP-13: "Learn More" links to OASIS source for each statement
- OUT-09: "Include Annex" checkbox toggle in export options
- OUT-10: Custom compliance styling in DOCX (matching PDF quality)
- OGM-01 through OGM-05: Occupational Group Matching (v3.1 scope)

### Out of Scope

- User authentication — single user demo only
- Database/persistence — no saved history, create → PDF → done
- Multi-user support — not needed for demo
- Production hosting — runs locally only
- Client Service Results section — requires org-specific business capability data (v2.0 feature)
- Organizational Context section — requires org-specific mandate/ID data (v2.0 feature)
- Inline rating editing — breaks provenance (ratings come from NOC, not user input)
- Custom statement creation — breaks audit trail (all content must trace to NOC source)

## Context

**Current State (v5.0):**
- Shipped v5.0 with ~35,196 LOC Python + HTML/CSS/JS
- Tech stack: Flask, BeautifulSoup, OpenAI SDK, WeasyPrint, python-docx, pandas (parquet), vanilla JS
- Full TBS Directive compliance (sections 6.2.3, 6.2.7, 6.3.5) with per-section source provenance
- JobForge 2.0 gold parquet (25 files) as primary data source; OASIS as explicit fallback for 5 gaps
- Sub-second search (155-234ms cold) from parquet; profile tabs from parquet for all 900 profiles
- Classification Step 1: Occupational Group Allocation with 426 groups, semantic matching, LLM classification
- Note: sentence-transformers unavailable (Python 3.14); TF-IDF fallback active for semantic matching

**Regulatory Context:**
This tool demonstrates compliance with the Treasury Board's Directive on Automated Decision-Making (https://www.tbs-sct.canada.ca/pol/doc-eng.aspx?id=32592). The directive requires transparency, accountability, and human oversight in automated decision systems.

**Data Sources:**
- OASIS site: https://noc.esdc.gc.ca/OaSIS/OaSISWelcome
- JobForge 2.0 gold parquet: 25 files (local), primary data source since v5.0
- Open Canada CSV data: guide.csv (Category definitions, OASIS label descriptions, scale meanings)

## Constraints

- **Tech stack**: Simple — vanilla HTML/CSS/JS frontend, Python/Flask backend
- **Deployment**: Local only (localhost) — no cloud hosting
- **Data access**: JobForge gold parquet (primary) + live OASIS scraping (fallback)
- **LLM provider**: OpenAI API (requires API key)
- **Complexity**: Demo-quality, minimal — not production-grade
- **Single user**: No auth, no multi-tenancy, no persistence

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Vanilla JS over framework | Demo simplicity, no build step, easy to understand | ✓ Good |
| Live scraping over cached data | Always shows current NOC data, no sync issues | ✓ Good |
| Python/Flask backend | Better scraping ecosystem (BeautifulSoup, lxml), CORS proxy | ✓ Good |
| Full compliance metadata in output | Core value proposition — demonstrates Directive compliance | ✓ Good |
| OpenAI for General Overview | User preference, widely available | ✓ Good |
| Provenance metadata from start | Ensures audit trail built in from foundation | ✓ Good |
| Service layer separation | Separation of concerns for testability | ✓ Good |
| Native details/summary accordions | Built-in accessibility, no JS required | ✓ Good |
| SSE for streaming generation | Standard protocol, works with POST requests | ✓ Good |
| WeasyPrint for PDF | CSS @page rules, professional output | ✓ Good |
| Backend enrichment over frontend joins | Avoid O(n*m) lookup performance issues | ✓ Good |
| UTF-8-sig encoding for CSV | Handle Windows BOM in guide.csv | ✓ Good |
| Unicode circles over icon libraries | Zero-dependency WCAG accessibility solution | ✓ Good |
| Annex after Appendix A | Clear separation between compliance metadata and reference attributes | ✓ Good |
| Module-level singleton for CSV loader | Zero-latency lookups via load-on-import | ✓ Good |
| localStorage with sessionStorage fallback | Handles QuotaExceededError gracefully | ✓ Good |
| Proxy-based state management | Auto-persist to localStorage, subscription pattern | ⚠️ Revisit |
| Keyword/Code pill toggle | Mimics OASIS UI, clear visual distinction between search modes | ✓ Good |
| EnrichedSearchResult model | Progressive enhancement - card data from search, profile data later | ✓ Good |
| 16 semantic icon categories | Balanced coverage of NOC occupation types without overwhelming LLM | ✓ Good |
| Temperature 0 for icons, 0.3 for descriptions | Deterministic icons, slight creativity for descriptions | ✓ Good |
| CSS ::after tooltips over JS library | Simpler, faster, no dependencies | ✓ Good |
| ARIA tab pattern with automatic activation | Arrow keys navigate and activate in single operation | ✓ Good |
| Single Create button | Removes dual-button confusion, overview generation in Create flow | ✓ Good |
| Few-shot prompting for style | No fine-tuning needed; learns style from 2-5 examples in prompt | ✓ Good |
| Post-validation over constrained decoding | OpenAI API limits logit_bias to ~300 tokens; validation + retry more reliable | ✓ Good |
| Provenance before generation | Research warns retrofit is difficult; design audit trail schema first | ✓ Good |
| pdfplumber for PDF extraction | MIT license, verified PyPI version, handles text-based PDFs | ✓ Good |
| Append-only temporal design | Provenance requires immutable history for DIM_OCCUPATIONAL | ✓ Good |
| sentence-transformers for semantic matching | Fast local inference, no API calls needed for shortlisting | ✓ Good |
| instructor library for structured LLM outputs | Pydantic integration, reliable schema enforcement | ✓ Good |
| 60/30/10 confidence formula | Definition fit primary (60%), semantic verification (30%), labels boost (10%) | ✓ Good |
| Inclusions for shortlisting only | Help identify candidates but don't boost confidence scores | ✓ Good |
| Relevance scoring in API route (not parser) | Parser lacks query context; route has both query and results for scoring | ✓ Good |
| Word-stem matching for relevance scoring | "Printer" stems to "print" to match "Printing" — exact substring fails across word forms | ✓ Good |
| JobForge parquet as primary data source | Sub-second search vs 5-60s OASIS path; deterministic, portable, no scraping fragility | ✓ Good |
| OASIS retained as explicit fallback | Parquet has 5 gaps (Main Duties, Interests, etc.); fallback ensures completeness | ✓ Good |
| CoverageStatus(str, Enum) three-state type | Three distinct failure modes (LOAD_ERROR/NOT_FOUND/FOUND) must not be collapsed | ✓ Good |
| Column stripping at read_parquet_safe time | Strip once at read, consistent for all callers — not at lookup time | ✓ Good |
| Parquet-first with OASIS fallback pattern | Try parquet, fall through transparently on failure — single code path for both sources | ✓ Good |
| Two-block try/except in /api/profile | OASIS fetch + mapper+response separate — parquet tabs served even when OASIS unreachable | ✓ Good |
| Per-section provenance in export | All 5 JD sections record source ("jobforge" vs "oasis") in TBS compliance appendix | ✓ Good |
| Symmetric search scoring (both paths 90) | OASIS and parquet stem-in-title tier score identically — no ranking bias by data source | ✓ Good |

---
*Last updated: 2026-03-11 after v5.1 milestone start*
