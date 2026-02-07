"""Word document generation service using python-docx."""

from io import BytesIO
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.shared import OxmlElement
from docx.oxml.ns import qn
from src.models.export_models import ExportData
from src.models.ai import StyleContentType
from src.models.vocabulary_audit import CONFIDENCE_THRESHOLDS


# Government of Canada primary color
GC_PRIMARY = RGBColor(0x26, 0x37, 0x4a)

# Confidence indicator colors (matching PDF CSS)
CONFIDENCE_COLORS = {
    "high": RGBColor(0x4c, 0xaf, 0x50),    # Green #4caf50
    "medium": RGBColor(0xff, 0x98, 0x00),  # Amber #ff9800
    "low": RGBColor(0xf4, 0x43, 0x36),     # Red #f44336
}

# AI disclosure blue (matching PDF CSS)
AI_DISCLOSURE_BLUE = RGBColor(0x19, 0x76, 0xd2)


def _get_confidence_level(score: float) -> str:
    """Map confidence score to level string for color lookup."""
    if score >= CONFIDENCE_THRESHOLDS["high"]:
        return "high"
    elif score >= CONFIDENCE_THRESHOLDS["medium"]:
        return "medium"
    return "low"


def _add_hyperlink(paragraph, url, text, color='1565C0', underline=True):
    """Add a hyperlink to a paragraph.

    Args:
        paragraph: docx paragraph object
        url: The URL to link to
        text: Display text for the link
        color: Hex color code (without #)
        underline: Whether to underline the link

    Returns:
        The hyperlink run
    """
    # Create relationship (rId)
    part = paragraph.part
    r_id = part.relate_to(url, 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink', is_external=True)

    # Create hyperlink element
    hyperlink = OxmlElement('w:hyperlink')
    hyperlink.set(qn('r:id'), r_id)

    # Create run within hyperlink
    run_element = OxmlElement('w:r')

    # Run properties
    rPr = OxmlElement('w:rPr')

    # Color
    if color:
        c = OxmlElement('w:color')
        c.set(qn('w:val'), color)
        rPr.append(c)

    # Underline
    if underline:
        u = OxmlElement('w:u')
        u.set(qn('w:val'), 'single')
        rPr.append(u)

    run_element.append(rPr)

    # Text element
    text_element = OxmlElement('w:t')
    text_element.text = text
    run_element.append(text_element)

    hyperlink.append(run_element)
    paragraph._p.append(hyperlink)

    return hyperlink


def _add_classification_section(doc, data):
    """Add classification section to document.

    Args:
        doc: Document object
        data: ExportData with classification_result
    """
    if not data.include_classification or not data.classification_result:
        return

    # Page break before classification
    doc.add_page_break()

    # Main heading
    heading = doc.add_heading('Classification Step 1: Occupational Group Allocation', 1)
    for run in heading.runs:
        run.font.color.rgb = GC_PRIMARY

    # Status table
    _add_key_value_table(doc, [
        ('Status', data.classification_result.get('status', '')),
        ('Match Context', data.classification_result.get('match_context', ''))
    ])

    # Recommendations heading
    rec_heading = doc.add_heading('Recommendations (Ranked by Confidence)', 2)
    for run in rec_heading.runs:
        run.font.color.rgb = GC_PRIMARY

    # Each recommendation
    for rec in data.classification_result.get('recommendations', []):
        # Recommendation heading
        rec_title = f"{rec['group_code']}: {rec['group_name']} ({rec['confidence']}% confidence)"
        rec_h = doc.add_heading(rec_title, 3)
        for run in rec_h.runs:
            run.font.size = Pt(12)

        # Rationale
        doc.add_heading('Rationale', 4)
        doc.add_paragraph(rec.get('rationale', ''))

        # Evidence
        if rec.get('evidence'):
            doc.add_heading('Supporting Evidence', 4)
            for ev in rec['evidence']:
                para = doc.add_paragraph()
                para.paragraph_format.left_indent = Inches(0.5)
                para.style = 'Quote'
                quote_run = para.add_run(f'"{ev["quote"]}"')
                quote_run.italic = True
                para.add_run(f'\n-- {ev["source_field"]}')

        # Authoritative Source
        doc.add_heading('Authoritative Source', 4)
        provenance = rec.get('provenance', {})

        # Source type
        para = doc.add_paragraph()
        para.add_run('Source: ').bold = True
        para.add_run(provenance.get('source_type', ''))

        # Document (with hyperlink)
        para = doc.add_paragraph()
        para.add_run('Document: ').bold = True
        if provenance.get('url'):
            _add_hyperlink(
                para,
                provenance['url'],
                f"TBS Occupational Group {rec['group_code']} Definition"
            )
        else:
            para.add_run(f"TBS Occupational Group {rec['group_code']} Definition")

        # Inclusions
        if provenance.get('inclusions_referenced'):
            para = doc.add_paragraph()
            para.add_run('Inclusions Referenced: ').bold = True
            para.add_run(', '.join(provenance['inclusions_referenced']))

        # Exclusions
        if provenance.get('exclusions_checked'):
            para = doc.add_paragraph()
            para.add_run('Exclusions Checked: ').bold = True
            para.add_run(', '.join(provenance['exclusions_checked']))

        # Data retrieved
        if provenance.get('scraped_at'):
            para = doc.add_paragraph()
            run = para.add_run(f"Data retrieved: {provenance['scraped_at']}")
            run.font.size = Pt(9)
            run.italic = True

    # Classification Audit Footer
    doc.add_heading('Classification Audit Trail', 3)
    analyzed_at = data.classification_result.get('analyzed_at')
    if analyzed_at and hasattr(analyzed_at, 'strftime'):
        analyzed_str = analyzed_at.strftime('%Y-%m-%d %H:%M UTC')
    else:
        analyzed_str = 'N/A'

    _add_key_value_table(doc, [
        ('Tool', 'JobForge Classification Engine'),
        ('Version', '4.1'),
        ('Generated', analyzed_str),
        ('Data Sources', 'TBS Occupational Group Definitions (2026-01)'),
        ('Compliance', 'TBS Directive 32592 (Automated Decision Making)'),
        ('Constraints', data.classification_result.get('constraints_compliance', ''))
    ])


def generate_docx(data: ExportData) -> bytes:
    """
    Generate Word document from export data.

    Args:
        data: Complete export data structure

    Returns:
        DOCX bytes ready for response
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

    # Add header
    header = section.header
    header_para = header.paragraphs[0]
    header_para.text = f"{data.job_title} ({data.noc_code})"
    header_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    header_run = header_para.runs[0] if header_para.runs else header_para.add_run()
    header_run.font.size = Pt(10)
    header_run.font.color.rgb = GC_PRIMARY

    # Add footer
    footer = section.footer
    footer_para = footer.paragraphs[0]
    footer_para.text = "Compliant with TBS Directive 32592"
    footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer_run = footer_para.runs[0] if footer_para.runs else footer_para.add_run()
    footer_run.font.size = Pt(8)
    footer_run.font.color.rgb = RGBColor(0x66, 0x66, 0x66)

    # Title
    title = doc.add_heading(data.job_title, 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # NOC Code subtitle
    subtitle = doc.add_paragraph(f"NOC Code: {data.noc_code}")
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # General Overview (if present)
    if data.general_overview:
        doc.add_heading("General Overview", 1)
        overview_para = doc.add_paragraph(data.general_overview)

        # Add AI indicator if applicable
        if data.ai_metadata:
            indicator = " [AI-Generated"
            if data.ai_metadata.modified:
                indicator += ", Modified"
            indicator += "]"
            run = overview_para.add_run(indicator)
            run.font.size = Pt(8)
            run.font.color.rgb = RGBColor(0x15, 0x65, 0xc0)

    # JD Elements
    for element in data.jd_elements:
        doc.add_heading(element.name, 1)
        for statement in element.statements:
            if statement.styled_variant:
                _add_styled_statement(doc, statement)
            else:
                # Original rendering (existing behavior)
                doc.add_paragraph(statement.text, style='List Bullet')

    # Add classification section if present
    _add_classification_section(doc, data)

    # Page break before compliance appendix
    doc.add_page_break()

    # Compliance Appendix
    doc.add_heading("Appendix A: Compliance Metadata", 0)

    for section in data.compliance_sections:
        doc.add_heading(section.title, 1)

        if section.section_id == "6.2.3":
            # Data Sources - simple key-value table
            _add_key_value_table(doc, [
                ("Data Steward", section.content.get("data_steward", "")),
                ("Authoritative Source", section.content.get("authoritative_source", "")),
                ("Access Method", section.content.get("access_method", "")),
                ("Source URL", section.content.get("source_url", "")),
                ("Retrieval Timestamp", section.content.get("retrieval_timestamp", "")),
                ("NOC Version", section.content.get("noc_version", ""))
            ])

        elif section.section_id == "6.2.7":
            # Manager Decisions - description and selections table
            doc.add_paragraph(section.content.get("description", ""))
            doc.add_paragraph(f"Total selections: {section.content.get('total_selections', 0)}")

            # Selections table
            selections = section.content.get("selections", [])
            if selections:
                table = doc.add_table(rows=1, cols=4)
                table.style = 'Table Grid'

                # Header row
                hdr_cells = table.rows[0].cells
                hdr_cells[0].text = "JD Element"
                hdr_cells[1].text = "Statement"
                hdr_cells[2].text = "Source"
                hdr_cells[3].text = "Selected At"

                # Make header bold
                for cell in hdr_cells:
                    for para in cell.paragraphs:
                        for run in para.runs:
                            run.bold = True

                # Data rows
                for sel in selections:
                    row_cells = table.add_row().cells
                    row_cells[0].text = sel.get("jd_element", "")
                    row_cells[1].text = sel.get("statement", "")[:100] + ("..." if len(sel.get("statement", "")) > 100 else "")
                    row_cells[2].text = sel.get("source_attribute", "")
                    row_cells[3].text = sel.get("selected_at", "")[:19]  # Truncate to datetime

        elif section.section_id == "6.3.5":
            # Data Quality - requirement/how-met table
            content = section.content
            _add_key_value_table(doc, [
                ("Relevant", f"{content.get('relevant', {}).get('how_met', '')}"),
                ("Accurate", f"{content.get('accurate', {}).get('how_met', '')}"),
                ("Up-to-date", f"{content.get('up_to_date', {}).get('how_met', '')}")
            ])

        elif section.section_id == "ai_disclosure":
            # AI Disclosure
            doc.add_paragraph(section.content.get("description", ""))
            _add_key_value_table(doc, [
                ("Content Type", section.content.get("content_type", "")),
                ("Model", section.content.get("model", "")),
                ("Generation Timestamp", section.content.get("generation_timestamp", "")),
                ("Input Statement Count", str(section.content.get("input_count", 0))),
                ("Modified by User", "Yes" if section.content.get("modified_by_user") else "No"),
                ("Purpose", section.content.get("purpose", ""))
            ])

        elif section.section_id == "styled_content_disclosure":
            # Styled Content Disclosure
            doc.add_paragraph(section.content.get("description", ""))

            # Summary table
            _add_key_value_table(doc, [
                ("Content Disclosure", section.content.get("disclosure_label", "")),
                ("Total Styled Statements", str(section.content.get("total_statements", 0))),
                ("AI-Styled Count", str(section.content.get("ai_styled_count", 0))),
                ("Original Fallback Count", str(section.content.get("original_fallback_count", 0)))
            ])

            # Vocabulary Audit subsection
            vocab_heading = doc.add_heading("Vocabulary Audit Summary", 2)
            for run in vocab_heading.runs:
                run.font.size = Pt(11)
            vocab_audit = section.content.get("vocabulary_audit", {})
            _add_key_value_table(doc, [
                ("Average NOC Coverage", vocab_audit.get("average_coverage", "")),
                ("Minimum Coverage", vocab_audit.get("minimum_coverage", "")),
                ("Vocabulary Source", vocab_audit.get("noc_vocabulary_source", ""))
            ])

            # Confidence Distribution subsection
            conf_heading = doc.add_heading("Confidence Distribution", 2)
            for run in conf_heading.runs:
                run.font.size = Pt(11)
            conf_summary = section.content.get("confidence_summary", {})
            _add_key_value_table(doc, [
                ("Average Confidence", str(conf_summary.get("average_confidence", ""))),
                ("High Confidence (>=0.8)", str(conf_summary.get("high_confidence_count", 0))),
                ("Medium Confidence (0.5-0.8)", str(conf_summary.get("medium_confidence_count", 0))),
                ("Low Confidence (<0.5)", str(conf_summary.get("low_confidence_count", 0)))
            ])

            # Generation Parameters subsection
            gen_heading = doc.add_heading("Generation Parameters", 2)
            for run in gen_heading.runs:
                run.font.size = Pt(11)
            gen_meta = section.content.get("generation_metadata", {})
            _add_key_value_table(doc, [
                ("Model", gen_meta.get("model", "")),
                ("Prompt Version", gen_meta.get("prompt_version", "")),
                ("Max Retries", str(gen_meta.get("max_retries", ""))),
                ("Vocabulary Threshold", gen_meta.get("vocabulary_threshold", "")),
                ("Semantic Similarity Threshold", gen_meta.get("semantic_similarity_threshold", ""))
            ])

    # Add Annex section if data available
    _add_annex_section(doc, data)

    # Write to bytes using context manager for memory safety
    with BytesIO() as buffer:
        doc.save(buffer)
        buffer.seek(0)
        return buffer.read()


def _add_key_value_table(doc, items):
    """Helper to add a simple 2-column key-value table."""
    table = doc.add_table(rows=len(items), cols=2)
    table.style = 'Table Grid'

    for i, (key, value) in enumerate(items):
        cells = table.rows[i].cells
        cells[0].text = key
        cells[1].text = str(value)

        # Make key column bold
        for para in cells[0].paragraphs:
            for run in para.runs:
                run.bold = True


# Text color constant for light gray
TEXT_LIGHT = RGBColor(0x66, 0x66, 0x66)


def _add_styled_statement(doc, statement):
    """Add statement with styled content and original below.

    Args:
        doc: Document object
        statement: StatementExport with styled_variant
    """
    styled = statement.styled_variant

    # Primary: Styled text as bullet point
    para = doc.add_paragraph()
    para.style = 'List Bullet'
    text_run = para.add_run(styled.styled_text)

    # Confidence dot (only for AI_STYLED, not ORIGINAL_NOC fallback)
    if styled.content_type == StyleContentType.AI_STYLED:
        dot_run = para.add_run(" \u25cf")  # Unicode filled circle
        dot_run.font.color.rgb = CONFIDENCE_COLORS.get(
            _get_confidence_level(styled.confidence_score),
            CONFIDENCE_COLORS["low"]
        )
        dot_run.font.size = Pt(8)

    # Original NOC text (only for AI_STYLED, not ORIGINAL_NOC fallback)
    if styled.content_type == StyleContentType.AI_STYLED:
        orig_para = doc.add_paragraph()
        orig_para.paragraph_format.left_indent = Inches(0.5)

        label_run = orig_para.add_run("Original NOC: ")
        label_run.font.size = Pt(9)
        label_run.font.color.rgb = RGBColor(0x88, 0x88, 0x88)
        label_run.bold = True

        text_run = orig_para.add_run(styled.original_noc_text)
        text_run.font.size = Pt(9)
        text_run.font.color.rgb = TEXT_LIGHT
        text_run.italic = True

    # AI disclosure label (for any styled variant)
    label_para = doc.add_paragraph()
    label_para.paragraph_format.left_indent = Inches(0.25)
    label_run = label_para.add_run(styled.disclosure_label)
    label_run.font.size = Pt(8)
    label_run.font.color.rgb = AI_DISCLOSURE_BLUE
    label_run.italic = True


def _add_annex_section(doc, data):
    """Add Annex section with unused NOC attributes.

    Renders the Annex after compliance appendix with all 4 categories:
    - Job Requirements (paragraph format)
    - Career Mobility (grouped list)
    - Interests (Holland Codes) (bullet list)
    - Personal Suitability (Placement Criteria) (bullet list)
    """
    if not data.annex_data or not data.annex_data.sections:
        return  # No annex data to render

    # Page break before Annex
    doc.add_page_break()

    # Main heading (Heading 1 for navigation pane)
    main_heading = doc.add_heading('Additional Job Information', 1)
    for run in main_heading.runs:
        run.font.color.rgb = GC_PRIMARY

    # Intro paragraph
    intro = doc.add_paragraph(
        'Reference information from the National Occupational Classification '
        'that may be useful for recruitment, career development, and job analysis.'
    )
    if intro.runs:
        intro.runs[0].italic = True

    # Render each category section
    for section in data.annex_data.sections:
        # Category heading (Heading 2 for hierarchy)
        category_heading = doc.add_heading(section.title, 2)
        for run in category_heading.runs:
            run.font.color.rgb = GC_PRIMARY
            run.font.size = Pt(12)
        category_heading.paragraph_format.space_after = Pt(9)

        # Handle empty sections
        if not section.items:
            empty_para = doc.add_paragraph('No additional information available.')
            if empty_para.runs:
                empty_para.runs[0].italic = True
                empty_para.runs[0].font.color.rgb = TEXT_LIGHT
            continue

        # Render based on format type
        if section.format_type == 'paragraph':
            # Job Requirements: paragraphs
            for item in section.items:
                doc.add_paragraph(item)

        elif section.format_type == 'grouped_list':
            # Career Mobility: grouped list with Entry/Advancement headers
            for item in section.items:
                if item.endswith(':'):
                    # Group header (Entry Paths:, Advancement Paths:)
                    para = doc.add_paragraph()
                    run = para.add_run(item)
                    run.bold = True
                else:
                    # Mobility item (indented with dash)
                    para = doc.add_paragraph(item)
                    para.paragraph_format.left_indent = Inches(0.25)

        else:  # 'list'
            # Interests, Personal Suitability: bullet list
            for item in section.items:
                para = doc.add_paragraph(item, style='List Bullet')
                para.paragraph_format.space_after = Pt(6)

    # Source attribution at end of Annex
    attr_para = doc.add_paragraph()
    attr_para.paragraph_format.space_before = Pt(24)
    attr_run = attr_para.add_run(
        f"Source: NOC {data.annex_data.source_noc_code}, "
        f"retrieved {data.annex_data.retrieved_at.strftime('%Y-%m-%d')}"
    )
    attr_run.font.size = Pt(9)
    attr_run.font.color.rgb = TEXT_LIGHT
    attr_run.italic = True
