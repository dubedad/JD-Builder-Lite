# Phase 13: Export Enhancement - Research

**Researched:** 2026-02-03
**Domain:** PDF/DOCX rendering of styled content, dual-format display, compliance metadata extension
**Confidence:** HIGH

## Summary

This phase extends existing export infrastructure (Phase 7) to render styled content using display patterns established in Phase 11. The research examined the current export architecture (WeasyPrint for PDF, python-docx for DOCX), the styled content models from Phase 11 (StyledStatement, VocabularyAudit, GenerationAttempt), and best practices for representing interactive UI elements (collapsible/expandable content) in static document formats.

The existing codebase provides a solid foundation: pdf_generator.py with Jinja2 templates, docx_generator.py with python-docx styling, export_models.py with compliance sections, and export_print.css with WeasyPrint-compatible styling. Phase 11 added StyledStatement (with original_noc_text preserved), VocabularyAudit (with coverage metrics), and confidence thresholds (0.8/0.5 for green/yellow/red). This phase extends these to render dual-format statements in exports while maintaining visual consistency between PDF and DOCX.

The research confirms that static document representation of collapsible content is best achieved through a **stacked layout** pattern: styled text primary with original text immediately below in a visually distinct (muted, smaller) format. This mirrors how regulatory documents present "current vs. original" text and avoids footnote complexity. Confidence indicators should use **colored circles** rendered via CSS `border-radius` (PDF) and Unicode bullet characters with color (DOCX). Vocabulary audit data fits best as a **summary table in the existing compliance appendix** to avoid document bloat.

**Primary recommendation:** Extend JD element rendering to show styled + original stacked layout, add confidence indicators as colored dots, extend AI disclosure compliance section with styled content metadata and vocabulary audit summary table.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| WeasyPrint | 68.0 (existing) | PDF generation from HTML/CSS | Already in use; supports CSS3 border-radius for circles, color specifications |
| python-docx | 1.2.0 (existing) | Word document generation | Already in use; supports cell shading via OxmlElement, RGBColor for text |
| Jinja2 | (via Flask) | PDF template rendering | Already used for jd_pdf.html; conditional rendering for dual-format |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| RGBColor | 1.2.0 (docx.shared) | Confidence indicator colors | Green/yellow/red dot text coloring |
| OxmlElement | (docx.oxml) | Table cell background shading | Optional: Alternative confidence indicator as background |
| BytesIO | (io module) | Memory-safe DOCX generation | Already used with context manager pattern |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Stacked layout | Footnote references | Footnotes add complexity; stacked is clearer for 1:1 pairing |
| Stacked layout | Appendix with all originals | Separates context from content; harder to compare |
| CSS circles | Unicode symbols (DOCX) | CSS circles work only in PDF; DOCX needs Unicode characters |
| Summary vocabulary table | Detailed term breakdown | Summary sufficient for compliance; detailed adds pages without value |

**Installation:**
```bash
# No new packages - using existing stack
```

## Architecture Patterns

### Recommended Template Structure
```
templates/export/
├── jd_pdf.html           # EXTEND: Add styled statement block, confidence dots
└── jd_preview.html       # EXTEND: Match PDF changes for preview consistency
src/services/
├── pdf_generator.py      # EXTEND: Pass styled content data to template
├── docx_generator.py     # EXTEND: Add styled statement rendering, confidence dots
└── export_service.py     # EXTEND: Include styled content in ExportData
src/models/
└── export_models.py      # EXTEND: Add styled content fields to statement models
static/css/
└── export_print.css      # EXTEND: Add styled statement styles, confidence dot classes
```

### Pattern 1: Stacked Dual-Format Layout (PDF)

**What:** Render styled statement primary, original statement immediately below in muted style.
**When to use:** All statements that have styled variants.
**Recommendation:** Stacked layout chosen over footnotes or appendix per Claude's discretion.

**Rationale:**
- Stacked keeps original in context (reader can compare immediately)
- Footnotes require numbering management and interrupt reading flow
- Appendix separates content from context, making comparison difficult
- Government regulatory documents commonly use "current text / original text" stacking

**Example (PDF/HTML):**
```html
<!-- Source: Extension of existing jd_pdf.html pattern -->
<li class="jd-statement{% if statement.styled_variant %} jd-statement--styled{% endif %}">
  <div class="jd-statement__main">
    <!-- Styled or original text (primary display) -->
    <span class="jd-statement__text">
      {{ statement.styled_variant.styled_text if statement.styled_variant else statement.text }}
    </span>

    <!-- Confidence indicator (if styled) -->
    {% if statement.styled_variant %}
    <span class="jd-confidence-dot jd-confidence-dot--{{ statement.confidence_level }}"></span>
    {% endif %}

    <!-- Proficiency (existing) -->
    {% if statement.proficiency and statement.proficiency.level %}
    <span class="jd-statement__level">
      {% for i in range(statement.proficiency.level) %}●{% endfor %}{% for i in range(statement.proficiency.max - statement.proficiency.level) %}○{% endfor %}
      L{{ statement.proficiency.level }}
    </span>
    {% endif %}
  </div>

  <!-- Original NOC text (stacked below, muted style) -->
  {% if statement.styled_variant and statement.styled_variant.content_type.value == 'ai_styled' %}
  <div class="jd-statement__original">
    <span class="jd-statement__original-label">Original NOC:</span>
    {{ statement.styled_variant.original_noc_text }}
  </div>
  {% endif %}

  <!-- AI disclosure indicator -->
  {% if statement.styled_variant %}
  <span class="jd-statement__ai-label">
    {{ statement.styled_variant.disclosure_label }}
  </span>
  {% endif %}

  <!-- Source attribution (existing) -->
  <span class="jd-statement__source">Source: {{ statement.source_attribute }}</span>
</li>
```

### Pattern 2: Confidence Indicators as Colored Dots

**What:** Visual confidence indicator matching UI dots (green/yellow/red).
**When to use:** All styled statements in exports.
**Recommendation:** Colored circles chosen over text labels or symbols per Claude's discretion.

**Rationale:**
- Colored dots match UI display pattern from Phase 11
- More compact than text labels ("High Confidence")
- Universal understanding (traffic light metaphor)
- CSS border-radius works in WeasyPrint for PDF
- Unicode bullet (●) with color works in python-docx for DOCX

**CSS for PDF (add to export_print.css):**
```css
/* Source: Extension of existing export_print.css */
.jd-confidence-dot {
  display: inline-block;
  width: 8pt;
  height: 8pt;
  border-radius: 50%;
  margin-left: 0.5em;
  vertical-align: middle;
}

.jd-confidence-dot--high {
  background-color: #4caf50;  /* Green */
}

.jd-confidence-dot--medium {
  background-color: #ff9800;  /* Yellow/Amber */
}

.jd-confidence-dot--low {
  background-color: #f44336;  /* Red */
}
```

**DOCX Implementation:**
```python
# Source: Research on python-docx + existing docx_generator.py pattern
from docx.shared import RGBColor

# Confidence colors matching PDF CSS
CONFIDENCE_COLORS = {
    "high": RGBColor(0x4c, 0xaf, 0x50),    # Green #4caf50
    "medium": RGBColor(0xff, 0x98, 0x00),  # Amber #ff9800
    "low": RGBColor(0xf4, 0x43, 0x36),     # Red #f44336
}

def add_confidence_indicator(para, confidence_level: str):
    """Add colored dot indicator to paragraph.

    Uses Unicode bullet with color rather than CSS (DOCX limitation).
    """
    run = para.add_run(" ●")
    run.font.color.rgb = CONFIDENCE_COLORS.get(confidence_level, CONFIDENCE_COLORS["low"])
    run.font.size = Pt(8)
```

### Pattern 3: Original Text Muted Display (PDF + DOCX)

**What:** Show original NOC text below styled text in visually distinct format.
**When to use:** All AI_STYLED statements (not ORIGINAL_NOC fallbacks).

**CSS for PDF:**
```css
/* Source: Extension of existing .jd-statement__description pattern */
.jd-statement__original {
  margin-top: 0.5em;
  padding: 0.4em 0.6em;
  font-size: 9pt;
  line-height: 1.4;
  color: #666666;
  background: #f5f5f5;
  border-left: 2pt solid #cccccc;
}

.jd-statement__original-label {
  font-weight: 600;
  color: #888888;
  margin-right: 0.5em;
}

.jd-statement__ai-label {
  display: block;
  margin-top: 0.25em;
  font-size: 8pt;
  color: #1976d2;
  font-style: italic;
}
```

**DOCX Implementation:**
```python
# Source: Extension of existing docx_generator.py patterns
def add_styled_statement(doc, statement, styled_variant):
    """Add statement with styled content and original stacked below."""
    # Primary: Styled text
    styled_para = doc.add_paragraph()
    styled_run = styled_para.add_run(styled_variant.styled_text)

    # Add confidence indicator
    add_confidence_indicator(styled_para, get_confidence_level(styled_variant.confidence_score))

    # Secondary: Original NOC text (muted)
    if styled_variant.content_type == StyleContentType.AI_STYLED:
        original_para = doc.add_paragraph()
        original_para.paragraph_format.left_indent = Inches(0.25)

        label_run = original_para.add_run("Original NOC: ")
        label_run.font.size = Pt(9)
        label_run.font.color.rgb = RGBColor(0x88, 0x88, 0x88)
        label_run.bold = True

        text_run = original_para.add_run(styled_variant.original_noc_text)
        text_run.font.size = Pt(9)
        text_run.font.color.rgb = RGBColor(0x66, 0x66, 0x66)
        text_run.italic = True

    # AI disclosure label
    disclosure_para = doc.add_paragraph()
    disclosure_run = disclosure_para.add_run(get_disclosure_label(styled_variant.content_type))
    disclosure_run.font.size = Pt(8)
    disclosure_run.font.color.rgb = RGBColor(0x19, 0x76, 0xd2)
    disclosure_run.italic = True
```

### Pattern 4: Vocabulary Audit in Compliance Appendix

**What:** Add vocabulary audit summary to existing AI disclosure compliance section.
**When to use:** When styled content is present in export.
**Recommendation:** Summary stats in existing appendix chosen over detailed breakdown or new section per Claude's discretion.

**Rationale:**
- Detailed term-by-term breakdown adds pages without compliance value
- Existing compliance appendix already has AI disclosure section
- Summary statistics sufficient for audit trail (coverage %, word counts)
- Keeps document length reasonable

**Content to add to AI Disclosure section:**
```python
# Source: Extension of export_service.py build_compliance_sections()
def build_styled_content_disclosure(styled_statements: List[StyledStatement]) -> Dict:
    """Build styled content metadata for compliance appendix."""
    ai_styled_count = sum(1 for s in styled_statements if s.content_type == StyleContentType.AI_STYLED)
    original_fallback_count = sum(1 for s in styled_statements if s.content_type == StyleContentType.ORIGINAL_NOC)

    # Aggregate vocabulary coverage
    coverage_values = [s.vocabulary_coverage for s in styled_statements if s.content_type == StyleContentType.AI_STYLED]
    avg_coverage = sum(coverage_values) / len(coverage_values) if coverage_values else 0.0
    min_coverage = min(coverage_values) if coverage_values else 0.0

    # Aggregate confidence
    confidence_values = [s.confidence_score for s in styled_statements if s.content_type == StyleContentType.AI_STYLED]
    avg_confidence = sum(confidence_values) / len(confidence_values) if confidence_values else 0.0

    # Confidence distribution
    high_count = sum(1 for c in confidence_values if c >= 0.8)
    medium_count = sum(1 for c in confidence_values if 0.5 <= c < 0.8)
    low_count = sum(1 for c in confidence_values if c < 0.5)

    return {
        "description": "Job description statements were AI-styled from original NOC content "
                      "using curated job description samples as style templates.",
        "disclosure_label": "AI-Styled using Job Description Samples",
        "total_statements": len(styled_statements),
        "ai_styled_count": ai_styled_count,
        "original_fallback_count": original_fallback_count,
        "vocabulary_audit": {
            "average_coverage": f"{avg_coverage:.1f}%",
            "minimum_coverage": f"{min_coverage:.1f}%",
            "noc_vocabulary_source": "ESDC OaSIS Skills, Abilities, Knowledge, Work Activities tables"
        },
        "confidence_summary": {
            "average_confidence": f"{avg_confidence:.2f}",
            "high_confidence_count": high_count,
            "medium_confidence_count": medium_count,
            "low_confidence_count": low_count
        },
        "generation_metadata": {
            "model": "GPT-4o",
            "prompt_version": "v3.0",
            "max_retries": 3,
            "vocabulary_threshold": "95%",
            "semantic_similarity_threshold": "0.75"
        }
    }
```

### Pattern 5: Extending ExportData Model

**What:** Add styled content data to export models for template access.
**When to use:** All exports with styled content.

**Example:**
```python
# Source: Extension of export_models.py
from src.models.styled_content import StyledStatement
from src.models.vocabulary_audit import ConfidenceLevel, CONFIDENCE_THRESHOLDS

class StyledStatementExport(BaseModel):
    """Styled statement data for export templates."""
    styled_text: str
    original_noc_text: str
    content_type: StyleContentType
    confidence_score: float
    confidence_level: str  # "high", "medium", "low" for CSS class
    vocabulary_coverage: float
    disclosure_label: str

    model_config = ConfigDict(frozen=True)

    @classmethod
    def from_styled_statement(cls, stmt: StyledStatement) -> "StyledStatementExport":
        """Factory from StyledStatement model."""
        # Map confidence score to level
        if stmt.confidence_score >= CONFIDENCE_THRESHOLDS["high"]:
            level = "high"
        elif stmt.confidence_score >= CONFIDENCE_THRESHOLDS["medium"]:
            level = "medium"
        else:
            level = "low"

        # Map content type to disclosure label
        labels = {
            StyleContentType.AI_STYLED: "AI-Styled using Job Description Samples",
            StyleContentType.AI_GENERATED: "AI-Generated",
            StyleContentType.ORIGINAL_NOC: "Original NOC",
        }

        return cls(
            styled_text=stmt.styled_text,
            original_noc_text=stmt.original_noc_text,
            content_type=stmt.content_type,
            confidence_score=stmt.confidence_score,
            confidence_level=level,
            vocabulary_coverage=stmt.vocabulary_coverage,
            disclosure_label=labels.get(stmt.content_type, "Unknown")
        )

class StatementExport(BaseModel):
    """Individual statement for export with full metadata."""
    text: str
    source_attribute: str
    description: Optional[str] = None
    proficiency: Optional[ProficiencyData] = None
    publication_date: Optional[str] = None
    source_table_url: Optional[str] = None
    # NEW: Optional styled variant
    styled_variant: Optional[StyledStatementExport] = None

    model_config = ConfigDict(from_attributes=True)
```

### Anti-Patterns to Avoid

- **Footnote chaos for originals:** Footnotes require numbering management; stacked layout is cleaner for 1:1 pairing
- **Separate appendix for originals:** Separates content from context, making comparison difficult
- **Text labels for confidence:** "High Confidence" text adds clutter; dots are compact and universal
- **Detailed vocabulary term lists:** Adds pages without compliance value; summary stats sufficient
- **Different layouts for PDF vs DOCX:** Maintain visual consistency; users expect same content in both formats
- **Forgetting fallback styling:** ORIGINAL_NOC statements should render without confidence dot (already 100% NOC)

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Confidence level mapping | Custom threshold logic everywhere | Use CONFIDENCE_THRESHOLDS from vocabulary_audit.py | Already defined with 0.8/0.5/0.0 thresholds |
| AI disclosure labels | String literals in templates | Use AI_DISCLOSURE_LABELS dict from ai.py pattern | Centralized, type-safe with StyleContentType |
| Cell shading (DOCX) | Manual XML construction | Use OxmlElement pattern from research | Established pattern for python-docx |
| Colored circles (PDF) | Images or SVG | CSS border-radius: 50% | WeasyPrint supports CSS3 border-radius |
| Export model extension | New parallel models | Extend existing StatementExport | Avoids model proliferation |

**Key insight:** The existing export infrastructure (Phase 7) and styled content models (Phase 11) provide most of the building blocks. This phase wires them together with minimal new code.

## Common Pitfalls

### Pitfall 1: Inconsistent PDF/DOCX Rendering

**What goes wrong:** PDF shows styled content one way, DOCX shows it differently; users confused.
**Why it happens:** Implementing PDF template first, then retrofitting DOCX without matching structure.
**How to avoid:** Define shared data structure (StyledStatementExport); implement both formats in parallel, testing side-by-side.
**Warning signs:** QA finds layout differences; users report "PDF looks different from Word doc".

### Pitfall 2: Confidence Dots Wrong Color in DOCX

**What goes wrong:** DOCX confidence dots all show as black instead of green/yellow/red.
**Why it happens:** python-docx RGBColor not applied correctly; font.color.rgb requires explicit RGBColor object.
**How to avoid:** Use RGBColor(0x4c, 0xaf, 0x50) not string "#4caf50"; test color rendering in actual Word.
**Warning signs:** All dots appear same color; Word shows black bullets.

### Pitfall 3: Original Text Missing for ORIGINAL_NOC Fallbacks

**What goes wrong:** Statements that fell back to original show no content (styled_text equals original_noc_text).
**Why it happens:** Template logic checks for styled_variant but ORIGINAL_NOC has both texts equal.
**How to avoid:** Only show "Original NOC:" section when content_type is AI_STYLED, not ORIGINAL_NOC.
**Warning signs:** Fallback statements show redundant "Original NOC:" with identical text.

### Pitfall 4: Vocabulary Audit Table Too Wide for Page

**What goes wrong:** Compliance appendix table extends beyond page margins in PDF.
**Why it happens:** Vocabulary audit has long field names or too many columns.
**How to avoid:** Use summary stats table (5-6 rows, 2 columns max); avoid per-term breakdown.
**Warning signs:** PDF renders with horizontal scroll; content cut off in print.

### Pitfall 5: Styled Content Data Not Passed to Template

**What goes wrong:** Template shows no styled content even when it exists in session.
**Why it happens:** export_service.py build_export_data() not updated to include styled variants.
**How to avoid:** Extend build_export_data() to accept styled content and populate StatementExport.styled_variant.
**Warning signs:** All statements show original text only; no confidence dots visible.

### Pitfall 6: WeasyPrint Circles Not Rendering

**What goes wrong:** Confidence dots appear as squares or not at all in PDF.
**Why it happens:** Missing width/height or border-radius percentage issue.
**How to avoid:** Use absolute units (pt) for width/height; use 50% for border-radius; test with WeasyPrint locally.
**Warning signs:** PDF shows squares instead of circles; dots invisible.

## Code Examples

Verified patterns from official sources and existing codebase:

### Complete PDF Template Styled Statement Block

```html
<!-- Source: Extension of templates/export/jd_pdf.html -->
{% for statement in element.statements %}
<li class="jd-statement{% if statement.styled_variant %} jd-statement--styled{% endif %}">
  <div class="jd-statement__main">
    <!-- Primary text: styled or original -->
    <span class="jd-statement__text">
      {{ statement.styled_variant.styled_text if statement.styled_variant else statement.text }}
    </span>

    <!-- Confidence indicator (AI_STYLED only, not ORIGINAL_NOC) -->
    {% if statement.styled_variant and statement.styled_variant.content_type.value == 'ai_styled' %}
    <span class="jd-confidence-dot jd-confidence-dot--{{ statement.styled_variant.confidence_level }}"></span>
    {% endif %}

    <!-- Proficiency level (existing) -->
    {% if statement.proficiency and statement.proficiency.level %}
    <span class="jd-statement__level">
      {% for i in range(statement.proficiency.level) %}●{% endfor %}{% for i in range(statement.proficiency.max - statement.proficiency.level) %}○{% endfor %}
      L{{ statement.proficiency.level }}
    </span>
    {% endif %}
  </div>

  <!-- Original NOC text (AI_STYLED only) -->
  {% if statement.styled_variant and statement.styled_variant.content_type.value == 'ai_styled' %}
  <div class="jd-statement__original">
    <span class="jd-statement__original-label">Original NOC:</span>
    {{ statement.styled_variant.original_noc_text }}
  </div>
  {% endif %}

  <!-- AI disclosure label -->
  {% if statement.styled_variant %}
  <span class="jd-statement__ai-label">{{ statement.styled_variant.disclosure_label }}</span>
  {% endif %}

  <!-- Element description (existing) -->
  {% if statement.description %}
  <p class="jd-statement__description">{{ statement.description }}</p>
  {% endif %}

  <!-- Source attribution (existing) -->
  <span class="jd-statement__source">Source: {{ statement.source_attribute }}</span>
</li>
{% endfor %}
```

### Complete DOCX Styled Statement Rendering

```python
# Source: Extension of src/services/docx_generator.py
from docx.shared import Inches, Pt, RGBColor
from src.models.ai import StyleContentType
from src.models.vocabulary_audit import CONFIDENCE_THRESHOLDS

# Confidence indicator colors
CONFIDENCE_COLORS = {
    "high": RGBColor(0x4c, 0xaf, 0x50),
    "medium": RGBColor(0xff, 0x98, 0x00),
    "low": RGBColor(0xf4, 0x43, 0x36),
}

def get_confidence_level(score: float) -> str:
    """Map confidence score to level string."""
    if score >= CONFIDENCE_THRESHOLDS["high"]:
        return "high"
    elif score >= CONFIDENCE_THRESHOLDS["medium"]:
        return "medium"
    return "low"

def _add_jd_elements(doc, data):
    """Add JD element sections with styled content support."""
    for element in data.jd_elements:
        doc.add_heading(element.name, 1)

        for statement in element.statements:
            if statement.styled_variant:
                _add_styled_statement(doc, statement)
            else:
                # Original rendering (existing)
                doc.add_paragraph(statement.text, style='List Bullet')

def _add_styled_statement(doc, statement):
    """Add statement with styled content and original below."""
    styled = statement.styled_variant

    # Primary: Styled text with confidence indicator
    para = doc.add_paragraph()
    para.style = 'List Bullet'
    text_run = para.add_run(styled.styled_text)

    # Confidence dot (only for AI_STYLED)
    if styled.content_type == StyleContentType.AI_STYLED:
        dot_run = para.add_run(" ●")
        dot_run.font.color.rgb = CONFIDENCE_COLORS.get(
            get_confidence_level(styled.confidence_score),
            CONFIDENCE_COLORS["low"]
        )
        dot_run.font.size = Pt(8)

    # Original NOC text (only for AI_STYLED)
    if styled.content_type == StyleContentType.AI_STYLED:
        orig_para = doc.add_paragraph()
        orig_para.paragraph_format.left_indent = Inches(0.5)

        label_run = orig_para.add_run("Original NOC: ")
        label_run.font.size = Pt(9)
        label_run.font.color.rgb = RGBColor(0x88, 0x88, 0x88)
        label_run.bold = True

        text_run = orig_para.add_run(styled.original_noc_text)
        text_run.font.size = Pt(9)
        text_run.font.color.rgb = RGBColor(0x66, 0x66, 0x66)
        text_run.italic = True

    # AI disclosure label
    label_para = doc.add_paragraph()
    label_para.paragraph_format.left_indent = Inches(0.25)
    label_run = label_para.add_run(styled.disclosure_label)
    label_run.font.size = Pt(8)
    label_run.font.color.rgb = RGBColor(0x19, 0x76, 0xd2)
    label_run.italic = True
```

### Vocabulary Audit Compliance Table

```html
<!-- Source: Addition to compliance appendix in jd_pdf.html -->
{% if styled_content_disclosure %}
<div class="compliance-section">
  <h2>AI-Styled Content Disclosure</h2>
  <p>{{ styled_content_disclosure.description }}</p>

  <table class="compliance-table">
    <tr><th>Content Disclosure</th><td>{{ styled_content_disclosure.disclosure_label }}</td></tr>
    <tr><th>Total Statements</th><td>{{ styled_content_disclosure.total_statements }}</td></tr>
    <tr><th>AI-Styled Count</th><td>{{ styled_content_disclosure.ai_styled_count }}</td></tr>
    <tr><th>Original Fallback Count</th><td>{{ styled_content_disclosure.original_fallback_count }}</td></tr>
  </table>

  <h3>Vocabulary Audit Summary</h3>
  <table class="compliance-table">
    <tr><th>Average NOC Coverage</th><td>{{ styled_content_disclosure.vocabulary_audit.average_coverage }}</td></tr>
    <tr><th>Minimum Coverage</th><td>{{ styled_content_disclosure.vocabulary_audit.minimum_coverage }}</td></tr>
    <tr><th>Vocabulary Source</th><td>{{ styled_content_disclosure.vocabulary_audit.noc_vocabulary_source }}</td></tr>
  </table>

  <h3>Confidence Distribution</h3>
  <table class="compliance-table">
    <tr><th>Average Confidence</th><td>{{ styled_content_disclosure.confidence_summary.average_confidence }}</td></tr>
    <tr><th>High Confidence (≥0.8)</th><td>{{ styled_content_disclosure.confidence_summary.high_confidence_count }}</td></tr>
    <tr><th>Medium Confidence (0.5-0.8)</th><td>{{ styled_content_disclosure.confidence_summary.medium_confidence_count }}</td></tr>
    <tr><th>Low Confidence (<0.5)</th><td>{{ styled_content_disclosure.confidence_summary.low_confidence_count }}</td></tr>
  </table>

  <h3>Generation Parameters</h3>
  <table class="compliance-table">
    <tr><th>Model</th><td>{{ styled_content_disclosure.generation_metadata.model }}</td></tr>
    <tr><th>Prompt Version</th><td>{{ styled_content_disclosure.generation_metadata.prompt_version }}</td></tr>
    <tr><th>Max Retries</th><td>{{ styled_content_disclosure.generation_metadata.max_retries }}</td></tr>
    <tr><th>Vocabulary Threshold</th><td>{{ styled_content_disclosure.generation_metadata.vocabulary_threshold }}</td></tr>
  </table>
</div>
{% endif %}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Interactive collapsible UI | Stacked layout for static docs | Standard for print | Clear comparison without interaction |
| Separate "track changes" document | Inline original with styled | Modern compliance patterns | Single document with full context |
| Text confidence labels | Color-coded dots | Visual design standards | Compact, universal traffic-light metaphor |
| Separate AI disclosure page | Integrated compliance appendix | Phase 7 pattern | Single audit trail section |

**Deprecated/outdated:**
- Footnotes for original text: Interrupts reading flow; numbering management overhead
- PDF-only interactive elements: WeasyPrint renders static; no JavaScript support
- Separate vocabulary report: Adds document bloat; summary sufficient for compliance

## Open Questions

Things that couldn't be fully resolved:

1. **Confidence Dot Size in Print**
   - What we know: 8pt circles work in screen preview
   - What's unclear: Whether 8pt is visible enough in print (300dpi)
   - Recommendation: Test with actual print; may need 10pt for visibility

2. **DOCX Unicode Bullet Rendering**
   - What we know: Unicode ● (U+25CF) works in Word
   - What's unclear: Whether color applies correctly in all Word versions
   - Recommendation: Test in Word 2019, 2021, and 365; fall back to text labels if issues

3. **Very Long Original Statements**
   - What we know: Stacked layout works for typical NOC statements (~100 chars)
   - What's unclear: How to handle originals >200 characters without excessive vertical space
   - Recommendation: Truncate in main body with "[...]"; full text in compliance appendix

4. **Mixed Styled/Original Documents**
   - What we know: Some statements may have styled variants, others not
   - What's unclear: Whether visual consistency is maintained when mixing
   - Recommendation: Non-styled statements render without confidence dot or original block; document should explain in appendix

## Sources

### Primary (HIGH confidence)
- Existing codebase: `src/services/pdf_generator.py`, `src/services/docx_generator.py`, `src/models/export_models.py`
- Existing CSS: `static/css/export_print.css`
- Phase 7 research: `.planning/phases/07-export-extensions/07-RESEARCH.md`
- Phase 11 research: `.planning/phases/11-provenance-architecture/11-RESEARCH.md`
- Phase 11 models: `src/models/styled_content.py`, `src/models/vocabulary_audit.py`, `src/models/ai.py`
- [python-docx Table Cell Shading](https://github.com/python-openxml/python-docx/issues/434) - OxmlElement pattern for cell colors
- [WeasyPrint 68.0 Documentation](https://doc.courtbouillon.org/weasyprint/stable/) - CSS support including border-radius

### Secondary (MEDIUM confidence)
- [Canada.ca Expand/Collapse Pattern](https://design.canada.ca/common-design-patterns/collapsible-content.html) - Government UI patterns (web-focused, not print)
- [CSS border-radius for circles](https://www.cvwdesign.com/blog/making-circles-with-css3-border-radius) - 50% radius technique
- [python-docx RGBColor](https://python-docx.readthedocs.io/en/latest/) - Color application to runs

### Tertiary (LOW confidence)
- WebSearch results on static representation of collapsible content - Limited guidance; mostly web-focused
- General document design patterns - Subjective; stacked layout is common but not universal standard

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Using existing WeasyPrint, python-docx from project
- Architecture patterns: HIGH - Extending proven Phase 7 patterns
- Stacked layout recommendation: MEDIUM - Best practice for static docs, but alternatives valid
- Confidence dots: HIGH - CSS circles verified in WeasyPrint; Unicode bullets standard in Word
- Vocabulary audit placement: MEDIUM - Summary in appendix is pragmatic; detailed breakdown alternative
- PDF/DOCX consistency: HIGH - Same data structure rendered both formats

**Research date:** 2026-02-03
**Valid until:** 30 days (stable export domain; libraries unchanged since Phase 7)
