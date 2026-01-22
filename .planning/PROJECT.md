# JD Builder Lite

## What This Is

A demo web application that helps managers create job descriptions by selecting content from Canada's official National Occupational Classification (NOC) database via the OASIS site. The tool demonstrates compliance with the Directive on Automated Decision-Making by providing full provenance, traceability, and audit trails for all content in the generated job description.

## Core Value

Every piece of content in the final job description can be traced back to its authoritative source (NOC/OASIS), with clear documentation of human decisions and AI involvement - demonstrating compliant, transparent, accountable job description creation.

## Requirements

### Validated

- ✓ SRCH-01: Manager can search OASIS for matching profiles - v1.0
- ✓ SRCH-02: App displays search results with NOC codes and titles - v1.0
- ✓ SRCH-03: Manager can select a profile from results - v1.0
- ✓ DATA-01: App scrapes all relevant NOC data (Overview, Work Characteristics, Skills & Abilities, Interests, Employment Requirements, Skills for Success) - v1.0
- ✓ DATA-02: App extracts and stores metadata (NOC code, profile URL, retrieval timestamp, version) - v1.0
- ✓ DISP-01: App presents NOC data organized by JD Element headers - v1.0
- ✓ DISP-02: Manager can select multiple statements under each JD Element header - v1.0
- ✓ DISP-03: App tracks which NOC source attribute each statement came from - v1.0
- ✓ AI-01: App generates General Overview using OpenAI API, informed by all selected statements - v1.0
- ✓ AI-02: App records AI generation metadata (model, timestamp, input statements) - v1.0
- ✓ OUT-01: App displays preview of assembled job description - v1.0
- ✓ OUT-02: Manager can export final JD to PDF - v1.0
- ✓ OUT-03: Final JD includes compliance metadata block (NOC code, source URLs, retrieval timestamp) - v1.0
- ✓ OUT-04: Final JD includes full audit trail (manager selections per JD Element, traced to NOC source) - v1.0
- ✓ OUT-05: Final JD includes AI disclosure (General Overview marked as AI-generated, inputs listed, model and timestamp) - v1.0

### Active

**v1.1 Milestone: Enhanced Data Display + Export Options**

*Search Results Improvements:*
- [ ] SRCH-04: Search results show grid view toggle (card vs table)
- [ ] SRCH-05: Search results display NOC code next to profile title
- [ ] SRCH-06: Grid view shows columns: Broad category, Training/Education, Lead statement

*Statement Display Enhancements:*
- [ ] DISP-04: Each JD Element tab shows category definition at top (from guide.csv)
- [ ] DISP-05: Each statement includes OASIS label description (from guide.csv)
- [ ] DISP-06: Statements show proficiency/complexity level (1-5 stars)
- [ ] DISP-07: Level display includes scale meaning (e.g., "5 - Highest Level" or "5 - Every day, many times per day")
- [ ] DISP-08: Work Context statements show appropriate dimension (Frequency, Duration, Degree of responsibility, etc.)

*Data Bug Fixes:*
- [ ] DATA-03: Responsibilities header populated (filter Work Context for "responsib" / "decision")
- [ ] DATA-04: Effort header captures all "effort" statements from Work Context
- [ ] DATA-05: Work Context scraping extracts complete data

*Profile Overview Enhancements:*
- [ ] DISP-09: Profile page shows NOC code prominently under title
- [ ] DISP-10: Profile page displays NOC hierarchical breakdown (TEER, broad category, major group)
- [ ] DISP-11: Reference NOC attributes displayed (job requirements, career mobility, example titles, interests, personal attributes)

*Export Enhancements:*
- [ ] OUT-06: Manager can export final JD to Word/DOCX
- [ ] OUT-07: Export includes Annex section with unused NOC attributes

### Out of Scope

- User authentication - single user demo only
- Database/persistence - no saved history, create -> PDF -> done
- Multi-user support - not needed for demo
- Production hosting - runs locally only
- Client Service Results section - requires org-specific business capability data (v2.0 feature)
- Organizational Context section - requires org-specific mandate/ID data (v2.0 feature)
- Annex section with excluded NOC attributes - now in v1.1 scope

## Context

**Current State (v1.0):**
- Shipped v1.0 with 5,130 LOC (Python, HTML, CSS, JS)
- Tech stack: Flask, BeautifulSoup, OpenAI SDK, WeasyPrint, python-docx, vanilla JS
- Full TBS Directive compliance (sections 6.2.3, 6.2.7, 6.3.5)
- Provenance chain complete from OASIS scrape to PDF export

**Regulatory Context:**
This tool demonstrates compliance with the Treasury Board's Directive on Automated Decision-Making (https://www.tbs-sct.canada.ca/pol/doc-eng.aspx?id=32592). The directive requires transparency, accountability, and human oversight in automated decision systems.

**Data Source:**
- OASIS site: https://noc.esdc.gc.ca/OaSIS/OaSISWelcome
- No public API - requires HTML scraping
- Profile pages contain multiple tabs: Overview, Work Characteristics, Skills and Abilities, Interests, Employment Requirements, Skills for Success
- **NEW for v1.1:** Open Canada CSV data at https://open.canada.ca/data/en/dataset/eeb3e442-9f19-4d12-8b38-c488fe4f6e5e
  - guide.csv: Category definitions, OASIS label descriptions, scale meanings
  - 20 CSV files covering all OASIS data (Skills, Abilities, Work Context, etc.)
  - Scale definitions: Proficiency (1-5), Importance (1-5), Complexity (1-5), Frequency (1-5), Duration (1-5), Degree of responsibility (1-5), etc.

## Constraints

- **Tech stack**: Simple - vanilla HTML/CSS/JS frontend, Python/Flask backend
- **Deployment**: Local only (localhost) - no cloud hosting
- **Data access**: Live scraping from OASIS (no pre-cached data)
- **LLM provider**: OpenAI API (requires API key)
- **Complexity**: Demo-quality, minimal - not production-grade
- **Single user**: No auth, no multi-tenancy, no persistence

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Vanilla JS over framework | Demo simplicity, no build step, easy to understand | ✓ Good - fast development, zero dependencies |
| Live scraping over cached data | Always shows current NOC data, no sync issues | ✓ Good - always fresh data |
| Python/Flask backend | Better scraping ecosystem (BeautifulSoup, lxml), CORS proxy for frontend | ✓ Good - clean service layer |
| Full compliance metadata in output | Core value proposition - demonstrates Directive compliance | ✓ Good - audit-ready output |
| OpenAI for General Overview | User preference, widely available | ✓ Good - quality generation |
| Provenance metadata from start | Ensures audit trail built in from foundation | ✓ Good - no retrofit needed |
| Service layer separation | Separation of concerns for testability | ✓ Good - clean architecture |
| CSS selector abstraction | Prevents brittle selector spread across codebase | ✓ Good - centralized maintenance |
| Native details/summary accordions | Built-in accessibility, no JS required | ✓ Good - screen reader support |
| Proxy-based state management | Auto-persist to localStorage, subscription pattern | ⚠️ Revisit - Proxy.set doesn't fire on nested updates |
| SSE for streaming generation | Standard protocol, works with POST requests | ✓ Good - real-time UX |
| WeasyPrint for PDF | CSS @page rules, professional output | ✓ Good - print-quality PDFs |
| Directive section references | TBS Directive compliance audit trail | ✓ Good - demonstrable compliance |

## Current Milestone: v1.1 Enhanced Data Display + Export

**Goal:** Enrich statement display with OASIS metadata (definitions, descriptions, proficiency levels with scale meanings), fix data extraction bugs, add Word export and Annex section.

**Target features:**
- Search results grid view with more data columns
- Category definitions and statement descriptions from guide.csv
- Proficiency/complexity levels with scale meaning display
- Work Context filtering fixes (Responsibilities, Effort)
- Word/DOCX export option
- Annex section for reference NOC attributes

---
*Last updated: 2026-01-22 after v1.1 milestone started*
