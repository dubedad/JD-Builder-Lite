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
- Integration: Add `.star-rating` component in main.css using Unicode star characters
- Pattern:
  ```html
  <span class="star-rating" data-level="3" aria-label="3 out of 5">
      stars displayed here
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
- Alternative: Unicode stars (U+2605, U+2606) or CSS shapes

**CSV parsing libraries** (clevercsv, csvkit)
- Why NOT: Built-in csv module is sufficient for well-formed OASIS CSVs
- Alternative: Python's csv.DictReader with proper encoding handling

## Version Verification for v1.1

| Library | Recommended | Verified Date | Source | Confidence |
|---------|-------------|---------------|--------|------------|
| Python csv module | Built-in (3.12+) | 2026-01-22 | [Python docs](https://docs.python.org/3/library/csv.html) | HIGH |
| python-docx | 1.2.0 | 2026-01-22 | [PyPI](https://pypi.org/project/python-docx/) | HIGH |
| Unicode stars | U+2605/U+2606 | 2026-01-22 | Unicode Standard | HIGH |
| CSS Grid | Stable (all modern browsers) | 2026-01-22 | MDN Web Docs | HIGH |

**Note on python-docx version:** Current requirements.txt shows `python-docx==1.2.0`, which matches the latest stable release from PyPI (released June 16, 2025). No upgrade needed.

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

---

# v3.0 Stack Additions: Style-Enhanced JD Writing

**Milestone:** v3.0 Style-Enhanced Writing with Vocabulary Constraints
**Researched:** 2026-02-03
**Overall Confidence:** MEDIUM

## Executive Summary for v3.0

The style-enhanced JD writing feature requires three new capabilities:
1. **Text extraction** from ~40 example JD files (PDF/DOCX)
2. **Style learning** from extracted examples
3. **Vocabulary-constrained generation** using only NOC/JobForge terms

The existing OpenAI SDK (v1.109.1) handles style learning and generation through **prompt engineering with few-shot examples**. No heavy NLP libraries or constrained decoding frameworks are needed. The main additions are lightweight: `pdfplumber` for PDF extraction and `pyarrow` for parquet vocabulary access.

---

## Recommended Stack Additions for v3.0

### 1. PDF Text Extraction

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| **pdfplumber** | 0.11.9 | Extract text from example JD PDFs | MIT license (safe for internal tools), reliable text extraction, pure Python, built on pdfminer.six |

**Rationale:** The example JDs are text-heavy documents (not scanned images), making pdfplumber ideal. PyMuPDF is faster but carries AGPL licensing concerns for internal tools. pypdf is lighter but pdfplumber handles complex layouts better.

**Installation:**
```bash
pip install pdfplumber==0.11.9
```

**Confidence:** HIGH - Verified via [PyPI](https://pypi.org/project/pdfplumber/) (January 5, 2026 release)

### 2. DOCX Text Extraction

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| **python-docx** | 1.2.0 | Extract text from example JD DOCX files | Already installed, proven reliable |

**Rationale:** Already in `requirements.txt` for export. Reuse for extraction - no new dependency needed.

**Confidence:** HIGH - Already validated in current stack

### 3. Parquet File Access (Vocabulary)

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| **pyarrow** | 19.x or 23.0.0 | Read JobForge 2.0 parquet files containing NOC vocabulary | Industry standard for parquet, no pandas required |

**Rationale:** JobForge 2.0 vocabulary lives in parquet files (gold model at `C:\Users\Administrator\Dropbox\++ Results Kit\JobForge 2.0\data\gold\`). PyArrow reads these directly as Arrow Tables without pandas overhead. Use `pq.read_table()` for simple column extraction.

**Version Note:**
- PyArrow 23.0.0 requires Python >= 3.10
- If project uses Python 3.9, use PyArrow 15.x (last Python 3.9 compatible version)
- Check project's Python version before pinning

**Installation:**
```bash
pip install pyarrow>=19.0.0
```

**Confidence:** HIGH - Verified via [Arrow docs v23.0.0](https://arrow.apache.org/docs/python/parquet.html)

---

## Approach: Style Learning + Vocabulary-Constrained Generation

### Recommended Approach: Few-Shot Prompting (No New Libraries)

| Approach | Complexity | Quality | Libraries Needed |
|----------|-----------|---------|------------------|
| **Few-shot prompting** | Low | Good | None (use existing OpenAI SDK) |
| Fine-tuning | High | Better | OpenAI fine-tuning API |
| Constrained decoding | Very High | Variable | Outlines (local models only) |
| Logit bias | Medium | Poor for vocab | OpenAI SDK (already installed) |

**Recommendation: Few-shot prompting with vocabulary injection**

The existing OpenAI SDK (v1.109.1) supports this pattern:

```python
# Pseudo-code for style-enhanced generation
prompt = f"""
You are writing job description content. Your task is to generate one sentence
that expands on the following NOC statement.

CRITICAL CONSTRAINT: You may ONLY use words from this vocabulary list:
{vocabulary_words}

If you cannot express the idea using only these words, say "CANNOT_EXPRESS".

STYLE EXAMPLES (mimic this writing style):
{few_shot_examples}

NOC STATEMENT TO EXPAND:
{noc_statement}

STYLED SENTENCE (using only allowed vocabulary):
"""
```

**Why not constrained decoding (Outlines)?**
- Outlines works with local models (vLLM, Ollama, llama.cpp) but has **limited OpenAI API support**
- OpenAI structured outputs only guarantee JSON schema compliance, not vocabulary constraints
- Logit bias is limited to ~300-1024 tokens and works at token level, not word level
- For vocabulary-constrained generation with cloud APIs, **prompt engineering + post-validation is the practical approach**

**Confidence:** MEDIUM - Based on [Outlines docs](https://dottxt-ai.github.io/outlines/latest/) and [OpenAI community discussions](https://community.openai.com/t/logit-bias-default-bias-and-blocking-tokens-not-in-list/1057281)

### Post-Generation Validation (Required)

Since prompt-based vocabulary constraints are "best effort," implement validation:

```python
def validate_vocabulary(generated_text: str, allowed_words: set) -> tuple[bool, list]:
    """Check if all words in generated text are in allowed vocabulary."""
    words = set(generated_text.lower().split())
    violations = words - allowed_words
    return len(violations) == 0, list(violations)
```

If violations detected:
1. Retry with violated words explicitly excluded in prompt
2. Or fall back to original NOC statement only

---

## What NOT to Add for v3.0

### Do NOT Add: Heavy NLP Libraries

| Library | Why NOT |
|---------|---------|
| spaCy | Overkill for style extraction - adds 500MB+ models, complex dependency |
| NLTK | Older, slower, unnecessary when LLM handles style learning |
| FastStylometry | Academic tool for authorship attribution, not style transfer |
| Gensim | Topic modeling not needed for JD style mimicking |
| Hugging Face Transformers | Massive dependency for features OpenAI already provides |

**Rationale:** The goal is style *mimicking*, not style *analysis*. LLMs learn style from examples directly through few-shot prompting - no preprocessing or feature extraction needed. Research confirms that "providing even a few writing examples significantly improves an LLM's ability to imitate implicit personal writing style" ([arxiv](https://arxiv.org/html/2509.14543v1)). Adding NLP libraries creates dependency bloat without improving output quality.

### Do NOT Add: Local Model Infrastructure

| Library | Why NOT |
|---------|---------|
| Outlines | Requires local model serving (vLLM/Ollama) for full vocabulary constraints |
| llama.cpp | Adds model hosting complexity to a Flask demo app |
| vLLM | Server infrastructure overkill for ~40 example files |

**Rationale:** JD Builder Lite is a Flask demo that already uses OpenAI. Adding local model serving creates operational complexity disproportionate to the feature value.

### Do NOT Add: Separate Embedding/RAG Stack

| Library | Why NOT |
|---------|---------|
| ChromaDB | ~40 example files fit in prompt context - no vector DB needed |
| Pinecone | Cloud dependency for a local demo tool |
| FAISS | C++ dependency complexity for minimal benefit |
| LangChain | Abstraction overhead for simple few-shot prompting |

**Rationale:** With ~40 example JDs totaling perhaps 50-100KB of text, a simple file-based approach (read examples, select relevant ones, include in prompt) outperforms RAG complexity.

---

## Integration with Existing Stack

### Existing Stack (DO NOT MODIFY)

| Component | Version | Purpose | Integration Point |
|-----------|---------|---------|-------------------|
| Flask | 3.1.2 | Web framework | New endpoint for styled generation |
| OpenAI SDK | 1.109.1 | LLM API access | **Use for style-enhanced generation** |
| python-docx | 1.2.0 | DOCX export | **Reuse for DOCX extraction** |
| WeasyPrint | 68.0 | PDF export | No change |
| BeautifulSoup | 4.14.3 | Web scraping | No change |
| Pydantic | 2.10.0 | Validation | Use for styled output models |

### New Integration Points

```
Example JDs (PDF/DOCX)
    |
    v
[pdfplumber] + [python-docx]  <-- Text extraction
    |
    v
Style Examples (in-memory cache)
    |
    +----> [OpenAI SDK]  <-- Few-shot prompting
    |           |
    |           v
    |      Styled Sentence
    |           |
    v           v
[pyarrow] --> Vocabulary Validation
    |
    v
JobForge parquet files
```

---

## Updated requirements.txt for v3.0

```txt
# Existing (unchanged)
flask==3.1.2
flask-cors==6.0.2
requests==2.32.5
beautifulsoup4==4.14.3
lxml==6.0.2
pydantic==2.10.0
python-dotenv==1.2.1
openai==1.109.1
tenacity==9.0.0
weasyprint==68.0
Flask-WeasyPrint==1.1.0
python-docx==1.2.0

# NEW for v3.0 style-enhanced writing
pdfplumber==0.11.9    # PDF text extraction from example JDs
pyarrow>=19.0.0       # Parquet reading for NOC vocabulary
```

**Note:** Check Python version. If Python < 3.10, pin `pyarrow<20.0.0`.

---

## Architecture Recommendation for v3.0

### New Service Layer Files

```
src/
  services/
    style_service.py        # NEW: Style extraction and generation
    vocabulary_service.py   # NEW: NOC vocabulary loading from parquet
    example_loader.py       # NEW: PDF/DOCX extraction
```

### Data Flow

1. **Startup:** Load example JDs once, extract text, cache in memory
2. **Startup:** Load vocabulary from JobForge parquet files
3. **Request:** User selects NOC statements
4. **Generation:** For each statement:
   - Select relevant style examples (by job category similarity)
   - Build few-shot prompt with vocabulary constraint
   - Call OpenAI with existing SDK
   - Validate output against vocabulary
   - Retry or fallback if validation fails

---

## Confidence Assessment for v3.0

| Decision | Confidence | Reason |
|----------|------------|--------|
| pdfplumber for PDF extraction | HIGH | MIT license, verified current version, good for text-heavy docs |
| python-docx for DOCX extraction | HIGH | Already in stack, proven |
| pyarrow for parquet | HIGH | Industry standard, verified API |
| Few-shot prompting approach | MEDIUM | Best available for cloud API + vocab constraint combo |
| No NLP libraries | MEDIUM | Assumption that LLM handles style learning adequately |
| No local model infrastructure | HIGH | Clear scope mismatch with demo app complexity |

---

## Open Questions for v3.0 Phase Planning

1. **Python version:** Verify project Python version to pin correct pyarrow version
2. **Example quality:** Are all 40 example JDs suitable? Some may be scanned images requiring OCR
3. **Vocabulary granularity:** Should vocabulary be NOC-code-specific or global across all NOC?
4. **Retry budget:** How many retries on vocabulary violations before fallback?
5. **Style example selection:** Simple random selection or match by NOC category?

---

## Sources for v3.0 Research

### Verified (HIGH confidence)
- [pdfplumber PyPI v0.11.9](https://pypi.org/project/pdfplumber/) - January 5, 2026
- [pypdf PyPI v6.6.2](https://pypdf.readthedocs.io/en/stable/meta/comparisons.html) - January 26, 2026
- [Apache Arrow Parquet docs v23.0.0](https://arrow.apache.org/docs/python/parquet.html)
- [pandas 2.2.2 Installation docs](https://pandas.pydata.org/pandas-docs/version/2.2.2/getting_started/install.html) - Python 3.9-3.12 support

### Research (MEDIUM confidence)
- [Outlines GitHub](https://github.com/dottxt-ai/outlines) - Structured output library
- [OpenAI Logit Bias Help Center](https://help.openai.com/en/articles/5247780-using-logit-bias-to-alter-token-probability-with-the-openai-api)
- [Constrained LLM Generation Deep Dive](https://medium.com/@docherty/controlling-your-llm-deep-dive-into-constrained-generation-1e561c736a20)
- [Few-shot prompting for style mimicking](https://relevanceai.com/docs/example-use-cases/few-shot-prompting)
- [LLM Style Imitation Research](https://arxiv.org/html/2509.14543v1)
- [PDF Library Comparison 2026](https://unstract.com/blog/evaluating-python-pdf-to-text-libraries/)

---

# v5.0 Stack: JobForge Gold/Bronze/Silver Parquet as Primary NOC Data Source

**Milestone:** v5.0 JobForge 2.0 Integration
**Researched:** 2026-03-06
**Overall Confidence:** HIGH

## Executive Summary for v5.0

v5.0 replaces live OASIS HTML scraping with JobForge gold parquet as the primary data source for NOC search and profile retrieval. The stack change is minimal: **no new libraries are required**. The existing pandas 2.2.3 + pyarrow 23.0.0 combination already installed is the correct tool. The architecture change is a caching strategy: load all gold parquet files into memory at app startup (0.36s, 27 MB total), build lookup structures, then serve requests from memory with OASIS as fallback.

**Bottom line:** Do not add polars, DuckDB, SQLite caching, or any new library. The 25 gold parquet files total 1.1 MB on disk, expand to 27 MB in memory, load in 0.36s at startup, and serve per-request lookups in sub-millisecond time via pre-built Python dicts. The existing pandas/pyarrow stack handles this perfectly.

---

## Current Parquet Usage (What Already Works)

The app already reads 10 gold parquet files via `LabelsLoader` (lazy per-request loads):

| File | Currently Used For |
|------|--------------------|
| `element_labels.parquet` | NOC labels per oasis_profile_code |
| `element_example_titles.parquet` | Example job titles per oasis_profile_code |
| `element_exclusions.parquet` | Excluded occupations per oasis_profile_code |
| `element_employment_requirements.parquet` | Requirements text per oasis_profile_code |
| `element_workplaces_employers.parquet` | Workplace names per oasis_profile_code |
| `oasis_workcontext.parquet` | Work context ratings per oasis_code |
| `element_main_duties.parquet` | Main duties (sample data only - 8 rows) |
| `element_additional_information.parquet` | Additional info per profile |
| `element_lead_statement.parquet` | Lead statement per unit_group_id |
| `element_workplaces_employers.parquet` | Workplaces per oasis_profile_code |

Bronze parquet files (4 files) are read by `VocabularyIndex` for vocabulary term extraction.

## What v5.0 Adds

v5.0 needs two new capabilities from parquet:

1. **NOC Search** - Replace `GET /api/search` which currently calls OASIS HTML scraping
2. **NOC Profile Fetch** - Replace `GET /api/profile` which currently calls OASIS HTML scraping

Both require gold parquet data that is already present but not yet used for these purposes.

---

## Recommended Stack for v5.0 (NO NEW LIBRARIES)

### Core Technologies (unchanged)

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| pandas | 2.2.3 | Primary parquet read + DataFrame operations | Already installed, Python 3.14 compatible (verified), handles all gold files |
| pyarrow | 23.0.0 | Parquet file format engine (used by pandas) | Already installed, Python 3.14 compatible (verified) |
| Python dict | built-in | Per-request O(1) profile lookup | Zero cost; pre-built at startup from DataFrames |

**Why pandas stays primary (not polars):** Benchmarking on actual gold files shows in-memory filter performance is nearly identical between pandas and polars at this data size (27 MB). The decisive factor is that the entire existing codebase uses pandas DataFrames and `.iterrows()` patterns. Switching to polars would require rewriting all of `LabelsLoader`, `VocabularyIndex`, and the new parquet service with no measurable user-facing benefit. The real performance win comes from the caching strategy (Python dict at O(0.0001ms) vs pandas filter at O(0.3ms)), not from switching DataFrame libraries.

**Why pyarrow stays the parquet engine:** pandas uses pyarrow under the hood for `.read_parquet()`. Already installed at v23.0.0, Python 3.14 compatible. No change needed.

**Why NOT polars:** Polars 1.38.1 is installed and Python 3.14 compatible, but it would require rewriting all existing pandas code for no measurable gain on 27 MB of data. The rule for this codebase is: use the tool already present unless there's a concrete reason to change.

**Why NOT DuckDB:** DuckDB is excellent for analytical SQL queries over parquet files but adds a dependency for functionality that Python dicts provide better. The gold files are small and static; analytical query optimization is irrelevant.

**Why NOT SQLite copy:** Copying parquet to SQLite at startup adds 50-200ms with no benefit over in-memory DataFrames. SQLite is already used for classification data (occupational.db); mixing it with NOC reference data would create confusion about the data boundary.

---

## Caching Strategy: Load-at-Startup, Serve-from-Memory

### The Numbers (measured on actual gold files)

| Metric | Value |
|--------|-------|
| Gold parquet files | 25 files, 1.1 MB total on disk |
| All files loaded into memory | 27.3 MB |
| Full startup load time | 0.36s (all 25 files + index build) |
| pandas linear filter (per request) | 0.32ms |
| pandas indexed .loc (pre-indexed) | 0.076ms |
| Python dict lookup (pre-built) | 0.0001ms |

### Recommended Pattern: Load + Index at Startup

```python
# At app startup (in initialize_vocabulary() or a new initialize_noc_service()):
class NocDataService:
    """In-memory NOC data service backed by JobForge gold parquet."""

    def __init__(self, gold_path: str):
        self._gold_path = Path(gold_path)
        self._loaded = False

        # Search index: DataFrame for text search
        self._search_df = None          # dim_noc + lead + titles, 894 rows

        # Profile lookup: Python dicts for O(1) access
        self._skills_lookup = {}        # oasis_code -> dict
        self._abilities_lookup = {}     # oasis_code -> dict
        self._knowledges_lookup = {}    # oasis_code -> dict
        self._workactivities_lookup = {}
        self._workcontext_lookup = {}   # oasis_code -> dict

    def load(self):
        """Load all gold parquet files and build indexes. Call at startup."""
        noc = pd.read_parquet(self._gold_path / 'dim_noc.parquet')
        lead = pd.read_parquet(self._gold_path / 'element_lead_statement.parquet')
        titles = pd.read_parquet(self._gold_path / 'element_example_titles.parquet')

        # Build search DataFrame
        unit_groups = noc[noc.noc_code.str.len() == 5].copy()
        self._search_df = unit_groups.merge(
            lead[['unit_group_id', 'Lead statement']], on='unit_group_id', how='left'
        )
        title_agg = titles.groupby('unit_group_id')['Job title text'].apply(list).reset_index()
        title_agg.columns = ['unit_group_id', 'example_titles']
        self._search_df = self._search_df.merge(title_agg, on='unit_group_id', how='left')

        # Build O(1) lookup dicts for profile data
        for attr, filename, key_col in [
            ('_skills_lookup', 'oasis_skills.parquet', 'oasis_code'),
            ('_abilities_lookup', 'oasis_abilities.parquet', 'oasis_code'),
            ('_knowledges_lookup', 'oasis_knowledges.parquet', 'oasis_code'),
            ('_workactivities_lookup', 'oasis_workactivities.parquet', 'oasis_code'),
            ('_workcontext_lookup', 'oasis_workcontext.parquet', 'oasis_code'),
        ]:
            df = pd.read_parquet(self._gold_path / filename)
            setattr(self, attr, df.set_index(key_col).to_dict('index'))

        self._loaded = True
```

**Why load-at-startup over lazy loading:** The existing `LabelsLoader` uses lazy loading (load on first request). That works but means the first user of each file pays the I/O cost. For v5.0 where parquet IS the primary path (not a supplement), eager loading gives consistent response times. The 0.36s startup cost is acceptable; the alternative is unpredictable first-request latency.

**Why Python dicts for profile lookup:** The benchmark shows Python dict lookup at 0.0001ms vs pandas filter at 0.32ms. For a profile fetch that queries 5+ parquet files, this compounds. Pre-building dicts at startup (one-time 0.36s cost) gives 3000x faster per-request performance. This is the standard pattern for static reference data in Flask apps.

**Why keep DataFrames for search:** Text search requires scanning across rows (title, definition, lead statement). A DataFrame with vectorized `.str.contains()` is the right tool here. The search index is 894 rows; even a linear scan is under 1ms.

---

## Gold Parquet File Inventory (for v5.0 Reference)

### Files Needed for Search

| File | Rows | Key Column | Used For |
|------|------|------------|---------|
| `dim_noc.parquet` | 516 | `noc_code`, `unit_group_id` | Title + definition text search |
| `element_lead_statement.parquet` | 900 | `unit_group_id` | Lead statement text search |
| `element_example_titles.parquet` | 18,666 | `unit_group_id` | Alternate title search |
| `element_labels.parquet` | 900 | `unit_group_id` | OASIS label text |

### Files Needed for Profile Fetch

| File | Rows | Key Column | Profile Section |
|------|------|------------|----------------|
| `oasis_skills.parquet` | 900 | `oasis_code` | Skills (40 columns) |
| `oasis_abilities.parquet` | 900 | `oasis_code` | Abilities (56 columns) |
| `oasis_knowledges.parquet` | 900 | `oasis_code` | Knowledge (40 columns) |
| `oasis_workactivities.parquet` | 900 | `oasis_code` | Work Activities (41 columns) |
| `oasis_workcontext.parquet` | 900 | `oasis_code` | Work Context (60+ columns) |
| `element_lead_statement.parquet` | 900 | `unit_group_id` | Lead statement |
| `element_main_duties.parquet` | 8 | `unit_group_id` | Main duties (SAMPLE ONLY) |
| `element_exclusions.parquet` | varies | `oasis_profile_code` | Exclusions |
| `element_employment_requirements.parquet` | varies | `oasis_profile_code` | Employment requirements |
| `element_workplaces_employers.parquet` | varies | `oasis_profile_code` | Workplaces |

### Critical Coverage Gap

`element_main_duties.parquet` has only 8 rows covering 3 unit groups. This is sample data. The gold layer does NOT have complete main duties for all 510 unit groups. This is the single biggest gap between OASIS HTML scraping (which provides full main duties) and the gold parquet layer.

**Impact:** v5.0 will need to retain OASIS scraping as fallback specifically for main duties, OR acknowledge that main duties will be empty for most NOC codes until JobForge 2.0 provides a complete `element_main_duties.parquet`.

### Key Column Naming Note

The gold files use two different code formats:

| Format | Example | Files That Use It |
|--------|---------|-------------------|
| `oasis_code` (XX.XX format) | `21232.00` | oasis_skills, oasis_abilities, oasis_knowledges, oasis_workactivities, oasis_workcontext |
| `oasis_profile_code` (XX.XX format) | `21232.00` | element_labels, element_example_titles, element_exclusions, element_employment_requirements |
| `unit_group_id` (5-digit NOC, no dot) | `21232` | dim_noc, element_lead_statement, element_main_duties |
| `noc_code` (variable length) | `21232` (5-digit) or `212` (major group) | dim_noc only |

For v5.0, the user-facing NOC code (e.g., `21232`) maps to:
- `unit_group_id = '21232'` in dim_noc and element_* files
- `oasis_code = '21232.00'` in oasis_* files (append `.00` to convert)

---

## What NOT to Add for v5.0

| Technology | Why NOT |
|------------|---------|
| **polars** | Installed but not used; 27 MB of data shows no benefit over pandas; would require full rewrite of existing parquet code |
| **DuckDB** | Excellent for OLAP over large parquet datasets; the gold files are too small (27 MB) to benefit; adds a dependency for O(1) dict lookups |
| **SQLite copy of parquet** | Adds 50-200ms startup cost; creates data boundary confusion with existing occupational.db; no benefit over in-memory DataFrames |
| **fastparquet** | Alternative parquet engine; pyarrow is already installed and is the industry standard engine |
| **Apache Arrow datasets API** | Useful for partitioned multi-file parquet datasets too large for RAM; gold files are 27 MB total, this is overkill |
| **Redis/memcached** | External cache process for a local single-user Flask app; module-level Python dicts are sufficient |
| **threading.Lock** | The parquet data is read-only after startup; Python's GIL + write-once pattern makes explicit locks unnecessary |

---

## Integration Points with Existing Stack

### What Changes

| Component | Current Behavior | v5.0 Behavior |
|-----------|-----------------|---------------|
| `GET /api/search` | Calls `scraper.search()` → OASIS HTML → BeautifulSoup parse | Query `NocDataService._search_df` → return results |
| `GET /api/profile` | Calls `scraper.fetch_profile()` → OASIS HTML → parser | Lookup `NocDataService._*_lookup[code]` → build response |
| `LabelsLoader` | Lazy-loads gold parquet per request | Unchanged (data already served from gold; can merge into NocDataService eventually) |
| `VocabularyIndex` | Loads bronze parquet for vocabulary terms | Unchanged (continue reading bronze) |
| `OASISScraper` | Primary data source | Fallback only (network unavailable, missing data) |

### What Does NOT Change

- Flask 3.1.2, Flask-CORS, requests, BeautifulSoup4, lxml — OASIS scraper stays, just demoted to fallback
- pandas 2.2.3, pyarrow 23.0.0 — already the parquet stack, no version change needed
- SQLite / db_manager / repository — classification data layer is separate, untouched
- OpenAI SDK, instructor — AI classification pipeline unchanged
- python-dotenv, JOBFORGE_GOLD_PATH env var — already configured

### New File: `src/services/noc_data_service.py`

This is the only new file v5.0 needs for the parquet integration. It wraps the load-at-startup + dict-lookup pattern, providing:
- `search(query, search_type)` — replaces `scraper.search()` + `parser.parse_search_results_enhanced()`
- `get_profile(code)` — replaces `scraper.fetch_profile()` + `parser.parse_profile()`
- `is_available()` — used by routes to decide primary vs fallback path

### Fallback Logic Pattern

```python
# In GET /api/search:
if noc_data_service.is_available():
    results = noc_data_service.search(query, search_type)
else:
    # Existing OASIS path
    html = scraper.search(query, search_type=search_type)
    results = parser.parse_search_results_enhanced(html)
```

The fallback decision is per-request, not at startup, so OASIS scraping remains fully functional if the gold path is misconfigured.

---

## Python 3.14 Compatibility

| Library | Version | Python 3.14 Status |
|---------|---------|-------------------|
| pandas | 2.2.3 | VERIFIED: imports and read_parquet work (tested on Python 3.14.3) |
| pyarrow | 23.0.0 | VERIFIED: imports and parquet round-trip work (tested on Python 3.14.3) |
| polars | 1.38.1 | VERIFIED: imports and read_parquet work (installed, not currently used) |

All three libraries confirmed working on Python 3.14.3 in this environment. No version changes needed.

**Note on sentence-transformers:** `sentence-transformers==3.4.1` is in requirements.txt but inactive (torch unavailable on Python 3.14; TF-IDF fallback is active). This is unrelated to parquet integration and requires no change for v5.0.

---

## Updated requirements.txt for v5.0

**No changes required.** The existing `requirements.txt` already has everything needed:

```txt
# These are already present and sufficient for v5.0 parquet integration:
pandas==2.2.3       # DataFrame operations + parquet read
pyarrow==19.0.0     # Parquet engine (note: v23.0.0 is actually installed; pinning >=19 is fine)
```

The only code addition is `src/services/noc_data_service.py`. No `pip install` step is needed for v5.0.

---

## Confidence Assessment for v5.0

| Decision | Confidence | Reason |
|----------|------------|--------|
| No new libraries needed | HIGH | Verified: all required parquet files load correctly with existing pandas/pyarrow |
| Load-at-startup caching strategy | HIGH | Benchmarked: 0.36s startup, 27 MB RAM, O(0.0001ms) per-request dict lookup |
| pandas over polars | HIGH | Benchmarked on actual gold files; no performance difference at 27 MB; avoids full rewrite |
| Python dict for profile lookup | HIGH | Benchmarked: 3000x faster than pandas filter; standard pattern for static reference data |
| main_duties coverage gap | HIGH | Verified: element_main_duties.parquet has 8 rows (sample), not full 510 unit groups |
| oasis_code column naming | HIGH | Verified by inspection: append `.00` to 5-digit NOC code to get oasis_code format |
| OASIS remains as fallback | HIGH | Preserves existing working path; no regression risk |

---

## Open Questions for v5.0 Phase Planning

1. **Main duties gap:** Should v5.0 silently fall back to OASIS for main duties per-profile, or show parquet data as authoritative (empty for most NOC codes)? This is an architectural decision that affects how the profile response is assembled.

2. **oasis_profile_code vs unit_group_id:** The gold element files use `oasis_profile_code` (e.g., `21232.00`) as the key, while dim_noc uses `unit_group_id` (e.g., `21232`). When a user requests profile for NOC code `21232`, the lookup needs to normalize. The conversion is: `oasis_profile_code = noc_code + '.00'` for unit-level profiles, but multi-profile occupations (where one unit_group has multiple oasis profiles like `21232.01`, `21232.02`) need additional handling.

3. **Code search type:** The existing `search_type=Code` path does a code lookup against OASIS. With parquet, this becomes a `dim_noc` filter on `noc_code`. Works for 5-digit codes; partial prefix matching (e.g., user types `212`) would return 10+ major-group results.

4. **Hot reload:** The existing watchdog observer monitors bronze parquet files for VocabularyIndex hot-reload. Should NocDataService also watch gold parquet files? Likely yes, as JobForge 2.0 may update gold files between sessions.

---

## Sources for v5.0 Research

### Verified (HIGH confidence) - All results from direct codebase inspection and benchmarking

- Direct inspection of 25 gold parquet files at `/Users/victornishi/Documents/GitHub/JobForge-2.0/data/gold/`
- Benchmarking scripts run on Python 3.14.3 with pandas 2.2.3 and pyarrow 23.0.0
- Codebase analysis: `src/services/labels_loader.py`, `src/vocabulary/index.py`, `src/services/mapper.py`, `src/routes/api.py`
- Column schema verified by reading actual DataFrames, not documentation

### Key Measurements (run on this machine, Python 3.14.3)

| Measurement | Result |
|-------------|--------|
| Gold parquet disk size | 1.1 MB (25 files) |
| Gold parquet in-memory | 27.3 MB |
| Full load + index build | 0.36s |
| pandas linear filter | 0.32ms per call |
| pandas indexed .loc | 0.076ms per call |
| Python dict lookup | 0.0001ms per call |
| pandas vs polars read+filter (100x) | pandas 4.3ms avg, polars 2.4ms avg (read from disk) |
| pandas vs polars in-memory filter (10k) | pandas 0.29ms avg, polars 0.47ms avg |

---

*Stack research for: JD Builder Lite — v5.0 JobForge 2.0 parquet integration*
*Researched: 2026-03-06*
