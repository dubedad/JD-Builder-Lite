---
status: complete
phase: 08-A-search-bar-redesign
source: [08-A-01-SUMMARY.md]
started: 2026-01-24T12:00:00Z
updated: 2026-01-24T12:00:00Z
---

## Current Test

[testing complete]

## Tests

### 1. Pill Toggle Visible
expected: Two pill buttons (Keyword/Code) visible above search input. Keyword is highlighted by default.
result: pass (fixed)
reported: "i see the pill buttons but the active selection is not highlighted"
fix: "Added !important to .pill-btn.active CSS (commit a923546)"

### 2. Toggle Active State
expected: Click "Code" pill — it becomes highlighted, "Keyword" becomes unhighlighted. Click "Keyword" — reverses.
result: pass

### 3. Placeholder Updates
expected: In Keyword mode, placeholder says "Search job titles...". In Code mode, placeholder says "Enter NOC code (e.g., 72600 or 72600.01)".
result: pass

### 4. Authoritative Sources Footnote
expected: Below the search bar, small gray text shows: "Authoritative Sources: ESDC OaSIS 2025 NOC v1.0 / ONET (R) 27.2 Database (USDOL/ETA)"
result: pass

### 5. Keyword Search Works
expected: With Keyword selected, search "software" — returns occupations matching keyword.
result: pass

### 6. Code Search Works
expected: With Code selected, search a NOC code like "21232" — returns matching occupation(s).
result: pass

### 7. Responsive Layout
expected: Resize browser to mobile width (~375px). Pill toggle should stack above the search input, full width.
result: pass

## Summary

total: 7
passed: 7
issues: 0
pending: 0
skipped: 0

## Gaps

[all resolved]
