---
phase: 11-provenance-architecture
plan: "01"
subsystem: models
tags: [provenance, enum, pydantic, vocabulary-audit]

dependency-graph:
  requires:
    - phase-10: style-analysis-pipeline (style constants established)
  provides:
    - StyleContentType enum for AI disclosure differentiation
    - VocabularyAudit model for vocabulary coverage tracking
    - ConfidenceLevel enum for visual indicators
    - CONFIDENCE_THRESHOLDS constants for level boundaries
  affects:
    - phase-11-02: styled content models will use these types
    - phase-12: generation implementation will reference these

tech-stack:
  added: []
  patterns:
    - str-enum-pattern: StyleContentType extends str and Enum for JSON serialization
    - frozen-model-pattern: immutable Pydantic models for audit data

key-files:
  created:
    - src/models/vocabulary_audit.py
  modified:
    - src/models/ai.py
    - src/models/__init__.py

decisions:
  - id: confidence-thresholds
    choice: "0.8 high, 0.5 medium, 0.0 low"
    reason: "Standard tiered thresholds with 80% as high quality bar"
  - id: frozen-models
    choice: "frozen=True for VocabularyTerm and VocabularyAudit"
    reason: "Audit data should be immutable once created"

metrics:
  duration: 2min 35sec
  completed: 2026-02-03
---

# Phase 11 Plan 01: Foundation Provenance Models Summary

**StyleContentType enum + VocabularyAudit model for AI disclosure and vocabulary coverage tracking**

## What Was Built

### StyleContentType Enum (`src/models/ai.py`)

Added to existing ai.py module:

```python
class StyleContentType(str, Enum):
    AI_STYLED = "ai_styled"      # Content styled from NOC using JD samples
    AI_GENERATED = "ai_generated" # Fully synthesized content
    ORIGINAL_NOC = "original_noc" # Unmodified NOC fallback
```

- Extends both `str` and `Enum` for JSON serialization compatibility
- Three values matching CONTEXT.md AI Disclosure Labels requirements

### Vocabulary Audit Module (`src/models/vocabulary_audit.py`)

New module with:

1. **ConfidenceLevel enum** - Visual indicator levels:
   - HIGH = "green" (>= 0.8)
   - MEDIUM = "yellow" (>= 0.5 and < 0.8)
   - LOW = "red" (< 0.5)

2. **CONFIDENCE_THRESHOLDS** - Boundary values:
   ```python
   {"high": 0.8, "medium": 0.5, "low": 0.0}
   ```

3. **VocabularyTerm** - Individual term tracking:
   - term: str
   - category: str (skill, ability, knowledge, work_activity)
   - is_noc_term: bool
   - Immutable (frozen=True)

4. **VocabularyAudit** - Validation results:
   - noc_terms_used: List[VocabularyTerm]
   - non_noc_terms: List[str] (matches VocabularyValidator output)
   - coverage_percentage: float
   - total_content_words: int
   - noc_word_count: int
   - Immutable (frozen=True)

### Package Exports (`src/models/__init__.py`)

All new types exported with explicit `__all__`:
- StyleContentType
- VocabularyTerm
- VocabularyAudit
- ConfidenceLevel
- CONFIDENCE_THRESHOLDS

## Commits

| Hash | Type | Description |
|------|------|-------------|
| cb59ead | feat | add StyleContentType enum for AI disclosure |
| 5fbc125 | feat | add VocabularyAudit models for provenance tracking |
| 53998ff | feat | export provenance models from models package |

## Deviations from Plan

None - plan executed exactly as written.

## Success Criteria Met

- [x] StyleContentType enum has AI_STYLED, AI_GENERATED, ORIGINAL_NOC (PROV-02)
- [x] VocabularyAudit model tracks NOC terms, non-NOC terms, coverage percentage (PROV-04)
- [x] ConfidenceLevel enum defines green/yellow/red visual indicators (PROV-05 partial)
- [x] CONFIDENCE_THRESHOLDS constants define 0.8/0.5/0.0 boundaries
- [x] All new types exportable from src.models package

## Next Phase Readiness

Plan 11-02 (Styled Content Models) can proceed:
- StyleContentType available for styled statement content_type field
- VocabularyAudit available for vocabulary_audit field in styled statements
- ConfidenceLevel + thresholds available for confidence display logic
