# Project Milestones: JD Builder Lite

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
