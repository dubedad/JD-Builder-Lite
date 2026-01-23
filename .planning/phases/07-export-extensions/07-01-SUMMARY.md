---
phase: 07-export-extensions
plan: 01
status: complete
completed_at: 2026-01-22
---

# 07-01 Summary: Parser Extension + Annex Data Models

## What Was Built

### 1. Parser Extensions (`src/services/parser.py`)

Added top-level fields to `parse_profile()` return dict for annex builder consumption:
- `interests`: List[str] - Interest names (Holland Codes)
- `personal_attributes`: List[str] - Personal suitability criteria
- `career_mobility`: Dict with `from` and `to` lists for entry/advancement paths

New method `_extract_career_mobility_dict()` extracts mobility data with entry/advancement distinction.

### 2. Annex Models (`src/models/export_models.py`)

**AnnexSection** - Single category section:
```python
class AnnexSection(BaseModel):
    title: str  # "Job Requirements", "Career Mobility", etc.
    category: str  # Internal key
    items: List[str]  # Content items
    format_type: Literal['paragraph', 'list', 'grouped_list']
```

**AnnexData** - Complete annex with all sections:
```python
class AnnexData(BaseModel):
    sections: List[AnnexSection]
    source_noc_code: str
    retrieved_at: datetime
```

**ExportData** updated with:
```python
annex_data: Optional[AnnexData] = None
```

### 3. Annex Builder Service (`src/services/annex_builder.py`)

`build_annex_data()` function:
- Takes raw NOC data and manager selections
- Filters out already-selected items
- Returns AnnexData with 4 sections in fixed order:
  1. Job Requirements (paragraph format)
  2. Career Mobility (grouped_list with Entry/Advancement)
  3. Interests (Holland Codes) (list format)
  4. Personal Suitability (Placement Criteria) (list format)

## Verification

```
Sections: 4
  Job Requirements: 2 items (paragraph)
  Career Mobility: 6 items (grouped_list)
  Interests (Holland Codes): 3 items (list)
  Personal Suitability (Placement Criteria): 2 items (list)

Annex builder test PASSED
```

## Files Modified

| File | Change |
|------|--------|
| `src/services/parser.py` | Added `_extract_career_mobility_dict()`, updated `parse_profile()` with top-level fields |
| `src/models/export_models.py` | Added `AnnexSection`, `AnnexData` models, updated `ExportData` |
| `src/services/annex_builder.py` | NEW - Annex data builder service |

## Ready for Next Plans

- 07-02 (PDF Annex) can now import `build_annex_data` and use `AnnexData` model
- 07-03 (DOCX Annex) can use same shared data structure
- Both plans depend on this foundation work
