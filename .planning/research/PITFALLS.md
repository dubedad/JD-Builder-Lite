# Pitfalls Research: v5.0 JobForge 2.0 Integration

**Domain:** Flask app migration from live HTML scraping to local parquet as primary data source
**Researched:** 2026-03-06
**Confidence:** HIGH (based on direct codebase analysis + verified pyarrow/pandas patterns)

---

## Executive Summary

v5.0 migrates JD Builder Lite from OASIS HTML scraping as the primary data source to JobForge 2.0 gold parquet files, with OASIS scraping retained as a fallback. This is not a greenfield integration — parquet is already partially in use (`labels_loader.py` supplies labels, work context, exclusions, interests, and example titles). The patterns established in the existing code reveal what works and what will bite you at scale.

The highest-risk pitfalls in this migration are not pyarrow API issues or file format problems. They are behavioral: the current codebase returns silent empty lists on every parquet failure, which means parquet gaps are invisible unless actively monitored. When parquet becomes _primary_ rather than supplementary, silent empty results flip from "missing enhancement" to "missing core data."

The second category of risk is the search gap: parquet has no equivalent to OASIS free-text search. The fallback decision for search is architecturally different from the fallback decision for profile data, and treating them the same way will produce confusing user-facing behavior.

---

## Critical Pitfalls

### PITFALL-V5-01: Silent Empty Results Masking Parquet Coverage Gaps

**What goes wrong:**
Every `_load_*` method in `labels_loader.py` catches all exceptions and returns `False`, and every `get_*` method catches all exceptions and returns `[]`. When parquet is supplementary, returning `[]` is fine — the scraper provides the real data. When parquet becomes primary, returning `[]` means the user gets an empty profile with no error, no warning, and no indication that anything is wrong.

**Why it happens:**
The existing code was designed for graceful degradation when parquet is optional. The exception-swallowing pattern (`except Exception: return []`) was intentional and correct for that role. The migration changes the contract: parquet going missing is now a data outage, not a missing enhancement.

Concrete example from the codebase (`labels_loader.py` line 258-260):
```python
except Exception:
    return False  # Silent failure - caller gets []
```

This pattern is repeated across all eight `_load_*` methods and all `get_*` methods. A missing or corrupt parquet file produces zero log output and zero error response.

**Warning signs:**
- Profile API returns 200 with empty `key_activities`, `skills`, `effort`, `responsibility` sections
- User searches successfully but clicking a profile shows nothing
- Fallback to OASIS never triggers because no exception is raised — `[]` is treated as a valid (empty) result
- `labels_loader.get_error()` exists but is never checked in `mapper.py` or `api.py`

**How to avoid:**
- Add explicit coverage checks: if parquet returns 0 results for a NOC code that should have data, that is a coverage miss, not a valid empty result
- Distinguish between "file missing/unloadable" (hard error, trigger fallback) and "NOC code not in parquet" (soft miss, trigger fallback)
- Log at WARNING level when parquet returns empty for a profile request: `logger.warning(f"Parquet coverage miss for {code}: {section}")`
- In the profile route, check coverage before returning: if all parquet sections are empty and OASIS fallback is available, use fallback instead of returning empty profile

**Phase to address:** Exploration phase (Phase 21) — inventory parquet coverage before any migration, and instrument the loader before promoting parquet to primary

---

### PITFALL-V5-02: Search Has No Parquet Equivalent

**What goes wrong:**
The current `/api/search` route is 100% OASIS-dependent. It calls `scraper.search()`, parses live HTML, and applies in-memory TF-IDF relevance scoring. The gold parquet files contain profile data by NOC code but have no full-text search index. If OASIS goes down or is unreachable, search returns a 502 — no parquet fallback exists or is possible without building a separate search index.

**Why it happens:**
Parquet is a columnar storage format for structured data, not a search engine. The existing parquet files (`element_labels.parquet`, `element_example_titles.parquet`, etc.) are keyed by `oasis_profile_code` — you must already know the code to query them. The search experience (type a job title, get a list of matching NOC profiles) requires either OASIS or a separately-built search index.

**Warning signs:**
- Planning assumes "parquet primary, OASIS fallback" applies uniformly to both search and profile routes
- Roadmap phase that adds parquet search without a separate index-building step
- Search route treated as a one-line swap from `scraper.search()` to `parquet_loader.search()`

**How to avoid:**
- Treat search and profile as two separate migration problems with different solutions
- For search: OASIS remains primary with no practical parquet replacement unless a title index is built from parquet data; the migration scope for search is "improve resilience" not "replace data source"
- For profile: parquet becomes primary (for sections it covers); OASIS is fallback
- If a parquet-based search index is desired, budget explicit scope for building and maintaining it (TF-IDF over NOC titles + descriptions from parquet)
- Do not block profile migration on solving the search problem — they are independent

**Phase to address:** Exploration phase — document search as out-of-scope for the parquet-primary migration unless a search index is explicitly built

---

### PITFALL-V5-03: Fallback Trigger Ambiguity — When Does Fallback Fire?

**What goes wrong:**
The fallback decision logic is undefined. The current code does not have a fallback for profile data (parquet is supplementary, not primary). When parquet becomes primary, three cases must be handled differently:

1. **Parquet file missing or unloadable** — hard error, should trigger OASIS fallback immediately
2. **Parquet has the NOC code but a section is empty** — may be a legitimate empty section (the occupation has no exclusions) or a data gap
3. **NOC code not in parquet at all** — coverage gap, should trigger OASIS fallback

Without explicit logic for each case, the fallback will either never trigger (silent empty) or always trigger (parquet becomes useless). The current `labels_loader.py` makes all three cases indistinguishable — they all return `[]`.

**Warning signs:**
- Fallback logic implemented as `if not parquet_result: use_oasis()` — this conflates all three cases
- Fallback triggers for NOC codes that are legitimately empty in parquet (e.g., a new NOC code with no exclusions)
- Fallback never triggers for NOC codes not in parquet (because `[]` looks like "empty but valid")
- No logging to distinguish which case occurred

**How to avoid:**
- Return a structured result from the parquet loader, not just a value: `(data, coverage_status)` where status is `LOADED`, `EMPTY_VALID`, `NOT_FOUND`, or `LOAD_ERROR`
- Trigger OASIS fallback only on `NOT_FOUND` and `LOAD_ERROR`; accept `EMPTY_VALID` (genuine empty sections exist)
- Log every fallback trigger with the reason: `logger.info(f"Parquet NOT_FOUND for {code}, using OASIS")`
- Build the coverage map during the exploration phase so `NOT_FOUND` vs `EMPTY_VALID` can be distinguished

**Phase to address:** Profile retrieval phase (Phase 22) — design the coverage decision API before writing any fallback logic

---

### PITFALL-V5-04: Hardcoded Absolute Paths Break on Environment Change

**What goes wrong:**
`labels_loader.py` hardcodes the parquet path as `/Users/victornishi/Documents/GitHub/JobForge-2.0/data/gold`. The environment variable `JOBFORGE_GOLD_PATH` overrides this, but the fallback is a developer-specific absolute path. When the app runs on any machine other than the developer's Mac — CI, a colleague's machine, a client demo VM — all parquet loading silently fails and the system runs in pure-scraping mode with no indication of why.

This is an existing pitfall that becomes critical once parquet is primary.

**Why it happens:**
The env-var pattern was added correctly, but the fallback default is the developer's local path rather than a relative path or a clear "not configured" sentinel. Silent failure (returns `[]`) means this configuration error is invisible.

**Warning signs:**
- App starts without error on a new machine but all parquet-backed sections are empty
- `JOBFORGE_GOLD_PATH` not documented in `.env.example` or README
- CI environment has no parquet files and tests pass because the loader silently returns empty
- A colleague reports "I set up the project and profiles have no work context"

**How to avoid:**
- Change the default to `None` or a sentinel that forces configuration
- On startup, if `JOBFORGE_GOLD_PATH` is not set and the hardcoded fallback does not exist, log a WARNING: `"JOBFORGE_GOLD_PATH not configured — parquet features disabled"` and set a flag that changes behavior to OASIS-primary mode
- Add `JOBFORGE_GOLD_PATH` to `.env.example` with an instructional comment
- Add a startup check that prints parquet status: `[LabelsLoader] Parquet: AVAILABLE (7 files) / UNAVAILABLE (path not found)`

**Phase to address:** Exploration phase — fix path configuration and startup diagnostics before any other work

---

### PITFALL-V5-05: Partial Profile Assembly — Frontend Receives Hybrid Undefined State

**What goes wrong:**
When parquet covers some sections of a profile and OASIS covers others, the assembled profile has mixed provenance. The frontend cannot distinguish between "this section came from parquet (potentially stale)" and "this section came from OASIS (live)." If the parquet data is from a 2023 snapshot and OASIS was updated in 2025, the same profile response may show 2023 skills data alongside 2025 main duties.

This is not a hypothetical — the current `mapper.py` already merges parquet example titles with scraped example titles (lines 53-61). The v5.0 migration extends this pattern to more sections, making hybrid provenance the norm.

**Warning signs:**
- `metadata.scraped_at` in ProfileResponse reflects the OASIS fetch time even for data that came from parquet
- No field in the response indicates which sections came from which source
- User edits a JD based on parquet data, compliance audit asks "where did this come from," answer is ambiguous
- A section that changed between the parquet snapshot date and today is presented without staleness indication

**How to avoid:**
- Add a `data_source` field to `EnrichedJDElementData` or `EnrichedNOCStatement`: `"parquet"`, `"oasis_live"`, or `"hybrid"`
- Add `parquet_snapshot_date` to the profile response metadata (read from the parquet file's `_ingested_at` column if available)
- The compliance provenance chain already tracks `source_url` — extend it to include `source_type` and `source_date`
- Do not mix parquet and OASIS data within the same JD element without indicating this in the response

**Phase to address:** Profile retrieval phase — design provenance fields before implementing the merge logic

---

### PITFALL-V5-06: Startup Time Regression from Eager Parquet Loading

**What goes wrong:**
`labels_loader.py` uses lazy loading — parquet files are loaded on first access, not at app startup. This was acceptable when parquet was supplementary (first access happens lazily during a profile request). When parquet becomes primary and covers more sections, the first profile request after startup will trigger 6-8 simultaneous lazy loads, creating a multi-second latency spike on the first request.

The vocabulary index in `app.py` already demonstrates the correct pattern: `initialize_vocabulary()` is called at startup, loading parquet eagerly. The `labels_loader` does not follow this pattern.

**Warning signs:**
- First profile request after server start takes 3-5 seconds; subsequent requests are fast
- Startup logs show `[LabelsLoader] Loaded ...` messages during the first API request, not during app initialization
- Load testing shows high P99 latency on first request from each worker
- Log timestamps: server starts at T+0, first `[LabelsLoader] Loaded` message appears at T+5s (on first request)

**How to avoid:**
- Add parquet pre-loading to `create_app()` in `app.py`, after the vocabulary initialization
- Pre-load the files most critical to profile rendering: `element_labels`, `element_example_titles`, `oasis_workcontext`
- Log the pre-load result at startup: `[LabelsLoader] Pre-loaded 8 parquet files in 1.2s`
- Keep lazy loading as a fallback for files loaded after first request, but primary files should be eager

**Phase to address:** Exploration phase — measure load times before migration and ensure startup pre-loading is in place

---

### PITFALL-V5-07: Stale Parquet Data Presented as Current

**What goes wrong:**
Parquet files are point-in-time snapshots. The JobForge 2.0 gold parquet was generated from OASIS data at a specific date. When a NOC profile is updated on OASIS (new main duties, revised work context, different skill levels), the parquet file does not update automatically. Users who rely on the parquet-primary profile will receive the snapshot version without knowing it is potentially months old.

For a compliance tool that generates legally-relevant job descriptions, "data currency" matters. A hiring manager using a 12-month-old NOC profile snapshot may produce a JD that does not reflect current government classifications.

**Warning signs:**
- No `_ingested_at` date displayed in the profile UI
- Profile response `metadata.scraped_at` reflects the OASIS fallback time, not the parquet snapshot date
- No version information on the parquet files (when were they generated?)
- Users do not know they are seeing snapshot data

**How to avoid:**
- Expose the parquet snapshot date in the profile response: `parquet_snapshot_date: "2025-Q4"`
- Display this date in the UI: "Data from JobForge 2.0 snapshot (Q4 2025). Live OASIS data may differ."
- Provide a "Refresh from OASIS" action on profile pages that bypasses parquet and fetches live
- Define a staleness threshold: if parquet snapshot is older than N months, show a staleness warning

**Phase to address:** Profile retrieval phase — add snapshot date to response schema before UI implementation

---

## Moderate Pitfalls

### PITFALL-V5-08: NOC Code Format Mismatch Between Parquet and OASIS

**What goes wrong:**
OASIS uses `21211.00` (5 digits, decimal, 2 decimal digits). The parquet files use the same format in some columns but not consistently. The `interests_oasis_2023_v1.0.csv` file uses float format for `OaSIS Code` (21232.0), requiring `float(oasis_profile_code)` conversion in `labels_loader.py` (line 421). Other parquet files use string format. When a profile code arrives as `21211` (without `.00`), some parquet lookups return nothing silently.

**Warning signs:**
- Works for codes typed as `21211.00` but fails for `21211`
- Interests and personal attributes return empty while other sections populate correctly
- Different parquet files return data for the same code (some handle format, some don't)

**How to avoid:**
- Normalize all incoming NOC codes to `XXXXX.XX` format at the API boundary (already partially done via `NOC_CODE_PATTERN` in `api.py` line 50)
- Add a `normalize_oasis_code(code: str) -> str` utility that ensures `21211` becomes `21211.00`
- Apply normalization before any parquet query in `labels_loader.py`
- Document which parquet files use string format and which use float

**Phase to address:** Exploration phase — audit code format across all parquet files and add normalization utility

---

### PITFALL-V5-09: Fallback Causes Double Latency Without User Indication

**What goes wrong:**
When the parquet lookup fails or returns empty and the OASIS fallback is triggered, the total request latency is `parquet_query_time + oasis_request_time`. For a profile request, OASIS fetching takes 1-3 seconds. If parquet silently fails first (1-2 seconds of pandas operations), the user waits 2-5 seconds total with no indication of why it's slow. If the fallback is triggered frequently (e.g., because parquet coverage is incomplete), every affected profile request will be slower than the pure-OASIS baseline.

**Warning signs:**
- Profile requests are slower after the parquet integration than before
- Some NOC codes respond in 500ms (parquet hit), others in 3 seconds (fallback)
- No logging to distinguish fast parquet-hit requests from slow fallback requests
- Users notice some profiles load instantly and some are slow, with no explanation

**How to avoid:**
- Log every fallback trigger with reason and latency: `logger.info(f"OASIS fallback for {code}: reason=NOT_FOUND, parquet_ms=1200, oasis_ms=2800")`
- Add a response header or metadata field indicating the data source for the current response
- Consider a short-circuit: if parquet lookup fails within 100ms (file missing), skip to OASIS immediately rather than waiting for full pandas load attempt
- Track fallback rate in metrics; if above 20%, investigate coverage gaps

**Phase to address:** Profile retrieval phase — build fallback with explicit timing and logging

---

### PITFALL-V5-10: Search Relevance Regression When OASIS Is Unavailable

**What goes wrong:**
If OASIS becomes unavailable and a parquet-based title index is built as an emergency fallback for search, the relevance scoring in the current `/api/search` route (lines 99-163 of `api.py`) is tightly coupled to OASIS response structure. A parquet-based search would return different result shapes, potentially breaking the relevance scoring pipeline and returning unranked or poorly-ranked results.

The current search scoring pipeline does stemming, plural normalization, and title/lead-statement matching. Lead statements come from OASIS HTML parsing — parquet may not have equivalent fields.

**Warning signs:**
- Search results from parquet fallback are not sorted by relevance
- `lead_statement` field is None/empty for parquet search results, causing the `lead_has_exact` branch to never fire
- `relevance_score` is 10 ("matched on alternate title") for all parquet results because the scoring depends on lead statement
- Users notice search quality degrades when OASIS is down

**How to avoid:**
- If building a parquet search index, ensure the result schema matches `EnrichedSearchResult` including `lead_statement`
- Use the same scoring pipeline for parquet results as for OASIS results — do not build a separate scoring system
- Test search relevance for parquet-backed results explicitly: verify that "data engineer" returns high-relevance results, not just any NOC code that contains those words

**Phase to address:** Search enhancement phase (if in scope) — design parquet search index to be compatible with existing scoring pipeline

---

### PITFALL-V5-11: Lazy Loading Race Condition in Multi-Worker Flask

**What goes wrong:**
`labels_loader.py` uses a module-level singleton initialized lazily. If Flask is run with multiple workers (gunicorn with `--workers 4`), each worker process initializes its own `labels_loader` singleton independently. This is correct behavior — there is no shared memory between workers. However, the lazy loading pattern means all workers load parquet files independently on their first request, potentially causing a thundering herd on startup: 4 workers × 8 parquet files = 32 simultaneous file reads.

For the current supplementary-only use, this is low impact. For parquet-as-primary, this becomes the critical startup path.

**Warning signs:**
- Under gunicorn with multiple workers, first batch of requests after startup is slow
- Log shows overlapping `[LabelsLoader] Loaded ...` messages from multiple workers simultaneously
- Memory usage spikes at startup (multiple workers loading large parquet DataFrames)

**How to avoid:**
- Pre-load parquet at app initialization (`create_app()`), not on first request — this happens once per worker but at startup time, not at request time
- Avoid shared state across workers (do not use Redis or mmap for parquet cache) — each worker should have its own in-memory DataFrames
- Document that gunicorn worker memory usage scales with number of workers × parquet DataFrame size

**Phase to address:** Exploration phase — measure per-worker memory footprint of parquet DataFrames

---

## Technical Debt Patterns

Shortcuts that seem reasonable but create long-term problems.

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Keep `except Exception: return []` pattern as-is | No code change required for exploration | Parquet coverage gaps are invisible; fallback never triggers correctly | Only acceptable in exploration phase; must be fixed before parquet-as-primary |
| Use `None` check to decide fallback (`if not parquet_result`) | Simple one-line fallback logic | Cannot distinguish empty-valid from not-found from load-error | Never acceptable for primary data source |
| Skip provenance field for parquet-sourced data | Faster implementation | Compliance audit fails: "where did this come from?" | Never: compliance provenance is a core requirement |
| Hardcode parquet snapshot date as a constant | No file-read needed | Date becomes stale as snapshots are updated | Only for MVP exploration; replace with dynamic read from `_ingested_at` |
| Use OASIS always as double-check after parquet | Simplest correctness guarantee | Doubles latency on every request; defeats the performance benefit of parquet | Never: if double-checking is needed, it should be selective (new NOC codes, staleness threshold) |

---

## Integration Gotchas

Common mistakes when connecting parquet to the existing scraping architecture.

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| `labels_loader` + `mapper.py` | Checking `if parquet_result` to decide whether to call OASIS, where `parquet_result` is `[]` | Return a coverage enum from loader; check `coverage_status == CoverageStatus.NOT_FOUND` |
| `labels_loader` path config | Using hardcoded fallback path from developer's machine | Require `JOBFORGE_GOLD_PATH` env var; log clearly if unset; never silently use stale path |
| Profile route + fallback | Catching OASIS `requests.RequestException` and re-raising as 502 (current behavior) | If parquet is primary, OASIS failure is a warning, not a fatal error; return parquet data with staleness flag |
| Parquet NOC code lookup | Querying with `oasis_profile_code == "21211"` | Always normalize to `21211.00` before query; add `normalize_oasis_code()` utility |
| Search route + parquet | Treating search as equivalent to profile: "add parquet fallback" | Search requires a separate text index; parquet is not a search engine; scope them separately |
| `scraped_at` timestamp | Setting `scraped_at = datetime.utcnow()` when parquet is the source | Set `scraped_at` to the parquet snapshot date when data came from parquet; use now() only for live OASIS fetches |

---

## Performance Traps

Patterns that work at small scale but fail as usage grows.

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Lazy-loading 8 parquet files on first request | First request after startup takes 3-5s; subsequent requests fast | Pre-load at `create_app()` for files needed on every profile request | On every cold start / worker restart |
| No coverage index — scanning full DataFrame per request | Profile requests slow as parquet files grow | Build per-code index dict at load time: `{code: row_index}` | When parquet files exceed ~50k rows |
| Triggering OASIS fallback silently on every NOC code not in parquet | All profile requests go to OASIS despite parquet integration | Build coverage map at load time; distinguish NOT_FOUND from LOAD_ERROR | Immediately after going to production |
| Loading all 8 parquet files in all 4 gunicorn workers | 32× file reads at startup, high memory | Tune worker count to fit parquet DataFrames in available RAM | At ~4 workers × ~500MB parquet total = 2GB RAM |

---

## "Looks Done But Isn't" Checklist

Things that appear complete but are missing critical pieces.

- [ ] **Parquet-as-primary:** Profile returns data but `metadata.scraped_at` still shows current time even when data came from parquet — verify snapshot date is set correctly
- [ ] **Fallback logic:** OASIS fallback "works" but check that it triggers for NOT_FOUND (missing NOC code) not just for LOAD_ERROR — verify with a NOC code known to not be in parquet
- [ ] **Coverage claim:** "Parquet covers X profiles" — verify by checking a random sample of NOC codes that OASIS returns in search results, not just codes known to be in parquet
- [ ] **Silent failure fixed:** `labels_loader.get_error()` is called somewhere and logged — verify it is not dead code
- [ ] **Path configuration:** `JOBFORGE_GOLD_PATH` is set in `.env.example` with instructions — verify a fresh clone does not silently run without parquet
- [ ] **Staleness visible to user:** Profile UI shows snapshot date — verify it renders correctly, not just that the field is in the response JSON
- [ ] **Search still works when OASIS is down:** Test with `OASIS_BASE_URL` pointed at a non-existent host — verify graceful error, not 500

---

## Recovery Strategies

When pitfalls occur despite prevention, how to recover.

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Silent empty profile (PITFALL-V5-01) | MEDIUM | Add logging to `labels_loader`; run profile requests for 10 NOC codes; check logs for coverage misses; identify which sections are empty |
| Parquet path not configured (PITFALL-V5-04) | LOW | Set `JOBFORGE_GOLD_PATH` in `.env`; restart app; verify `[LabelsLoader] Loaded` messages appear at startup |
| Hybrid provenance exposed in compliance audit (PITFALL-V5-05) | HIGH | Audit which profiles were generated from parquet vs. OASIS; add `data_source` to response; regenerate any JDs that used mixed-source data without disclosure |
| Startup latency spike (PITFALL-V5-06) | LOW | Move parquet load to `create_app()`; measure startup time before and after |
| Stale data discovered post-delivery (PITFALL-V5-07) | HIGH | Document snapshot date clearly; add "Refresh from OASIS" button; communicate data currency to all users; re-fetch affected profiles from OASIS |
| Fallback ambiguity causing wrong trigger (PITFALL-V5-03) | MEDIUM | Add coverage status enum to loader return; add logging for each fallback trigger; review logs to categorize actual failure modes |

---

## Pitfall-to-Phase Mapping

How roadmap phases should address these pitfalls.

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| PITFALL-V5-01: Silent empty results | Exploration (Phase 21) — add coverage logging and `CoverageStatus` enum | Run profile API for 20 NOC codes; verify warnings appear for misses |
| PITFALL-V5-02: Search has no parquet equivalent | Exploration (Phase 21) — document search as separate problem | Phase plan explicitly separates search and profile migration scope |
| PITFALL-V5-03: Fallback trigger ambiguity | Profile retrieval phase (Phase 22) — design `CoverageStatus` before any fallback code | Unit test: NOT_FOUND triggers OASIS; EMPTY_VALID does not; LOAD_ERROR triggers OASIS |
| PITFALL-V5-04: Hardcoded absolute paths | Exploration (Phase 21) — fix path config and startup diagnostics first | Fresh clone with only `.env.example` filled in: parquet loads correctly |
| PITFALL-V5-05: Hybrid provenance | Profile retrieval phase (Phase 22) — add `data_source` field to schema | Compliance review: every exported JD shows which sections came from parquet |
| PITFALL-V5-06: Startup latency from lazy loading | Exploration (Phase 21) — measure load times and decide pre-load strategy | Server startup log shows `[LabelsLoader] Pre-loaded N files in Xms` |
| PITFALL-V5-07: Stale parquet data | Profile retrieval phase (Phase 22) — add snapshot date to response | UI displays snapshot date; "Refresh from OASIS" button works |
| PITFALL-V5-08: NOC code format mismatch | Exploration (Phase 21) — audit code formats and add normalization utility | All parquet lookups use normalized `XXXXX.XX` format |
| PITFALL-V5-09: Fallback double latency | Profile retrieval phase (Phase 22) — add timing and source logging | Log analysis shows P50/P99 latency split between parquet-hit and fallback requests |
| PITFALL-V5-10: Search relevance regression | Search enhancement phase (if in scope) — validate parquet search schema matches existing scoring | Search quality test: top 5 results for "data engineer" are correct from both OASIS and parquet |
| PITFALL-V5-11: Multi-worker lazy loading | Exploration (Phase 21) — document worker memory requirements | gunicorn with 4 workers starts without thundering herd; startup time is predictable |

---

## Sources

- Direct codebase analysis: `src/services/labels_loader.py`, `src/services/mapper.py`, `src/routes/api.py`, `src/app.py`, `src/config.py` (2026-03-06)
- Pandas documentation: `read_parquet` lazy vs. eager loading behavior — verified HIGH confidence
- Python logging best practices for silent failure patterns — standard library, HIGH confidence
- Flask application factory pattern and worker memory isolation — official Flask docs, HIGH confidence
- NOC code format analysis: `oasis_profile_code` column in existing parquet files and `OaSIS Code` in CSV sources (observed in `labels_loader.py` lines 420-421)
- Prior pitfalls research for this project: `.planning/research/PITFALLS.md` (v1.1) and `.planning/research/v3-PITFALLS.md` (v3.0) for architectural context

---

*Pitfalls research for: v5.0 Flask migration from OASIS scraping to JobForge 2.0 parquet as primary data source*
*Researched: 2026-03-06*
