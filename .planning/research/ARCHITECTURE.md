# Architecture Research: v1.1 Enhanced Data Display + Export

**Domain:** Enhancement to existing JD Builder Lite (Flask + Vanilla JS)
**Researched:** 2026-01-22
**Confidence:** HIGH (extending existing v1.0 architecture with well-understood patterns)

## Executive Summary

v1.1 adds enhanced data display features and DOCX export to the existing JD Builder Lite architecture. The integration involves: (1) new CSV data loading service for Open Canada guide.csv, (2) enriched response models with metadata fields, (3) frontend grid view component, and (4) parallel DOCX export route. All changes extend existing patterns without architectural restructuring. Build order follows data availability: CSV loader first, then backend enrichment, then frontend display, then export features.

## Current v1.0 Architecture (Baseline)

### Backend Structure (Flask + Service Layer)

```
Flask App (src/app.py)
    |
    v
Routes (src/routes/api.py)
    |
    +---> Services
    |     - scraper.py: OASIS HTTP client
    |     - parser.py: HTML -> structured data
    |     - mapper.py: NOC data -> JD elements
    |     - llm_service.py: OpenAI generation
    |     - export_service.py: Build export data
    |     - pdf_generator.py: WeasyPrint PDF
    |     - docx_generator.py: python-docx Word (v1.0)
    |
    +---> Models (Pydantic)
    |     - noc.py: SearchResult, NOCStatement, JDElementData
    |     - responses.py: ProfileResponse, SearchResponse
    |     - export_models.py: ExportRequest, ExportData
    |     - ai.py: GenerationMetadata
    |
    +---> Utils
          - selectors.py: CSS selectors for scraping
```

### Frontend Structure (Vanilla JS)

```
static/
    +-- js/
        - state.js: Store with localStorage persistence
        - api.js: Fetch wrapper for backend
        - search.js: Search UI logic
        - accordion.js: JD element tabs
        - selection.js: Statement checkbox logic
        - generate.js: AI overview generation
        - export.js: PDF/DOCX download
```

### Data Flow (v1.0)

```
User Search → /api/search → scraper → parser → SearchResponse
    |
    v
Select Profile → /api/profile → scraper → parser → mapper → ProfileResponse
    |                                                            - JD elements
    |                                                            - NOCStatements
    v
Select Statements → Frontend state.js → localStorage
    |
    v
Generate Overview → /api/generate → llm_service → SSE stream
    |
    v
Export PDF → /api/export/pdf → build_export_data → generate_pdf → BytesIO
```

## v1.1 Integration Points

### Backend Changes

| Component | Change Type | Description | Why |
|-----------|-------------|-------------|-----|
| **src/services/csv_loader.py** | NEW | Load and parse guide.csv from Open Canada | Provides category definitions, label descriptions, scale meanings |
| **src/services/enrichment_service.py** | NEW | Enrich NOCStatements with CSV metadata | Adds descriptions, proficiency levels, dimension names to statements |
| **src/models/noc.py** | MODIFY | Add fields to NOCStatement | Add: description, proficiency_level, scale_meaning, dimension |
| **src/models/responses.py** | MODIFY | Add profile metadata fields | Add: noc_hierarchy (TEER, broad category, major group), reference_attributes |
| **src/services/parser.py** | MODIFY | Extract Work Context dimensions | Parse dimension labels (Frequency, Duration, etc.) from HTML |
| **src/services/mapper.py** | MODIFY | Call enrichment service | Enrich statements after mapping, fix Effort/Responsibility filters |
| **src/routes/api.py** | MODIFY | /api/profile enrichment | Call enrichment before returning ProfileResponse |
| **src/routes/api.py** | VERIFY | /api/export/docx | Already exists in v1.0 - verify functionality |
| **src/services/export_service.py** | MODIFY | Include Annex in ExportData | Add reference_attributes section to export data |

### Frontend Changes

| Component | Change Type | Description | Why |
|-----------|-------------|-------------|-----|
| **static/js/grid-view.js** | NEW | Grid toggle component for search results | Display card vs table view with columns |
| **static/js/statement-display.js** | MODIFY | Render enriched statement metadata | Show descriptions, proficiency stars, scale meanings |
| **static/js/profile-header.js** | NEW | Profile overview component | Display NOC code, hierarchy, reference attributes |
| **static/css/grid.css** | NEW | Grid view styles | Table layout for search results |
| **static/css/statement-enhancements.css** | NEW | Enhanced statement display | Star ratings, dimension badges, descriptions |
| **templates/index.html** | MODIFY | Add grid toggle controls | Button to switch between card/table view |

### New Data Flows

#### CSV Data Loading (Startup)

```
App Initialization
    |
    v
csv_loader.load_guide()
    |
    +---> Read guide.csv from data/
    +---> Parse into lookup dictionaries:
          - category_definitions: {category_name: definition}
          - label_descriptions: {oasis_label: description}
          - scale_meanings: {scale_type: {level: meaning}}
    |
    v
Store in module-level cache (singleton pattern)
```

#### Enhanced Profile Response (Request Time)

```
/api/profile?code=21232
    |
    v
scraper.fetch_profile(code)
    |
    v
parser.parse_profile(html, code)
    |
    +---> Extract Work Context with dimensions
    |     Example: "Frequency of Decision Making — 5"
    |
    v
mapper.to_jd_elements(noc_data)
    |
    +---> Map NOC attributes to JD elements
    +---> Filter Work Context for Effort/Responsibility
    |
    v
enrichment_service.enrich_statements(jd_elements)
    |
    +---> For each NOCStatement:
    |     - Lookup label description from guide.csv
    |     - Extract proficiency level from text
    |     - Get scale meaning for level
    |     - Add dimension name (for Work Context)
    |
    v
ProfileResponse (enriched)
{
  "noc_code": "21232",
  "title": "Software developers",
  "noc_hierarchy": {
    "teer": "1",
    "broad_category": "Natural and applied sciences",
    "major_group": "21"
  },
  "key_activities": {
    "statements": [
      {
        "text": "Design and develop software",
        "source_attribute": "Main Duties",
        "source_url": "...",
        "description": "Core tasks performed",  // NEW
        "proficiency_level": null,
        "scale_meaning": null,
        "dimension": null
      }
    ]
  },
  "skills": {
    "statements": [
      {
        "text": "Programming — 5",
        "source_attribute": "Skills",
        "source_url": "...",
        "description": "Using logic and methods to develop solutions",  // NEW
        "proficiency_level": 5,  // NEW
        "scale_meaning": "5 - Highest Level",  // NEW
        "dimension": null
      }
    ]
  },
  "working_conditions": {
    "statements": [
      {
        "text": "Frequency of Decision Making — 5",
        "source_attribute": "Work Context",
        "source_url": "...",
        "description": "How often required to make decisions",  // NEW
        "proficiency_level": 5,  // NEW
        "scale_meaning": "5 - Every day, many times per day",  // NEW
        "dimension": "Frequency"  // NEW
      }
    ]
  },
  "reference_attributes": {  // NEW - for Annex
    "example_titles": ["Software Engineer", "Application Developer"],
    "interests": ["Investigative", "Conventional"],
    "personal_attributes": ["Analytical thinking", "Attention to detail"]
  },
  "metadata": { ... }
}
```

#### Frontend Enhanced Display

```
ProfileResponse received
    |
    v
Render profile header with NOC hierarchy
    |
    v
For each JD element tab:
    |
    +---> Display category definition at top (from response)
    |
    +---> For each statement:
          |
          +---> Show statement text
          +---> Show description below (if present)
          +---> Show proficiency stars (if level present)
          +---> Show scale meaning next to stars
          +---> Show dimension badge (if present)
```

#### Grid View Display

```
Search results received
    |
    v
User clicks grid toggle
    |
    +---> Switch display mode: card → table or table → card
    |
    v
Table mode renders:
    |
    +---> Columns: NOC Code | Title | Broad Category | Training/Education | Lead Statement
    +---> Data from search results + profile preview
```

#### Annex Export

```
Export request (PDF or DOCX)
    |
    v
build_export_data(request)
    |
    +---> Include reference_attributes in ExportData
    |
    v
PDF/DOCX generator
    |
    +---> Render main JD sections
    +---> Add page break
    +---> Add "Annex: Reference Attributes" section
          - Example Titles
          - Interests
          - Personal Attributes
          - Career Mobility
```

## New Components Needed

### 1. CSV Loader Service (src/services/csv_loader.py)

**Purpose:** Load and parse guide.csv at application startup

**Responsibilities:**
- Read CSV from data/ directory
- Parse into lookup dictionaries
- Provide query methods for enrichment

**Interface:**
```python
class CSVLoader:
    def load_guide(self, file_path: str) -> None
    def get_category_definition(self, category: str) -> Optional[str]
    def get_label_description(self, label: str) -> Optional[str]
    def get_scale_meaning(self, scale_type: str, level: int) -> Optional[str]
```

**Singleton:** Module-level instance (like scraper, mapper)

### 2. Enrichment Service (src/services/enrichment_service.py)

**Purpose:** Enrich NOCStatements with CSV metadata

**Responsibilities:**
- Match statement text to CSV labels
- Extract proficiency levels from text (regex)
- Lookup descriptions and scale meanings
- Add dimension names for Work Context

**Interface:**
```python
class EnrichmentService:
    def __init__(self, csv_loader: CSVLoader)
    def enrich_statement(self, statement: NOCStatement, category: str) -> NOCStatement
    def enrich_jd_elements(self, jd_data: Dict[str, JDElementData]) -> Dict[str, JDElementData]
```

### 3. Grid View Component (static/js/grid-view.js)

**Purpose:** Toggle search results between card and table view

**Responsibilities:**
- Render table HTML from search results
- Toggle visibility between card/table containers
- Persist view preference in localStorage

**Interface:**
```javascript
function initGridView()
function toggleView(mode: 'card' | 'table')
function renderTable(results: SearchResult[])
```

### 4. Enhanced Statement Display (static/js/statement-display.js)

**Purpose:** Render enriched statement metadata

**Responsibilities:**
- Show description below statement text
- Render star rating from proficiency level
- Display scale meaning next to stars
- Show dimension badge for Work Context

**Interface:**
```javascript
function renderStatement(statement: NOCStatement, container: HTMLElement)
function renderStars(level: number): string
function renderDimension(dimension: string): string
```

### 5. Profile Header Component (static/js/profile-header.js)

**Purpose:** Display NOC code and hierarchy prominently

**Responsibilities:**
- Render NOC code below title
- Show TEER/broad category/major group
- Display reference attributes section

**Interface:**
```javascript
function renderProfileHeader(profile: ProfileResponse, container: HTMLElement)
function renderHierarchy(hierarchy: NOCHierarchy): string
function renderReferenceAttributes(attrs: ReferenceAttributes): string
```

## Suggested Build Order

Build order follows data availability and dependency chain:

### Phase 1: CSV Infrastructure (Build First)

**Components:** csv_loader.py, enrichment_service.py, updated models

**Why first:**
- Foundation for all enhancements
- Can test independently with sample data
- No frontend dependencies

**Deliverables:**
- CSV data loaded at startup
- Enrichment service tests passing
- NOCStatement model has new fields

**Testing:** Unit tests with sample CSV data

### Phase 2: Backend Enrichment (Build Second)

**Components:** Modified mapper.py, modified api.py /api/profile route

**Why second:**
- Depends on CSV infrastructure (Phase 1)
- Frontend needs enriched data to display
- Can test with curl/Postman

**Deliverables:**
- /api/profile returns enriched statements
- Work Context filtering fixed (Effort/Responsibility)
- Profile includes NOC hierarchy and reference attributes

**Testing:** API tests verify enriched response structure

### Phase 3: Frontend Enhanced Display (Build Third)

**Components:** statement-display.js, statement-enhancements.css, profile-header.js

**Why third:**
- Depends on enriched API responses (Phase 2)
- Core feature - users need to see enhancements
- Can iterate on styling with real data

**Deliverables:**
- Statements show descriptions, stars, scale meanings
- Profile displays NOC hierarchy prominently
- Category definitions visible at top of tabs

**Testing:** Manual verification with multiple profiles

### Phase 4: Grid View (Build Fourth)

**Components:** grid-view.js, grid.css, modified search.js

**Why fourth:**
- Independent of enrichment features
- Can build in parallel with Phase 3 if needed
- Enhancement to search, not core data display

**Deliverables:**
- Grid toggle button functional
- Table view displays correctly
- View preference persists

**Testing:** Test with various search results

### Phase 5: Annex Export (Build Last)

**Components:** Modified export_service.py, modified pdf_generator.py, modified docx_generator.py

**Why last:**
- Depends on reference_attributes from Phase 2
- Output feature, not core functionality
- Easiest to test once everything else works

**Deliverables:**
- Annex section in PDF exports
- Annex section in DOCX exports
- Reference attributes formatted correctly

**Testing:** Export multiple profiles, verify Annex content

### Dependency Graph

```
Phase 1: CSV Infrastructure
    |
    v
Phase 2: Backend Enrichment
    |
    +------------------------+
    |                        |
    v                        v
Phase 3: Enhanced Display   Phase 4: Grid View
    |                        |
    +------------------------+
    |
    v
Phase 5: Annex Export
```

**Critical Path:** Phase 1 → Phase 2 → Phase 3 → Phase 5

**Parallel Opportunity:** Phase 4 (Grid View) can be built in parallel with Phase 3 if resources allow.

## Integration Patterns

### Pattern 1: CSV Singleton Loader

**Problem:** Multiple services need CSV data, but loading is expensive

**Solution:** Module-level singleton loaded once at startup

```python
# csv_loader.py
class CSVLoader:
    def __init__(self):
        self._guide_data = None

    def load_guide(self, path):
        if self._guide_data is None:
            self._guide_data = self._parse_csv(path)

# Module-level instance
csv_loader = CSVLoader()

# app.py
from src.services.csv_loader import csv_loader

@app.before_first_request
def load_csv_data():
    csv_loader.load_guide('data/guide.csv')
```

**Why:** Matches existing pattern (scraper, mapper singletons)

### Pattern 2: Optional Enrichment

**Problem:** Not all statements have CSV metadata (e.g., Main Duties have no proficiency levels)

**Solution:** Enrichment adds fields as Optional, frontend checks before displaying

```python
# models/noc.py
class NOCStatement(BaseModel):
    text: str
    source_attribute: str
    source_url: str
    description: Optional[str] = None  # May not exist
    proficiency_level: Optional[int] = None  # May not exist
    scale_meaning: Optional[str] = None
    dimension: Optional[str] = None
```

```javascript
// Frontend
if (statement.proficiency_level) {
    stmtElement.innerHTML += renderStars(statement.proficiency_level);
}
```

**Why:** Graceful degradation - works with partial data

### Pattern 3: Incremental Rendering

**Problem:** Grid view needs more data than simple search returns

**Solution:** Table columns show what's available, fetch details on demand if needed

```javascript
// Initial: Show NOC code, title from search results
renderBasicTable(searchResults);

// Optional: Fetch profile previews for additional columns
async function enhanceTableWithPreviews(results) {
    for (const result of results) {
        const preview = await fetchProfilePreview(result.noc_code);
        updateTableRow(result.noc_code, preview);
    }
}
```

**Why:** Progressive enhancement - fast initial load, richer data if needed

### Pattern 4: Backward Compatible Models

**Problem:** Enrichment adds new fields, but v1.0 exports might not have them

**Solution:** All new fields are Optional with defaults

```python
class NOCStatement(BaseModel):
    # v1.0 fields (required)
    text: str
    source_attribute: str
    source_url: str

    # v1.1 fields (optional, backward compatible)
    description: Optional[str] = None
    proficiency_level: Optional[int] = None
    scale_meaning: Optional[str] = None
    dimension: Optional[str] = None
```

**Why:** Existing v1.0 data structures still valid, no migration needed

## Anti-Patterns to Avoid

### Anti-Pattern 1: Loading CSV on Every Request

**What:** Reading guide.csv in enrichment_service for each /api/profile call

**Why bad:** I/O bottleneck, slow response times

**Instead:** Load once at startup, cache in memory

### Anti-Pattern 2: Enrichment in Frontend

**What:** Sending raw CSV data to frontend, matching labels in JavaScript

**Why bad:** Large payload, duplicated logic, CSV exposure

**Instead:** Enrich in backend, send enriched JSON

### Anti-Pattern 3: Separate Enrichment Endpoint

**What:** /api/profile returns basic data, /api/enrich adds metadata

**Why bad:** Two round trips, complex state management

**Instead:** /api/profile returns fully enriched data in one call

### Anti-Pattern 4: Hardcoded Scale Meanings

**What:** Mapping levels to meanings in code: `{1: "Lowest", 5: "Highest"}`

**Why bad:** Incorrect for different scales (Frequency uses different meanings)

**Instead:** Load from CSV, respect per-scale definitions

### Anti-Pattern 5: Grid View as Separate Page

**What:** /search shows cards, /search/grid shows table

**Why bad:** State duplication, back button confusion

**Instead:** Single page, toggle component switches display mode

## Data Model Extensions

### Extended NOCStatement

```python
class NOCStatement(BaseModel):
    """v1.1: Extended with CSV enrichment"""
    # v1.0 fields
    text: str
    source_attribute: str  # "Main Duties", "Skills", etc.
    source_url: str

    # v1.1 enrichment fields
    description: Optional[str] = None  # From guide.csv
    proficiency_level: Optional[int] = None  # Extracted from text
    scale_meaning: Optional[str] = None  # From guide.csv
    dimension: Optional[str] = None  # "Frequency", "Duration", etc.
```

### Extended ProfileResponse

```python
class ProfileResponse(BaseModel):
    """v1.1: Extended with hierarchy and reference attributes"""
    # v1.0 fields
    noc_code: str
    title: str
    key_activities: JDElementData
    skills: JDElementData
    effort: JDElementData
    responsibility: JDElementData
    working_conditions: JDElementData
    metadata: SourceMetadata

    # v1.1 fields
    noc_hierarchy: Optional[NOCHierarchy] = None
    reference_attributes: Optional[ReferenceAttributes] = None

class NOCHierarchy(BaseModel):
    teer: str  # Training, Education, Experience, Responsibilities
    broad_category: str
    major_group: str

class ReferenceAttributes(BaseModel):
    """Annex-bound attributes"""
    example_titles: List[str] = []
    interests: List[str] = []
    personal_attributes: List[str] = []
    career_mobility: Optional[str] = None
```

### Extended ExportData

```python
class ExportData(BaseModel):
    """v1.1: Extended with Annex section"""
    # v1.0 fields
    noc_code: str
    job_title: str
    general_overview: Optional[str]
    jd_elements: List[JDElementExport]
    manager_selections: List[SelectionMetadata]
    ai_metadata: Optional[AIMetadata]
    source_metadata: SourceMetadataExport
    compliance_sections: List[ComplianceSection]
    generated_at: datetime

    # v1.1 fields
    reference_attributes: Optional[ReferenceAttributes] = None
```

## Technology Verification

### Existing Stack (No Changes)

| Component | Technology | Status | Notes |
|-----------|-----------|--------|-------|
| Backend | Flask 3.1.0 | ✓ Continues | No version change |
| HTML Parser | BeautifulSoup + lxml | ✓ Continues | Handles Work Context dimension parsing |
| PDF | WeasyPrint | ✓ Continues | Can render Annex section |
| DOCX | python-docx | ✓ Continues | Already implemented in v1.0 |
| Frontend | Vanilla JS | ✓ Continues | Grid view uses plain JS/CSS |
| State | localStorage | ✓ Continues | Persist grid view preference |

### New Dependencies (v1.1)

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| CSV parsing | Python csv module | Built-in | Parse guide.csv (standard library) |

**No new external dependencies required.** All v1.1 features use existing stack.

## File Structure Impact

### New Files

```
jd-builder-lite/
|
+-- data/                      # NEW directory
|   +-- guide.csv              # Open Canada CSV
|
+-- src/services/
|   +-- csv_loader.py          # NEW
|   +-- enrichment_service.py  # NEW
|
+-- static/js/
|   +-- grid-view.js           # NEW
|   +-- statement-display.js   # NEW (refactored from existing)
|   +-- profile-header.js      # NEW
|
+-- static/css/
    +-- grid.css               # NEW
    +-- statement-enhancements.css  # NEW
```

### Modified Files

```
src/models/noc.py              # Add fields to NOCStatement
src/models/responses.py        # Add NOCHierarchy, ReferenceAttributes
src/services/parser.py         # Extract Work Context dimensions
src/services/mapper.py         # Call enrichment, fix filters
src/routes/api.py              # Enrich in /api/profile
src/services/export_service.py # Include reference_attributes
src/services/pdf_generator.py  # Render Annex section
src/services/docx_generator.py # Render Annex section
static/js/search.js            # Grid view integration
static/js/accordion.js         # Render enriched statements
templates/index.html           # Grid toggle button
```

**Modification Risk:** LOW - all changes extend existing patterns without breaking v1.0 functionality

## Testing Strategy

### Unit Tests (Backend)

```python
# test_csv_loader.py
def test_load_guide()
def test_get_category_definition()
def test_get_scale_meaning()

# test_enrichment.py
def test_enrich_statement_with_proficiency()
def test_enrich_work_context_with_dimension()
def test_enrich_missing_csv_data()

# test_parser.py (extended)
def test_extract_work_context_dimension()
```

### Integration Tests (API)

```bash
# Profile returns enriched data
curl localhost:5000/api/profile?code=21232
# Verify: statements have description, proficiency_level, scale_meaning

# Export includes Annex
curl -X POST localhost:5000/api/export/pdf -d '{...}'
# Verify: PDF contains "Annex: Reference Attributes"
```

### Manual Testing (Frontend)

- Search results grid toggle
- Statement display with stars and descriptions
- Profile header shows NOC hierarchy
- Category definitions visible at tab tops
- Export Annex in PDF and DOCX

## Performance Considerations

| Operation | v1.0 Baseline | v1.1 Impact | Mitigation |
|-----------|---------------|-------------|------------|
| /api/profile | ~2-3s (scraping) | +50-100ms (enrichment) | Acceptable - enrichment is in-memory lookups |
| CSV loading | N/A | ~200ms (startup) | One-time cost, not per-request |
| Grid view rendering | N/A | ~10ms (100 results) | Vanilla JS, no framework overhead |
| Export | ~500ms (PDF) | +50ms (Annex) | Negligible - Annex is small section |

**Overall Impact:** Minimal - enrichment adds <5% to request time

## Rollback Plan

If v1.1 issues occur, rollback is straightforward:

1. **Code rollback:** Git revert to v1.0 tag
2. **Data rollback:** Remove data/ directory (CSV)
3. **Frontend rollback:** Remove grid-view.js, statement-enhancements.css

**Risk:** LOW - all v1.1 features are additive, not replacing v1.0 functionality

## Sources

**High Confidence Sources:**

- Existing v1.0 codebase examination (src/routes/api.py, src/services/*, src/models/*)
- Open Canada NOC Dataset: [https://open.canada.ca/data/en/dataset/eeb3e442-9f19-4d12-8b38-c488fe4f6e5e](https://open.canada.ca/data/en/dataset/eeb3e442-9f19-4d12-8b38-c488fe4f6e5e)
- Flask documentation (patterns already used in v1.0)
- Python csv module (standard library, well-documented)

**Medium Confidence Sources:**

- v1.1 requirements from PROJECT.md (SRCH-04 through OUT-07)

**Architectural Patterns Confidence:**

- CSV singleton pattern: HIGH (matches existing scraper/mapper pattern)
- Optional enrichment: HIGH (standard Pydantic pattern)
- Grid view component: HIGH (vanilla JS, no framework complexity)
- Annex export: HIGH (extends existing export_service pattern)

---

*Architecture research complete. Ready for roadmap phase structure planning.*
