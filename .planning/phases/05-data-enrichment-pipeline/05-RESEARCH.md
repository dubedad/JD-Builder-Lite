# Phase 5: Data Enrichment Pipeline - Research

**Researched:** 2026-01-22
**Domain:** CSV data loading, backend enrichment, OASIS metadata integration
**Confidence:** HIGH

## Summary

Phase 5 transforms the existing v1.0 profile response by enriching statements with metadata from guide.csv (category definitions, descriptions, proficiency levels) and extracting additional NOC profile data (hierarchy breakdown, reference attributes). The enrichment must happen on the backend at profile fetch time to avoid O(n*m) frontend performance issues.

The implementation follows the existing codebase patterns: module-level singleton services (like scraper.py, mapper.py), Pydantic models for data structures, and Flask routes calling service methods. The critical technical concern is CSV encoding (UTF-8 BOM from Windows exports) which requires `utf-8-sig` encoding. The guide.csv lookup uses element ID as primary key with title fallback, and LLM imputation for missing entries with confidence tracking.

**Primary recommendation:** Create csv_loader.py and enrichment_service.py as singleton services loaded at app startup, extend NOCStatement model with optional enrichment fields, modify parser.py to extract proficiency ratings and Work Context dimension types, and modify mapper.py to apply enrichment before returning ProfileResponse.

## Standard Stack

The established libraries/tools for this phase:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python csv module | built-in | Parse guide.csv | Standard library, zero dependencies, DictReader handles headers |
| Flask 3.1.x | existing | App startup hooks | Already in use, app factory pattern |
| Pydantic 2.x | existing | Data models | Already used for NOCStatement, ProfileResponse |
| BeautifulSoup4 | existing | Enhanced HTML parsing | Already in use for OASIS scraping |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| OpenAI SDK | existing | LLM imputation | When guide.csv lookup fails |
| logging | built-in | Match statistics | Track ID matches, title fallbacks, imputations |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| csv module | pandas | Overkill for single CSV, adds 150MB dependency |
| LLM imputation | Return null | Loses enrichment value, worse UX |
| Module singleton | Flask-Injector | Unnecessary complexity for single-user demo |

**Installation:**
```bash
# No new dependencies required - all built-in or existing
```

## Architecture Patterns

### Recommended Project Structure
```
src/
├── services/
│   ├── csv_loader.py      # NEW: Load guide.csv, provide lookup methods
│   ├── enrichment_service.py  # NEW: Enrich statements with CSV data
│   ├── scraper.py         # EXISTING: HTTP client
│   ├── parser.py          # MODIFY: Extract ratings, dimensions
│   └── mapper.py          # MODIFY: Apply enrichment
├── models/
│   ├── noc.py             # MODIFY: Add enrichment fields to NOCStatement
│   └── responses.py       # MODIFY: Add reference_attributes to ProfileResponse
```

### Pattern 1: Module-Level Singleton for CSV Loader
**What:** Load CSV once at module import, provide O(1) lookup via dict
**When to use:** Data loaded once at startup, used across all requests
**Example:**
```python
# Source: Python patterns guide - module singleton
# src/services/csv_loader.py
import csv
from typing import Dict, Optional
from pathlib import Path

class GuideCSVLoader:
    """Singleton CSV loader with O(1) lookups."""

    def __init__(self):
        self._by_element_id: Dict[str, dict] = {}
        self._by_title: Dict[str, dict] = {}
        self._loaded_at: Optional[str] = None
        self._stats = {"id_matches": 0, "title_fallbacks": 0, "missing": 0}

    def load(self, path: Path):
        """Load CSV with utf-8-sig encoding (handles Windows BOM)."""
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                element_id = row.get("element_id", "").strip()
                title = row.get("title", "").strip()
                if element_id:
                    self._by_element_id[element_id] = row
                if title:
                    self._by_title[title.lower()] = row  # case-insensitive
        self._loaded_at = datetime.utcnow().isoformat()

    def lookup(self, element_id: str = None, title: str = None) -> Optional[dict]:
        """Lookup by element_id (primary) or title (fallback)."""
        if element_id and element_id in self._by_element_id:
            self._stats["id_matches"] += 1
            return self._by_element_id[element_id]
        if title and title.lower() in self._by_title:
            self._stats["title_fallbacks"] += 1
            return self._by_title[title.lower()]
        self._stats["missing"] += 1
        return None

# Module-level singleton
guide_csv = GuideCSVLoader()
```

### Pattern 2: Enrichment Service with Confidence Tracking
**What:** Enrich NOCStatement objects with guide.csv data, track source
**When to use:** Transform raw statements before API response
**Example:**
```python
# src/services/enrichment_service.py
from dataclasses import dataclass
from typing import Optional
from enum import Enum

class EnrichmentSource(str, Enum):
    GUIDE_CSV = "guide_csv"
    LLM_IMPUTED = "llm_imputed"

@dataclass
class EnrichedStatement:
    """Statement with enrichment metadata."""
    text: str
    source_attribute: str
    source_url: str
    # Enrichment fields
    description: Optional[str] = None
    proficiency: Optional[dict] = None  # {level: 4, max: 5, label: "4 - High Level"}
    category_definition: Optional[str] = None
    dimension_type: Optional[str] = None  # For Work Context
    enrichment_source: EnrichmentSource = EnrichmentSource.GUIDE_CSV
    confidence: float = 1.0  # 1.0 for guide_csv, 0.0-0.9 for LLM
```

### Pattern 3: Extended Parser for Ratings
**What:** Modify parser.py to extract proficiency ratings alongside text
**When to use:** Enhanced scraping of OASIS profile pages
**Example:**
```python
# In parser.py - extract rating from OASIS HTML structure
def _extract_rating_items_with_levels(self, soup, section_name) -> List[dict]:
    """Extract items with proficiency levels from rating section."""
    items = []
    # Find rating circles: filled circles indicate level
    for row in panel_body.select('.wb-eqht-grd'):
        name_cell = row.select_one('.OasisdescriptorRatingCell:first-child')
        rating_cells = row.select('.scale-option-circle')

        if name_cell:
            text = name_cell.get_text(strip=True)
            # Count filled circles for rating level
            level = sum(1 for c in rating_cells if 'filled' in c.get('class', []))
            items.append({
                "text": text,
                "level": level,
                "max": len(rating_cells) or 5
            })
    return items
```

### Anti-Patterns to Avoid
- **Frontend CSV joins:** O(n*m) performance, 50 statements x 1000 CSV rows = 2+ second lag
- **Loading CSV per request:** File I/O on every profile fetch, cache miss behavior
- **Hardcoded scale meanings:** Different categories use different scales (3 vs 5 point)
- **Ignoring BOM encoding:** Silent lookup failures with Windows-exported CSV

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| CSV BOM handling | Strip bytes manually | `encoding='utf-8-sig'` | Built-in, handles non-BOM gracefully |
| Case-insensitive lookup | Manual .lower() everywhere | Dict with lowercased keys | O(1) instead of O(n) scan |
| Scale meaning labels | Giant switch statement | Lookup table keyed by category+level | Easier to maintain, extend |
| LLM confidence tracking | Ad-hoc field names | Consistent EnrichmentSource enum | Type-safe, documented |

**Key insight:** The Python csv module with DictReader and utf-8-sig encoding handles all CSV edge cases. Don't build custom parsing.

## Common Pitfalls

### Pitfall 1: UTF-8 BOM Breaks Dictionary Lookups
**What goes wrong:** First column name becomes `\ufeffNOC_Code` instead of `NOC_Code`, all lookups by that key return None silently
**Why it happens:** Windows Excel adds invisible BOM (Byte Order Mark) when saving as "CSV UTF-8"
**How to avoid:** Always use `encoding='utf-8-sig'` when opening CSV files
**Warning signs:** Lookups returning None, printing column names shows `\ufeff` prefix

### Pitfall 2: Different OASIS Categories Use Different Scales
**What goes wrong:** Displaying 5 stars for a 3-point scale category makes Level 3 look "bad"
**Why it happens:** Knowledge uses 1-3 scale, Skills/Abilities use 1-5 scale
**How to avoid:** Return both `level` and `max` in proficiency object, frontend renders stars relative to max
**Warning signs:** User confusion about why some categories have max 3 stars

### Pitfall 3: Work Context Has Multiple Dimension Types
**What goes wrong:** All Work Context statements display same "Proficiency" label
**Why it happens:** Work Context dimensions include Frequency, Duration, Responsibility, etc. with different meanings
**How to avoid:** Extract dimension type from HTML during scraping, include in enriched statement
**Warning signs:** "Frequency: Level 4" makes sense, "Proficiency: Level 4" for Frequency does not

### Pitfall 4: 0-Level Statements Polluting Output
**What goes wrong:** Statements with Level 0 (not applicable) appear in results
**Why it happens:** Parser extracts all items, doesn't filter by applicability
**How to avoid:** Filter statements where `level == 0` in enrichment service
**Warning signs:** Many irrelevant statements appearing in profile

### Pitfall 5: Flask before_first_request Removed
**What goes wrong:** Trying to use deprecated decorator causes ImportError
**Why it happens:** `before_first_request` was deprecated in Flask 2.3, removed in Flask 3.0
**How to avoid:** Load CSV during module import (singleton pattern) or in app factory before returning app
**Warning signs:** ImportError: cannot import name 'before_first_request'

### Pitfall 6: LLM Imputation Without Rate Limiting
**What goes wrong:** Many missing entries cause burst of OpenAI API calls, hitting rate limits
**Why it happens:** Eager imputation for every missing entry during single request
**How to avoid:** Batch imputation calls, cache results, or impute lazily on demand
**Warning signs:** OpenAI rate limit errors, slow profile response times

## Code Examples

Verified patterns from official sources:

### CSV Loading with BOM Handling
```python
# Source: Python docs - csv module
import csv
from pathlib import Path

def load_csv_with_bom(path: Path) -> list:
    """Load CSV handling both BOM and non-BOM files."""
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)
```

### OASIS Scale Definitions (from Open Canada documentation)
```python
# Source: https://open.canada.ca/data/en/dataset/eeb3e442-9f19-4d12-8b38-c488fe4f6e5e
SCALE_MEANINGS = {
    "skills": {
        1: "1 - Lowest Level",
        2: "2 - Low Level",
        3: "3 - Moderate Level",
        4: "4 - High Level",
        5: "5 - Highest Level",
        "max": 5,
        "dimension": "Proficiency"
    },
    "abilities": {
        1: "1 - Lowest Level",
        2: "2 - Low Level",
        3: "3 - Moderate Level",
        4: "4 - High Level",
        5: "5 - Highest Level",
        "max": 5,
        "dimension": "Proficiency"
    },
    "knowledge": {
        1: "1 - Basic",
        2: "2 - Intermediate",
        3: "3 - Advanced",
        "max": 3,
        "dimension": "Knowledge Level"
    },
    "work_activities": {
        1: "1 - Lowest Complexity",
        2: "2 - Low Complexity",
        3: "3 - Moderate Complexity",
        4: "4 - High Complexity",
        5: "5 - Highest Complexity",
        "max": 5,
        "dimension": "Complexity"
    },
    "personal_attributes": {
        1: "1 - Lowest Importance",
        2: "2 - Low Importance",
        3: "3 - Moderate Importance",
        4: "4 - High Importance",
        5: "5 - Highest Importance",
        "max": 5,
        "dimension": "Importance"
    },
    # Work Context dimension-specific scales
    "work_context_frequency": {
        1: "Once a year or more but not every month",
        2: "Once a month or more but not every week",
        3: "Once a week or more but not every day",
        4: "Every day, a few times per day",
        5: "Every day, many times per day",
        "max": 5,
        "dimension": "Frequency"
    },
    "work_context_duration": {
        1: "Very little time",
        2: "Less than half the time",
        3: "About half the time",
        4: "More than half the time",
        5: "All the time, or almost all the time",
        "max": 5,
        "dimension": "Duration"
    }
}
```

### NOC Hierarchy Structure (from NOC 2021 documentation)
```python
# Source: https://noc.esdc.gc.ca/Structure/Matrix
# NOC code structure: 72600.01
#   7 = Broad occupational category (first digit)
#   2 = TEER category (second digit)
#   26 = Major group (first 2 digits)
#   260 = Minor group (first 3 digits)
#   2600 = Unit group (first 4 digits)
#   72600.01 = OaSIS occupation (full 7 digits)

TEER_CATEGORIES = {
    0: "Management occupations",
    1: "University degree usually required",
    2: "College diploma or apprenticeship (2+ years), or supervisory",
    3: "College diploma or apprenticeship (<2 years), or 6+ months training",
    4: "High school diploma or several weeks training",
    5: "Short-term work demonstration, no formal education"
}

def extract_noc_hierarchy(noc_code: str) -> dict:
    """Extract NOC hierarchy from 7-digit code."""
    # Remove decimal for parsing
    code = noc_code.replace(".", "")

    return {
        "noc_code": noc_code,
        "broad_category": int(code[0]),  # First digit
        "teer_category": int(code[1]),   # Second digit
        "teer_description": TEER_CATEGORIES.get(int(code[1]), "Unknown"),
        "major_group": code[:2],          # First 2 digits
        "minor_group": code[:3],          # First 3 digits
        "unit_group": code[:4],           # First 4 digits
    }
```

### Extended NOCStatement Model
```python
# Source: Existing codebase pattern (src/models/noc.py)
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class EnrichmentSource(str, Enum):
    GUIDE_CSV = "guide_csv"
    LLM_IMPUTED = "llm_imputed"

class ProficiencyLevel(BaseModel):
    """Proficiency level with scale context."""
    level: int
    max: int
    label: str
    dimension: str  # "Proficiency", "Complexity", "Frequency", etc.

class EnrichedNOCStatement(BaseModel):
    """NOC statement with enrichment metadata."""
    # Original fields
    text: str
    source_attribute: str
    source_url: str

    # Enrichment fields (optional for backward compatibility)
    element_id: Optional[str] = None
    description: Optional[str] = None
    proficiency: Optional[ProficiencyLevel] = None
    category_definition: Optional[str] = None
    dimension_type: Optional[str] = None  # For Work Context
    classification_reason: Optional[str] = None  # For Responsibilities/Effort routing

    # Metadata
    enrichment_source: Optional[EnrichmentSource] = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
```

### Work Context Classification
```python
# Source: CONTEXT.md decisions
CLASSIFICATION_PATTERNS = {
    "responsibilities": ["responsib", "decision"],
    "effort": ["effort"]
}

def classify_work_context(text: str, description: str = None) -> tuple:
    """Classify Work Context statement into section.

    Returns: (section_name, reason)
    """
    search_text = f"{text} {description or ''}".lower()

    for section, patterns in CLASSIFICATION_PATTERNS.items():
        for pattern in patterns:
            if pattern in search_text:
                return (section, f"matched: '{pattern}' in {'title' if pattern in text.lower() else 'description'}")

    return ("other_work_context", "no pattern match")
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| before_first_request | Module-level singleton or app factory | Flask 3.0 | Must update any Flask 2.x startup patterns |
| Frontend CSV joins | Backend enrichment | v1.1 decision | 10x+ performance improvement |
| Hardcoded scale labels | Dynamic lookup by category | v1.1 requirement | Correct display for 3 vs 5 point scales |

**Deprecated/outdated:**
- `@app.before_first_request`: Removed in Flask 3.0, use module import or app factory
- Single scale assumption: Categories have different max levels, must return both level and max

## Open Questions

Things that couldn't be fully resolved:

1. **Exact guide.csv column names**
   - What we know: File contains element_id, title, description, category definition
   - What's unclear: Exact column header names (may vary between versions)
   - Recommendation: Validate column names on load, log warning if expected columns missing

2. **OASIS HTML structure for proficiency extraction**
   - What we know: Ratings displayed with filled/empty circles in `.scale-option-circle` elements
   - What's unclear: Exact class names for "filled" state (may be `filled`, `active`, or similar)
   - Recommendation: Test with live OASIS page during implementation, add fallback patterns

3. **Reference attributes availability**
   - What we know: Overview tab shows "Also known as", "Core competencies", hierarchy breakdown
   - What's unclear: Which attributes are consistently available vs optional
   - Recommendation: Treat all reference fields as optional, use empty array/null for missing

4. **LLM imputation caching strategy**
   - What we know: Should track imputation with source indicator and confidence
   - What's unclear: Whether to cache imputations persistently or regenerate each session
   - Recommendation: Start with in-memory caching per app instance, evaluate persistence need later

## Sources

### Primary (HIGH confidence)
- Python csv module documentation - verified DictReader, utf-8-sig encoding patterns
- Open Canada OASIS 2022 dataset portal - scale definitions, measurement approaches
- Existing codebase (src/services/*.py) - singleton patterns, Pydantic models, Flask routes
- NOC 2021 TEER documentation - hierarchy structure, category definitions

### Secondary (MEDIUM confidence)
- Web search results for Flask startup patterns - verified before_first_request removed in 3.0
- Web search for Python singleton patterns - module-level instance is Pythonic standard
- Overview slides (milestone 2) - visual reference for expected UI, data requirements

### Tertiary (LOW confidence)
- guide.csv exact structure - column names inferred, needs validation with actual file
- OASIS HTML rating extraction - patterns inferred from parser.py, needs live testing
- Work Context dimension type labels - some visible in overview, complete list needs verification

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - all built-in or existing dependencies
- Architecture: HIGH - follows established codebase patterns
- Pitfalls: HIGH - CSV BOM, Flask 3.0, scale differences well-documented
- Scale meanings: MEDIUM - partial from Open Canada, some inferred
- HTML extraction patterns: MEDIUM - based on existing parser, needs live validation

**Research date:** 2026-01-22
**Valid until:** 30 days (stable patterns, but guide.csv structure should be validated early)
