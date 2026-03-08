---
phase: 22-profile-service
plan: 02
status: complete
completed: 2026-03-08
---

# Plan 22-02 Summary: Source Badges + Export Provenance

## What Was Built

### Task 1: Source Badge UI
- Added `.source-badge`, `.source-badge--jobforge` (green), `.source-badge--oasis` (grey) CSS classes to `static/css/main.css`
- Added `renderSourceBadge()` function to `static/js/accordion.js`
- Injected source badge at the bottom of all 6 statement tabs (Skills, Abilities, Knowledge, Key Activities, Effort, Responsibility)
- Key Activities badge includes hover tooltip: "Main Duties always served from OASIS (ETL pending)"
- Overview and Core Competencies tabs have no badge (correct — composite view and OASIS-only respectively)

### Task 2: Export Provenance Extension
- Added `section_sources: Optional[dict[str, str]] = None` to `SourceMetadataExport` in `src/models/export_models.py`
- Extended `build_compliance_sections()` in `src/services/export_service.py` to include per-section provenance in Section 6.2.3 when `section_sources` is present
- `access_method` text updated to reflect both OASIS and JobForge when section_sources present
- Backward compatible: existing exports without `section_sources` continue to work

## Commits

| Commit | What |
|--------|------|
| `fb3e398` | Source badge CSS + renderSourceBadge() in accordion.js |
| `9befc12` | SourceMetadataExport.section_sources + export_service provenance extension |

## Verification

User verified in browser (2026-03-08):
- Skills, Abilities, Knowledge, Effort, Responsibility tabs: green "Source: JobForge" badge ✓
- Key Activities tab: grey "Source: OASIS" badge with tooltip ✓
- Overview, Core Competencies: no badge ✓
- Badges visually distinct (green vs grey) ✓

## Locked Decisions Honoured

- Badge text: exactly "Source: JobForge" and "Source: OASIS"
- Badge placement: bottom of tab content
- Badge is the ONLY signal of fallback — no error messages
- Visually distinct: green (#e8f5e9) vs grey (#f5f5f5)
