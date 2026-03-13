# Phase 30: Export Page + New PDF/DOCX/JSON - Research

**Researched:** 2026-03-13
**Domain:** Flask export page, Python PDF generation (reportlab), python-docx Word export, JSON audit schema
**Confidence:** HIGH (codebase), MEDIUM (library choices verified)

---

## Summary

Phase 30 builds a dedicated Export page (Step 5 in the v5.1 stepper) and replaces the existing
WeasyPrint-based PDF with a working reportlab PDF. The critical blocker is that WeasyPrint/libpango
is broken on this machine — the `HAS_WEASYPRINT` flag is always `False` and PDF generation throws
at runtime. The replacement must be a pure-Python library that installs without system dependencies.

The codebase already has a complete, working export data pipeline: `ExportRequest` → `build_export_data()`
→ `ExportData`, and a fully-wired `generate_docx()` using python-docx 1.2.0. The existing export
endpoints (`/api/export/pdf`, `/api/export/docx`) already accept the correct JSON body. Phase 30
restructures the section content, adds the new Export page HTML, and replaces the PDF generator.

The new Export page is a Jinja2-rendered route inside the existing SPA (currently Step 5 = "Export"
opens the sidebar — this must be replaced with a proper page render or content-swap). Session state
lives in localStorage (`store.getState()`) and in Flask session (`session['ai_generation']`). All
data needed for export is already being assembled by `buildExportRequest()` in export.js.

**Primary recommendation:** Use reportlab 4.4.10 for PDF (installs cleanly on Python 3.14, no system
deps). Keep python-docx 1.2.0 for DOCX (already installed, fully working). Add a new Flask route
`/export` that renders a Jinja2 template for the Export page.

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| reportlab | 4.4.10 | PDF generation | Pure Python, no system deps, Python 3.9–3.14 compatible, confirmed installable on this machine |
| python-docx | 1.2.0 | Word generation | Already installed and working, existing `generate_docx()` just needs section restructure |
| Flask | 3.1.2 | Route + template rendering | Already in use |
| Jinja2 | (Flask bundled) | Export page template | Already in use |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| json (stdlib) | - | JSON audit trail serialization | JSON export endpoint |
| io.BytesIO | (stdlib) | PDF/DOCX byte buffers | Return file downloads |
| datetime (stdlib) | - | Timestamps in audit trail | JSON export |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| reportlab | fpdf2 2.8.7 | fpdf2 also installable on Python 3.14, simpler API but less table/style control; reportlab preferred for complex provenance tables |
| reportlab | WeasyPrint | Broken on this machine (libpango missing), ruled out |
| Jinja2 template | Client-side rendering | App uses server-side templates throughout; consistency demands Jinja2 |

**Installation (to add to requirements.txt):**
```bash
pip install reportlab==4.4.10
```

---

## Architecture Patterns

### Current Structure (what exists)
```
src/
├── routes/api.py                  # /api/export/pdf, /api/export/docx, /api/preview endpoints
├── services/
│   ├── export_service.py          # build_export_data(), build_compliance_sections()
│   ├── pdf_generator.py           # generate_pdf() — BROKEN (WeasyPrint)
│   ├── docx_generator.py          # generate_docx() — WORKING, needs section restructure
│   └── annex_builder.py           # build_annex_data()
├── models/
│   └── export_models.py           # ExportRequest, ExportData, SelectionMetadata, AIMetadata
templates/
├── export/
│   ├── jd_pdf.html                # PDF template (WeasyPrint, being replaced)
│   └── jd_preview.html            # Preview page (currently injected into body innerHTML)
static/js/
└── export.js                      # buildExportRequest(), downloadPDF(), downloadDOCX()
```

### Phase 30 Target Structure
```
src/
├── routes/
│   ├── api.py                     # Add /api/export/json endpoint; keep pdf/docx endpoints
│   └── pages.py (new)             # GET /export — render export page template
├── services/
│   ├── pdf_generator.py           # Rewrite: reportlab instead of WeasyPrint
│   ├── docx_generator.py          # Restructure sections (same file, new content)
│   └── export_service.py          # Extend: build_json_export()
├── models/
│   └── export_models.py           # Add ExportOptions model (checkboxes)
templates/
├── export/
│   ├── jd_pdf.html                # DELETE (no longer needed with reportlab)
│   └── jd_preview.html            # KEEP for modal use, may need minor updates
├── export_page.html (new)         # The new Export page (v5.1 chrome, 3 cards, buttons, JD preview)
static/js/
└── export.js                      # Update: add navigateToExportPage(), downloadJSON()
```

### Pattern 1: Export Page as Server-Rendered Route

**What:** A new Flask route `GET /export` renders a full Jinja2 template inside the v5.1 chrome.
The page passes compliance data and JD preview content from the server.

**When to use:** Export page is a distinct step (Step 5) in the workflow — a full page render is
cleaner than the current innerHTML-swap approach.

**How it wires to the stepper:** The current `case 5` in main.js opens the sidebar. This must
change to `window.location.href = '/export'` (or a `fetch` + page swap), passing session data
to the route.

**Pattern — server route:**
```python
# src/routes/pages.py (new file)
from flask import Blueprint, render_template, session, redirect, url_for
pages_bp = Blueprint('pages', __name__)

@pages_bp.route('/export')
def export_page():
    """Render the Export page with session state."""
    # Session data injected into template
    ai_generation = session.get('ai_generation', None)
    return render_template('export_page.html',
        ai_generation=ai_generation
    )
```

**Alternative pattern — keep SPA, content swap:** The stepper's `case 5` triggers a
`fetch('/api/export-page-data')` and swaps page content, similar to how the preview page
currently works (the `showPreview()` method in export.js replaces `document.body.innerHTML`).
This avoids a page navigation and keeps all JS state alive. This is the RECOMMENDED approach
since the current export flow already uses this pattern — `currentExportData` in exportModule
would remain available.

### Pattern 2: reportlab PDF Generation

**What:** Replace WeasyPrint HTML-to-PDF with direct reportlab Platypus document construction.

**When to use:** Required — WeasyPrint is broken. reportlab is pure Python, no system deps.

**Key reportlab concepts:**
- `SimpleDocTemplate` or `BaseDocTemplate` for page setup
- `Paragraph`, `Table`, `Spacer`, `PageBreak` as `Flowables`
- `TableStyle` for coloured cell backgrounds and borders
- `ParagraphStyle` for heading/body/caption text styles
- `HRFlowable` for horizontal rules
- Colored pill badges require a `Table` with `BACKGROUND` style (no native pill widget)

```python
# Source: reportlab 4.4.10 official docs
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, PageBreak
from reportlab.lib.units import inch

# Pill badge simulation using a 1-row table with rounded background
def make_pill_badge(text, bg_color, text_color=colors.white):
    """Create a pill-badge style element for source tags."""
    return Table(
        [[Paragraph(text, ParagraphStyle('pill',
            fontName='Helvetica-Bold', fontSize=8,
            textColor=text_color, spaceAfter=0))]],
        colWidths=[None],
        style=TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), bg_color),
            ('TOPPADDING', (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
            ('ROUNDEDCORNERS', [4]),
        ])
    )
```

### Pattern 3: JSON Audit Trail Schema

**What:** A clean, HR-system-consumable JSON structure. No UI-specific fields. Self-contained
statements. All provenance embedded inline.

**Recommended top-level schema:**
```json
{
  "schema_version": "1.0",
  "export_timestamp": "2026-03-13T14:00:00Z",
  "session": {
    "session_id": "abc123",
    "noc_code": "21232",
    "job_title": "Data Scientist",
    "noc_data_retrieved_at": "2026-03-13T10:00:00Z",
    "noc_version": "NOC 2025.1"
  },
  "position_overview": {
    "text": "The position...",
    "generated_by": {
      "model": "gpt-4o",
      "prompt_version": "v3.0",
      "generated_at": "2026-03-13T11:30:00Z",
      "modified_by_user": false,
      "input_statement_ids": ["key_activities-0", "skills-2"]
    }
  },
  "classification": {
    "top_group_code": "CS",
    "top_group_name": "Computer Systems",
    "confidence_pct": 85,
    "analyzed_at": "2026-03-13T12:00:00Z"
  },
  "selected_statements": [
    {
      "id": "key_activities-0",
      "jd_section": "Key Duties and Responsibilities",
      "text": "Develop and maintain data pipelines...",
      "source": "Main Duties",
      "source_table_url": "https://...",
      "source_publication_date": "2025-10-30",
      "selected_at": "2026-03-13T11:00:00Z"
    }
  ],
  "compliance": {
    "directive": "TBS Directive 32592",
    "data_steward": "ESDC",
    "total_selections": 12
  },
  "provenance_annex_included": true,
  "audit_trail_included": true
}
```

**Decision — JSON always exports everything:** JSON is an API payload. Downstream HR systems
need the full data; checkbox gating would produce inconsistent payloads. JSON always exports
full content. The `provenance_annex_included` and `audit_trail_included` fields record what
was checked, as metadata only.

**Decision — Checkboxes default to checked ON:** For a government compliance tool, including
provenance and audit trail by default is the correct conservative choice. Users opt-out rather
than opt-in.

### Pattern 4: Compliance Summary Cards (Claude's Discretion)

Three cards surfacing data already available in session:

**DAMA DMBOK (green):** Data quality dimensions.
- Accuracy: "Sourced from ESDC NOC (authoritative)"
- Completeness: "N statements selected across M sections"
- Timeliness: "Data retrieved [date]"
- Consistency: "Single source (OASIS/JobForge parquet)"

**TBS Directives (blue):** Directive attestation.
- Directive 32592 (DADM): "Automated decision disclosed"
- Directive on Classification: "Occupational group allocated"
- AI Disclosure: model name + prompt version (from `ai_generation` session key)

**Full Lineage (purple):** Source trace.
- NOC code + version
- Per-section data sources (jobforge vs oasis, from `section_sources`)
- Total selected statements count
- Session ID for traceability

### Anti-Patterns to Avoid
- **WeasyPrint usage:** Already broken. Do not attempt `HTML(string=...)` — throws `OSError` at import.
- **Client-side PDF generation:** jsPDF etc. cannot replicate the provenance table complexity needed.
- **session_state.py assumption:** There is NO `src/services/session_state.py` file — Flask session
  is used directly via `session['ai_generation']`. All other state comes from the JS store (localStorage)
  and is passed in the POST body of export requests.
- **Replacing `export.js` entirely:** `buildExportRequest()` and `downloadPDF()`/`downloadDOCX()` are
  wired and working — extend, don't replace.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| PDF generation | Custom HTML-to-PDF | reportlab 4.4.10 | Handles page breaks, headers, footers, tables, font embedding |
| Word generation | Custom XML writer | python-docx 1.2.0 (already present) | Complex Word XML is unmaintainable by hand |
| JSON serialization of datetime | Manual strftime | `default=str` in `json.dumps()` or pydantic `.model_dump(mode='json')` | Handles datetime, Enum, Decimal automatically |
| Pill badges in PDF | SVG/image | reportlab `Table` with `BACKGROUND` color + tight padding | reportlab doesn't support border-radius but a colored cell achieves the same visual |

**Key insight:** The full export data model (`ExportData`) is already correct and well-structured.
Phase 30 does NOT need to change `export_models.py`, `export_service.py`, or `annex_builder.py` —
only the generators (PDF rebuild) and new endpoints (JSON) need to be written.

---

## Common Pitfalls

### Pitfall 1: WeasyPrint Still Being Called

**What goes wrong:** `generate_pdf()` in `pdf_generator.py` calls `HTML(string=..., base_url=...)`
which is `None` when `HAS_WEASYPRINT = False`, causing `TypeError: 'NoneType' object is not callable`.

**Why it happens:** The guard is `if not HAS_WEASYPRINT: raise RuntimeError(...)` but there's no
such guard — the function just calls `HTML(...)` unconditionally after the import guard sets `HTML = None`.

**How to avoid:** The entire function body must be replaced. The new `generate_pdf()` will use
reportlab exclusively — no import of WeasyPrint anywhere.

**Warning signs:** `TypeError: 'NoneType' object is not callable` in the Flask log.

### Pitfall 2: Export Page State Transfer

**What goes wrong:** The Export page (Step 5) needs to know: NOC code, job title, selected statements,
overview text, AI metadata, classification result. All of this lives in localStorage (JS store) and
Flask session — but a full page navigation (`window.location.href = '/export'`) loses all JS state.

**Why it happens:** The current export flow uses `exportModule.buildExportRequest()` which reads from
`store.getState()` and `window.currentProfile`. A hard navigation discards these.

**How to avoid:** Use the content-swap pattern (matching the existing `showPreview()` approach):
fetch `/api/export-page` as HTML and replace `document.body.innerHTML`, OR pass export data
as a POST body to a new endpoint that returns the page HTML. The export data object from
`buildExportRequest()` contains everything needed for the compliance cards.

### Pitfall 3: reportlab Pill Badge Border-Radius

**What goes wrong:** `ROUNDEDCORNERS` in `TableStyle` is only supported in some reportlab versions
and contexts; it may be silently ignored.

**Why it happens:** reportlab's PDF drawing model doesn't natively support border-radius on tables.

**How to avoid:** Use a `RoundRect` canvas drawing for true rounded badges, or accept that PDF
badges will be rectangular. For compliance documents, rectangular colored tags are acceptable.
The UI pill visual is the primary surface — PDF tags just need the correct color and label.

### Pitfall 4: python-docx Table Border Rendering

**What goes wrong:** `Table Grid` style renders differently in LibreOffice vs Microsoft Word.
Bold cell borders may appear too heavy.

**How to avoid:** The existing `docx_generator.py` already uses `'Table Grid'` successfully
for compliance tables. Follow the same pattern for new sections.

### Pitfall 5: JSON Datetime Serialization

**What goes wrong:** `json.dumps(data)` raises `TypeError: Object of type datetime is not JSON serializable`.

**Why it happens:** `SelectionMetadata.selected_at` is a Python `datetime`, not a string.

**How to avoid:** Use pydantic's `.model_dump(mode='json')` which auto-serializes datetimes to
ISO 8601 strings, or pass `default=str` to `json.dumps()`.

### Pitfall 6: Stepper Step 5 Currently Opens Sidebar

**What goes wrong:** In `main.js`, `case 5` (Export step) currently opens the sidebar — not a
page or content section. The new Export page must replace this behavior.

**Why it happens:** The old Export flow was sidebar-based (old design). v5.1 requires a dedicated
Export page.

**How to avoid:** In Phase 30, update `case 5` in the `navigateToStep()` switch to call
`exportModule.navigateToExportPage()` instead of opening the sidebar. The `buildExportRequest()`
call must happen before the navigation so data is ready.

---

## Code Examples

### reportlab: Basic JD Section with Source Tags

```python
# Source: reportlab 4.4.10 docs + codebase pattern
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Table, TableStyle,
    Spacer, PageBreak, HRFlowable
)
from reportlab.lib.units import inch
from io import BytesIO

# Source pill colors matching UI CSS variables
SOURCE_COLORS = {
    'Main Duties':    colors.HexColor('#6f42c1'),  # --pill-oasis-bg
    'Skills':         colors.HexColor('#17a2b8'),  # --pill-onet-bg
    'Abilities':      colors.HexColor('#17a2b8'),
    'Knowledge':      colors.HexColor('#17a2b8'),
    'Work Activities': colors.HexColor('#fd7e14'), # --pill-ochro-bg
}

def make_source_tag(source_attribute: str) -> Table:
    """Inline source tag matching UI data-source-pill style."""
    bg = SOURCE_COLORS.get(source_attribute, colors.HexColor('#555555'))
    style = ParagraphStyle('tag', fontName='Helvetica', fontSize=7,
                           textColor=colors.white)
    return Table(
        [[Paragraph(source_attribute, style)]],
        style=TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), bg),
            ('TOPPADDING', (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
            ('LEFTPADDING', (0,0), (-1,-1), 5),
            ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ])
    )


def generate_pdf(data: ExportData, include_provenance: bool, include_audit: bool) -> bytes:
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter,
                            leftMargin=inch*0.75, rightMargin=inch*0.75,
                            topMargin=inch, bottomMargin=inch)
    styles = getSampleStyleSheet()
    story = []

    # Title
    story.append(Paragraph(data.job_title, styles['Title']))
    story.append(Paragraph(f"NOC Code: {data.noc_code}", styles['Normal']))
    story.append(Spacer(1, 12))

    # Key Duties with source tags — inline table per statement
    story.append(Paragraph("Key Duties and Responsibilities", styles['Heading1']))
    for element in data.jd_elements:
        if element.key == 'key_activities':
            for stmt in element.statements:
                # Row: [bullet text | source tag]
                row = [
                    Paragraph(f"• {stmt.text}", styles['Normal']),
                    make_source_tag(stmt.source_attribute)
                ]
                t = Table([row], colWidths=[4.5*inch, 1.5*inch])
                t.setStyle(TableStyle([
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ('LEFTPADDING', (0,0), (0,-1), 0),
                    ('RIGHTPADDING', (-1,0), (-1,-1), 0),
                ]))
                story.append(t)
                story.append(Spacer(1, 4))

    doc.build(story)
    buf.seek(0)
    return buf.read()
```

### python-docx: Source Tag as Colored Run

```python
# Source: python-docx 1.2.0 — existing docx_generator.py pattern
from docx.shared import RGBColor, Pt

SOURCE_COLORS_DOCX = {
    'Main Duties':    RGBColor(0x6f, 0x42, 0xc1),
    'Skills':         RGBColor(0x17, 0xa2, 0xb8),
    'Work Activities': RGBColor(0xfd, 0x7e, 0x14),
}

def add_statement_with_source_tag(doc, statement):
    para = doc.add_paragraph()
    para.style = 'List Bullet'
    # Statement text
    para.add_run(statement.text)
    # Source tag — inline colored run
    tag_run = para.add_run(f"  [{statement.source_attribute}]")
    tag_run.font.size = Pt(8)
    tag_run.font.color.rgb = SOURCE_COLORS_DOCX.get(
        statement.source_attribute,
        RGBColor(0x55, 0x55, 0x55)
    )
    tag_run.bold = True
```

### JSON Export: Serialize from ExportData

```python
# Source: pydantic model_dump + json stdlib
import json
from datetime import datetime

def build_json_export(data: ExportData, session_id: str,
                      include_provenance: bool, include_audit: bool) -> str:
    """Build JSON audit trail payload for HR system consumption."""
    top_rec = None
    if data.classification_result and data.classification_result.get('recommendations'):
        top_rec = data.classification_result['recommendations'][0]

    payload = {
        "schema_version": "1.0",
        "export_timestamp": datetime.utcnow().isoformat() + "Z",
        "session": {
            "session_id": session_id,
            "noc_code": data.noc_code,
            "job_title": data.job_title,
            "noc_data_retrieved_at": data.source_metadata.scraped_at.isoformat(),
            "noc_version": data.source_metadata.version
        },
        "position_overview": None,
        "classification": None,
        "selected_statements": [],
        "compliance": {
            "directive": "TBS Directive 32592 (DADM)",
            "data_steward": "ESDC",
            "total_selections": len(data.manager_selections)
        },
        "provenance_annex_included": include_provenance,
        "audit_trail_included": include_audit
    }

    # Overview
    if data.general_overview and data.ai_metadata:
        payload["position_overview"] = {
            "text": data.general_overview,
            "generated_by": {
                "model": data.ai_metadata.model,
                "prompt_version": data.ai_metadata.prompt_version,
                "generated_at": data.ai_metadata.timestamp.isoformat(),
                "modified_by_user": data.ai_metadata.modified,
                "input_statement_ids": data.ai_metadata.input_statement_ids
            }
        }

    # Classification
    if top_rec:
        payload["classification"] = {
            "top_group_code": top_rec["group_code"],
            "top_group_name": top_rec["group_name"],
            "confidence_pct": top_rec["confidence"],
            "analyzed_at": data.classification_result.get("analyzed_at", "")
        }

    # Statements
    for sel in data.manager_selections:
        payload["selected_statements"].append({
            "id": sel.id,
            "jd_section": sel.jd_element,
            "text": sel.text,
            "source": sel.source_attribute,
            "source_table_url": sel.source_table_url,
            "source_publication_date": sel.publication_date,
            "selected_at": sel.selected_at.isoformat()
        })

    return json.dumps(payload, indent=2, ensure_ascii=False)
```

### Export Page HTML: Section Layout

```html
<!-- templates/export_page.html — inserted into existing SPA chrome via content swap -->
<!-- Toolbar row: Export Options above, Download Buttons below -->
<div class="export-toolbar">
  <div class="export-options-group">
    <label class="export-option-label"><strong>Export Options</strong></label>
    <label class="export-checkbox">
      <input type="checkbox" id="opt-provenance" checked>
      Include provenance annex
    </label>
    <label class="export-checkbox">
      <input type="checkbox" id="opt-audit" checked>
      Include audit trail
    </label>
  </div>
  <div class="export-download-buttons">
    <button id="btn-download-pdf" class="btn btn--danger">
      Download PDF — With embedded provenance
    </button>
    <button id="btn-download-docx" class="btn btn--primary">
      Download Word — With audit trail annex
    </button>
    <button id="btn-download-json" class="btn btn--outline">
      Download Full Audit Trail (JSON)
    </button>
  </div>
</div>

<!-- Compliance Summary Cards -->
<div class="compliance-cards-row">
  <div class="compliance-card compliance-card--green" id="card-dama">...</div>
  <div class="compliance-card compliance-card--blue" id="card-tbs">...</div>
  <div class="compliance-card compliance-card--purple" id="card-lineage">...</div>
</div>

<!-- JD Preview Card (scrollable) -->
<div class="jd-preview-card" id="export-jd-preview">
  <!-- Assembled by export.js assembleJDPreview() -->
</div>
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| WeasyPrint HTML→PDF | reportlab Platypus PDF | Phase 30 | No system dep; pure Python |
| Preview page (body innerHTML swap) | Dedicated Export page (same swap pattern) | Phase 30 | Cleaner UX, no page navigation needed |
| No JSON export | JSON audit trail endpoint | Phase 30 | HR system integration |
| No compliance cards | 3 compliance summary cards | Phase 30 | Surfaced from existing session data |
| PDF uses WeasyPrint template | PDF uses reportlab Flowables | Phase 30 | New PDF is programmatic not HTML |

**Deprecated/outdated:**
- `templates/export/jd_pdf.html`: Only used by WeasyPrint `generate_pdf()`. Once reportlab is
  in place this template is dead code and should be deleted.
- The existing `generate_pdf()` function body in `pdf_generator.py`: Fully replaced.

---

## Session State Available for Export

All data fields confirmed by reading `export.js` → `buildExportRequest()` and `export_models.py`.

### Available from JS store (localStorage)
- `state.selections` — `{key_activities: ['key_activities-0', ...], skills: [...], ...}` (8 sections)
- `state.selectionTimestamps` — `{stmtId: ISO8601 string}` — per-statement selection timestamp
- `state.positionTitle` — editable position title string
- `state.currentProfileCode` — NOC code

### Available from `window.currentProfile`
- `profile.noc_code`, `profile.title`
- `profile.key_activities.statements[i].text`, `.source_attribute`, `.description`, `.proficiency`
- Same for `skills`, `effort`, `responsibility`, `working_conditions`
- `profile.metadata.scraped_at`, `.profile_url`, `.version`, `.noc_code`
- `profile.key_activities.data_source` — `'jobforge'` or `'oasis'`
- `profile.reference_attributes.core_competencies[]` — array of strings
- Abilities/Knowledge: filtered from `profile.skills.statements` by source_attribute

### Available from `window.aiGenerationMetadata` (Flask session via `/api/generation-metadata`)
- `model` — e.g. `"gpt-4o"`
- `timestamp` — ISO8601
- `prompt_version` — e.g. `"v3.0"`
- `input_statement_ids[]`
- `modified` — boolean

### Available from `classifyModule.getCurrentAllocation()`
- Full AllocationResponse: `recommendations[]`, `provenance_map`, `confidence_summary`
- Each recommendation: `group_code`, `group_name`, `confidence`, `rationale`, `evidence_spans[]`

### NOT available / gaps
- There is NO `session_state.py` — Flask session only stores `ai_generation` dict.
- No server-side record of "user opened search", "user loaded profile" timestamps — audit trail
  chronological log must be reconstructed from: profile `scraped_at` + `selectionTimestamps` +
  AI `generation.timestamp`. These three timestamps are the audit trail events.
- `session_id` is only in localStorage (`jdb_session_id`), not in Flask session.

---

## PDF Restructured Section Order (per Phase 30 Requirements)

New PDF section structure (PDF-01 through PDF-04):

1. **Position Overview** — `data.general_overview` (AI prose) + AI indicator
2. **Key Duties and Responsibilities** — `key_activities` statements with colored source tag pills
3. **Qualifications** — Sub-sections:
   - Skills (`skills` element)
   - Abilities (`abilities` element — currently in `skills` section filtered by source_attribute)
   - Knowledge (`knowledge` element — same)
   - Core Competencies (from `profile.reference_attributes.core_competencies` — plain strings, NOT in `ExportData.jd_elements`)
4. **Effort & Physical Demands** — `effort` element
5. **Responsibilities** — `responsibility` element (note: existing code uses `working_conditions` too)
6. **Data Provenance & Compliance** — New combined section containing:
   - Policy Provenance table (Authoritative Data Sources)
   - DADM compliance attestation paragraph
   - DAMA DMBOK data quality summary
7. **(If checkbox: Include provenance annex)** — Full annex pages appended
8. **(If checkbox: Include audit trail)** — Chronological action log appended

**Critical gap:** `core_competencies` is NOT in `ExportData.jd_elements` — it's a separate
array in `profile.reference_attributes`. The `buildExportRequest()` in export.js includes
`core_competencies` in `state.selections` but does NOT map them to `selections` (line 519
in export.js shows it reads from `profile.reference_attributes.core_competencies`). The
`export_service.py` `JD_ELEMENT_ORDER` does not include `core_competencies`.

**Resolution:** The PDF/DOCX generator must handle core_competencies separately from `jd_elements`.
When `export_request.selections` contains `core_competencies-N` IDs, these need to be resolved
in `build_export_data()` or passed through a new field. **This is an existing gap** that Phase 30
must address for the Qualifications section.

---

## Open Questions

1. **Core Competencies in ExportData**
   - What we know: `core_competencies` IDs are in `state.selections` and in `buildExportRequest()`,
     but `export_service.py` `JD_ELEMENT_ORDER` does not include them, and `profile.reference_attributes.core_competencies`
     is not currently passed to the backend export endpoint.
   - What's unclear: Should `buildExportRequest()` be updated to include core_competencies as a proper
     `selections` item, or should a new field be added to `ExportData`?
   - Recommendation: Add `'core_competencies'` to `JD_ELEMENT_ORDER` in `export_service.py` and update
     `buildExportRequest()` to include them with `source_attribute: 'Core Competencies'` and the text
     from `profile.reference_attributes.core_competencies[index]`.

2. **Export Page Navigation Pattern**
   - What we know: Current Step 5 opens the sidebar. Content-swap (innerHTML replace) is established
     pattern from `showPreview()`.
   - What's unclear: Whether to add a dedicated `/export` route (server render) or stay fully
     client-side (content swap). Server render means session data on the server is accessible
     directly; client-side means all data already assembled in JS.
   - Recommendation: Use content-swap pattern (matching existing preview). Add a new API endpoint
     `POST /api/export-page` that returns the export page HTML, using the same `ExportRequest`
     body already assembled by `buildExportRequest()`. This avoids a full page navigation and
     keeps JS state alive.

3. **Audit Trail: What Events to Log**
   - What we know: `selectionTimestamps` captures when each statement was selected. `ai_metadata.timestamp`
     captures when AI generation ran. `source_metadata.scraped_at` captures when the profile was loaded.
   - What's unclear: Whether "search performed" timestamp is tracked anywhere.
   - Recommendation: The audit trail section should log: (1) Profile loaded at `scraped_at`, (2) each
     selection event from `selectionTimestamps` in chronological order, (3) AI generation at `ai_metadata.timestamp`
     if present. No "search performed" event is available — skip it.

4. **reportlab vs fpdf2**
   - What we know: Both are installable on Python 3.14. reportlab 4.4.10 is the more mature library
     with better table/style support. fpdf2 2.8.7 has a simpler API.
   - Recommendation: Use reportlab for richer compliance table formatting capability.

---

## Sources

### Primary (HIGH confidence)
- Codebase direct reading — `src/services/pdf_generator.py`, `docx_generator.py`, `export_service.py`,
  `models/export_models.py`, `routes/api.py`, `static/js/export.js`, `static/js/state.js`,
  `templates/export/jd_preview.html`, `templates/export/jd_pdf.html`
- `pip3 install reportlab --dry-run` — confirmed installable on Python 3.14.3 (reportlab 4.4.10)
- `pip3 install fpdf2 --dry-run` — confirmed installable on Python 3.14.3 (fpdf2 2.8.7)
- `python3 -c "import weasyprint"` — confirmed broken on this machine (libpango missing)
- `pip3 show python-docx` — confirmed 1.2.0 installed and working
- PyPI page for reportlab — version 4.4.10, Python 3.9–3.14 compatible, released 2026-02-12

### Secondary (MEDIUM confidence)
- reportlab 4.4.10 PyPI page — feature set, Python compatibility
- Phase 26 plans read — confirmed v5.1 chrome structure, step mapping, data-source-pill CSS

### Tertiary (LOW confidence)
- Training knowledge of reportlab `ROUNDEDCORNERS` support in `TableStyle` — needs validation
  at implementation time; may need to use rectangular cells instead

---

## Metadata

**Confidence breakdown:**
- Session state available: HIGH — read directly from source files
- WeasyPrint broken: HIGH — confirmed by running `python3 -c "import weasyprint"`
- reportlab installability: HIGH — confirmed via dry-run pip install
- reportlab API patterns: MEDIUM — based on official docs + training knowledge; specific roundedcorners
  behavior needs testing
- python-docx source tag approach: HIGH — extending existing proven pattern in docx_generator.py
- JSON schema design: HIGH — derived from actual available data fields
- Export page navigation pattern: HIGH — derived from existing showPreview() pattern in codebase

**Research date:** 2026-03-13
**Valid until:** 2026-04-13 (reportlab is stable; all other findings are codebase facts)
