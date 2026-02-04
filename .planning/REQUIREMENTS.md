# Requirements: JD Builder Lite v3.0

**Defined:** 2026-02-03
**Core Value:** Every piece of content in the final job description can be traced back to its authoritative source (NOC/OASIS), with clear documentation of human decisions and AI involvement.

## v3.0 Requirements: Style-Enhanced Writing

Requirements for style-enhanced JD generation with vocabulary constraints.

### Style Infrastructure

- [x] **STYLE-01**: Style patterns documented from analysis of example JD corpus (`Examples of Job Descriptions/`)
- [x] **STYLE-02**: Few-shot examples created from corpus for generation prompts
- [x] **STYLE-03**: System builds vocabulary index from JobForge parquet files (abilities, skills, knowledges, work activities)
- [x] **STYLE-04**: Style rules implemented as code constants for runtime prompt construction

### Constrained Generation

- [x] **GEN-01**: System generates styled sentence for each selected NOC statement using few-shot prompting
- [x] **GEN-02**: System validates generated text against NOC vocabulary index (reject non-NOC words)
- [x] **GEN-03**: System retries generation (up to N attempts) when vocabulary validation fails
- [x] **GEN-04**: System falls back to original NOC statement when retry budget exhausted (graceful degradation)
- [x] **GEN-05**: UI displays dual-format: authoritative NOC statement alongside styled variant
- [x] **GEN-06**: System performs semantic equivalence checking to verify meaning preserved
- [x] **GEN-07**: User can regenerate individual styled sentences (per-statement control)
- [x] **GEN-08**: System displays confidence score for each styled sentence

### Compliance & Provenance

- [x] **PROV-01**: Audit trail extends to track styled output linked to original NOC statement ID
- [x] **PROV-02**: Export includes differentiated AI disclosure ("AI-styled" vs "AI-generated")
- [x] **PROV-03**: Original NOC statements always preserved in export alongside styled variants
- [x] **PROV-04**: Export includes vocabulary audit section showing NOC terms used
- [x] **PROV-05**: Export includes generation metadata (confidence scores, retry counts, vocabulary coverage)

### Export Enhancement

- [x] **EXP-01**: PDF export includes styled statements with dual-format display
- [x] **EXP-02**: DOCX export includes styled statements with dual-format display
- [x] **EXP-03**: Export compliance appendix updated for style-enhanced content

## Future Requirements (v3.1+)

### Occupational Group Matching
- **OGM-01**: System scrapes TBS Occupational Groups table to build DIM_OCCUPATIONAL
- **OGM-02**: System matches JD inclusions/exclusions to occupational group definitions
- **OGM-03**: System ranks top 3 matches with confidence scores and rationale
- **OGM-04**: System provides policy provenance to TBS Allocation Guide
- **OGM-05**: System traces matching decision to DADM requirements

### Multi-Style Support
- **MSTYLE-01**: User can assign different styles to different JD sections
- **MSTYLE-02**: System supports style blending (combine multiple reference JDs)

## Out of Scope

| Feature | Reason |
|---------|--------|
| Fine-tuned custom models | Few-shot prompting sufficient; fine-tuning adds complexity without clear benefit |
| Real-time constrained decoding | OpenAI API limitation (logit_bias limited to ~300 tokens) |
| Style editing UI | Users accept/reject/regenerate, not edit styled text (maintains provenance) |
| User-uploaded style examples | Style learning happens during development from curated corpus, not at runtime |
| User-selectable style profiles | Single curated style; multi-style support deferred to v3.1+ |
| OCR for scanned PDFs | Adds complexity; example JDs are text-based PDFs analyzed during development |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| STYLE-01 | Phase 10 | Complete |
| STYLE-02 | Phase 10 | Complete |
| STYLE-03 | Phase 9 | Complete |
| STYLE-04 | Phase 10 | Complete |
| GEN-01 | Phase 12 | Complete |
| GEN-02 | Phase 12 | Complete |
| GEN-03 | Phase 12 | Complete |
| GEN-04 | Phase 12 | Complete |
| GEN-05 | Phase 12 | Complete |
| GEN-06 | Phase 12 | Complete |
| GEN-07 | Phase 12 | Complete |
| GEN-08 | Phase 12 | Complete |
| PROV-01 | Phase 11 | Complete |
| PROV-02 | Phase 11 | Complete |
| PROV-03 | Phase 11 | Complete |
| PROV-04 | Phase 11 | Complete |
| PROV-05 | Phase 11 | Complete |
| EXP-01 | Phase 13 | Complete |
| EXP-02 | Phase 13 | Complete |
| EXP-03 | Phase 13 | Complete |

**Coverage:**
- v3.0 requirements: 20 total
- Mapped to phases: 20
- Unmapped: 0

---
*Requirements defined: 2026-02-03*
*Last updated: 2026-02-03 - v3.0 requirements complete (20/20)*
