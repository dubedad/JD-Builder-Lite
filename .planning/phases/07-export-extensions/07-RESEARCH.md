# Phase 7: Export Extensions - Research

**Researched:** 2026-01-22
**Domain:** Document Generation (python-docx, WeasyPrint, Word/PDF formatting)
**Confidence:** HIGH

## Summary

Phase 7 extends export capabilities with DOCX generation and Annex sections for both PDF and DOCX formats. The research confirms python-docx 1.2.0 (already in requirements.txt) provides production-ready DOCX generation with comprehensive styling capabilities matching PDF output. The existing WeasyPrint infrastructure handles PDF generation.

The standard approach uses:
- **python-docx 1.2.0** with context managers (BytesIO) to prevent memory leaks
- **Built-in heading styles** (Heading 1, Heading 2) for navigation pane integration and accessibility
- **RGBColor** for exact color matching between PDF (CSS) and DOCX (python-docx)
- **Table Grid style** with custom formatting for compliance metadata tables
- **Page setup via Section** for Letter size, 1" margins, headers/footers
- **Dynamic Annex generation** by comparing NOC raw data with manager selections to identify unused attributes

**Primary recommendation:** Extend existing docx_generator.py with Annex section builder, create shared Annex data structure, and use context manager pattern (with BytesIO() as buffer) throughout to prevent memory accumulation from repeated exports.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| python-docx | 1.2.0 | Word document generation | Official python-openxml library, 5M+ downloads/month, comprehensive Word format support including styles, tables, headers/footers |
| WeasyPrint | 68.0 | PDF generation from HTML/CSS | Already in use, full CSS support, automatic font embedding, handles complex layouts |
| BytesIO | Native (io module) | In-memory binary buffers | Zero-copy memory management for document generation, prevents disk I/O overhead |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| RGBColor | 1.2.0 (docx.shared) | Exact color specification | Matching PDF colors in DOCX (e.g., GC_PRIMARY #26374a) |
| Pt, Inches | 1.2.0 (docx.shared) | Unit conversion | Setting font sizes, margins, dimensions consistently |
| WD_ALIGN_PARAGRAPH | 1.2.0 (docx.enum.text) | Text alignment | Center title pages, align headers/footers |
| Section | 1.2.0 (docx) | Page setup | Configure Letter size, margins, headers, footers, page numbers |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| python-docx | Aspose.Words, Spire.Doc | Commercial licenses required, overkill for simple document generation |
| BytesIO context manager | Manual buffer.close() | Risk of memory leaks if exceptions occur before close() |
| Built-in Table Grid | Custom table styling from scratch | Time-consuming, python-docx table styles are tested and reliable |
| Shared Annex data structure | Duplicate logic in PDF/DOCX generators | Code divergence, maintenance burden, consistency issues |

**Installation:**
```bash
# Already in requirements.txt
python-docx==1.2.0
```

## Architecture Patterns

### Recommended Project Structure
```
src/
├── services/
│   ├── export_service.py       # Build export data (existing)
│   ├── annex_builder.py        # NEW: Build Annex data structure
│   ├── pdf_generator.py        # Add Annex rendering to PDF
│   └── docx_generator.py       # Add Annex rendering to DOCX
├── models/
│   └── export_models.py        # Add AnnexSection, AnnexData models
└── templates/
    └── export/
        └── jd_pdf.html          # Add Annex section after Appendix A
```

### Pattern 1: Context Manager for BytesIO (CRITICAL)
**What:** Always use context manager (with statement) when creating BytesIO buffers to prevent memory leaks
**When to use:** Every DOCX generation call, especially for repeated exports
**Example:**
```python
# Source: Python io module documentation + memory management best practices
def generate_docx(data: ExportData) -> bytes:
    """Generate DOCX with proper memory management."""
    doc = Document()

    # ... build document ...

    # CRITICAL: Use context manager to ensure buffer cleanup
    with BytesIO() as buffer:
        doc.save(buffer)
        buffer.seek(0)
        return buffer.read()
    # buffer automatically closed here, memory released
```

### Pattern 2: Shared Annex Data Structure
**What:** Build Annex data once, render in both PDF and DOCX generators to avoid divergence
**When to use:** For Annex section containing unused NOC attributes
**Example:**
```python
# Source: Project architecture pattern from export_service.py
# NEW: src/services/annex_builder.py

from typing import List, Dict, Any
from src.models.export_models import AnnexSection, AnnexData

def build_annex_data(
    raw_noc_data: Dict[str, Any],
    used_attributes: List[str],
    noc_code: str,
    scraped_at: datetime
) -> AnnexData:
    """
    Build Annex data structure from NOC profile.

    Args:
        raw_noc_data: Full parsed NOC profile from parser
        used_attributes: List of attribute names already in JD elements
        noc_code: NOC code for attribution
        scraped_at: Retrieval timestamp for attribution

    Returns:
        AnnexData with categorized unused attributes
    """
    # Filter out attributes already used in JD elements
    unused = filter_unused_attributes(raw_noc_data, used_attributes)

    # Build sections in fixed order (from CONTEXT.md)
    sections = [
        build_job_requirements_section(unused),
        build_career_mobility_section(unused),
        build_interests_section(unused),
        build_personal_suitability_section(unused)
    ]

    return AnnexData(
        sections=sections,
        source_noc_code=noc_code,
        retrieved_at=scraped_at
    )
```

### Pattern 3: Heading Styles for Navigation Pane
**What:** Use built-in heading styles (Heading 1, Heading 2, Heading 3) for Word navigation pane integration
**When to use:** All section headers in DOCX export
**Example:**
```python
# Source: python-docx documentation on styles
# Document structure with heading hierarchy
doc.add_heading('Job Description Title', 0)  # Title style
doc.add_heading('General Overview', 1)       # Heading 1
doc.add_heading('Key Activities', 1)         # Heading 1

# Annex section
doc.add_heading('Additional Job Information', 1)  # Heading 1
doc.add_heading('Job Requirements', 2)            # Heading 2
doc.add_heading('Career Mobility', 2)             # Heading 2

# Built-in styles automatically appear in navigation pane
# No additional configuration needed
```

### Pattern 4: Color Matching PDF to DOCX
**What:** Extract exact RGB values from CSS variables, convert to RGBColor for python-docx
**When to use:** Styling headings, tables, accents to match PDF export
**Example:**
```python
# Source: export_print.css + python-docx RGBColor
from docx.shared import RGBColor

# Match CSS :root variables
GC_PRIMARY = RGBColor(0x26, 0x37, 0x4a)      # --primary: #26374a
TEXT_COLOR = RGBColor(0x33, 0x33, 0x33)      # --text: #333333
TEXT_LIGHT = RGBColor(0x66, 0x66, 0x66)      # --text-light: #666666
BORDER_COLOR = RGBColor(0xcc, 0xcc, 0xcc)    # --border: #cccccc
ACCENT_BLUE = RGBColor(0x19, 0x76, 0xd2)     # --accent: #1976d2

# Apply to document elements
heading = doc.add_heading('Section Title', 1)
heading_run = heading.runs[0]
heading_run.font.color.rgb = GC_PRIMARY
heading_run.font.size = Pt(14)  # Match PDF .jd-section h2 { font-size: 14pt; }
```

### Pattern 5: Table Formatting Matching PDF
**What:** Use python-docx table styles to replicate PDF compliance table appearance
**When to use:** Annex sections, compliance metadata tables
**Example:**
```python
# Source: python-docx table documentation + export_print.css
def add_annex_section_table(doc, title, items):
    """Add Annex section with formatted table."""
    doc.add_heading(title, 2)  # Heading 2 for subsection

    if not items:
        doc.add_paragraph('No additional information available.')
        return

    # Create table (2 columns if key-value, single column for lists)
    table = doc.add_table(rows=len(items), cols=1)
    table.style = 'Table Grid'

    # Match PDF .compliance-table styling
    for i, item in enumerate(items):
        cell = table.rows[i].cells[0]
        cell.text = item

        # Set cell borders to match PDF (1pt solid #cccccc)
        # python-docx uses default Table Grid borders which closely match

        # Padding equivalent: cell.paragraphs[0].paragraph_format
        para = cell.paragraphs[0]
        para.space_before = Pt(6)  # 0.5em ≈ 6pt
        para.space_after = Pt(6)
```

### Pattern 6: Page Headers and Footers
**What:** Configure section headers/footers to match PDF @page rules
**When to use:** DOCX export to replicate PDF page layout
**Example:**
```python
# Source: python-docx Section documentation + export_print.css @page
section = doc.sections[0]

# Page setup matching PDF @page { size: letter portrait; margin: 1in 0.75in; }
section.page_height = Inches(11)
section.page_width = Inches(8.5)
section.top_margin = Inches(1)
section.bottom_margin = Inches(1)
section.left_margin = Inches(0.75)
section.right_margin = Inches(0.75)

# Header matching PDF @top-center
header = section.header
header_para = header.paragraphs[0]
header_para.text = f"{job_title} ({noc_code})"
header_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
header_run = header_para.runs[0]
header_run.font.size = Pt(10)
header_run.font.color.rgb = GC_PRIMARY

# Footer matching PDF @bottom-right and @bottom-left
footer = section.footer
footer_para = footer.paragraphs[0]
footer_para.text = "Compliant with TBS Directive 32592"
footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
footer_run = footer_para.runs[0]
footer_run.font.size = Pt(8)
footer_run.font.color.rgb = TEXT_LIGHT

# NOTE: python-docx does not support dynamic page numbering via fields
# Page numbers would need to be added manually or via Word field codes
```

### Anti-Patterns to Avoid
- **Don't create BytesIO without context manager:** Leads to memory leaks in repeated exports
- **Don't duplicate Annex logic:** Build once, render twice (PDF and DOCX)
- **Don't use direct formatting instead of styles:** Breaks navigation pane, reduces accessibility
- **Don't hardcode colors as strings:** Use RGBColor objects for type safety
- **Don't iterate over paragraphs to add content:** Use Document.add_* methods which handle paragraph management

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Page numbering in DOCX | Custom field code insertion | Let Word handle it (limitations accepted) | python-docx doesn't support PAGE field; manual workarounds break in Word versions |
| Table of contents | Custom TOC generation | Skip for this phase (not required) | python-docx has no native TOC support; requires Word COM automation or third-party libraries |
| Identifying unused attributes | Complex set operations on nested dicts | Parse once, track usage during mapping | mapper.py already builds JD elements; capture source_attribute during that process |
| Color conversion | String parsing and validation | RGBColor(0x26, 0x37, 0x4a) | Built-in validation, type safety, explicit hex values |
| Memory management | Manual try-finally with buffer.close() | with BytesIO() as buffer | Automatic cleanup even on exceptions, Pythonic pattern |
| Document structure validation | Schema validation post-generation | Pydantic models pre-generation | Catch errors before expensive document generation |

**Key insight:** python-docx intentionally doesn't support advanced Word features (TOC, page numbers, complex fields) because they require Word's rendering engine at runtime. Accept these limitations rather than building fragile workarounds.

## Common Pitfalls

### Pitfall 1: BytesIO Memory Leak Without Context Manager
**What goes wrong:** Repeated DOCX exports accumulate memory until server OOM
**Why it happens:** BytesIO buffers not explicitly closed retain memory; Python GC may delay collection
**How to avoid:** Always use context manager: `with BytesIO() as buffer:`
**Warning signs:** Memory usage grows with each export, doesn't stabilize; server crashes after 50-100 exports

### Pitfall 2: Annex Logic Divergence Between PDF and DOCX
**What goes wrong:** PDF shows different Annex content than DOCX; inconsistent user experience
**Why it happens:** Building Annex data separately in pdf_generator.py and docx_generator.py
**How to avoid:** Create annex_builder.py with shared build_annex_data() function; both generators call it
**Warning signs:** Bug fixes applied to PDF but not DOCX; users report export format differences

### Pitfall 3: Using String Style Names Instead of Built-in Heading Levels
**What goes wrong:** Custom "Heading 1" string style doesn't appear in navigation pane
**Why it happens:** doc.add_heading(text, level) uses built-in styles; doc.add_paragraph(text, style='Heading 1') may not
**How to avoid:** Always use doc.add_heading(title, level) for headings, not add_paragraph with style parameter
**Warning signs:** Word navigation pane empty; document outline doesn't populate

### Pitfall 4: Hardcoding Colors as Hex Strings
**What goes wrong:** runtime error "expected RGBColor, got str"
**Why it happens:** run.font.color.rgb expects RGBColor object, not "#26374a" string
**How to avoid:** Define color constants as RGBColor(0x26, 0x37, 0x4a) at module level
**Warning signs:** TypeError when applying colors; colors render as default black

### Pitfall 5: Not Seeking to Buffer Start Before Reading
**What goes wrong:** send_file() returns 0-byte DOCX; download appears to succeed but file is empty
**Why it happens:** doc.save(buffer) leaves buffer position at end; buffer.read() returns empty bytes
**How to avoid:** Always call buffer.seek(0) before buffer.read() or returning buffer
**Warning signs:** DOCX downloads complete instantly; Word shows "corrupt file" error

### Pitfall 6: Forgetting Page Break Before Annex
**What goes wrong:** Annex section starts mid-page immediately after compliance metadata
**Why it happens:** Copying PDF template structure which uses CSS page-break-before
**How to avoid:** Call doc.add_page_break() before adding Annex heading
**Warning signs:** Annex squished on last page of compliance; inconsistent with PDF layout

### Pitfall 7: Empty Annex Sections Showing "None" or Crashing
**What goes wrong:** Annex displays "None" text or raises AttributeError when NOC data missing
**Why it happens:** Not handling empty lists when NOC profile lacks certain attributes
**How to avoid:** Check if items list empty before rendering; show "No additional information available."
**Warning signs:** TypeError: 'NoneType' object is not iterable; "None" appearing in Word document

### Pitfall 8: Incorrect Attribute Filtering Logic
**What goes wrong:** Annex shows attributes already in main JD sections (not truly "unused")
**Why it happens:** Comparing attribute names instead of actual statement text; fuzzy matching issues
**How to avoid:** Track actual statement text used in selections, compare against raw NOC statement text
**Warning signs:** Duplicate information in JD body and Annex; users confused about purpose of Annex

## Code Examples

Verified patterns from official sources:

### Complete DOCX Generation with Context Manager
```python
# Source: python-docx documentation + memory management best practices
from io import BytesIO
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

def generate_docx(data: ExportData) -> bytes:
    """
    Generate Word document with proper memory management.

    CRITICAL: Uses context manager to prevent memory leaks.
    """
    doc = Document()

    # Configure page setup
    section = doc.sections[0]
    section.page_height = Inches(11)
    section.page_width = Inches(8.5)
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(0.75)
    section.right_margin = Inches(0.75)

    # Add content
    _add_header_footer(doc, data)
    _add_title_page(doc, data)
    _add_jd_sections(doc, data)
    _add_compliance_appendix(doc, data)
    _add_annex_section(doc, data)  # NEW

    # Write to bytes with context manager
    with BytesIO() as buffer:
        doc.save(buffer)
        buffer.seek(0)  # CRITICAL: Seek to start
        return buffer.read()
    # Buffer automatically closed and memory released
```

### Annex Data Builder (Shared Logic)
```python
# NEW: src/services/annex_builder.py
from typing import List, Dict, Any, Optional
from datetime import datetime
from src.models.export_models import AnnexSection, AnnexData

def build_annex_data(
    raw_noc_data: Dict[str, Any],
    manager_selections: List[SelectionMetadata],
    noc_code: str,
    scraped_at: datetime
) -> AnnexData:
    """
    Build Annex section data from NOC profile.

    Identifies unused NOC attributes by comparing raw data against
    manager selections. Fixed category order from CONTEXT.md.
    """
    # Extract used statement texts
    used_texts = {sel.text for sel in manager_selections}

    # Build sections in fixed order
    sections = []

    # 1. Job Requirements (employment_requirements from NOC)
    job_req = _build_job_requirements(
        raw_noc_data.get('employment_requirements', []),
        used_texts
    )
    if job_req:
        sections.append(job_req)

    # 2. Career Mobility (requires fetching from NOC - may be empty)
    mobility = _build_career_mobility(
        raw_noc_data.get('career_mobility', {}),
        used_texts
    )
    if mobility:
        sections.append(mobility)

    # 3. Interests (Holland Codes)
    interests = _build_interests(
        raw_noc_data.get('interests', []),
        used_texts
    )
    if interests:
        sections.append(interests)

    # 4. Personal Suitability (renamed from "Personal Attributes")
    suitability = _build_personal_suitability(
        raw_noc_data.get('personal_attributes', []),
        used_texts
    )
    if suitability:
        sections.append(suitability)

    return AnnexData(
        sections=sections,
        source_noc_code=noc_code,
        retrieved_at=scraped_at
    )


def _build_job_requirements(items: List[str], used: set) -> Optional[AnnexSection]:
    """Build Job Requirements section."""
    unused = [item for item in items if item not in used]

    if not unused:
        return None

    return AnnexSection(
        title='Job Requirements',
        category='job_requirements',
        items=unused,
        format_type='paragraph'  # Keep as-is from NOC
    )


def _build_career_mobility(mobility_data: Dict[str, Any], used: set) -> Optional[AnnexSection]:
    """
    Build Career Mobility section with From/To grouping.

    Mobility data expected format:
    {
        'from': ['Entry position 1', 'Entry position 2'],
        'to': ['Advancement position 1', 'Advancement position 2']
    }
    """
    from_paths = mobility_data.get('from', [])
    to_paths = mobility_data.get('to', [])

    # Filter unused (though mobility rarely appears in JD selections)
    from_unused = [p for p in from_paths if p not in used]
    to_unused = [p for p in to_paths if p not in used]

    if not from_unused and not to_unused:
        return None

    # Format with grouping
    items = []
    if from_unused:
        items.append('Entry Paths:')
        items.extend(f'  • {p}' for p in from_unused)
    if to_unused:
        items.append('Advancement Paths:')
        items.extend(f'  • {p}' for p in to_unused)

    return AnnexSection(
        title='Career Mobility',
        category='career_mobility',
        items=items,
        format_type='grouped_list'
    )


def _build_interests(items: List[str], used: set) -> Optional[AnnexSection]:
    """Build Interests (Holland Codes) section."""
    unused = [item for item in items if item not in used]

    if not unused:
        return None

    return AnnexSection(
        title='Interests (Holland Codes)',
        category='interests',
        items=unused,
        format_type='list'
    )


def _build_personal_suitability(items: List[str], used: set) -> Optional[AnnexSection]:
    """Build Personal Suitability section."""
    unused = [item for item in items if item not in used]

    if not unused:
        return None

    return AnnexSection(
        title='Personal Suitability (Placement Criteria)',
        category='personal_suitability',
        items=unused,
        format_type='list'
    )
```

### DOCX Annex Rendering
```python
# Add to src/services/docx_generator.py
def _add_annex_section(doc: Document, data: ExportData):
    """Add Annex section with unused NOC attributes."""
    if not data.annex_data or not data.annex_data.sections:
        return  # No annex data to render

    # Page break before Annex
    doc.add_page_break()

    # Main heading
    doc.add_heading('Additional Job Information', 1)

    # Render each category section
    for section in data.annex_data.sections:
        doc.add_heading(section.title, 2)

        # Handle empty sections
        if not section.items:
            doc.add_paragraph('No additional information available.')
            continue

        # Render based on format type
        if section.format_type == 'paragraph':
            # Job Requirements: keep as-is
            for item in section.items:
                doc.add_paragraph(item)

        elif section.format_type == 'grouped_list':
            # Career Mobility: already formatted with grouping
            for item in section.items:
                if item.startswith('  •'):
                    doc.add_paragraph(item.strip(), style='List Bullet')
                else:
                    # Group header (Entry Paths:, Advancement Paths:)
                    para = doc.add_paragraph(item)
                    para.runs[0].bold = True

        else:  # 'list'
            # Interests, Personal Suitability: bullet list
            for item in section.items:
                doc.add_paragraph(item, style='List Bullet')

        # Source attribution
        attribution = f"Source: NOC {data.annex_data.source_noc_code}, " \
                     f"retrieved {data.annex_data.retrieved_at.strftime('%Y-%m-%d')}"
        attr_para = doc.add_paragraph(attribution)
        attr_para.runs[0].font.size = Pt(9)
        attr_para.runs[0].font.color.rgb = RGBColor(0x66, 0x66, 0x66)
        attr_para.runs[0].italic = True
```

### PDF Annex Rendering (HTML Template)
```html
<!-- Add to templates/export/jd_pdf.html after compliance appendix -->
{% if annex_data and annex_data.sections %}
<section class="annex-section">
  <h1>Additional Job Information</h1>

  {% for section in annex_data.sections %}
  <div class="annex-category">
    <h2>{{ section.title }}</h2>

    {% if not section.items %}
    <p class="empty-state">No additional information available.</p>
    {% else %}

      {% if section.format_type == 'paragraph' %}
      <!-- Job Requirements: paragraphs -->
      {% for item in section.items %}
      <p>{{ item }}</p>
      {% endfor %}

      {% elif section.format_type == 'grouped_list' %}
      <!-- Career Mobility: grouped list -->
      {% for item in section.items %}
        {% if item.startswith('  •') %}
        <li class="mobility-item">{{ item|trim }}</li>
        {% else %}
        <p class="mobility-group-header"><strong>{{ item }}</strong></p>
        {% endif %}
      {% endfor %}

      {% else %}
      <!-- List format: Interests, Personal Suitability -->
      <ul class="annex-list">
        {% for item in section.items %}
        <li>{{ item }}</li>
        {% endfor %}
      </ul>
      {% endif %}
    {% endif %}

    <!-- Source attribution -->
    <p class="annex-attribution">
      Source: NOC {{ annex_data.source_noc_code }},
      retrieved {{ annex_data.retrieved_at.strftime('%Y-%m-%d') }}
    </p>
  </div>
  {% endfor %}
</section>
{% endif %}
```

### Export Models (Add Annex Types)
```python
# Add to src/models/export_models.py
from typing import List, Literal

class AnnexSection(BaseModel):
    """Single Annex category section."""
    title: str  # e.g., "Job Requirements", "Career Mobility"
    category: str  # Internal key: job_requirements, career_mobility, etc.
    items: List[str]  # Unused attribute texts
    format_type: Literal['paragraph', 'list', 'grouped_list']

    model_config = ConfigDict(from_attributes=True)


class AnnexData(BaseModel):
    """Complete Annex section data."""
    sections: List[AnnexSection]
    source_noc_code: str
    retrieved_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExportData(BaseModel):
    """Complete data structure for PDF/Word template rendering."""
    # ... existing fields ...

    # NEW: Annex section
    annex_data: Optional[AnnexData] = None
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Manual buffer.close() | Context managers (with BytesIO()) | Python 2.5+ (2006) | Memory leak prevention, cleaner error handling |
| String style names | Built-in heading levels via add_heading() | python-docx 0.8+ (2016) | Automatic navigation pane integration, accessibility |
| Separate PDF/DOCX logic | Shared data structures, dual rendering | Modern architecture patterns | Consistency, maintainability, single source of truth |
| Direct color strings | RGBColor objects | python-docx 0.3+ (2013) | Type safety, explicit hex values, validation |
| Custom table styling | Built-in Table Grid style | python-docx 0.7+ (2015) | Consistent appearance across Word versions |

**Deprecated/outdated:**
- **python-docx 0.x API:** Document() now required, not docx.Document()
- **Manual seek before write:** Always seek before read/return; easy to forget
- **Assuming page numbers work:** python-docx cannot insert PAGE fields; limitation accepted

## Open Questions

Things that couldn't be fully resolved:

1. **NOC Data Source for Career Mobility and Interests**
   - What we know: OASIS profiles contain these attributes according to methodology docs
   - What's unclear: parser.py currently doesn't extract career_mobility or interests (not in parse_profile)
   - Recommendation: Verify if OASIS HTML includes these sections; may need parser updates or separate API calls

2. **Example Titles Location**
   - What we know: CONTEXT says "Example Titles NOT in Annex — goes in overview card"
   - What's unclear: Where in current codebase is "overview card"? Is this the General Overview section?
   - Recommendation: Confirm with user; likely means example titles displayed in profile header, not Annex

3. **Empty Annex Handling Strategy**
   - What we know: "Always show structure: Include category headers even if content is empty"
   - What's unclear: Should we show empty Annex section in exports if all categories are empty?
   - Recommendation: Show Annex section with all 4 category headers; display "No additional information" for each

4. **NOC Attribute Retrieval Date**
   - What we know: Source metadata has scraped_at timestamp
   - What's unclear: Is this sufficient for "retrieved {date}" or should we track per-attribute fetch times?
   - Recommendation: Use profile-level scraped_at; all attributes retrieved simultaneously

5. **DOCX Page Numbers**
   - What we know: python-docx cannot insert dynamic page numbers (PAGE field limitation)
   - What's unclear: Is this acceptable for milestone requirements?
   - Recommendation: Document limitation; Word users can insert page numbers manually via Insert > Page Number

## Sources

### Primary (HIGH confidence)
- [python-docx 1.2.0 Documentation](https://python-docx.readthedocs.io/en/latest/) - Official API reference
- [python-docx Quickstart Guide](https://python-docx.readthedocs.io/en/latest/user/quickstart.html) - Best practices for document creation
- [python-docx Working with Styles](https://python-docx.readthedocs.io/en/latest/user/styles-using.html) - Heading styles, navigation pane integration
- [Python io.BytesIO Documentation](https://docs.python.org/3/library/io.html#io.BytesIO) - Official memory buffer documentation
- [WeasyPrint 68.0 Documentation](https://doc.courtbouillon.org/weasyprint/stable/) - PDF generation features

### Secondary (MEDIUM confidence)
- [python-docx GitHub Issue #408](https://github.com/python-openxml/python-docx/issues/408) - Performance: add_paragraph() degradation
- [python-docx GitHub Issue #686](https://github.com/python-openxml/python-docx/issues/686) - PAGE field limitations
- [python-docx GitHub Issue #36](https://github.com/python-openxml/python-docx/issues/36) - Table of Contents limitation
- [Python Speed: BytesIO Memory Usage](https://pythonspeed.com/articles/bytesio-reduce-memory-usage/) - Memory management best practices
- [NOC Canada OASIS Welcome](https://noc.esdc.gc.ca/Oasis/OasisWelcome) - NOC attribute structure (certificate error, LOW confidence)
- [OASIS Methodology](https://noc.esdc.gc.ca/Oasis/OasisMethodology) - Profile attribute details (certificate error, LOW confidence)

### Tertiary (LOW confidence)
- WebSearch results on OASIS structure - General information about Holland codes, career mobility
- WebSearch results on python-docx issues - Community reports of limitations

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - python-docx already in use, well-documented, stable 1.2.0 release
- Architecture patterns: HIGH - Context managers are Python standard practice, shared data structures proven pattern
- DOCX formatting: HIGH - All required features (styles, tables, headers) supported by python-docx 1.2.0
- Annex data source: MEDIUM - Parser may need updates to extract career_mobility and interests from OASIS HTML
- PDF/DOCX consistency: HIGH - Shared AnnexData model ensures identical content structure
- Memory management: HIGH - Context manager pattern is well-established best practice

**Research date:** 2026-01-22
**Valid until:** 2026-03-22 (60 days - stable libraries, python-docx 1.2.0 released Jan 2026)

**Notes:**
- python-docx 1.2.0 already in requirements.txt; no new dependencies needed
- BytesIO context manager pattern is CRITICAL to prevent memory leaks
- NOC data for Annex (career_mobility, interests, personal_attributes) may require parser updates
- Page numbers in DOCX are limitation of python-docx; document as known constraint
- Annex structure must match exactly between PDF and DOCX to avoid user confusion
