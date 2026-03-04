# Coding Conventions

**Analysis Date:** 2026-03-04

## Naming Patterns

**Files:**
- Snake case for all Python files: `semantic_matcher.py`, `llm_service.py`, `db_manager.py`
- Files correspond to classes or logical units: `classifier.py` contains `LLMClassifier` class
- Subdirectories group related functionality: `src/matching/`, `src/services/`, `src/storage/`, `src/models/`
- Test files use prefix: `test_uat_screenshots.py`, `uat_terminal.py`

**Functions:**
- Snake case: `get_connection()`, `build_system_prompt()`, `parse_search_results()`
- Private functions prefixed with underscore: `_cache_key()`, `_load_groups_with_statements()`, `_extract_primary_purpose_text()`
- Helper functions at module level after classes: `shortlist_candidates()` follows `SemanticMatcher` class
- Query/fetch functions use `get_` prefix: `get_selector()`, `get_fallback()`, `get_db()`
- Builder/creation functions use `build_` prefix: `build_system_prompt()`, `build_user_prompt()`, `build_export_data()`

**Variables:**
- Snake case for all variables: `jd_data`, `semantic_similarity`, `max_retries`
- Constants use UPPER_SNAKE_CASE: `CONFIDENCE_THRESHOLD`, `OPENAI_MODEL`, `REQUEST_TIMEOUT`
- Configuration values at module top: `OASIS_BASE_URL = "https://noc.esdc.gc.ca"` in `src/config.py`
- Cache/state variables with clear descriptive names: `_allocation_cache`, `_definition_cache`, `vocab_index`
- Temporary loop variables can be short: `r` for results in list comprehensions

**Types:**
- Use Pydantic `BaseModel` for structured data: `EvidenceSpan`, `ReasoningStep`, `GroupRecommendation`, `AllocationResult` in `src/matching/models.py`
- Use dataclass patterns for simple containers: `SearchResult`, `EnrichedSearchResult` in `src/models/noc.py`
- Type annotations throughout: `def allocate(self, jd_data: Dict) -> AllocationResult:`

## Code Style

**Formatting:**
- No explicit formatter configured (no `.black`, `.isort`, `flake8` config found)
- 4-space indentation throughout
- Lines appear to follow ~100-120 character soft limit based on observed code
- Class methods separated by single blank line
- Module-level functions separated by double blank lines

**Linting:**
- No `.pylintrc` or `setup.cfg` linting configuration found
- Code follows PEP 8 style conventions by convention
- Type hints used throughout but not enforced via tools

## Import Organization

**Order:**
1. Standard library imports: `import os`, `import re`, `from typing import Dict, List`
2. Third-party imports: `from pydantic import BaseModel`, `from flask import Flask`, `from sentence_transformers import SentenceTransformer`
3. Local imports: `from src.config import OPENAI_API_KEY`, `from src.matching.models import AllocationResult`

**Path Aliases:**
- No path aliases configured (no `jsconfig.json` or equivalent)
- All imports use absolute paths from project root: `from src.matching.models import ...`
- Relative imports NOT used

**Examples:**
```python
# Header of src/matching/classifier.py
from typing import Dict, List
import instructor
from openai import OpenAI

from src.config import OPENAI_API_KEY, OPENAI_MODEL
from src.matching.models import AllocationResult
from src.matching.prompts import build_system_prompt, build_user_prompt
```

## Error Handling

**Patterns:**
- Try/except with specific exception handling: `try: return self.classify(...) except Exception as e:`
- Custom exceptions raised with descriptive messages: `raise ValueError("top_recommendations must have at most 3 entries")`
- Validation errors via Pydantic `@field_validator` decorators:
  ```python
  @field_validator("top_recommendations")
  @classmethod
  def validate_top_recommendations(cls, v: List[GroupRecommendation]) -> List[GroupRecommendation]:
      if len(v) > 3:
          raise ValueError("top_recommendations must have at most 3 entries")
      return v
  ```
- Fallback patterns for failures: `classify_with_fallback()` creates minimal result on LLM failure
- Context-specific error classes expected to be defined but not seen in sampled files; use generic `Exception` with descriptive strings
- Validation at function entry (e.g., query length check): `if not query or len(query) < 2: return ErrorResponse(...)`

## Logging

**Framework:** `logging` module (Python standard library)

**Patterns:**
- Logger created per module: `logger = logging.getLogger(__name__)` in `src/services/parser.py`
- Used for debugging and tracking: `logger.debug()`, `logger.warning()`, `logger.error()` patterns expected
- Print statements used for CLI output: `print(f"[Vocabulary] Loaded: {vocab_index.get_term_count()} terms")` in `src/app.py`
- Terminal-based tests use ANSI color codes for formatted output:
  ```python
  GREEN = "\033[92m"
  RED = "\033[91m"
  print(f"  {GREEN}[PASS]{RESET} {name}")
  ```

## Comments

**When to Comment:**
- Module docstrings describe file purpose and decisions: All files start with `"""File description."""` triple-quoted string
- Complex algorithms explained inline: Semantic matching, confidence calculation
- Decision rationale from CONTEXT.md/RESEARCH.md referenced: `# Per CONTEXT.md: Cache results with invalidation when JD changes`
- Edge cases and validation logic: `# NOTE: No INCLUSION_SUPPORT_WEIGHT - inclusions used for shortlisting only`

**JSDoc/TSDoc:**
- Not applicable (Python project, not TypeScript)
- Docstrings follow Google/NumPy style (based on docstring patterns):

```python
def get_selector(element: str) -> str:
    """Get primary CSS selector for element.

    Args:
        element: Element name from SELECTORS dict

    Returns:
        Primary CSS selector string

    Raises:
        KeyError: If element not found in SELECTORS
    """
```

**Docstring Style:**
- One-liner summary followed by blank line, then details
- Args/Returns/Raises sections for function docstrings
- Class docstrings explain purpose and key methods
- Detailed docstrings for public methods, minimal for private methods

## Function Design

**Size:** Functions range from single-line helpers to ~50 lines. Preferred pattern:
- Helper functions: 10-20 lines
- Main orchestration methods: 30-50 lines (e.g., `allocate()` method)
- Classes responsible for related functionality in same module

**Parameters:**
- Use type hints for all parameters: `def classify(self, jd_data: Dict, candidates: List[Dict], max_retries: int = 3)`
- Dict and List used for flexible data structures; Pydantic models for strict schemas
- Optional parameters with defaults near the end: `max_retries: int = 3`, `min_similarity: float = 0.3`

**Return Values:**
- Explicit return type hints: `-> AllocationResult`, `-> List[Dict]`, `-> Tuple[bool, str]`
- Return early for edge cases: `if not jd_text.strip(): return self._empty_result(...)`
- Destructure return tuples: `passed, total = test_api_health()`

## Module Design

**Exports:**
- Modules export public classes and functions at module level
- Private utilities prefixed with underscore: `_cache_key()`, `_empty_result()`
- Lazy module initialization: `__getattr__` in `src/matching/__init__.py` for dynamic imports

**Barrel Files:**
- Not heavily used; most modules import directly from implementation files
- Example: `src/vocabulary/__init__.py` re-exports: `VocabularyIndex`, `VocabularyValidator`, `start_vocabulary_watcher`

**Example from `src/matching/__init__.py`:**
```python
def __getattr__(name):
    """Lazy-load matching submodules to avoid circular imports."""
    if name == "allocate_jd":
        from src.matching.allocator import allocate_jd
        return allocate_jd
    # ... more lazy imports
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
```

---

*Convention analysis: 2026-03-04*
