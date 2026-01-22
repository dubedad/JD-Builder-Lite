# Phase 7: Export Extensions - Context

**Phase Goal:** Users can export job descriptions to Word/DOCX format with the same compliance structure as PDF, and both PDF and DOCX exports include Annex section with unused NOC reference attributes.

**Requirements:**
- OUT-06: Manager can export final JD to Word/DOCX format
- OUT-07: PDF export includes Annex section with unused NOC reference attributes
- OUT-08: DOCX export includes Annex section with unused NOC reference attributes

**Created:** 2026-01-22
**Source:** User discussion session

---

## Annex Content

### What Goes in Annex
- **"Unused" definition:** Attributes not appearing in main sections (General Overview or JD Elements)
- **Example Titles:** NOT in Annex — goes in the overview card (main body)
- **Annex contains:** The remaining four attribute types only

### Annex Section Title
- **Title:** "Additional Job Information"

### Category Order (fixed)
1. Job Requirements
2. Career Mobility
3. Interests (Holland Codes)
4. Personal Suitability (Placement Criteria)

### Category Names (renamed from NOC labels)
- "Interests" → "Interests (Holland Codes)"
- "Personal Attributes" → "Personal Suitability (Placement Criteria)"

### Source Attribution
- **Per section:** Each category section includes attribution line
- **Format:** "Source: NOC {code}, retrieved {date}"

### Content Formatting
- **Job Requirements:** As-is from NOC (keep exact text)
- **Career Mobility:** Grouped by direction — separate "From" (entry paths) and "To" (advancement) sections
- **Interests/Personal Suitability:** Keep as separate sections

### Empty State Handling
- **Always show structure:** Include category headers even if content is empty
- Shows the full Annex framework regardless of data availability

---

## DOCX Formatting

### Visual Match
- **Exact match to PDF:** Same fonts, spacing, colors, table borders

### Document Structure
- **Heading styles:** Use proper Word heading styles (H1, H2, H3) for navigation pane and accessibility
- **Table of contents:** Claude's discretion (include if document length warrants)

### Page Setup
- **Page size:** Letter (8.5" x 11")
- **Margins:** 1" all sides
- **Headers/footers:** Match PDF (include page numbers)

### Styling
- **Colors:** Exact OASIS blue accents matching PDF
- **Tables:** Same border style as PDF export

---

## Button Placement

### Export UI Pattern
- **Dropdown menu:** Single "Export Job Description" button that reveals options
- **NOT side-by-side buttons**

### Dropdown Options
- "Export as PDF"
- "Export as Word"

### Icons
- **Yes:** File type icons next to each format option in dropdown

---

## Error Handling

### Export Failure
- **Toast notification:** Non-blocking error message, user can retry

### File Naming
- **Format:** `{NOC code} - {Title} - {date} - Job Description.{ext}`
- **Example:** "72600.01 - Air Pilots - 2026-01-22 - Job Description.docx"

### Loading State
- **Spinner on button:** Button shows spinner and is disabled during generation

### Empty Selection Warning
- **Warning before export:** Allow click but show "No statements selected" warning
- Does NOT disable the button preemptively

---

## Deferred Ideas

*None captured during this discussion.*

---
*Context captured: 2026-01-22*
*Ready for: Research and planning*
