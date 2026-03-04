# Codebase Structure

**Analysis Date:** 2026-03-04

## Directory Layout

```
jd-builder-lite/
├── src/                          # Application source code
│   ├── app.py                    # Flask app factory and initialization
│   ├── config.py                 # Configuration constants (OASIS URLs, API keys, paths)
│   ├── __init__.py              # Package initialization
│   ├── routes/
│   │   ├── __init__.py
│   │   └── api.py               # Flask API routes (search, profile, generate, export, allocate)
│   ├── services/                 # Business logic layer
│   │   ├── scraper.py           # OASIS HTTP client (OASISScraper class)
│   │   ├── parser.py            # HTML/JSON parsing into structured data
│   │   ├── mapper.py            # NOC → JD element transformation (JDMapper class)
│   │   ├── llm_service.py       # OpenAI API wrapper (generation, classification, icons)
│   │   ├── export_service.py    # Build export data structures
│   │   ├── pdf_generator.py     # WeasyPrint rendering for PDF
│   │   ├── docx_generator.py    # python-docx Word document generation
│   │   ├── generation_service.py # Styled statement generation with vocabulary validation
│   │   ├── enrichment_service.py # Work context classification
│   │   ├── csv_loader.py        # Load Guide CSV data
│   │   ├── labels_loader.py     # Load NOC labels from parquet
│   │   ├── annex_builder.py     # Build NOC profile Annex for export
│   │   ├── semantic_checker.py  # Semantic similarity checking
│   │   ├── few_shot_examples.py # Few-shot examples for LLM styling
│   │   ├── style_constants.py   # Style generation configuration
│   │   └── __init__.py
│   ├── models/                   # Pydantic data models
│   │   ├── noc.py               # NOC domain models (NOCStatement, JDElementData)
│   │   ├── responses.py          # API response models (SearchResponse, ProfileResponse)
│   │   ├── allocation.py         # Allocation request/response models
│   │   ├── export_models.py      # Export request/response structures
│   │   ├── ai.py                # AI generation request/response models
│   │   ├── styled_content.py    # Styled statement models
│   │   ├── vocabulary_audit.py  # Vocabulary validation models
│   │   └── __init__.py
│   ├── matching/                 # Phase 15 - Classification engine
│   │   ├── allocator.py         # Main orchestrator (OccupationalGroupAllocator)
│   │   ├── classifier.py        # LLM classification with structured outputs
│   │   ├── confidence.py        # Multi-factor confidence scoring
│   │   ├── edge_cases.py        # Edge case detection (split duties, etc)
│   │   ├── models.py            # Allocation result models
│   │   ├── prompts.py           # LLM system/user prompts
│   │   ├── provenance_builder.py # Build TBS directive provenance maps
│   │   ├── shortlisting/
│   │   │   ├── __init__.py
│   │   │   ├── semantic_matcher.py   # Semantic similarity filtering
│   │   │   └── labels_matcher.py     # Label-based boosting
│   │   ├── evidence/
│   │   │   ├── __init__.py
│   │   │   ├── extractor.py     # Quote extraction from JD
│   │   │   └── provenance.py    # Evidence-to-provenance mapping
│   │   └── __init__.py
│   ├── storage/                  # Database and cache layer
│   │   ├── db_manager.py        # Database connection management
│   │   ├── repository.py        # Occupational group data access (ORM-like)
│   │   └── __init__.py
│   ├── vocabulary/               # NOC vocabulary indexing
│   │   ├── index.py             # VocabularyIndex (loads from parquet)
│   │   ├── validator.py         # VocabularyValidator (coverage checking)
│   │   ├── watcher.py           # File system watcher for hot-reload
│   │   └── __init__.py
│   ├── utils/                    # Shared utilities
│   │   ├── oasis_provenance.py  # OASIS source table URL builder
│   │   ├── selectors.py         # CSS/XPath selectors for parsing
│   │   └── __init__.py
│   ├── scrapers/                 # Deprecated (functionality moved to services/)
│   │   ├── http_client.py
│   │   ├── tbs_scraper.py
│   │   ├── tbs_parser.py
│   │   └── validation.py
│   ├── data/                     # Deprecated (functionality moved to services/)
│   │   └── (scraped data cached here)
│   └── cli/                      # Command-line tools
│       ├── __init__.py
│       └── refresh_occupational.py  # Prime occupational groups database
├── static/                       # Frontend assets
│   ├── js/
│   │   ├── main.js              # Application initialization, event handlers
│   │   ├── api.js               # API client wrapper (fetch)
│   │   ├── state.js             # Reactive state management (store pattern)
│   │   ├── accordion.js         # JD section collapse/expand
│   │   ├── sidebar.js           # Sidebar toggle and navigation
│   │   ├── selection.js         # Checkbox selection and persistence
│   │   ├── classify.js          # Classification UI and evidence highlighting
│   │   ├── export.js            # Export preview and download
│   │   ├── generate.js          # AI generation streaming display
│   │   ├── styling.js           # Statement styling workflow
│   │   ├── filters.js           # Result filtering and sorting
│   │   ├── profile_tabs.js      # Profile section tabbing
│   │   ├── search.js            # Search form handling (minimal)
│   │   └── storage.js           # localStorage wrapper utilities
│   └── css/
│       ├── main.css             # Core layout, typography, variables
│       ├── accordion.css        # Section accordion styles
│       ├── sidebar.css          # Sidebar styling
│       ├── skeleton.css         # Loading skeleton animations
│       ├── overview.css         # Overview section styling
│       ├── results-cards.css    # Search result card styling
│       ├── classify.css         # Classification result styling
│       ├── evidence.css         # Evidence highlighting styles
│       └── filters.css          # Filter and sort UI styles
├── templates/
│   ├── index.html               # Single-page application shell
│   └── export/
│       ├── jd_pdf.html          # PDF template (rendered by WeasyPrint)
│       └── jd_preview.html      # HTML preview template
├── tests/
│   ├── test_uat_screenshots.py  # User acceptance testing
│   └── uat_terminal.py          # UAT test runner
├── .planning/                    # Project documentation (GSD framework)
│   ├── config.json              # GSD configuration
│   ├── codebase/                # This analysis directory
│   ├── state/                   # Phase state tracking
│   └── phases/                  # Phase implementation plans
├── requirements.txt             # Python dependencies
├── .env.example                 # Example environment variables
├── .gitignore                   # Git ignore patterns
└── README.md                    # Project overview and quick start
```

## Directory Purposes

**src/:**
- Purpose: All application Python code
- Contains: Packages for routing, services, models, matching engine, storage, vocabulary
- Key files: `app.py` (entry point), `config.py` (constants)

**src/routes/:**
- Purpose: Flask HTTP route handlers
- Contains: API endpoints
- Key files: `api.py` (all endpoints)

**src/services/:**
- Purpose: Business logic and data transformation
- Contains: Scrapers, parsers, mappers, LLM clients, exporters, vocabulary loaders
- Key files: `scraper.py`, `mapper.py`, `export_service.py`, `llm_service.py`

**src/models/:**
- Purpose: Pydantic data validation and type safety
- Contains: Request/response models, domain models, data structures
- Key files: `allocation.py`, `noc.py`, `export_models.py`

**src/matching/:**
- Purpose: Classification and occupational group allocation
- Contains: Orchestration, shortlisting, LLM classification, confidence scoring, evidence extraction
- Key files: `allocator.py` (main entry point), `shortlisting/` (candidate filtering)

**src/storage/:**
- Purpose: Persistent storage and database access
- Contains: Connection management, repository pattern for data access
- Key files: `db_manager.py`, `repository.py`

**src/vocabulary/:**
- Purpose: NOC vocabulary indexing and validation
- Contains: Parquet file loading, term lookup, hot-reload file watching
- Key files: `index.py` (VocabularyIndex class)

**src/utils/:**
- Purpose: Shared utility functions
- Contains: Provenance URL builders, CSS selectors
- Key files: `oasis_provenance.py`

**static/js/:**
- Purpose: Frontend application code
- Contains: Module exports, event handlers, API calls, state management
- Key files: `main.js` (initialization), `api.js` (HTTP client), `state.js` (store)

**static/css/:**
- Purpose: Frontend styling
- Contains: Layout, typography, component styles
- Key files: `main.css` (core), feature-specific CSS files

**templates/:**
- Purpose: HTML templates
- Contains: Single-page app shell, export templates
- Key files: `index.html` (entry point for browser)

**tests/:**
- Purpose: User acceptance testing
- Contains: UAT test scripts and screenshot validation
- Key files: `test_uat_screenshots.py`, `uat_terminal.py`

## Key File Locations

**Entry Points:**

- `src/app.py`: Flask application factory and WSGI entry point
  - Initializes vocabulary index and file watcher
  - Registers API blueprint
  - Serves static files and index.html

- `templates/index.html`: Single-page application shell
  - Loads all JavaScript and CSS
  - Provides root DOM structure (header, stepper, main content, sidebar)

- `static/js/main.js`: JavaScript application initialization
  - Initializes modules in dependency order
  - Sets up event listeners for UI interactions
  - Manages view state and rendering

**Configuration:**

- `src/config.py`: Central configuration
  - OASIS_BASE_URL, OASIS_VERSION
  - OPENAI_API_KEY, OPENAI_MODEL
  - JOBFORGE_BRONZE_PATH (parquet files)
  - Flask SECRET_KEY

- `.env`: Runtime environment variables
  - OPENAI_API_KEY (required)
  - FLASK_ENV (development/production)
  - SECRET_KEY (Flask session encryption)

- `.env.example`: Template for .env

**Core Logic:**

- `src/routes/api.py`: All HTTP endpoints
  - /api/search: NOC search
  - /api/profile: Full NOC profile fetch
  - /api/generate: AI overview generation
  - /api/style: Statement styling
  - /api/allocate: Occupational group classification
  - /api/preview: Export preview rendering
  - /api/export/pdf: PDF download
  - /api/export/docx: Word download

- `src/services/mapper.py`: NOC → JD transformation
  - Converts scraped data into JD element structure
  - Classifies work context into effort/responsibility
  - Supplements with parquet-loaded data

- `src/matching/allocator.py`: Classification orchestration
  - Main entry point for occupational group allocation
  - Coordinates shortlisting, classification, confidence, evidence extraction

**Testing:**

- `tests/test_uat_screenshots.py`: Screenshot comparison tests
- `tests/uat_terminal.py`: Interactive UAT test runner

## Naming Conventions

**Files:**

- Python files: `snake_case.py` (e.g., `export_service.py`, `llm_service.py`)
  - Class names within: PascalCase (e.g., `ExportService`, `OASISScraper`)
- JavaScript files: `snake_case.js` (e.g., `main.js`, `api.js`)
- CSS files: `kebab-case.css` (e.g., `main.css`, `results-cards.css`)
- HTML files: `snake_case.html` (e.g., `index.html`, `jd_pdf.html`)

**Directories:**

- Python packages: `snake_case/` (e.g., `src/services/`, `src/matching/`)
- Frontend: `static/js/`, `static/css/`, `templates/`
- Data: `data/bronze/`, `data/silver/`, `data/gold/` (medallion layers)

**API Endpoints:**

- Route names: `/api/{resource}/{action}` (e.g., `/api/search`, `/api/export/pdf`)
- Query params: `snake_case` (e.g., `?q=`, `?type=`, `?code=`)
- Request/response bodies: `snake_case` (e.g., `position_title`, `key_activities`)

**HTML Elements:**

- IDs: `kebab-case` (e.g., `#search-input`, `#jd-sections`)
- Classes: `kebab-case` (e.g., `.pill-btn`, `.results-list`)
- Data attributes: `data-attribute` (e.g., `data-step`, `data-noc-code`)

**CSS Variables:**

- Colors: `--color-{name}` (e.g., `--color-primary`, `--color-error`)
- Spacing: `--spacing-{size}` (e.g., `--spacing-sm`, `--spacing-lg`)
- Typography: `--font-{property}` (e.g., `--font-base`, `--font-heading`)

**JavaScript Objects:**

- API client methods: camelCase (e.g., `api.search()`, `api.getProfile()`)
- Store methods: camelCase (e.g., `store.getState()`, `store.setState()`)
- Module functions: camelCase (e.g., `initSidebar()`, `renderResults()`)

**Pydantic Models:**

- Request models: `{Name}Request` (e.g., `AllocationRequest`, `ExportRequest`)
- Response models: `{Name}Response` (e.g., `SearchResponse`, `ProfileResponse`)
- Data models: `{Name}Data` or `{Name}` (e.g., `JDElementData`, `NOCStatement`)

## Where to Add New Code

**New Feature (Non-model, Non-route):**

- Primary code: `src/services/{feature_name}.py`
  - Define a class with public methods
  - Example: `src/services/new_service.py` with `class NewService: def do_thing(self): ...`

- Tests: `tests/test_{feature_name}.py`
  - Use pytest if adding unit tests
  - Current codebase uses UAT (screenshot tests) in `tests/`

- Register in app if needed: Update `src/app.py` initialization

**New API Endpoint:**

- Route: `src/routes/api.py`
  - Add function to `api_bp` blueprint
  - Define request model in `src/models/` if needed
  - Return response using Pydantic model serialization

- Response model: `src/models/{endpoint_name}.py`
  - Define with Pydantic BaseModel
  - Export from `src/models/__init__.py`

**New Component/Module:**

- Implementation: `src/matching/{component_name}.py`
  - Define main class
  - Example: `src/matching/new_matcher.py` with `class NewMatcher: def match(self): ...`

- Integrate into orchestrator: Update `src/matching/allocator.py`
  - Instantiate component in `__init__`
  - Call from `allocate()` method

**Frontend UI Feature:**

- JavaScript module: `static/js/{feature_name}.js`
  - Export initialization function (e.g., `function initFeature() { ... }`)
  - Keep module scope separate (use closures)

- CSS: `static/css/{feature_name}.css`
  - Define component-specific styles
  - Use CSS variables for consistency

- HTML structure: Update `templates/index.html`
  - Add markup in appropriate section
  - Use data attributes for JavaScript hooks

**Utilities:**

- Shared helpers: `src/utils/{category_name}.py`
  - Example: `src/utils/text_processing.py` with utility functions
  - Keep functions pure and testable

- Frontend helpers: `static/js/storage.js` or new module
  - Reusable across modules
  - Example: localStorage wrapper, formatting utilities

**Data Models:**

- New request/response type: `src/models/{entity_name}.py`
  - Define Pydantic BaseModel with validation
  - Export from `src/models/__init__.py`
  - Use in routes for automatic validation

## Special Directories

**data/:**
- Purpose: Stored scraped data (Bronze/Silver/Gold layers)
- Generated: Yes (created by scraper CLI)
- Committed: No (git-ignored)
- Location path: `C:/Users/Administrator/Dropbox/++ Results Kit/JobForge 2.0/data/bronze` (configured in config.py)

**.planning/:**
- Purpose: GSD framework documentation and phase tracking
- Generated: Partially (orchestrator creates files)
- Committed: Yes
- Contains: Architecture analysis, implementation plans, phase state

**static/:**
- Purpose: Frontend assets served by Flask
- Generated: No (hand-written)
- Committed: Yes
- Sub-directories: `js/`, `css/`, `images/`

**templates/:**
- Purpose: HTML templates rendered by Flask
- Generated: No (hand-written)
- Committed: Yes
- Entry point: `index.html` (SPA shell), `export/jd_pdf.html`, `export/jd_preview.html`

**tests/:**
- Purpose: Test automation
- Generated: No (hand-written)
- Committed: Yes
- Current type: UAT (screenshot-based testing)

---

*Structure analysis: 2026-03-04*
