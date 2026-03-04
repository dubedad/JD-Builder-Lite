# External Integrations

**Analysis Date:** 2026-03-04

## APIs & External Services

**LLM Services:**
- OpenAI API (gpt-4o) - Primary AI service for job description generation, occupation description synthesis, and occupational classification
  - SDK/Client: `openai` 1.109.1 (ChatCompletion API)
  - Auth: `OPENAI_API_KEY` (environment variable)
  - Usage: Streaming generation, icon selection, description synthesis, classification prompts
  - Integration points: `src/services/llm_service.py`, `src/services/generation_service.py`
  - Rate limiting: Handled by upstream OpenAI service; internal retry logic via `tenacity`

**Government Data Sources:**
- ESDC NOC 2025 v1.0 - National Occupational Classification (Government of Canada)
  - Accessible via OASIS portal at `https://noc.esdc.gc.ca`
  - Scraped via HTTP client in `src/scrapers/http_client.py`
  - Version: "2025.0" (configured in `src/config.py`)

- O*NET 27.2 - Occupational Information Network (US Department of Labor)
  - Referenced in README as secondary authoritative source
  - Integrated via data files (not directly API-based in current implementation)

- TBS Occupational Groups (Treasury Board of Canada Secretariat)
  - Base URL: `https://www.canada.ca`
  - Scraping paths:
    - `/en/treasury-board-secretariat/services/collective-agreements/occupational-groups.html`
    - `/en/treasury-board-secretariat/services/collective-agreements/occupational-groups/definitions.html`
    - `/en/treasury-board-secretariat/services/classification/job-evaluation/guide-allocating-positions-using-occupational-group-definitions.html`
  - Implementation: `src/scrapers/tbs_scraper.py`, `src/scrapers/tbs_parser.py`
  - Rate limiting: 1.0 second delay between requests (user decision per CONTEXT.md)

## Data Storage

**Databases:**
- SQLite 3 (local)
  - File: `data/occupational.db`
  - Client: sqlite3 (stdlib)
  - Configuration: WAL mode, foreign key constraints enabled, 5-second busy timeout
  - Purpose: Occupational reference data (NOC definitions, TBS occupational groups, classification rules)
  - Schema: `src/storage/schema.sql`
  - Management: `src/storage/db_manager.py` with context manager pattern

**File Storage:**
- Local filesystem only
  - Vocabulary indices: `data/noc/`, `data/onet/`, `data/classification/` (Parquet format)
  - Bronze layer: Raw scraped HTML/JSON
  - Silver layer: Parsed structured data
  - Gold layer: Domain-mapped data with provenance
  - Accessible via `JOBFORGE_BRONZE_PATH` config (set to Windows path in current deployment)
  - Hot-reload: Watched by `watchdog.observers.Observer` in `src/vocabulary/watcher.py`

**Caching:**
- In-memory cache for allocation results
  - Implementation: `_allocation_cache` dict in `src/routes/api.py`
  - Key: SHA256 hash of request data (16 chars)
  - Invalidation: Clears on JD content changes (per `_cache_key()` function)
  - No external cache system (Redis, Memcached) detected

## Authentication & Identity

**Auth Provider:**
- Custom/None - No external auth detected
- Flask sessions for state management
- `SECRET_KEY` from environment (required for session encryption)
- CORS enabled for cross-origin requests

## Monitoring & Observability

**Error Tracking:**
- None detected (README suggests optional Sentry/CloudWatch setup for production)
- LLM errors caught and sanitized in `src/services/llm_service.py` (API key errors masked for client)

**Logs:**
- Python logging module (stdlib)
- Loggers instantiated in services: `src/scrapers/tbs_scraper.py`, `src/services/generation_service.py`
- Console output for startup (vocabulary load count, generation service initialization)
- No centralized logging service detected

## CI/CD & Deployment

**Hosting:**
- Flask development server (dev): `app.run(debug=True, port=5000)`
- WSGI-compatible production servers (gunicorn, uWSGI, etc.)
  - Entry point: Module-level `app` in `src/app.py` (line 77)
  - Environment: `FLASK_ENV` (development|production)

**CI Pipeline:**
- Not detected in codebase (no GitHub Actions, Jenkins, etc.)

## Environment Configuration

**Required env vars:**
- `OPENAI_API_KEY`: OpenAI API key (sk-...) - CRITICAL
- `SECRET_KEY`: Flask session key (32+ bytes for production) - CRITICAL
- Optional:
  - `FLASK_ENV`: development or production (default: development)
  - `CLASSIFICATION_CACHE_TTL`: Cache lifetime seconds (default: 3600)
  - `CLASSIFICATION_MODEL`: LLM model name (default: gpt-4o)
  - `JOBFORGE_BRONZE_PATH`: Vocabulary parquet file path

**Secrets location:**
- `.env` file (local, not committed)
- Example provided: `.env.example` (credentials removed)
- No secrets manager integration detected (AWS Secrets Manager, HashiCorp Vault, etc.)

## Data Retrieval & Scraping

**Outgoing HTTP:**
- TBS occupational group pages: Rate-limited via `RATE_LIMIT_DELAY = 1.0` sec
- OASIS/NOC data: Direct HTTPS retrieval with retry logic
- Retry strategy: 3 attempts with exponential backoff (2, 4, 8 sec), targets [429, 500, 502, 503, 504]
- User-Agent: "JD-Builder/1.0 (TBS Occupational Data Scraper)" (transparency per IETF)
- Timeout: 30 seconds per request

**Data Archival:**
- Raw HTML archived by `src/scrapers/html_archiver.py`
- Change detection: `content_changed()` function prevents re-archiving identical content
- Provenance: Archive timestamp and content hash tracked for audit

## Webhooks & Callbacks

**Incoming:**
- None detected

**Outgoing:**
- None detected

## Integration Patterns

**Medallion Architecture (Bronze → Silver → Gold):**
1. **Bronze**: Raw scraped HTML/JSON stored in `data/` directories
2. **Silver**: Parsed structured data via BeautifulSoup and custom parsers
3. **Gold**: Domain-mapped objects with full provenance metadata
   - Used for API responses, export generation, classification

**Provenance Tracking:**
- Every data point tracked with:
  - Source identifier (ESDC NOC, O*NET, TBS)
  - Publication/scrape date (ISO 8601)
  - Source URL (for audit trail)
  - Data version (NOC 2025.0, O*NET 27.2)
- Exported in PDF/DOCX compliance metadata (Compliance Appendix)

**Generation Pipeline:**
1. User selects NOC statements → frontend sends to `/api/generate`
2. LLM service streams token-by-token to client (SSE)
3. Generation service validates output:
   - Vocabulary coverage (95% NOC terms required)
   - Semantic equivalence (0.75 cosine similarity threshold via sentence-transformers)
   - Retry on failure (max 3 attempts per `MAX_RETRIES`)
4. Fallback to original on exhaustion
5. All changes tracked with model, timestamp, prompt version

**Classification Pipeline:**
1. User initiates classification via `/api/allocate`
2. TBS occupational group data loaded from SQLite + parquet
3. Shortlisting: Semantic matching to candidate groups
4. LLM classification: GPT-4o ranks recommendations
5. Confidence scoring: 0.0-1.0 scale
6. Evidence extraction: Identifies supporting quotes from JD
7. Results cached in-memory with invalidation on JD changes

---

*Integration audit: 2026-03-04*
