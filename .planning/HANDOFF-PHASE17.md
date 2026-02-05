# Phase 17 Handoff & Future Work

**Date:** 2026-02-04
**Status:** Phase 17 Complete, Future work documented

---

## What Was Accomplished in Phase 17

### Classification Algorithm Fixes (Critical)
1. **De-duplication by group_code** - Database had 426 entries but only 85 unique codes (SRE=40, SRW=40). Fixed to keep only best match per code.
2. **Inclusion-based ranking** - Uses `max(definition_sim, inclusion_sim)` for ranking. IT group has legal preamble in definition but clear inclusions.
3. **Keyword boost** - Added +15% boost for obvious title-to-group matches:
   - "Administrative" → AS
   - "Software/Developer" → IT
   - "Printer/Printing" → PR
   - And more in `TITLE_KEYWORD_GROUPS` dict

### Test Results After Fixes
| Test Case | Before | After |
|-----------|--------|-------|
| Software Engineer → IT | #61 | **#1** |
| Admin Assistant → AS | #8 | **#1** |
| Printer → PR | Not in top 10 | **#1** |

### UI Fixes
1. **Select All checkbox** - Added to all statement tabs (Activities, Skills, Effort, Responsibility)
2. **Exclusion penalty tooltip** - Added missing hover tooltip in confidence breakdown
3. **Occupational group names** - Display full names (e.g., "IT - Information Technology")
4. **Allocation check explanations** - More comprehensive context for inclusions/exclusions
5. **TBS definition links** - Now anchor to specific group code

### Files Modified
- `src/matching/shortlisting/__init__.py` - De-duplication, inclusion ranking, keyword boost
- `static/js/accordion.js` - Select All checkbox for all tabs
- `static/js/selection.js` - handleSelectAll function
- `static/js/classify.js` - exclusion_penalty tooltip, group names
- `static/css/main.css` - Select All styles

---

## Future Work: JobForge Integration (Phase 18+)

### Problem Statement
The current classification relies on semantic matching against TBS definitions. This fails for obvious cases because:
1. TBS definitions have legal preamble that hurts similarity
2. No direct NOC → Occupational Group mapping exists
3. Keyword heuristics are a workaround, not a solution

### Proposed Architecture
```
JobForge 2.0 (Gold Source)
┌─────────────────────────────────────────┐
│ dim_occupational_group (TBS scraped)    │
│ dim_og_inclusion                        │
│ dim_og_exclusion                        │
│ dim_noc_og_concordance  ←── NEW         │
│ dim_noc_profile (existing OaSIS)        │
└─────────────────────────────────────────┘
              │
              │ Read-only connection
              ▼
┌─────────────────────────────────────────┐
│ JD Builder Lite                         │
│ - Connects to JobForge gold models      │
│ - Classification uses concordance       │
│ - No duplicate scraping                 │
└─────────────────────────────────────────┘
```

### JobForge Iteration Scope
1. **Scrape full TBS Occupational Group page**
   - All 85 group definitions
   - All inclusions and exclusions
   - Links to qualification standards, rates of pay
   - Store in normalized tables

2. **Create NOC → OG Concordance Table**
   ```
   dim_noc_og_concordance
   - noc_2021_code (e.g., "21231")
   - og_code (e.g., "IT")
   - confidence ("deterministic" | "probable" | "possible")
   - source ("TBS" | "inferred" | "manual")
   ```

3. **Expose Gold Models**
   - Config: `JOBFORGE_DATA_PATH` or API endpoint
   - JD Builder reads from this path

### JD Builder Lite Changes (After JobForge)
1. Add config for JobForge data path
2. Update allocator to check concordance first
3. Concordance match → 95%+ confidence, skip semantic
4. No concordance → fall back to current semantic matching

---

## Future Work: Classify UI Enhancements (Phase 18+)

### Two-Column Recommendation Cards
- Left: JD info (position title, selected activities)
- Right: OG info (definition, inclusions, exclusions)
- Side-by-side comparison for classifier review

### LLM-Generated Improvement Suggestions
- When "Key activities too brief" warning appears
- LLM generates proposed additional activities
- Based on NOC profile + OG definition

### Interactive Statement Adoption
- Checkboxes on suggested statements
- "Add to Key Activities" button
- Flag as "non-provenance" (LLM-generated vs NOC-sourced)

---

## How to Resume

1. **For JobForge iteration:**
   - Open JobForge 2.0 project
   - Reference this document for concordance table design
   - Scrape TBS occupational group page

2. **For JD Builder Phase 18:**
   - Read this handoff document
   - JobForge integration depends on JobForge iteration completing first
   - UI enhancements can proceed independently

3. **Key files to review:**
   - `src/matching/shortlisting/__init__.py` - current algorithm
   - `src/matching/allocator.py` - orchestration
   - `static/js/classify.js` - UI rendering
