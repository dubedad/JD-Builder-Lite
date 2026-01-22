# Technology Stack

**Project:** JD Builder Lite
**Researched:** 2026-01-21
**Overall Confidence:** HIGH

## Executive Summary

For a single-user, local-only demo app that scrapes NOC data, presents a form UI, calls OpenAI, and outputs PDFs, the recommended stack is:

- **Backend:** Python 3.12 + Flask (lightweight, battle-tested)
- **Scraping:** BeautifulSoup4 + requests (standard, reliable)
- **PDF Generation:** fpdf2 (pure Python, Windows-friendly)
- **Frontend:** Vanilla HTML/CSS/JS (per requirements)
- **AI Integration:** OpenAI Python SDK 2.x

This stack prioritizes simplicity, Windows compatibility, and minimal dependencies - appropriate for a demo-quality local tool.

---

## Recommended Stack

### Backend Framework

| Technology | Version | Purpose | Confidence |
|------------|---------|---------|------------|
| Python | 3.12+ | Runtime | HIGH |
| Flask | 3.1.2 | Web server, API routes | HIGH |
| Flask-CORS | 6.0.2 | CORS handling for local dev | HIGH |

**Why Flask over FastAPI:**
- **Simpler for demo scope:** FastAPI's async features and auto-docs are overkill for a single-user local app
- **Lower learning curve:** Flask's request/response model is more intuitive for simple form processing
- **Mature ecosystem:** More examples available for common patterns
- **No performance need:** FastAPI's 15-20k req/sec advantage is irrelevant for single-user local use

**Why not Django:** Too heavy for a simple form + API app. Django's ORM, admin, auth are unnecessary overhead.

**Source:** [Flask 3.1.2 on PyPI](https://pypi.org/project/flask/) (verified 2026-01-21)

### Web Scraping

| Technology | Version | Purpose | Confidence |
|------------|---------|---------|------------|
| requests | 2.32.5 | HTTP client | HIGH |
| beautifulsoup4 | 4.14.3 | HTML parsing | HIGH |
| lxml | 6.0.2 | Fast HTML/XML parser | HIGH |

**Why BeautifulSoup + requests:**
- **Standard pairing:** The de-facto Python scraping stack for static HTML
- **No JavaScript rendering needed:** NOC pages serve static HTML
- **Forgiving parser:** Handles messy government HTML gracefully
- **Extensive documentation:** Well-documented error handling patterns

**Why lxml as parser:**
- **Performance:** Faster than html.parser for larger pages
- **Better handling:** More robust with malformed HTML
- **XPath support:** Useful for complex selectors if needed

**Why not Selenium/Playwright:** Overkill - NOC site serves static HTML, no JS rendering required.

**Why not Scrapy:** Designed for large-scale crawling; too heavy for targeted page fetching.

**Sources:**
- [requests 2.32.5 on PyPI](https://pypi.org/project/requests/) (verified 2026-01-21)
- [beautifulsoup4 4.14.3 on PyPI](https://pypi.org/project/beautifulsoup4/) (verified 2026-01-21)
- [lxml 6.0.2 on PyPI](https://pypi.org/project/lxml/) (verified 2026-01-21)

### PDF Generation

| Technology | Version | Purpose | Confidence |
|------------|---------|---------|------------|
| fpdf2 | 2.8.5 | PDF creation | HIGH |

**Why fpdf2 over WeasyPrint:**
- **Pure Python:** No GTK/Pango system dependencies
- **Windows-friendly:** Installs cleanly with `pip install fpdf2`
- **Sufficient for job descriptions:** Tables, headers, Unicode text, basic formatting
- **Actively maintained:** Regular releases, 1300+ unit tests

**Why not WeasyPrint:**
- Requires MSYS2 + GTK dependencies on Windows
- Known DLL issues (`gobject-2.0-0.dll` errors)
- Overkill for simple document layout - designed for full CSS-to-PDF conversion

**Why not ReportLab:**
- Steeper learning curve (canvas-based API)
- More complex for simple text documents
- fpdf2 is simpler for table-based layouts like job descriptions

**Limitation acknowledged:** fpdf2's HTML-to-PDF support is basic. If complex HTML rendering is needed later, reconsider WeasyPrint with Docker deployment (avoiding Windows GTK issues).

**Source:** [fpdf2 2.8.5 on PyPI](https://pypi.org/project/fpdf2/) (verified 2026-01-21)

### AI Integration

| Technology | Version | Purpose | Confidence |
|------------|---------|---------|------------|
| openai | 2.15.0 | OpenAI API client | HIGH |

**Why OpenAI official SDK:**
- **Official support:** Maintained by OpenAI
- **Type hints:** Full typing for IDE support
- **Async support:** Available if needed (not required for demo)
- **Automatic retries:** Built-in retry logic for rate limits

**Source:** [openai 2.15.0 on PyPI](https://pypi.org/project/openai/) (verified 2026-01-21)

### Frontend

| Technology | Version | Purpose | Confidence |
|------------|---------|---------|------------|
| HTML5 | - | Structure | HIGH |
| CSS3 | - | Styling | HIGH |
| Vanilla JavaScript | ES2022+ | Interactivity | HIGH |

**Why vanilla JS (per requirements):**
- **Simplicity:** No build step, no npm, no framework learning curve
- **Browser-native:** Modern browsers support ES modules, fetch, FormData natively
- **Demo-appropriate:** Framework overhead unjustified for simple forms
- **Direct DOM manipulation:** Adequate for form handling and results display

**Key browser APIs to use:**
- `fetch()` for API calls
- `FormData` for form handling
- `classList` for UI state
- `template` elements for dynamic content (optional)

**Source:** [Strapi - Vanilla JavaScript Form Handling Guide](https://strapi.io/blog/vanilla-javascript-form-handling-guide)

### Configuration & Environment

| Technology | Version | Purpose | Confidence |
|------------|---------|---------|------------|
| python-dotenv | 1.2.1 | Environment variables | HIGH |

**Why python-dotenv:**
- **API key management:** Keep OpenAI key out of code
- **Simple:** Single `.env` file, no complex config
- **Standard pattern:** Well-known in Python ecosystem

**Source:** [python-dotenv 1.2.1 on PyPI](https://pypi.org/project/python-dotenv/) (verified 2026-01-21)

---

## Data Source Strategy

### Primary: Web Scraping NOC Site

**Target:** `https://noc.esdc.gc.ca/`

**Approach:**
1. Scrape specific NOC profile pages (e.g., `/Structure/NOCProfile?code=21234`)
2. Parse HTML for duties, requirements, examples
3. Cache results locally to minimize requests

**Considerations:**
- Certificate issues observed (SSL verification may need handling)
- Respect rate limiting (1 request per 10-15 seconds is conservative)
- Check robots.txt (unable to fetch directly due to cert issues)
- Add appropriate User-Agent header

### Alternative: Open Government CSV Data

**Available at:** [Open Government Portal - NOC 2021](https://open.canada.ca/data/en/dataset/1feee3b5-8068-4dbb-b361-180875837593)

**Formats:**
- CSV files with classification structure
- PDF/HTML documentation
- JSON metadata (not full dataset)

**Recommendation:** Consider downloading CSV as fallback/supplement. The Open Government data provides the classification structure, but the detailed job descriptions require scraping the profile pages.

**Note:** The GC API Store closed September 2023. Direct API access requires contacting ESDC to request account creation.

---

## Alternatives Considered (Not Recommended)

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| Backend | Flask | FastAPI | Async/OpenAPI overkill for local demo |
| Backend | Flask | Django | ORM/admin unnecessary overhead |
| Scraping | BS4+requests | Scrapy | Too heavy for targeted page fetching |
| Scraping | BS4+requests | Selenium | No JS rendering needed |
| PDF | fpdf2 | WeasyPrint | Windows GTK dependency hell |
| PDF | fpdf2 | ReportLab | Steeper learning curve |
| Frontend | Vanilla JS | React/Vue | Build tooling overkill for forms |

---

## Installation

### Requirements File (`requirements.txt`)

```txt
# Web Framework
flask==3.1.2
flask-cors==6.0.2

# Web Scraping
requests==2.32.5
beautifulsoup4==4.14.3
lxml==6.0.2

# PDF Generation
fpdf2==2.8.5

# AI Integration
openai==2.15.0

# Configuration
python-dotenv==1.2.1
```

### Setup Commands

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables (`.env`)

```env
OPENAI_API_KEY=sk-your-key-here
```

---

## Project Structure (Recommended)

```
JD Builder Lite/
|-- app.py                 # Flask application
|-- requirements.txt       # Python dependencies
|-- .env                   # API keys (gitignored)
|-- .env.example           # Template for .env
|-- static/
|   |-- index.html         # Main UI
|   |-- styles.css         # Styling
|   |-- app.js             # Frontend logic
|-- services/
|   |-- scraper.py         # NOC scraping logic
|   |-- pdf_generator.py   # PDF creation
|   |-- ai_service.py      # OpenAI integration
|-- data/
|   |-- cache/             # Cached NOC data
|-- .planning/             # Planning docs
```

---

## Confidence Assessment

| Component | Confidence | Rationale |
|-----------|------------|-----------|
| Flask | HIGH | Verified version, mature, well-documented |
| BeautifulSoup4 + requests | HIGH | De-facto standard, verified versions |
| fpdf2 | HIGH | Verified version, pure Python, Windows-tested |
| OpenAI SDK | HIGH | Official library, verified version |
| Vanilla JS | HIGH | Browser-native, no verification needed |
| lxml | MEDIUM | Verified version, but C extension may have Windows edge cases |

---

## Risk Factors

### Low Risk
- **Stack maturity:** All components are production-stable
- **Documentation:** Extensive docs for all libraries
- **Windows compatibility:** Stack tested on Windows

### Medium Risk
- **NOC site changes:** Government sites occasionally restructure; scraper may need updates
- **SSL certificate issues:** Observed cert verification issues with noc.esdc.gc.ca
- **lxml compilation:** C extension; pre-built wheels usually available but edge cases exist

### Mitigation
- Cache scraped data aggressively
- Implement fallback to Open Government CSV data
- Pin exact versions in requirements.txt
- Test on clean Windows install before delivery

---

## What NOT to Use

| Technology | Why Not |
|------------|---------|
| **Selenium/Playwright** | NOC site is static HTML; browser automation unnecessary |
| **Scrapy** | Industrial crawler; overkill for targeted scraping |
| **Django** | Full web framework; ORM/admin not needed |
| **FastAPI** | Async/OpenAPI unnecessary for local single-user app |
| **WeasyPrint** | GTK dependencies painful on Windows |
| **React/Vue/Angular** | Build tooling overkill for simple forms |
| **SQLite/Postgres** | No database needed; JSON/file cache sufficient |
| **Docker** | Local demo; adds deployment complexity |
| **TypeScript** | Build step; vanilla JS sufficient for demo |

---

## Sources

### Verified Package Versions (PyPI, 2026-01-21)
- [Flask 3.1.2](https://pypi.org/project/flask/)
- [Flask-CORS 6.0.2](https://pypi.org/project/flask-cors/)
- [requests 2.32.5](https://pypi.org/project/requests/)
- [beautifulsoup4 4.14.3](https://pypi.org/project/beautifulsoup4/)
- [lxml 6.0.2](https://pypi.org/project/lxml/)
- [fpdf2 2.8.5](https://pypi.org/project/fpdf2/)
- [openai 2.15.0](https://pypi.org/project/openai/)
- [python-dotenv 1.2.1](https://pypi.org/project/python-dotenv/)

### Framework Comparisons
- [JetBrains - Django vs Flask vs FastAPI](https://blog.jetbrains.com/pycharm/2025/02/django-flask-fastapi/)
- [Strapi - FastAPI vs Flask 2025](https://strapi.io/blog/fastapi-vs-flask-python-framework-comparison)

### PDF Libraries
- [Templated.io - 8 PDF Tools Compared 2025](https://templated.io/blog/generate-pdfs-in-python-with-libraries/)
- [DEV Community - WeasyPrint vs ReportLab](https://dev.to/claudeprime/generate-pdfs-in-python-weasyprint-vs-reportlab-ifi)

### Web Scraping
- [Real Python - Beautiful Soup Web Scraper](https://realpython.com/beautiful-soup-web-scraper-python/)
- [GeeksforGeeks - Web Scraping with BeautifulSoup](https://www.geeksforgeeks.org/python/implementing-web-scraping-python-beautiful-soup/)

### NOC Data
- [NOC Portal](https://noc.esdc.gc.ca/)
- [Open Government - NOC 2021 Dataset](https://open.canada.ca/data/en/dataset/1feee3b5-8068-4dbb-b361-180875837593)
- [Open Government - Skills and Competencies Taxonomy 2025](https://open.canada.ca/data/en/dataset/618d2756-8c37-4f99-b184-8b3c1ef1b0f5)

### Frontend
- [Strapi - Vanilla JavaScript Form Handling Guide](https://strapi.io/blog/vanilla-javascript-form-handling-guide)
- [HTML All The Things - Vanilla JS in 2025](https://www.htmlallthethings.com/podcast/stop-using-frameworks-for-everything-vanilla-javascript-in-2025)

---

# v1.1 Stack Additions

**Milestone:** v1.1 Enhanced Data Display + Export Options
**Researched:** 2026-01-22
**Confidence:** HIGH

## Executive Summary for v1.1

v1.1 requires **NO new dependencies**. The existing stack already contains all necessary libraries: Python's built-in `csv` module handles CSV parsing for guide.csv and OASIS CSV files, `python-docx` 1.2.0 (already in requirements.txt) handles Word export, and vanilla JavaScript with CSS handles frontend grid view and star rating display. The focus should be on usage patterns and integration, not dependency additions.

## Recommended Additions for v1.1

### NONE REQUIRED

All v1.1 features can be implemented with the existing stack:

**CSV Parsing:** Python built-in `csv` module (no installation needed)
- Why: Standard library, memory-efficient, perfect for line-by-line processing of guide.csv and OASIS CSVs
- Integration: Add `csv_service.py` in `src/services/` using `csv.DictReader` pattern
- Usage pattern:
  ```python
  import csv

  with open('guide.csv', newline='', encoding='utf-8') as csvfile:
      reader = csv.DictReader(csvfile)
      for row in reader:
          # Process row as dict with column headers as keys
  ```

**DOCX Export:** python-docx 1.2.0 (already installed)
- Why: Already in requirements.txt, proven library for Word document generation
- Integration: Existing `src/services/docx_generator.py` already implements full export pipeline
- Extend for v1.1: Add Annex section generation in `generate_docx()` function

**Grid View Toggle:** Vanilla JavaScript + CSS (no framework)
- Why: Matches existing frontend architecture, zero dependencies
- Integration: Add toggle button in search.js, CSS Grid for table layout in main.css
- Pattern: Use CSS classes to switch between `.card-view` and `.grid-view` display modes

**Star Rating Display:** CSS + HTML entity stars
- Why: Pure CSS solution, accessible, no icon libraries needed
- Integration: Add `.star-rating` component in main.css using Unicode star characters (★/☆)
- Pattern:
  ```html
  <span class="star-rating" data-level="3" aria-label="3 out of 5">
      ★★★☆☆
  </span>
  ```

## Not Recommended for v1.1

**pandas** (popular CSV library)
- Why NOT: Overkill for simple CSV reading, adds 50+ MB dependency for functionality that built-in csv module provides
- Alternative: Use Python's built-in `csv` module with `DictReader` for header-mapped row access

**openpyxl** (Excel library)
- Why NOT: v1.1 requires DOCX (Word), not XLSX (Excel)
- Alternative: Continue using python-docx for all document export needs

**Frontend UI frameworks** (React, Vue, Alpine.js)
- Why NOT: Would require build step, contradicts existing vanilla JS architecture
- Alternative: CSS Grid + vanilla JavaScript for grid view toggle

**Icon libraries** (Font Awesome, Material Icons)
- Why NOT: Unnecessary dependency for simple star ratings
- Alternative: Unicode stars (★ U+2605, ☆ U+2606) or CSS shapes

**CSV parsing libraries** (clevercsv, csvkit)
- Why NOT: Built-in csv module is sufficient for well-formed OASIS CSVs
- Alternative: Python's csv.DictReader with proper encoding handling

## Integration Guidance for v1.1

### CSV Service Layer

Create new service at `src/services/csv_service.py`:

```python
"""CSV data service for OASIS metadata files."""

import csv
from pathlib import Path
from typing import Dict, List, Optional

class CSVService:
    """Service for reading OASIS CSV metadata files."""

    def __init__(self, csv_dir: Path):
        self.csv_dir = csv_dir
        self._guide_cache: Optional[Dict] = None

    def load_guide(self) -> Dict[str, Dict]:
        """Load guide.csv with category definitions and scale meanings.

        Returns dict mapping OASIS labels to metadata:
        {
            "Abilities": {
                "category": "Abilities",
                "definition": "...",
                "scale": "Proficiency"
            }
        }
        """
        if self._guide_cache:
            return self._guide_cache

        guide_path = self.csv_dir / "guide.csv"
        guide_data = {}

        with open(guide_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                label = row.get('OASIS_Label', '')
                guide_data[label] = {
                    'category': row.get('Category', ''),
                    'definition': row.get('Definition', ''),
                    'scale': row.get('Scale', '')
                }

        self._guide_cache = guide_data
        return guide_data
```

**Integration point:** Instantiate in `app.py`, inject into routes that need statement metadata.

### DOCX Annex Section

Extend existing `src/services/docx_generator.py`:

```python
def generate_docx(data: ExportData) -> bytes:
    # ... existing code ...

    # NEW: Annex section (before compliance appendix)
    if data.annex_attributes:
        doc.add_page_break()
        doc.add_heading("Annex: Reference NOC Attributes", 1)

        for attr_group in data.annex_attributes:
            doc.add_heading(attr_group.name, 2)
            for item in attr_group.items:
                doc.add_paragraph(item, style='List Bullet')

    # Existing compliance appendix code...
```

**Integration point:** Add `annex_attributes` field to `ExportData` model in `src/models/export_models.py`.

### Frontend Grid View

Add to `static/js/search.js`:

```javascript
// Toggle between card and grid view
function toggleView(viewMode) {
    const resultsContainer = document.getElementById('search-results');
    resultsContainer.classList.remove('card-view', 'grid-view');
    resultsContainer.classList.add(viewMode);
    localStorage.setItem('searchViewMode', viewMode);
}
```

Add to `static/css/main.css`:

```css
/* Search results grid view */
.search-results.grid-view {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 1rem;
}

.search-results.card-view .result-card {
    /* Existing card styles */
}

.search-results.grid-view .result-card {
    display: grid;
    grid-template-columns: 80px 1fr 200px;
    align-items: center;
    padding: 0.75rem;
}
```

**Integration point:** Wire toggle button in search results template, persist preference in localStorage.

### Star Rating Component

Add to `static/css/main.css`:

```css
/* Star rating display */
.star-rating {
    color: #f5a623;
    font-size: 1rem;
    letter-spacing: 0.1em;
    white-space: nowrap;
}

.star-rating::after {
    content: attr(data-scale-meaning);
    margin-left: 0.5rem;
    color: var(--text-light);
    font-size: 0.875rem;
    font-weight: normal;
}
```

Add helper in `static/js/main.js`:

```javascript
function renderStarRating(level, scaleMeaning) {
    const filled = '★'.repeat(level);
    const empty = '☆'.repeat(5 - level);
    return `<span class="star-rating" data-level="${level}" data-scale-meaning="${scaleMeaning}" aria-label="${level} out of 5">${filled}${empty}</span>`;
}
```

**Integration point:** Use in statement rendering functions in selection.js.

## Version Verification for v1.1

| Library | Recommended | Verified Date | Source | Confidence |
|---------|-------------|---------------|--------|------------|
| Python csv module | Built-in (3.12+) | 2026-01-22 | [Python docs](https://docs.python.org/3/library/csv.html) | HIGH |
| python-docx | 1.2.0 | 2026-01-22 | [PyPI](https://pypi.org/project/python-docx/) | HIGH |
| Unicode stars | U+2605/U+2606 | 2026-01-22 | Unicode Standard | HIGH |
| CSS Grid | Stable (all modern browsers) | 2026-01-22 | MDN Web Docs | HIGH |

**Note on python-docx version:** Current requirements.txt shows `python-docx==1.2.0`, which matches the latest stable release from PyPI (released June 16, 2025). No upgrade needed.

## CSV Module Best Practices

Based on official Python documentation:

1. **Always use `newline=''`** when opening CSV files
   - Prevents newline interpretation issues on Windows
   - Critical for cross-platform compatibility

2. **Specify encoding explicitly**
   - Use `encoding='utf-8'` for OASIS CSVs (likely contain French text)
   - Prevents encoding errors on different systems

3. **Use DictReader for header-mapped access**
   - More readable than index-based access
   - Self-documenting code
   - Easier to maintain if CSV columns change

4. **Use context managers (`with` statements)**
   - Automatic file closure
   - Exception-safe

5. **Cache parsed data if accessed multiple times**
   - guide.csv likely accessed for every statement display
   - Parse once, cache in memory for request lifecycle

## python-docx Usage Patterns

Based on existing `docx_generator.py` and official documentation:

**Existing patterns to follow:**
- Document initialization: `doc = Document()`
- Section configuration for page setup
- Header/footer customization
- Heading hierarchy (0 = title, 1 = section, 2 = subsection)
- Style application: `doc.add_paragraph(text, style='List Bullet')`
- Table generation for structured data
- Font styling via runs
- BytesIO buffer for in-memory generation

**New patterns needed for v1.1:**
- Annex section: Same as JD Elements (heading + bullet list)
- No new python-docx features required

## Frontend Patterns for v1.1

Based on existing vanilla JS architecture:

**State management:** Existing Proxy-based state in `static/js/state.js`
- Add `searchViewMode: 'card'` to state
- Subscribe to changes for view toggle

**Event delegation:** Existing pattern in search.js
- Use for grid/card view toggle buttons
- Maintain single event listener on container

**CSS classes for state:** Existing pattern throughout
- `.card-view` / `.grid-view` classes for display mode
- `.selected` class for active toggle button

**localStorage persistence:** Existing pattern in state.js
- Persist view mode preference
- Restore on page load

## Risk Assessment for v1.1

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| CSV encoding issues (French text) | Medium | Low | Explicit UTF-8 encoding, test with actual OASIS CSVs |
| CSV column name changes | Low | Medium | Robust error handling, log missing columns |
| Grid view layout on mobile | Medium | Low | CSS media queries, fallback to card view |
| Star unicode rendering | Low | Low | Unicode widely supported, add aria-label for accessibility |
| guide.csv structure assumption | Medium | Medium | Validate CSV structure on load, fail gracefully |

## Sources for v1.1 Research

- [Python csv module documentation](https://docs.python.org/3/library/csv.html) - Official Python docs
- [python-docx PyPI page](https://pypi.org/project/python-docx/) - Version verification (June 16, 2025)
- [python-docx official documentation](https://python-docx.readthedocs.io/) - API patterns
- [Python CSV best practices - Real Python](https://realpython.com/python-csv/) - Usage patterns
- Existing codebase analysis - `src/services/docx_generator.py`, `static/js/search.js`

## Confidence Assessment for v1.1

**Overall: HIGH**

- CSV parsing: HIGH (built-in module, well-documented, proven patterns)
- DOCX export: HIGH (already implemented, just needs extension)
- Grid view: HIGH (CSS Grid stable, matches existing patterns)
- Star ratings: HIGH (simple CSS + Unicode solution)

**No external research flags.** All findings verified with official documentation or existing codebase analysis.
