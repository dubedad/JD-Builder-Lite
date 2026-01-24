# Project Milestones: JD Builder Lite

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
