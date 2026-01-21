"""API routes for NOC data search and profile fetching."""

from flask import Blueprint, jsonify, request, current_app
import requests
import re
from src.services.scraper import scraper
from src.services.parser import parser
from src.services.mapper import mapper
from src.models.responses import SearchResponse, ProfileResponse, ErrorResponse
from src.models.noc import SourceMetadata
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
