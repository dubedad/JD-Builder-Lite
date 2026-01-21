---
phase: 01-backend-scraping
plan: 02
subsystem: backend
tags: [beautifulsoup4, lxml, html-parsing, data-transformation, provenance]

# Dependency graph
requires:
  - phase: 01-01
    provides: data models, scraper service, config constants
provides:
  - CSS selector abstraction with primary/fallback patterns
  - HTML parser extracting structured data from OASIS pages
  - NOC-to-JD mapper organizing data by job description elements
  - Full provenance tracking on every statement
affects: [01-03, api-routes, frontend-integration]

# Tech tracking
tech-stack:
  added: []
  patterns: [selector-abstraction, primary-fallback-pattern, keyword-filtering, singleton-services]

key-files:
  created: [src/utils/selectors.py, src/services/parser.py, src/services/mapper.py]
  modified: []

key-decisions:
  - "CSS selector abstraction prevents brittle selector spread across codebase"
  - "Primary/fallback selector pattern enables resilience to OASIS HTML changes"
  - "Keyword filtering divides work_context into Effort and Responsibility elements"
  - "Module-level singletons (parser, mapper) for consistent import pattern"

patterns-established:
  - "Selector abstraction layer isolates CSS selectors in single location"
  - "BeautifulSoup with lxml parser for fast HTML processing"
  - "Every NOCStatement includes source_attribute and source_url for complete provenance"
  - "SourceMetadata on all responses includes noc_code, profile_url, scraped_at, version"

# Metrics
duration: 5min
completed: 2026-01-21
---

# Phase 1 Plan 2: HTML Parser and JD Mapper Summary

**BeautifulSoup parser extracting NOC data from OASIS HTML and mapper organizing it by JD elements with full provenance tracking**

## Performance

- **Duration:** 5 minutes
- **Started:** 2026-01-21T22:50:22Z
- **Completed:** 2026-01-21T17:55:15Z
- **Tasks:** 3
- **Files modified:** 3

## Accomplishments
- Created CSS selector abstraction layer with primary/fallback patterns for all OASIS page elements
- Built HTML parser (OASISParser) that extracts search results and profile sections using BeautifulSoup
- Implemented JD mapper (JDMapper) that transforms NOC data into JD element structure (Key Activities, Skills, Effort, Responsibility, Working Conditions)
- Established keyword-based filtering to organize work_context items into appropriate JD elements
- Ensured every statement includes complete provenance (source attribute, source URL)

## Task Commits

Each task was committed atomically:

1. **Task 1: CSS selector abstraction layer** - `74b1bd3` (feat)
2. **Task 2: OASIS HTML parser** - `e8d8bd4` (feat)
3. **Task 3: NOC to JD element mapper** - `f61c25a` (feat)

## Files Created/Modified
- `src/utils/selectors.py` - SELECTORS dict with primary/fallback CSS selectors, helper functions (get_selector, get_fallback, get_all_selectors)
- `src/services/parser.py` - OASISParser class with parse_search_results() and parse_profile() methods, NOC code regex pattern
- `src/services/mapper.py` - JDMapper class with to_jd_elements() and element-specific mapping methods, keyword filtering for Effort/Responsibility

## Decisions Made

**CSS selector abstraction:**
- Created centralized SELECTORS dict to prevent selector spread across codebase
- Primary/fallback pattern enables resilience when OASIS changes HTML structure
- Selectors are educated guesses based on common patterns - will be validated during live testing in Plan 03

**HTML parsing approach:**
- BeautifulSoup with lxml parser for fast, reliable HTML processing
- Regex-based NOC code extraction (matches "21232" or "21232.00" format)
- Try primary selector first, fallback on failure - graceful degradation

**JD element mapping strategy:**
- Combine main_duties + work_activities → Key Activities
- Combine skills + abilities + knowledge → Skills
- Filter work_context by EFFORT_KEYWORDS → Effort element
- Filter work_context by RESPONSIBILITY_KEYWORDS → Responsibility element
- All work_context → Working Conditions element

**Provenance tracking:**
- Every NOCStatement includes source_attribute (e.g., "Main Duties") and source_url
- SourceMetadata on all responses includes noc_code, profile_url, scraped_at timestamp, version
- Enables complete audit trail from JD content back to source NOC profile

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None - all imports, instantiation tests, and end-to-end verification passed on first attempt.

## User Setup Required

None - builds on existing dependencies from Plan 01-01 (BeautifulSoup4 and lxml already installed).

## Next Phase Readiness

**Ready for Plan 01-03 (Live testing & Flask API):**
- CSS selectors defined (ready for validation against real OASIS HTML)
- Parser can extract structured data from HTML
- Mapper can transform NOC data into JD element structure
- All provenance tracking in place

**Blockers:**
- None

**Concerns:**
- CSS selectors are educated guesses - need validation against live OASIS site in Plan 03
- Keyword filtering for Effort/Responsibility may need refinement based on actual work_context data
- Some work_context items may match both effort and responsibility keywords (acceptable - items can appear in multiple elements)

---
*Phase: 01-backend-scraping*
*Completed: 2026-01-21*
