---
phase: 14-data-layer
plan: 02
subsystem: scraping
tags: [http-client, rate-limiting, html-parsing, beautifulsoup, content-hashing]

# Dependency graph
requires: [14-01]
provides:
  - Rate-limited HTTP client for TBS government pages
  - Content-addressed HTML archiving with SHA-256
  - BeautifulSoup parsers for occupational groups table and definitions
  - Validation utilities for parsed data
affects: [14-03, 15-matching-engine]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "HTTPAdapter with Retry for exponential backoff"
    - "Content-addressed archiving with hash-based filenames"
    - "Lazy imports in __init__.py for incremental development"
    - "Section-aware HTML parsing for nested TBS structure"

key-files:
  created:
    - src/scrapers/__init__.py
    - src/scrapers/http_client.py
    - src/scrapers/html_archiver.py
    - src/scrapers/tbs_parser.py
  modified: []

key-decisions:
  - "Rate limit: 1 req/sec via time.sleep in client, not HTTPAdapter"
  - "Retry on 429, 500, 502, 503, 504 with backoff_factor=2 (2, 4, 8 sec)"
  - "Archive filenames: {url_slug}-{timestamp}-{hash[:8]}.html"
  - "Parse TBS sections inside <section> elements for inclusions/exclusions"

patterns-established:
  - "TBSHttpClient class with fetch() returning (content, metadata) tuple"
  - "archive_html() returns provenance dict with hash, path, size"
  - "parse_definition_page() returns list of group dicts with inclusions/exclusions"

# Metrics
duration: 10min
completed: 2026-02-04
---

# Phase 14 Plan 02: TBS Scraper Infrastructure Summary

**HTTP client with 1 req/sec rate limiting and retry logic, content-addressed HTML archiver with SHA-256 hashing, and BeautifulSoup parsers extracting 217 groups with 452 inclusions and 165 exclusions from TBS pages**

## Performance

- **Duration:** 10 min
- **Started:** 2026-02-04T05:15:23Z
- **Completed:** 2026-02-04T05:25:41Z
- **Tasks:** 3/3
- **Files created:** 4

## Accomplishments

- Created rate-limited HTTP client respecting 1 req/sec for polite government scraping
- Implemented automatic retry with exponential backoff on 429/5xx errors
- Built content-addressed HTML archiver enabling change detection and audit trail
- Developed BeautifulSoup parsers extracting structured data from TBS HTML pages
- Achieved 217 groups from concordance table, 214 definitions with 452 inclusions and 165 exclusions

## Task Commits

Each task was committed atomically:

1. **Task 1: Create rate-limited HTTP client with retry logic** - `f71b743` (feat)
2. **Task 2: Create HTML archiver with content hashing** - `8956518` (feat)
3. **Task 3: Create TBS HTML parsers for occupational group data** - `47bd463` (feat)

## Files Created

| File | Purpose | Exports |
|------|---------|---------|
| `src/scrapers/__init__.py` | Package with lazy imports | All scraper components |
| `src/scrapers/http_client.py` | Rate-limited HTTP client | `TBSHttpClient`, `create_scraping_session` |
| `src/scrapers/html_archiver.py` | Content-addressed archiving | `archive_html`, `calculate_content_hash`, `get_archived_content` |
| `src/scrapers/tbs_parser.py` | BeautifulSoup parsers | `parse_occupational_groups_table`, `parse_definition_page`, `parse_allocation_guide`, `validate_parsed_group` |

## Key Implementation Details

### HTTP Client

- Uses `requests.Session` with `HTTPAdapter` and `urllib3.Retry`
- Retry strategy: 3 attempts, backoff_factor=2 (waits 2, 4, 8 seconds)
- Status codes triggering retry: 429, 500, 502, 503, 504
- Rate limiting enforced via `time.sleep()` between requests
- Returns `(bytes, metadata)` tuple for provenance tracking

### HTML Archiver

- SHA-256 content hashing via `hashlib.sha256`
- Filename format: `{url_slug}-{timestamp}-{hash[:8]}.html`
- Windows-compatible timestamps (colons replaced with dashes)
- Archive directory: `data/html_archive/`

### TBS Parsers

- Uses BeautifulSoup with lxml parser for speed
- Handles TBS `<section>` structure containing headings and lists
- Extracts from concordance table: group_code, definition_url, job_eval_url, qualification_url, rates_of_pay URLs
- Extracts from definitions page: definition text, inclusions, exclusions with order
- Graceful error handling: logs warnings, continues parsing remaining groups

## Decisions Made

| Decision | Rationale |
|----------|-----------|
| Rate limit in client, not adapter | HTTPAdapter doesn't support rate limiting, only retry |
| Return metadata with content | Enables provenance tracking without re-fetching |
| Lazy imports in __init__.py | Allows incremental development without import errors |
| Parse section elements | TBS HTML nests inclusions/exclusions inside sections |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Fixed import error from missing modules**

- **Found during:** Task 1 verification
- **Issue:** `__init__.py` imported all modules eagerly, but only http_client existed
- **Fix:** Changed to lazy `__getattr__` import pattern
- **Files modified:** `src/scrapers/__init__.py`
- **Commit:** f71b743

**2. [Rule 1 - Bug] Fixed inclusion extraction for section-wrapped content**

- **Found during:** Task 3 verification
- **Issue:** Parser found 0 inclusions because TBS HTML nests lists inside `<section>` elements
- **Fix:** Updated `_extract_list_items` to search inside section elements
- **Files modified:** `src/scrapers/tbs_parser.py`
- **Commit:** 47bd463

## Verification Results

| Criterion | Expected | Actual | Status |
|-----------|----------|--------|--------|
| Two requests >= 1s | >= 1.0s | 7.06s | PASS |
| Hash deterministic | Same hash | Same hash | PASS |
| Archive in data/html_archive/ | True | True | PASS |
| Table returns 30+ groups | >= 30 | 217 | PASS |
| Definitions have inc/exc | True | True | PASS |
| Validation catches empty def | True | True | PASS |

## Next Phase Readiness

- HTTP client ready for scraper orchestration in 14-03
- Parsers ready to extract all TBS occupational group data
- Archive system ready for provenance tracking
- Repository from 14-01 ready to receive parsed data

---
*Phase: 14-data-layer*
*Completed: 2026-02-04*
