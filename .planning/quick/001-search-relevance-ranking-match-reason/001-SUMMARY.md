---
phase: quick
plan: 001
subsystem: search
tags: [relevance, scoring, UX, search-results]
dependency-graph:
  requires: []
  provides: [search-relevance-scoring, match-reason-display]
  affects: []
tech-stack:
  added: []
  patterns: [route-level-scoring]
key-files:
  created: []
  modified:
    - src/models/noc.py
    - src/routes/api.py
    - static/js/main.js
    - static/css/results-cards.css
    - .planning/PROJECT.md
decisions:
  - id: scoring-in-route
    choice: "Score in API route, not parser"
    reason: "Parser lacks query context; route has both query and results"
metrics:
  duration: "5 minutes"
  completed: "2026-02-06"
---

# Quick Task 001: Search Relevance Ranking + Match Reason Summary

Search results now scored by relevance (title=3, lead statement=2, alternate title=1), sorted best-first, with color-coded match-reason badges on result cards.

## What Was Done

### Task 1: Add relevance scoring fields and backend sorting logic
- Added `relevance_score` (Optional[int]) and `match_reason` (Optional[str]) to `EnrichedSearchResult` in `src/models/noc.py`
- Added scoring loop in `src/routes/api.py` search() function that checks where the query matches: title (score=3), lead statement (score=2), or alternate job title (score=1)
- Sorting applied with `results.sort(key=lambda r: r.relevance_score or 0, reverse=True)` so title matches surface first
- Commit: `a6cf9a7`

### Task 2: Display match reason on result cards and wire up relevance sort
- Added match-reason badge in the card-footer template in `renderCardView()` with dynamic CSS class based on relevance score (high/medium/low)
- Updated sort dropdown `'match'` case to sort by `relevance_score` instead of preserving original order
- Added CSS styles for `.match-reason` badge with three color variants: green (title match), amber (description match), pink (alternate job title)
- Commit: `7b9b90f`

### Task 3: Update PROJECT.md with new requirement and key decision
- Added `SRCH-13` validated requirement under v2.0 UI Redesign section
- Added key decision row documenting scoring-in-route architectural choice
- Updated last-updated timestamp
- Commit: `5379c21`

## Verification Results

1. **Printer search**: "Plateless printing equipment operators" (description match, score=2) sorts above "Athletes" (alternate title match, score=1) -- the confusing "Sprinter contains printer" case is now visually explained and sorted lower
2. **Engineer search**: All title matches (score=3) like "Engineering managers", "Software engineers and designers" sort first, before description/alternate matches
3. All results include `relevance_score` (1-3) and `match_reason` (string) in API JSON
4. Sort dropdown "Matching search criteria" re-sorts by relevance_score

## Deviations from Plan

None -- plan executed exactly as written.

## Decisions Made

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Relevance scoring in API route (not parser) | Parser lacks query context; route has both query and results for scoring | Good |

## Commits

| Commit | Type | Description |
|--------|------|-------------|
| `a6cf9a7` | feat | Add relevance scoring fields and backend sorting |
| `7b9b90f` | feat | Display match-reason badges on cards and wire relevance sort |
| `5379c21` | docs | Add SRCH-13 requirement and scoring decision to PROJECT.md |
