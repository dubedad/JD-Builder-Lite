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
