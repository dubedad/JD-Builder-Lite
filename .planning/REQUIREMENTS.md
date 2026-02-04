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

- [ ] **MATCH-01**: Extract primary purpose from JD using Client-Service Results and Key Activities
- [ ] **MATCH-02**: Shortlist candidate occupational groups based on JD inclusions (labels.csv)
- [ ] **MATCH-03**: Evaluate definition fit holistically (not keyword matching) per TBS guide
- [ ] **MATCH-04**: Check inclusion statements — link to definition when used
- [ ] **MATCH-05**: Check exclusion statements — confirm they don't reflect primary purpose
- [ ] **MATCH-06**: Perform comparative checks with benchmark positions when doubt exists
- [ ] **MATCH-07**: Produce ranked top-3 recommendations with confidence scores (0.0-1.0)
- [ ] **MATCH-08**: Handle "multiple groups plausible" case with best-fit resolution

### Output — Recommendations & Rationale

- [ ] **OUT-01**: Output allocated_group with allocation_confidence score
- [ ] **OUT-02**: Output primary_purpose_summary (why position exists)
- [ ] **OUT-03**: Output evidence_index with pointers to JD text spans used
- [ ] **OUT-04**: Output definition_fit_rationale explaining why chosen group fits
- [ ] **OUT-05**: Output inclusion_check showing applied statements or "none applies"
- [ ] **OUT-06**: Output exclusion_check confirming exclusions don't apply
- [ ] **OUT-07**: Output constraints_compliance statement: "evaluated work, not person"

### Policy Provenance — Traceability

- [ ] **PROV-01**: Provenance map linking each decision rule to authoritative source paragraphs
- [ ] **PROV-02**: Label authoritative text paragraphs (P1, P2, P3...) for reference
- [ ] **PROV-03**: Each output includes source_snippet and explanation_of_mapping
- [ ] **PROV-04**: Traceable to TBS Classification Policy (allocation method)
- [ ] **PROV-05**: Traceable to Directive on Automated Decision Making (DADM)

### API Layer

- [ ] **API-01**: POST /api/allocate accepts JD data, returns allocation recommendations
- [ ] **API-02**: Response includes full provenance map
- [ ] **API-03**: Response includes confidence scores and rationale for each recommendation
- [ ] **API-04**: Handle edge cases: "Needs Work Description Clarification", "Invalid Combination of Work"

### UI Layer — Recommendations Display

- [ ] **UI-01**: Display top-3 ranked group recommendations with confidence bars
- [ ] **UI-02**: Show rationale for each recommendation (expandable)
- [ ] **UI-03**: Show evidence links to JD text spans (highlight on click)
- [ ] **UI-04**: Show provenance chain to authoritative source
- [ ] **UI-05**: Display "Classification Step 1 Complete" status with next steps

### Troubleshooting & Edge Cases

- [ ] **EDGE-01**: Handle AP vs TC disambiguation (theoretical vs practical knowledge)
- [ ] **EDGE-02**: Handle "work appears in more than one group" cases
- [ ] **EDGE-03**: Detect and flag "Invalid Combination of Work" (same JD used for multiple groups)
- [ ] **EDGE-04**: Generate remediation checklist when JD quality insufficient

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
| DATA-01 | Phase 1 | Pending |
| DATA-02 | Phase 1 | Pending |
| DATA-03 | Phase 1 | Pending |
| DATA-04 | Phase 1 | Pending |
| DATA-05 | Phase 1 | Pending |
| MATCH-01 | Phase 2 | Pending |
| MATCH-02 | Phase 2 | Pending |
| MATCH-03 | Phase 2 | Pending |
| MATCH-04 | Phase 2 | Pending |
| MATCH-05 | Phase 2 | Pending |
| MATCH-06 | Phase 2 | Pending |
| MATCH-07 | Phase 2 | Pending |
| MATCH-08 | Phase 2 | Pending |
| OUT-01 | Phase 2 | Pending |
| OUT-02 | Phase 2 | Pending |
| OUT-03 | Phase 2 | Pending |
| OUT-04 | Phase 2 | Pending |
| OUT-05 | Phase 2 | Pending |
| OUT-06 | Phase 2 | Pending |
| OUT-07 | Phase 2 | Pending |
| PROV-01 | Phase 2 | Pending |
| PROV-02 | Phase 2 | Pending |
| PROV-03 | Phase 2 | Pending |
| PROV-04 | Phase 2 | Pending |
| PROV-05 | Phase 2 | Pending |
| API-01 | Phase 3 | Pending |
| API-02 | Phase 3 | Pending |
| API-03 | Phase 3 | Pending |
| API-04 | Phase 3 | Pending |
| UI-01 | Phase 4 | Pending |
| UI-02 | Phase 4 | Pending |
| UI-03 | Phase 4 | Pending |
| UI-04 | Phase 4 | Pending |
| UI-05 | Phase 4 | Pending |
| EDGE-01 | Phase 2 | Pending |
| EDGE-02 | Phase 2 | Pending |
| EDGE-03 | Phase 2 | Pending |
| EDGE-04 | Phase 2 | Pending |

**Coverage:**
- v4.0 requirements: 38 total
- Mapped to phases: 38
- Unmapped: 0

---
*Requirements defined: 2026-02-04*
*Last updated: 2026-02-04 - Initial v4.0 Occupational Group Allocation*
