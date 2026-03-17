# Phase 31: Export Completeness & Reset Crash Fix - Research

**Researched:** 2026-03-17
**Domain:** JavaScript state management + export payload construction (no new libraries)
**Confidence:** HIGH — all findings sourced directly from reading the actual codebase files

---

## Summary

Phase 31 closes two confirmed bugs documented in `v5.1-MILESTONE-AUDIT.md`. Both bugs exist
in JavaScript files only — no Python backend changes are required. The root causes are fully
understood from the audit; this research confirms the exact code locations and the minimal,
safe fixes needed.

**Bug 1 — `store.reset()` crash:** `main.js` line 112 calls `store.reset()`, but `state.js`
exports only `getState`, `subscribe`, `setState`, `setSelections`, and `notify`. There is no
`reset` method. The fix is to add a `reset()` method to the `createStore` factory in `state.js`
that calls `store.setState(defaultState)` and also clears the localStorage key
(`STORAGE_KEY = 'jdBuilderState'`). `defaultState` is already declared at module scope and is
accessible. Alternatively, `main.js` can be changed to call
`store.setState(defaultState)` directly, but adding `reset()` to the store is cleaner and
matches the intent of the calling code.

**Bug 2 — `buildExportRequest()` drops 3 sections:** `export.js` `buildExportRequest()`
iterates `Object.entries(state.selections)` and does
`profile[sectionId].statements` for every section. Three sections live in non-standard
locations in the profile object: `core_competencies` is at
`profile.reference_attributes.core_competencies[]` (array of plain strings, not objects with
`.text`); `abilities` and `knowledge` are inside `profile.skills.statements[]` filtered by
`source_attribute === 'Abilities'` or `'Knowledge'`. The fix adds special-case handling
identical to the pattern already used in `assembleJDPreview()` (lines 518–533 of export.js)
and in `sidebar.js` (lines 93–108). No backend changes needed — the backend receives the
selections as a flat list of `SelectionMetadata` objects and works correctly with any
`jd_element` value.

**Primary recommendation:** Two surgical edits: add `reset()` to `state.js` store;
add three-section special-case to `buildExportRequest()` in `export.js`. Both are 10-15
line changes with no architectural impact.

---

## Standard Stack

This phase uses no new libraries. The existing stack is:

### Core (already in use)
| Component | Location | Purpose |
|-----------|----------|---------|
| `state.js` | `static/js/state.js` | Reactive store with localStorage persistence |
| `export.js` | `static/js/export.js` | Export request builder and download handlers |
| `main.js` | `static/js/main.js` | App init, Reset Session button handler |
| `api.py` | `src/routes/api.py` | `/api/export/pdf|docx|json` endpoints |
| `export_service.py` | `src/services/export_service.py` | ExportData builder (backend) |

No new npm packages, Python packages, or CDN resources needed.

---

## Architecture Patterns

### Pattern 1: Store Reset via setState(defaultState)

The `createStore` factory in `state.js` already has `setState` that does a shallow merge and
calls `notify()` which persists to localStorage. A `reset()` method should call
`setState(defaultState)` AND explicitly remove the localStorage key so the persisted state is
fully erased (otherwise the next page load would restore the old state).

```javascript
// Source: state.js (lines 3-43) — existing createStore pattern
// Add this inside the returned object from createStore():
reset: () => {
    state = { ...defaultState };  // reset in-memory state
    try {
        localStorage.removeItem(STORAGE_KEY);  // wipe persisted state
    } catch (e) {
        console.warn('localStorage remove failed:', e);
    }
    listeners.forEach(fn => fn(state));  // notify listeners
},
```

Note: `STORAGE_KEY` is `'jdBuilderState'` (defined at line 2 of state.js). It is in scope
inside `createStore` because `createStore` is called in the same file after `STORAGE_KEY` is
declared. `defaultState` is also module-scope, defined at line 58, and accessible at call
time.

### Pattern 2: Three-Section Special-Case in buildExportRequest()

The existing `buildExportRequest()` loop (export.js lines 58-80) does:

```javascript
// CURRENT CODE (broken for 3 sections):
Object.entries(state.selections).forEach(([sectionId, selectedIds]) => {
    const sectionData = profile[sectionId];
    if (!sectionData || !sectionData.statements) return;  // silent skip

    selectedIds.forEach(stmtId => {
        const index = parseInt(stmtId.split('-').pop(), 10);
        const stmt = sectionData.statements[index];
        // ...push to selections
    });
});
```

The fix replicates the pattern from `assembleJDPreview()` (export.js lines 514-533) and
`sidebar.js` (lines 93-108), which both correctly handle the three special sections:

```javascript
// Source: export.js assembleJDPreview() lines 518-533 — verified pattern
// FIX: Replace the inner block for the 3 special sections:
selectedIds.forEach(stmtId => {
    const index = parseInt(stmtId.split('-').pop(), 10);
    let text = '';
    let sourceAttribute = '';

    if (sectionId === 'core_competencies') {
        // core_competencies: plain strings in profile.reference_attributes.core_competencies[]
        const ccItems = profile.reference_attributes?.core_competencies || [];
        text = ccItems[index] || '';
        sourceAttribute = 'Core Competencies';
    } else if (sectionId === 'abilities') {
        // abilities: filter profile.skills.statements by source_attribute === 'Abilities'
        const filtered = (profile.skills?.statements || [])
            .filter(s => s.source_attribute === 'Abilities');
        const stmt = filtered[index];
        text = stmt?.text || '';
        sourceAttribute = stmt?.source_attribute || 'Abilities';
    } else if (sectionId === 'knowledge') {
        // knowledge: filter profile.skills.statements by source_attribute === 'Knowledge'
        const filtered = (profile.skills?.statements || [])
            .filter(s => s.source_attribute === 'Knowledge');
        const stmt = filtered[index];
        text = stmt?.text || '';
        sourceAttribute = stmt?.source_attribute || 'Knowledge';
    } else {
        // Standard path: profile[sectionId].statements[index]
        const sectionData = profile[sectionId];
        if (!sectionData || !sectionData.statements) return;
        const stmt = sectionData.statements[index];
        if (!stmt) return;
        text = stmt.text;
        sourceAttribute = stmt.source_attribute;
        // continue building selection with stmt.source_url, stmt.description, stmt.proficiency
    }

    if (text) {
        selections.push({
            id: stmtId,
            text: text,
            jd_element: sectionId,
            source_attribute: sourceAttribute,
            source_url: null,  // core_competencies/abilities/knowledge have no source_url
            selected_at: state.selectionTimestamps?.[stmtId] || now,
            description: null,
            proficiency: null
        });
    }
});
```

### Recommended Project Structure (unchanged)

No new files are needed. Both fixes go in existing files:

```
static/js/
├── state.js          CHANGE: add reset() method to createStore return object
├── export.js         CHANGE: fix buildExportRequest() special-case for 3 sections
└── main.js           NO CHANGE: already calls store.reset() and window.location.reload()
```

### Anti-Patterns to Avoid

- **Removing `store.reset()` call from main.js instead of adding it to state.js:** The calling
  code is correct. The fix belongs in state.js, not by removing the call.
- **Using `store.setState(defaultState)` without removing the localStorage key:** The state
  persists to localStorage on every `notify()`. If you only call `setState`, the persisted
  key still exists and will restore the old state on next page load. You must also call
  `localStorage.removeItem(STORAGE_KEY)` (or equivalent).
- **Modifying `JD_ELEMENT_ORDER` in export_service.py to include core_competencies/abilities/knowledge:**
  The backend already handles these correctly — they arrive as `SelectionMetadata` objects
  with `jd_element = 'core_competencies'` etc., and `manager_selections` (used for
  core_competencies) is separate from `jd_elements`. No backend change is needed.
- **Trying to add a `working_conditions` special case:** `working_conditions` is in
  `state.selections` (defaultState) but is in `profile.working_conditions.statements` just
  like skills/effort/responsibility — the standard path handles it. It is already in
  `JD_ELEMENT_ORDER` in export_service.py. No special case needed.

---

## Don't Hand-Roll

No problems here require external solutions. All needed patterns already exist within the
codebase.

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Text lookup for 3 special sections | New utility function | Copy the pattern from `assembleJDPreview()` | Pattern already verified working in preview |
| State reset | Custom localStorage clearing logic | `store.reset()` calling `setState(defaultState)` + `localStorage.removeItem(STORAGE_KEY)` | Keeps reset logic co-located with store |

---

## Common Pitfalls

### Pitfall 1: `defaultState` not accessible inside `createStore` at call time

**What goes wrong:** Referencing `defaultState` inside the `reset()` closure when `defaultState`
is defined after `createStore` is called.
**Why it happens:** In `state.js`, `createStore` is defined first (lines 4-43), then called
immediately as `const store = createStore(initialState)` (line 78). `defaultState` is
defined at line 58, which is between the function definition and its invocation, so it IS
in scope at call time.
**How to avoid:** Verify the line order: `createStore` defined → `defaultState` defined →
`store = createStore(initialState)` called. The `reset()` closure captures `defaultState`
from the enclosing module scope, which is fine.
**Warning signs:** `ReferenceError: defaultState is not defined` at runtime.

### Pitfall 2: `core_competencies` index vs. raw array

**What goes wrong:** Using `profile.reference_attributes.core_competencies[index]` where
`index` is parsed from the stmtId suffix — but confusing whether the index is into the raw
array or some other derived list.
**Why it happens:** For core_competencies, the stmtId is `core_competencies-0`,
`core_competencies-1`, etc., and the index directly maps to `profile.reference_attributes.core_competencies[index]`. This is a plain string, not an object with `.text`.
**How to avoid:** Confirmed in `assembleJDPreview()` line 520: `text = ccItems[index] || ''`
where `ccItems = profile.reference_attributes?.core_competencies || []`. Replicate exactly.
**Warning signs:** `undefined` for text, or trying to do `.text` on a string.

### Pitfall 3: `abilities`/`knowledge` index into filtered array, not full skills array

**What goes wrong:** Indexing into `profile.skills.statements[index]` without filtering,
which gives the wrong statement.
**Why it happens:** The stmtId for abilities is `abilities-0`, `abilities-1`, etc., where 0
and 1 are positions in the **filtered** array (statements where `source_attribute === 'Abilities'`),
not the full `profile.skills.statements` array.
**How to avoid:** Filter first: `const filtered = profile.skills.statements.filter(s => s.source_attribute === 'Abilities')`, then `filtered[index]`. Confirmed in `assembleJDPreview()`
lines 524-527 and `sidebar.js` lines 99-101.
**Warning signs:** Getting a Skills statement where an Abilities statement is expected.

### Pitfall 4: `source_attribute` value for core_competencies selections

**What goes wrong:** Sending `source_attribute: undefined` or `source_attribute: 'core_competencies'` instead of `'Core Competencies'`.
**Why it happens:** `core_competencies` items are plain strings with no `.source_attribute`
property. You must hardcode `'Core Competencies'`.
**How to avoid:** Always set `source_attribute = 'Core Competencies'` for core_competencies
items. This matches `SOURCE_TAG_MAP['Core Competencies'] = '[GC]'` in both
`pdf_generator.py` and `docx_generator.py`.
**Warning signs:** Source tag shows as `[NOC]` (the default) instead of `[GC]` in the PDF.

### Pitfall 5: Reset only clears `localStorage.removeItem('jdb_session_id')` + `'classification_cache'` but misses `'jdBuilderState'`

**What goes wrong:** `main.js` lines 110-111 already removes `jdb_session_id` and
`classification_cache`. If `store.reset()` does not also remove `'jdBuilderState'`, the app
state (selections, profile code, etc.) persists to the next page load from localStorage.
**Why it happens:** `state.js` persists to `STORAGE_KEY = 'jdBuilderState'` on every
`notify()`. If `reset()` doesn't clear this key, the next `loadPersistedState()` call
restores the old state.
**How to avoid:** `store.reset()` must call `localStorage.removeItem('jdBuilderState')` (or
reference `STORAGE_KEY`). The `window.location.reload()` in `main.js` will then get a clean
state.
**Warning signs:** After reset + reload, the same selections appear restored.

### Pitfall 6: Breaking the `source_url` and `proficiency` fields for standard sections

**What goes wrong:** When refactoring `buildExportRequest()`, accidentally removing
`source_url`, `description`, and `proficiency` from the standard-path selections.
**Why it happens:** The standard path reads these from `stmt` (the statement object). If you
restructure the loop and forget to carry these fields through, existing exports lose
provenance data.
**How to avoid:** Keep the standard path's `stmt.source_url`, `stmt.description`, and
`stmt.proficiency` assignments intact. Only the three special sections (core_competencies,
abilities, knowledge) get `null` for these optional fields because they lack them.

---

## Code Examples

All patterns sourced directly from the codebase files.

### How `assembleJDPreview()` already handles the three sections (verified working)

```javascript
// Source: static/js/export.js, lines 518-533
// PITFALL: core_competencies items are plain strings in profile.reference_attributes.core_competencies[idx]
if (key === 'core_competencies') {
    const ccItems = profile.reference_attributes?.core_competencies || [];
    text = ccItems[index] || '';
}
// PITFALL: abilities/knowledge use filtered sub-arrays by source_attribute
else if (key === 'abilities' || key === 'knowledge') {
    const sourceAttr = key === 'abilities' ? 'Abilities' : 'Knowledge';
    const filtered = (profile.skills?.statements || []).filter(s => s.source_attribute === sourceAttr);
    text = filtered[index]?.text || '';
} else {
    const sectionData = profile[key];
    if (sectionData?.statements?.[index]) {
        text = sectionData.statements[index].text;
    }
}
```

### How sidebar.js already handles the three sections (verified working)

```javascript
// Source: static/js/sidebar.js, lines 93-108
// PITFALL: core_competencies uses profile.reference_attributes.core_competencies[idx]
if (sectionId === 'core_competencies') {
    const ccItems = profile.reference_attributes?.core_competencies || [];
    text = ccItems[index] || '';
}
// PITFALL: abilities/knowledge use filtered sub-array by source_attribute
else if (sectionId === 'abilities' || sectionId === 'knowledge') {
    const sourceAttr = sectionId === 'abilities' ? 'Abilities' : 'Knowledge';
    const filtered = (profile.skills?.statements || []).filter(s => s.source_attribute === sourceAttr);
    text = filtered[index]?.text || '';
} else {
    const sectionData = profile[sectionId];
    if (sectionData?.statements?.[index]) {
        text = sectionData.statements[index].text;
    }
}
```

### How the backend (export_service.py) handles core_competencies in PDF/DOCX

```python
# Source: src/services/export_service.py, lines 86-110 and src/services/pdf_generator.py lines 293-338
# core_competencies arrive as SelectionMetadata objects with jd_element='core_competencies'
# They are collected in data.manager_selections (not data.jd_elements)
# pdf_generator.py uses:
cc_sels = [
    s_item
    for s_item in data.manager_selections
    if s_item.jd_element == "core_competencies"
]
if cc_sels:
    story.append(Paragraph("Core Competencies", s["sub_heading"]))
    for sel in cc_sels:
        story.append(Paragraph(f"• {sel.text}", s["bullet"]))
```

```python
# For abilities/knowledge in PDF: they arrive as part of the 'skills' JDElementExport
# (because their jd_element == 'skills' in the payload — wait, see critical note below)
```

**CRITICAL FINDING on abilities/knowledge jd_element value:**

The audit says abilities/knowledge come from `profile.skills.statements` filtered by
`source_attribute`. The stmtId is `abilities-0`. But what `jd_element` value should be set
in the export payload?

Looking at `pdf_generator.py` lines 314-332:
```python
# Source: src/services/pdf_generator.py lines 293-332
skills_el = elements_by_key.get("skills")
# ...
ability_stmts = [
    st for st in skills_el.statements
    if st.source_attribute == "Abilities"
]
if ability_stmts:
    story.append(Paragraph("Abilities", s["sub_heading"]))
    for stmt in ability_stmts:
        story.append(Paragraph(f"• {stmt.text}", s["bullet"]))
```

And in `export_service.py` lines 87-111:
```python
# JD_ELEMENT_ORDER = ["key_activities", "skills", "effort", "responsibility", "working_conditions"]
# selections_by_element is keyed by selection.jd_element
# skills elements are rendered from selections_by_element["skills"]
```

This means: **abilities and knowledge selections must be pushed with `jd_element: 'skills'`
(not `jd_element: 'abilities'`)**. The backend groups them into `elements_by_key['skills']`
and then filters by `source_attribute === 'Abilities'` or `'Knowledge'` to render them under
their sub-headings.

Confirmed by looking at how `export_service.py` builds `jd_elements`:
```python
for key in JD_ELEMENT_ORDER:  # includes 'skills'
    if key in selections_by_element:
        jd_elements.append(JDElementExport(
            name=JD_ELEMENT_LABELS[key],
            key=key,
            statements=selections_by_element[key]  # abilities+knowledge+skills all land here
        ))
```

So the correct export payload construction for abilities/knowledge:
- `jd_element: 'skills'` (not 'abilities' or 'knowledge')
- `source_attribute: 'Abilities'` or `'Knowledge'`
- `id: stmtId` (can remain `'abilities-0'` etc. — the id field is just for audit trail)

For `core_competencies`:
- `jd_element: 'core_competencies'`
- `source_attribute: 'Core Competencies'`
- (Backend collects from `data.manager_selections`, not `data.jd_elements`)

### Store reset() method

```javascript
// Source: static/js/state.js — createStore return object pattern (lines 18-42)
// Add reset() to the return object:
reset: () => {
    state = { ...defaultState };
    try {
        localStorage.removeItem(STORAGE_KEY);
    } catch (e) {
        console.warn('localStorage remove failed:', e);
    }
    listeners.forEach(fn => fn(state));
},
```

---

## State of the Art

| Old Approach | Current Approach | Notes |
|--------------|------------------|-------|
| N/A — these are bugs, not old approaches | Add `reset()` to store; fix `buildExportRequest()` | Minimal targeted fixes |

---

## Open Questions

1. **Should `jd_element` for abilities/knowledge be `'skills'` or `'abilities'`/`'knowledge'`?**
   - What we know: `export_service.py` builds `jd_elements` from `JD_ELEMENT_ORDER = ["key_activities", "skills", ...]`. If `jd_element` is `'abilities'`, the selection goes into `selections_by_element['abilities']` which is never in `JD_ELEMENT_ORDER`, so it won't appear in `jd_elements`. It will only appear in `manager_selections` (the compliance audit trail), but NOT in the "Qualifications and Requirements" section body.
   - What's unclear: Whether to set `jd_element: 'skills'` (gets into PDF body) vs `'abilities'` (only in audit trail). Looking at the success criteria: "Downloaded PDF includes Abilities sub-section populated with user selections" — so it must reach the PDF body.
   - **Recommendation:** Set `jd_element: 'skills'` for both abilities and knowledge. This matches how `pdf_generator.py` and `docx_generator.py` already expect to find them (inside `skills_el.statements` filtered by `source_attribute`). Confirmed by reading the generators: `ability_stmts = [st for st in skills_el.statements if st.source_attribute == "Abilities"]`.

2. **Does `JD_ELEMENT_LABELS` in export_service.py need updating for abilities/knowledge?**
   - What we know: `JD_ELEMENT_LABELS = {"key_activities": ..., "skills": "Skills", ...}`. If abilities/knowledge selections arrive with `jd_element: 'skills'`, they join the existing `skills` element. The label stays "Skills" but the sub-heading comes from `source_attribute` filtering in the generators.
   - Recommendation: No change to `JD_ELEMENT_LABELS`. The generators already produce "Abilities" and "Knowledge" sub-headings via the `source_attribute` filter pattern.

---

## Sources

### Primary (HIGH confidence)
- Direct read of `static/js/state.js` — complete file, confirmed no `reset()` method
- Direct read of `static/js/export.js` — confirmed `buildExportRequest()` gap (lines 58-80), and the working pattern in `assembleJDPreview()` (lines 514-533)
- Direct read of `static/js/main.js` — confirmed `store.reset()` call at line 112
- Direct read of `static/js/sidebar.js` — confirmed working special-case pattern (lines 93-108)
- Direct read of `static/js/accordion.js` — confirmed abilities/knowledge use `filter(s => s.source_attribute === 'Abilities'/'Knowledge')` on `profile.skills.statements`
- Direct read of `src/services/pdf_generator.py` — confirmed abilities/knowledge rendered from `skills_el.statements` filtered by `source_attribute`
- Direct read of `src/services/docx_generator.py` — same pattern confirmed
- Direct read of `src/services/export_service.py` — confirmed `JD_ELEMENT_ORDER` and `selections_by_element` grouping logic
- Direct read of `src/models/noc.py` — confirmed `ReferenceAttributes.core_competencies: List[str]` (plain strings)
- Direct read of `.planning/v5.1-MILESTONE-AUDIT.md` — gaps confirmed and quoted

### Secondary (MEDIUM confidence)
- None needed — all findings come from direct code inspection

### Tertiary (LOW confidence)
- None

---

## Metadata

**Confidence breakdown:**
- Bug root causes: HIGH — confirmed by reading every relevant file
- Fix approach (state.js reset): HIGH — pattern is straightforward, `defaultState` in scope
- Fix approach (buildExportRequest): HIGH — exact pattern already exists in `assembleJDPreview()` and `sidebar.js`
- `jd_element` value for abilities/knowledge: HIGH — confirmed by tracing `export_service.py` JD_ELEMENT_ORDER and `pdf_generator.py` filter logic
- Backend impact: HIGH — confirmed no backend changes needed

**Research date:** 2026-03-17
**Valid until:** Stable — findings are based on reading actual code, not external docs
