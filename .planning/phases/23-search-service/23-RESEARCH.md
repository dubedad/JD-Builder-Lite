# Phase 23 Research: Search Service

**Generated:** 2026-03-08
**Phase goal:** Sub-second search from parquet with tiered relevance scoring and transparent OASIS fallback.

---

## Current Search Flow

`GET /api/search?q=<query>` in `src/routes/api.py`:
1. Calls `scraper.search(query)` → HTTP request to OASIS (up to 60s timeout)
2. Calls `parser.parse_search_results_enhanced(html)` → list of `EnrichedSearchResult`
3. Scores results in-route with word-stemming logic (tiered: 100/95/85/60/50/10)
4. Returns `SearchResponse` with list of `EnrichedSearchResult`

**Bottleneck:** Step 1 (live OASIS HTTP). Can be 5-60s. Parquet replaces this.

---

## Parquet Files for Search (All 900 Profiles / 516 Unit Groups)

| File | Rows | Key Column | Search Column | Notes |
|------|------|-----------|--------------|-------|
| `element_labels.parquet` | 900 | `unit_group_id` | `Label` | Occupation title (e.g., "Software engineers and designers") |
| `element_lead_statement.parquet` | 900 | `unit_group_id` | `Lead statement` | Lead paragraph — long text |
| `element_example_titles.parquet` | 18,666 | `unit_group_id` | `Job title text` | Multiple titles per profile; `Job title type` is 'Example', 'Index', or 'Inclusion' |

All three files share `unit_group_id` (5-digit string, e.g., `'21231'`) as the join key.
`unit_group_id` maps directly to the NOC code (no transformation needed).
`oasis_profile_code` is `unit_group_id + ".00"` (e.g., `'21231.00'`).

### Column Notes
- `element_labels.parquet`: `Label` column may have whitespace — already handled by `read_parquet_safe` (strips all column names). The *value* in `Label` is clean.
- `element_lead_statement.parquet`: Column name `Lead statement` (with space). After strip this is correct.
- `element_example_titles.parquet`: `Job title type` values: `['Example', 'Index', 'Inclusion']`. All three are useful for search.

---

## Performance Benchmark

Measured on actual gold files (Python 3.14, macOS):

| Operation | Time |
|-----------|------|
| Load 3 files from disk (cold) | ~100ms |
| Load from module-level cache (warm) | ~0ms |
| Search across all 3 files (in-memory) | ~14ms |
| **Total cold** | ~115ms |
| **Total warm** | ~14ms |

**Conclusion:** Well under 1 second even on cold load. The existing `read_parquet_safe` cache ensures warm loads are instant.

---

## Tiered Scoring (SRCH-02)

From ROADMAP requirements:
- **95-100**: Labels match — `Label` in `element_labels.parquet` (exact/near-exact = 100, partial = 95)
- **90**: Occupation title match — exact or near-exact `Label` match (sub-tier)
- **80**: Example titles match — `Job title text` in `element_example_titles.parquet`
- **50**: Lead statement match — `Lead statement` in `element_lead_statement.parquet`

**Implementation interpretation:**
- Score 100: query == Label (case-insensitive, after plural normalization)
- Score 95: Label contains full query string
- Score 90: Label contains query stem(s)
- Score 80: Any `Job title text` contains query (all title types: Example, Index, Inclusion)
- Score 50: `Lead statement` contains query or query stems

**Existing scoring logic in api.py** (lines ~120-160) implements similar stemming + normalization. The parquet search service should use the same approach so behavior is consistent.

---

## URL Construction

Current OASIS results return a `url` field from the HTML. For parquet results, construct:
```python
url = f"{OASIS_BASE_URL}/OaSIS/OaSISProfile?code={unit_group_id}.00&version={OASIS_VERSION}"
```
This matches the profile URL format used by the existing scraper.

---

## Code Search (search_type='Code')

When `search_type='Code'` and query is a 5-digit NOC code:
- Look up `unit_group_id == query` directly in `element_labels.parquet`
- Return single result with score 100
- This replaces the OASIS code lookup path too

---

## New Service: SearchParquetReader

Create `src/services/search_parquet_reader.py`:

```python
class SearchParquetReader:
    def search(self, query: str, search_type: str = 'Keyword') -> list[EnrichedSearchResult] | None:
        """Return results from parquet or None if parquet unavailable."""
```

- Returns `None` on `LOAD_ERROR` (triggers OASIS fallback in api.py)
- Returns `[]` when parquet loads but query matches nothing (also triggers OASIS fallback per SRCH-03)
- Returns list of `EnrichedSearchResult` on success

**Why return None vs empty list matters:**
- `None` = parquet unavailable → always fall back
- `[]` = parquet searched but no results → also fall back (SRCH-03 says "returns no results")

---

## Integration in api.py

Minimal change to `search()` route:

```python
# 1. Try parquet
results = search_parquet_reader.search(query, search_type)

# 2. Fall back to OASIS if parquet unavailable or empty
if not results:
    html = scraper.search(query, search_type=search_type)
    results = parser.parse_search_results_enhanced(html)
    # ... existing scoring logic ...
    source = 'oasis'
else:
    source = 'parquet'
    # results already scored by SearchParquetReader
```

The existing post-processing (hierarchy codes, filter/sort, response building) runs regardless of source.

---

## Result Population

`EnrichedSearchResult` fields populated from parquet:

| Field | Source |
|-------|--------|
| `noc_code` | `unit_group_id` from labels |
| `title` | `Label` from `element_labels.parquet` |
| `url` | Constructed (see above) |
| `lead_statement` | `Lead statement` from `element_lead_statement.parquet` |
| `relevance_score` | Computed by tiered scoring |
| `match_reason` | Human-readable string |
| `broad_category` | First digit of `noc_code` |
| `sub_major_group` | First 3 digits |
| `unit_group` | First 4 digits |

Fields NOT populated from parquet (remain None): `teer_description`, `broad_category_name`, `matching_criteria`, `example_titles`, `mobility_progression`, `source_table`, `publication_date`, `top_skills`, `top_abilities`, `top_knowledge`.

**Note on `teer_description`:** OASIS search HTML includes TEER level description on the card. Parquet doesn't have this field. It's display-only; leaving it None is acceptable.

---

## Plan Breakdown (2 Plans)

### Plan 23-01: SearchParquetReader + tiered scorer
- Create `src/services/search_parquet_reader.py`
- Implement `search()` method: load 3 files via `read_parquet_safe`, join on `unit_group_id`, apply tiered scoring
- Unit test with known queries (e.g., 'software engineer' → finds 21231, 21232)
- **No api.py changes yet** — isolated service

### Plan 23-02: Wire into api.py + OASIS fallback
- Import `SearchParquetReader` in `api.py`
- Modify `/search` route: try parquet first, fall back to OASIS if `None` or `[]`
- Remove/skip existing OASIS scoring logic when parquet results are used (avoid double-scoring)
- Human verification: search 'software engineer', verify results appear fast + correct

---

## Key Constraints from Phase 21 Decisions

- `read_parquet_safe()` in `src/services/parquet_reader.py` handles caching and column stripping — reuse it, don't bypass
- `CoverageStatus.LOAD_ERROR` means fall back; `NOT_FOUND` also means fall back (no results)
- Import `JOBFORGE_GOLD_PATH` from `src.config` for file paths
- Code type search: `unit_group_id` column in `element_labels.parquet` is the lookup key
