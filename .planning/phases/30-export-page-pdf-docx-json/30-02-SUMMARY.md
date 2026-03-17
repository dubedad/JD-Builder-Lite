---
phase: 30-export-page-pdf-docx-json
plan: 02
subsystem: export
tags: [reportlab, pdf, docx, python-docx, python3.14, provenance]

# Dependency graph
requires:
  - phase: 30-01
    provides: Export page Step 5 HTML/CSS/JS — initExportPage(), download buttons wired
  - phase: 29-classification-restyle-generate-page
    provides: Classification result shape used in export appendix

provides:
  - reportlab==4.4.10 PDF generation replacing WeasyPrint (Python 3.14 compatible)
  - pdf_generator.py with 9-section Platypus story (header + 5 content + 3 appendices)
  - Colored source tags in PDF Key Duties ([NOC] purple, [OaSIS] teal/orange, [GC] green)
  - jd_pdf.html with correct source tag mapping for all 8 source attributes
  - docx_generator.py with module-level SOURCE_TAG_MAP and get_source_tag() matching PDF

affects:
  - 30-03: JSON export endpoint (also in phase 30)
  - any future PDF/DOCX work

# Tech tracking
tech-stack:
  added:
    - reportlab==4.4.10
  patterns:
    - reportlab Platypus story pattern: build list of Flowables then doc.build(story)
    - Source tag constants at module level shared across pdf_generator and docx_generator
    - generate_pdf() returns bytes; no base_url parameter (reportlab vs WeasyPrint)

key-files:
  created: []
  modified:
    - requirements.txt
    - src/services/pdf_generator.py
    - src/services/docx_generator.py
    - templates/export/jd_pdf.html
    - src/routes/api.py

key-decisions:
  - "reportlab over WeasyPrint — WeasyPrint has no Python 3.14 wheels; reportlab 4.4.10 installs cleanly"
  - "generate_pdf() drops base_url parameter — WeasyPrint needed it for CSS resolution; reportlab does not"
  - "SOURCE_TAG_MAP lives at module level in both pdf_generator.py and docx_generator.py — same map, same source of truth"
  - "jd_pdf.html kept as browser preview reference — reportlab generates the actual PDF bytes"

patterns-established:
  - "PDF sections: Position Overview, Key Duties (colored tags), Qualifications (4 sub), Effort, Responsibilities, Appendix A/B/C"
  - "Source tag color coding: [NOC] purple #6f42c1, [OaSIS] teal #17a2b8, [GC] green #28a745, [JobForge] blue #007bff"
  - "Reportlab ParagraphStyle factory (_build_styles) returns named dict — doc_title, section_heading, sub_heading, appendix_heading, body, bullet, ai_note"

# Metrics
duration: 5min
completed: 2026-03-17
---

# Phase 30 Plan 02: PDF/DOCX Restructure Summary

**Replaced WeasyPrint with reportlab 4.4.10 for Python 3.14-compatible PDF generation with 9-section Platypus story and colored source tags; aligned DOCX section structure to match**

## Performance

- **Duration:** 5 min
- **Started:** 2026-03-17T15:03:09Z
- **Completed:** 2026-03-17T15:08:15Z
- **Tasks:** 3
- **Files modified:** 5

## Accomplishments

- Removed WeasyPrint/Flask-WeasyPrint (no Python 3.14 wheels) and replaced with reportlab==4.4.10
- Rewrote pdf_generator.py using reportlab Platypus; 9-section document with colored inline source tags via `<font color>` XML markup
- Fixed api.py generate_pdf() call to drop the now-removed base_url parameter
- Extended jd_pdf.html source tag mapping to cover all 8 source attributes (Skills, Effort, Responsibility were missing)
- Added module-level SOURCE_TAG_MAP and get_source_tag() to docx_generator.py matching pdf_generator.py API

## Task Commits

Each task was committed atomically:

1. **Task 1: Add reportlab to requirements.txt and rewrite pdf_generator.py** - `6b8c73d` (feat)
2. **Task 2: Restructure jd_pdf.html template** - `ab19719` (feat)
3. **Task 3: Restructure docx_generator.py** - `f5760a6` (feat)

**Plan metadata:** (docs commit follows)

## Files Created/Modified

- `requirements.txt` - Replaced weasyprint==68.0 + Flask-WeasyPrint==1.1.0 with reportlab==4.4.10
- `src/services/pdf_generator.py` - Complete rewrite using reportlab Platypus; 9-section story; no WeasyPrint
- `src/services/docx_generator.py` - Added module-level SOURCE_TAG_MAP + get_source_tag(); inline dict removed
- `templates/export/jd_pdf.html` - Fixed source tag mapping: added OaSIS for Skills/Abilities/Knowledge/Effort/Responsibility, GC for Core Competencies
- `src/routes/api.py` - Removed base_url argument from generate_pdf() call

## Decisions Made

- reportlab chosen over WeasyPrint because WeasyPrint has no Python 3.14 wheels and requires system libraries (pango/cairo) that are often unavailable in CI/deployment environments; reportlab 4.4.10 is pure Python and installs cleanly.
- generate_pdf() signature changed: `base_url` parameter removed since reportlab does not resolve CSS from URLs. api.py updated accordingly (Rule 3 deviation).
- SOURCE_TAG_MAP placed at module level in both pdf_generator.py and docx_generator.py to keep a shared canonical mapping — avoids drift between PDF and DOCX output.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Updated api.py generate_pdf() call to drop base_url**
- **Found during:** Task 1 (rewriting pdf_generator.py)
- **Issue:** api.py called `generate_pdf(export_data, request.url_root)` — the old WeasyPrint signature. The new reportlab signature has no base_url parameter; calling with positional arg would TypeError.
- **Fix:** Changed call to `generate_pdf(export_data)` in src/routes/api.py
- **Files modified:** src/routes/api.py
- **Verification:** PYTHONPATH=. python3 import test passes; no TypeError
- **Committed in:** 6b8c73d (Task 1 commit)

**2. [Rule 1 - Bug] Fixed incomplete source tag mapping in jd_pdf.html**
- **Found during:** Task 2 (reviewing template)
- **Issue:** Key Duties source tag logic only handled 'Main Duties' -> [NOC] and 'Work Activities' -> [OaSIS]; all other attributes fell through to [NOC] — incorrect for Skills, Abilities, Knowledge, Effort, Responsibility ([OaSIS]) and Core Competencies ([GC]).
- **Fix:** Extended Jinja if/elif chain to cover all 8 source attributes.
- **Files modified:** templates/export/jd_pdf.html
- **Verification:** grep confirms correct tag mapping for all source attributes
- **Committed in:** ab19719 (Task 2 commit)

---

**Total deviations:** 2 auto-fixed (1 blocking, 1 bug)
**Impact on plan:** Both fixes essential for correctness. No scope creep.

## Issues Encountered

None beyond the auto-fixed deviations documented above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- PDF export: generate_pdf() ready; reportlab renders all 9 sections with source tags
- DOCX export: generate_docx() ready; section structure matches PDF; source tag mapping complete
- 30-03 (JSON export endpoint) can proceed immediately — no dependencies on this plan's changes
- Requirements.txt is clean for Python 3.14 (no WeasyPrint, no Flask-WeasyPrint)

---
*Phase: 30-export-page-pdf-docx-json*
*Completed: 2026-03-17*
