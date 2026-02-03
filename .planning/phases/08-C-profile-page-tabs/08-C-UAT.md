---
status: testing
phase: 08-C-profile-page-tabs
source: [08-C-01-SUMMARY.md, 08-C-02-SUMMARY.md, 08-C-03-SUMMARY.md]
started: 2026-01-24T22:00:00Z
updated: 2026-01-24T22:00:00Z
---

## Current Test

number: 1
name: Profile Header Blue Banner
expected: |
  Search for an occupation (e.g., "pilot") and select a profile.
  A blue gradient banner header appears with the occupation title in large white text.
awaiting: user response

## Tests

### 1. Profile Header Blue Banner
expected: Search for an occupation and select a profile. Blue gradient banner header appears with occupation title in large white text.
result: [pending]

### 2. OaSIS Code Badge
expected: Below the occupation title in the header, the OaSIS/NOC code appears as a small badge with translucent background (e.g., "21320").
result: [pending]

### 3. LLM Icon Display
expected: After ~1-3 seconds, an icon appears on the right side of the header. Icon should be contextually appropriate (e.g., atom for scientist, tools for trades).
result: [pending]

### 4. LLM Description Display
expected: After ~1-3 seconds, an italicized paragraph description appears in the header below the lead statement. This is AI-generated, not a direct copy of source text.
result: [pending]

### 5. Six Tabs Visible
expected: Below the header, six horizontal tabs appear: Overview | Key Activities | Skills | Effort | Responsibility | Feeder Group Mobility & Career Progression
result: [pending]

### 6. Tab Click Navigation
expected: Click the "Skills" tab. The Skills panel becomes visible. Other panels are hidden. The Skills tab shows a blue bottom border indicating active state.
result: [pending]

### 7. Arrow Key Navigation
expected: With keyboard focus on a tab, press Right Arrow. Focus moves to next tab and that tab becomes active. Left Arrow moves backward. (Wrap-around at ends.)
result: [pending]

## Summary

total: 7
passed: 0
issues: 0
pending: 7
skipped: 0

## Gaps

[none yet]
