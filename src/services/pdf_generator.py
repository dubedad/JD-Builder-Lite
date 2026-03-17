"""PDF generation service using reportlab (Python 3.14 compatible)."""

from io import BytesIO
from flask import render_template

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Table, TableStyle,
    Spacer, PageBreak, HRFlowable, ListFlowable, ListItem
)
from reportlab.lib.units import inch

from src.models.export_models import ExportData


# ---------------------------------------------------------------------------
# Source tag constants
# ---------------------------------------------------------------------------
SOURCE_TAG_MAP = {
    "Main Duties": "[NOC]",
    "Work Activities": "[OaSIS]",
    "Abilities": "[OaSIS]",
    "Knowledge": "[OaSIS]",
    "Skills": "[OaSIS]",
    "Effort": "[OaSIS]",
    "Responsibility": "[OaSIS]",
    "Core Competencies": "[GC]",
}

SOURCE_TAG_COLORS = {
    "Main Duties": "#6f42c1",
    "Skills": "#17a2b8",
    "Abilities": "#17a2b8",
    "Knowledge": "#17a2b8",
    "Work Activities": "#fd7e14",
    "Core Competencies": "#28a745",
    "Effort": "#17a2b8",
    "Responsibility": "#17a2b8",
}


def get_source_tag(source_attribute: str, data_source: str = None) -> str:
    """Return the bracketed source tag for a statement."""
    if data_source == "jobforge":
        return "[JobForge]"
    return SOURCE_TAG_MAP.get(source_attribute, "[NOC]")


def get_source_color(source_attribute: str, data_source: str = None) -> str:
    """Return the hex color string for a source tag."""
    if data_source == "jobforge":
        return "#007bff"
    return SOURCE_TAG_COLORS.get(source_attribute, "#6f42c1")


# ---------------------------------------------------------------------------
# Style factory
# ---------------------------------------------------------------------------
def _build_styles():
    """Return a dict of named ParagraphStyle objects for the PDF."""
    base = getSampleStyleSheet()

    styles = {}

    styles["doc_title"] = ParagraphStyle(
        "doc_title",
        parent=base["Title"],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1a1a2e"),
        spaceAfter=4,
        alignment=TA_CENTER,
    )
    styles["doc_subtitle"] = ParagraphStyle(
        "doc_subtitle",
        parent=base["Normal"],
        fontSize=11,
        textColor=colors.HexColor("#555555"),
        spaceAfter=2,
        alignment=TA_CENTER,
    )
    styles["section_heading"] = ParagraphStyle(
        "section_heading",
        parent=base["Heading1"],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#26374a"),
        spaceBefore=14,
        spaceAfter=6,
        fontName="Helvetica-Bold",
    )
    styles["sub_heading"] = ParagraphStyle(
        "sub_heading",
        parent=base["Heading2"],
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#26374a"),
        spaceBefore=10,
        spaceAfter=4,
        fontName="Helvetica-Bold",
    )
    styles["appendix_heading"] = ParagraphStyle(
        "appendix_heading",
        parent=base["Heading1"],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#26374a"),
        spaceBefore=18,
        spaceAfter=8,
        fontName="Helvetica-Bold",
    )
    styles["body"] = ParagraphStyle(
        "body",
        parent=base["Normal"],
        fontSize=10,
        leading=14,
        spaceAfter=4,
    )
    styles["bullet"] = ParagraphStyle(
        "bullet",
        parent=base["Normal"],
        fontSize=10,
        leading=14,
        leftIndent=16,
        bulletIndent=4,
        spaceAfter=3,
    )
    styles["ai_note"] = ParagraphStyle(
        "ai_note",
        parent=base["Italic"],
        fontSize=8,
        textColor=colors.HexColor("#1976d2"),
        spaceAfter=4,
    )
    styles["caption"] = ParagraphStyle(
        "caption",
        parent=base["Normal"],
        fontSize=8,
        textColor=colors.HexColor("#666666"),
        spaceAfter=2,
    )

    return styles


# ---------------------------------------------------------------------------
# Table helpers
# ---------------------------------------------------------------------------
_TABLE_HEADER_STYLE = [
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#26374a")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, 0), 9),
    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f8f9fa"), colors.white]),
    ("FONTSIZE", (0, 1), (-1, -1), 9),
    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cccccc")),
    ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ("TOPPADDING", (0, 0), (-1, -1), 4),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
]

_KV_TABLE_STYLE = [
    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 9),
    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.HexColor("#f8f9fa"), colors.white]),
    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cccccc")),
    ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ("TOPPADDING", (0, 0), (-1, -1), 4),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
]


def _kv_table(rows: list, col_widths=None, styles_override=None) -> Table:
    """Build a two-column key-value table."""
    table = Table(rows, colWidths=col_widths or [2.0 * inch, 4.5 * inch])
    table.setStyle(TableStyle(styles_override or _KV_TABLE_STYLE))
    return table


def _data_table(headers: list, rows: list, col_widths=None) -> Table:
    """Build a multi-column data table with header row."""
    all_rows = [headers] + rows
    table = Table(all_rows, colWidths=col_widths)
    table.setStyle(TableStyle(_TABLE_HEADER_STYLE))
    return table


# ---------------------------------------------------------------------------
# Main generate_pdf
# ---------------------------------------------------------------------------
def generate_pdf(
    data: ExportData,
    include_provenance: bool = True,
    include_audit: bool = True,
) -> bytes:
    """
    Generate PDF from export data using reportlab Platypus.

    Args:
        data: Complete export data structure
        include_provenance: Whether to render Appendix A/B/C
        include_audit: Whether to include the audit/data-quality appendix

    Returns:
        PDF bytes ready for response
    """
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=letter,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    s = _build_styles()
    story = []

    # Build element lookup
    elements_by_key = {el.key: el for el in data.jd_elements}

    # ------------------------------------------------------------------
    # HEADER — title, NOC code, date
    # ------------------------------------------------------------------
    story.append(Paragraph(data.job_title, s["doc_title"]))
    story.append(Paragraph(f"NOC Code: {data.noc_code}", s["doc_subtitle"]))
    story.append(
        Paragraph(
            f"Generated: {data.generated_at.strftime('%Y-%m-%d')}",
            s["doc_subtitle"],
        )
    )
    if data.include_classification and data.classification_result:
        recs = data.classification_result.get("recommendations", [])
        if recs:
            top = recs[0]
            story.append(
                Paragraph(
                    f"Occupational Group: {top['group_code']} — "
                    f"{top['group_name']} ({top['confidence']}% confidence)",
                    s["doc_subtitle"],
                )
            )
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#26374a")))
    story.append(Spacer(1, 8))

    # ------------------------------------------------------------------
    # 1. POSITION OVERVIEW
    # ------------------------------------------------------------------
    if data.general_overview:
        story.append(Paragraph("Position Overview", s["section_heading"]))
        if data.ai_metadata:
            ai_label = (
                f"AI Generated — Model: {data.ai_metadata.model} · "
                f"Prompt v{data.ai_metadata.prompt_version}"
                + (" · Modified by User" if data.ai_metadata.modified else "")
            )
            story.append(Paragraph(ai_label, s["ai_note"]))
        story.append(Paragraph(data.general_overview, s["body"]))
        story.append(Spacer(1, 6))

    # ------------------------------------------------------------------
    # 2. KEY DUTIES AND RESPONSIBILITIES
    # ------------------------------------------------------------------
    key_act = elements_by_key.get("key_activities")
    if key_act and key_act.statements:
        story.append(Paragraph("Key Duties and Responsibilities", s["section_heading"]))
        for stmt in key_act.statements:
            text = stmt.styled_variant.styled_text if stmt.styled_variant else stmt.text
            tag = get_source_tag(stmt.source_attribute)
            tag_color = get_source_color(stmt.source_attribute)
            # Inline colored tag via reportlab XML markup
            bullet_text = (
                f"{text}&nbsp;&nbsp;"
                f'<font color="{tag_color}"><b>{tag}</b></font>'
            )
            story.append(Paragraph(f"• {bullet_text}", s["bullet"]))
        story.append(Spacer(1, 6))

    # ------------------------------------------------------------------
    # 3. QUALIFICATIONS AND REQUIREMENTS
    # ------------------------------------------------------------------
    skills_el = elements_by_key.get("skills")
    cc_sels = [
        s_item
        for s_item in data.manager_selections
        if s_item.jd_element == "core_competencies"
    ]

    if skills_el or cc_sels:
        story.append(Paragraph("Qualifications and Requirements", s["section_heading"]))

        if skills_el:
            # Skills
            skill_stmts = [
                st for st in skills_el.statements
                if st.source_attribute not in ("Abilities", "Knowledge")
            ]
            if skill_stmts:
                story.append(Paragraph("Skills", s["sub_heading"]))
                for stmt in skill_stmts:
                    story.append(Paragraph(f"• {stmt.text}", s["bullet"]))

            # Abilities
            ability_stmts = [
                st for st in skills_el.statements
                if st.source_attribute == "Abilities"
            ]
            if ability_stmts:
                story.append(Paragraph("Abilities", s["sub_heading"]))
                for stmt in ability_stmts:
                    story.append(Paragraph(f"• {stmt.text}", s["bullet"]))

            # Knowledge
            know_stmts = [
                st for st in skills_el.statements
                if st.source_attribute == "Knowledge"
            ]
            if know_stmts:
                story.append(Paragraph("Knowledge", s["sub_heading"]))
                for stmt in know_stmts:
                    story.append(Paragraph(f"• {stmt.text}", s["bullet"]))

        # Core Competencies
        if cc_sels:
            story.append(Paragraph("Core Competencies", s["sub_heading"]))
            for sel in cc_sels:
                story.append(Paragraph(f"• {sel.text}", s["bullet"]))

        story.append(Spacer(1, 6))

    # ------------------------------------------------------------------
    # 4. EFFORT & PHYSICAL DEMANDS
    # ------------------------------------------------------------------
    effort_el = elements_by_key.get("effort")
    if effort_el and effort_el.statements:
        story.append(Paragraph("Effort &amp; Physical Demands", s["section_heading"]))
        for stmt in effort_el.statements:
            story.append(Paragraph(f"• {stmt.text}", s["bullet"]))
        story.append(Spacer(1, 6))

    # ------------------------------------------------------------------
    # 5. RESPONSIBILITIES
    # ------------------------------------------------------------------
    resp_el = elements_by_key.get("responsibility")
    if resp_el and resp_el.statements:
        story.append(Paragraph("Responsibilities", s["section_heading"]))
        for stmt in resp_el.statements:
            story.append(Paragraph(f"• {stmt.text}", s["bullet"]))
        story.append(Spacer(1, 6))

    # ------------------------------------------------------------------
    # APPENDICES (if include_provenance)
    # ------------------------------------------------------------------
    if include_provenance:

        # ── Appendix A: Data Provenance & Compliance ──────────────────
        story.append(PageBreak())
        story.append(
            Paragraph("Appendix A: Data Provenance &amp; Compliance", s["appendix_heading"])
        )

        # Source Information
        story.append(Paragraph("Source Information", s["sub_heading"]))
        source_rows = [
            ["NOC Code", data.noc_code],
            ["Data Source", "JobForge 2.0 / OASIS (Occupational and Skills Information System)"],
            ["Source Authority", "Employment and Social Development Canada (ESDC)"],
            ["Generated By", "JobForge JD Builder 1.0"],
            ["Generation Date", data.generated_at.strftime("%Y-%m-%d %H:%M UTC")],
            ["NOC Version", data.source_metadata.version],
            ["Profile URL", data.source_metadata.profile_url],
            ["Retrieved", data.source_metadata.scraped_at.strftime("%Y-%m-%d %H:%M UTC")],
        ]
        story.append(_kv_table(source_rows))
        story.append(Spacer(1, 8))

        # DAMA DMBOK Compliance
        story.append(Paragraph("DAMA DMBOK Compliance", s["sub_heading"]))
        story.append(
            Paragraph(
                "Data management complies with the GC Data Quality Management Framework "
                "(DAMA DMBOK 2.0). All data sourced from authoritative Government of Canada "
                "occupational classification systems with documented lineage and timestamped "
                "retrieval.",
                s["body"],
            )
        )
        story.append(Spacer(1, 6))

        # DADM Directive Compliance (Section 6.2.7)
        story.append(
            Paragraph("DADM Directive Compliance (Section 6.2.7)", s["sub_heading"])
        )
        for sec in data.compliance_sections:
            if sec.section_id == "6.2.7":
                story.append(Paragraph(sec.content.get("description", ""), s["body"]))
                total = sec.content.get("total_selections", 0)
                story.append(
                    Paragraph(f"Total selections: {total}", s["body"])
                )
                selections = sec.content.get("selections", [])
                if selections:
                    sel_headers = ["JD Element", "Statement", "Source", "Publication Date"]
                    sel_rows = []
                    for sel in selections:
                        stmt_text = sel.get("statement", "")
                        sel_rows.append([
                            sel.get("jd_element", ""),
                            (stmt_text[:80] + "…") if len(stmt_text) > 80 else stmt_text,
                            sel.get("source_attribute", ""),
                            sel.get("publication_date", ""),
                        ])
                    story.append(
                        _data_table(
                            sel_headers,
                            sel_rows,
                            col_widths=[1.2 * inch, 3.2 * inch, 1.0 * inch, 1.1 * inch],
                        )
                    )
        story.append(Spacer(1, 6))

        # Directive on Classification Compliance (Section 4.1.2)
        story.append(
            Paragraph(
                "Directive on Classification Compliance (Section 4.1.2)", s["sub_heading"]
            )
        )
        if data.include_classification and data.classification_result:
            recs = data.classification_result.get("recommendations", [])
            if recs:
                top = recs[0]
                story.append(
                    Paragraph(
                        f"Occupational group allocation performed per TBS Directive on "
                        f"Classification Section 4.1.2. Recommended group: "
                        f"{top['group_code']} — {top['group_name']} "
                        f"({top['confidence']}% confidence). "
                        f"Full rationale recorded in Classification section.",
                        s["body"],
                    )
                )
        else:
            story.append(
                Paragraph(
                    "Classification Step 1 not yet performed for this job description. "
                    "Proceed to the Classify step to generate an occupational group "
                    "recommendation per TBS Directive on Classification Section 4.1.2.",
                    s["body"],
                )
            )

        # ── Appendix B: Policy Provenance ────────────────────────────
        story.append(PageBreak())
        story.append(Paragraph("Appendix B: Policy Provenance", s["appendix_heading"]))

        # Authoritative Data Sources table
        story.append(Paragraph("Authoritative Data Sources", s["sub_heading"]))
        retrieval_date = data.source_metadata.scraped_at.strftime("%Y-%m-%d")
        prov_headers = ["Source", "Data Steward", "Publication", "Times Removed"]
        prov_rows = [
            ["2021 NOC", "ESDC", retrieval_date, "0 — Direct"],
            ["OaSIS", "ESDC", retrieval_date, "0 — Direct"],
            ["O*NET SOC (US)", "U.S. Dept. of Labor / ETA", "2024", "1 — Crosswalked"],
        ]
        # Add JobForge entries if section_sources present
        if data.source_metadata.section_sources:
            for section_key, source_val in data.source_metadata.section_sources.items():
                if source_val == "jobforge":
                    prov_rows.append([
                        f"JobForge 2.0 Gold Parquet ({section_key})",
                        "JobForge Data Pipeline",
                        "Current",
                        "1 — Crosswalked from NOC/OaSIS source tables",
                    ])
        story.append(
            _data_table(
                prov_headers,
                prov_rows,
                col_widths=[1.8 * inch, 2.0 * inch, 0.9 * inch, 1.8 * inch],
            )
        )
        story.append(Spacer(1, 8))

        # Degrees of Separation legend
        story.append(Paragraph("Degrees of Separation Legend", s["sub_heading"]))
        legend_rows = [
            ["0 — Direct", "Data retrieved directly from authoritative source"],
            ["1 — Crosswalked", "Data mapped from one authoritative taxonomy to another"],
            ["2+ — Derived", "Data computed or inferred from source data"],
        ]
        story.append(_kv_table(legend_rows))
        story.append(Spacer(1, 8))

        # AI-Generated Content (if ai_metadata present)
        if data.ai_metadata:
            story.append(Paragraph("AI-Generated Content", s["sub_heading"]))
            ai_rows = [
                ["Content Type", "Position Overview (General Overview)"],
                ["Model", data.ai_metadata.model],
                [
                    "Generation Timestamp",
                    data.ai_metadata.timestamp.strftime("%Y-%m-%d %H:%M UTC"),
                ],
                ["Prompt Version", data.ai_metadata.prompt_version],
                ["Input Statements", str(len(data.ai_metadata.input_statement_ids))],
                ["Modified by User", "Yes" if data.ai_metadata.modified else "No"],
                [
                    "Purpose",
                    "Synthesize selected NOC statements into cohesive position overview prose",
                ],
            ]
            story.append(_kv_table(ai_rows))
            story.append(Spacer(1, 6))

        # ── Appendix C: Data Quality ──────────────────────────────────
        if include_audit:
            story.append(PageBreak())
            story.append(
                Paragraph(
                    "Appendix C: Data Quality (DAMA DMBOK)", s["appendix_heading"]
                )
            )
            for sec in data.compliance_sections:
                if sec.section_id == "6.3.5":
                    c = sec.content
                    dq_headers = ["Dimension", "Requirement", "How Met"]
                    dq_rows = [
                        [
                            "Accuracy",
                            c.get("accurate", {}).get("requirement", ""),
                            c.get("accurate", {}).get("how_met", ""),
                        ],
                        [
                            "Completeness",
                            "Data must be complete for its intended purpose",
                            "All selected JD elements retrieved from authoritative "
                            "NOC/OaSIS sources with no truncation",
                        ],
                        [
                            "Consistency",
                            "Data must be consistent across sources",
                            "NOC 2021 v1.0 used as single authoritative taxonomy; "
                            "crosswalks documented in provenance chain",
                        ],
                        [
                            "Timeliness",
                            c.get("up_to_date", {}).get("requirement", ""),
                            c.get("up_to_date", {}).get("how_met", ""),
                        ],
                    ]
                    story.append(
                        _data_table(
                            dq_headers,
                            dq_rows,
                            col_widths=[1.0 * inch, 2.5 * inch, 3.0 * inch],
                        )
                    )

    # Build document
    doc.build(story)
    buf.seek(0)
    return buf.read()


# ---------------------------------------------------------------------------
# Preview (HTML) — unchanged, uses Jinja templates
# ---------------------------------------------------------------------------
def render_preview(data: ExportData) -> str:
    """
    Render preview HTML (Jinja template for browser display).

    Args:
        data: Complete export data structure

    Returns:
        HTML string for browser display
    """
    return render_template(
        "export/jd_preview.html",
        data=data,
        noc_code=data.noc_code,
        job_title=data.job_title,
        general_overview=data.general_overview,
        jd_elements=data.jd_elements,
        compliance_sections=data.compliance_sections,
        ai_metadata=data.ai_metadata,
        source_metadata=data.source_metadata,
        generated_at=data.generated_at,
        classification_result=data.classification_result,
        include_classification=data.include_classification,
        app_version="5.1",
        tbs_data_version="2026-01",
    )
