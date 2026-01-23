"""API routes for NOC data search and profile fetching."""

from flask import Blueprint, jsonify, request, current_app, Response, stream_with_context, session, send_file
from io import BytesIO
import requests
import re
from src.services.scraper import scraper
from src.services.parser import parser
from src.services.mapper import mapper
from src.services.llm_service import generate_stream, get_model_name, get_prompt_version
from src.services.export_service import build_export_data
from src.services.pdf_generator import generate_pdf, render_preview
from src.services.docx_generator import generate_docx
from src.models.responses import SearchResponse, ProfileResponse, ErrorResponse
from src.models.noc import SourceMetadata
from src.models.ai import GenerationRequest, GenerationMetadata, StatementInput, JobContext
from src.models.export_models import ExportRequest
from src.config import OASIS_BASE_URL, OASIS_VERSION
from datetime import datetime

# Create API blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Regex pattern for NOC code validation (5 digits, optional .2 digits)
NOC_CODE_PATTERN = re.compile(r'^\d{5}(?:\.\d{2})?$')


@api_bp.route('/search')
def search():
    """Search OASIS for NOC profiles by query string.

    Query params:
        q: Search query (minimum 2 characters)

    Returns:
        SearchResponse with results array and metadata
        ErrorResponse with 400/500/502 on error
    """
    query = request.args.get('q', '')

    # Validate query
    if not query or len(query) < 2:
        error = ErrorResponse(
            error="Invalid query",
            detail="Query parameter 'q' must be at least 2 characters"
        )
        return jsonify(error.model_dump()), 400

    try:
        # Fetch and parse search results
        html = scraper.search(query)
        results = parser.parse_search_results(html)

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

    try:
        # Fetch, parse, and map profile data
        html = scraper.fetch_profile(code)
        noc_data = parser.parse_profile(html, code)
        jd_data = mapper.to_jd_elements(noc_data)

        # Create response
        response = ProfileResponse(**jd_data)

        return jsonify(response.model_dump())

    except requests.RequestException as e:
        current_app.logger.error(f"Profile request failed for code {code}: {e}")
        error = ErrorResponse(
            error="Profile fetch failed",
            detail=str(e)
        )
        return jsonify(error.model_dump()), 502

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
                gen_request.context
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
