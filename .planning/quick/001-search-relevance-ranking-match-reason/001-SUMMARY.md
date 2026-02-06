---
phase: quick
plan: 001
subsystem: search
tags: [relevance, scoring, UX, search-results, stemming]
dependency-graph:
  requires: []
  provides: [search-relevance-scoring, match-reason-display, confidence-percentage]
  affects: []
tech-stack:
  added: []
  patterns: [route-level-scoring, word-stem-matching]
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
  - id: stem-matching
    choice: "Word-stem matching for relevance scoring"
    reason: "Exact substring fails across word forms (Printer vs Printing)"
metrics:
  completed: "2026-02-06"
---

# Quick Task 001: Search Relevance Scoring with Confidence % and Rationale

Search results scored by confidence percentage (95/85/60/50/10) with human-readable rationale explaining WHY each result appeared. Results sorted best-first. Word-stem matching ensures "Printer" matches "Printing" across word forms.

## Problem

OASIS keyword search matches on hidden example job titles using substring matching. Searching "Printer" returned "Athletes" (because "Sprinter" contains "printer") with no indication of why. All 8 results appeared equally relevant with no ranking.

## Solution

### Confidence Scoring (src/routes/api.py)

5-tier confidence scoring based on where the search term matches:

| Confidence | Condition | Example |
|------------|-----------|---------|
| 95% | Exact query in title | "Printer" in "Printer Operators" |
| 85% | Stem match in title | "Print" in "Printing press operators" |
| 60% | Exact query in lead statement | "Printer" in description text |
| 50% | Stem match in lead statement | "Print" in description text |
| 10% | No visible match | Matched via hidden alternate job title |

### Word-Stem Matching

Query stems computed by stripping common suffixes (-ers, -er, -ing, -tion, -ment, -ed, -ly, -s). "Printer" → "Print", which matches "Printing" in titles. Minimum stem length of 3 characters prevents over-stripping.

### Rationale Display

Each result includes a human-readable rationale:
- `Title contains "Printing"` — shows the actual matched word
- `Description mentions "printing"` — for lead statement matches
- `Matched on alternate job title not shown` — for hidden OASIS matches

### Frontend (static/js/main.js, static/css/results-cards.css)

Card footer shows confidence badge with percentage and rationale:
- Green badge (>=80%): title matches
- Amber badge (>=40%): description matches
- Pink badge (<40%): alternate job title matches

Sort dropdown "Matching search criteria" sorts by confidence descending.

## Verification Results

**"Printer" search (8 results):**

| Rank | NOC | Title | Confidence | Rationale |
|------|-----|-------|------------|-----------|
| 1 | 72022.00 | Supervisors, printing and related occupations | 85% | Title contains "printing" |
| 2 | 73401.00 | Printing press operators | 85% | Title contains "Printing" |
| 3 | 94150.00 | Plateless printing equipment operators | 85% | Title contains "printing" |
| 4 | 53200.00 | Athletes | 10% | Matched on alternate job title not shown |
| 5 | 72020.00 | Contractors and supervisors, mechanic trades | 10% | Matched on alternate job title not shown |
| 6-8 | ... | Other low-relevance results | 10% | Matched on alternate job title not shown |

**"Engineer" search (83 results):** All engineering titles (Engineering managers, Software engineers, Civil engineers) rank first at 85%+ before alternate-title matches.

## Decisions Made

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Relevance scoring in API route (not parser) | Parser lacks query context; route has both query and results for scoring | Good |
| Word-stem matching over exact substring | "Printer" must match "Printing" — exact substring fails across word forms | Good |
| 5-tier confidence (95/85/60/50/10) over 3-tier (3/2/1) | Percentage communicates meaning; rationale explains the match | Good |
| Rationale shows matched word | "Title contains 'Printing'" more informative than "Title match" | Good |

## Commits

| Commit | Type | Description |
|--------|------|-------------|
| `a6cf9a7` | feat | Add relevance scoring fields and backend sorting |
| `7b9b90f` | feat | Display match-reason badges on cards and wire relevance sort |
| `5379c21` | docs | Add SRCH-13 requirement and scoring decision to PROJECT.md |
| `34467a4` | fix | Use word-stem matching for relevance scoring |
| `bdc7fb4` | feat | Confidence % scoring with rationale for search results |
