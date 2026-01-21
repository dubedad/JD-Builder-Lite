# Project Research Summary

**Project:** JD Builder Lite
**Domain:** Government data scraping + LLM integration + compliance tooling
**Researched:** 2026-01-21
**Confidence:** HIGH

## Executive Summary

JD Builder Lite is a compliance-focused job description builder that pulls data from Canada's NOC/OASIS database, allows users to select relevant content, optionally generates AI overviews, and exports PDF documents with full provenance tracking. The core differentiator is audit trail compliance with Canada's Directive on Automated Decision-Making, not feature breadth.

The recommended approach is a **3-tier architecture** with Python/Flask backend acting as a proxy and data transformation layer. The backend handles NOC site scraping (bypassing CORS), HTML parsing, OpenAI integration (protecting API keys), and data mapping. The frontend is vanilla HTML/CSS/JS with no build step. PDF generation uses fpdf2 (pure Python, Windows-friendly). This stack prioritizes simplicity and Windows compatibility appropriate for a single-user demo tool.

The critical risks are: (1) **LLM hallucinations** generating fabricated job requirements that break compliance traceability, (2) **brittle CSS selectors** that silently fail when government sites restructure, and (3) **incomplete audit trails** that undermine the core value proposition. Mitigation requires designing provenance schema first, using OpenAI Structured Outputs with source validation, and building selector abstraction layers with content validation from day one.

## Key Findings

### Recommended Stack

Python 3.12 with Flask 3.1.2 provides a lightweight, battle-tested backend appropriate for a single-user local demo. FastAPI's async features and Django's ORM/admin are unnecessary overhead. BeautifulSoup4 with lxml handles NOC site scraping reliably, and fpdf2 generates PDFs without Windows GTK dependency issues.

**Core technologies:**
- **Python 3.12 + Flask 3.1.2:** Web server and API routes — mature, simple, well-documented
- **BeautifulSoup4 + lxml:** HTML scraping and parsing — de-facto standard, handles messy government HTML
- **fpdf2 2.8.5:** PDF generation — pure Python, Windows-friendly, sufficient for document layout
- **OpenAI SDK 2.15.0:** LLM integration — official client with built-in retry logic
- **Vanilla HTML/CSS/JS:** Frontend — no build step, browser-native, demo-appropriate
- **python-dotenv:** Environment config — keeps API keys out of code

### Expected Features

**Must have (table stakes):**
- NOC search by job title
- Profile selection from results
- NOC data display organized by JD element
- Statement selection (checkbox UI)
- JD preview (real-time as selections change)
- PDF export with clear data attribution
- Basic provenance (NOC code + source URL in export)

**Should have (differentiators):**
- Full provenance trail (timestamps, source URLs, scrape metadata)
- AI-generated overview with "AI-generated" labeling
- NOC source metadata in export (audit-ready)
- Explainability section (NOC-to-JD mapping documentation)
- Compliance metadata block in PDF

**Defer (v2+):**
- User authentication (single-user demo)
- Multi-user collaboration
- ATS/HRIS integration
- Template library
- Bias detection (NOC language is government-vetted)
- Version history UI
- Multi-language support

### Architecture Approach

A 3-tier Backend-for-Frontend (BFF) architecture where the browser communicates only with the Flask backend, which proxies all external requests to OASIS and OpenAI. The backend transforms raw HTML into clean JSON shaped specifically for this frontend's needs. State is managed entirely in the browser; the backend is stateless.

**Major components:**
1. **Scrape Proxy** — fetches OASIS pages, bypasses CORS
2. **HTML Parser** — extracts NOC data using BeautifulSoup
3. **Data Mapper** — transforms NOC structure to JD elements
4. **LLM Proxy** — calls OpenAI securely, constructs prompts
5. **Frontend UI** — user interaction, display, PDF export

### Critical Pitfalls

1. **Brittle CSS selectors** — Government sites restructure; use semantic selectors, build fallbacks, validate content patterns, store raw HTML for debugging
2. **LLM hallucinations** — Use Structured Outputs (not JSON mode), constrain prompts to source material, validate generated content against source text
3. **Incomplete audit trail** — Design provenance schema FIRST, capture all transformations, reject outputs missing required provenance fields
4. **Rate limit crashes** — Implement exponential backoff with tenacity, cache responses, use separate API keys per environment
5. **PDF layout breaks** — Create print stylesheet before PDF implementation, use explicit positioning, avoid CSS Grid/Flexbox

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 1: Backend Foundation + Scraping Pipeline
**Rationale:** Everything depends on getting NOC data; frontend cannot function without backend endpoints; most likely to have issues (external site structure)
**Delivers:** Working Flask server that returns parsed, mapped JD data for any NOC profile URL
**Addresses:** NOC search, profile selection, OASIS scraping, data display structure
**Avoids:** CRITICAL-1 (brittle selectors) — build selector abstraction with validation from day one
**Includes:** Provenance schema design (CRITICAL-3 prevention)

### Phase 2: Frontend Core UI
**Rationale:** Now has real data to display; can iterate on UI with working backend
**Delivers:** Complete search, profile display, and selection interface
**Uses:** Flask backend from Phase 1, vanilla JS
**Implements:** User interaction flow, statement selection, JD preview
**Addresses:** Statement selection, JD preview, data attribution display

### Phase 3: LLM Integration
**Rationale:** Needs selections from UI; most expensive to test (API costs); can mock while developing prompts
**Delivers:** AI-generated overview with full provenance tracking
**Uses:** OpenAI SDK with Structured Outputs
**Avoids:** CRITICAL-2 (hallucinations), MODERATE-1 (rate limits), MODERATE-4 (JSON confusion)
**Implements:** Prompt construction, source validation, AI labeling

### Phase 4: PDF Export + Compliance
**Rationale:** Needs complete flow working; finishing touches, not core functionality
**Delivers:** Export-ready PDF with compliance metadata, full provenance block
**Uses:** fpdf2 for generation
**Avoids:** MODERATE-2 (layout breaks) — print stylesheet before implementation
**Implements:** Document assembly, compliance metadata, audit-ready formatting

### Phase 5: Polish + Hardening
**Rationale:** Integration testing, error handling, edge cases
**Delivers:** Demo-ready application with graceful degradation
**Addresses:** Health checks, error handling, fallback behaviors, SSL certificate handling

### Phase Ordering Rationale

- **Data pipeline first:** Search -> Profile -> Parse -> Map must work before any UI or AI features
- **UI before AI:** Statement selection drives AI generation input; can't build AI prompts without understanding selection data shape
- **Compliance throughout:** Provenance schema designed in Phase 1, enforced in every subsequent phase
- **PDF last:** Requires all content (selections + AI overview + metadata) to be complete

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 1 (Scraping):** NOC site structure may need real-world testing; SSL certificate handling needs investigation
- **Phase 3 (LLM):** Prompt engineering for compliance-safe generation; Structured Outputs schema design

Phases with standard patterns (skip research-phase):
- **Phase 2 (Frontend):** Standard form/selection UI, well-documented patterns
- **Phase 4 (PDF):** fpdf2 documentation is comprehensive; print CSS is standard
- **Phase 5 (Polish):** Error handling patterns are universal

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All versions verified on PyPI; mature, well-documented libraries |
| Features | HIGH | Directive requirements are explicit; commercial tool features well-documented |
| Architecture | HIGH | Standard BFF proxy pattern; well-established for scraping + API scenarios |
| Pitfalls | HIGH | Multiple authoritative sources; government compliance requirements clear |

**Overall confidence:** HIGH

### Gaps to Address

- **NOC site SSL certificates:** Research noted certificate verification issues; may need `verify=False` or custom cert handling
- **NOC site structure validation:** Selectors should be validated against live site before implementation
- **robots.txt compliance:** Could not fetch robots.txt due to cert issues; verify scraping is permitted
- **OpenAI Structured Outputs schema:** Exact schema for job description generation needs design during Phase 3

## Sources

### Primary (HIGH confidence)
- PyPI package documentation (Flask, BeautifulSoup4, fpdf2, OpenAI SDK) — verified versions 2026-01-21
- Canada Directive on Automated Decision-Making — authoritative compliance requirements
- OpenAI Structured Outputs documentation — hallucination mitigation patterns

### Secondary (MEDIUM confidence)
- JetBrains, Strapi framework comparisons — Flask vs FastAPI rationale
- Templated.io, DEV Community — PDF library comparisons
- Real Python, GeeksforGeeks — web scraping patterns
- Gartner, Ongig, JDXpert — commercial JD tool feature analysis

### Tertiary (LOW confidence)
- NOC site structure — may have changed since research; needs live validation
- robots.txt status — could not verify due to SSL issues

---
*Research completed: 2026-01-21*
*Ready for roadmap: yes*
