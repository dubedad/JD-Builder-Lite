# Roadmap: JD Builder Lite v3.0

## Overview

v3.0 adds style-enhanced writing capabilities to JD Builder Lite. The milestone delivers vocabulary-constrained style transfer: learning writing patterns from example JDs and generating styled sentences that use ONLY NOC vocabulary while maintaining full TBS Directive compliance. The journey starts with vocabulary foundation (enabling constraint enforcement), proceeds through style analysis and provenance architecture (schema before generation), then implements constrained generation with retry logic, and concludes with styled export formats.

## Milestones

- **v3.0 Style-Enhanced Writing** - Phases 9-13 (in progress)

## Phases

**Phase Numbering:**
- Integer phases (9, 10, 11...): Planned milestone work
- Decimal phases (9.1, 9.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 9: Vocabulary Foundation** - Build term index from JobForge parquet for constraint enforcement
- [ ] **Phase 10: Style Analysis Pipeline** - PDF/DOCX parsing, style profile extraction and management
- [ ] **Phase 11: Provenance Architecture** - Extended audit trail schema for styled content
- [ ] **Phase 12: Constrained Generation** - Few-shot styling with vocabulary validation and retry
- [ ] **Phase 13: Export Enhancement** - Styled statements in PDF/DOCX with dual-format display

## Phase Details

### Phase 9: Vocabulary Foundation
**Goal**: System can validate any text against NOC vocabulary index
**Depends on**: Nothing (first phase of v3.0)
**Requirements**: STYLE-03
**Success Criteria** (what must be TRUE):
  1. System loads vocabulary from JobForge parquet files (abilities, skills, knowledges, work activities)
  2. System can check if a given word exists in the NOC vocabulary index
  3. System can identify non-NOC words in any input text
  4. Vocabulary index loads at app startup without blocking user interaction
**Plans**: 1 plan

Plans:
- [ ] 09-01-PLAN.md - VocabularyIndex + VocabularyValidator + hot-reload watcher

### Phase 10: Style Analysis Pipeline
**Goal**: User can upload example JDs and view extracted style characteristics
**Depends on**: Nothing (can parallel Phase 9)
**Requirements**: STYLE-01, STYLE-02, STYLE-04, STYLE-05, STYLE-06, STYLE-07
**Success Criteria** (what must be TRUE):
  1. User can upload PDF example JDs and see extracted text content
  2. User can upload DOCX example JDs and see extracted text content
  3. User can view identified writing patterns (sentence structure, phrasing conventions) before generation
  4. System saves style profiles that persist across browser sessions
  5. User can select from previously saved style profiles
**Plans**: TBD

Plans:
- [ ] 10-01: PDF/DOCX parsing
- [ ] 10-02: Style profile extraction and persistence

### Phase 11: Provenance Architecture
**Goal**: Audit trail schema supports styled content with differentiated AI disclosure
**Depends on**: Nothing (can parallel Phases 9-10, MUST complete before Phase 12)
**Requirements**: PROV-01, PROV-02, PROV-03, PROV-04, PROV-05
**Success Criteria** (what must be TRUE):
  1. Styled output is linked to its original NOC statement ID in audit trail
  2. Export differentiates "AI-styled" from "AI-generated" content with distinct labels
  3. Original NOC statements are always preserved alongside styled variants
  4. Export includes vocabulary audit section showing which NOC terms were used
  5. Export includes generation metadata (style profile, confidence scores, retry counts)
**Plans**: TBD

Plans:
- [ ] 11-01: Extended provenance schema
- [ ] 11-02: AI disclosure differentiation

### Phase 12: Constrained Generation
**Goal**: System generates styled sentences using few-shot prompting with vocabulary validation
**Depends on**: Phase 9 (vocabulary), Phase 11 (provenance)
**Requirements**: GEN-01, GEN-02, GEN-03, GEN-04, GEN-05, GEN-06, GEN-07, GEN-08
**Success Criteria** (what must be TRUE):
  1. System generates styled variants for selected NOC statements using few-shot prompting
  2. System validates generated text and rejects sentences containing non-NOC words
  3. System automatically retries generation when vocabulary validation fails
  4. System falls back to original NOC statement when retry budget exhausted
  5. UI displays both authoritative NOC statement and styled variant side-by-side
  6. System shows confidence score for each styled sentence
  7. User can regenerate individual styled sentences
  8. System verifies semantic equivalence is preserved during styling
**Plans**: TBD

Plans:
- [ ] 12-01: Few-shot prompt construction
- [ ] 12-02: Vocabulary validation and retry logic
- [ ] 12-03: Dual-format UI and per-statement controls

### Phase 13: Export Enhancement
**Goal**: PDF/DOCX exports include styled statements with full compliance metadata
**Depends on**: Phase 12 (constrained generation)
**Requirements**: EXP-01, EXP-02, EXP-03
**Success Criteria** (what must be TRUE):
  1. PDF export includes styled statements with dual-format display (original + styled)
  2. DOCX export includes styled statements with dual-format display (original + styled)
  3. Compliance appendix includes style-enhanced content metadata and vocabulary audit
**Plans**: TBD

Plans:
- [ ] 13-01: Styled export implementation

## Progress

**Execution Order:**
Phases execute in numeric order: 9 -> 10 -> 11 -> 12 -> 13
Note: Phases 9, 10, 11 can execute in parallel; Phase 12 requires 9 and 11 complete.

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 9. Vocabulary Foundation | 0/1 | Planned | - |
| 10. Style Analysis Pipeline | 0/2 | Not started | - |
| 11. Provenance Architecture | 0/2 | Not started | - |
| 12. Constrained Generation | 0/3 | Not started | - |
| 13. Export Enhancement | 0/1 | Not started | - |

---
*Roadmap created: 2026-02-03*
*Milestone: v3.0 Style-Enhanced Writing*
