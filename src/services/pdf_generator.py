"""PDF generation service using WeasyPrint."""

from flask import render_template, current_app
from flask_weasyprint import HTML, render_pdf
from src.models.export_models import ExportData


def generate_pdf(data: ExportData, base_url: str) -> bytes:
    """
    Generate PDF from export data using WeasyPrint.

    Args:
        data: Complete export data structure
        base_url: Flask request.url_root for resolving static assets

    Returns:
        PDF bytes ready for response
    """
    # Render HTML template
    html_content = render_template(
        'export/jd_pdf.html',
        data=data,
        # Flatten some data for easier template access
        noc_code=data.noc_code,
        job_title=data.job_title,
        general_overview=data.general_overview,
        jd_elements=data.jd_elements,
        compliance_sections=data.compliance_sections,
        ai_metadata=data.ai_metadata,
        source_metadata=data.source_metadata,
        generated_at=data.generated_at
    )

    # Generate PDF with WeasyPrint
    # base_url ensures CSS and images resolve correctly
    html = HTML(string=html_content, base_url=base_url)

    return html.write_pdf()


def render_preview(data: ExportData) -> str:
    """
    Render preview HTML (same template, screen styles).

    Args:
        data: Complete export data structure

    Returns:
        HTML string for browser display
    """
    return render_template(
        'export/jd_preview.html',
        data=data,
        noc_code=data.noc_code,
        job_title=data.job_title,
        general_overview=data.general_overview,
        jd_elements=data.jd_elements,
        compliance_sections=data.compliance_sections,
        ai_metadata=data.ai_metadata,
        source_metadata=data.source_metadata,
        generated_at=data.generated_at
    )
