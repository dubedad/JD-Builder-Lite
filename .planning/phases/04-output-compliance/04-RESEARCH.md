# Phase 4: Output + Compliance - Research

**Researched:** 2026-01-22
**Domain:** PDF/Word document generation, compliance documentation, audit trails
**Confidence:** HIGH

## Summary

Phase 4 requires generating audit-ready PDF and Word exports from Flask, with compliance metadata demonstrating conformance to Canada's Directive on Automated Decision-Making. The standard Python stack for this is WeasyPrint 68.0 for PDF generation (HTML/CSS to PDF with full CSS Paged Media support) and python-docx 1.2.0 for Word document creation. Flask-WeasyPrint 1.1.0 provides seamless integration with Flask applications.

The compliance appendix must address specific Directive sections: 6.2.7 (document decisions made by automated systems), 6.3.5 (data validation - relevant, accurate, up-to-date), and transparency requirements. Best practices for government audit trails emphasize capturing timestamps, user actions (manager selections), data sources with URLs, and maintaining an immutable record structure.

Key architectural insight: Use HTML templates rendered by Flask for both preview display and PDF generation, ensuring visual consistency. WeasyPrint renders the same HTML/CSS that users see in preview, eliminating design drift between preview and export.

**Primary recommendation:** Use WeasyPrint with Flask-WeasyPrint for PDF generation (HTML/CSS templates with @page rules for headers/footers) and python-docx for Word exports. Structure compliance appendix with explicit Directive section references to give managers confidence in audit-readiness.

## Standard Stack

The established libraries/tools for Python PDF and Word document generation:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| WeasyPrint | 68.0 | HTML/CSS to PDF rendering | Industry standard for print-quality PDFs from HTML, full CSS Paged Media Level 3 support, no external dependencies like wkhtmltopdf |
| Flask-WeasyPrint | 1.1.0 | Flask integration for WeasyPrint | Official integration layer, handles Flask url_for() and static assets correctly, WSGI-level short-circuiting for authenticated routes |
| python-docx | 1.2.0 | Word .docx file creation | De facto standard for programmatic Word document generation, supports headers/footers/tables/styling, active maintenance |
| Pydantic | 2.10.0 | Data validation and serialization | Already in project, use for export data models to ensure type safety |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Jinja2 | (bundled with Flask) | Template rendering for PDF/preview | Core templating engine, use for both preview HTML and PDF HTML |
| python-docx-template | 0.20.x | Jinja2 templates in Word | Only if template-based approach preferred over programmatic (OPTIONAL) |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| WeasyPrint | ReportLab | ReportLab requires low-level Python code for layout vs. HTML/CSS. Use WeasyPrint for HTML-based workflow consistency with preview. |
| WeasyPrint | pdfkit/wkhtmltopdf | wkhtmltopdf is deprecated (last release 2020), requires system binary installation. WeasyPrint is pure Python with active development. |
| python-docx | python-docx-template | Template approach adds Jinja2 layer but limits dynamic structure control. Use python-docx for full programmatic control. |

**Installation:**
```bash
pip install weasyprint==68.0
pip install Flask-WeasyPrint==1.1.0
pip install python-docx==1.2.0
```

**Note:** WeasyPrint 68.0 (released January 19, 2026) is a security update (CVE-2025-68616). Always use latest version.

## Architecture Patterns

### Recommended Project Structure
```
src/
├── services/
│   ├── export_service.py      # Orchestrates PDF and Word generation
│   ├── pdf_generator.py       # WeasyPrint PDF generation logic
│   ├── docx_generator.py      # python-docx Word generation logic
│   └── compliance_builder.py  # Builds compliance metadata structures
├── routes/
│   └── api.py                 # Add /api/export/pdf and /api/export/docx endpoints
├── models/
│   └── export_models.py       # Pydantic models for export data (selections, metadata)
templates/
├── export/
│   ├── jd_preview.html        # Preview display (also used for PDF)
│   ├── jd_pdf.html            # PDF-specific wrapper with print CSS
│   └── compliance_appendix.html  # Compliance metadata template
static/
└── css/
    ├── export_screen.css      # Screen display styles
    └── export_print.css       # PDF print styles with @page rules
```

### Pattern 1: Unified HTML Template for Preview and PDF
**What:** Use the same HTML template for both web preview and PDF generation, with media queries and @page rules for print-specific styling.

**When to use:** Always. Eliminates design drift between preview and final PDF.

**Example:**
```python
# Source: Flask-WeasyPrint documentation + best practices synthesis
from flask import render_template, request
from flask_weasyprint import HTML, render_pdf

@app.route('/api/preview')
def preview():
    """Manager sees this before exporting."""
    data = build_export_data(request.args)
    return render_template('export/jd_preview.html', **data)

@app.route('/api/export/pdf')
def export_pdf():
    """Same template, rendered to PDF."""
    data = build_export_data(request.args)
    html = render_template('export/jd_pdf.html', **data)
    return render_pdf(HTML(string=html))
```

### Pattern 2: CSS @page Rules for Headers and Footers
**What:** Use CSS Paged Media @page margin boxes with running elements and page counters for consistent headers/footers across all pages.

**When to use:** Required for repeating headers/footers with page numbers.

**Example:**
```css
/* Source: WeasyPrint Tips & Tricks documentation */
@page {
  size: letter portrait;
  margin: 1in 0.75in;

  @top-center {
    content: string(job-title) " (" string(noc-code) ")";
    font-size: 10pt;
    color: #26374a;
  }

  @bottom-left {
    content: "Compliant with TBS Directive 32592";
    font-size: 8pt;
  }

  @bottom-right {
    content: "Page " counter(page) " of " counter(pages);
    font-size: 8pt;
  }
}

/* Define running elements */
.page-header {
  position: running(page-header);
}

h1.job-title {
  string-set: job-title content();
}

.noc-code {
  string-set: noc-code content();
}
```

### Pattern 3: Compliance Appendix with Directive Section References
**What:** Structure compliance metadata as separate appendix sections explicitly mapped to Directive requirements.

**When to use:** Always. Provides manager confidence and demonstrates audit-readiness.

**Example:**
```html
<!-- Source: Directive on Automated Decision-Making + audit trail best practices -->
<div class="compliance-appendix">
  <h1>Appendix A: Compliance Metadata</h1>

  <section id="section-6-2-7">
    <h2>Section 6.2.7: Documented Decisions</h2>
    <p>This job description was created using the JD Builder Lite tool, which
    documents all manager selections from authoritative NOC data.</p>

    <h3>Manager Selections</h3>
    <table>
      <thead>
        <tr>
          <th>JD Element</th>
          <th>Selected Statement</th>
          <th>Source (NOC Attribute)</th>
          <th>Selection Timestamp</th>
        </tr>
      </thead>
      <tbody>
        {% for selection in manager_selections %}
        <tr>
          <td>{{ selection.jd_element }}</td>
          <td>{{ selection.text }}</td>
          <td>{{ selection.source_attribute }}</td>
          <td>{{ selection.timestamp }}</td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </section>

  <section id="section-6-3-5">
    <h2>Section 6.3.5: Data Quality Validation</h2>
    <table>
      <tr>
        <th>Requirement</th>
        <th>How Met</th>
      </tr>
      <tr>
        <td>Relevant</td>
        <td>Data sourced from ESDC National Occupational Classification (NOC),
        the authoritative source for occupational data in Canada</td>
      </tr>
      <tr>
        <td>Accurate</td>
        <td>Data retrieved directly from OASIS at
        <a href="{{ metadata.profile_url }}">{{ metadata.profile_url }}</a></td>
      </tr>
      <tr>
        <td>Up-to-date</td>
        <td>NOC Version: {{ metadata.version }}<br>
        Retrieved: {{ metadata.scraped_at }}</td>
      </tr>
    </table>
  </section>

  <section id="ai-disclosure">
    <h2>AI-Generated Content Disclosure</h2>
    <p>The following content was generated using Large Language Model (LLM) technology:</p>
    <ul>
      <li><strong>General Overview:</strong> Generated by {{ ai_metadata.model }}
      on {{ ai_metadata.timestamp }}</li>
      <li><strong>Input statements:</strong> {{ ai_metadata.input_count }} NOC statements
      selected by manager</li>
      <li><strong>Purpose:</strong> Synthesize selected NOC statements into cohesive
      overview paragraph</li>
    </ul>
  </section>
</div>
```

### Pattern 4: python-docx Programmatic Document Construction
**What:** Build Word documents programmatically with headers, footers, tables, and styled paragraphs.

**When to use:** For Word export functionality.

**Example:**
```python
# Source: python-docx official documentation
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

def generate_word_export(data):
    """Generate Word document with compliance metadata."""
    doc = Document()

    # Configure page setup
    section = doc.sections[0]
    section.page_height = Inches(11)
    section.page_width = Inches(8.5)
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)

    # Add header with job title and NOC code
    header = section.header
    header_para = header.paragraphs[0]
    header_para.text = f"{data['job_title']} ({data['noc_code']})"
    header_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Add footer with page numbers
    footer = section.footer
    footer_para = footer.paragraphs[0]
    footer_para.text = "\tCompliant with TBS Directive 32592\t"
    # Page numbers added via field code (requires python-docx advanced usage)

    # Add main content
    doc.add_heading(data['job_title'], 0)
    doc.add_paragraph(data['general_overview'])

    # Add JD elements as sections
    for element in ['Key Activities', 'Skills', 'Effort']:
        doc.add_heading(element, 1)
        for statement in data[element.lower().replace(' ', '_')]:
            doc.add_paragraph(statement.text, style='List Bullet')

    # Add compliance appendix as new section with page break
    doc.add_page_break()
    doc.add_heading('Appendix A: Compliance Metadata', 0)

    # Add table for manager selections
    doc.add_heading('Section 6.2.7: Documented Decisions', 1)
    table = doc.add_table(rows=1, cols=4)
    table.style = 'Light Grid Accent 1'

    # Header row
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'JD Element'
    hdr_cells[1].text = 'Selected Statement'
    hdr_cells[2].text = 'Source (NOC Attribute)'
    hdr_cells[3].text = 'Selection Timestamp'

    # Data rows
    for selection in data['manager_selections']:
        row_cells = table.add_row().cells
        row_cells[0].text = selection.jd_element
        row_cells[1].text = selection.text
        row_cells[2].text = selection.source_attribute
        row_cells[3].text = str(selection.timestamp)

    return doc
```

### Anti-Patterns to Avoid

- **Generating PDF from HTML string without base_url:** Images and CSS won't load. Always pass `base_url=request.url_root` to WeasyPrint HTML() constructor.
- **Using global variables for export data:** Flask request context is threaded. Pass data explicitly through function parameters.
- **Generating PDFs synchronously in request handler for large documents:** Can cause timeouts. For production, consider Celery for async generation (though not required for MVP).
- **Hand-rolling page numbering logic:** Use CSS counter(page) and counter(pages) instead of trying to calculate programmatically.
- **Different templates for preview and PDF:** Creates design drift. Use same template with media queries.

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| PDF page layout, headers, footers | Custom PDF layout engine | CSS @page rules + WeasyPrint | CSS Paged Media is W3C standard. WeasyPrint handles pagination, page breaks, running elements. Custom solutions miss edge cases (orphans/widows, table splitting). |
| Page numbering | Python loop to count pages | CSS counter(page) / counter(pages) | WeasyPrint calculates pages after layout. You can't know page count until rendering completes. CSS counters are automatic. |
| Word document structure | XML manipulation of .docx | python-docx API | .docx is ZIP of XML. Hand-editing XML breaks easily. python-docx abstracts complexity, handles relationships/styles/numbering. |
| Audit trail timestamp formatting | Custom date formatters | ISO 8601 with datetime.isoformat() | ISO 8601 is international standard for timestamps. Unambiguous, sortable, machine-readable. Government compliance expects this format. |
| Table styling in PDFs | Inline styles on every cell | CSS classes + WeasyPrint | WeasyPrint fully supports CSS. Use semantic classes, apply styles in CSS. Cleaner HTML, easier maintenance. |
| Section breaks / page breaks | Manual div positioning | CSS page-break-before/after | Browser print engines handle page breaks. WeasyPrint respects CSS page-break properties. Automatic, no manual calculation. |

**Key insight:** WeasyPrint is a full browser rendering engine for print. Don't try to calculate layout manually - define desired output with CSS and let WeasyPrint handle the complexity.

## Common Pitfalls

### Pitfall 1: WeasyPrint Can't Find Static Assets (CSS/Images)
**What goes wrong:** PDF renders but CSS doesn't apply, or images show as broken.

**Why it happens:** WeasyPrint needs absolute URLs or proper base_url to resolve relative paths in HTML. Flask url_for() generates relative URLs in templates.

**How to avoid:**
- Use Flask-WeasyPrint's HTML() and CSS() instead of weasyprint directly (handles Flask routing)
- Always pass base_url: `HTML(string=html, base_url=request.url_root)`
- For images, use absolute URLs or url_for('static', filename='...', _external=True)

**Warning signs:** PDF has content but no styling, or image placeholder boxes.

### Pitfall 2: Large CSS Frameworks Kill Performance
**What goes wrong:** PDF generation takes 30+ seconds for simple documents.

**Why it happens:** WeasyPrint processes all CSS rules against all HTML elements. Bootstrap/Tailwind have thousands of unused rules. Tables with many rows compound this (O(n*m) complexity).

**How to avoid:**
- Don't import full Bootstrap/Tailwind for PDFs
- Write minimal custom CSS specific to export layout
- Use simple table markup without nested divs
- Avoid CSS frameworks designed for interactive web (not print)

**Warning signs:** PDF generation timeout, high CPU usage, exponentially slower with more content.

### Pitfall 3: Forgetting to Declare Running Elements Before Use
**What goes wrong:** Headers/footers don't appear, or only appear on last page.

**Why it happens:** CSS running elements must be defined in HTML before they can be referenced in @page margin boxes. HTML is parsed top-to-bottom.

**How to avoid:**
- Place header element definitions near top of HTML body
- Use `position: running(name)` on element to remove from normal flow
- Content becomes available to @page after element is parsed

**Warning signs:** Footer only on last page, header missing entirely, console warnings about undefined running elements.

### Pitfall 4: Word Document Styling Breaks on Opening
**What goes wrong:** Document opens but formatting is wrong, or Word shows repair dialog.

**Why it happens:** python-docx generates valid .docx XML, but incorrect use of API can create malformed relationships or missing style definitions.

**How to avoid:**
- Always use built-in styles when possible: `doc.add_paragraph(text, style='List Bullet')`
- Don't manually edit paragraph._element XML unless necessary
- Test generated .docx files by opening in Word (not just viewing in browser)
- Use table.style with built-in Word table styles (e.g., 'Light Grid Accent 1')

**Warning signs:** Word asks to repair document, formatting lost on open, images disappear.

### Pitfall 5: Audit Trail Missing Critical Metadata
**What goes wrong:** Compliance review fails because audit trail doesn't capture required information per Directive 6.2.7.

**Why it happens:** Developers focus on technical implementation, miss regulatory requirements for "decisions made or assisted by automated systems."

**How to avoid:**
- Capture manager selections with timestamps at time of selection (not export time)
- Store selection metadata in frontend localStorage alongside selections
- Include: what was selected, when, from which NOC source attribute, for which JD element
- Reference specific Directive section numbers in appendix headings

**Warning signs:** Timestamp shows export time (not selection time), missing "why this statement" rationale, no traceability to NOC source.

### Pitfall 6: Security Vulnerability in URL Fetcher (CVE-2025-68616)
**What goes wrong:** WeasyPrint <68.0 has security vulnerability if using untrusted HTML or custom URL fetchers.

**Why it happens:** WeasyPrint 67.x and earlier have CVE-2025-68616 affecting default_url_fetcher.

**How to avoid:**
- Use WeasyPrint 68.0 or later (released January 19, 2026)
- Don't render untrusted user HTML through WeasyPrint
- This project's HTML is from controlled templates, so risk is low, but stay current

**Warning signs:** Using WeasyPrint <68.0, security scanner flags CVE-2025-68616.

## Code Examples

Verified patterns from official sources:

### Flask-WeasyPrint PDF Generation Endpoint
```python
# Source: Flask-WeasyPrint official documentation
from flask import Blueprint, render_template, request, jsonify
from flask_weasyprint import HTML, render_pdf
from src.services.export_service import build_export_data
from src.models.export_models import ExportRequest

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/export/pdf', methods=['POST'])
def export_pdf():
    """Generate PDF from manager's selections."""
    try:
        # Parse request body
        export_req = ExportRequest(**request.json)

        # Build export data from selections + metadata
        data = build_export_data(export_req)

        # Render template (same one used for preview)
        html = render_template('export/jd_pdf.html', **data)

        # Generate PDF with Flask-WeasyPrint
        # render_pdf() returns Response with correct headers
        return render_pdf(
            HTML(string=html, base_url=request.url_root),
            download_filename=f"JD-{data['noc_code']}.pdf"
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### CSS Print Styles with @page Rules
```css
/* Source: WeasyPrint Tips & Tricks documentation */
/* static/css/export_print.css */

@media print {
  /* Page setup */
  @page {
    size: letter portrait;
    margin: 1in 0.75in 1in 0.75in;

    /* Header on every page */
    @top-center {
      content: string(job-title) " (" string(noc-code) ")";
      font-family: "Lato", sans-serif;
      font-size: 10pt;
      color: #26374a;
      padding-bottom: 0.25in;
      border-bottom: 1pt solid #26374a;
    }

    /* Footer left: compliance reference */
    @bottom-left {
      content: "Compliant with TBS Directive 32592";
      font-size: 8pt;
      color: #666;
    }

    /* Footer right: page numbers */
    @bottom-right {
      content: "Page " counter(page) " of " counter(pages);
      font-size: 8pt;
      color: #666;
    }
  }

  /* Separate first page (cover) - no header */
  @page :first {
    @top-center {
      content: none;
    }
  }

  /* Appendix pages - different header */
  @page appendix {
    @top-center {
      content: "Appendix: Compliance Metadata";
    }
  }

  /* Apply appendix page style to appendix section */
  .compliance-appendix {
    page: appendix;
    page-break-before: always;
  }

  /* Running elements for header content */
  .job-title-running {
    position: running(job-title);
  }

  .noc-code-running {
    position: running(noc-code);
  }

  /* String-set for dynamic header content */
  h1.job-title {
    string-set: job-title content();
  }

  .noc-code {
    string-set: noc-code content();
  }

  /* Table styling for compliance data */
  table.compliance-table {
    width: 100%;
    border-collapse: collapse;
    margin: 1em 0;
  }

  table.compliance-table th {
    background-color: #26374a;
    color: white;
    padding: 8px;
    text-align: left;
    font-weight: 600;
  }

  table.compliance-table td {
    padding: 8px;
    border-bottom: 1px solid #ddd;
  }

  /* Avoid breaks inside important elements */
  .selection-entry,
  .metadata-block {
    page-break-inside: avoid;
  }

  /* Force breaks before major sections */
  h1 {
    page-break-before: always;
  }

  h1:first-of-type {
    page-break-before: avoid; /* Don't break before first heading */
  }
}
```

### Export Data Model with Pydantic
```python
# Source: Pydantic documentation + project patterns
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class SelectionMetadata(BaseModel):
    """Manager's selection with audit trail."""
    jd_element: str  # "Key Activities", "Skills", etc.
    text: str
    source_attribute: str  # NOC attribute name
    source_url: str
    selected_at: datetime  # When manager selected (not export time)

class AIMetadata(BaseModel):
    """AI-generated content disclosure."""
    model: str  # e.g., "claude-sonnet-3-5-20240620"
    timestamp: datetime
    input_count: int  # Number of statements used as input
    content_type: str  # "General Overview"

class ExportRequest(BaseModel):
    """Request body for export endpoints."""
    noc_code: str
    job_title: str
    selections: List[SelectionMetadata]
    ai_metadata: Optional[AIMetadata] = None
    source_metadata: dict  # NOC source metadata (URL, version, scraped_at)

class ExportData(BaseModel):
    """Complete data structure for PDF/Word generation."""
    noc_code: str
    job_title: str
    general_overview: Optional[str] = None
    key_activities: List[str]
    skills: List[str]
    effort: List[str]
    responsibility: List[str]
    working_conditions: List[str]
    manager_selections: List[SelectionMetadata]
    ai_metadata: Optional[AIMetadata] = None
    source_metadata: dict
    generated_at: datetime = Field(default_factory=datetime.utcnow)
```

### Building Compliance Appendix Data
```python
# Source: Best practices synthesis from audit trail requirements
from datetime import datetime
from src.models.export_models import ExportData, SelectionMetadata

def build_export_data(export_request):
    """Build complete export data structure from request."""

    # Organize selections by JD element
    selections_by_element = {}
    for selection in export_request.selections:
        if selection.jd_element not in selections_by_element:
            selections_by_element[selection.jd_element] = []
        selections_by_element[selection.jd_element].append(selection.text)

    # Build structured export data
    export_data = ExportData(
        noc_code=export_request.noc_code,
        job_title=export_request.job_title,
        general_overview=generate_general_overview(export_request),  # LLM call
        key_activities=selections_by_element.get('Key Activities', []),
        skills=selections_by_element.get('Skills', []),
        effort=selections_by_element.get('Effort', []),
        responsibility=selections_by_element.get('Responsibility', []),
        working_conditions=selections_by_element.get('Working Conditions', []),
        manager_selections=export_request.selections,
        ai_metadata=export_request.ai_metadata,
        source_metadata=export_request.source_metadata,
        generated_at=datetime.utcnow()
    )

    return export_data.model_dump()
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| wkhtmltopdf (via pdfkit) | WeasyPrint | 2020 (wkhtmltopdf deprecated) | WeasyPrint is actively maintained, pure Python, better CSS support, no system dependencies |
| ReportLab low-level API | HTML/CSS with WeasyPrint | ~2018 | HTML/CSS workflow aligns with web preview, designers can style without Python knowledge |
| Manual XML editing for .docx | python-docx API | ~2015 | API abstracts complexity, prevents malformed documents, better maintainability |
| CSS2 for print (@page basic) | CSS Paged Media Level 3 | ~2020 | Running elements, string-set, named pages enable sophisticated headers/footers without JavaScript |
| Separate preview and PDF templates | Unified template with @media print | 2021+ | Eliminates design drift, single source of truth, easier maintenance |

**Deprecated/outdated:**
- **wkhtmltopdf:** Last release 2020, based on old Qt WebKit, no longer maintained. Use WeasyPrint instead.
- **xhtml2pdf (pisa):** Limited CSS support, poor table handling. Use WeasyPrint for modern HTML/CSS.
- **Manually creating page numbers in PDFs:** Use CSS counter(page) and counter(pages) automatically provided by Paged Media.
- **Storing audit trail in separate system:** Build compliance metadata into document itself per Directive 6.2.7 requirements.

## Open Questions

Things that couldn't be fully resolved:

1. **Frontend selection timestamp capture**
   - What we know: Directive 6.2.7 requires documenting "when" decisions were made
   - What's unclear: Current Phase 2 localStorage stores selections but may not capture timestamps
   - Recommendation: Verify Phase 2 implementation includes timestamp on each selection. If not, add `selectedAt: new Date().toISOString()` when manager selects statement. Frontend should pass timestamps to export endpoint.

2. **LLM API response metadata capture**
   - What we know: AI disclosure requires model name and timestamp
   - What's unclear: Whether Phase 3 LLM integration captures and returns model metadata
   - Recommendation: Phase 3 should return AI metadata alongside generated content. Export endpoint expects this in ExportRequest.ai_metadata field.

3. **Production PDF generation performance**
   - What we know: WeasyPrint can be slow for complex documents, async generation recommended for production
   - What's unclear: Whether MVP needs async generation or if synchronous is acceptable
   - Recommendation: Start with synchronous generation (simpler). If PDF export takes >5 seconds in testing, add Celery task queue in future phase. For 1-2 page JDs, synchronous should be fine.

4. **Word document page numbering**
   - What we know: python-docx supports headers/footers but page numbering requires field codes
   - What's unclear: How complex is adding page numbers to Word footers programmatically
   - Recommendation: Start without page numbers in Word (editable version, manager can add). If required, investigate python-docx field code insertion or accept "Page X" placeholder text.

## Sources

### Primary (HIGH confidence)
- WeasyPrint 68.0 documentation - https://doc.courtbouillon.org/weasyprint/stable/ - Version confirmation, architecture
- Flask-WeasyPrint 1.1.0 documentation - https://doc.courtbouillon.org/flask-weasyprint/stable/ - Integration patterns
- python-docx 1.2.0 documentation - https://python-docx.readthedocs.io/en/latest/ - API capabilities, headers/footers/tables
- Canada Directive on Automated Decision-Making - https://www.tbs-sct.canada.ca/pol/doc-eng.aspx?id=32592 - Section 6.2.7, 6.3.5 requirements
- WeasyPrint Tips & Tricks - https://doc.courtbouillon.org/weasyprint/v52.5/tips-tricks.html - CSS @page patterns, running elements

### Secondary (MEDIUM confidence)
- [How to Generate PDFs in Python: 8 Tools Compared (Updated for 2025)](https://templated.io/blog/generate-pdfs-in-python-with-libraries/) - Library comparison
- [Build Modern, Print-Ready PDFs with Python, Flask & WeasyPrint](https://www.incentius.com/blog-posts/build-modern-print-ready-pdfs-with-python-flask-weasyprint/) - Flask integration patterns
- [Audit Trail Requirements: Guidelines for Compliance and Best Practices](https://www.inscopehq.com/post/audit-trail-requirements-guidelines-for-compliance-and-best-practices) - Audit trail structure
- [Running Headers and Footers | PrintCSS](https://printcss.net/articles/running-headers-and-footers) - CSS Paged Media patterns
- [How to Create an Appendix in Research Paper: Complete Guide 2026](https://www.automateed.com/how-to-create-an-appendix) - Appendix formatting standards

### Tertiary (LOW confidence)
- [Common Use Cases - WeasyPrint 68.0 documentation](https://doc.courtbouillon.org/weasyprint/stable/common_use_cases.html) - Pitfalls and troubleshooting (marked for validation in testing)
- [Flask PDF generation performance memory issues best practices 2026](https://glinteco.com/en/post/flask-application-cleanup-and-optimization/) - WebSearch compilation, needs validation
- [WeasyPrint consumes a lot of memory for long documents · Issue #671](https://github.com/Kozea/WeasyPrint/issues/671) - Performance considerations (2019 issue, may be outdated)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - WeasyPrint 68.0 and python-docx 1.2.0 verified from official documentation, currently maintained, widely used
- Architecture: HIGH - Flask-WeasyPrint patterns from official docs, CSS @page from W3C Paged Media spec
- Pitfalls: MEDIUM - Synthesized from documentation, GitHub issues, and community articles; needs validation in project context
- Compliance requirements: HIGH - Directive sections verified from official Canada.ca source

**Research date:** 2026-01-22
**Valid until:** 2026-02-22 (30 days - stable domain, WeasyPrint updates quarterly, python-docx stable)
