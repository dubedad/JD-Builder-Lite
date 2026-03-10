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

---

# v1.1 Research Summary

**Milestone:** v1.1 Enhanced Data Display + Export
**Researched:** 2026-01-22
**Confidence:** HIGH

## Executive Summary

v1.1 enhances the existing JD Builder Lite with CSV-based data enrichment (category definitions, proficiency levels, statement descriptions from Open Canada guide.csv), Work Context filtering fixes, and parallel DOCX export. The integration requires NO new external dependencies - Python's built-in csv module handles data loading, python-docx 1.2.0 (already in requirements.txt) handles Word export, and vanilla JavaScript with CSS handles enhanced UI components. The critical insight is that enrichment should happen on the backend at profile fetch time, not in frontend rendering, to avoid O(n*m) lookup performance issues. The highest risks are CSV encoding BOM issues (silent failure on Windows-exported files), python-docx BytesIO memory leaks, and localStorage quota exhaustion from caching enriched data.

## Key Findings

### Stack (No New Dependencies Required)

v1.1 extends the v1.0 stack without adding external dependencies. Python's built-in csv module parses guide.csv using csv.DictReader for header-mapped row access. python-docx 1.2.0 (already installed) handles Word document generation. Vanilla JavaScript with CSS Grid provides grid view toggle functionality. Unicode star characters (U+2605/U+2606) with CSS render proficiency ratings without icon libraries.

**Key Technologies:**
- **Python csv module (built-in):** Parse guide.csv with DictReader pattern — standard library, zero dependencies
- **python-docx 1.2.0 (existing):** DOCX export with Annex section — already in requirements.txt, proven implementation
- **CSS Grid (browser-native):** Grid view toggle — stable across modern browsers, no framework needed
- **Unicode stars:** Star rating display — accessible, zero dependency solution

### Features (Enhanced Display + Export)

v1.1 features fall into two categories: enhanced data display (showing OASIS metadata with statements) and export improvements (DOCX format, Annex section with reference attributes).

**Enhanced Display (Table Stakes):**
- Visual star display (1-5 stars) for proficiency/importance/complexity levels
- Scale meaning labels explaining what each rating level means
- Category definitions at top of each JD Element tab
- Statement descriptions from guide.csv (tooltip/popover display)
- Grid view toggle for search results (card vs table comparison)

**Export Enhancements (Table Stakes):**
- DOCX export matching PDF structure (same sections, compliance appendix)
- Annex section with reference NOC attributes (example titles, interests, career mobility)
- Correct Work Context dimension handling (Frequency, Duration, Responsibility scales)

**Deferred Features:**
- Column sorting/customization in grid view (nice-to-have, adds complexity)
- Filter by rating level (power user feature, defer to v1.2)
- Animated star filling (visual gimmick without functional value)
- Inline editing of ratings (breaks provenance chain, violates compliance)

### Architecture (Backend Enrichment Pattern)

v1.1 extends the existing v1.0 architecture with a CSV data loading service and enrichment layer. The critical architectural decision is enrichment location: backend enrichment at profile fetch time avoids frontend performance issues and keeps CSV data abstracted from the browser.

**New Components:**
1. **CSV Loader Service (src/services/csv_loader.py):** Load guide.csv once at startup, provide lookup methods, module-level singleton pattern
2. **Enrichment Service (src/services/enrichment_service.py):** Enrich NOCStatements with descriptions, proficiency levels, scale meanings, dimension names
3. **Grid View Component (static/js/grid-view.js):** Toggle between card and table view, persist preference in localStorage
4. **Enhanced Statement Display (static/js/statement-display.js):** Render stars, descriptions, scale meanings, dimension badges

**Integration Points:**
- CSV loaded at app startup via `@app.before_first_request` (singleton pattern)
- Enrichment called in `/api/profile` route after mapping, before response
- Frontend receives fully enriched ProfileResponse with new optional fields
- DOCX/PDF generators extend to include Annex section from reference_attributes

**Data Flow:**
```
App Start -> Load guide.csv -> Cache in memory
    |
/api/profile -> Scrape -> Parse -> Map -> Enrich -> Return enriched JSON
    |
Frontend -> Render with stars, descriptions, dimensions
    |
Export -> Build ExportData with Annex -> Generate PDF/DOCX
```

### Critical Risks

1. **CSV Encoding BOM Issues (CRITICAL):** Windows Excel exports include UTF-8 BOM causing first column name to be '\ufeffNOC_Code' instead of 'NOC_Code', breaking all dictionary lookups. Silent failure - data appears to load but all lookups return None. **Mitigation:** Use `encoding='utf-8-sig'` when reading CSVs, validate column names after load, test with Windows-exported files.

2. **python-docx Memory Leaks (CRITICAL):** BytesIO objects created for DOCX generation persist in memory after function return, causing gradual memory exhaustion in long-running Flask processes. **Mitigation:** Use context manager pattern (`with BytesIO() as buffer`), explicitly close buffers, test repeated exports to verify no accumulation.

3. **localStorage Quota Exhaustion (CRITICAL):** Adding enriched CSV data to state exceeds 5MB browser limit, throwing QuotaExceededError that breaks entire frontend. No graceful degradation in current state.js implementation. **Mitigation:** Cache only active profile enrichment (not entire CSV), implement quota checks with fallback to in-memory state, add size monitoring.

4. **CSV Lookup Performance (CRITICAL):** Naive O(n*m) joins on every statement render causes 50,000+ lookups per page load with 50 statements and 1000+ CSV rows, creating 2+ second lag and unresponsive browser. **Mitigation:** Pre-compute enrichment on backend (not frontend), use Map-based indexing if frontend joins needed, measure with performance profiling.

5. **Star Rating Accessibility (MODERATE):** Incorrect ARIA implementation causes screen readers to announce "image 4 out of 5 stars star star star star star" with repetitive output, violating WCAG 2.1 Level AA required for TBS compliance. **Mitigation:** Use aria-hidden on decorative stars, single aria-label on container, test with NVDA/VoiceOver.

## Implications for Roadmap

v1.1 follows a clear dependency chain from data infrastructure through backend enrichment to frontend display and finally export features. Build order must respect this flow.

### Suggested Phase Structure

**Phase 1: CSV Infrastructure (Build First)**
- Components: csv_loader.py, enrichment_service.py, extended NOCStatement model
- Rationale: Foundation for all enhancements; no frontend dependencies; can test independently
- Delivers: CSV loaded at startup, enrichment service operational
- Avoids: PITFALL-1 (CSV encoding BOM), PITFALL-8 (repeated CSV loading)
- Research needed: None - Python csv module well-documented

**Phase 2: Backend Enrichment (Build Second)**
- Components: Modified mapper.py, modified /api/profile route, Work Context filtering fix
- Rationale: Depends on Phase 1; frontend needs enriched data to display; can test with curl/Postman
- Delivers: /api/profile returns enriched statements with descriptions, levels, scale meanings
- Avoids: PITFALL-4 (lookup performance) by enriching on backend
- Research needed: None - extends existing mapper pattern

**Phase 3: Frontend Enhanced Display (Build Third)**
- Components: statement-display.js, statement-enhancements.css, profile-header.js, star ratings
- Rationale: Depends on Phase 2 enriched responses; core user-facing feature
- Delivers: Statements show stars, descriptions, scale meanings; category definitions visible
- Avoids: PITFALL-6 (star rating accessibility), PITFALL-3 (localStorage quota)
- Research needed: None - standard UX patterns, WCAG compliance documented

**Phase 4: Grid View (Build Fourth, Optional Parallel)**
- Components: grid-view.js, grid.css, modified search.js
- Rationale: Independent of enrichment; can build parallel with Phase 3; enhancement not core
- Delivers: Grid toggle functional, table view displays, preference persists
- Avoids: PITFALL-10 (performance without virtualization) - acceptable for <50 results
- Research needed: None - CSS Grid stable, vanilla JS patterns

**Phase 5: Annex Export (Build Last)**
- Components: Modified export_service.py, extended pdf_generator.py, extended docx_generator.py
- Rationale: Depends on reference_attributes from Phase 2; output feature not core functionality
- Delivers: Annex section in PDF and DOCX exports with reference attributes
- Avoids: PITFALL-2 (BytesIO leaks), PITFALL-7 (PDF/DOCX divergence), PITFALL-15 (structure misalignment)
- Research needed: None - extends existing export pattern

### Critical Path

```
Phase 1 (CSV Infrastructure)
    | REQUIRED
Phase 2 (Backend Enrichment)
    | REQUIRED
Phase 3 (Enhanced Display) + Phase 4 (Grid View - PARALLEL OK)
    | REQUIRED
Phase 5 (Annex Export)
```

### Phase Ordering Rationale

- **CSV Infrastructure first:** All downstream features depend on guide.csv being loaded and queryable
- **Backend enrichment before frontend display:** Avoids performance pitfalls and keeps CSV abstracted from browser
- **Grid view can be parallel:** Independent of enrichment pipeline, can build alongside Phase 3 if resources allow
- **Export last:** Requires complete enriched data flow working end-to-end

### Research Flags

**No additional research needed for v1.1 phases:**
- Phase 1 (CSV Infrastructure): Python csv module comprehensively documented
- Phase 2 (Backend Enrichment): Extends existing mapper pattern, no novel patterns
- Phase 3 (Enhanced Display): Standard UX patterns, WCAG compliance well-documented
- Phase 4 (Grid View): CSS Grid stable, vanilla JS patterns established
- Phase 5 (Annex Export): python-docx usage patterns already proven in v1.0

All findings verified with official documentation (Python docs, python-docx readthedocs, MDN Web Docs, W3C WAI-ARIA).

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack (No New Dependencies) | HIGH | Built-in csv module, python-docx already installed, browser-native CSS |
| Features (Enhanced Display) | HIGH | Standard UX patterns verified across multiple authoritative sources |
| Architecture (Backend Enrichment) | HIGH | Extends existing v1.0 patterns, singleton loader matches scraper/mapper design |
| Pitfalls (Integration-Specific) | HIGH | CSV encoding, BytesIO leaks, localStorage quotas verified with GitHub issues and official docs |

**Overall confidence:** HIGH

### Gaps to Address

- **guide.csv schema validation:** Exact column names and structure should be validated with actual Open Canada file during Phase 1 implementation
- **OASIS Work Context dimension mapping:** Dimension labels (Frequency, Duration, etc.) extracted from HTML need verification against live NOC site structure
- **DOCX Annex placement:** Design decision needed on whether Annex comes before or after Appendix A (compliance metadata)

These gaps are implementation details, not architectural uncertainties. Address during respective phases with actual data.

## Sources

### Primary (HIGH confidence)
- Python csv module documentation — verified built-in library patterns
- python-docx PyPI page and readthedocs — version verification and API patterns
- Open Canada NOC Dataset portal — OASIS metadata file availability confirmed
- MDN Web Docs — CSS Grid stability and browser support
- W3C WAI-ARIA Authoring Practices Guide — accessibility patterns for star ratings
- GitHub Issues (pandas, python-docx) — BOM encoding issues, BytesIO memory leaks verified

### Secondary (MEDIUM confidence)
- UX design resources (Eleken, Pencilandpaper, UX Patterns) — grid view, collapsible sections, tooltip patterns
- Medium, CodeRivers — python-docx usage patterns and optimization
- Real Python — CSV best practices

### Tertiary (LOW confidence - implementation details)
- Annex vs Appendix formatting standards — multiple conflicting sources, design decision needed
- Work Context dimension scale meanings — inferred from OASIS documentation, needs verification with guide.csv

---
*v1.1 Research completed: 2026-01-22*
*Ready for roadmap: yes*

---

# v3.0 Research Summary: Style-Enhanced Writing

**Milestone:** v3.0 Style-Enhanced Writing with Vocabulary Constraints
**Researched:** 2026-02-03
**Confidence:** MEDIUM-HIGH

## Executive Summary

JD Builder Lite v3.0 adds style-enhanced writing capabilities: learning writing patterns from ~40 example JDs and generating styled sentences that use ONLY NOC vocabulary while maintaining TBS Directive compliance. This is **vocabulary-constrained style transfer** -- a specialized problem where the LLM must improve readability without introducing new content words.

The recommended approach is **few-shot prompting with post-generation vocabulary validation**. Research confirms that constrained decoding (forcing vocabulary at token level) has limited support in cloud APIs like OpenAI and incurs significant performance penalties. Instead, generate freely using style examples in the prompt, then validate output vocabulary and regenerate on violations. The existing Flask + OpenAI stack handles this well with three new lightweight dependencies: `pdfplumber` for PDF extraction, `python-docx` (already installed) for DOCX extraction, and `pyarrow` for reading JobForge vocabulary from parquet files.

The core risk is **provenance chain breakage**: if the LLM generates words not traceable to NOC sources, compliance collapses. Three critical pitfalls require architectural attention: vocabulary escape (LLM invents words), semantic drift (meaning changes during styling), and provenance opacity (cannot trace styled output to source statements). Prevention requires vocabulary validation on every generated sentence, semantic equivalence checking, and statement-level provenance tracking designed into the architecture from the start.

## Key Findings

### Recommended Stack for v3.0

The v3.0 stack extends the existing v2.0 foundation with minimal additions. No heavy NLP libraries or local model infrastructure required.

**Core technologies for v3.0:**
- **pdfplumber 0.11.9:** PDF text extraction from example JDs -- MIT license, pure Python, handles text-heavy documents well
- **python-docx 1.2.0:** DOCX text extraction -- already installed for export, reuse for input parsing
- **pyarrow 19.x+:** Parquet file reading for NOC vocabulary from JobForge 2.0 gold data -- industry standard, no pandas overhead
- **OpenAI SDK 1.109.1:** Few-shot prompting with style examples -- already installed, handles style learning through prompting

**What NOT to add:**
- No spaCy/NLTK (LLM handles style learning directly)
- No Outlines/constrained decoding (limited OpenAI API support)
- No vector databases (40 example files fit in prompt context)
- No local model infrastructure (scope mismatch with demo app)

### Expected Features for v3.0

**Must have (table stakes):**
- Upload example JDs (PDF/DOCX) as style references
- Extract and display style characteristics from examples
- Dual-format output: original NOC statement + styled companion sentence
- Vocabulary constraint enforcement with post-generation validation
- Statement-level toggle (use styled / use original per statement)
- Regeneration on vocabulary violation (graceful degradation to original)

**Should have (competitive):**
- Style template library (pre-loaded organizational styles)
- Vocabulary coverage report (% of style patterns achievable)
- Style fidelity and content preservation scores
- Batch styling for multiple statements

**Defer (v2+):**
- Style mixing (combine attributes from multiple references)
- Vocabulary expansion suggestions (requires NOC ontology work)
- Style fine-tuning (overkill for ~40 examples)

### Architecture Approach for v3.0

The style-enhanced generation integrates cleanly with the existing Flask architecture through four new service modules: `style_analyzer.py` (parse example JDs), `vocabulary_index.py` (build term index from parquet), `style_generator.py` (constrained LLM generation), and `style_service.py` (orchestration). The existing `llm_service.py` provides OpenAI patterns to follow. The frontend extends `profile_tabs.js` with dual-display (authoritative + styled) without breaking existing data flows.

**Major components:**
1. **VocabularyIndex** -- Load parquet files, build searchable term index, validate generated text
2. **StyleAnalyzer** -- Parse PDF/DOCX, extract writing patterns via LLM, build style profiles
3. **StyleGenerator** -- Build constrained prompts, call OpenAI, validate output, retry on violation
4. **StyleService** -- Orchestrate pipeline, manage style profiles, coordinate generation

**New API endpoints:**
- `POST /api/generate-styled` -- Generate styled variants for selected statements
- `GET /api/style-profiles` -- List available style profiles
- `POST /api/vocabulary-check` -- Validate text against NOC vocabulary

### Critical Pitfalls for v3.0

1. **Vocabulary Escape (V3-01)** -- LLM generates non-NOC words breaking traceability. **Prevention:** Post-generation vocabulary validation with function word whitelist; fail-safe to original statement if validation fails after retries.

2. **Semantic Drift (V3-02)** -- Style changes subtly alter meaning (e.g., "may supervise" becomes "supervises"). **Prevention:** Semantic equivalence validation via embedding similarity; lock modal verbs (may/must/should), negations, and quantifiers.

3. **Provenance Chain Breakage (V3-03)** -- Cannot trace styled output to source statements. **Prevention:** Design provenance schema BEFORE implementing style generation; maintain statement-level mapping through transformation.

4. **PDF Parsing Corruption (V3-04)** -- OCR/extraction errors corrupt source vocabulary. **Prevention:** Continue using web scraping from OASIS HTML; if PDF required, use vision-LLM approach; validate extracted text for OCR error patterns.

5. **AI Disclosure Confusion (V3-07)** -- Users confuse "AI-generated" with "AI-styled authoritative content." **Prevention:** Differentiated disclosure: generation (synthesized content) vs. styling (reformatted authoritative content with source preserved).

## Implications for Roadmap

Based on research, suggested phase structure for v3.0:

### Phase 1: Vocabulary Foundation
**Rationale:** Independent of style analysis; provides testable foundation for constraint enforcement. Must exist before any generation.
**Delivers:** VocabularyIndex service, vocabulary validation API, term index from JobForge parquet files
**Addresses:** Table stakes vocabulary constraint enforcement
**Avoids:** PITFALL-V3-01 (Vocabulary Escape) by establishing validation infrastructure first

### Phase 2: Style Analysis Pipeline
**Rationale:** Document parsing is independent of generation. Can be developed and tested in isolation.
**Delivers:** StyleAnalyzer service, PDF/DOCX parsing, style profile extraction, `/api/style-profiles` endpoint
**Uses:** pdfplumber, python-docx from stack additions
**Implements:** Style reference upload and extraction display features

### Phase 3: Provenance Architecture
**Rationale:** Research emphasizes: "Provenance architecture must be designed BEFORE implementing style generation." Retrofit is extremely difficult.
**Delivers:** Extended data models with statement-level tracing, transformation logging schema, compliance metadata for AI-enhanced content
**Addresses:** PITFALL-V3-03 (Provenance Chain Breakage), PITFALL-V3-07 (AI Disclosure Confusion)
**Avoids:** Audit trail gaps that would violate TBS Directive 6.2.7

### Phase 4: Constrained Generation
**Rationale:** Requires both vocabulary foundation and provenance architecture. Core feature implementation.
**Delivers:** StyleGenerator service, few-shot prompting with vocabulary constraints, retry logic, semantic validation
**Uses:** OpenAI SDK (existing), VocabularyIndex (Phase 1), StyleAnalyzer (Phase 2)
**Implements:** Dual-format output, statement-level controls, graceful degradation

### Phase 5: Integration and Export
**Rationale:** Ties everything together; requires all previous phases complete.
**Delivers:** StyleService orchestrator, frontend dual-display UI, export with styled variants, differentiated AI disclosure
**Avoids:** PITFALL-V3-09 (Style Inconsistency) through unified style service

### Phase Ordering Rationale

- **Vocabulary before Generation:** Cannot validate LLM output without vocabulary index. Research confirms post-generation validation is the practical approach for cloud APIs.
- **Provenance before Generation:** Research explicitly warns against retrofit. Schema design must accommodate statement-level tracing through transformation.
- **Style Analysis parallel-able:** Document parsing and style profile extraction can proceed alongside vocabulary foundation.
- **Integration last:** Frontend dual-display and export changes require stable backend services.

### Research Flags for v3.0

Phases likely needing deeper research during planning:
- **Phase 3 (Provenance):** Complex schema design; review TBS Directive 6.2.7 requirements; may need legal consultation on AI disclosure differentiation
- **Phase 4 (Constrained Generation):** Few-shot prompting patterns for style transfer need experimentation; retry budget and semantic threshold tuning required

Phases with standard patterns (skip research-phase):
- **Phase 1 (Vocabulary):** Well-documented parquet reading with pyarrow; existing labels_loader.py patterns to follow
- **Phase 2 (Style Analysis):** Standard PDF/DOCX parsing; existing document handling patterns in codebase
- **Phase 5 (Integration):** Extends existing UI patterns; no new technology

## Confidence Assessment for v3.0

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Verified versions on PyPI; minimal additions to proven stack |
| Features | HIGH | Well-documented style transfer patterns; existing UI precedent |
| Architecture | HIGH | Analyzed existing codebase; clear integration points identified |
| Pitfalls | HIGH | Multiple academic sources; TBS Directive is authoritative |

**Overall confidence:** MEDIUM-HIGH

Stack and architecture have high confidence based on verified sources and existing codebase analysis. The MEDIUM qualifier comes from uncertainty in generation quality -- few-shot prompting effectiveness depends on vocabulary richness and style example quality, which can only be validated empirically.

### Gaps to Address for v3.0

- **Python version verification:** PyArrow 23.0.0 requires Python >= 3.10. Verify project Python version before pinning.
- **Example JD quality:** Are all 40 example JDs suitable? Some may be scanned images requiring OCR (out of scope).
- **Semantic threshold tuning:** Embedding similarity threshold (0.92 suggested) needs empirical validation with actual JD content.
- **Retry budget:** How many regeneration attempts on vocabulary violations before fallback? Research suggests 3, but needs validation.
- **Style example selection:** Simple random selection vs. match by NOC category -- needs experimentation.

## Sources for v3.0

### Primary (HIGH confidence)
- [TBS Directive on Automated Decision-Making](https://www.tbs-sct.canada.ca/pol/doc-eng.aspx?id=32592) -- Compliance requirements (6.2.3, 6.2.7, 6.3.5)
- [pdfplumber PyPI v0.11.9](https://pypi.org/project/pdfplumber/) -- January 5, 2026 release verified
- [Apache Arrow Parquet docs v23.0.0](https://arrow.apache.org/docs/python/parquet.html) -- Parquet reading patterns
- [DOMINO: Guiding LLMs The Right Way](https://arxiv.org/html/2403.06988v1) -- Constrained generation challenges
- Existing codebase analysis -- llm_service.py, labels_loader.py, api.py patterns

### Secondary (MEDIUM confidence)
- [CTG Survey: Controllable Text Generation for LLMs](https://arxiv.org/html/2408.12599v1) -- Style transfer risks semantic dissimilarity
- [AuditableLLM Framework](https://www.mdpi.com/2079-9292/15/1/56) -- Hash-chain-backed audit trails
- [Few-Shot Prompting Guide](https://www.promptingguide.ai/techniques/fewshot) -- Best practices
- [LLM Style Imitation Research](https://arxiv.org/html/2509.14543v1) -- Few examples improve style mimicking

### Tertiary (LOW confidence - needs validation)
- [CRANE: Reasoning with Constrained Generation](https://arxiv.org/pdf/2502.09061) -- Performance benchmarks may not match JD Builder use case
- OpenAI logit_bias limitations -- Community discussions confirm 300-1024 token limit, but exact behavior may vary

---
*v3.0 Research completed: 2026-02-03*
*Ready for roadmap: yes*

---

# v5.0 Research Summary: JobForge 2.0 Integration

**Milestone:** v5.0 JobForge 2.0 Integration — local-parquet-first search and profile
**Researched:** 2026-03-06
**Confidence:** HIGH

## Executive Summary

v5.0 is a data-source migration, not a feature addition. The existing JD Builder Lite already partially reads from JobForge 2.0 gold parquet files (`labels_loader.py` supplies labels, work context, exclusions, and example titles via 6 parquet files and 2 CSVs). What remains is to extend this established pattern to the two live OASIS HTTP calls that still drive every search and profile load: `scraper.search()` and `scraper.fetch_profile()`. Replacing these with parquet reads eliminates the primary pain points confirmed in UAT — 3-15 second latency, dependency on government site availability, and an opaque black-box search algorithm that misses "data engineer" entirely (UAT S1-12). The recommended approach is parquet-first with OASIS fallback: add two new services (`NOCSearchService`, `NOCProfileService`) and a data adapter (`ParquetAdapter`), wire them into `api.py` with try/except fallback to the existing scraper/parser, and leave the rest of the stack unchanged.

The migration is feasible and low-risk because the parquet data is already verified to exist and be complete for the core data types. Gold parquet files cover all 900 OASIS profiles for skills, abilities, knowledges, work activities, work context, labels, example titles, lead statements, and employment requirements. The primary verified gap is `element_main_duties.parquet`, which has data for only 3 of 900 profiles; the source CSV covering all 900 exists in the source layer and requires ETL coordination with the JobForge team. The architecture decision to wrap rather than replace the existing scraper means the OASIS fallback remains operational throughout the transition, protecting against both data gaps and regression.

The critical risk is not technical complexity — it is silent failure. The existing `labels_loader.py` pattern catches all exceptions and returns `[]`, which was correct when parquet was supplementary. When parquet becomes primary, `[]` becomes an invisible data outage rather than a graceful degradation. Every phase of this milestone must treat coverage logging and explicit fallback triggers as first-class requirements. Data exploration (Phase 21) is the mandatory first step: inventory parquet coverage, instrument the loader for visibility, fix path configuration, and determine fallback scope before writing a single line of migration code.

## Key Findings

### Recommended Stack

The existing stack requires no changes for v5.0. Python 3.12 + Flask 3.1.2 with pandas and pyarrow handles parquet reads; these dependencies are already in use via `labels_loader.py` and `vocabulary/index.py`. The addition of two new service files follows the established singleton-with-lazy-loading pattern and adds no new runtime dependencies.

**Core technologies (unchanged from current stack):**
- **Python 3.12 + Flask 3.1.2:** Runtime and web server — battle-tested for this single-user local demo scope
- **pandas + pyarrow:** Already in use for parquet reads; extend existing pattern to search and profile data
- **BeautifulSoup4 + requests:** Retained as fallback scraper — not removed in v5.0
- **OpenAI Python SDK 2.x:** Unchanged — classification pipeline not affected by parquet migration
- **fpdf2:** Unchanged — export routes call `noc_profile_service` instead of scraper, but PDF generation is unaffected

See `.planning/research/STACK.md` for full stack rationale.

### Expected Features

The parquet migration delivers two categories of improvement: table-stakes replacements (parity with current OASIS scraping but faster and more reliable) and parquet-enabled differentiators (features impossible with live scraping).

**Must have (v5.0 table stakes — P1):**
- **Data exploration inventory** — gates all other work; confirms what gold parquet actually covers
- **Search from parquet** (`dim_noc` + `element_labels` + `element_example_titles` + `element_lead_statement`) — replaces `scraper.search()` with sub-100ms pandas filtering
- **Profile statements from parquet** (`oasis_skills`, `oasis_abilities`, `oasis_knowledges`, `oasis_workactivities`, `oasis_workcontext`) — replaces `scraper.fetch_profile()` for all statement tabs
- **Main Duties / Key Activities from parquet** (`element_main_duties`) — first tab users see; contingent on ETL gap resolution
- **Lead statement and NOC hierarchy from parquet** — used in search cards and profile headers
- **Graceful OASIS fallback for missing data** — Interests, Personal Attributes, Core Competencies remain OASIS-served
- **Provenance metadata updated for parquet source** — TBS Directive compliance requires valid source attribution

**Should have (parquet-enabled differentiators — P2, include if time permits):**
- **Full-text search across all NOC attributes** — fixes UAT S1-12 "data engineer" miss; searches labels, example titles, lead statements simultaneously
- **Match rationale with NOC hierarchy level** (UAT S1-03) — "Unit Group match" vs. "Example Title match" transparency
- **Matching criteria displayed on search result cards** (UAT S1-04) — shows which attribute triggered the match
- **Deterministic NOC-to-OG pre-filtering via `bridge_noc_og`** (UAT S5-04) — 2-3x classification speed improvement
- **Sub-100ms profile load** — side effect of P1, not additional work
- **Offline operation** — side effect of P1, not additional work

**Defer (v6.0+):**
- CAF Careers taxonomy search (UAT S1-08) — multi-taxonomy out of scope until NOC parquet is proven
- Bubble matrix classification report (UAT S5-06) — visualization feature
- OG enrichment via Stylize button (UAT S2-06) — RAG architecture

**Confirmed anti-features (do not build in v5.0):**
- Removing OASIS scraping entirely — data gaps in gold (Interests, Personal Attributes CSVs; Core Competencies unresolved) make this premature
- Full-text search engine (Elasticsearch, etc.) — pandas DataFrame filtering is sufficient for ~500 NOC unit groups
- Re-implementing OASIS search algorithm — the point is to do better, not replicate its limitations

See `.planning/research/FEATURES.md` for full feature analysis and OASIS-vs-parquet comparison table.

### Architecture Approach

The target architecture adds three new service files and modifies five call sites in `api.py`. Everything else — `scraper.py`, `parser.py`, `mapper.py`, `labels_loader.py`, `vocabulary/index.py`, all frontend JS, and all response schemas — remains unchanged. The new services follow the existing `LabelsLoader` singleton pattern: load parquet DataFrames once on first call, cache in instance variables. A new `ParquetAdapter` handles the wide-to-list-of-dicts pivot because oasis_* parquet files use one-row-per-profile wide format while the existing `mapper.to_jd_elements()` contract expects `[{text, level, max, element_id}]` list format. Column name whitespace contamination (`'Writing  '`, `' Digital Literacy'`) is a verified reality that the adapter must strip.

**Major components:**
1. **`NOCSearchService`** (`src/services/noc_search_service.py`, NEW) — keyword search across `dim_noc`, `element_labels`, `element_example_titles`, `element_lead_statement`; returns `List[EnrichedSearchResult]` identical to parser output; tiered relevance scoring (Labels 95-100, class_title 90, example titles 80, lead statement 50)
2. **`NOCProfileService`** (`src/services/noc_profile_service.py`, NEW) — assembles full profile dict from parquet tables; output schema must be byte-for-byte compatible with `parser.parse_profile()` output so `mapper.to_jd_elements()` needs no changes
3. **`ParquetAdapter`** (`src/services/parquet_adapter.py`, NEW) — pivots wide parquet rows to list-of-dicts; strips whitespace from all column names before use
4. **`api.py` (5 call sites modified)** — `/api/search` (L88-89), `/api/profile` (L231-233), `/api/preview` (L372), `/api/export/pdf` (L416), `/api/export/docx` (L460) — each wrapped in try-parquet-first, except-OASIS-fallback pattern
5. **`config.py` (minor extension)** — promote `JOBFORGE_GOLD_PATH` and `JOBFORGE_SOURCE_PATH` to top-level config constants

**Key verified data facts:**
- `element_main_duties.parquet`: only 8 rows / 3 profiles — critical gap; source CSV has all 900 profiles and needs ETL
- oasis_profile_code join: `dim_noc` uses 5-digit `noc_code`; `element_*` use `XXXXX.XX` format; normalize all incoming codes before querying
- All 10 gold parquet files confirmed present and schema-verified as of 2026-03-06

See `.planning/research/ARCHITECTURE.md` for full component spec, code signatures, and data flow diagrams.

### Critical Pitfalls

1. **Silent empty results masking parquet coverage gaps (PITFALL-V5-01)** — the existing `except Exception: return []` pattern in `labels_loader.py` was correct when parquet was supplementary; when parquet is primary, it means data outages produce 200 OK responses with empty profile sections rather than triggering OASIS fallback. Fix: add `CoverageStatus` enum (`LOADED`, `EMPTY_VALID`, `NOT_FOUND`, `LOAD_ERROR`), log warnings on coverage misses, trigger fallback only on `NOT_FOUND` and `LOAD_ERROR`.

2. **Search and profile are two different migration problems (PITFALL-V5-02)** — parquet has no search index; `element_*` tables are keyed by NOC code, not searchable by job title. Search migration requires building a text index (pandas substring/TF-IDF over parquet columns), not a data-source swap. Profile migration is a data-source swap. Treating them identically produces confusing failure modes.

3. **Fallback trigger ambiguity (PITFALL-V5-03)** — `if not parquet_result:` conflates three distinct cases: (a) file missing/unloadable, (b) NOC code not in parquet, (c) genuinely empty section. Only (a) and (b) should trigger OASIS fallback; (c) returning empty is correct. Design the `CoverageStatus` enum before writing any fallback code.

4. **Hardcoded absolute path breaks on any non-developer machine (PITFALL-V5-04)** — `labels_loader.py` defaults to `/Users/victornishi/Documents/GitHub/JobForge-2.0/data/gold`. On CI, a colleague's machine, or a demo VM, this silently returns `[]` everywhere. Fix: change default to `None`, require `JOBFORGE_GOLD_PATH` in `.env.example`, add startup diagnostic: `"[LabelsLoader] Parquet: AVAILABLE (N files)"`.

5. **Stale parquet data presented as current without disclosure (PITFALL-V5-07)** — parquet files are point-in-time snapshots. For a compliance tool generating TBS-governed job descriptions, data currency matters. Add `parquet_snapshot_date` to `ProfileResponse.metadata`; display it in the UI; provide a "Refresh from OASIS" button.

See `.planning/research/PITFALLS.md` for 11 total pitfalls with a phase-to-pitfall mapping table and recovery strategies.

## Implications for Roadmap

Based on combined research, the recommended phase structure has 4 phases with clear dependency ordering.

### Phase 21: Data Exploration and Infrastructure Hardening

**Rationale:** Everything else depends on knowing what parquet actually covers. PITFALLS-V5-01, V5-03, V5-04, V5-06, V5-08, and V5-11 all require exploration-phase fixes before any migration code is safe to write. This is mandatory first — skipping it to get to "real implementation" faster is the single highest-risk decision on this milestone.

**Delivers:**
- Inventory of all gold parquet tables: row counts, column names, NOC code coverage
- Confirmed join key strategy and `normalize_oasis_code()` utility
- Fixed `JOBFORGE_GOLD_PATH` path configuration with startup diagnostics
- `CoverageStatus` enum designed (not yet wired to routes)
- Decision on `element_main_duties` gap: confirm 3-profile coverage, flag ETL need to JobForge team
- Decision on search scope: document that search requires text index building, not a data swap
- Measurement of parquet load times to inform pre-loading strategy

**Addresses features:** Data exploration inventory (P1 — gates all others)

**Avoids pitfalls:** PITFALL-V5-01 (silent empty), PITFALL-V5-04 (hardcoded path), PITFALL-V5-06 (startup latency), PITFALL-V5-08 (code format mismatch), PITFALL-V5-11 (multi-worker loading)

**Research flag:** Standard patterns — no additional research needed; pure discovery work within the existing codebase.

### Phase 22: Parquet Profile Service

**Rationale:** Profile data is the highest-value migration because (a) all required gold parquet is confirmed complete for 900 profiles, (b) it eliminates the 3-15 second OASIS HTTP round-trip on the most-used routes (`/api/profile`, `/api/preview`, `/api/export/*`), and (c) the architecture is straightforward: new service + adapter with 4 call sites to wrap. Search is deliberately deferred because it requires a separate text index design decision (PITFALL-V5-02).

**Delivers:**
- `NOCProfileService.fetch_profile()` returning parser-compatible dict from parquet
- `ParquetAdapter._pivot_wide_to_statements()` with whitespace-stripped column names
- 5 `api.py` call sites wrapped with parquet-first + OASIS fallback
- `CoverageStatus` enum implemented with correct fallback trigger logic
- `parquet_snapshot_date` added to `ProfileResponse.metadata`
- Profile loads in <500ms for parquet-covered codes (vs. 3-15s current)
- `data_source` field added to response (parquet/oasis_live/hybrid) for TBS provenance compliance
- OASIS fallback confirmed working for Interests, Personal Attributes, Core Competencies gaps

**Addresses features:** Profile statements from parquet (P1), Lead statement from parquet (P1), NOC hierarchy from parquet (P1), Provenance metadata (P1), OASIS fallback for gap fields (P1), Sub-100ms profile load (P2 — side effect), Offline operation (P2 — side effect)

**Avoids pitfalls:** PITFALL-V5-01 (coverage status enum), PITFALL-V5-03 (fallback trigger design), PITFALL-V5-05 (hybrid provenance), PITFALL-V5-07 (stale data disclosure), PITFALL-V5-09 (fallback latency logging)

**Research flag:** Standard patterns — `NOCProfileService` follows `LabelsLoader` exactly; `ParquetAdapter` pivot is standard pandas; ARCHITECTURE.md provides complete implementation spec.

### Phase 23: Parquet Search Service

**Rationale:** Search migration requires building a text index from parquet columns — architecturally distinct from the profile data swap. Deferring until after Phase 22 ensures the parquet infrastructure pattern is proven before extending it to the more complex search problem. The search text index design must be validated against UAT S1-12 ("data engineer" miss) before committing.

**Delivers:**
- `NOCSearchService.search()` returning `List[EnrichedSearchResult]` from pandas text search
- Keyword search across `element_labels`, `dim_noc`, `element_example_titles`, `element_lead_statement` with tiered relevance scoring
- Code search: exact/prefix match on `oasis_profile_code`
- `/api/search` wired with parquet-first + OASIS fallback
- Sub-100ms search response for typical queries
- Full-text coverage that fixes UAT S1-12 ("data engineer" finds "database analysts")
- Results flow through existing relevance scoring pipeline in `api.py` (lines 99-167) unchanged

**Addresses features:** Search from parquet (P1), Full-text search across attributes (P2), Offline operation for search (P2)

**Avoids pitfalls:** PITFALL-V5-02 (search treated as equivalent to profile — explicitly scoped separately), PITFALL-V5-10 (search relevance regression — parquet results flow through existing scoring pipeline)

**Research flag:** Needs research during planning — relevance tier weights (95/90/80/50) need validation against real UAT search queries (S1-12, S1-03, S1-04) before committing to the scoring design.

### Phase 24: Main Duties ETL Gap Resolution (Conditional)

**Rationale:** `element_main_duties.parquet` has data for only 3 of 900 profiles. The source CSV covers all 900. Until ETL runs, main duties are OASIS-served for 897/900 profiles, creating a silent hybrid provenance state. This is a JobForge-side ETL task but must be tracked as a JD Builder milestone dependency.

**Delivers:**
- Coordination with JobForge team to ETL `main-duties_oasis-2023_v1.0.csv` into gold parquet
- `noc_profile_service` update to read main duties from fully-populated `element_main_duties.parquet`
- Test coverage confirming main duties render for a representative sample of 10+ NOC profiles
- OASIS fallback retired for main duties once ETL is confirmed complete

**Addresses features:** Main Duties / Key Activities from parquet (P1 — completion, not initial delivery)

**Avoids pitfalls:** PITFALL-V5-05 (hybrid provenance — main duties coming from OASIS while skills come from parquet creates provenance ambiguity in compliance exports)

**Research flag:** External dependency — ETL pattern is standard but timeline depends on JobForge team; flag for coordination before scoping.

### Phase Ordering Rationale

- **Phase 21 must be first:** 6 pitfalls require exploration-phase fixes before any migration code is written. This is non-negotiable.
- **Profile before search:** Profile parquet coverage is confirmed complete (900 profiles across all required tables); search requires a text index design decision that depends on Phase 21 findings.
- **ETL gap last:** Cross-team dependency that JD Builder cannot unblock unilaterally; the app functions correctly with OASIS fallback for main duties during Phases 21-23.
- **P2 features (match rationale, NOC-to-OG bridge, job_architecture search):** Post-v5.0 enhancements that build on the parquet pattern established in Phases 22-23; do not attempt until the core P1 migration is stable.

### Research Flags

Phases needing deeper research during planning:
- **Phase 23 (Search Service):** Relevance tier weights (95/90/80/50) need validation against real UAT search queries before committing to the implementation design.
- **Phase 24 (ETL Gap):** Timeline and format of ETL output depend on JobForge team; requires coordination before this phase can be accurately scoped.

Phases with standard patterns (skip research-phase):
- **Phase 21 (Exploration):** Pure codebase discovery — no external research needed
- **Phase 22 (Profile Service):** Follows `LabelsLoader` pattern exactly; ARCHITECTURE.md provides complete implementation spec including class signatures and output dict schema

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Existing stack is confirmed working; no new dependencies; all technologies in active use today |
| Features | HIGH | Based on direct codebase analysis + JOBFORGE-DATA-REQUIREMENTS.md + UAT-FINDINGS.md; all data sources verified by inspection |
| Architecture | HIGH | All parquet files schema-verified via pandas inspection (2026-03-06); code relationships traced through direct file reads; join key strategy confirmed; component signatures designed |
| Pitfalls | HIGH | Based on direct `labels_loader.py` code analysis identifying the silent-failure pattern; pyarrow/pandas behavior from official docs |

**Overall confidence: HIGH**

### Gaps to Address

- **`bridge_noc_og` availability:** Phase 21 must verify whether `bridge_noc_og.parquet` exists in gold; UAT S5-04 (NOC-to-OG pre-filtering) is a P2 feature that depends on it. If absent, coordination with JobForge team is needed.
- **`job_architecture` table availability:** UAT S1-06 (search by Job Title/Family/Function from GC job architecture) requires this table in gold. Phase 21 must confirm its presence and schema.
- **Core Competencies data source:** No gold parquet or source CSV identified. Remains OASIS-served unless a source is found. Does not block v5.0 but should be documented as a known gap.
- **Search relevance quality:** The tiered scoring (Labels 95-100, class_title 90, example titles 80, lead statement 50) is designed from UAT patterns but not empirically tested. Phase 23 planning must include manual query testing before implementation commits.
- **`element_main_duties` ETL timeline:** Depends on JobForge team. If ETL cannot be scheduled within the v5.0 milestone window, Phase 24 may slip to v5.1.

## Sources

### Primary (HIGH confidence — direct codebase inspection)
- `src/services/labels_loader.py`, `src/services/scraper.py`, `src/services/parser.py`, `src/services/mapper.py`, `src/routes/api.py`, `src/app.py`, `src/config.py`, `src/vocabulary/index.py`, `src/models/responses.py`, `src/models/noc.py` — inspected directly (2026-03-06)
- JobForge 2.0 gold parquet files — schema and row counts verified via pandas inspection (2026-03-06): `dim_noc.parquet` (516 rows), `element_lead_statement.parquet` (900 rows), `element_main_duties.parquet` (8 rows / 3 profiles — critical gap), `oasis_skills.parquet` (900 rows, whitespace-contaminated column names confirmed), `element_labels.parquet` (900 rows), `element_example_titles.parquet` (18,666 rows)
- `.planning/JOBFORGE-DATA-REQUIREMENTS.md` — confirmed gold parquet table inventory (2026-02-06)
- `.planning/UAT-FINDINGS.md` — UAT issues S1-03, S1-04, S1-06, S1-07, S1-10, S1-12, S5-04 (2026-02-06)
- `.planning/PROJECT.md` — v5.0 milestone definition, existing architecture decisions (2026-03-06)

### Secondary (HIGH confidence — official documentation)
- PyPI: Flask 3.1.2 — verified 2026-01-21
- Pandas documentation: `read_parquet`, lazy vs. eager loading, DataFrame pivot patterns
- Flask application factory pattern and worker memory isolation — official Flask docs
- Python logging best practices — standard library

### Tertiary (MEDIUM confidence — inference from patterns)
- Search relevance tier weights (95/90/80/50) — designed from UAT patterns; not empirically validated
- `bridge_noc_og` and `job_architecture` availability in gold — inferred from JOBFORGE-DATA-REQUIREMENTS; needs Phase 21 verification

---
*v5.0 Research completed: 2026-03-06*
*Ready for roadmap: yes*
