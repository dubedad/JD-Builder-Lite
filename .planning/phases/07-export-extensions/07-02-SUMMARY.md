---
phase: 07-export-extensions
plan: 02
status: complete
completed_at: 2026-01-22
---

# 07-02 Summary: PDF Export with Annex Section

## What Was Built

### 1. Export Service Integration (`src/services/export_service.py`)

Updated `build_export_data()` to accept optional `raw_noc_data` parameter:
- Imports `build_annex_data` from annex_builder
- Builds AnnexData when raw NOC data provided
- Passes annex_data to ExportData

### 2. PDF Template Annex Section (`templates/export/jd_pdf.html`)

Added Annex section after compliance appendix:
- "Additional Job Information" heading
- Introductory paragraph
- 4 category sections with format-specific rendering:
  - `paragraph` for Job Requirements
  - `grouped_list` for Career Mobility (Entry/Advancement headers)
  - `list` for Interests and Personal Suitability
- Empty state handling: "No additional information available"
- Source attribution at end

### 3. Preview Template (`templates/export/jd_preview.html`)

Added matching Annex section so preview matches PDF output.

### 4. Print Styles (`static/css/export_print.css`)

Added Annex CSS:
- `.annex-section` with page break and named page
- `@page annex` with custom header
- Category headings with GC primary color (#26374a)
- Format-specific styles (paragraph, grouped list, bullet list)
- Source attribution styling

### 5. API Endpoints (`src/routes/api.py`)

Updated export endpoints to fetch raw NOC data:
- `preview()` - fetches NOC data for Annex in preview
- `export_pdf()` - fetches NOC data, updated filename format
- `export_docx()` - fetches NOC data, updated filename format

New filename format per CONTEXT.md:
```
{NOC code} - {Title} - {date} - Job Description.{ext}
Example: 72600 - Air Pilots - 2026-01-22 - Job Description.pdf
```

## Files Modified

| File | Change |
|------|--------|
| `src/services/export_service.py` | Added raw_noc_data param, annex_data building |
| `templates/export/jd_pdf.html` | Added Annex section HTML |
| `templates/export/jd_preview.html` | Added matching Annex section |
| `static/css/export_print.css` | Added Annex print styles |
| `src/routes/api.py` | Updated preview/export endpoints with NOC fetch |

## Verification

- Template syntax: OK
- CSS contains annex-section: OK
- All imports: OK
