# Requirements: JD Builder Lite v4.1 Polish

**Defined:** 2026-02-06
**Core Value:** Every piece of content in the final job description can be traced back to its authoritative source (NOC/OASIS), with clear documentation of human decisions and AI involvement.

## v4.1 Requirements

Requirements for exec-ready demo polish. Each maps to roadmap phases.

### Tab Restructure

- [x] **TAB-01**: Skills, Abilities, and Knowledge display as 3 separate profile tabs (currently lumped under Skills)
- [x] **TAB-02**: Core Competencies has its own dedicated profile tab (currently inside Overview section)
- [x] **TAB-03**: Navy blue description section moves inside the Overview tab content (currently floats above tabs)
- [x] **TAB-04**: Feeder Group Mobility & Career Progression content consolidates into Overview tab
- [x] **TAB-05**: Other Job Information content consolidates into Overview tab
- [x] **TAB-06**: Feeder Group Mobility, Career Progression, and Other Job Information tabs are removed after content migration

### Navigation

- [ ] **NAV-01**: Preview screen shows "Classify" button as navigation option alongside Export and Return to Builder
- [ ] **NAV-02**: Preview screen "Back to Edit" becomes "Return to Builder" and navigates to profile page with all selections preserved
- [ ] **NAV-03**: Classification results screen has "Return to Builder" button that returns to profile page with selections preserved

### Coaching UX

- [ ] **UX-01**: Invalid Combination classification result displays as informational/coaching style (blue or amber), not red error
- [ ] **UX-02**: Invalid Combination explains WHY the combination is invalid (conflicting signals, mismatched work types)
- [ ] **UX-03**: Invalid Combination suggests what to adjust (which statements conflict, what elements are missing)
- [ ] **UX-04**: Invalid Combination includes "Return to Builder" button for refinement

### Data Display

- [x] **DISP-01**: Level circles display dimension type label alongside the rating (e.g., "Proficiency: 4/5", "Importance: 3/5", "Frequency: 5/5")
- [x] **DISP-02**: Dimension type derived from guide.csv scale definitions per category (Skills=Proficiency, Abilities=Proficiency, Knowledge=Knowledge Level, Work Activities=Complexity, Personal Attributes=Importance, Work Context=varies)
- [x] **DISP-03**: Occupational category filter shows sub-major group and minor group headings the user can filter by

### Export

- [ ] **EXP-01**: Classification results (OG recommendations, confidence scores, rationale, evidence) exportable as part of JD export
- [ ] **EXP-02**: Exported classification section includes provenance metadata (model, timestamp, input statements)

### Housekeeping

- [ ] **DOC-01**: GitHub README updated to reflect v4.0 state, current architecture, setup instructions, and shipped features

## Future Requirements

Deferred to v5.0+ milestones.

### Classification Step 2 (v5.0)

- **JES-01**: Job Evaluation Standards scoring per occupational group
- **JES-02**: Benchmark position comparison UI
- **JES-03**: Manager consultation workflow

### Blocked by S1-10 -- JobForge Gold Integration

- **JFG-01**: Primary data source switches from OASIS scraping to JobForge gold parquet (S1-10)
- **JFG-02**: Match rationale specifies WHERE in NOC hierarchy match occurred (S1-03)
- **JFG-03**: Matching search criteria shows actual matched content in result cards (S1-04)
- **JFG-04**: Sort by matched NOC attribute (S1-05)
- **JFG-05**: Search quality improvement -- match across all NOC text fields (S1-12)
- **JFG-06**: Match Type filter (requires local data) (S1-11 partial)
- **JFG-07**: Job Family / Managerial Level filters from JobForge (S1-11 partial)

## Out of Scope

| Feature | Reason |
|---------|--------|
| JobForge gold integration (S1-10) | Architectural SEED -- prerequisite for blocked enhancements, separate milestone |
| Multi-result selection (S1-09) | Significant flow change -- changes JD assembly architecture |
| RAG enrichment (S5-03) | SEED -- requires multi-source integration infrastructure |
| Bubble matrix (S5-06) | SEED -- requires JobForge gold data for granularity dimension |
| PuMP formalization (S5-11) | SEED -- measurement framework design, separate initiative |
| CAF taxonomy (S1-08) | SEED -- new taxonomy integration |
| Search from JobForge tables (S1-06) | SEED -- requires JobForge lookup table |
| Semantic/fuzzy search | Requires local data source (S1-10) |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| TAB-01 | Phase 18 | Complete |
| TAB-02 | Phase 18 | Complete |
| TAB-03 | Phase 18 | Complete |
| TAB-04 | Phase 18 | Complete |
| TAB-05 | Phase 18 | Complete |
| TAB-06 | Phase 18 | Complete |
| NAV-01 | Phase 19 | Pending |
| NAV-02 | Phase 19 | Pending |
| NAV-03 | Phase 19 | Pending |
| UX-01 | Phase 19 | Pending |
| UX-02 | Phase 19 | Pending |
| UX-03 | Phase 19 | Pending |
| UX-04 | Phase 19 | Pending |
| DISP-01 | Phase 18 | Complete |
| DISP-02 | Phase 18 | Complete |
| DISP-03 | Phase 18 | Complete |
| EXP-01 | Phase 19 | Pending |
| EXP-02 | Phase 19 | Pending |
| DOC-01 | Phase 19 | Pending |

**Coverage:**
- v4.1 requirements: 19 total
- Mapped to phases: 19
- Unmapped: 0

---
*Requirements defined: 2026-02-06*
*Last updated: 2026-02-07 -- Phase 18 requirements (TAB-01..06, DISP-01..03) marked Complete*
