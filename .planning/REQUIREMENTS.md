# Requirements: JD Builder Lite

**Defined:** 2026-01-22
**Core Value:** Every piece of content in the final job description can be traced back to its authoritative source (NOC/OASIS), with clear documentation of human decisions and AI involvement.

## v1.1 Requirements

Requirements for v1.1 Enhanced Data Display + Export milestone.

### Search Results

- [ ] **SRCH-04**: Search results display grid view toggle (card vs table views)
- [ ] **SRCH-05**: Search results show NOC code next to profile title (e.g., "Air pilots (72600.01)")

### Statement Display

- [ ] **DISP-04**: Each JD Element section shows category definition at top (from guide.csv)
- [ ] **DISP-05**: Each statement includes OASIS label description (from guide.csv lookup)
- [ ] **DISP-06**: Statements display proficiency/complexity level as stars (1-5)
- [ ] **DISP-07**: Star ratings include scale meaning label (e.g., "5 - Highest Level" for Skills)
- [ ] **DISP-08**: Work Context statements show dimension type (Frequency, Duration, Degree of responsibility, etc.)

### Data Bug Fixes

- [ ] **DATA-03**: Responsibilities header populated with Work Context items containing "responsib" or "decision"
- [ ] **DATA-04**: Effort header captures all Work Context items containing "effort"
- [ ] **DATA-05**: Work Context scraping extracts complete data from OASIS

### Profile Overview

- [ ] **DISP-09**: Profile page shows NOC code prominently under title
- [ ] **DISP-10**: Profile page displays NOC hierarchical breakdown (TEER, broad category, major group)
- [ ] **DISP-11**: Profile page displays reference NOC attributes (job requirements, career mobility, example titles, interests, personal attributes)

### Export

- [ ] **OUT-06**: Manager can export final JD to Word/DOCX format
- [ ] **OUT-07**: PDF export includes Annex section with unused NOC reference attributes
- [ ] **OUT-08**: DOCX export includes Annex section with unused NOC reference attributes

## v1.2 Requirements (Future)

Deferred to future milestone. Tracked but not in v1.1 roadmap.

### Search Results Enhancements

- **SRCH-06**: Grid view shows columns: Broad category, Training/Education, Lead statement
- **SRCH-07**: Filter items by Job Family
- **SRCH-08**: Filter items by Organizational Unit
- **SRCH-09**: Filter items by Digital Competencies

### Statement Display Differentiators

- **DISP-12**: Visual scale distinction by category type (different colors/styles)
- **DISP-13**: "Learn More" links to OASIS source for each statement

### Export Differentiators

- **OUT-09**: "Include Annex" checkbox toggle in export options
- **OUT-10**: Custom compliance styling in DOCX (matching PDF quality)

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Inline rating editing | Breaks provenance - ratings come from NOC, not user input |
| Custom statement creation | Breaks audit trail - all content must trace to NOC source |
| Animated star ratings | Visual gimmick, no user value |
| Printing grid view | Poor layout, card view sufficient for print |
| User authentication | Single user demo only (from v1.0) |
| Database/persistence | No saved history (from v1.0) |
| Multi-user support | Not needed for demo (from v1.0) |
| Production hosting | Runs locally only (from v1.0) |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| SRCH-04 | TBD | Pending |
| SRCH-05 | TBD | Pending |
| DISP-04 | TBD | Pending |
| DISP-05 | TBD | Pending |
| DISP-06 | TBD | Pending |
| DISP-07 | TBD | Pending |
| DISP-08 | TBD | Pending |
| DATA-03 | TBD | Pending |
| DATA-04 | TBD | Pending |
| DATA-05 | TBD | Pending |
| DISP-09 | TBD | Pending |
| DISP-10 | TBD | Pending |
| DISP-11 | TBD | Pending |
| OUT-06 | TBD | Pending |
| OUT-07 | TBD | Pending |
| OUT-08 | TBD | Pending |

**Coverage:**
- v1.1 requirements: 16 total
- Mapped to phases: 0
- Unmapped: 16 (pending roadmap creation)

---
*Requirements defined: 2026-01-22*
*Last updated: 2026-01-22 after initial definition*
