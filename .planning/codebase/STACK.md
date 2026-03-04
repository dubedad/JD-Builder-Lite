# Technology Stack

**Analysis Date:** 2026-03-04

## Languages

**Primary:**
- Python 3.11+ - Backend application, data processing, API layer
- JavaScript/HTML/CSS - Frontend UI, client-side interaction

## Runtime

**Environment:**
- Python 3.11 or higher (specified in README.md)

**Package Manager:**
- pip (Python)
- Lockfile: `requirements.txt` (present, pinned versions)

## Frameworks

**Core:**
- Flask 3.1.2 - Web framework, API server, template rendering
- Flask-CORS 6.0.2 - Cross-origin resource sharing support
- Flask-WeasyPrint 1.1.0 - PDF generation integration

**Frontend:**
- Vanilla JavaScript (ES6+) with JSDoc comments - No frontend framework detected
- HTML5 templates with Jinja2 (Flask templating)
- CSS3 with media queries for print/screen styles

**LLM & AI:**
- OpenAI API (gpt-4o model) - Job description generation, icon selection, classification
- sentence-transformers 3.4.1 - Semantic similarity checking (all-MiniLM-L6-v2 model)
- instructor >=1.0.0,<2.0.0 - Structured output from LLM responses

**Data Processing:**
- pandas 2.2.3 - DataFrames for NOC/O*NET data
- pyarrow 19.0.0 - Parquet file support
- beautifulsoup4 4.14.3 - HTML parsing for scraping
- lxml 6.0.2 - XML/HTML parsing (BeautifulSoup backend)

**Document Export:**
- python-docx 1.2.0 - DOCX generation
- weasyprint 68.0 - CSS-to-PDF rendering (dependency of Flask-WeasyPrint)

**Utilities:**
- requests 2.32.5 - HTTP client for TBS/OASIS scraping
- pydantic 2.10.0 - Data validation and type hinting
- python-dotenv 1.2.1 - Environment variable loading
- tenacity 9.0.0 - Retry logic with exponential backoff
- watchdog 6.0.0 - File system monitoring for vocabulary hot-reload

## Key Dependencies

**Critical:**
- openai 1.109.1 - LLM service integration (gpt-4o for generation, classification)
- Flask 3.1.2 - Web server and API framework
- pydantic 2.10.0 - Type validation and request/response models
- sentence-transformers 3.4.1 - Semantic equivalence validation (22MB all-MiniLM-L6-v2)

**Data Storage & Processing:**
- sqlite3 (stdlib) - Local occupational reference database
- pandas 2.2.3 - NOC/O*NET vocabulary processing from parquet files
- pyarrow 19.0.0 - Parquet format support for vocabulary indices

**Content & Scraping:**
- beautifulsoup4 4.14.3 - TBS occupational group HTML parsing
- lxml 6.0.2 - XML/HTML parsing backend
- requests 2.32.5 - Rate-limited HTTP client for TBS scraping

**Export & Document Generation:**
- weasyprint 68.0 - CSS-to-PDF rendering for compliance export
- python-docx 1.2.0 - DOCX document generation with styling
- Flask-WeasyPrint 1.1.0 - Integration layer for WeasyPrint in Flask

**Robustness:**
- tenacity 9.0.0 - Automatic retry with exponential backoff for LLM calls
- watchdog 6.0.0 - File system events for vocabulary index hot-reload

## Configuration

**Environment:**
- `.env` file (required, example provided in `.env.example`)
- Key variables:
  - `OPENAI_API_KEY`: OpenAI API key for gpt-4o access (required)
  - `SECRET_KEY`: Flask session encryption (default: dev-secret-change-in-production)
  - `FLASK_ENV`: development or production (default: development)
  - `JOBFORGE_BRONZE_PATH`: Path to JobForge parquet vocabulary files (Windows path in config)

**Build:**
- No build system detected (Python app, runs directly with Flask)
- No webpack/bundler (static JS files served as-is)

## Platform Requirements

**Development:**
- Python 3.11+
- pip
- Internet connection (for ESDC NOC 2025 and O*NET 27.2 data retrieval)
- Sufficient disk space for parquet vocabulary indices and SQLite database

**Production:**
- Python 3.11+
- HTTPS support (TLS certificate required)
- OpenAI API key with rate limiting configured
- CORS origin allowlist (configured via CORS())
- Monitoring system (Sentry, CloudWatch, etc. - optional per README)
- WSGI server (gunicorn, uWSGI - app supports WSGI via module-level `app` in `src/app.py`)

**Database:**
- SQLite 3 (embedded, no external DB required for occupational reference data)
- WAL mode enabled for concurrent reads
- Foreign key constraints enforced

---

*Stack analysis: 2026-03-04*
