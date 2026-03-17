---
phase: 30-export-page-pdf-docx-json
plan: 03
subsystem: export
tags: [json, audit-trail, export, flask, javascript, fetch, blob-download]

# Dependency graph
requires:
  - phase: 30-01
    provides: Export page Step 5 HTML/CSS/JS — initExportPage(), download buttons wired
  - phase: 30-02
    provides: PDF/DOCX generation with reportlab; ExportRequest/ExportData models; build_export_data()

provides:
  - POST /api/export/json endpoint returning structured JSON audit trail as file download
  - exportModule.downloadJSON() in export.js POSTing to /api/export/json and triggering blob download
  - Audit trail JSON containing: generated_at, noc_code, job_title, general_overview, source_metadata, selections (full metadata), ai_metadata, classification_result, compliance_sections

affects:
  - any future export format work
  - compliance/provenance audit tooling

# Tech tracking
tech-stack:
  added: []
  patterns:
    - json.dumps() with default=str for datetime serialization in audit export
    - Server sets Content-Disposition filename; client extracts via regex or falls back to _generateFilename()
    - Blob download pattern: fetch -> response.blob() -> URL.createObjectURL() -> anchor click -> revokeObjectURL()

key-files:
  created: []
  modified:
    - src/routes/api.py
    - static/js/export.js

key-decisions:
  - "export_options metadata recorded in JSON payload instead of filtering content — all session data always exported; checkbox state captured as metadata only"
  - "json always includes everything regardless of checkboxes — audit trail is authoritative, complete record"
  - "Filename convention: {NOC code} - {Title} - {date} - Audit Trail.json (not Job Description)"

patterns-established:
  - "JSON audit trail structure mirrors ExportData model: generated_at, noc_code, job_title, general_overview, source_metadata, selections[], ai_metadata, classification_result, compliance_sections[]"
  - "datetime fields serialized via .isoformat(); json_lib.dumps default=str as safety net"
  - "downloadJSON() uses same fetch/blob/_downloadBlob pattern as downloadPDF/downloadDOCX; btn disabled during generation"

# Metrics
duration: 3min
completed: 2026-03-17
---

# Phase 30 Plan 03: JSON Audit Trail Export Summary

**POST /api/export/json endpoint + exportModule.downloadJSON() delivering complete machine-readable compliance audit trail with all session data, provenance metadata, AI generation info, and classification result as a dated JSON file download**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-17T15:12:36Z
- **Completed:** 2026-03-17T15:15:00Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- Added POST /api/export/json route to api.py following the same ExportRequest pattern as /export/pdf and /export/docx
- JSON payload includes all session fields: generated_at, noc_code, job_title, general_overview, source_metadata (with section_sources), full selections array (id, text, jd_element, source_attribute, selected_at, description, proficiency, publication_date, source_table_url), ai_metadata (when present), classification_result, compliance_sections
- Filename follows convention: `{NOC code} - {Title} - {date} - Audit Trail.json`
- Added downloadJSON() to exportModule in export.js following the same fetch/blob/_downloadBlob pattern as downloadPDF/downloadDOCX
- export-download-json button already wired in initExport() from plan 30-01

## Task Commits

Both tasks were committed as part of prior plan executions (30-01 and 30-02). The implementations were verified correct and complete in HEAD:

1. **Task 1: Add /api/export/json to api.py** - `6b8c73d` (feat, committed as part of 30-02)
2. **Task 2: Add downloadJSON() to export.js** - `060acdf` (feat, committed as part of 30-01)

**Plan metadata:** (docs commit follows)

## Files Created/Modified

- `src/routes/api.py` - Added export_json() route at /api/export/json; builds full audit trail dict from ExportData, serializes with json.dumps, returns BytesIO as attachment with dated filename
- `static/js/export.js` - Added downloadJSON() method to exportModule; POSTs currentExportData to /api/export/json, extracts filename from Content-Disposition header, downloads via _downloadBlob()

## Decisions Made

- JSON always exports everything — checkbox state (include_provenance, include_audit) is recorded in the payload's export_options field but does not filter the content. The audit trail is meant to be a complete, authoritative record.
- compliance_sections array included alongside selections — these are the policy/DAMA/TBS compliance paragraphs assembled by build_export_data().
- datetime objects serialized via .isoformat() with json_lib.dumps(default=str) as a safety net for any non-serializable values.

## Deviations from Plan

None - plan executed exactly as written. Both tasks were already committed in HEAD as part of the 30-01 (downloadJSON in export.js) and 30-02 (export_json route in api.py) plan executions. Code verified against plan specification — all required fields present, filename convention correct, fetch/blob pattern correct.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- All three plans in phase 30 are complete: export page HTML/CSS/JS (30-01), PDF/DOCX generators (30-02), JSON audit trail (30-03)
- Export pipeline is fully functional: PDF via reportlab, DOCX via python-docx, JSON via stdlib json
- Phase 30 complete — v5.1 UI Overhaul milestone all 15/15 plans done
- No blockers for milestone sign-off

---
*Phase: 30-export-page-pdf-docx-json*
*Completed: 2026-03-17*
