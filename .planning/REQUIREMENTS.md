# Requirements: JD Builder Lite v4.0

**Defined:** 2026-02-04
**Core Value:** Classification Step 1 — Match job descriptions to occupational groups using the prescribed TBS allocation method with full policy provenance.

**Authoritative Source:** https://www.canada.ca/en/treasury-board-secretariat/services/classification/job-evaluation/guide-allocating-positions-using-occupational-group-definitions.html

## v4.0 Requirements: Occupational Group Allocation

Classification Step 1: Match JD inclusions/exclusions against TBS occupational group definitions to recommend best-fit classification.

### Data Layer — DIM_OCCUPATIONAL Table

- [ ] **DATA-01**: Scrape TBS occupational groups table from https://www.canada.ca/en/treasury-board-secretariat/services/collective-agreements/occupational-groups.html
- [ ] **DATA-02**: For each group, scrape linked definition page to extract: definition statement, inclusion statements, exclusion statements
- [ ] **DATA-03**: Extract and store: Group code, Subgroup, Definition, Qualification standard, Rates of pay links
- [ ] **DATA-04**: Build DIM_OCCUPATIONAL lookup table with all scraped data
- [ ] **DATA-05**: Store Table of Concordance linking group definitions ↔ inclusion/exclusion ↔ job evaluation standards

### Matching Engine — OccupationalGroupAllocator

- [x] **MATCH-01**: Extract primary purpose from JD using Client-Service Results and Key Activities
- [x] **MATCH-02**: Shortlist candidate occupational groups based on JD inclusions (labels.csv)
- [x] **MATCH-03**: Evaluate definition fit holistically (not keyword matching) per TBS guide
- [x] **MATCH-04**: Check inclusion statements — link to definition when used
- [x] **MATCH-05**: Check exclusion statements — confirm they don't reflect primary purpose
- [x] **MATCH-06**: Perform comparative checks with benchmark positions when doubt exists
- [x] **MATCH-07**: Produce ranked top-3 recommendations with confidence scores (0.0-1.0)
- [x] **MATCH-08**: Handle "multiple groups plausible" case with best-fit resolution

### Output — Recommendations & Rationale

- [x] **OUT-01**: Output allocated_group with allocation_confidence score
- [x] **OUT-02**: Output primary_purpose_summary (why position exists)
- [x] **OUT-03**: Output evidence_index with pointers to JD text spans used
- [x] **OUT-04**: Output definition_fit_rationale explaining why chosen group fits
- [x] **OUT-05**: Output inclusion_check showing applied statements or "none applies"
- [x] **OUT-06**: Output exclusion_check confirming exclusions don't apply
- [x] **OUT-07**: Output constraints_compliance statement: "evaluated work, not person"

### Policy Provenance — Traceability

- [x] **PROV-01**: Provenance map linking each decision rule to authoritative source paragraphs
- [x] **PROV-02**: Label authoritative text paragraphs (P1, P2, P3...) for reference
- [x] **PROV-03**: Each output includes source_snippet and explanation_of_mapping
- [x] **PROV-04**: Traceable to TBS Classification Policy (allocation method)
- [x] **PROV-05**: Traceable to Directive on Automated Decision Making (DADM)

### API Layer

- [x] **API-01**: POST /api/allocate accepts JD data, returns allocation recommendations
- [x] **API-02**: Response includes full provenance map
- [x] **API-03**: Response includes confidence scores and rationale for each recommendation
- [x] **API-04**: Handle edge cases: "Needs Work Description Clarification", "Invalid Combination of Work"

### UI Layer — Recommendations Display

- [ ] **UI-01**: Display top-3 ranked group recommendations with confidence bars
- [ ] **UI-02**: Show rationale for each recommendation (expandable)
- [ ] **UI-03**: Show evidence links to JD text spans (highlight on click)
- [ ] **UI-04**: Show provenance chain to authoritative source
- [ ] **UI-05**: Display "Classification Step 1 Complete" status with next steps

### Troubleshooting & Edge Cases

- [x] **EDGE-01**: Handle AP vs TC disambiguation (theoretical vs practical knowledge)
- [x] **EDGE-02**: Handle "work appears in more than one group" cases
- [x] **EDGE-03**: Detect and flag "Invalid Combination of Work" (same JD used for multiple groups)
- [x] **EDGE-04**: Generate remediation checklist when JD quality insufficient

## Constraints

| Constraint | Description |
|------------|-------------|
| Holistic matching | Do not match keywords; evaluate complete definition entities |
| Work not person | Never use incumbent education/skills as allocation drivers |
| Inclusion non-exhaustive | "No inclusion match" ≠ "no allocation possible" |
| Rework on exclusion conflict | If exclusion reflects primary purpose → loop to another group |
| Single allocation | Same JD cannot be allocated to different groups |

## Out of Scope (v4.0)

| Feature | Reason |
|---------|--------|
| Job evaluation standards scoring | Step 2 of classification (v5.0) |
| Benchmark position comparison UI | Available via text, not interactive |
| Manager consultation workflow | Human-in-loop deferred to v5.0 |
| Multi-JD batch processing | Single JD at a time for v4.0 |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| DATA-01 | Phase 14 | Complete |
| DATA-02 | Phase 14 | Complete |
| DATA-03 | Phase 14 | Complete |
| DATA-04 | Phase 14 | Complete |
| DATA-05 | Phase 14 | Complete |
| MATCH-01 | Phase 15 | Complete |
| MATCH-02 | Phase 15 | Complete |
| MATCH-03 | Phase 15 | Complete |
| MATCH-04 | Phase 15 | Complete |
| MATCH-05 | Phase 15 | Complete |
| MATCH-06 | Phase 15 | Complete |
| MATCH-07 | Phase 15 | Complete |
| MATCH-08 | Phase 15 | Complete |
| OUT-01 | Phase 15 | Complete |
| OUT-02 | Phase 15 | Complete |
| OUT-03 | Phase 15 | Complete |
| OUT-04 | Phase 15 | Complete |
| OUT-05 | Phase 15 | Complete |
| OUT-06 | Phase 15 | Complete |
| OUT-07 | Phase 15 | Complete |
| PROV-01 | Phase 15 | Complete |
| PROV-02 | Phase 15 | Complete |
| PROV-03 | Phase 15 | Complete |
| PROV-04 | Phase 15 | Complete |
| PROV-05 | Phase 15 | Complete |
| API-01 | Phase 16 | Complete |
| API-02 | Phase 16 | Complete |
| API-03 | Phase 16 | Complete |
| API-04 | Phase 16 | Complete |
| UI-01 | Phase 4 | Pending |
| UI-02 | Phase 4 | Pending |
| UI-03 | Phase 4 | Pending |
| UI-04 | Phase 4 | Pending |
| UI-05 | Phase 4 | Pending |
| EDGE-01 | Phase 15 | Complete |
| EDGE-02 | Phase 15 | Complete |
| EDGE-03 | Phase 15 | Complete |
| EDGE-04 | Phase 15 | Complete |

**Coverage:**
- v4.0 requirements: 38 total
- Mapped to phases: 38
- Unmapped: 0

---
*Requirements defined: 2026-02-04*
*Last updated: 2026-02-04 - Phases 14-16 complete, API layer ready*
