"""Export service for building export data structures."""

from typing import List, Dict, Any, Optional
from datetime import datetime
from src.models.export_models import (
    ExportRequest, ExportData, JDElementExport, StatementExport,
    SelectionMetadata, ComplianceSection, ProficiencyData, StyledStatementExport
)
from src.models.ai import StyleContentType
from src.models.styled_content import StyledStatement
from src.services.annex_builder import build_annex_data
from src.utils.oasis_provenance import (
    get_publication_date, get_source_table_url, OASIS_DATASET_URL
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


def build_export_data(request: ExportRequest, raw_noc_data: Optional[Dict[str, Any]] = None) -> ExportData:
    """
    Build complete export data structure from request.

    Organizes selections by JD element and builds compliance sections
    with Directive references. Optionally builds Annex data if raw NOC
    data is provided.

    Args:
        request: ExportRequest with selections and metadata
        raw_noc_data: Optional raw NOC profile data for Annex generation
    """
    # Group selections by JD element (with full metadata)
    selections_by_element: Dict[str, List[StatementExport]] = {}
    for selection in request.selections:
        if selection.jd_element not in selections_by_element:
            selections_by_element[selection.jd_element] = []

        # Build StatementExport with description, proficiency, and provenance
        stmt_export = StatementExport(
            text=selection.text,
            source_attribute=selection.source_attribute,
            description=selection.description,
            proficiency=selection.proficiency,
            publication_date=selection.publication_date or get_publication_date(selection.source_attribute),
            source_table_url=selection.source_table_url or get_source_table_url(selection.source_attribute)
        )
        selections_by_element[selection.jd_element].append(stmt_export)

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

    # Build Annex data if raw NOC data provided
    annex_data = None
    if raw_noc_data:
        annex_data = build_annex_data(
            raw_noc_data=raw_noc_data,
            manager_selections=request.selections,
            noc_code=request.noc_code,
            scraped_at=request.source_metadata.scraped_at
        )

    return ExportData(
        noc_code=request.noc_code,
        job_title=request.job_title,
        general_overview=request.general_overview,
        jd_elements=jd_elements,
        manager_selections=request.selections,
        ai_metadata=request.ai_metadata,
        source_metadata=request.source_metadata,
        compliance_sections=compliance_sections,
        annex_data=annex_data,
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

    # Section 6.2.7: Manager Decisions with full provenance
    selections_data = []
    for sel in request.selections:
        # Get provenance data for this selection
        pub_date = sel.publication_date or get_publication_date(sel.source_attribute)
        source_url = sel.source_table_url or get_source_table_url(sel.source_attribute)

        selections_data.append({
            "jd_element": JD_ELEMENT_LABELS.get(sel.jd_element, sel.jd_element),
            "statement": sel.text,
            "source_attribute": sel.source_attribute,
            "publication_date": pub_date,
            "source_url": source_url,
            "selected_at": sel.selected_at.isoformat()
        })

    sections.append(ComplianceSection(
        section_id="6.2.7",
        title="Documented Decisions (Directive 6.2.7)",
        content={
            "description": "This job description was created using the JD Builder Lite tool. "
                          "All content selections were made by the hiring manager from "
                          "authoritative NOC data published on Open Canada.",
            "total_selections": len(request.selections),
            "selections": selections_data,
            "oasis_dataset_url": OASIS_DATASET_URL
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


def build_styled_content_disclosure(
    styled_statements: List[StyledStatement]
) -> Optional[Dict[str, Any]]:
    """Build styled content metadata for compliance appendix.

    Creates a disclosure dictionary containing aggregate statistics about
    AI-styled content, including vocabulary coverage, confidence distribution,
    and generation metadata for compliance documentation.

    Args:
        styled_statements: List of StyledStatement objects from session

    Returns:
        Dictionary with styled content disclosure data, or None if no styled content
    """
    if not styled_statements:
        return None

    ai_styled_count = sum(
        1 for s in styled_statements
        if s.content_type == StyleContentType.AI_STYLED
    )
    original_fallback_count = sum(
        1 for s in styled_statements
        if s.content_type == StyleContentType.ORIGINAL_NOC
    )

    # Aggregate vocabulary coverage (only for AI_STYLED)
    coverage_values = [
        s.vocabulary_coverage for s in styled_statements
        if s.content_type == StyleContentType.AI_STYLED
    ]
    avg_coverage = sum(coverage_values) / len(coverage_values) if coverage_values else 0.0
    min_coverage = min(coverage_values) if coverage_values else 0.0

    # Aggregate confidence (only for AI_STYLED)
    confidence_values = [
        s.confidence_score for s in styled_statements
        if s.content_type == StyleContentType.AI_STYLED
    ]
    avg_confidence = sum(confidence_values) / len(confidence_values) if confidence_values else 0.0

    # Confidence distribution using thresholds from Phase 11 (0.8/0.5)
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
