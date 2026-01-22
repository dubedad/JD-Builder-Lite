# Roadmap: JD Builder Lite v1.1

**Milestone:** v1.1 Enhanced Data Display + Export
**Created:** 2026-01-22
**Phases:** 3 (starting from Phase 5)

## Overview

| Phase | Name | Goal | Requirements |
|-------|------|------|--------------|
| 5 | Data Enrichment Pipeline | Backend provides enriched statements with descriptions, proficiency levels, and reference attributes | DISP-04, DISP-05, DISP-06, DISP-07, DISP-08, DATA-03, DATA-04, DATA-05, DISP-09, DISP-10, DISP-11 |
| 6 | Enhanced UI Display | Users see enriched data with stars, descriptions, scale meanings, and grid view options | SRCH-04, SRCH-05 |
| 7 | Export Extensions | Users can export to DOCX and view Annex section with reference attributes | OUT-06, OUT-07, OUT-08 |

## Phase Details

### Phase 5: Data Enrichment Pipeline

**Goal:** Backend loads guide.csv at startup and enriches all profile responses with category definitions, statement descriptions, proficiency levels with scale meanings, correct Work Context filtering, and reference NOC attributes.

**Requirements:**
- DISP-04: Each JD Element section shows category definition at top (from guide.csv)
- DISP-05: Each statement includes OASIS label description (from guide.csv lookup)
- DISP-06: Statements display proficiency/complexity level as stars (1-5)
- DISP-07: Star ratings include scale meaning label (e.g., "5 - Highest Level" for Skills)
- DISP-08: Work Context statements show dimension type (Frequency, Duration, Degree of responsibility, etc.)
- DATA-03: Responsibilities header populated with Work Context items containing "responsib" or "decision"
- DATA-04: Effort header captures all Work Context items containing "effort"
- DATA-05: Work Context scraping extracts complete data from OASIS
- DISP-09: Profile page shows NOC code prominently under title
- DISP-10: Profile page displays NOC hierarchical breakdown (TEER, broad category, major group)
- DISP-11: Profile page displays reference NOC attributes (job requirements, career mobility, example titles, interests, personal attributes)

**Success Criteria:**
1. User searches for a profile and sees NOC code displayed under the title on profile page
2. User views profile and sees NOC hierarchy breakdown (TEER, broad category, major group) prominently displayed
3. User views any statement and sees its proficiency level as star rating with scale meaning label
4. User views any statement and sees descriptive text explaining what the OASIS label means (from guide.csv)
5. User views JD Element sections and sees category definition at the top of each section
6. User views Work Context tab and sees dimension type labels (Frequency, Duration, etc.) on each statement
7. User views Responsibilities section and sees Work Context items filtered correctly (containing "responsib" or "decision")
8. User views Effort section and sees Work Context items filtered correctly (containing "effort")
9. User views profile and sees reference attributes section with job requirements, career mobility, example titles, interests, and personal attributes

**Notes:**
- CRITICAL: Use encoding='utf-8-sig' when loading guide.csv to handle Windows BOM (prevents column name lookup failures)
- CRITICAL: Load CSV once at app startup using singleton pattern (avoid repeated file I/O)
- CRITICAL: Enrich on backend at /api/profile response time (avoid O(n*m) frontend lookups)
- Use Map-based indexing for CSV lookups to ensure O(1) performance
- Validate CSV column names after load to catch encoding issues early
- Work Context filtering applies pattern matching on statement text to route statements to correct JD Element headers
- Reference attributes extracted from Overview tab (example titles, interests, etc.) and included in profile response

### Phase 6: Enhanced UI Display

**Goal:** Frontend renders enriched data with visual enhancements including star ratings, descriptions, scale meanings, NOC codes in search results, and grid view toggle.

**Requirements:**
- SRCH-04: Search results display grid view toggle (card vs table views)
- SRCH-05: Search results show NOC code next to profile title (e.g., "Air pilots (72600.01)")

**Success Criteria:**
1. User performs search and sees NOC code displayed next to each profile title in results (e.g., "Air pilots (72600.01)")
2. User performs search and sees toggle button to switch between card view and table view
3. User clicks grid toggle and sees results display as table with columns (title, NOC code, broad category, lead statement)
4. User switches between card and table views and sees preference persisted on page reload
5. User views profile statements and sees proficiency stars rendered visually (1-5 filled stars)
6. User views statements and sees scale meaning labels displayed clearly (e.g., "5 - Highest Level")
7. User views Work Context statements and sees dimension type badges displayed (Frequency, Duration, etc.)
8. Screen reader users hear correct ARIA labels for star ratings without repetition (WCAG 2.1 Level AA compliance)

**Notes:**
- Use Unicode star characters (U+2605 filled, U+2606 empty) with CSS for zero-dependency rendering
- CRITICAL: Implement aria-hidden on decorative stars, single aria-label on container for accessibility
- Grid view uses CSS Grid for responsive table layout (browser-native, no framework)
- Persist grid preference in localStorage with quota check to avoid QuotaExceededError
- Test star rating accessibility with NVDA/VoiceOver to ensure compliance
- Grid view displays first 50 results without virtualization (acceptable performance for search result set)

### Phase 7: Export Extensions

**Goal:** Users can export job descriptions to Word/DOCX format with the same compliance structure as PDF, and both PDF and DOCX exports include Annex section with unused NOC reference attributes.

**Requirements:**
- OUT-06: Manager can export final JD to Word/DOCX format
- OUT-07: PDF export includes Annex section with unused NOC reference attributes
- OUT-08: DOCX export includes Annex section with unused NOC reference attributes

**Success Criteria:**
1. User completes job description and sees "Export to DOCX" button alongside "Export to PDF"
2. User clicks "Export to DOCX" and receives Word document with same section structure as PDF (General Overview, JD Elements, Compliance Metadata, Appendix A)
3. User exports to PDF and sees Annex section at end of document listing unused NOC reference attributes (example titles, interests, career mobility, personal attributes)
4. User exports to DOCX and sees Annex section at end of document listing unused NOC reference attributes (matching PDF structure)
5. User views Annex section in both formats and sees reference attributes formatted consistently with appropriate headings and attribution

**Notes:**
- python-docx 1.2.0 already in requirements.txt (no new dependency)
- CRITICAL: Use context manager pattern (with BytesIO() as buffer) to prevent memory leaks in DOCX generation
- Annex section placed after Appendix A (Compliance Metadata) in both formats
- Annex content includes: Example titles, Interests, Career mobility paths, Job requirements, Personal attributes
- Each Annex item includes source attribution (NOC code, retrieval timestamp)
- Test repeated exports to verify no BytesIO accumulation in memory
- DOCX and PDF Annex structure must match exactly (avoid divergence)

## Traceability

| Requirement | Phase | Success Criterion |
|-------------|-------|-------------------|
| DISP-04 | 5 | SC-5.5 |
| DISP-05 | 5 | SC-5.4 |
| DISP-06 | 5 | SC-5.3 |
| DISP-07 | 5 | SC-5.3 |
| DISP-08 | 5 | SC-5.6 |
| DATA-03 | 5 | SC-5.7 |
| DATA-04 | 5 | SC-5.8 |
| DATA-05 | 5 | SC-5.7, SC-5.8 |
| DISP-09 | 5 | SC-5.1 |
| DISP-10 | 5 | SC-5.2 |
| DISP-11 | 5 | SC-5.9 |
| SRCH-04 | 6 | SC-6.2, SC-6.3, SC-6.4 |
| SRCH-05 | 6 | SC-6.1 |
| OUT-06 | 7 | SC-7.1, SC-7.2 |
| OUT-07 | 7 | SC-7.3 |
| OUT-08 | 7 | SC-7.4, SC-7.5 |

**Coverage:** 16/16 requirements mapped

## Progress

| Phase | Status | Completed |
|-------|--------|-----------|
| 5 - Data Enrichment Pipeline | Pending | - |
| 6 - Enhanced UI Display | Pending | - |
| 7 - Export Extensions | Pending | - |

---
*Roadmap created: 2026-01-22*
*Continues from v1.0 (Phase 4 complete)*
