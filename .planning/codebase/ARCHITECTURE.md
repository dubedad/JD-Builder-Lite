# Architecture

**Analysis Date:** 2026-03-04

## Pattern Overview

**Overall:** Medallion Architecture (Bronze → Silver → Gold) + Layered Web Application

The application follows a three-tier medallion pattern for data quality:
- **Bronze**: Raw scraped HTML/JSON from OASIS and O*NET
- **Silver**: Parsed structured data (NOC statements, attributes)
- **Gold**: Domain-mapped JD elements with full provenance tracking

Combined with a layered web application:
- **HTTP Layer**: Flask API routes with REST endpoints
- **Service Layer**: Business logic (scraper, parser, mapper, LLM, export)
- **Storage Layer**: Database and cache management
- **Matching Engine**: Classification and allocation orchestration
- **Frontend**: Single-page application with client-side state management

**Key Characteristics:**
- Provenance-first design: Every data point tracks source, publication date, URL, scrape timestamp
- Separation of concerns: HTTP routing, business logic, and data access are cleanly separated
- Structured LLM outputs: Uses Pydantic models for type-safe OpenAI API contracts
- Vocabulary-driven: Dynamic vocabulary indexing from JobForge parquet files with hot-reload
- Chain-of-thought reasoning: Classification includes explicit reasoning steps and evidence extraction

## Layers

**HTTP/API Layer:**
- Purpose: Flask REST API endpoints for frontend consumption
- Location: `src/routes/api.py`
- Contains: Route handlers for search, profile, generation, export, allocation, styling
- Depends on: Services (scraper, mapper, export), models (Pydantic validation), LLM service
- Used by: Browser frontend, mobile clients, external integrations

**Service Layer:**
- Purpose: Business logic orchestration, data transformation, external service calls
- Location: `src/services/`
- Contains:
  - `scraper.py`: HTTP client wrapper (OASIS, O*NET)
  - `parser.py`: HTML/JSON parsing → structured data
  - `mapper.py`: NOC → JD element transformation
  - `llm_service.py`: OpenAI API calls for generation, classification, icon selection
  - `export_service.py`: Build export data structures
  - `pdf_generator.py`: WeasyPrint rendering
  - `docx_generator.py`: Word document generation
  - `generation_service.py`: Styled statement generation with vocabulary validation
  - `enrichment_service.py`: Work context classification
  - `csv_loader.py`, `labels_loader.py`: Data loading from parquet/CSV files
- Depends on: External APIs (OpenAI, OASIS), models, storage, vocabulary
- Used by: Routes, matching engine, export services

**Model/Data Layer:**
- Purpose: Type-safe data contracts and validation
- Location: `src/models/`
- Contains:
  - `noc.py`: NOC domain models (NOCStatement, JDElementData, SourceMetadata)
  - `responses.py`: API response models (SearchResponse, ProfileResponse, ErrorResponse)
  - `allocation.py`: Allocation request/response models (AllocationRequest, AllocationResponse)
  - `export_models.py`: Export data structures (ExportRequest, ExportData, JDElementExport)
  - `ai.py`: AI generation contracts (GenerationRequest, GenerationMetadata, StatementInput)
  - `styled_content.py`: Styled statement models (StyledStatement, StyleVersionHistory)
  - `vocabulary_audit.py`: Vocabulary validation models (VocabularyTerm, VocabularyAudit)
- Depends on: Pydantic (validation framework)
- Used by: Routes, services, matching engine

**Storage/Database Layer:**
- Purpose: Persistent storage, caching, and data repository access
- Location: `src/storage/`
- Contains:
  - `db_manager.py`: Database connection and lifecycle management
  - `repository.py`: ORM-like access to occupational groups, definitions, provenance
- Depends on: Database driver (SQLite, PostgreSQL)
- Used by: Matching engine, services

**Matching/Classification Engine:**
- Purpose: Phase 15 - Allocate job descriptions to occupational groups
- Location: `src/matching/`
- Contains:
  - `allocator.py`: Main orchestrator (OccupationalGroupAllocator)
  - `shortlisting/semantic_matcher.py`: Semantic similarity filtering
  - `shortlisting/labels_matcher.py`: Label-based candidate boosting
  - `classifier.py`: LLMClassifier for structured output
  - `confidence.py`: Multi-factor confidence scoring
  - `evidence/extractor.py`: Quote extraction from job description
  - `edge_cases.py`: Special case handling (split duties, borderline matches)
  - `provenance_builder.py`: Build TBS directive provenance maps
  - `models.py`: AllocationResult, GroupRecommendation, EvidenceSpan
- Depends on: LLM service, storage, models
- Used by: /allocate API endpoint

**Vocabulary Module:**
- Purpose: NOC term indexing and coverage validation
- Location: `src/vocabulary/`
- Contains:
  - `index.py`: VocabularyIndex (loads from JobForge parquet files)
  - `validator.py`: VocabularyValidator (checks text against NOC terminology)
  - `watcher.py`: File system watcher for hot-reload on parquet changes
- Depends on: pandas, pyarrow (parquet reading)
- Used by: Generation service, app initialization

**Frontend Layer:**
- Purpose: Single-page application for JD building workflow
- Location: `static/js/`, `templates/index.html`
- Contains:
  - `main.js`: Application initialization, event handling, view management
  - `api.js`: API client wrapper with fetch-based requests
  - `state.js`: Reactive state management with localStorage persistence
  - `accordion.js`: Collapsible section management
  - `main.css`: Core styling, layout, typography
  - `classify.js`: Classification UI and evidence highlighting
  - `export.js`: Export preview and download orchestration
  - `generate.js`: AI generation streaming and display
  - `styling.js`: Statement styling workflow
  - `filters.js`: Result filtering and sorting
- Depends on: Fetch API, localStorage, Font Awesome icons
- Used by: Browser

## Data Flow

**Search & Profile Flow:**

1. User enters search query in browser
2. Frontend calls `GET /api/search?q=...`
3. Scraper fetches HTML from OASIS search endpoint
4. Parser extracts result items with NOC codes, titles, lead statements
5. Results scored by relevance (exact match > partial match > description match)
6. Filtered to remove low-confidence results (≤20%)
7. Sorted by relevance score descending
8. Frontend renders results as cards or table

**Profile Selection Flow:**

1. User clicks result to fetch full profile
2. Frontend calls `GET /api/profile?code=21232`
3. Scraper fetches full HTML from OASIS profile endpoint
4. Parser extracts:
   - Title, lead statement, example job titles
   - Key activities (with proficiency levels/skill codes)
   - Skills (with levels)
   - Work context (effort/responsibility/conditions)
   - Reference attributes, inclusions/exclusions
5. Mapper transforms into JD element structure:
   - Groups activities by proficiency level
   - Classifies work context into effort/responsibility/working conditions
   - Supplements with parquet-loaded example titles
   - Creates source metadata (NOC version, scraped date, profile URL)
6. Frontend displays in tabbed interface with metadata

**JD Building & Selection Flow:**

1. User selects statements from profile (checkboxes)
2. Frontend stores selections in client-side `store` (state.js)
3. Selections persisted to localStorage
4. User can edit descriptions, proficiency levels, text
5. When profile changes, selections auto-clear (resetSelectionsForProfile)
6. All selections retained across page refreshes

**AI Generation Flow:**

1. User clicks "Generate Overview" with selected statements
2. Frontend calls `POST /api/generate` with statements and job context
3. Route stores generation metadata in Flask session (model, prompt version, timestamp)
4. Backend streams OpenAI response as Server-Sent Events (SSE)
5. Frontend receives tokens in real-time and displays streaming text
6. When complete, frontend calls `POST /api/mark-modified` if user edits text
7. Session metadata tracks if AI content was modified by user

**Styled Statement Generation Flow:**

1. User clicks "Style" button on NOC statement
2. Frontend calls `POST /api/style` with statement ID, text, section
3. GenerationService:
   - Loads VocabularyIndex from app initialization
   - Generates styled variant using sentence transformers + few-shot examples
   - Validates output against NOC vocabulary with confidence scoring
   - Falls back to original text if confidence too low
4. Frontend displays styled variant with confidence metadata

**Classification/Allocation Flow:**

1. User completes JD and clicks "Classify"
2. Frontend calls `POST /api/allocate` with position_title, client_service_results, key_activities, skills, labels
3. Request validated against AllocationRequest Pydantic model
4. Cache checked (invalidates when JD content changes)
5. OccupationalGroupAllocator orchestrates:
   - Load occupational groups from database
   - Shortlist candidates using semantic similarity + label matching
   - LLMClassifier calls GPT-4o with structured outputs
   - ConfidenceCalculator scores multi-factor (definition fit, inclusions, exclusions, labels, semantics)
   - EvidenceExtractor extracts quoted text supporting each recommendation
   - EdgeCaseHandler detects split duties, borderline matches
6. ProvenanceBuilder maps each recommendation to TBS directive URLs
7. Response with top 3 recommendations, full provenance, confidence summary
8. Frontend displays recommendations with evidence highlighting

**Export Flow:**

1. User clicks "Export to PDF/DOCX"
2. Frontend sends `POST /api/export/pdf` or `/api/export/docx` with all JD data
3. Route fetches raw NOC data for Annex (graceful degradation if fails)
4. ExportService builds complete export structure:
   - Organize selections by JD element
   - Attach provenance (source_attribute, publication_date, source_table_url)
   - Build classification section (if available)
   - Build Annex with raw NOC profile
5. PDF/DOCX generator renders template with compliance metadata
6. File returned with Content-Disposition header for download

**State Management:**

**Frontend State (state.js):**
- `selections`: Object mapping JD element → selected statements array
- `currentProfileCode`: Currently loaded NOC code
- Mutations via `setState()`, `setSelections()`, `resetSelectionsForProfile()`
- All changes persisted to localStorage
- Listeners notify modules of state changes

**Backend Session State:**
- `ai_generation`: GenerationMetadata stored in Flask session
  - Tracks model name, prompt version, input statement IDs, timestamp, modified flag
  - Used by export to include provenance in PDF/DOCX

**Cache (api.py):**
- Simple in-memory cache for allocation results
- Key generated from request data hash
- Invalidates when JD content changes

## Key Abstractions

**OccupationalGroupAllocator:**
- Purpose: Single responsibility pattern for classification orchestration
- Examples: `src/matching/allocator.py`
- Pattern: Strategy pattern (shortlisting, classification, confidence, evidence extraction all injected as components)
- Methods: `allocate(jd_data: Dict) → AllocationResult`

**JDMapper:**
- Purpose: Transform external data (NOC) into internal domain structure (JD elements)
- Examples: `src/services/mapper.py`
- Pattern: Adapter pattern (OASIS HTML/JSON → JDElementData)
- Methods: `to_jd_elements(noc_data: Dict) → Dict with JDElementData`

**VocabularyIndex:**
- Purpose: Load and search NOC vocabulary from parquet files
- Examples: `src/vocabulary/index.py`
- Pattern: Singleton-like (initialized once at app startup)
- Methods: `get_terms(section: str)`, `get_term_count()`, `validate_text(text: str)`

**ExportService:**
- Purpose: Build exportable data structure with full provenance
- Examples: `src/services/export_service.py`
- Pattern: Builder pattern (gradually assemble export structure)
- Methods: `build_export_data(request: ExportRequest, raw_noc_data: Optional) → ExportData`

**OASISScraper:**
- Purpose: HTTP client for OASIS endpoints with session management
- Examples: `src/services/scraper.py`
- Pattern: Facade pattern (wraps requests library)
- Methods: `search(query, search_type)`, `fetch_profile(code)`

**Pydantic Models:**
- Purpose: Type-safe validation and serialization for API contracts
- Examples: `src/models/`
- Pattern: Data Transfer Objects (DTOs)
- Usage: Request validation, response serialization, documentation

## Entry Points

**Flask Application:**
- Location: `src/app.py`
- Triggers: `python -m flask run` or `gunicorn src.app:app`
- Responsibilities:
  - Create Flask app instance
  - Initialize vocabulary index and file watcher
  - Register API blueprint
  - Serve frontend HTML at `/`
  - Handle CORS headers

**API Routes:**
- Location: `src/routes/api.py`
- Triggers: HTTP requests to `/api/*` endpoints
- Responsibilities:
  - Validate request data
  - Call services/matching engine
  - Format responses
  - Handle error cases with appropriate status codes

**Frontend Application:**
- Location: `templates/index.html`
- Triggers: Browser load of `/`
- Responsibilities:
  - Initialize modules (sidebar, selection, filters)
  - Set up event listeners
  - Display progress stepper (4 steps: Search → Profile → Build → Export)
  - Manage workflow state

**CLI Tools:**
- Location: `src/cli/refresh_occupational.py`
- Triggers: `python -m src.cli.refresh_occupational`
- Responsibilities:
  - Fetch and cache occupational group definitions
  - Prime database for allocation engine

## Error Handling

**Strategy:** Graceful degradation with descriptive error responses

**Patterns:**

**API Errors (Flask routes):**
```python
# Validation error → HTTP 400
if not query or len(query) < 2:
    return jsonify(ErrorResponse(error="Invalid query", detail="...").model_dump()), 400

# Network error → HTTP 502
except requests.RequestException as e:
    return jsonify(ErrorResponse(error="Search failed", detail=str(e)).model_dump()), 502

# Internal error → HTTP 500 (no detail exposed to client)
except Exception as e:
    return jsonify(ErrorResponse(error="Internal error", detail=None).model_dump()), 500
```

**Service Errors:**
- Services raise exceptions with descriptive messages
- Routes catch and convert to appropriate HTTP status codes
- No internal details leaked to client in production

**Frontend Errors:**
- API client (api.js) parses error responses and throws
- UI modules catch and display user-friendly messages
- Fetch failures (network timeouts) handled with retry or fallback

**Optional Data Handling:**
- NOC Annex generation fails gracefully (continues without Annex)
- Label boosting fails gracefully (proceeds with semantic matching only)
- Vocabulary validation shows confidence scores (allows fallback to original)

## Cross-Cutting Concerns

**Logging:**
- Flask app logger (current_app.logger) used throughout routes
- Log levels: WARNING for expected errors, ERROR for unexpected failures
- No explicit logging module imported; uses Flask's built-in logger
- Format: `current_app.logger.error(f"context: {message}")`

**Validation:**
- Pydantic models validate all API request data
- Field validators in allocation.py, export_models.py
- NOC code pattern validation with regex (^\d{5}(?:\.\d{2})?$)
- Minimum length/format checks on strings

**Authentication:**
- Not required per CONTEXT.md (single JD per request, no auth)
- CORS enabled for cross-origin requests
- Session used only for AI generation metadata tracking
- SECRET_KEY configured in .env for session encryption

**Provenance Tracking:**
- Every statement includes: source_attribute, publication_date, source_table_url
- Scrape timestamps recorded in SourceMetadata
- AI generation tracked: model name, prompt version, input IDs, modified flag
- Classification includes full reasoning steps and evidence spans
- Export embeds all provenance in PDF/DOCX

**Rate Limiting:**
- Not implemented (out of scope for v4.1)
- OpenAI API rate limits enforced at SDK level
- OASIS scraping respects HTTP timeouts (60 seconds)

---

*Architecture analysis: 2026-03-04*
