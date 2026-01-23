"""Word document generation service using python-docx."""

from io import BytesIO
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from src.models.export_models import ExportData


# Government of Canada primary color
GC_PRIMARY = RGBColor(0x26, 0x37, 0x4a)


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
            doc.add_paragraph(statement, style='List Bullet')

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
