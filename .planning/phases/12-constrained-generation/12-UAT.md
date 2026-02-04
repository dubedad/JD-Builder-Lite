---
status: complete
phase: 12-constrained-generation
source: [12-01-SUMMARY.md, 12-02-SUMMARY.md, 12-03-SUMMARY.md]
started: 2026-02-04T00:45:00Z
updated: 2026-02-04T01:00:00Z
---

## Current Test

[testing complete]

## Tests

### 1. Style Selected Button Visible
expected: In the profile page, each section (Key Activities, Skills, etc.) has a blue "Style Selected" button in the section header area, next to the section title.
result: pass

### 2. Style Selected Triggers Generation
expected: Selecting one or more statement checkboxes and clicking "Style Selected" shows a styled statement container below each selected statement (may take a few seconds for API call).
result: pass

### 3. Styled Container Appearance
expected: Styled statement container has blue left border, shows styled text (different/longer than original), and displays confidence percentage.
result: pass

### 4. Confidence Dot Color
expected: Confidence dot is colored: green (>=80%), yellow (50-79%), or red (<50%). Color matches the percentage shown.
result: pass

### 5. Show Original Toggle
expected: Clicking "Show original NOC statement" expands to show the original text below the styled text. Clicking again collapses it.
result: pass

### 6. Regenerate Button
expected: Clicking "Regenerate" shows a loading spinner, then updates the styled text with a new generation (may be same or different).
result: pass

### 7. Use Original Checkbox
expected: Checking "Use original" swaps the displayed text to the original NOC statement and changes the label. Unchecking swaps back to styled.
result: pass

### 8. Fallback Behavior
expected: If styling fails (vocabulary validation), container shows original text with gray border and label "Using original NOC statement (styling not applied)".
result: pass

## Summary

total: 8
passed: 8
issues: 0
pending: 0
skipped: 0

## Gaps

[none yet]
