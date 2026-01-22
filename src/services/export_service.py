"""Export service for building export data structures."""

from typing import List, Dict, Any
from datetime import datetime
from src.models.export_models import (
    ExportRequest, ExportData, JDElementExport,
    SelectionMetadata, ComplianceSection
)


# JD Element display names
JD_ELEMENT_LABELS = {
    "key_activities": "Key Activities",
    "skills": "Skills",
    "effort": "Effort",
    "responsibility": "Responsibility",
    "working_conditions": "Working Conditions"
}

# JD Element order for display
JD_ELEMENT_ORDER = ["key_activities", "skills", "effort", "responsibility", "working_conditions"]


def build_export_data(request: ExportRequest) -> ExportData:
    """
    Build complete export data structure from request.

    Organizes selections by JD element and builds compliance sections
    with Directive references.
    """
    # Group selections by JD element
    selections_by_element: Dict[str, List[str]] = {}
    for selection in request.selections:
        if selection.jd_element not in selections_by_element:
            selections_by_element[selection.jd_element] = []
        selections_by_element[selection.jd_element].append(selection.text)

    # Build JD element sections in order
    jd_elements = []
    for key in JD_ELEMENT_ORDER:
        if key in selections_by_element:
            jd_elements.append(JDElementExport(
                name=JD_ELEMENT_LABELS[key],
                key=key,
                statements=selections_by_element[key]
            ))

    # Build compliance sections
    compliance_sections = build_compliance_sections(request)

    return ExportData(
        noc_code=request.noc_code,
        job_title=request.job_title,
        general_overview=request.general_overview,
        jd_elements=jd_elements,
        manager_selections=request.selections,
        ai_metadata=request.ai_metadata,
        source_metadata=request.source_metadata,
        compliance_sections=compliance_sections,
        generated_at=datetime.utcnow()
    )


def build_compliance_sections(request: ExportRequest) -> List[ComplianceSection]:
    """
    Build compliance appendix sections organized by Directive requirements.

    References:
    - Section 6.2.3: Input data, source, method of collection
    - Section 6.2.7: Document decisions made/assisted by automated systems
    - Section 6.3.5: Data must be relevant, accurate, up-to-date
    """
    sections = []

    # Section 6.2.3: Data Sources
    sections.append(ComplianceSection(
        section_id="6.2.3",
        title="Data Sources (Directive 6.2.3)",
        content={
            "data_steward": "Employment and Social Development Canada (ESDC)",
            "authoritative_source": "National Occupational Classification (NOC)",
            "access_method": "Direct retrieval from OASIS (Occupational and Skills Information System)",
            "source_url": request.source_metadata.profile_url,
            "retrieval_timestamp": request.source_metadata.scraped_at.isoformat(),
            "noc_version": request.source_metadata.version
        }
    ))

    # Section 6.2.7: Manager Decisions
    selections_data = []
    for sel in request.selections:
        selections_data.append({
            "jd_element": JD_ELEMENT_LABELS.get(sel.jd_element, sel.jd_element),
            "statement": sel.text,
            "source_attribute": sel.source_attribute,
            "selected_at": sel.selected_at.isoformat()
        })

    sections.append(ComplianceSection(
        section_id="6.2.7",
        title="Documented Decisions (Directive 6.2.7)",
        content={
            "description": "This job description was created using the JD Builder Lite tool. "
                          "All content selections were made by the hiring manager from "
                          "authoritative NOC data.",
            "total_selections": len(request.selections),
            "selections": selections_data
        }
    ))

    # Section 6.3.5: Data Quality
    sections.append(ComplianceSection(
        section_id="6.3.5",
        title="Data Quality Validation (Directive 6.3.5)",
        content={
            "relevant": {
                "requirement": "Data must be relevant to the decision",
                "how_met": "Data sourced from ESDC National Occupational Classification (NOC), "
                          "the authoritative source for occupational data in Canada"
            },
            "accurate": {
                "requirement": "Data must be accurate",
                "how_met": f"Data retrieved directly from OASIS at {request.source_metadata.profile_url}"
            },
            "up_to_date": {
                "requirement": "Data must be up-to-date",
                "how_met": f"NOC Version: {request.source_metadata.version}, "
                          f"Retrieved: {request.source_metadata.scraped_at.strftime('%Y-%m-%d %H:%M:%S UTC')}"
            }
        }
    ))

    # AI Disclosure (if AI was used)
    if request.ai_metadata:
        sections.append(ComplianceSection(
            section_id="ai_disclosure",
            title="AI-Generated Content Disclosure",
            content={
                "description": "The following content was generated using Large Language Model (LLM) technology:",
                "content_type": "General Overview",
                "model": request.ai_metadata.model,
                "generation_timestamp": request.ai_metadata.timestamp.isoformat(),
                "prompt_version": request.ai_metadata.prompt_version,
                "input_count": len(request.ai_metadata.input_statement_ids),
                "modified_by_user": request.ai_metadata.modified,
                "purpose": "Synthesize selected NOC statements into cohesive overview paragraph"
            }
        ))

    return sections
