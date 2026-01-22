# Requirements: JD Builder Lite

**Defined:** 2025-01-21
**Core Value:** Every piece of content in the final job description can be traced back to its authoritative source (NOC/OASIS), with clear documentation of human decisions and AI involvement.

## v1 Requirements

Requirements for initial demo release.

### Search & Selection

- [x] **SRCH-01**: Manager can enter a job title and search OASIS for matching Occupational Profiles
- [x] **SRCH-02**: App displays search results showing NOC codes and profile names
- [x] **SRCH-03**: Manager can select an Occupational Profile from the results menu

### Data Acquisition

- [x] **DATA-01**: App scrapes all relevant NOC data from selected profile (Overview, Work Characteristics, Skills & Abilities, Interests, Employment Requirements, Skills for Success)
- [x] **DATA-02**: App extracts and stores metadata from scraped pages (NOC code, profile URL, retrieval timestamp, any version info)

### Data Display & Selection

- [x] **DISP-01**: App presents NOC data organized by JD Element headers (Key Activities, Skills, Effort, Responsibility, Working Conditions)
- [x] **DISP-02**: Manager can select multiple statements under each JD Element header
- [x] **DISP-03**: App tracks which NOC source attribute each statement came from

### AI Generation

- [ ] **AI-01**: App generates a General Overview section using OpenAI API, informed by all selected statements
- [ ] **AI-02**: App records AI generation metadata (model used, timestamp, input statements)

### Output & Compliance

- [ ] **OUT-01**: App displays a preview of the assembled job description
- [ ] **OUT-02**: Manager can export the final JD to PDF
- [ ] **OUT-03**: Final JD includes compliance metadata block (NOC code, source URLs, retrieval timestamp, page metadata)
- [ ] **OUT-04**: Final JD includes full audit trail (manager's selections per JD Element, traced to NOC source)
- [ ] **OUT-05**: Final JD includes AI disclosure (General Overview marked as AI-generated, inputs listed, model and timestamp documented)

## v2 Requirements

Deferred to future iterations.

### Data Display Enhancements

- **DISP-04**: Annex section with excluded NOC attributes (job requirements, career mobility, example titles, labels, leading statements, interests, personal attributes)
- **DISP-05**: Inline source attribution visible during selection

### Organizational Context

- **ORG-01**: Client Service Results section (requires org-specific business capability data)
- **ORG-02**: Organizational Context section (requires org-specific mandate/ID data)

### UI Polish

- **UI-01**: Search result count and NOC data version display
- **UI-02**: Loading states and progress indicators
- **UI-03**: Error messages and recovery guidance

## Out of Scope

| Feature | Reason |
|---------|--------|
| User authentication | Single user demo only |
| Database/persistence | No saved history needed — create -> PDF -> done |
| Multi-user support | Demo purposes only |
| Cloud hosting | Runs locally only |
| Template library | Scope creep — manager selects from NOC data |
| Bias detection | Enterprise feature, out of demo scope |
| ATS integration | Enterprise feature, out of demo scope |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| SRCH-01 | Phase 1 | Complete |
| SRCH-02 | Phase 1 | Complete |
| SRCH-03 | Phase 1 | Complete |
| DATA-01 | Phase 1 | Complete |
| DATA-02 | Phase 1 | Complete |
| DISP-01 | Phase 2 | Complete |
| DISP-02 | Phase 2 | Complete |
| DISP-03 | Phase 2 | Complete |
| AI-01 | Phase 3 | Pending |
| AI-02 | Phase 3 | Pending |
| OUT-01 | Phase 4 | Pending |
| OUT-02 | Phase 4 | Pending |
| OUT-03 | Phase 4 | Pending |
| OUT-04 | Phase 4 | Pending |
| OUT-05 | Phase 4 | Pending |

**Coverage:**
- v1 requirements: 15 total
- Mapped to phases: 15
- Unmapped: 0

---
*Requirements defined: 2025-01-21*
*Last updated: 2026-01-21 after roadmap creation*
