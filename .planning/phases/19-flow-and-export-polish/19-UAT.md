---
status: testing
phase: 19-flow-and-export-polish
source: [19-01-SUMMARY.md, 19-02-SUMMARY.md, 19-03-SUMMARY.md]
started: 2026-02-07T17:00:00Z
updated: 2026-02-07T17:00:00Z
---

## Current Test

number: 1
name: Preview page split navigation layout
expected: |
  Steps: Search a job title > Select a profile > Select some statements > Click "Export" (Step 4)
  On the preview page you should see:
  - TOP BAR: "Return to Builder" button on the left, step breadcrumb "Builder > Preview > Classify" in the center
  - BOTTOM: "Classify" button (primary/blue) and "Export" dropdown button
awaiting: user response

## Tests

### 1. Preview page split navigation layout
expected: Search a job title > Select profile > Select statements > Click "Export" (Step 4). Preview page shows: TOP BAR with "Return to Builder" on left + "Builder > Preview > Classify" breadcrumb in center. BOTTOM shows "Classify" button (blue) and "Export" dropdown.
result: [pending]

### 2. Breadcrumb highlights current step
expected: On the preview page, look at the breadcrumb "Builder > Preview > Classify". "Preview" should appear highlighted/bold as the current step. "Builder" should look clickable (completed step). "Classify" should look dimmed (future step).
result: [pending]

### 3. Return to Builder from Preview
expected: On the preview page, click "Return to Builder" (top left). You should land back on the Build JD screen (Step 3) with all your statement checkboxes still checked and profile still loaded.
result: [pending]

### 4. Return to Builder from Classification
expected: Go back to preview (Step 4), then click "Classify" to run classification. After results appear, scroll down to the "Classification Step 1 Complete" section. Click "Return to Builder". You should land back on the Build JD screen with all selections intact.
result: [pending]

### 5. Classification cache (no re-fetch)
expected: After completing Test 4, navigate back to Step 5 (Classify) via the stepper. Your previous classification results should appear immediately -- no loading spinner, no API call. Same recommendations as before.
result: [pending]

### 6. Stale warning after JD edit
expected: While classification results are cached (from Test 5), click the stepper to go back to Build JD (Step 3). Add or remove a statement checkbox. Then navigate to Step 5 (Classify). An amber/yellow warning banner should appear saying "JD changed -- re-classify for updated results" with a "Re-classify" button.
result: [pending]

### 7. Multi-group coaching panel (blue, not red)
expected: To trigger this: classify a JD that spans multiple occupational groups (e.g., a JD mixing IT duties with admin duties). When the result is "invalid_combination" / multiple groups, it should display as a BLUE coaching panel with a lightbulb icon -- NOT a red error box. The tone should feel like helpful guidance.
result: [pending]

### 8. Coaching panel ranked cards with duty alignment
expected: Inside the blue coaching panel (from Test 7), each recommended group should appear as a card showing: (1) confidence percentage badge, (2) group code and name, (3) up to 3 key duty evidence quotes. Cards should be ranked highest confidence first.
result: [pending]

### 9. Accept Top Recommendation dismisses coaching panel
expected: In the coaching panel (from Test 7/8), click the "Accept Top Recommendation" button. The blue coaching panel should disappear, but the full recommendation cards should still be visible below.
result: [pending]

### 10. Status badge shows "Multiple Groups Identified"
expected: For the multi-group result (from Test 7), look at the status badge near the top of the classification section. It should read "Multiple Groups Identified" in blue styling -- NOT "Invalid Combination" in red.
result: [pending]

### 11. Export options modal with checkboxes
expected: From the preview page, click the "Export" dropdown > choose PDF or Word. A modal should pop up with checkboxes to include/exclude sections (at minimum: JD content and Classification). Both checkboxes should be checked by default. Click "Continue to Preview" or equivalent to proceed.
result: [pending]

### 12. Classification section in PDF export
expected: Export as PDF (with classification checkbox checked). Open the PDF. After the JD content sections, there should be a "Classification" section showing: recommended groups sorted by confidence, evidence quotes, and provenance source references. It appears before the compliance appendix.
result: [pending]

### 13. Provenance URLs clickable in DOCX
expected: Export as Word/DOCX (with classification checkbox checked). Open the .docx file. In the classification section, TBS directive provenance URLs should be clickable hyperlinks (blue, underlined) -- not plain text.
result: [pending]

### 14. README.md exists
expected: Check the project root folder. A README.md file should exist. Open it -- it should lead with compliance/TBS Directive 32592 information, then cover v4.0 architecture and setup instructions.
result: [pending]

## Summary

total: 14
passed: 0
issues: 0
pending: 14
skipped: 0

## Gaps

[none yet]
