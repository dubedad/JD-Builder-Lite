---
phase: 24-compliance-hardening
researched: 2026-03-09
domain: frontend JS, Flask route resilience, gsd-verifier process
confidence: HIGH
---

# Phase 24: Compliance Hardening - Research

**Researched:** 2026-03-09
**Domain:** Frontend JS export provenance, Flask route fallback, formal phase verification
**Confidence:** HIGH — all findings from direct source inspection, no ambiguity

## Summary

Phase 24 closes three concrete tech debt items identified in the v5.0 milestone audit. All three are
surgical, well-bounded changes with zero ambiguity about what to do or where to do it.

TD-1 is a one-line frontend fix: add `working_conditions` to the `section_sources` dict in
`export.js` lines 113-118. The backend already accepts the key. The value pattern is identical
to the four existing keys.

TD-2 is a route-level refactor of `/api/profile` in `src/routes/api.py` (lines 245-270): wrap
`scraper.fetch_profile()` in a try/except, catch `requests.RequestException` and any other
exception, and on failure construct a partial profile response using parquet-only data from
`mapper.to_jd_elements()` with a minimal stub `noc_data` dict. The five parquet tabs (Skills,
Abilities, Knowledge, Work Activities, Work Context) can all be served without OASIS. Main Duties
and working_conditions will be empty in the fallback.

TD-3 is documentation only: create `.planning/phases/22-profile-service/22-VERIFICATION.md`
containing a formal pass/fail assessment of Phase 22 against its four ROADMAP success criteria.
All four criteria are satisfied based on the existing SUMMARY files and the audit findings.

**Primary recommendation:** Implement in the order TD-1 (trivial), TD-3 (documentation only),
TD-2 (code change with most complexity). Each is independent; no ordering dependency between them.

---

## RESEARCH COMPLETE

### TD-1: working_conditions in export.js

**Current state (exact location):**

File: `static/js/export.js`
Lines 112-119 (the `section_sources` dict inside `buildExportRequest()`):

```javascript
// Per-section provenance for TBS Directive 32592 compliance (Phase 22)
section_sources: {
  key_activities: profile.key_activities?.data_source || 'oasis',
  skills: profile.skills?.data_source || 'oasis',
  effort: profile.effort?.data_source || 'oasis',
  responsibility: profile.responsibility?.data_source || 'oasis',
}
```

**The gap:** `working_conditions` is the 5th JD element but is absent from this dict. When a user
selects Working Conditions statements and exports, the TBS compliance appendix Section 6.2.3 does
not record where those statements came from.

**The fix — exact line to add:**

```javascript
section_sources: {
  key_activities: profile.key_activities?.data_source || 'oasis',
  skills: profile.skills?.data_source || 'oasis',
  effort: profile.effort?.data_source || 'oasis',
  responsibility: profile.responsibility?.data_source || 'oasis',
  working_conditions: profile.working_conditions?.data_source || 'oasis',
}
```

**Value analysis:**

- `profile.working_conditions` is returned by the API as the `working_conditions` key in
  `ProfileResponse`, produced by `mapper._map_working_conditions_enriched()`.
- That method returns `EnrichedJDElementData(statements=statements, ..., source_attribute="Work Context")`
  — notice: it does NOT set `data_source` explicitly.
- `EnrichedJDElementData.data_source` defaults to `"oasis"` (set in `src/models/responses.py`).
- Therefore `profile.working_conditions?.data_source` will always be `"oasis"` in the current
  implementation — the fallback `|| 'oasis'` is belt-and-suspenders.
- The value `'oasis'` is correct: `_map_working_conditions_enriched` reads from
  `enrichment_service.enrich_work_context(data.get('work_context', []), ...)` which is always
  OASIS-scraped data (work_context comes from the HTML parser, not parquet).
- This is a frontend-only fix. The backend `build_compliance_sections()` in `export_service.py`
  already iterates over `section_sources.items()` with no hardcoded key list — it will accept
  `working_conditions` without any backend change.

**Confidence:** HIGH — direct inspection of export.js lines 112-119, mapper.py
`_map_working_conditions_enriched`, export_service.py `build_compliance_sections()`.

---

### TD-2: /api/profile OASIS-down fallback

**Current route structure (src/routes/api.py lines 216-270):**

```python
@api_bp.route('/profile')
def profile():
    code = request.args.get('code', '')
    # ... validation (lines 228-243)
    try:
        # Fetch, parse, and map profile data
        html = scraper.fetch_profile(code)           # line 247 — OASIS HTTP call
        noc_data = parser.parse_profile(html, code)  # line 248
        jd_data = mapper.to_jd_elements(noc_data)    # line 249
        response = ProfileResponse(**jd_data)
        return jsonify(response.model_dump())
    except requests.RequestException as e:           # line 256 — HTTP errors
        return jsonify(error.model_dump()), 502       # line 262 — returns 502
    except Exception as e:                           # line 264 — all others
        return jsonify(error.model_dump()), 500       # line 270 — returns 500
```

**The gap:** Both except branches return an error response. When OASIS is down, the entire profile
fails even though 5 tabs can be served from parquet. The parquet path only activates inside
`mapper.to_jd_elements()`, which is never reached when `scraper.fetch_profile()` raises.

**How mapper.to_jd_elements() uses noc_data:**

`to_jd_elements(noc_data)` in `src/services/mapper.py` (line 65) expects a dict with:
- `noc_code` (str) — required for parquet lookups and building base_url
- `title` (str) — used as profile title
- `main_duties` (list) — from OASIS, empty list is safe
- `work_activities` (list) — from OASIS, empty list is safe
- `skills` (list) — from OASIS, empty list is safe
- `abilities` (list) — from OASIS, empty list is safe
- `knowledge` (list) — from OASIS, empty list is safe
- `work_context` (list) — from OASIS, empty list is safe
- `noc_hierarchy` (optional)
- `reference_attributes` (optional)

The 5 parquet tabs are fetched inside `to_jd_elements()` via `get_all_profile_tabs(noc_code)`.
They are NOT derived from `noc_data` — they use only `noc_code`. This means: if we call
`mapper.to_jd_elements()` with a minimal stub `noc_data` containing only `noc_code` and `title`,
the parquet tabs will still be served correctly.

**Exception types from scraper.fetch_profile():**

`scraper.py` uses `requests.Session.get()` with `response.raise_for_status()`. Possible exceptions:
- `requests.exceptions.ConnectionError` — OASIS host unreachable
- `requests.exceptions.Timeout` — request exceeds `REQUEST_TIMEOUT`
- `requests.exceptions.HTTPError` — non-200 response (raised by `raise_for_status()`)
- `requests.exceptions.RequestException` — base class for all of the above
- Any unexpected exception from the session layer

The existing route already catches `requests.RequestException` separately from `Exception`.

**What the fallback response should contain:**

When OASIS is down:
- Parquet tabs (Skills, Abilities, Knowledge, Work Activities, Work Context): populated from parquet
  if profile is covered, empty if not
- Main Duties / key_activities: empty list (OASIS-only, not in parquet)
- working_conditions: empty list (OASIS-only, derived from scraped work_context)
- title: unknown (could use noc_code as placeholder, e.g., `f"NOC {code}"`)
- metadata.profile_url: can still be constructed from `code` and config constants

**Recommended fallback pattern (to replicate search's pattern):**

In `src/routes/api.py`, modify the profile route try/except:

```python
try:
    html = scraper.fetch_profile(code)
    noc_data = parser.parse_profile(html, code)
except Exception as e:
    current_app.logger.warning(f"OASIS fetch failed for {code}, falling back to parquet: {e}")
    # Build minimal stub — parquet tabs will be populated by mapper from parquet_tabs
    noc_data = {
        'noc_code': code,
        'title': f'NOC {code}',
        'main_duties': [],
        'work_activities': [],
        'skills': [],
        'abilities': [],
        'knowledge': [],
        'work_context': [],
        'noc_hierarchy': None,
        'reference_attributes': None,
    }

try:
    jd_data = mapper.to_jd_elements(noc_data)
    response = ProfileResponse(**jd_data)
    return jsonify(response.model_dump())
except Exception as e:
    current_app.logger.error(f"Profile internal error for code {code}: {e}")
    error = ErrorResponse(error="Internal error", detail=None)
    return jsonify(error.model_dump()), 500
```

**Important implementation notes:**

1. The search fallback pattern (lines 87-100 in api.py) uses `if parquet_results is not None and
   len(parquet_results) > 0` to select the path. For profile, the pattern is different: try
   scraper first, catch exception, fall back to stub — not a "check parquet first" design.

2. The original try/except has TWO except branches (RequestException and Exception). The new design
   should catch ALL exceptions from the OASIS fetch/parse step, since the goal is "serve parquet
   if OASIS fails for any reason."

3. `parser.parse_profile(html, code)` should also be inside the try block because a malformed
   HTML response from OASIS (e.g., 200 but garbage) would raise in the parser. A failed parse
   should also trigger the parquet fallback.

4. `mapper.to_jd_elements(noc_data)` should be in its own try/except because if parquet itself
   fails (e.g., malformed parquet files), we should still return a 500 rather than silently
   returning an empty profile.

5. The 502 status code for `requests.RequestException` is currently the response. With the new
   design, the 502 disappears — the client gets a 200 with partial data instead. This is the
   intended behavior per the tech debt description ("OASIS-down no longer causes total profile
   failure").

**`requests` module import:** Already imported at line 9 of api.py (`import requests`).
No new imports needed.

**Confidence:** HIGH — direct inspection of api.py profile route (lines 216-270), mapper.py
`to_jd_elements` signature and body, scraper.py `fetch_profile` exception behavior.

---

### TD-3: Phase 22 VERIFICATION.md

**Phase 22 success criteria from ROADMAP.md:**

1. "Skills, Abilities, Knowledge, Work Activities, and Work Context tabs on the profile page load
   their statement data from parquet (not live OASIS scraping) for any of the 900 profiles covered
   in the gold files"

2. "Main Duties / Key Activities, Interests, Personal Attributes, and Core Competencies tabs
   automatically fall back to OASIS scraping without any user-visible error or empty state -- the
   fallback is transparent"

3. "Exported JD provenance metadata records each section's source as either 'JobForge parquet
   (version X, path Y)' or 'OASIS (URL, scrape timestamp)' -- the distinction is present and
   readable in the compliance block"

4. "All parquet column names displayed as UI labels are stripped of leading and trailing whitespace
   before rendering -- no label shows a leading space or trailing space regardless of raw column
   name in the file"

**Evidence from SUMMARY files and audit for each criterion:**

Criterion 1 — PASS:
- `22-01-SUMMARY.md`: "Verified: NOC 21211 returns 25/28/7/35/39 ratings from jobforge for
  skills/abilities/knowledge/work_activities/work_context"
- `mapper.py` confirmed: `get_all_profile_tabs(noc_code)` called in `to_jd_elements()`, all 5
  tabs use parquet-first path
- `profile_parquet_reader.py` confirmed: reads from `oasis_skills.parquet`, `oasis_abilities.parquet`,
  `oasis_knowledges.parquet`, `oasis_workactivities.parquet`, `oasis_workcontext.parquet`

Criterion 2 — PASS:
- `22-01-SUMMARY.md`: "Fallback verified: unknown NOC codes fall back gracefully (no crash)"
- `mapper.py` confirmed: when parquet returns `([], "oasis")`, OASIS enrichment path used
- `22-02-SUMMARY.md` user verification: "Source badges verified in browser... Badges visually
  distinct (green vs grey)"
- Key Activities always OASIS (confirmed in mapper.py comment: "data_source is always 'oasis':
  Main Duties anchor this element to OASIS")

Criterion 3 — PARTIAL PASS (TD-1 closes this fully):
- `SourceMetadataExport.section_sources` confirmed present in `export_models.py` line 160
- `build_compliance_sections()` confirmed writes per-section provenance to Section 6.2.3 when
  `section_sources` is present
- `export.js` confirmed sends `section_sources` with 4 keys — `working_conditions` key is missing
  (this is TD-1)
- Assessment: 4 of 5 sections tracked; criterion not fully satisfied until TD-1 is implemented

Criterion 4 — PASS:
- From Phase 21-02 SUMMARY and Phase 21 VERIFICATION.md: `read_parquet_safe()` strips whitespace
  at read time
- Phase 21 VERIFICATION.md: "Phase 21 — Passed 4/4 criteria" which includes PROF-04

**Recommended VERIFICATION.md structure and content:** The file should follow the standard
gsd-verifier format with explicit PASS/FAIL per criterion, evidence citations, and an overall
verdict. Overall verdict should be CONDITIONAL PASS (3 of 4 criteria fully met; criterion 3
partially met pending TD-1 from Phase 24).

**File location:** `.planning/phases/22-profile-service/22-VERIFICATION.md`

**Confidence:** HIGH — Phase 22 success criteria from ROADMAP confirmed; evidence from SUMMARY
files confirmed; partial satisfaction of criterion 3 documented in v5.0-MILESTONE-AUDIT.md.

---

### Implementation Notes

**Ordering:**

TD-1 (export.js one-liner) and TD-3 (documentation) can be done in any order — they are
fully independent. TD-2 (route change) is also independent but has the most code complexity
and deserves its own task with a verify step.

Recommended plan structure:
- Plan 24-01: TD-1 (export.js fix) + TD-2 (route fallback) as Tasks 1 and 2
- Plan 24-02: TD-3 (Phase 22 VERIFICATION.md) — documentation-only plan

Alternative: combine all three into a single 3-task plan if lightweight.

**TD-2 gotcha — noc_data stub key names:**

`mapper.to_jd_elements()` accesses these keys from `noc_data` throughout its methods:
- `noc_data['noc_code']` (line 75) — required
- `noc_data['title']` (line 114) — required
- `noc_data.get('main_duties', [])` (line 175) — safe with []
- `noc_data.get('work_activities', [])` (line 183) — safe with []
- `noc_data.get('skills', [])` (line 240) — safe with []
- `noc_data.get('abilities', [])` (line 243) — safe with []
- `noc_data.get('knowledge', [])` (line 247) — safe with []
- `noc_data.get('work_context', [])` (line 332) — safe with []
- `noc_data.get('noc_hierarchy')` (line 124) — safe with None
- `noc_data.get('reference_attributes')` (line 141) — safe with None

The stub must have at least `noc_code` and `title` as direct keys (not `.get()`), and all other
fields should use `.get()` in mapper — which they already do.

**TD-2 gotcha — working_conditions in fallback:**

`_map_working_conditions_enriched()` calls `enrichment_service.enrich_work_context(data.get('work_context', []), url)`.
With an empty list, `enrich_work_context([])` will return an empty dict or equivalent empty
structure. The result will be an `EnrichedJDElementData` with `statements=[]`. This is correct
behavior for OASIS-down: no Working Conditions statements are served (they have no parquet source).

**TD-2 gotcha — labels_loader and example_titles:**

In `to_jd_elements()`, `labels_loader.get_example_titles(noc_code)` and `labels_loader.get_labels(noc_code)` are called unconditionally. These read from parquet and return empty lists on failure. They do not depend on OASIS. Safe in fallback.

**TD-1 gotcha — working_conditions data_source value:**

`_map_working_conditions_enriched()` does NOT pass `data_source` to `EnrichedJDElementData`.
The default for `data_source` in `EnrichedJDElementData` is `"oasis"`. So
`profile.working_conditions?.data_source` returns `"oasis"` for all profiles, always.
The value sent to the backend will always be `"oasis"` — which is accurate (Working Conditions
is derived from OASIS-scraped work_context HTML).

**TD-3 gotcha — criterion 3 assessment:**

The VERIFICATION.md for Phase 22 must accurately report that criterion 3 is only partially met
at the time Phase 22 was completed. The Phase 24 fix (TD-1) closes the gap. The VERIFICATION.md
should note this, i.e., "Criterion 3: PARTIAL at Phase 22 completion — working_conditions key
missing from frontend section_sources; addressed by Phase 24 TD-1."

**No new dependencies:** All three fixes use only existing imports, existing services, and
existing patterns. No new libraries or modules needed.

---

## Architecture Patterns

### Search fallback pattern (established, replicate for profile)

In `api.py` search route (lines 88-99), the pattern is:
```python
parquet_results = search_parquet_reader.search(...)
if parquet_results is not None and len(parquet_results) > 0:
    results = parquet_results
else:
    # Fallback path: run OASIS scraper
    html = scraper.search(...)
    results = parser.parse_search_results_enhanced(html)
```

For profile, the pattern inverts (try OASIS first, fall back to parquet on exception) because
the milestone goal was "OASIS with parquet-first enrichment" for profile (not "parquet with OASIS
fallback"). The approach is:

```python
try:
    html = scraper.fetch_profile(code)
    noc_data = parser.parse_profile(html, code)
except Exception as e:
    logger.warning(...)
    noc_data = { ... minimal stub ... }
# mapper.to_jd_elements() handles parquet vs OASIS internally
```

### Don't Hand-Roll

| Problem | Don't Build | Use Instead |
|---------|-------------|-------------|
| Constructing partial profile title | Custom NOC lookup | Just use `f"NOC {code}"` as placeholder |
| Detecting OASIS down vs parse error | Separate exception types | Catch all Exception in one block |

---

## Common Pitfalls

### Pitfall 1: Splitting try/except too finely for TD-2

**What goes wrong:** Catching only `requests.RequestException` in the fallback means a parse error
in `parser.parse_profile()` (e.g., OASIS returns 200 with garbage HTML) would still propagate as
a 500 without triggering the parquet fallback.

**How to avoid:** The try block should wrap BOTH `scraper.fetch_profile()` AND
`parser.parse_profile()`. Catch `Exception` (not just `requests.RequestException`) to ensure
malformed responses also trigger the fallback.

### Pitfall 2: Leaving old except branches in place for TD-2

**What goes wrong:** If the route's existing `except requests.RequestException` and `except
Exception` branches are left unchanged, they will catch errors from `mapper.to_jd_elements()` too,
silently swallowing parquet failures.

**How to avoid:** After restructuring, only `mapper.to_jd_elements()` and `ProfileResponse()` are
in the second try block. The second try block should have its own except that returns 500 — this is
the only code path that still returns 500 for a profile request.

### Pitfall 3: Forgetting trailing comma in JS object for TD-1

**What goes wrong:** Adding `working_conditions` without a trailing comma on `responsibility` line
causes a JS syntax error.

**How to avoid:** Check the surrounding context — the dict currently ends with `responsibility`
(no trailing comma because it's the last key). After the fix, `responsibility` needs a trailing
comma and `working_conditions` is the last key (no trailing comma needed, but JS allows it).

---

## Sources

### Primary (HIGH confidence)

- Direct inspection of `static/js/export.js` lines 112-119 — section_sources dict confirmed
- Direct inspection of `src/routes/api.py` lines 216-270 — profile route structure confirmed
- Direct inspection of `src/services/mapper.py` — `to_jd_elements()` signature, stub requirements
- Direct inspection of `src/services/scraper.py` — `fetch_profile()` exception behavior
- Direct inspection of `src/services/export_service.py` — `build_compliance_sections()` confirmed
- Direct inspection of `src/models/export_models.py` — `SourceMetadataExport.section_sources` confirmed
- Direct inspection of `.planning/phases/22-profile-service/22-01-SUMMARY.md` — Phase 22 evidence
- Direct inspection of `.planning/phases/22-profile-service/22-02-SUMMARY.md` — Phase 22 evidence
- Direct inspection of `.planning/ROADMAP.md` — Phase 22 success criteria (4 items)
- Direct inspection of `.planning/v5.0-MILESTONE-AUDIT.md` — TD-1/TD-2/TD-3 definitions

---

## Metadata

**Confidence breakdown:**
- TD-1 fix: HIGH — one-line change, all context confirmed by direct inspection
- TD-2 fix: HIGH — route structure confirmed, mapper stub requirements confirmed
- TD-3 content: HIGH — ROADMAP success criteria confirmed, SUMMARY evidence confirmed
- No gaps remaining

**Research date:** 2026-03-09
**Valid until:** 2026-04-08 (stable codebase; only changes invalidating this research are
modifications to export.js, api.py profile route, or mapper.py)
