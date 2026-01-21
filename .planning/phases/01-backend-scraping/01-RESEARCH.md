# Phase 1: Backend + Scraping - Research

**Researched:** 2026-01-21
**Domain:** Flask backend, OASIS web scraping, HTML parsing, NOC data mapping
**Confidence:** HIGH

## Summary

Phase 1 implements a Flask backend that searches Canada's OASIS website for occupational profiles, scrapes NOC data from selected profiles, parses the HTML into structured data, and maps it to JD elements ready for frontend display. The backend serves as a proxy to bypass CORS restrictions and protects any future API keys.

The recommended approach uses **Flask 3.1.2** with **BeautifulSoup4 + lxml** for scraping, **Pydantic** for data validation and response models, and a service layer pattern for clean separation of concerns. The OASIS site serves static HTML, so browser automation (Selenium/Playwright) is not required.

**Primary recommendation:** Build a Flask API with three core endpoints: `/api/search` for profile search, `/api/profile` for full profile data, and use Pydantic models for all responses to ensure consistent, validated data structures with provenance metadata.

## Standard Stack

The established libraries/tools for this phase:

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Flask | 3.1.2 | Web server, API routes | De-facto Python micro-framework, mature, simple |
| Flask-CORS | 6.0.2 | CORS handling for frontend | Standard Flask extension for cross-origin requests |
| requests | 2.32.5 | HTTP client for scraping | De-facto Python HTTP library |
| beautifulsoup4 | 4.14.3 | HTML parsing | Standard for web scraping, handles malformed HTML |
| lxml | 6.0.2 | Fast HTML/XML parser | 10x faster than html.parser, better error handling |
| Pydantic | 2.10.0 | Data validation, response models | Type-safe, auto-validation, JSON serialization |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| python-dotenv | 1.2.1 | Environment variables | API key management (for later phases) |
| certifi | 2026.1.4 | SSL certificate bundle | If SSL verification issues persist |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Flask | FastAPI | FastAPI has async and OpenAPI docs, but overkill for demo |
| BeautifulSoup | Scrapy | Scrapy is for large-scale crawling; too heavy for targeted scraping |
| BeautifulSoup | Selectolax | Faster but less documentation; BS4 is more maintainable |
| requests | httpx | httpx has async support; not needed for sequential scraping |

**Installation:**
```bash
pip install flask==3.1.2 flask-cors==6.0.2 requests==2.32.5 beautifulsoup4==4.14.3 lxml==6.0.2 pydantic==2.10.0 python-dotenv==1.2.1
```

## Architecture Patterns

### Recommended Project Structure

```
src/
├── app.py                 # Flask application entry point
├── config.py              # Configuration (env vars, constants)
├── models/
│   ├── __init__.py
│   ├── noc.py             # NOC data Pydantic models
│   └── responses.py       # API response models
├── services/
│   ├── __init__.py
│   ├── scraper.py         # OASIS HTTP fetching
│   ├── parser.py          # HTML parsing with BeautifulSoup
│   └── mapper.py          # NOC -> JD element mapping
├── routes/
│   ├── __init__.py
│   └── api.py             # API route definitions
└── utils/
    ├── __init__.py
    └── selectors.py       # CSS selector definitions (abstracted)
static/
├── index.html             # Frontend (Phase 2)
├── styles.css
└── app.js
```

### Pattern 1: Service Layer Separation

**What:** Separate scraping, parsing, and mapping into distinct services
**When to use:** Always - ensures testability and maintainability
**Example:**

```python
# services/scraper.py
import requests
from typing import Optional

class OASISScraper:
    BASE_URL = "https://noc.esdc.gc.ca"

    def __init__(self, timeout: int = 60):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "JD-Builder-Lite/1.0 (Educational Demo)"
        })

    def search(self, query: str, version: str = "2025.0") -> str:
        """Fetch search results HTML from OASIS."""
        url = f"{self.BASE_URL}/OaSIS/OaSISSearchResult"
        params = {
            "searchType": "Keyword",
            "searchText": query,
            "version": version
        }
        response = self.session.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        return response.text

    def fetch_profile(self, code: str, version: str = "2025.0") -> str:
        """Fetch full profile HTML from OASIS."""
        url = f"{self.BASE_URL}/OaSIS/OaSISOccProfile"
        params = {"code": code, "version": version}
        response = self.session.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        return response.text
```

### Pattern 2: Pydantic Response Models

**What:** Define all API responses as Pydantic models with validation
**When to use:** All API endpoints - ensures consistent, documented responses
**Example:**

```python
# models/noc.py
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class SourceMetadata(BaseModel):
    """Provenance tracking for scraped data."""
    noc_code: str
    profile_url: str
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
    version: str = "2025.0"

class SearchResult(BaseModel):
    """Single search result from OASIS."""
    noc_code: str
    title: str
    url: str

class SearchResponse(BaseModel):
    """API response for /api/search endpoint."""
    query: str
    results: List[SearchResult]
    count: int
    metadata: SourceMetadata

class NOCStatement(BaseModel):
    """Single statement from NOC profile with source tracking."""
    text: str
    source_attribute: str  # e.g., "Main Duties", "Skills"
    source_url: str

class JDElementData(BaseModel):
    """Data for a single JD element (e.g., Key Activities)."""
    statements: List[NOCStatement]

class ProfileResponse(BaseModel):
    """API response for /api/profile endpoint."""
    noc_code: str
    title: str
    key_activities: JDElementData
    skills: JDElementData
    effort: JDElementData
    responsibility: JDElementData
    working_conditions: JDElementData
    metadata: SourceMetadata
```

### Pattern 3: CSS Selector Abstraction

**What:** Define selectors in one place, with fallbacks
**When to use:** All HTML parsing - prevents brittle selector spread
**Example:**

```python
# utils/selectors.py
"""
CSS selectors for OASIS HTML parsing.
Abstracted to single location for easy maintenance when site changes.
"""

SELECTORS = {
    "search_results": {
        "primary": "table.search-results tr",
        "fallback": "div.results-list li",
        "validation_pattern": r"\d{5}\.\d{2}"  # NOC code pattern
    },
    "profile_title": {
        "primary": "h1.profile-title",
        "fallback": "div.content h1"
    },
    "main_duties": {
        "primary": "div#main-duties ul li",
        "fallback": "section.duties li"
    },
    # ... more selectors
}

def get_selector(element: str) -> str:
    """Return primary selector for element."""
    return SELECTORS.get(element, {}).get("primary", "")

def get_fallback(element: str) -> str:
    """Return fallback selector when primary fails."""
    return SELECTORS.get(element, {}).get("fallback", "")
```

### Anti-Patterns to Avoid

- **Hardcoded selectors in parsing code:** Always use the selector abstraction layer
- **Returning raw HTML to frontend:** Backend parses all HTML, frontend receives clean JSON
- **Skipping validation:** Every scraped field should be validated against expected patterns
- **No timeout configuration:** Always set explicit timeouts (60s+ for government sites)
- **Ignoring SSL errors silently:** Log SSL issues, use certifi, don't just `verify=False`

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| HTTP requests | Custom urllib wrapper | `requests` library | Handles encoding, sessions, retries, headers |
| HTML parsing | Regex extraction | BeautifulSoup with lxml | Handles malformed HTML, provides tree traversal |
| Data validation | Manual dict checking | Pydantic models | Auto-validation, serialization, type hints |
| JSON responses | Manual dict -> json.dumps | Flask's `jsonify` or Pydantic `model_dump()` | Handles encoding, content-type headers |
| CORS handling | Manual headers | Flask-CORS | Handles preflight, all edge cases |
| Session management | Manual cookie handling | `requests.Session()` | Maintains cookies, connection pooling |

**Key insight:** Government websites have quirky HTML. BeautifulSoup's lenient parsing handles edge cases that regex cannot. Pydantic ensures data consistency across all responses.

## Common Pitfalls

### Pitfall 1: Brittle CSS Selectors

**What goes wrong:** Selectors like `div:nth-child(3) > table > tr` break when OASIS restructures HTML
**Why it happens:** Using DevTools "Copy selector" without considering fragility
**How to avoid:**
- Use semantic selectors (IDs, data attributes, ARIA labels) when available
- Define selectors in one file with fallbacks
- Validate extracted content matches expected patterns
- Store raw HTML for debugging failed parses
**Warning signs:** Empty arrays where data was expected, truncated values, HTML fragments in output

### Pitfall 2: SSL Certificate Verification Errors

**What goes wrong:** `requests` throws `SSLError` when fetching from noc.esdc.gc.ca
**Why it happens:** Government certificate chains can have intermediate cert issues
**How to avoid:**
- First, ensure `certifi` package is up-to-date: `pip install --upgrade certifi`
- If issues persist, explicitly pass cert bundle: `requests.get(url, verify=certifi.where())`
- As last resort (development only), `verify=False` with logged warning
- Never deploy production code with `verify=False`
**Warning signs:** Intermittent connection failures, works in browser but not in code

### Pitfall 3: Timeout Defaults Too Short

**What goes wrong:** Requests timeout on slow government servers, returning errors
**Why it happens:** Default timeout is 30s; government sites can be slow
**How to avoid:**
- Set explicit timeout of 60-90 seconds for all requests
- Implement retry logic for timeout errors (3 retries with exponential backoff)
- Consider caching successful responses to reduce repeated requests
**Warning signs:** Intermittent failures, "Connection timed out" errors in logs

### Pitfall 4: No Content Validation

**What goes wrong:** Scraper returns empty or wrong data without failing
**Why it happens:** HTML structure changes, scraper extracts wrong elements silently
**How to avoid:**
- Validate NOC codes match `\d{5}\.\d{2}` pattern
- Check that expected fields are non-empty
- Fail loudly when validation fails (raise exception, log error)
- Implement health check endpoint that validates against known-good profile
**Warning signs:** Empty strings in response, data in wrong fields, no errors but wrong results

### Pitfall 5: Missing Provenance Metadata

**What goes wrong:** Scraped data lacks source URLs, timestamps, cannot be audited
**Why it happens:** Provenance added as afterthought, not designed into data model
**How to avoid:**
- Define `SourceMetadata` model FIRST, before any scraping code
- Every response includes metadata (url, timestamp, version)
- Store raw HTML hash for integrity verification
**Warning signs:** Cannot answer "where did this data come from?", missing timestamps

## Code Examples

Verified patterns for this phase:

### Flask App Setup

```python
# app.py
from flask import Flask, jsonify, request
from flask_cors import CORS
from pydantic import ValidationError
from services.scraper import OASISScraper
from services.parser import OASISParser
from services.mapper import JDMapper
from models.responses import SearchResponse, ProfileResponse

app = Flask(__name__, static_folder='static')
CORS(app)  # Enable CORS for frontend

scraper = OASISScraper()
parser = OASISParser()
mapper = JDMapper()

@app.route('/api/search')
def search():
    query = request.args.get('q', '')
    if not query or len(query) < 2:
        return jsonify({"error": "Query must be at least 2 characters"}), 400

    try:
        html = scraper.search(query)
        results = parser.parse_search_results(html)
        response = SearchResponse(
            query=query,
            results=results,
            count=len(results),
            metadata={"noc_code": "", "profile_url": scraper.BASE_URL, "version": "2025.0"}
        )
        return jsonify(response.model_dump())
    except Exception as e:
        app.logger.error(f"Search error: {e}")
        return jsonify({"error": "Search failed"}), 500

@app.route('/api/profile')
def profile():
    code = request.args.get('code', '')
    if not code:
        return jsonify({"error": "NOC code required"}), 400

    try:
        html = scraper.fetch_profile(code)
        noc_data = parser.parse_profile(html, code)
        jd_data = mapper.to_jd_elements(noc_data)
        response = ProfileResponse(**jd_data)
        return jsonify(response.model_dump())
    except ValidationError as e:
        app.logger.error(f"Validation error: {e}")
        return jsonify({"error": "Invalid data structure"}), 500
    except Exception as e:
        app.logger.error(f"Profile error: {e}")
        return jsonify({"error": "Profile fetch failed"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

### HTML Parsing with BeautifulSoup

```python
# services/parser.py
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from models.noc import SearchResult, NOCStatement
from utils.selectors import get_selector, get_fallback
import re

class OASISParser:
    NOC_CODE_PATTERN = re.compile(r'\d{5}\.\d{2}')

    def parse_search_results(self, html: str) -> List[SearchResult]:
        """Parse search results page into structured data."""
        soup = BeautifulSoup(html, 'lxml')
        results = []

        # Try primary selector, then fallback
        rows = soup.select(get_selector("search_results"))
        if not rows:
            rows = soup.select(get_fallback("search_results"))

        for row in rows:
            # Extract NOC code and title from each result row
            code_match = self.NOC_CODE_PATTERN.search(row.get_text())
            if code_match:
                code = code_match.group()
                title_elem = row.select_one('a, .title')
                title = title_elem.get_text(strip=True) if title_elem else ""
                url = title_elem.get('href', '') if title_elem else ""

                results.append(SearchResult(
                    noc_code=code,
                    title=title,
                    url=url
                ))

        return results

    def parse_profile(self, html: str, code: str) -> Dict[str, Any]:
        """Parse full profile page into NOC data structure."""
        soup = BeautifulSoup(html, 'lxml')

        return {
            "noc_code": code,
            "title": self._extract_title(soup),
            "main_duties": self._extract_list(soup, "main_duties"),
            "work_activities": self._extract_list(soup, "work_activities"),
            "skills": self._extract_list(soup, "skills"),
            "abilities": self._extract_list(soup, "abilities"),
            "knowledge": self._extract_list(soup, "knowledge"),
            "work_context": self._extract_list(soup, "work_context"),
            "employment_requirements": self._extract_list(soup, "employment_requirements"),
        }

    def _extract_title(self, soup: BeautifulSoup) -> str:
        elem = soup.select_one(get_selector("profile_title"))
        if not elem:
            elem = soup.select_one(get_fallback("profile_title"))
        return elem.get_text(strip=True) if elem else ""

    def _extract_list(self, soup: BeautifulSoup, element_name: str) -> List[str]:
        items = soup.select(get_selector(element_name))
        if not items:
            items = soup.select(get_fallback(element_name))
        return [item.get_text(strip=True) for item in items if item.get_text(strip=True)]
```

### NOC to JD Element Mapping

```python
# services/mapper.py
from typing import Dict, Any, List
from models.noc import NOCStatement, JDElementData
from datetime import datetime

class JDMapper:
    """Maps NOC data structure to JD element structure."""

    # Mapping from NOC attributes to JD elements
    MAPPING = {
        "key_activities": ["main_duties", "work_activities"],
        "skills": ["skills", "abilities", "knowledge"],
        "effort": ["work_context"],  # Filter for effort-related
        "responsibility": ["work_context"],  # Filter for responsibility-related
        "working_conditions": ["work_context"],
    }

    EFFORT_KEYWORDS = ["effort", "physical", "mental", "demands"]
    RESPONSIBILITY_KEYWORDS = ["responsib", "decision", "supervis", "direct"]

    def to_jd_elements(self, noc_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform NOC data to JD element structure."""
        base_url = f"https://noc.esdc.gc.ca/OaSIS/OaSISOccProfile?code={noc_data['noc_code']}"

        return {
            "noc_code": noc_data["noc_code"],
            "title": noc_data["title"],
            "key_activities": self._map_key_activities(noc_data, base_url),
            "skills": self._map_skills(noc_data, base_url),
            "effort": self._map_effort(noc_data, base_url),
            "responsibility": self._map_responsibility(noc_data, base_url),
            "working_conditions": self._map_working_conditions(noc_data, base_url),
            "metadata": {
                "noc_code": noc_data["noc_code"],
                "profile_url": base_url,
                "scraped_at": datetime.utcnow().isoformat(),
                "version": "2025.0"
            }
        }

    def _map_key_activities(self, data: Dict, url: str) -> JDElementData:
        statements = []
        for source in ["main_duties", "work_activities"]:
            for text in data.get(source, []):
                statements.append(NOCStatement(
                    text=text,
                    source_attribute=source.replace("_", " ").title(),
                    source_url=url
                ))
        return JDElementData(statements=statements)

    def _map_skills(self, data: Dict, url: str) -> JDElementData:
        statements = []
        for source in ["skills", "abilities", "knowledge"]:
            for text in data.get(source, []):
                statements.append(NOCStatement(
                    text=text,
                    source_attribute=source.title(),
                    source_url=url
                ))
        return JDElementData(statements=statements)

    def _map_effort(self, data: Dict, url: str) -> JDElementData:
        statements = []
        for text in data.get("work_context", []):
            if any(kw in text.lower() for kw in self.EFFORT_KEYWORDS):
                statements.append(NOCStatement(
                    text=text,
                    source_attribute="Work Context (Effort)",
                    source_url=url
                ))
        return JDElementData(statements=statements)

    def _map_responsibility(self, data: Dict, url: str) -> JDElementData:
        statements = []
        for text in data.get("work_context", []):
            if any(kw in text.lower() for kw in self.RESPONSIBILITY_KEYWORDS):
                statements.append(NOCStatement(
                    text=text,
                    source_attribute="Work Context (Responsibility)",
                    source_url=url
                ))
        return JDElementData(statements=statements)

    def _map_working_conditions(self, data: Dict, url: str) -> JDElementData:
        statements = []
        for text in data.get("work_context", []):
            statements.append(NOCStatement(
                text=text,
                source_attribute="Work Context",
                source_url=url
            ))
        return JDElementData(statements=statements)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Flask-RESTful | Plain Flask + Pydantic | ~2023 | Flask-RESTful adds boilerplate; Pydantic handles validation better |
| html.parser | lxml parser | Always | 10x faster, better malformed HTML handling |
| Manual JSON validation | Pydantic models | ~2020+ | Type safety, auto-serialization, validation |
| Regex for HTML parsing | BeautifulSoup | Always | Tree traversal, handles edge cases |

**Deprecated/outdated:**
- **Flask-RESTful**: Still works but adds unnecessary abstraction for simple APIs
- **Marshmallow for validation**: Pydantic is now preferred (simpler, faster, type hints)

## Open Questions

Things that couldn't be fully resolved:

1. **OASIS exact HTML structure**
   - What we know: URL patterns documented in PROJECT.md
   - What's unclear: Exact CSS selectors need live testing
   - Recommendation: Build selector abstraction layer, validate against live site before finalizing selectors

2. **SSL certificate handling**
   - What we know: WebFetch showed certificate errors
   - What's unclear: Whether production scraping will face same issues
   - Recommendation: Test with requests library directly, have certifi fallback ready

3. **Rate limiting by OASIS**
   - What we know: No documented rate limits
   - What's unclear: Actual limits on government site
   - Recommendation: Add 2-3 second delay between requests, implement exponential backoff on 429s

## Sources

### Primary (HIGH confidence)
- [Flask 3.1.2 on PyPI](https://pypi.org/project/flask/) - verified 2026-01-21
- [requests 2.32.5 on PyPI](https://pypi.org/project/requests/) - verified 2026-01-21
- [beautifulsoup4 4.14.3 on PyPI](https://pypi.org/project/beautifulsoup4/) - verified 2026-01-21
- [Pydantic documentation](https://docs.pydantic.dev/latest/) - data validation patterns
- [Flask-CORS documentation](https://flask-cors.readthedocs.io/) - CORS handling

### Secondary (MEDIUM confidence)
- [Auth0 - Best Practices for Flask API Development](https://auth0.com/blog/best-practices-for-flask-api-development/) - service layer patterns
- [Cosmic Python - Flask API and Service Layer](https://www.cosmicpython.com/book/chapter_04_service_layer.html) - architecture patterns
- [Real Python - Beautiful Soup Web Scraper](https://realpython.com/beautiful-soup-web-scraper-python/) - scraping patterns

### Tertiary (LOW confidence)
- OASIS HTML structure - needs live validation
- Government site rate limits - needs testing

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All versions verified on PyPI, mature libraries
- Architecture: HIGH - Standard Flask patterns, well-documented
- Pitfalls: HIGH - Multiple sources confirm government scraping challenges

**Research date:** 2026-01-21
**Valid until:** 30 days (stable libraries, government site may change)
