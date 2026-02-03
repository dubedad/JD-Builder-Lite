# Requirements: JD Builder Lite v3.0

**Defined:** 2026-02-03
**Core Value:** Every piece of content in the final job description can be traced back to its authoritative source (NOC/OASIS), with clear documentation of human decisions and AI involvement.

## v3.0 Requirements: Style-Enhanced Writing

Requirements for style-enhanced JD generation with vocabulary constraints.

### Style Infrastructure

- [ ] **STYLE-01**: System can parse PDF example JDs to extract text content
- [ ] **STYLE-02**: System can parse DOCX example JDs to extract text content
- [ ] **STYLE-03**: System builds vocabulary index from JobForge parquet files (abilities, skills, knowledges, work activities)
- [ ] **STYLE-04**: System analyzes extracted JD text to identify writing patterns (sentence structure, phrasing conventions)
- [ ] **STYLE-05**: User can view extracted style characteristics before generation
- [ ] **STYLE-06**: System persists style profiles for reuse across sessions
- [ ] **STYLE-07**: User can select from saved style profiles

### Constrained Generation

- [ ] **GEN-01**: System generates styled sentence for each selected NOC statement using few-shot prompting
- [ ] **GEN-02**: System validates generated text against NOC vocabulary index (reject non-NOC words)
- [ ] **GEN-03**: System retries generation (up to N attempts) when vocabulary validation fails
- [ ] **GEN-04**: System falls back to original NOC statement when retry budget exhausted (graceful degradation)
- [ ] **GEN-05**: UI displays dual-format: authoritative NOC statement alongside styled variant
- [ ] **GEN-06**: System performs semantic equivalence checking to verify meaning preserved
- [ ] **GEN-07**: User can regenerate individual styled sentences (per-statement control)
- [ ] **GEN-08**: System displays confidence score for each styled sentence

### Compliance & Provenance

- [ ] **PROV-01**: Audit trail extends to track styled output linked to original NOC statement ID
- [ ] **PROV-02**: Export includes differentiated AI disclosure ("AI-styled" vs "AI-generated")
- [ ] **PROV-03**: Original NOC statements always preserved in export alongside styled variants
- [ ] **PROV-04**: Export includes vocabulary audit section showing NOC terms used
- [ ] **PROV-05**: Export includes generation metadata (style profile used, confidence scores, retry counts)

### Export Enhancement

- [ ] **EXP-01**: PDF export includes styled statements with dual-format display
- [ ] **EXP-02**: DOCX export includes styled statements with dual-format display
- [ ] **EXP-03**: Export compliance appendix updated for style-enhanced content

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
| Automatic style selection | User must explicitly choose style profile (transparency requirement) |
| OCR for scanned PDFs | Adds complexity; assume example JDs are text-based PDFs |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| STYLE-01 | TBD | Pending |
| STYLE-02 | TBD | Pending |
| STYLE-03 | TBD | Pending |
| STYLE-04 | TBD | Pending |
| STYLE-05 | TBD | Pending |
| STYLE-06 | TBD | Pending |
| STYLE-07 | TBD | Pending |
| GEN-01 | TBD | Pending |
| GEN-02 | TBD | Pending |
| GEN-03 | TBD | Pending |
| GEN-04 | TBD | Pending |
| GEN-05 | TBD | Pending |
| GEN-06 | TBD | Pending |
| GEN-07 | TBD | Pending |
| GEN-08 | TBD | Pending |
| PROV-01 | TBD | Pending |
| PROV-02 | TBD | Pending |
| PROV-03 | TBD | Pending |
| PROV-04 | TBD | Pending |
| PROV-05 | TBD | Pending |
| EXP-01 | TBD | Pending |
| EXP-02 | TBD | Pending |
| EXP-03 | TBD | Pending |

**Coverage:**
- v3.0 requirements: 23 total
- Mapped to phases: 0
- Unmapped: 23

---
*Requirements defined: 2026-02-03*
*Last updated: 2026-02-03 after initial definition*
