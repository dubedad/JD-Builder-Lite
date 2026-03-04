# Codebase Concerns

**Analysis Date:** 2026-03-04

## Security Issues

### Critical: Disabled SSL Certificate Verification

**Risk Level:** CRITICAL

- **Issue:** SSL verification disabled in HTTP requests to Canada's NOC (OASIS) system
- **Files:**
  - `src/services/scraper.py:47,73` - `verify=False` in requests.Session.get()
- **Impact:** Man-in-the-middle (MITM) attacks possible. Sensitive occupational data and government websites are compromised endpoints.
- **Current Status:** Production-ready code with MITM vulnerability
- **Fix Approach:**
  1. Remove `verify=False` parameter from both `.get()` calls
  2. Ensure requests library has current SSL certificates: `pip install --upgrade certifi`
  3. For development environments only, use environment-based override with explicit opt-in (never default to disabled)
  4. Test against OASIS URLs to verify SSL chain works correctly

### Medium: Weak Default Secret Key

**Risk Level:** MEDIUM

- **Issue:** Default SECRET_KEY in config.py is weak development key not intended for production
- **Files:** `src/config.py:17` - `SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-in-production")`
- **Impact:** Session hijacking, CSRF attacks if default used in production. Flask uses this for session encryption.
- **Current Status:** Environment variable with weak fallback
- **Fix Approach:**
  1. Remove default fallback entirely - raise error if SECRET_KEY not set
  2. Document in README that SECRET_KEY must be set for all deployments
  3. Add startup validation to check SECRET_KEY is production-strength (32+ bytes)
  4. Update deployment checklist

### Medium: In-Memory Cache Not Bound to User Sessions

**Risk Level:** MEDIUM

- **Issue:** Allocation classification cache in `_allocation_cache` dict is global with no session isolation
- **Files:** `src/routes/api.py:31,46` - Global dict caching without user context
- **Impact:** Multi-user deployments may leak cached classification results between users. User A's JD classification could be visible to User B if similar JD submitted.
- **Current Status:** Works for single-user development, breaks in multi-user production
- **Fix Approach:**
  1. Move cache from global dict to Flask session: `session['_allocation_cache']`
  2. Or use request context scoped cache with user ID as part of key
  3. Add test case for multi-user isolation
  4. Document cache lifetime in docstring

---

## Performance & Scalability

### High: Lazy Semantic Matcher Model Loading

**Risk Level:** HIGH (affects UX)

- **Issue:** Sentence-transformer model loaded on first shortlisting call, not at startup
- **Files:**
  - `src/matching/shortlisting/__init__.py:64-79` - Lazy singleton loading
  - `src/matching/shortlisting/semantic_matcher.py` - Model initialization
- **Impact:** First classification request hangs 30-60 seconds while downloading/loading model (~500MB). Subsequent requests fast. Bad UX for users unaware of cold start.
- **Current Status:** Works but UX issue
- **Improvement Path:**
  1. Pre-load semantic matcher at app startup in `initialize_vocabulary()` in `src/app.py`
  2. Show loading progress indicator or splash screen
  3. Add timeout handling - if model load exceeds 120s, graceful fallback to keyword matching only
  4. Document expected startup time in README

### High: No Request Timeout for OpenAI API

**Risk Level:** HIGH

- **Issue:** OpenAI client initialized without timeout. Network hangs or slow API responses block indefinitely.
- **Files:**
  - `src/services/llm_service.py:54` - `client = OpenAI(api_key=OPENAI_API_KEY)`
  - `src/services/generation_service.py:98` - Same
  - `src/matching/classifier.py:32` - Instructor-wrapped OpenAI client
- **Impact:** Long-running requests consume resources indefinitely. Slow clients lock database connections. Frontend SSE stream hangs.
- **Fix Approach:**
  1. Add `timeout=30` to OpenAI client initialization (or config parameter)
  2. Wrap LLM calls with try/except for `openai.APITimeoutError`
  3. Return user-friendly error when timeout occurs
  4. Test with slow network conditions

### Medium: No Max Retries on External HTTP Requests

**Risk Level:** MEDIUM

- **Issue:** OASIS HTTP requests in `src/services/scraper.py` use `response.raise_for_status()` without retry logic
- **Files:** `src/services/scraper.py:23-49` (search), `51-75` (profile fetch)
- **Impact:** Transient network errors (timeout, 503) immediately fail user request. No exponential backoff for OASIS outages.
- **Improvement Path:**
  1. Wrap requests in `tenacity.retry` decorator (already in requirements.txt)
  2. Use exponential backoff: `wait_exponential(multiplier=1, min=1, max=10)`
  3. Max 3 retries for search/profile fetches
  4. Return 503 to user after exhausting retries

---

## Test Coverage Gaps

### Critical: Minimal Test Coverage

**Risk Level:** HIGH

- **Issue:** Only 2 test files in codebase (`uat_terminal.py`, `test_uat_screenshots.py`)
- **Files:** `tests/` directory
- **What's Not Tested:**
  - Classification engine (`src/matching/allocator.py`, `classifier.py`, `confidence.py`)
  - Evidence extraction (`src/matching/evidence/`)
  - API routes error handling (`src/routes/api.py`)
  - Export service and PDF/DOCX generation (`src/services/export_service.py`, `pdf_generator.py`, `docx_generator.py`)
  - Parser robustness against malformed HTML
  - Database layer and repository operations
- **Risk:** Bugs in classification flow, export format corruption, and data access patterns go undetected until UAT/production
- **Priority:** HIGH - Add unit tests for:
  1. Classification confidence calculations (edge cases: tied scores, all low confidence)
  2. Evidence extraction with various JD formats
  3. Export serialization and PDF/DOCX rendering
  4. Parser fallback selectors when HTML changes

### Medium: No Integration Tests for Multi-Step Flows

**Risk Level:** MEDIUM

- **Issue:** No tests for full request-response cycles
- **Risk:** End-to-end bugs like session data loss or missing export headers not caught
- **Test Types Needed:**
  - Search → Profile → Classification → Export flow
  - Generation metadata tracking through session
  - Cache invalidation on JD changes

---

## Technical Debt & Deprecation

### Medium: Deprecated Parser Methods Not Removed

**Risk Level:** MEDIUM

- **Issue:** Old parser methods kept for backward compatibility but create confusion
- **Files:**
  - `src/services/parser.py:382` - DEPRECATED comment for old extraction method
  - `src/services/mapper.py:298` - DEPRECATED non-enriched methods
- **Impact:** Code smell. Maintainers unsure which methods to use. Risk of bugs if deprecated code still called.
- **Fix Approach:**
  1. Remove `parse_search_results()` (line ~23) - replaced by `parse_search_results_enhanced()`
  2. Remove old mapping methods in mapper.py - verify no callers in codebase
  3. Add deprecation warnings if temporary compatibility needed
  4. Update imports to remove unused methods

### Medium: Hardcoded File Path in Config

**Risk Level:** MEDIUM

- **Issue:** Hardcoded Windows user path in `src/config.py`
- **Files:** `src/config.py:20` - `JOBFORGE_BRONZE_PATH = "C:/Users/Administrator/Dropbox/..."`
- **Impact:** Won't work on other machines or Linux/Mac. Development blocker if file not at exact path.
- **Fix Approach:**
  1. Move to environment variable: `JOBFORGE_BRONZE_PATH = os.getenv("JOBFORGE_BRONZE_PATH", default_path)`
  2. Add `.env.example` entry with placeholder
  3. Document required setup in README quick start

---

## Data Consistency & Validation

### Medium: No Validation on External HTML Parsing Fallbacks

**Risk Level:** MEDIUM

- **Issue:** Parser uses fallback selectors but no validation that parsed data is correct format
- **Files:** `src/services/parser.py:35-50` - Primary/fallback selector with no data quality checks
- **Impact:** If OASIS HTML changes, fallback might parse wrong data silently. No error surface until export or classification fails.
- **Fix Approach:**
  1. Add schema validation after parsing: verify NOC codes match pattern `\d{5}(\.\d{2})?`
  2. Log warnings if fallback selector used (indicates potential HTML change)
  3. Validate required fields non-empty before returning
  4. Raise exception if data quality check fails (don't return partial data)

### Low: Missing Type Hints on Some Functions

**Risk Level:** LOW

- **Issue:** Some older service methods lack type hints
- **Files:** Various in `src/services/`
- **Impact:** IDE autocomplete gaps, harder debugging
- **Fix Approach:** Add return type hints to all public methods (use `Optional[T]` appropriately)

---

## Error Handling Gaps

### Medium: Broad Exception Catching in Critical Paths

**Risk Level:** MEDIUM

- **Issue:** Multiple places catch generic `Exception` without re-raising critical errors
- **Files:**
  - `src/routes/api.py:304-306` - Catches all exceptions in generation
  - `src/matching/classifier.py:100` - Generic exception handler in LLM classify fallback
  - `src/routes/api.py:372-374` - Graceful degradation hides errors (intentional but opaque)
- **Impact:**
  - Difficult to debug production issues (swallowed stack traces)
  - Some errors should fail loudly (e.g., database errors) not be caught
- **Fix Approach:**
  1. Catch specific exceptions: `except (ValueError, KeyError, TypeError)` not `except Exception`
  2. Log full stack traces: `logger.exception("Error in X", exc_info=True)`
  3. Distinguish recoverable errors (log + graceful fallback) vs fatal errors (re-raise)
  4. Return meaningful error codes to frontend for user messaging

### Low: Missing Rate Limiting on LLM Calls

**Risk Level:** MEDIUM (cost control)

- **Issue:** No rate limiting or quota tracking for OpenAI API calls
- **Files:** `src/routes/api.py:/generate`, `src/matching/classifier.py`
- **Impact:** Runaway costs if user runs many classifications. No cost monitoring.
- **Fix Approach:**
  1. Track API call count in session or database
  2. Return 429 when limit exceeded
  3. Log API call costs for monitoring
  4. Add configurable quota per user/day

---

## Dependencies & Versions

### Medium: Unpinned Version Constraint on instructor

**Risk Level:** MEDIUM

- **Issue:** `requirements.txt` has `instructor>=1.0.0,<2.0.0` - will pull latest 1.x
- **Files:** `requirements.txt:17`
- **Impact:** Updates to instructor library could break structured output Pydantic integration without warning
- **Fix Approach:**
  1. Pin to specific tested version: `instructor==1.3.2` (example)
  2. Document when versions tested
  3. Add test that validates structured output schema with current instructor version

### Low: Sentence-transformers Model Size

**Risk Level:** LOW (performance, not functionality)

- **Issue:** `sentence-transformers` in requirements.txt downloads large model at runtime (~500MB)
- **Files:** `requirements.txt:16`
- **Impact:** First request slow, increases deployment artifact size
- **Improvement:** Pre-build Docker image with model cached, or use smaller model variant

---

## Known Limitations / Edge Cases

### High: AP vs TC Group Classification Ambiguity

**Risk Level:** HIGH (classification accuracy)

- **Issue:** Applied Science (AP) vs Technician/Technologist (TC) classification requires manual disambiguation
- **Files:** `src/matching/edge_cases.py:59-97` - Detection logic only, no automatic resolution
- **Impact:** Users may select wrong group if edge case not caught. Classification depends on manual review.
- **Current Status:** Edge case flagged for expert review, no auto-selection
- **Improvement:**
  1. Add more indicator keywords in AP_TC_RULES
  2. Consider secondary signals: required certifications, education level
  3. Add example JDs to training for LLM classifier

### Medium: Vague Job Descriptions Not Caught Early

**Risk Level:** MEDIUM

- **Issue:** EDGE-04 detector in `edge_cases.py` flags vague content but no minimum JD content enforcement
- **Files:** `src/matching/edge_cases.py` - Detection only
- **Impact:** Classification on minimal data produces low-confidence result with no warning
- **Fix Approach:**
  1. Add validation on `/generate` route: minimum 100 chars of activities required
  2. Warn user before classification if JD content minimal
  3. Suggest user provide more details

### Low: Allocation Guide URL Hardcoded

**Risk Level:** LOW

- **Issue:** TBS allocation guide URL hardcoded in multiple places
- **Files:**
  - `src/scrapers/http_client.py:19`
  - `src/matching/edge_cases.py` (implicit)
- **Impact:** If TBS updates URL, code breaks silently
- **Fix Approach:** Move to config constant, document source

---

## Fragile Areas Requiring Careful Changes

### HTML Parser Fragility (MEDIUM RISK)

**Files:** `src/services/parser.py`, `src/scrapers/tbs_parser.py`

**Why Fragile:** Uses CSS selectors to parse government websites (OASIS, TBS). OASIS HTML updates monthly, TBS site redesigns periodically.

**Safe Modification:**
1. Maintain primary + fallback selectors for all extractions
2. Add integration tests that validate parser against real OASIS responses (cached)
3. Log warnings when fallback selectors used (indicates HTML drift)
4. Have parsing output validation schema to catch malformed data

### LLM Response Parsing (MEDIUM RISK)

**Files:** `src/matching/classifier.py`, `src/services/llm_service.py`

**Why Fragile:** Instructor library enforces Pydantic schema, but OpenAI API can still return incomplete/null fields if under token pressure

**Safe Modification:**
1. Always check AllocationResult fields for None before accessing
2. Add fallback values for critical fields (e.g., if no recommendations, return empty list not None)
3. Test with max_retries=3 to ensure schema validation works
4. Don't assume token length calculations - add try/except around token counting

### Session-Based Export Metadata (MEDIUM RISK)

**Files:** `src/routes/api.py` (generation metadata in session)

**Why Fragile:** Provenance metadata stored in Flask session dict, no versioning

**Safe Modification:**
1. Always validate session keys exist before accessing: `session.get('ai_generation', {})`
2. Version metadata schema if fields change: add `schema_version` field
3. Handle missing fields gracefully (backward compat)
4. Don't rely on session persisting across server restarts

---

## Monitoring & Observability Gaps

### Medium: No Error Tracking or Alerting

**Risk Level:** MEDIUM

- **Issue:** No Sentry, CloudWatch, or error aggregation service integrated
- **Files:** All error handlers in `src/routes/api.py`
- **Impact:** Production errors only discovered when users report. No visibility into failure patterns.
- **Recommendation:** Add Sentry integration (documented in README production checklist)

### Low: Logging Not Structured

**Risk Level:** LOW

- **Issue:** Logs use Python logging with no structured fields (JSON)
- **Files:** Throughout codebase (`logger = logging.getLogger()`)
- **Impact:** Harder to parse logs in log aggregation service
- **Recommendation:** Switch to `python-json-logger` for structured logging

---

## Security Considerations

### Medium: API Routes Have No Authentication

**Risk Level:** MEDIUM (depends on deployment)

- **Issue:** All `/api/*` routes are public - no API key or user authentication required
- **Files:** `src/routes/api.py` - All routes lack `@require_auth` decorator
- **Impact:**
  - Anyone can call `/api/generate` and incur OpenAI costs
  - Anyone can scrape occupational data via `/api/search` and `/api/profile`
- **Current Mitigation:** Designed as internal tool, not public API
- **Recommendations for Production:**
  1. Add API key validation if exposed publicly
  2. Implement rate limiting per IP or user
  3. Document that this tool assumes secure network (not internet-facing)
  4. Add authentication section to deployment guide

### Medium: No CORS Validation

**Risk Level:** MEDIUM

- **Issue:** `CORS(app)` enables CORS for all origins
- **Files:** `src/app.py:51` - Blanket CORS enabled
- **Impact:** Browser-based CSRF attacks possible if frontend hosted elsewhere
- **Fix Approach:**
  1. Change to: `CORS(app, origins=["http://localhost:5000"])`  (development)
  2. Use config parameter for allowed origins in production
  3. Document CORS setup in deployment guide

---

## Database Concerns

### Low: No Connection Pooling

**Risk Level:** LOW (small-scale app)

- **Issue:** Each database request creates new connection
- **Files:** `src/storage/db_manager.py:86` - `get_connection()` creates fresh connection
- **Impact:** For multi-user deployments, connection overhead increases. SQLite handles this OK but not optimal.
- **Improvement Path (future):** Consider connection pool if user base grows (e.g., with `sqlite3-pool` or migration to PostgreSQL)

### Low: No Data Backup Strategy

**Risk Level:** LOW

- **Issue:** SQLite database in `data/occupational.db` not mentioned in backup procedures
- **Files:** Database stored in project directory
- **Impact:** User data loss if system failure (though data is reconstructed from OASIS)
- **Recommendation:** Document backup strategy in operations guide

---

## Summary of Priorities

| Priority | Issue | File(s) | Impact |
|----------|-------|---------|--------|
| **CRITICAL** | SSL verification disabled | `src/services/scraper.py` | MITM attacks on gov data |
| **HIGH** | Minimal test coverage | `tests/` | Undetected bugs in core logic |
| **HIGH** | Semantic model cold start | `src/matching/shortlisting/` | UX: 30-60s first request hang |
| **HIGH** | No LLM timeout | `src/services/llm_service.py` | Requests block indefinitely |
| **MEDIUM** | In-memory cache not isolated | `src/routes/api.py` | Multi-user data leak risk |
| **MEDIUM** | Weak default SECRET_KEY | `src/config.py` | Session hijacking in production |
| **MEDIUM** | No request retries | `src/services/scraper.py` | Transient failures fail immediately |
| **MEDIUM** | Deprecated code not removed | `src/services/parser.py` | Code smell, confusion |
| **MEDIUM** | No CORS origin validation | `src/app.py` | CSRF attacks |

---

*Concerns audit: 2026-03-04*
