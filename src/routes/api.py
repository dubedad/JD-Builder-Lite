"""API routes for NOC data search and profile fetching."""

from typing import List, Dict
from functools import wraps
import hashlib
import json
from flask import Blueprint, jsonify, request, current_app, Response, stream_with_context, session, send_file
from io import BytesIO
import requests
import re
from src.services.scraper import scraper
from src.services.parser import parser
from src.services.mapper import mapper
from src.services.llm_service import generate_stream, get_model_name, get_prompt_version, select_occupation_icon, generate_occupation_description
from src.services.generation_service import get_generation_service
from src.services.export_service import build_export_data
from src.services.pdf_generator import generate_pdf, render_preview
from src.services.docx_generator import generate_docx
from src.models.responses import SearchResponse, ProfileResponse, ErrorResponse
from src.models.noc import SourceMetadata
from src.models.ai import GenerationRequest, GenerationMetadata, StatementInput, JobContext
from src.models.export_models import ExportRequest
from src.config import OASIS_BASE_URL, OASIS_VERSION
from src.services.search_parquet_reader import search_parquet_reader
from datetime import datetime

# Create API blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Simple in-memory cache for allocation results
# Per CONTEXT.md: Cache results with invalidation when JD changes
_allocation_cache: Dict[str, dict] = {}


def _cache_key(data: dict) -> str:
    """Generate cache key from request data.

    Key changes when JD content changes, invalidating cache.
    """
    # Sort keys for consistent hashing
    normalized = json.dumps(data, sort_keys=True)
    return hashlib.sha256(normalized.encode()).hexdigest()[:16]


def clear_allocation_cache():
    """Clear allocation cache (for testing or manual invalidation)."""
    global _allocation_cache
    _allocation_cache.clear()

# Regex pattern for NOC code validation (5 digits, optional .2 digits)
NOC_CODE_PATTERN = re.compile(r'^\d{5}(?:\.\d{2})?$')


@api_bp.route('/ping')
def ping():
    """Simple health check endpoint."""
    return jsonify({"status": "ok"})


@api_bp.route('/search')
def search():
    """Search OASIS for NOC profiles by query string.

    Query params:
        q: Search query (minimum 2 characters)
        type: Search type - "Keyword" or "Code" (default: "Keyword")

    Returns:
        SearchResponse with results array and metadata
        ErrorResponse with 400/500/502 on error
    """
    query = request.args.get('q', '')
    search_type = request.args.get('type', 'Keyword')

    # Validate search_type
    if search_type not in ['Keyword', 'Code']:
        search_type = 'Keyword'

    # Validate query
    if not query or len(query) < 2:
        error = ErrorResponse(
            error="Invalid query",
            detail="Query parameter 'q' must be at least 2 characters"
        )
        return jsonify(error.model_dump()), 400

    try:
        # --- SRCH-01/SRCH-03: Try parquet first for sub-second response ---
        parquet_results = search_parquet_reader.search(query, search_type=search_type)

        if parquet_results is not None and len(parquet_results) > 0:
            # Parquet path: results already scored by SearchParquetReader (SRCH-02).
            # Hierarchy fields (sub_major_group, unit_group, broad_category) are
            # already populated by _build_result() in search_parquet_reader.py.
            # Skip OASIS scraper call and the OASIS scoring block entirely.
            results = parquet_results
        else:
            # Fallback path: parquet returned None (LOAD_ERROR) or [] (no matches).
            # Run existing OASIS scraper unchanged — user sees results, not an error.

            # Fetch and parse search results
            html = scraper.search(query, search_type=search_type)
            results = parser.parse_search_results_enhanced(html)

            # Populate hierarchy codes for filter building (18-02)
            for r in results:
                code = r.noc_code.split('.')[0] if r.noc_code else ''
                r.sub_major_group = code[:3] if len(code) >= 3 else None
                r.unit_group = code[:4] if len(code) >= 4 else None

            # Score results by relevance with confidence % and rationale (SRCH-13)
            # Stem each word independently: "Engineers" → "Engineer", "Printing" → "Print"
            query_lower = query.lower()
            def _stem_word(word):
                stemmed = re.sub(r'(ers?|ing|tion|ment|ed|ly|s)$', '', word, count=1)
                return stemmed if len(stemmed) >= 3 else word
            query_stems = [_stem_word(w) for w in query_lower.split()]
            query_stem = ' '.join(query_stems)

            def _find_matched_word(text, stem):
                """Find the actual word in text that contains the stem."""
                words = re.findall(r'\b\w*' + re.escape(stem) + r'\w*\b', text, re.IGNORECASE)
                return words[0] if words else stem

            def _normalize_plural(text):
                """Normalize plural suffixes for near-exact title comparison."""
                words = text.lower().split()
                out = []
                for w in words:
                    if w.endswith('ies') and len(w) > 4:
                        out.append(w[:-3] + 'y')
                    elif w.endswith('es') and len(w) > 3:
                        out.append(w[:-2])
                    elif w.endswith('s') and len(w) > 2 and not w.endswith('ss'):
                        out.append(w[:-1])
                    else:
                        out.append(w)
                return ' '.join(out)

            query_norm = _normalize_plural(query_lower)

            for result in results:
                title_lower = result.title.lower()
                lead_lower = (result.lead_statement or '').lower()

                title_has_exact = query_lower in title_lower
                title_has_stem = query_stem in title_lower or any(s in title_lower for s in query_stems)
                lead_has_exact = query_lower in lead_lower
                lead_has_stem = query_stem in lead_lower or any(s in lead_lower for s in query_stems)

                # Near-exact: query ≈ title after normalizing plurals (S1-15)
                title_norm = _normalize_plural(title_lower)
                is_near_exact = query_norm == title_norm

                if is_near_exact:
                    result.relevance_score = 100
                    result.match_reason = f"Exact title match: \"{query}\""
                elif title_has_exact:
                    result.relevance_score = 95
                    result.match_reason = f"Title contains \"{query}\""
                elif title_has_stem:
                    matched = _find_matched_word(result.title, query_stem)
                    result.relevance_score = 90
                    result.match_reason = f"Title contains \"{matched}\""
                elif lead_has_exact:
                    result.relevance_score = 60
                    result.match_reason = f"Description mentions \"{query}\""
                elif lead_has_stem:
                    matched = _find_matched_word(result.lead_statement, query_stem)
                    result.relevance_score = 50
                    result.match_reason = f"Description mentions \"{matched}\""
                else:
                    result.relevance_score = 10
                    result.match_reason = "Matched on alternate job title not shown"

        # --- Common path: sort, filter, and construct response (both parquet and OASIS) ---

        # Sort by relevance score descending (best matches first)
        results.sort(key=lambda r: r.relevance_score or 0, reverse=True)

        # Hide low-confidence results (S1-01: filter out ≤20%)
        results = [r for r in results if (r.relevance_score or 0) > 20]

        # Create response with metadata
        response = SearchResponse(
            query=query,
            results=results,
            count=len(results),
            metadata=SourceMetadata(
                noc_code="",  # Not applicable for search
                profile_url=f"{OASIS_BASE_URL}/OaSIS/OaSISSearchResult",
                scraped_at=datetime.utcnow(),
                version=OASIS_VERSION
            )
        )

        return jsonify(response.model_dump())

    except requests.RequestException as e:
        current_app.logger.error(f"Search request failed: {e}")
        error = ErrorResponse(
            error="Search failed",
            detail=str(e)
        )
        return jsonify(error.model_dump()), 502

    except Exception as e:
        current_app.logger.error(f"Search internal error: {e}")
        error = ErrorResponse(
            error="Internal error",
            detail=None  # Don't expose internal details to client
        )
        return jsonify(error.model_dump()), 500


@api_bp.route('/profile')
def profile():
    """Fetch full NOC profile with JD element mapping.

    Query params:
        code: NOC code (e.g., "21232" or "21232.00")

    Returns:
        ProfileResponse with JD elements and metadata
        ErrorResponse with 400/500/502 on error
    """
    code = request.args.get('code', '')

    # Validate NOC code presence
    if not code:
        error = ErrorResponse(
            error="Invalid request",
            detail="Query parameter 'code' is required"
        )
        return jsonify(error.model_dump()), 400

    # Validate NOC code format
    if not NOC_CODE_PATTERN.match(code):
        error = ErrorResponse(
            error="Invalid NOC code",
            detail=f"Code must match pattern XXXXX or XXXXX.XX (got: {code})"
        )
        return jsonify(error.model_dump()), 400

    # Block 1: OASIS fetch (falls back to stub on any failure)
    try:
        html = scraper.fetch_profile(code)
        noc_data = parser.parse_profile(html, code)
    except Exception as e:
        current_app.logger.warning(
            f"OASIS fetch failed for {code}, falling back to parquet-only: {e}"
        )
        noc_data = {
            'noc_code': code,
            'title': f'NOC {code}',
            'main_duties': [],
            'work_activities': [],
            'skills': [],
            'abilities': [],
            'knowledge': [],
            'work_context': [],
            'noc_hierarchy': None,
            'reference_attributes': None,
        }

    # Block 2: Mapper + response (parquet tabs served regardless of OASIS outcome)
    try:
        jd_data = mapper.to_jd_elements(noc_data)
        response = ProfileResponse(**jd_data)
        return jsonify(response.model_dump())
    except Exception as e:
        current_app.logger.error(f"Profile internal error for code {code}: {e}")
        error = ErrorResponse(
            error="Internal error",
            detail=None
        )
        return jsonify(error.model_dump()), 500


@api_bp.route('/generate', methods=['POST'])
def generate():
    """Generate AI overview from selected statements.

    Expects JSON body:
    {
        "statements": [{"id": "...", "text": "...", "source_attribute": "...", "jd_element": "..."}],
        "context": {"job_title": "...", "noc_code": "...", "noc_title": "..."}
    }

    Returns:
        SSE stream with tokens, [DONE] on success, [ERROR] on failure
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body required"}), 400

        # Validate request
        gen_request = GenerationRequest(**data)

        if len(gen_request.statements) == 0:
            return jsonify({"error": "At least one statement required"}), 400

        # Record provenance metadata in session BEFORE generation
        metadata = GenerationMetadata(
            model=get_model_name(),
            prompt_version=get_prompt_version(),
            input_statement_ids=[s.id for s in gen_request.statements],
            timestamp=datetime.utcnow(),
            modified=False
        )
        session['ai_generation'] = metadata.model_dump(mode='json')
        session.modified = True

        # Stream response
        return Response(
            stream_with_context(generate_stream(
                gen_request.statements,
                gen_request.context,
                gen_request.additional_context
            )),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no',
                'Connection': 'keep-alive'
            }
        )

    except Exception as e:
        current_app.logger.error(f"Generation error: {e}")
        return jsonify({"error": "Generation failed", "detail": str(e)}), 500


@api_bp.route('/mark-modified', methods=['POST'])
def mark_modified():
    """Mark the AI-generated text as modified by user.

    Called when user edits the generated overview textarea.
    Updates session metadata for provenance tracking.
    """
    if 'ai_generation' in session:
        session['ai_generation']['modified'] = True
        session.modified = True
        return jsonify({"status": "ok", "modified": True})
    return jsonify({"status": "ok", "modified": False})


@api_bp.route('/generation-metadata', methods=['GET'])
def get_generation_metadata():
    """Get current AI generation metadata from session.

    Used by frontend to display provenance info and by PDF export.
    """
    if 'ai_generation' in session:
        return jsonify(session['ai_generation'])
    return jsonify(None)


@api_bp.route('/health')
def health():
    """Health check endpoint.

    Returns:
        Status OK with version
    """
    return jsonify({
        "status": "ok",
        "version": "1.0.0"
    })


@api_bp.route('/preview', methods=['POST'])
def preview():
    """Render JD preview HTML for browser display.

    Expects JSON body matching ExportRequest schema.

    Returns:
        HTML string for browser rendering
        ErrorResponse with 400/500 on error
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify(ErrorResponse(
                error="Request body required"
            ).model_dump()), 400

        # Validate and parse request
        export_request = ExportRequest(**data)

        # Fetch raw NOC data for Annex generation
        raw_noc_data = None
        try:
            html = scraper.fetch_profile(export_request.noc_code)
            raw_noc_data = parser.parse_profile(html, export_request.noc_code)
        except Exception as e:
            current_app.logger.warning(f"Could not fetch NOC data for Annex: {e}")
            # Continue without Annex data - graceful degradation

        # Build export data with Annex
        export_data = build_export_data(export_request, raw_noc_data)

        # Render preview HTML
        preview_html = render_preview(export_data)

        return preview_html, 200, {'Content-Type': 'text/html'}

    except Exception as e:
        current_app.logger.error(f"Preview error: {e}")
        return jsonify(ErrorResponse(
            error="Preview generation failed",
            detail=str(e)
        ).model_dump()), 500


@api_bp.route('/export/pdf', methods=['POST'])
def export_pdf():
    """Generate and download PDF job description.

    Expects JSON body matching ExportRequest schema.

    Returns:
        PDF file download with Content-Disposition header
        ErrorResponse with 400/500 on error
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify(ErrorResponse(
                error="Request body required"
            ).model_dump()), 400

        # Validate and parse request
        export_request = ExportRequest(**data)

        # Fetch raw NOC data for Annex generation
        raw_noc_data = None
        try:
            html = scraper.fetch_profile(export_request.noc_code)
            raw_noc_data = parser.parse_profile(html, export_request.noc_code)
        except Exception as e:
            current_app.logger.warning(f"Could not fetch NOC data for Annex: {e}")
            # Continue without Annex data - graceful degradation

        # Build export data with Annex
        export_data = build_export_data(export_request, raw_noc_data)

        # Generate PDF
        pdf_bytes = generate_pdf(export_data, request.url_root)

        # Create filename per CONTEXT.md: {NOC code} - {Title} - {date} - Job Description.pdf
        safe_title = "".join(c for c in export_data.job_title if c.isalnum() or c in " -_")[:50]
        today = datetime.utcnow().strftime('%Y-%m-%d')
        filename = f"{export_data.noc_code} - {safe_title} - {today} - Job Description.pdf"

        # Return as download
        return send_file(
            BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        current_app.logger.error(f"PDF export error: {e}")
        return jsonify(ErrorResponse(
            error="PDF generation failed",
            detail=str(e)
        ).model_dump()), 500


@api_bp.route('/export/docx', methods=['POST'])
def export_docx():
    """Generate and download Word document job description.

    Expects JSON body matching ExportRequest schema.

    Returns:
        DOCX file download with Content-Disposition header
        ErrorResponse with 400/500 on error
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify(ErrorResponse(
                error="Request body required"
            ).model_dump()), 400

        # Validate and parse request
        export_request = ExportRequest(**data)

        # Fetch raw NOC data for Annex generation
        raw_noc_data = None
        try:
            html = scraper.fetch_profile(export_request.noc_code)
            raw_noc_data = parser.parse_profile(html, export_request.noc_code)
        except Exception as e:
            current_app.logger.warning(f"Could not fetch NOC data for Annex: {e}")
            # Continue without Annex data - graceful degradation

        # Build export data with Annex
        export_data = build_export_data(export_request, raw_noc_data)

        # Generate DOCX
        docx_bytes = generate_docx(export_data)

        # Create filename per CONTEXT.md: {NOC code} - {Title} - {date} - Job Description.docx
        safe_title = "".join(c for c in export_data.job_title if c.isalnum() or c in " -_")[:50]
        today = datetime.utcnow().strftime('%Y-%m-%d')
        filename = f"{export_data.noc_code} - {safe_title} - {today} - Job Description.docx"

        # Return as download
        return send_file(
            BytesIO(docx_bytes),
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        current_app.logger.error(f"DOCX export error: {e}")
        return jsonify(ErrorResponse(
            error="Word document generation failed",
            detail=str(e)
        ).model_dump()), 500


@api_bp.route('/occupation-icon', methods=['POST'])
def occupation_icon():
    """Select an appropriate icon for an occupation using LLM.

    Expects JSON body:
    {
        "occupation_title": str,
        "lead_statement": str
    }

    Returns:
        {"icon_class": "fa-atom"} on success
        ErrorResponse with 400/500 on error
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify(ErrorResponse(
                error="Request body required"
            ).model_dump()), 400

        # Validate required fields
        occupation_title = data.get('occupation_title', '').strip()
        lead_statement = data.get('lead_statement', '').strip()

        if not occupation_title or not lead_statement:
            return jsonify(ErrorResponse(
                error="Invalid request",
                detail="Both 'occupation_title' and 'lead_statement' are required and must be non-empty"
            ).model_dump()), 400

        # Call LLM service
        icon_class = select_occupation_icon(occupation_title, lead_statement)

        return jsonify({"icon_class": icon_class})

    except Exception as e:
        current_app.logger.error(f"Occupation icon error: {e}")
        return jsonify(ErrorResponse(
            error="Icon selection failed",
            detail=str(e)
        ).model_dump()), 500


@api_bp.route('/occupation-description', methods=['POST'])
def occupation_description():
    """Generate a concise occupation description using LLM.

    Expects JSON body:
    {
        "occupation_title": str,
        "lead_statement": str,
        "main_duties": list[str]
    }

    Returns:
        {"description": "...paragraph..."} on success
        ErrorResponse with 400/500 on error
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify(ErrorResponse(
                error="Request body required"
            ).model_dump()), 400

        # Validate required fields
        occupation_title = data.get('occupation_title', '').strip()
        lead_statement = data.get('lead_statement', '').strip()
        main_duties = data.get('main_duties', [])

        if not occupation_title or not lead_statement:
            return jsonify(ErrorResponse(
                error="Invalid request",
                detail="Both 'occupation_title' and 'lead_statement' are required and must be non-empty"
            ).model_dump()), 400

        # Validate main_duties is a list (can be empty)
        if not isinstance(main_duties, list):
            return jsonify(ErrorResponse(
                error="Invalid request",
                detail="'main_duties' must be a list"
            ).model_dump()), 400

        # Call LLM service
        description = generate_occupation_description(occupation_title, lead_statement, main_duties)

        return jsonify({"description": description})

    except Exception as e:
        current_app.logger.error(f"Occupation description error: {e}")
        return jsonify(ErrorResponse(
            error="Description generation failed",
            detail=str(e)
        ).model_dump()), 500


@api_bp.route('/style', methods=['POST'])
def style_statement():
    """Generate styled variant of a NOC statement.

    Request JSON:
        {
            "statement_id": str,  # e.g., "key_activities-0"
            "text": str,          # Original NOC statement text
            "section": str        # JD element: key_activities, skills, effort, working_conditions
        }

    Response JSON (success):
        {
            "success": true,
            "styled_statement": {
                "original_noc_statement_id": str,
                "original_noc_text": str,
                "styled_text": str,
                "content_type": str,  # "ai_styled" or "original_noc"
                "confidence_score": float,
                "vocabulary_coverage": float,
                "retry_count": int,
                "is_fallback": bool
            }
        }

    Response JSON (error):
        {
            "success": false,
            "error": str
        }
    """
    try:
        data = request.get_json()

        # Validate required fields
        required = ['statement_id', 'text', 'section']
        for field in required:
            if field not in data:
                return jsonify({"success": False, "error": f"Missing required field: {field}"}), 400

        statement_id = data['statement_id']
        text = data['text']
        section = data['section']

        # Validate section
        valid_sections = ['key_activities', 'skills', 'effort', 'working_conditions',
                          'abilities', 'knowledge', 'core_competencies', 'responsibility']
        if section not in valid_sections:
            return jsonify({
                "success": False,
                "error": f"Invalid section. Must be one of: {', '.join(valid_sections)}"
            }), 400

        # Get generation service via singleton (initialized at app startup)
        # Import vocab_index from app inside function to avoid circular import
        from src.app import vocab_index
        gen_service = get_generation_service(vocab_index)

        # Generate styled statement
        styled = gen_service.generate_styled_statement(
            noc_statement_id=statement_id,
            noc_text=text,
            section=section
        )

        # Convert to response format
        response_data = {
            "success": True,
            "styled_statement": {
                "original_noc_statement_id": styled.original_noc_statement_id,
                "original_noc_text": styled.original_noc_text,
                "styled_text": styled.styled_text,
                "content_type": styled.content_type.value,  # Enum to string
                "confidence_score": styled.confidence_score,
                "vocabulary_coverage": styled.vocabulary_coverage,
                "retry_count": styled.retry_count,
                "is_fallback": styled.content_type.value == "original_noc"
            }
        }

        return jsonify(response_data)

    except Exception as e:
        # Log the error for debugging
        current_app.logger.error(f"Style generation error: {str(e)}")

        return jsonify({
            "success": False,
            "error": "Failed to generate styled statement. Please try again."
        }), 500


@api_bp.route('/allocate', methods=['POST'])
def allocate():
    """Allocate JD to occupational groups with provenance.

    Implements API-01, API-02, API-03, API-04 requirements.

    Request JSON:
        AllocationRequest with position_title, client_service_results,
        key_activities (required), skills, labels (optional)

    Response JSON (200):
        AllocationResponse with recommendations, provenance_map,
        confidence_summary, and edge case fields if applicable.

    Per CONTEXT.md:
    - Return HTTP 200 for all responses including edge cases
    - Edge cases use status field ("needs_clarification", "invalid_combination")
    - Full provenance embedded in each recommendation
    """
    from pydantic import ValidationError
    from src.models.allocation import (
        AllocationRequest,
        AllocationResponse,
        ALLOCATION_STATUS_SUCCESS,
        ALLOCATION_STATUS_NEEDS_CLARIFICATION,
        ALLOCATION_STATUS_INVALID_COMBINATION,
    )
    from src.models.responses import ErrorResponse
    from src.matching.provenance_builder import build_provenance_map, build_confidence_summary

    try:
        # Validate request body exists
        data = request.get_json()
        if not data:
            return jsonify(ErrorResponse(
                error="Request body required"
            ).model_dump(mode='json')), 400

        # Validate request schema (API-01)
        allocation_request = AllocationRequest(**data)

        # Check cache (per CONTEXT.md: cache with invalidation)
        cache_key = _cache_key(allocation_request.model_dump())
        if cache_key in _allocation_cache:
            current_app.logger.info(f"Returning cached allocation for {cache_key}")
            return jsonify(_allocation_cache[cache_key]), 200

        # Call matching engine (Phase 15)
        try:
            from src.matching.allocator import OccupationalGroupAllocator
            allocator = OccupationalGroupAllocator()
            current_app.logger.info(f"Starting allocation for '{allocation_request.position_title}' with {len(allocation_request.key_activities)} activities")
            result = allocator.allocate(allocation_request.model_dump())
            current_app.logger.info(f"Allocation complete: {len(result.top_recommendations)} recommendations")
        except ImportError:
            # Allocator not yet implemented - return helpful error
            current_app.logger.warning("OccupationalGroupAllocator not yet available")
            return jsonify(ErrorResponse(
                error="Allocation engine not available",
                detail="Phase 15 allocator implementation in progress"
            ).model_dump(mode='json')), 503
        except Exception as e:
            # Catch all other exceptions from allocator
            import traceback
            current_app.logger.error(f"Allocation engine error: {str(e)}")
            current_app.logger.error(traceback.format_exc())
            return jsonify(ErrorResponse(
                error="Allocation engine error",
                detail=str(e)
            ).model_dump(mode='json')), 500

        # Build provenance map (API-02)
        provenance_map = build_provenance_map(result)

        # Build confidence summary (API-03)
        confidence_summary = build_confidence_summary(result)

        # Determine response status based on edge cases (API-04)
        status = ALLOCATION_STATUS_SUCCESS
        clarification_needed = None
        conflicting_duties = None

        if result.match_context and "split duties detected" in result.match_context.lower():
            status = ALLOCATION_STATUS_INVALID_COMBINATION
            conflicting_duties = result.duty_split
        elif not result.top_recommendations:
            status = ALLOCATION_STATUS_NEEDS_CLARIFICATION
            clarification_needed = _detect_missing_fields(allocation_request)
        elif confidence_summary and max(confidence_summary.values()) < allocation_request.minimum_confidence:
            status = ALLOCATION_STATUS_NEEDS_CLARIFICATION
            clarification_needed = ["Insufficient confidence - provide more detail in Client-Service Results and Key Activities"]

        # Build response (API-01, API-02, API-03)
        response = AllocationResponse(
            status=status,
            recommendations=result.top_recommendations,
            provenance_map=provenance_map,
            primary_purpose_summary=result.primary_purpose_summary,
            match_context=result.match_context,
            borderline_flag=result.borderline_flag,
            confidence_summary=confidence_summary,
            clarification_needed=clarification_needed,
            conflicting_duties=conflicting_duties,
            warnings=result.warnings if result.warnings else None,
            constraints_compliance=result.constraints_compliance
        )

        # Cache the response (invalidated when JD changes)
        response_dict = response.model_dump(mode='json')
        _allocation_cache[cache_key] = response_dict

        # Per CONTEXT.md: Return HTTP 200 for all cases including edge cases
        return jsonify(response_dict), 200

    except ValidationError as e:
        # Field-specific validation errors
        current_app.logger.warning(f"Validation error in /allocate: {e.errors()}")
        return jsonify(ErrorResponse(
            error="Invalid request data",
            detail=str(e.errors())
        ).model_dump(mode='json')), 400

    except Exception as e:
        current_app.logger.error(f"Allocation failed: {e}", exc_info=True)
        return jsonify(ErrorResponse(
            error="Allocation failed",
            detail=None  # Don't expose internals
        ).model_dump(mode='json')), 500


def _detect_missing_fields(req: 'AllocationRequest') -> List[str]:
    """Detect which fields need more detail for successful allocation.

    Per API-04: Generate helpful guidance when clarification needed.

    Args:
        req: The validated allocation request

    Returns:
        List of fields needing more detail
    """
    missing = []
    if not req.client_service_results or len(req.client_service_results) < 50:
        missing.append("Client-Service Results (needs more detail about position's primary purpose)")
    if not req.key_activities or len(req.key_activities) < 2:
        missing.append("Key Activities (needs at least 2 substantive activities)")
    if not missing:
        missing.append("Work description needs more detail overall")
    return missing
