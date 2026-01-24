# JD Builder Lite

## What This Is

A demo web application that helps managers create job descriptions by selecting content from Canada's official National Occupational Classification (NOC) database via the OASIS site. The tool demonstrates compliance with the Directive on Automated Decision-Making by providing full provenance, traceability, and audit trails for all content in the generated job description. Includes enriched statement display with proficiency levels, NOC hierarchy breakdown, and export to PDF/DOCX with Annex sections.

## Core Value

Every piece of content in the final job description can be traced back to its authoritative source (NOC/OASIS), with clear documentation of human decisions and AI involvement - demonstrating compliant, transparent, accountable job description creation.

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

### Active

**v2.0 UI Redesign (Current Milestone):**

Goal: Redesign the JD Builder Lite UI to mirror the OaSIS website interface, following the swimlane process map with numbered steps.

Target features:
- UI-01: Step 1 Search Bar Redesign - Keyword/Code pill toggle, authoritative sources footnote
- UI-02: Step 4 Card View - Replicate OaSIS cards with 6 data points
- UI-03: Step 4 Grid View - Custom columns (Skills, Abilities, Knowledge)
- UI-04: Step 4 Custom Filters - Minor Unit Group, Feeder Group Mobility, Career Progression
- UI-05: Step 9 Profile Header - LLM icon, code badge, LLM paragraph description
- UI-06: Step 9 Job Header Tabs - Overview, Key Activities, Skills, Effort, Responsibility, Mobility
- UI-07: Step 10 Statement Selection - Checkboxes, proficiency circles, description tooltips on hover
- UI-08: Step 10 Create JD Button - Single action with selection count

**Deferred to v2.1:**
- SRCH-06: Grid view shows columns: Broad category, Training/Education, Lead statement
- SRCH-07: Filter items by Job Family
- SRCH-08: Filter items by Organizational Unit
- SRCH-09: Filter items by Digital Competencies
- DISP-12: Visual scale distinction by category type (different colors/styles)
- DISP-13: "Learn More" links to OASIS source for each statement
- OUT-09: "Include Annex" checkbox toggle in export options
- OUT-10: Custom compliance styling in DOCX (matching PDF quality)

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

**Current State (v1.1):**
- Shipped v1.1 with 7,868 LOC (Python, HTML, CSS, JS)
- Tech stack: Flask, BeautifulSoup, OpenAI SDK, WeasyPrint, python-docx, vanilla JS
- Full TBS Directive compliance (sections 6.2.3, 6.2.7, 6.3.5)
- Provenance chain complete from OASIS scrape to PDF/DOCX export
- Enriched data pipeline using guide.csv for category definitions and scale meanings
- OASIS-style proficiency circles with WCAG 2.1 Level AA accessibility

**Regulatory Context:**
This tool demonstrates compliance with the Treasury Board's Directive on Automated Decision-Making (https://www.tbs-sct.canada.ca/pol/doc-eng.aspx?id=32592). The directive requires transparency, accountability, and human oversight in automated decision systems.

**Data Sources:**
- OASIS site: https://noc.esdc.gc.ca/OaSIS/OaSISWelcome
- No public API — requires HTML scraping
- Open Canada CSV data: https://open.canada.ca/data/en/dataset/eeb3e442-9f19-4d12-8b38-c488fe4f6e5e
  - guide.csv: Category definitions, OASIS label descriptions, scale meanings
  - Scale definitions: Proficiency (1-5), Importance (1-5), Complexity (1-5), Frequency (1-5), Duration (1-5), etc.

## Constraints

- **Tech stack**: Simple — vanilla HTML/CSS/JS frontend, Python/Flask backend
- **Deployment**: Local only (localhost) — no cloud hosting
- **Data access**: Live scraping from OASIS (no pre-cached data)
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

---
*Last updated: 2026-01-24 — v2.0 UI Redesign milestone started*
