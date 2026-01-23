---
phase: 07-export-extensions
plan: 04
status: complete
completed_at: 2026-01-22
---

# 07-04 Summary: Export UI Dropdown + Toast Notifications

## What Was Built

### 1. Export Dropdown Menu (`templates/export/jd_preview.html`)

Replaced side-by-side PDF/DOCX buttons with single dropdown:
```html
<div class="export-dropdown" id="export-dropdown">
  <button id="export-btn" class="btn btn--primary export-btn">
    <span class="export-btn-text">Export Job Description</span>
    <svg class="export-btn-icon"><!-- chevron --></svg>
    <span class="export-btn-spinner"></span>
  </button>
  <div class="export-dropdown-menu" role="menu">
    <button class="export-option" data-format="pdf">
      <svg class="export-option-icon"><!-- PDF icon --></svg>
      <span>Export as PDF</span>
    </button>
    <button class="export-option" data-format="docx">
      <svg class="export-option-icon"><!-- Word icon --></svg>
      <span>Export as Word</span>
    </button>
  </div>
</div>
```

Added toast container: `<div id="toast-container" class="toast-container" aria-live="polite"></div>`

### 2. Dropdown and Toast Styles (`static/css/export_screen.css`)

- `.export-dropdown` - Relative positioning for menu
- `.export-btn-icon` - Chevron rotation on expand
- `.export-btn-spinner` - Loading spinner (hidden by default)
- `.export-btn--loading` - Loading state (hides icon, shows spinner)
- `.export-dropdown-menu` - Absolute positioned menu
- `.export-option` - Menu items with icons
- `.toast-container` - Fixed bottom-right positioning
- `.toast--error`, `.toast--success`, `.toast--warning` - Color variants
- `.annex-section` screen styles for preview

### 3. JavaScript Updates (`static/js/export.js`)

**New `showToast()` function:**
```javascript
function showToast(message, type = 'info') {
  // Creates toast element with dismiss button
  // Auto-dismisses after 5 seconds
}
```

**Updated `attachPreviewListeners()`:**
- Dropdown toggle on button click
- Click outside to close
- Export option handlers for PDF/DOCX

**Updated `downloadPDF()` and `downloadDOCX()`:**
- Use dropdown button loading state
- Show success/error toasts instead of alerts
- Use `_generateFilename()` helper

**Helper methods:**
- `_generateFilename(ext)` - Generates `{NOC} - {Title} - {date} - Job Description.{ext}`
- `_downloadBlob(blob, filename)` - Shared download logic

**Empty selection warning:**
- Shows warning toast (non-blocking) per CONTEXT.md
- Export still proceeds with header-only content

## Files Modified

| File | Change |
|------|--------|
| `templates/export/jd_preview.html` | Dropdown menu, toast container |
| `static/css/export_screen.css` | Dropdown + toast + annex screen styles |
| `static/js/export.js` | Toast function, dropdown handlers, updated downloads |

## Verification

- JavaScript syntax: OK (`node --check`)
- Template syntax: OK
- CSS contains dropdown (3 matches) and toast (1 match)

## UI Behavior

1. Click "Export Job Description" → dropdown opens
2. Click "Export as PDF" → loading spinner, generates PDF, success toast
3. Click "Export as Word" → loading spinner, generates DOCX, success toast
4. Error → error toast (non-blocking)
5. Empty selection → warning toast (export proceeds)
6. Click outside dropdown → closes
