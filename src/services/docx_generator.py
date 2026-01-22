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

    # Write to bytes
    buffer = BytesIO()
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
