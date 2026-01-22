---
phase: 04-output-compliance
plan: 01
subsystem: export
tags: [weasyprint, python-docx, pdf, docx, compliance, directive-32592]

# Dependency graph
requires:
  - phase: 03-llm-integration
    provides: AI metadata for compliance tracking
  - phase: 01-backend-scraping
    provides: Source metadata for provenance
provides:
  - Export Pydantic models (ExportRequest, ExportData, SelectionMetadata)
  - Export service with compliance section builder
  - PDF generator (WeasyPrint-based, needs templates)
  - DOCX generator (fully functional)
  - API endpoints (/api/preview, /api/export/pdf, /api/export/docx)
affects: [04-02-templates, frontend-export-ui]

# Tech tracking
tech-stack:
  added: [weasyprint==68.0, Flask-WeasyPrint==1.1.0, python-docx==1.2.0, GTK3-Runtime]
  patterns: [compliance-section-builder, directive-6.2.3, directive-6.2.7, directive-6.3.5]

key-files:
  created:
    - src/models/export_models.py
    - src/services/export_service.py
    - src/services/pdf_generator.py
    - src/services/docx_generator.py
  modified:
    - requirements.txt
    - src/routes/api.py

key-decisions:
  - "GTK3 Runtime installed via winget for WeasyPrint on Windows"
  - "Compliance sections reference TBS Directive 32592 sections 6.2.3, 6.2.7, 6.3.5"
  - "DOCX generator includes GC-styled header/footer with audit appendix"

patterns-established:
  - "Compliance section builder: structured metadata for each Directive section"
  - "Export data flow: ExportRequest -> build_export_data() -> generator -> bytes"
  - "Safe filename generation: alphanumeric + spaces/hyphens only, max 50 chars"

# Metrics
duration: 35min
completed: 2026-01-22
---

# Phase 4 Plan 1: Backend Export Infrastructure Summary

**Export service with WeasyPrint PDF generator, python-docx Word generator, and TBS Directive 32592 compliance sections**

## Performance

- **Duration:** 35 min
- **Started:** 2026-01-22T07:49:08Z
- **Completed:** 2026-01-22T08:24:11Z
- **Tasks:** 3
- **Files modified:** 6

## Accomplishments

- Installed export libraries (weasyprint, Flask-WeasyPrint, python-docx) with GTK3 runtime
- Created comprehensive Pydantic models for export data with compliance fields
- Built export service that organizes selections and constructs Directive-compliant metadata sections
- Implemented DOCX generator with GC styling (verified working - 38KB test document)
- Added three API endpoints: /api/preview, /api/export/pdf, /api/export/docx

## Task Commits

Each task was committed atomically:

1. **Task 1: Add dependencies and create export models** - `8e3d1c4` (feat)
2. **Task 2: Create export service and document generators** - `231c6f3` (feat)
3. **Task 3: Add export API endpoints** - `edbc8b7` (feat)

## Files Created/Modified

- `requirements.txt` - Added weasyprint, Flask-WeasyPrint, python-docx
- `src/models/export_models.py` - Pydantic models for export data and compliance
- `src/services/export_service.py` - build_export_data() and compliance section builder
- `src/services/pdf_generator.py` - WeasyPrint generate_pdf() and render_preview()
- `src/services/docx_generator.py` - python-docx generate_docx() with GC styling
- `src/routes/api.py` - Added /api/preview, /api/export/pdf, /api/export/docx

## Decisions Made

1. **GTK3 Runtime via winget** - WeasyPrint requires GTK3/Pango libraries on Windows. Installed `tschoonj.GTKForWindows` (3.24.31) via winget to resolve missing libgobject-2.0-0 error.

2. **Compliance section structure** - Built three Directive-referenced sections:
   - Section 6.2.3: Data Sources (NOC/OASIS provenance)
   - Section 6.2.7: Documented Decisions (manager selections with timestamps)
   - Section 6.3.5: Data Quality Validation (relevant, accurate, up-to-date)
   - AI Disclosure section (when AI-generated overview present)

3. **DOCX styling** - Government of Canada primary color (#26374a), centered header with job title/NOC code, footer with "Compliant with TBS Directive 32592", page break before compliance appendix.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Installed GTK3 Runtime for WeasyPrint**
- **Found during:** Task 1 (dependency verification)
- **Issue:** WeasyPrint failed to import: "cannot load library 'libgobject-2.0-0'"
- **Fix:** Installed GTK3 Runtime via `winget install tschoonj.GTKForWindows`
- **Files modified:** None (system-level installation)
- **Verification:** `python -c "from weasyprint import HTML; print('OK')"` succeeds
- **Committed in:** N/A (system dependency, not code change)

---

**Total deviations:** 1 auto-fixed (blocking)
**Impact on plan:** Required system dependency for WeasyPrint. Standard Windows setup.

## Issues Encountered

- PDF and preview endpoints require templates (export/jd_pdf.html, export/jd_preview.html) which will be created in Plan 02
- GLib-GIO warnings appear on Windows when importing WeasyPrint (cosmetic, not functional)

## User Setup Required

None - GTK3 Runtime was installed automatically. If deploying to a new Windows machine, GTK3 Runtime must be installed:
```
winget install tschoonj.GTKForWindows
```

## Next Phase Readiness

**Ready for Plan 02 (Export Templates):**
- All export infrastructure in place
- DOCX export fully functional
- PDF/Preview endpoints ready, awaiting Jinja2 templates
- Compliance sections will render correctly in templates

**Blockers:** None

---
*Phase: 04-output-compliance*
*Completed: 2026-01-22*
