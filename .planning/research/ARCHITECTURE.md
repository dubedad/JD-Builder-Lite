# Architecture: JobForge 2.0 Parquet Integration

**Domain:** Flask app migrating primary NOC data source from live HTML scraping to local parquet
**Researched:** 2026-03-06
**Confidence:** HIGH (based on direct codebase inspection and JobForge parquet schema verification)

---

## Current Architecture (What Exists Today)

```
CURRENT SYSTEM (v4.x — OASIS scraping as primary)

  ROUTES                 SERVICES                   DATA SOURCES
  ======                 ========                   ============

  /api/search  --------> scraper.search()  -------> OASIS HTTP (live)
      |                  OASISScraper.search()           noc.esdc.gc.ca
      |                       |
      |                  parser.parse_search_results_enhanced()
      |                  OASISParser (BeautifulSoup HTML)
      |                       |
      v                       v
  SearchResponse         EnrichedSearchResult[]
  (query, results[])     (noc_code, title, lead_statement,
                          teer_description, relevance_score)


  /api/profile --------> scraper.fetch_profile()  -> OASIS HTTP (live)
  /api/preview              OASISScraper                noc.esdc.gc.ca
  /api/export/pdf                |
  /api/export/docx         parser.parse_profile()
                           OASISParser (BeautifulSoup HTML)
                                |
                           mapper.to_jd_elements()
                           JDMapper
                                |
                                +<---- labels_loader  (parquet GOLD: element_*,
                                |      LabelsLoader     oasis_workcontext)
                                |
                                v
                           ProfileResponse
                           (noc_code, title, key_activities,
                            skills, effort, responsibility,
                            working_conditions, other_job_info)


  STARTUP (app.py)
  VocabularyIndex  -----> parquet BRONZE:
  (startup load)           oasis_abilities.parquet
                           oasis_skills.parquet
                           oasis_knowledges.parquet
                           oasis_workactivities.parquet
```

**Key observation:** The scraper (`src/services/scraper.py`) is a thin HTTP client, not a service facade. It has no fallback logic, no caching, and no parquet awareness. The parser and mapper are where the real transformation work happens.

---

## Parquet Data Inventory (Verified Against JobForge 2.0)

This inventory is factual, not hypothetical. Every file listed was verified to exist and its schema was inspected.

### Gold Layer — already used by JD Builder

| File | Rows | Key Columns | Current Consumer |
|------|------|-------------|-----------------|
| `element_labels.parquet` | 900 | unit_group_id, oasis_profile_code, Label | `labels_loader.get_labels()` |
| `element_example_titles.parquet` | 18,666 | unit_group_id, oasis_profile_code, Job title text | `labels_loader.get_example_titles()` |
| `element_exclusions.parquet` | ~900 | unit_group_id, oasis_profile_code, Excluded code, Job title | `labels_loader.get_exclusions()` |
| `element_employment_requirements.parquet` | ~900 | unit_group_id, oasis_profile_code, Employment requirement | `labels_loader.get_employment_requirements()` |
| `element_workplaces_employers.parquet` | ~900 | unit_group_id, oasis_profile_code, Workplace/employer name | `labels_loader.get_workplaces()` |
| `oasis_workcontext.parquet` | 900 | oasis_code, oasis_label, [70 context columns] | `labels_loader.get_work_context_filtered()` |
| `oasis_abilities.parquet` | 900 | unit_group_id, oasis_code, oasis_label, [53 ability columns] | `VocabularyIndex` (column names only) |
| `oasis_skills.parquet` | 900 | unit_group_id, oasis_code, oasis_label, [37 skill columns] | `VocabularyIndex` (column names only) |
| `oasis_knowledges.parquet` | 900 | unit_group_id, oasis_code, oasis_label, [42 knowledge columns] | `VocabularyIndex` (column names only) |
| `oasis_workactivities.parquet` | 900 | unit_group_id, oasis_code, oasis_label, [38 activity columns] | `VocabularyIndex` (column names only) |

### Gold Layer — NOT yet used by JD Builder (needed for v5.0)

| File | Rows | Key Columns | Intended Use |
|------|------|-------------|-------------|
| `dim_noc.parquet` | 516 | unit_group_id, noc_code, class_title, class_definition | Search source (unit group name + definition) |
| `element_lead_statement.parquet` | 900 | unit_group_id, oasis_profile_code, Lead statement | Search result cards |
| `element_main_duties.parquet` | 8 | unit_group_id, oasis_profile_code, Main Duty | **SPARSE — only 3 profiles** |

### Source Layer — complete but NOT yet ETL'd to gold parquet

| File | Rows | Key Columns | Status |
|------|------|-------------|--------|
| `main-duties_oasis-2023_v1.0.csv` | 4,991 | OaSIS profile code, Main duties | Covers all 900 profiles — needs ETL |

**Critical finding:** `element_main_duties.parquet` in gold only has data for 3 profiles. The source CSV has all 900. Phase 21 data exploration will confirm this gap. Main duties cannot be fully served from parquet until ETL runs against the source CSV.

### Key Code Relationships (oasis_profile_code vs noc_code)

```
OASIS Data Model:

  noc_code (5-digit)         oasis_profile_code (5-digit.2-digit)
  e.g. "21211"     ---1:N--> e.g. "21211.00", "21211.01", ...

  dim_noc: 516 unit groups (5-digit noc_codes)
  element_*: 900 OASIS profiles (oasis_profile_codes like "21211.00")

  JOIN KEY:
    unit_group_id in element_* == noc_code digits in dim_noc
    e.g. unit_group_id "21211" matches noc_code "21211"

  When frontend sends code "21211" or "21211.00":
    - Strip decimal suffix to get unit_group_id
    - Query element tables by oasis_profile_code = code + ".00"
      (or by unit_group_id for tables that aggregate across sub-profiles)
```

---

## Target Architecture (v5.0 — Parquet Primary, OASIS Fallback)

```
TARGET SYSTEM (v5.0 — parquet as primary)

  ROUTES                 SERVICES                   DATA SOURCES
  ======                 ========                   ============

  /api/search  --------> noc_search_service  ------> parquet GOLD:
      |                  (NEW)                         dim_noc
      |                       |                        element_labels
      |                       |                        element_example_titles
      |                       |                        element_lead_statement
      |                  [parquet miss]
      |                       |
      |                  scraper.search()  ---------> OASIS HTTP (fallback)
      |                  (EXISTING, unchanged)
      |
      v
  SearchResponse (schema UNCHANGED)


  /api/profile --------> noc_profile_service  -----> parquet GOLD:
  /api/preview           (NEW)                         element_lead_statement
  /api/export/pdf             |                        element_main_duties
  /api/export/docx            |                        oasis_skills
                              |                        oasis_abilities
                              |                        oasis_knowledges
                              |                        oasis_workactivities
                              |                        oasis_workcontext
                              |                        element_*
                              |
                         noc_profile_adapter  ------> mapper.to_jd_elements()
                         (NEW: converts parquet      (EXISTING, unchanged)
                          dict to same format as
                          parser.parse_profile())
                              |
                         [parquet miss]
                              |
                         scraper.fetch_profile()  --> OASIS HTTP (fallback)
                         parser.parse_profile()      (EXISTING, unchanged)
                              |
                              v
                         ProfileResponse (schema UNCHANGED)


  STARTUP (app.py)       UNCHANGED
  VocabularyIndex  -----> parquet BRONZE (already works)
```

---

## New Components

### 1. `src/services/noc_search_service.py` (NEW)

**Purpose:** Search NOC profiles using local parquet files instead of OASIS HTTP.

**What it replaces:** `scraper.search()` + `parser.parse_search_results_enhanced()` in the `/api/search` route.

**Input:** query string, search_type (Keyword | Code)

**Output:** `List[EnrichedSearchResult]` — same model the route uses today

**Search logic:**
- Keyword search: query against `element_labels` (Label), `element_example_titles` (Job title text), `element_lead_statement` (Lead statement), `dim_noc` (class_title)
- Code search: exact or prefix match on `oasis_profile_code` in `element_labels`
- Return top N ranked results with `noc_code`, `title`, `lead_statement`

**Data loading pattern:** Follow `LabelsLoader` — load DataFrames once at first call, cache in instance.

```python
class NOCSearchService:
    """Search NOC profiles from local parquet files."""

    def __init__(self):
        self._labels_df: Optional[pd.DataFrame] = None
        self._titles_df: Optional[pd.DataFrame] = None
        self._lead_df: Optional[pd.DataFrame] = None
        self._noc_df: Optional[pd.DataFrame] = None
        self._loaded = False

    def search(self, query: str, search_type: str = "Keyword") -> List[EnrichedSearchResult]:
        """Return EnrichedSearchResult list matching query."""

    def _build_result(self, row: pd.Series) -> EnrichedSearchResult:
        """Map parquet row to EnrichedSearchResult (same schema as parser output)."""

# Module singleton
noc_search_service = NOCSearchService()
```

**Match logic:** For Keyword search, search across multiple fields in priority order:
1. Exact match in `element_labels.Label` -> relevance_score 95-100
2. Exact match in `dim_noc.class_title` -> relevance_score 90
3. Match in `element_example_titles.Job title text` -> relevance_score 80
4. Match in `element_lead_statement.Lead statement` -> relevance_score 50

The existing relevance scoring logic in `api.py` (lines 99-167) runs AFTER the search results are returned, so parquet search results will naturally flow through it unchanged.

### 2. `src/services/noc_profile_service.py` (NEW)

**Purpose:** Read a full NOC profile from local parquet files.

**What it replaces:** `scraper.fetch_profile()` + `parser.parse_profile()` in the `/api/profile`, `/api/preview`, `/api/export/pdf`, `/api/export/docx` routes.

**Input:** `noc_code` string (e.g., "21211" or "21211.00")

**Output:** `Dict[str, Any]` — same dict structure that `parser.parse_profile()` produces today

```python
# Expected output shape (must match parser.parse_profile() contract):
{
    'noc_code': '21211.00',
    'title': str,
    'noc_hierarchy': NOCHierarchy,
    'main_duties': List[str],            # from element_main_duties or fallback
    'work_activities': List[dict],       # [{text, level, max, element_id}]
    'skills': List[dict],                # [{text, level, max, element_id}]
    'abilities': List[dict],             # [{text, level, max, element_id}]
    'knowledge': List[dict],             # [{text, level, max, element_id}]
    'work_context': List[dict],          # [{text, level, max, dimension_type}]
    'employment_requirements': List[str],
    'reference_attributes': ReferenceAttributes,
    'interests': List[str],
    'personal_attributes': List[str],
    'career_mobility': Dict[str, List[str]],
}
```

**Data assembly:**
- `noc_code` + `title`: from `dim_noc` or `element_labels` (oasis_label column)
- `noc_hierarchy`: derive from code structure (same logic as `parser.extract_noc_hierarchy()`)
- `main_duties`: from `element_main_duties.parquet` (WARNING: sparse in gold — Phase 21 validates)
- `work_activities`, `skills`, `abilities`, `knowledge`: pivot from wide-format oasis_* parquets
  - Wide format: each row = one profile, each column = one attribute with numeric score
  - Must pivot to `[{text: col_name, level: score, max: 5, element_id: None}]`
- `work_context`: pivot from `oasis_workcontext.parquet` wide format
- `employment_requirements`: from `element_employment_requirements.parquet`
- `reference_attributes.example_titles`: from `element_example_titles.parquet`

```python
class NOCProfileService:
    """Read NOC profiles from local parquet files."""

    def fetch_profile(self, code: str) -> Dict[str, Any]:
        """Return parse_profile()-compatible dict from parquet."""

    def _pivot_wide_to_statements(
        self,
        df: pd.DataFrame,
        oasis_code: str,
        skip_cols: set
    ) -> List[dict]:
        """Pivot wide parquet row into [{text, level, max, element_id}] format."""

# Module singleton
noc_profile_service = NOCProfileService()
```

### 3. `src/services/parquet_adapter.py` (NEW)

**Purpose:** Normalize inconsistencies between parquet data format and the dict schema `parser.parse_profile()` produces. This is a pure transformation layer — no data loading.

**Why needed:** The parquet files use wide format (one row per profile, one column per attribute). The parser output uses a list-of-dicts format. The adapter handles this pivoting and any column name cleaning (some columns have trailing whitespace: `'Writing  '`, `' Digital Literacy'`).

**Key transformation:**
```python
# Wide parquet row:
# oasis_code | Reading Comprehension | Writing   | Numeracy
# 21211.00   |         4             |     3     |    2

# Adapter output (list-of-dicts for mapper.py):
[
    {"text": "Reading Comprehension", "level": 4, "max": 5, "element_id": None},
    {"text": "Writing", "level": 3, "max": 5, "element_id": None},
    {"text": "Numeracy", "level": 2, "max": 5, "element_id": None},
]
```

Column name cleaning is essential: `'Writing  '` must become `'Writing'`, `' Digital Literacy'` must become `'Digital Literacy'`. The column names in the parquet files have inconsistent whitespace.

---

## Modified Components (Surgical Changes Only)

### `src/routes/api.py` — THREE call sites to update

The route has three patterns of OASIS calls to modify:

**Pattern 1: `/api/search` route (lines 88-89)**
```python
# BEFORE:
html = scraper.search(query, search_type=search_type)
results = parser.parse_search_results_enhanced(html)

# AFTER (try-parquet-first):
try:
    results = noc_search_service.search(query, search_type=search_type)
    if not results:  # empty parquet result -> fallback
        raise ParquetMiss("no results")
except Exception:
    html = scraper.search(query, search_type=search_type)
    results = parser.parse_search_results_enhanced(html)
```

**Pattern 2: `/api/profile` route (lines 231-233)**
```python
# BEFORE:
html = scraper.fetch_profile(code)
noc_data = parser.parse_profile(html, code)
jd_data = mapper.to_jd_elements(noc_data)

# AFTER:
try:
    noc_data = noc_profile_service.fetch_profile(code)
except Exception:
    html = scraper.fetch_profile(code)
    noc_data = parser.parse_profile(html, code)
jd_data = mapper.to_jd_elements(noc_data)
```

**Pattern 3: Export routes (3 places — `/api/preview`, `/api/export/pdf`, `/api/export/docx`)**

Each export route fetches a profile for the Annex (lines ~372-374, ~416-418, ~460-462):
```python
# BEFORE (in each export route):
html = scraper.fetch_profile(export_request.noc_code)
raw_noc_data = parser.parse_profile(html, export_request.noc_code)

# AFTER:
try:
    raw_noc_data = noc_profile_service.fetch_profile(export_request.noc_code)
except Exception:
    html = scraper.fetch_profile(export_request.noc_code)
    raw_noc_data = parser.parse_profile(html, export_request.noc_code)
```

### `src/services/scraper.py` — NO changes

The existing `OASISScraper` and module-level `scraper` singleton stay exactly as they are. Fallback calls go directly to this module. It already has proper error handling for network failures.

### `src/services/mapper.py` — NO changes

`mapper.to_jd_elements(noc_data)` accepts the same dict regardless of whether `noc_data` came from the parser or from `noc_profile_service`. The adapter ensures schema compatibility.

### `src/services/parser.py` — NO changes

Parser stays as fallback. It is not deprecated.

### `src/config.py` — MINOR: add gold/source paths

`JOBFORGE_GOLD_PATH` and `JOBFORGE_SOURCE_PATH` are currently only in `LabelsLoader` class attributes, not in `config.py`. The new services need them. Add:
```python
JOBFORGE_GOLD_PATH = os.getenv(
    "JOBFORGE_GOLD_PATH",
    "/Users/victornishi/Documents/GitHub/JobForge-2.0/data/gold"
)
JOBFORGE_SOURCE_PATH = os.getenv(
    "JOBFORGE_SOURCE_PATH",
    "/Users/victornishi/Documents/GitHub/JobForge-2.0/data/source"
)
```

---

## Fallback Pattern (Concrete)

The fallback pattern is try-parquet-first with silent exception catch and OASIS retry.

```python
# Standard fallback pattern for all NOC data fetches

def _fetch_with_fallback(code: str) -> dict:
    """Parquet-first, OASIS fallback."""
    try:
        result = noc_profile_service.fetch_profile(code)
        if result:
            return result
        # Treat empty result as miss
        raise ValueError("empty parquet result")
    except Exception as e:
        current_app.logger.warning(
            f"Parquet miss for {code}: {e}. Falling back to OASIS."
        )
        html = scraper.fetch_profile(code)
        return parser.parse_profile(html, code)
```

**When parquet wins:** Profile code is in `element_labels.parquet` (900 profiles covered)

**When fallback fires:**
- Profile not in parquet (codes not yet ingested)
- Parquet file missing or corrupt
- `element_main_duties` sparse (only 3 profiles) — fallback fetches full main duties from OASIS
- Any DataFrame query exception

**Logging:** Warning on fallback, not error. Fallback is expected during v5.0 transition.

**Feature flag option (optional, Phase 22+):**
```python
# src/config.py
USE_PARQUET_PRIMARY = os.getenv("USE_PARQUET_PRIMARY", "true").lower() == "true"
```

If flag is false, skip parquet entirely and go straight to OASIS. Useful for debugging.

---

## Data Flow Diagrams

### Search Flow (Target)

```
/api/search?q=engineer
        |
        v
noc_search_service.search("engineer")
        |
        |-- load_once: dim_noc, element_labels,
        |              element_example_titles, element_lead_statement
        |
        |-- keyword match across:
        |     element_labels.Label         (score 95-100)
        |     dim_noc.class_title          (score 90)
        |     element_example_titles.text  (score 80)
        |     element_lead_statement.text  (score 50)
        |
        v
List[EnrichedSearchResult]
        |
        |-- (empty or exception) --> fallback to scraper.search()
        |                           + parser.parse_search_results_enhanced()
        v
[EXISTING] relevance scoring in api.py (lines 99-167)
        |
        v
SearchResponse  (schema unchanged)
```

### Profile Flow (Target)

```
/api/profile?code=21211
        |
        v
noc_profile_service.fetch_profile("21211")
        |
        |-- normalize code: "21211" -> "21211.00"
        |
        |-- title: element_labels WHERE oasis_profile_code = "21211.00"
        |
        |-- main_duties: element_main_duties WHERE oasis_profile_code = "21211.00"
        |   WARNING: sparse table — likely empty for most codes
        |   -> if empty, downstream fallback handles it
        |
        |-- skills, abilities, knowledge, work_activities:
        |   oasis_skills/abilities/knowledges/workactivities parquets
        |   -> pivot wide row to [{text, level, max}] via parquet_adapter
        |   -> strip whitespace from column names
        |
        |-- work_context:
        |   oasis_workcontext parquet
        |   -> pivot wide row to [{text, level, max, dimension_type="Unknown"}]
        |
        |-- employment_requirements: element_employment_requirements
        |-- reference_attributes.example_titles: element_example_titles
        |
        v
Dict[str, Any]  (same schema as parser.parse_profile() output)
        |
        |-- (exception or code not found) --> fallback to scraper + parser
        |
        v
mapper.to_jd_elements(noc_data)  (unchanged)
        |
        +-- labels_loader (already reads parquet for labels, work_context enrichment)
        |
        v
ProfileResponse  (schema unchanged)
```

---

## Response Schema Compatibility

**The frontend JS must not change.** Both response schemas are preserved identically.

### SearchResponse — unchanged

```json
{
    "query": "engineer",
    "results": [
        {
            "noc_code": "21211.00",
            "title": "Data scientists",
            "url": "",
            "lead_statement": "Data scientists use...",
            "teer_description": null,
            "broad_category_name": null,
            "relevance_score": 95,
            "match_reason": "Title contains \"engineer\""
        }
    ],
    "count": 1,
    "metadata": { ... }
}
```

**Parquet vs OASIS differences in this response:**
- `url`: OASIS returns a real URL; parquet returns `""` (empty string). The frontend currently uses `url` only as a fallback display. The NOC code is the canonical key.
- `teer_description`: OASIS populates from search HTML; parquet has this derivable from noc_code but Phase 21 determines exact column availability. Can be left null.
- `broad_category_name`: Same — derivable but may be null until Phase 21 determines source.

**These nulls are safe** — the frontend already handles them as optional fields (see `EnrichedSearchResult` model with `Optional` on all extended fields).

### ProfileResponse — unchanged

The `mapper.to_jd_elements()` produces the exact same structure whether it receives parquet-derived or OASIS-derived `noc_data`. The adapter guarantees this. No frontend changes needed.

One exception: `metadata.profile_url`. Currently set to OASIS URL. When serving from parquet, this should be set to a canonical JobForge identifier or left as the OASIS URL for provenance traceability.

---

## Build Order (Phase Sequence)

The order is constrained by data dependencies discovered in Phase 21.

### Phase 21: Data Exploration (MANDATORY FIRST)

**Goal:** Answer: what can parquet serve completely today vs what still requires OASIS?

**Deliverables:**
- Inventory all parquet files relevant to search and profile
- Verify completeness: how many profiles have main duties in `element_main_duties`?
- Identify column name issues (trailing whitespace in wide-format parquets)
- Map `unit_group_id` / `oasis_profile_code` join logic
- Confirm `dim_noc.class_title` is title-level (not label-level)
- Document which data the parquet fallback must cover vs OASIS-only content

**Do not implement anything in Phase 21.** Exploration only. The Phase 22+ implementation plan depends on these findings.

### Phase 22: Parquet Search Service

**Goal:** Implement `noc_search_service.py` and wire into `/api/search` with fallback.

**Prerequisites:** Phase 21 findings confirm `element_labels` + `element_lead_statement` cover all 900 profiles.

**Scope:**
- `NOCSearchService` class with pandas-based text search
- Wire into `/api/search` route with parquet-first fallback
- Unit tests: known NOC codes return correct results
- Integration test: fallback fires on missing code

**Not in scope:** Semantic search, fuzzy matching, ranking refinement. Basic substring/keyword matching only.

### Phase 23: Parquet Profile Service

**Goal:** Implement `noc_profile_service.py` + `parquet_adapter.py` and wire into all profile fetch points.

**Prerequisites:** Phase 21 confirms wide-format pivot strategy. Phase 22 complete.

**Scope:**
- `NOCProfileService.fetch_profile()` returning parser-compatible dict
- `ParquetAdapter._pivot_wide_to_statements()` for oasis_* tables
- Column name normalization (whitespace stripping)
- Wire into `/api/profile`, `/api/preview`, `/api/export/pdf`, `/api/export/docx`
- The main_duties gap (sparse `element_main_duties`) — handle by returning empty list, triggering fallback

### Phase 24: Main Duties ETL Gap (if confirmed in Phase 21)

**Goal:** Ensure main duties are served from parquet, not OASIS.

**Condition:** Only needed if Phase 21 confirms `element_main_duties` is sparse (currently verified: only 3 profiles).

**Scope:** ETL pipeline to load `main-duties_oasis-2023_v1.0.csv` (4,991 rows, all 900 profiles) into `element_main_duties.parquet`. This is a JobForge-side task, not a JD Builder task — but JD Builder Phase 21 must flag the gap so it can be coordinated.

### Phase 25 (Optional): Remove OASIS Fallback

**Goal:** Confidence-test that parquet is complete enough to remove OASIS dependency entirely.

**Prerequisites:** Phase 21-23 complete, fallback call rate is measurably low in logs.

**Scope:** Feature flag `USE_PARQUET_PRIMARY=true` with `DISABLE_OASIS_FALLBACK=true` mode. Monitor for 404/miss rates.

---

## Component Summary

| Component | Action | File | Reason |
|-----------|--------|------|--------|
| `NOCSearchService` | CREATE | `src/services/noc_search_service.py` | Parquet search |
| `NOCProfileService` | CREATE | `src/services/noc_profile_service.py` | Parquet profile read |
| `ParquetAdapter` | CREATE | `src/services/parquet_adapter.py` | Wide-to-list pivot |
| `api.py` search route | MODIFY | `src/routes/api.py` L88-89 | Wire parquet-first |
| `api.py` profile route | MODIFY | `src/routes/api.py` L231-233 | Wire parquet-first |
| `api.py` export routes | MODIFY | `src/routes/api.py` L372, 416, 460 | Wire parquet-first |
| `config.py` | MINOR EXTEND | `src/config.py` | Expose gold/source paths |
| `scraper.py` (OASIS) | UNCHANGED | `src/services/scraper.py` | Fallback stays |
| `parser.py` | UNCHANGED | `src/services/parser.py` | Fallback stays |
| `mapper.py` | UNCHANGED | `src/services/mapper.py` | Accepts both sources |
| `labels_loader.py` | UNCHANGED | `src/services/labels_loader.py` | Already parquet |
| `vocabulary/index.py` | UNCHANGED | `src/vocabulary/index.py` | Already parquet |

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: Changing mapper.py to Accept Parquet Directly

**What people do:** Pass a pandas DataFrame or raw parquet dict directly to `mapper.to_jd_elements()`.

**Why it's wrong:** `mapper.to_jd_elements()` has a well-tested contract. Breaking its input schema would require updating every consumer and test. The parser produces a specific dict format; the adapter must produce that same format.

**Do this instead:** `parquet_adapter.py` bridges the format gap. `mapper.py` never needs to know whether data came from HTML parsing or parquet.

### Anti-Pattern 2: Replacing scraper.py Instead of Wrapping It

**What people do:** Delete `scraper.py` and replace all callsites with parquet calls.

**Why it's wrong:** OASIS is the only source of truth for some data during v5.0 transition (sparse `element_main_duties`, anything not yet in gold). Removing the fallback means those profiles silently return empty data.

**Do this instead:** Keep `scraper.py` exactly as is. Add parquet-first logic in the route layer where the try/except is visible and easy to monitor.

### Anti-Pattern 3: Loading All Parquet Files at Startup

**What people do:** Load all 10+ parquet DataFrames when the Flask app starts.

**Why it's wrong:** Increases startup time, uses memory for parquet data that may not be needed on every request. The existing `LabelsLoader` pattern uses lazy loading for a reason.

**Do this instead:** Follow `LabelsLoader` pattern — `_load_X()` method that loads once on first call, caches in instance variable, returns `False` gracefully if file not found.

### Anti-Pattern 4: Matching on Whitespace-Contaminated Column Names

**What people do:** Use `df['Writing  ']` (with trailing spaces) directly as the text value in search results.

**Why it's wrong:** The `oasis_skills`, `oasis_abilities`, and other wide-format parquets have column names with leading/trailing whitespace (confirmed: `'Writing  '`, `' Digital Literacy'`, `'Oral Communication: Active Listening   '`). These will appear verbatim in statement text shown to users.

**Do this instead:** `parquet_adapter.py` strips whitespace from all column names before using them as text values. This must happen before any output is passed to `mapper.py`.

### Anti-Pattern 5: Returning OASIS URL in parquet-sourced SearchResponse

**What people do:** Set `profile_url` in `SearchResponse.metadata` to an OASIS URL when the data came from parquet.

**Why it's wrong:** Misleads provenance — the data didn't come from that URL.

**Do this instead:** When serving from parquet, set `profile_url` to a JobForge canonical reference (e.g., `jobforge://gold/element_labels/21211.00`) or leave as the OASIS URL with a note that it's the authoritative source reference (not the fetch source). Phase 21 should decide the convention.

---

## Integration Points Checklist

- [ ] `src/routes/api.py` L88-89 — `/api/search` calls `noc_search_service.search()`
- [ ] `src/routes/api.py` L231-233 — `/api/profile` calls `noc_profile_service.fetch_profile()`
- [ ] `src/routes/api.py` L372 — `/api/preview` calls `noc_profile_service.fetch_profile()`
- [ ] `src/routes/api.py` L416 — `/api/export/pdf` calls `noc_profile_service.fetch_profile()`
- [ ] `src/routes/api.py` L460 — `/api/export/docx` calls `noc_profile_service.fetch_profile()`
- [ ] All five above have OASIS fallback in except block
- [ ] `src/config.py` exports `JOBFORGE_GOLD_PATH` and `JOBFORGE_SOURCE_PATH`
- [ ] `parquet_adapter.py` strips whitespace from wide-format column names
- [ ] `noc_profile_service.fetch_profile()` output matches `parser.parse_profile()` dict contract
- [ ] `noc_search_service.search()` output is `List[EnrichedSearchResult]` (same type as parser)
- [ ] Fallback logs `WARNING` (not `ERROR`) — fallback is expected during transition

---

## Sources

- Codebase inspection: `src/routes/api.py`, `src/services/scraper.py`, `src/services/parser.py`, `src/services/mapper.py`, `src/services/labels_loader.py`, `src/vocabulary/index.py`, `src/models/responses.py`, `src/models/noc.py`, `src/config.py` (HIGH confidence — direct file reads)
- JobForge parquet schemas verified via Python/pandas inspection (HIGH confidence — verified 2026-03-06):
  - `dim_noc.parquet`: 516 rows, confirmed columns
  - `element_lead_statement.parquet`: 900 rows, confirmed columns
  - `element_main_duties.parquet`: 8 rows (3 profiles only) — CRITICAL GAP
  - `oasis_skills.parquet`: 900 rows, 41 columns including whitespace-contaminated names
  - `element_labels.parquet`: 900 rows, confirmed columns
  - `element_example_titles.parquet`: 18,666 rows, confirmed columns
  - `source/main-duties_oasis-2023_v1.0.csv`: 4,991 rows, all 900 profiles — confirms source exists
- `.planning/JOBFORGE-DATA-REQUIREMENTS.md` — existing data inventory (HIGH confidence)

---

*Architecture research for: JobForge 2.0 parquet integration — Flask OASIS scraping migration*
*Researched: 2026-03-06*
