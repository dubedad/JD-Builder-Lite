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

- [x] **Phase 9: Vocabulary Foundation** - Build term index from JobForge parquet for constraint enforcement
- [x] **Phase 10: Style Analysis Pipeline** - Analyze example JD corpus, document patterns, build few-shot examples
- [x] **Phase 11: Provenance Architecture** - Extended audit trail schema for styled content
- [x] **Phase 12: Constrained Generation** - Few-shot styling with vocabulary validation and retry
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
- [x] 09-01-PLAN.md - VocabularyIndex + VocabularyValidator + hot-reload watcher

### Phase 10: Style Analysis Pipeline
**Goal**: Style patterns documented and few-shot examples ready for generation prompts
**Depends on**: Nothing (can parallel Phase 9)
**Requirements**: STYLE-01, STYLE-02, STYLE-04
**Success Criteria** (what must be TRUE):
  1. Example JD corpus analyzed (`Examples of Job Descriptions/` - 42 files, ~20 unique)
  2. Style patterns documented in `.planning/` (sentence structure, vocabulary patterns, section formatting)
  3. Few-shot examples created from corpus for generation prompts
  4. Key style rules implemented as code constants in `src/` for runtime prompt construction
**Plans**: 2 plans

Plans:
- [x] 10-01-PLAN.md - Corpus analysis and style documentation
- [x] 10-02-PLAN.md - Style constants and few-shot examples as code

### Phase 11: Provenance Architecture
**Goal**: Audit trail schema supports styled content with differentiated AI disclosure
**Depends on**: Nothing (can parallel Phases 9-10, MUST complete before Phase 12)
**Requirements**: PROV-01, PROV-02, PROV-03, PROV-04, PROV-05
**Success Criteria** (what must be TRUE):
  1. Styled output is linked to its original NOC statement ID in audit trail
  2. Export differentiates "AI-styled" from "AI-generated" content with distinct labels
  3. Original NOC statements are always preserved alongside styled variants
  4. Export includes vocabulary audit section showing which NOC terms were used
  5. Export includes generation metadata (confidence scores, retry counts, vocabulary coverage)
**Plans**: 2 plans

Plans:
- [x] 11-01-PLAN.md - Foundation provenance models (StyleContentType, VocabularyAudit, ConfidenceLevel)
- [x] 11-02-PLAN.md - Styled content models (StyledStatement, GenerationAttempt, StyleVersionHistory)

### Phase 12: Constrained Generation
**Goal**: System generates styled sentences using few-shot prompting with vocabulary validation
**Depends on**: Phase 9 (vocabulary), Phase 10 (style constants), Phase 11 (provenance)
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
**Plans**: 3 plans

Plans:
- [x] 12-01-PLAN.md - Semantic checker + Generation service with retry logic
- [x] 12-02-PLAN.md - API endpoint for styled statement generation
- [x] 12-03-PLAN.md - Dual-format UI with per-statement controls

### Phase 13: Export Enhancement
**Goal**: PDF/DOCX exports include styled statements with full compliance metadata
**Depends on**: Phase 12 (constrained generation)
**Requirements**: EXP-01, EXP-02, EXP-03
**Success Criteria** (what must be TRUE):
  1. PDF export includes styled statements with dual-format display (original + styled)
  2. DOCX export includes styled statements with dual-format display (original + styled)
  3. Compliance appendix includes style-enhanced content metadata and vocabulary audit
**Plans**: 3 plans

Plans:
- [ ] 13-01-PLAN.md - Export data model extension with StyledStatementExport
- [ ] 13-02-PLAN.md - PDF template and CSS for dual-format styled content
- [ ] 13-03-PLAN.md - DOCX generator for dual-format styled content

## Progress

**Execution Order:**
Phases execute in numeric order: 9 -> 10 -> 11 -> 12 -> 13
Note: Phases 9, 10, 11 can execute in parallel; Phase 12 requires 9, 10, and 11 complete.

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 9. Vocabulary Foundation | 1/1 | Complete | 2026-02-03 |
| 10. Style Analysis Pipeline | 2/2 | Complete | 2026-02-03 |
| 11. Provenance Architecture | 2/2 | Complete | 2026-02-03 |
| 12. Constrained Generation | 3/3 | Complete | 2026-02-03 |
| 13. Export Enhancement | 0/3 | Planned | - |

---
*Roadmap created: 2026-02-03*
*Last updated: 2026-02-03 - Phase 12 complete*
*Milestone: v3.0 Style-Enhanced Writing*
