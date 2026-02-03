# Architecture: Style-Enhanced JD Generation

**Domain:** Style-enhanced writing for job descriptions constrained to NOC vocabulary
**Researched:** 2026-02-03
**Confidence:** HIGH

## Executive Summary

Style-enhanced JD generation integrates cleanly with the existing Flask + OpenAI architecture. The current system already has the necessary extension points:

1. **llm_service.py** handles all OpenAI interactions with clear patterns for new generation functions
2. **labels_loader.py** loads parquet data and provides caching patterns for vocabulary indexing
3. **mapper.py** transforms data through enrichment pipelines that can accommodate style variants
4. **api.py** demonstrates SSE streaming patterns for async generation

The architecture adds three new service modules and extends the frontend with dual-display (authoritative + styled) without breaking existing data flows.

## Current Architecture Overview

```
                                    CURRENT SYSTEM (v2.0)
+-----------------------------------------------------------------------------+
|                                                                             |
|   FRONTEND (vanilla JS)                      BACKEND (Flask)                |
|   ========================                   ================               |
|                                                                             |
|   search.js -----> /api/search -----> scraper.py (OASIS HTTP)              |
|                                              |                              |
|                                              v                              |
|   profile_tabs.js -> /api/profile --> parser.py (BeautifulSoup)            |
|                                              |                              |
|                                              v                              |
|                                       mapper.py (NOC -> JD Elements)       |
|                                              |                              |
|                                              +<-- enrichment_service.py    |
|                                              +<-- labels_loader.py         |
|                                              |     (parquet data)          |
|                                              v                              |
|   generate.js ---> /api/generate --> llm_service.py (OpenAI)              |
|        |                                     |                              |
|        |           SSE stream <--------------+                              |
|        v                                                                    |
|   export.js -----> /api/export/pdf --> export_service.py                  |
|                                              |                              |
|                                              v                              |
|                                       pdf_generator.py (WeasyPrint)        |
|                                                                             |
+-----------------------------------------------------------------------------+
```

## Integration Points Identified

### 1. llm_service.py (Line 1-261)

**Current Functions:**
- `generate_stream()` - SSE streaming for overview generation (temp 0.7)
- `select_occupation_icon()` - Deterministic icon selection (temp 0)
- `generate_occupation_description()` - Short description (temp 0.3)

**Integration Pattern:**
```python
# NEW FUNCTION: Style-constrained sentence generation
def generate_styled_sentence(
    authoritative_text: str,
    style_profile: StyleProfile,
    vocabulary_constraints: VocabularyIndex
) -> str:
    """Generate styled variant constrained to NOC vocabulary."""
```

Temperature should be 0.7-1.0 for stylistic variation while maintaining vocabulary constraints in the prompt.

### 2. labels_loader.py (Line 1-571)

**Current Pattern:**
- Singleton `LabelsLoader` class with lazy loading
- Parquet file loading with pandas
- In-memory caching by NOC code
- Method pattern: `_load_X()` + `get_X(noc_code)`

**Integration Pattern:**
```python
# EXTENDS LabelsLoader pattern
class VocabularyIndex:
    """Load and index vocabulary from parquet files."""

    # Same lazy load pattern as LabelsLoader
    ABILITIES_FILE = GOLD_DATA_PATH / "oasis_abilities.parquet"
    SKILLS_FILE = GOLD_DATA_PATH / "oasis_skills.parquet"
    KNOWLEDGE_FILE = GOLD_DATA_PATH / "oasis_knowledges.parquet"
    WORK_ACTIVITIES_FILE = GOLD_DATA_PATH / "oasis_workactivities.parquet"

    def get_domain_vocabulary(self, noc_code: str) -> List[str]:
        """Get all valid terms for a NOC code."""
```

### 3. mapper.py (Line 1-443)

**Current Pattern:**
- `to_jd_elements()` transforms parsed NOC data
- Creates `EnrichedNOCStatement` objects with metadata
- Calls `enrichment_service` for lookups
- Returns dict matching `ProfileResponse` structure

**Integration Pattern:**
```python
# EXTEND return structure (backward compatible)
return {
    'noc_code': noc_code,
    'title': noc_data['title'],
    # ... existing fields ...

    # NEW: Style variants (None until generated)
    'style_variants': None,  # Populated by style_service when requested
}
```

### 4. api.py (Line 1-499)

**Current Patterns:**
- POST endpoints for generation (`/api/generate`, `/api/occupation-icon`)
- SSE streaming response pattern
- Session storage for metadata provenance
- JSON request/response with Pydantic validation

**Integration Pattern:**
```python
# NEW ENDPOINT
@api_bp.route('/generate-styled', methods=['POST'])
def generate_styled():
    """Generate styled sentence variants for selected statements.

    Expects JSON body:
    {
        "statements": [{"id": "...", "text": "...", "source_attribute": "..."}],
        "style_profile_id": "professional-formal",
        "noc_code": "21232.00"
    }

    Returns:
    {
        "variants": [
            {
                "original_id": "key_activities-0",
                "original_text": "...",
                "styled_text": "...",
                "vocabulary_compliance": 0.95,
                "style_confidence": 0.87
            }
        ]
    }
    """
```

## Recommended Architecture

```
                         v3.0 STYLE-ENHANCED ARCHITECTURE
+-----------------------------------------------------------------------------+
|                                                                             |
|   NEW COMPONENTS (src/services/)                                            |
|   ==============================                                            |
|                                                                             |
|   +-------------------+    +-------------------+    +-------------------+   |
|   | style_analyzer.py |    | vocabulary_index.py|   | style_generator.py |  |
|   +-------------------+    +-------------------+    +-------------------+   |
|   | parse_example_jds |    | load parquet vocab |   | constrained_gen   |  |
|   | extract_patterns  |    | build term index   |   | apply_style_rules |  |
|   | build_style_prof  |    | validate_terms     |   | score_compliance  |  |
|   +-------------------+    +-------------------+    +-------------------+   |
|            |                        |                        |              |
|            +------------------------+------------------------+              |
|                                     |                                       |
|                                     v                                       |
|                          +-----------------------+                          |
|                          | style_service.py      |                          |
|                          +-----------------------+                          |
|                          | Orchestrates style    |                          |
|                          | generation pipeline   |                          |
|                          +-----------------------+                          |
|                                     |                                       |
|                                     v                                       |
|   INTEGRATION                                                               |
|   ===========                                                               |
|                                                                             |
|   api.py                    llm_service.py                                 |
|   +--------------------+    +-----------------------+                       |
|   | /api/generate-styled    | generate_styled_text  |                      |
|   | /api/style-profiles     | validate_vocabulary   |                      |
|   | /api/vocabulary-check   |                       |                      |
|   +--------------------+    +-----------------------+                       |
|                                                                             |
|   FRONTEND EXTENSION                                                        |
|   ==================                                                        |
|                                                                             |
|   profile_tabs.js (extended)                                               |
|   +-----------------------------------------------------------------+      |
|   | Dual display: [Authoritative NOC] | [Styled Variant]            |      |
|   | Toggle: "Show styled" checkbox                                   |      |
|   | Visual distinction: border color, badge                          |      |
|   +-----------------------------------------------------------------+      |
|                                                                             |
+-----------------------------------------------------------------------------+
```

## New Components Specification

### 1. style_analyzer.py

**Purpose:** Parse example JDs (PDF/DOCX) to extract writing style patterns

**Dependencies:**
- `pdfplumber` or `PyPDF2` for PDF parsing
- `python-docx` for DOCX parsing (already installed)
- OpenAI for pattern extraction

**Class Design:**
```python
class StyleAnalyzer:
    """Extract writing style patterns from example JDs."""

    def __init__(self, llm_client: OpenAI):
        self._llm = llm_client
        self._pattern_cache = {}

    def parse_document(self, file_path: Path) -> ParsedDocument:
        """Extract text from PDF or DOCX."""

    def extract_style_patterns(self, texts: List[str]) -> StyleProfile:
        """Use LLM to identify writing patterns:
        - Sentence structure (active/passive voice ratios)
        - Average sentence length
        - Vocabulary complexity level
        - Common phrase patterns
        - Verb tense preferences
        """

    def build_style_profile(self, documents: List[Path]) -> StyleProfile:
        """Aggregate patterns from multiple documents."""
```

**StyleProfile Model:**
```python
class StyleProfile(BaseModel):
    id: str
    name: str
    patterns: Dict[str, Any]  # Extracted patterns
    voice: str  # "active" | "passive" | "mixed"
    avg_sentence_length: int
    vocabulary_level: str  # "simple" | "professional" | "technical"
    phrase_templates: List[str]
    source_documents: List[str]
    created_at: datetime
```

### 2. vocabulary_index.py

**Purpose:** Build searchable index from NOC/JobForge parquet files

**Dependencies:**
- `pandas` (already installed)
- Optional: `rapidfuzz` for fuzzy matching

**Class Design:**
```python
class VocabularyIndex:
    """Index NOC vocabulary for constrained generation."""

    # Extends LabelsLoader pattern
    GOLD_DATA_PATH = Path(r"C:\...\JobForge 2.0\data\gold")

    def __init__(self):
        self._abilities_df = None
        self._skills_df = None
        self._knowledge_df = None
        self._work_activities_df = None
        self._full_index = None  # Combined searchable index

    def build_index(self) -> None:
        """Load all parquet files and build unified term index."""

    def get_valid_terms(self, noc_code: str, category: str = None) -> Set[str]:
        """Get all valid vocabulary terms for a NOC code."""

    def validate_text(self, text: str, noc_code: str) -> ValidationResult:
        """Check if text uses valid NOC vocabulary.

        Returns:
            ValidationResult with:
            - compliance_score: float (0-1)
            - valid_terms: List[str]
            - invalid_terms: List[str]
            - suggestions: Dict[str, List[str]]  # invalid -> valid alternatives
        """

    def suggest_replacements(self, invalid_term: str, noc_code: str) -> List[str]:
        """Suggest valid NOC terms for an invalid word."""
```

### 3. style_generator.py

**Purpose:** Generate styled text constrained to NOC vocabulary

**Dependencies:**
- `openai` (already installed)
- `vocabulary_index.py`

**Class Design:**
```python
class StyleGenerator:
    """Generate vocabulary-constrained styled text."""

    def __init__(
        self,
        llm_client: OpenAI,
        vocab_index: VocabularyIndex
    ):
        self._llm = llm_client
        self._vocab = vocab_index

    def generate_styled_sentence(
        self,
        authoritative_text: str,
        style_profile: StyleProfile,
        noc_code: str,
        max_retries: int = 3
    ) -> StyledSentence:
        """Generate styled variant constrained to NOC vocabulary.

        Prompt structure:
        1. System: Style rules from profile
        2. User: Original text + vocabulary constraints
        3. Constraint: ONLY use these terms: [valid_terms]

        Returns:
            StyledSentence with:
            - styled_text: str
            - vocabulary_compliance: float
            - style_confidence: float
            - retries_used: int
        """

    def _build_constraint_prompt(
        self,
        original: str,
        style: StyleProfile,
        valid_terms: Set[str]
    ) -> str:
        """Build prompt with vocabulary constraints."""

    def _validate_and_retry(
        self,
        generated: str,
        noc_code: str,
        attempt: int
    ) -> Tuple[str, float]:
        """Validate output, retry if non-compliant."""
```

### 4. style_service.py (Orchestrator)

**Purpose:** Coordinate style analysis, indexing, and generation

**Class Design:**
```python
class StyleService:
    """Orchestrates style-enhanced generation pipeline."""

    def __init__(self):
        self._analyzer = StyleAnalyzer(client)
        self._vocab = VocabularyIndex()
        self._generator = StyleGenerator(client, self._vocab)
        self._profiles: Dict[str, StyleProfile] = {}

    def load_style_profile(self, profile_id: str) -> StyleProfile:
        """Load or return cached style profile."""

    def create_style_profile(
        self,
        name: str,
        document_paths: List[Path]
    ) -> StyleProfile:
        """Create new profile from example documents."""

    def generate_variants(
        self,
        statements: List[StatementInput],
        profile_id: str,
        noc_code: str
    ) -> List[StyledVariant]:
        """Generate styled variants for multiple statements."""

    def get_vocabulary_stats(self, noc_code: str) -> VocabularyStats:
        """Get vocabulary statistics for a NOC code."""

# Module singleton
style_service = StyleService()
```

## Data Flow Changes

### Current Flow (unchanged)
```
User selects statements
        |
        v
/api/generate (POST)
        |
        v
llm_service.generate_stream()
        |
        v
SSE stream -> overview_textarea
```

### New Flow (additive)
```
User enables "Style Enhancement"
        |
        v
/api/generate-styled (POST)
        |
        +---> style_service.generate_variants()
        |           |
        |           +---> vocab_index.get_valid_terms()
        |           |
        |           +---> style_generator.generate_styled_sentence()
        |           |
        |           +---> vocab_index.validate_text()
        |
        v
JSON response with variants
        |
        v
UI displays dual view:
[Authoritative] | [Styled]
```

## API Endpoints

### POST /api/generate-styled

**Request:**
```json
{
    "statements": [
        {
            "id": "key_activities-0",
            "text": "Coordinate activities with other engineers and technical personnel",
            "source_attribute": "Work Activities",
            "jd_element": "key_activities"
        }
    ],
    "style_profile_id": "professional-formal",
    "noc_code": "21232.00"
}
```

**Response:**
```json
{
    "variants": [
        {
            "original_id": "key_activities-0",
            "original_text": "Coordinate activities with other engineers and technical personnel",
            "styled_text": "Collaborate with engineering teams and technical specialists to align project activities",
            "vocabulary_compliance": 0.98,
            "style_confidence": 0.91,
            "invalid_terms": [],
            "generation_metadata": {
                "model": "gpt-4o",
                "temperature": 0.8,
                "retries": 0
            }
        }
    ],
    "profile_used": "professional-formal",
    "noc_vocabulary_size": 847
}
```

### GET /api/style-profiles

**Response:**
```json
{
    "profiles": [
        {
            "id": "professional-formal",
            "name": "Professional Formal",
            "source_document_count": 15,
            "created_at": "2026-01-15T10:30:00Z"
        },
        {
            "id": "concise-active",
            "name": "Concise Active Voice",
            "source_document_count": 8,
            "created_at": "2026-01-20T14:00:00Z"
        }
    ]
}
```

### POST /api/vocabulary-check

**Request:**
```json
{
    "text": "Manage software development lifecycle using agile methodologies",
    "noc_code": "21232.00"
}
```

**Response:**
```json
{
    "compliance_score": 0.85,
    "valid_terms": ["software", "development", "manage"],
    "invalid_terms": ["agile", "methodologies"],
    "suggestions": {
        "agile": ["iterative", "adaptive"],
        "methodologies": ["methods", "approaches", "practices"]
    }
}
```

## Frontend Changes

### profile_tabs.js Extension

```javascript
// NEW: Style toggle in statement display
const renderStatementWithStyle = (statement, variant) => {
    return `
        <li class="statement ${variant ? 'statement--has-variant' : ''}">
            <div class="statement__authoritative">
                <input type="checkbox" class="statement__checkbox" />
                <span class="statement__text">${statement.text}</span>
                <span class="statement__provenance">${statement.source_attribute}</span>
            </div>
            ${variant ? `
                <div class="statement__styled">
                    <span class="statement__styled-badge">Styled</span>
                    <span class="statement__styled-text">${variant.styled_text}</span>
                    <span class="statement__compliance"
                          title="Vocabulary compliance: ${(variant.vocabulary_compliance * 100).toFixed(0)}%">
                        ${renderComplianceIndicator(variant.vocabulary_compliance)}
                    </span>
                </div>
            ` : ''}
        </li>
    `;
};
```

### New CSS Classes

```css
/* Statement dual display */
.statement--has-variant {
    border-left: 3px solid var(--styled-accent);
}

.statement__styled {
    margin-left: 2rem;
    padding: 0.5rem;
    background: var(--styled-bg);
    border-radius: 4px;
}

.statement__styled-badge {
    font-size: 0.75rem;
    background: var(--styled-accent);
    color: white;
    padding: 0.125rem 0.5rem;
    border-radius: 2px;
}

.statement__compliance {
    font-size: 0.75rem;
    color: var(--muted-text);
}
```

## Suggested Build Order

Based on dependency analysis:

### Phase 1: Vocabulary Foundation
1. `vocabulary_index.py` - Load parquet, build term index
2. Unit tests for vocabulary validation
3. `/api/vocabulary-check` endpoint

**Rationale:** Independent of style analysis, provides testable foundation.

### Phase 2: Style Analysis
4. `style_analyzer.py` - PDF/DOCX parsing
5. StyleProfile model and storage
6. `/api/style-profiles` endpoint

**Rationale:** Document parsing is independent of generation.

### Phase 3: Constrained Generation
7. `style_generator.py` - LLM with constraints
8. Retry logic for vocabulary compliance
9. `/api/generate-styled` endpoint

**Rationale:** Requires both vocabulary and style components.

### Phase 4: Integration
10. `style_service.py` - Orchestration
11. Frontend dual-display UI
12. Export with styled variants

**Rationale:** Ties everything together.

## Patterns to Follow

### Pattern 1: Singleton Service (from labels_loader.py)
```python
class StyleService:
    # ... class implementation ...

# Module-level singleton
style_service = StyleService()
```
**Use:** All new services follow this pattern for easy import.

### Pattern 2: Lazy Loading with Cache (from labels_loader.py)
```python
def _load_vocabulary(self) -> bool:
    if self._vocab_df is not None:
        return True
    # ... load logic ...

def get_terms(self, noc_code: str) -> List[str]:
    if noc_code in self._cache:
        return self._cache[noc_code]
    if not self._load_vocabulary():
        return []
    # ... query and cache ...
```
**Use:** All data loading follows lazy-load-then-cache pattern.

### Pattern 3: Pydantic Models (from models/ai.py)
```python
class StyledVariant(BaseModel):
    original_id: str
    original_text: str
    styled_text: str
    vocabulary_compliance: float
    style_confidence: float

    model_config = ConfigDict(from_attributes=True)
```
**Use:** All API request/response models use Pydantic.

### Pattern 4: Temperature Conventions (from llm_service.py)
```python
# Deterministic selection: temp = 0
# Controlled creativity: temp = 0.3
# Stylistic generation: temp = 0.7-1.0
```
**Use:** Style generation uses higher temperature for variation.

## Anti-Patterns to Avoid

### Anti-Pattern 1: Breaking Provenance Chain
**What:** Generating text without tracking authoritative source
**Why bad:** Core value proposition requires audit trail
**Instead:** Always link styled variants back to original statement ID

### Anti-Pattern 2: Synchronous Batch Generation
**What:** Generating all variants in single blocking request
**Why bad:** Slow, poor UX for many statements
**Instead:** Consider SSE streaming or async generation with polling

### Anti-Pattern 3: Vocabulary Validation in Frontend
**What:** Checking vocabulary compliance in JavaScript
**Why bad:** Index too large, security concern
**Instead:** All validation server-side via `/api/vocabulary-check`

### Anti-Pattern 4: Hardcoded Style Profiles
**What:** Embedding style rules in code
**Why bad:** Inflexible, requires code changes
**Instead:** Store profiles as data (JSON/DB), load dynamically

## File Structure

```
src/
  services/
    style_analyzer.py     # NEW: Parse example JDs
    vocabulary_index.py   # NEW: Build vocab index from parquet
    style_generator.py    # NEW: Constrained LLM generation
    style_service.py      # NEW: Orchestrator
    llm_service.py        # EXTEND: Add styled generation function
    labels_loader.py      # REFERENCE: Pattern template
  models/
    style.py              # NEW: StyleProfile, StyledVariant, etc.
    ai.py                 # EXTEND: Add styled generation metadata
  routes/
    api.py                # EXTEND: Add /generate-styled, /style-profiles
static/
  js/
    style_toggle.js       # NEW: Style enhancement toggle
    profile_tabs.js       # EXTEND: Dual display rendering
  css/
    style.css             # EXTEND: Styled variant CSS
data/
  style_profiles/         # NEW: Stored style profiles (JSON)
    professional-formal.json
    concise-active.json
```

## Scalability Considerations

| Concern | At 10 JDs | At 100 JDs | At 1000 JDs |
|---------|-----------|------------|-------------|
| Vocabulary index load | Lazy load once | Same | Same |
| Style profile storage | JSON files | JSON files | Consider SQLite |
| Generation latency | ~2s per statement | Batch parallel | Rate limiting needed |
| Cache size | Negligible | ~50MB | Consider LRU eviction |

## Sources

- Existing codebase analysis (HIGH confidence)
  - `src/services/llm_service.py` - OpenAI integration patterns
  - `src/services/labels_loader.py` - Parquet loading patterns
  - `src/services/enrichment_service.py` - Service composition
  - `src/routes/api.py` - API endpoint patterns
- JobForge 2.0 data structure verified via filesystem (HIGH confidence)
  - Parquet files: abilities, skills, knowledge, work activities, work context
- OpenAI API patterns from existing implementation (HIGH confidence)
  - Temperature conventions: 0 (deterministic), 0.3 (controlled), 0.7 (creative)
  - SSE streaming for long-running generation
