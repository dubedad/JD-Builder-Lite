# Resume Context: v5.0 Job Evaluation Standard Application

**Paused:** 2026-02-04
**Last Milestone:** v4.0 Occupational Group Allocation (SHIPPED)
**Next Milestone:** v5.0 Job Evaluation Standard Application

---

## What Was Accomplished in v4.0

- **Classification Step 1 COMPLETE**: Occupational Group Allocation
- DIM_OCCUPATIONAL table: 426 groups, 900 inclusions, 330 exclusions
- POST /api/allocate endpoint with confidence scoring
- Recommendation cards UI with expandable rationale
- Full policy provenance to TBS Classification Policy and DADM

---

## v5.0 Vision: Complete TBS Classification Automation

v5.0 will implement **TBS Classification Step 5: Apply Job Evaluation Standard** to determine the specific level (e.g., EC-04, CS-03) within the allocated occupational group.

### The TBS 5-Step Process (Policy Provenance: [GUIDE-S2])

| Step | Description | Status |
|------|-------------|--------|
| 1 | Review Work Description | ✓ v1.0-v3.0 |
| 2 | Identify Primary Purpose → Allocate to Group | ✓ v4.0 |
| 3 | Check Selection Against Group Definitions | ✓ v4.0 |
| 4 | Allocate to Subgroup (if applicable) | ✓ v4.0 |
| **5** | **Apply Job Evaluation Standard → Determine Level** | **v5.0** |

---

## Key Research Documents (READ THESE FIRST)

### Critical for v5.0 Planning

1. **`.planning/research/TBS-CLASSIFICATION-PROCESS.md`**
   - Complete TBS classification methodology with policy provenance
   - ASCII BPMN swimlane diagram
   - Gap analysis for v5.0

2. **`.planning/research/TBS-CLASSIFICATION-BPMN.md`**
   - Mermaid BPMN diagram for rendering
   - Swimlanes: Manager, JD Builder, JobForge, Classification Advisor, Data Sources, Gold Tables

3. **`.planning/research/V5.0-DATA-REQUEST.md`**
   - Formal data specification for client
   - Required fields for: Org Context, CSR, JES
   - Sample CSV/Excel structures

4. **`.planning/research/BENCHMARK-POSITIONS-RESEARCH.md`**
   - **KEY FINDING**: Benchmarks ARE publicly available in TBS standard documents
   - EC: 19 benchmarks, EX: 72 benchmarks
   - Schema for dim_benchmark_position table
   - Scraping strategy from canada.ca

---

## Data Dependencies for v5.0

| # | Data Needed | Source | Status |
|---|-------------|--------|--------|
| 1 | Organizational Context | Client provides | BLOCKED - waiting on client |
| 2 | Client-Service Results | Client provides | BLOCKED - waiting on client |
| 3 | Job Evaluation Standards | Client provides / scrape TBS | BLOCKED - waiting on client |
| 4 | Benchmark Positions | Scrape from canada.ca | **AVAILABLE** - no dependency |

### Data Request Sent to Client

The formal data specification is in `.planning/research/V5.0-DATA-REQUEST.md`. Client needs to provide:
- Org codes, unit codes, mandates, supervisor relationships
- CSR templates or statement library by classification
- JES factors, degrees, point values, level ranges

---

## Architecture Ideas for v5.0

### New Gold Tables Needed

```sql
-- Job Evaluation Standards
dim_job_eval_standard (standard_code, name, total_points, effective_date)
dim_factor (standard_code, factor_code, factor_name, criterion, max_points)
dim_degree (standard_code, factor_code, degree_number, points, description)
dim_level_range (standard_code, level_code, min_points, max_points)

-- Benchmark Positions (CAN SCRAPE NOW)
dim_benchmark_position (standard_code, benchmark_number, position_title,
                        level_code, total_points, factor_scores,
                        point_breakdown, source_url, scraped_at)

-- Organizational Context
dim_organization (org_code, org_name)
dim_org_unit (unit_code, org_code, unit_name, mandate, parent_unit_code)

-- Client-Service Results
dim_csr_template (group_code, level, csr_template, typical_clients, typical_outcomes)
```

### Scoring Engine Concept

```
Input: JD content + allocated group (from v4.0)
Process:
  1. Load JES for allocated group
  2. For each factor:
     a. Match JD content to degree descriptors
     b. Assign degree (with confidence)
     c. Calculate points
  3. Sum total points
  4. Map to level via level_range table
  5. Compare to benchmark positions
Output: Recommended level + factor breakdown + benchmark comparison
```

---

## Policy Provenance Standards

A global skill was created for mapping policy provenance: `~/.claude/skills/mapping-policy-provenance/`

### Labeling Convention

```
[SOURCE-SECTION.PARAGRAPH]

Examples:
- [GUIDE-S2.P1] - Guide to Allocating Positions, Section 2, Paragraph 1
- [DOC-B.2.2.1] - Directive on Classification, Appendix B, Section 2.2.1
- [JES-EC-DM-D5] - EC Job Evaluation Standard, Decision Making factor, Degree 5
- [DADM-6.2.3] - Directive on Automated Decision-Making, Section 6.2.3
```

### Key Policy References

| Code | Document | URL |
|------|----------|-----|
| GUIDE | Guide to Allocating Positions | canada.ca/...guide-allocating-positions... |
| DOC | Directive on Classification | tbs-sct.canada.ca/pol/doc-eng.aspx?id=28700 |
| JES | Job Evaluation Standards | canada.ca/...job-evaluation-standards... |
| DADM | Directive on Automated Decision-Making | tbs-sct.canada.ca/pol/doc-eng.aspx?id=32592 |

---

## UI Ideas Discussed

### "Predict Classified Group" Button (PRESTO)

A shortcut button on the Export page that bypasses JD building and goes straight to allocation results. Allows users to quickly get classification predictions without completing the full JD workflow.

- Should be added to Phase 17 (UI Layer) scope
- Navigation bar updates needed
- From export page, button triggers allocation API directly

---

## Value Proposition (for pitching v5.0)

**For** Government of Canada HR advisors and hiring managers **who** struggle to write compliant, well-structured job descriptions that align with TBS classification standards,

**our** Job Builder Lite **provides** classification-ready job descriptions in minutes

**by** pulling from authoritative NOC/OASIS profiles and guiding users through a 5-step builder with AI-assisted content generation.

**As opposed to** manual JD writing using Word templates, copy-pasting from old JDs, and guesswork on classification alignment,

**our** Job Builder Lite **embeds TBS policy provenance directly into the workflow, automatically maps duties to occupational groups, and provides transparent allocation recommendations with full audit trails for DADM compliance**.

---

## Terminal UAT Test Suite

Created `tests/uat_terminal.py` - a terminal-based UAT test suite that doesn't require screenshots or Playwright:

```bash
python tests/uat_terminal.py
```

Tests API endpoints, homepage elements, search/profile APIs, allocation API, and export endpoints.

---

## Known Issues

1. **Claude Code B: drive error** - The Bun runtime has cached paths from a B: drive that no longer exists. Fix: `npm uninstall -g @anthropic-ai/claude-code && npm install -g @anthropic-ai/claude-code`

2. **NOC code 21232 invalid** - Use 21211 (Data Engineers) for testing instead

3. **Allocation API timeout** - LLM calls can take >30s; test suite uses 60s timeout

---

## Next Actions When Resuming

1. **Check if client provided data** - Items 1, 2, 3 from data request
2. **If data available**: Start v5.0 milestone planning with `/gsd:new-milestone`
3. **If data not available**:
   - Start benchmark scraping (no dependency)
   - Create dim_benchmark_position table
   - Scrape EC (19) and EX (72) benchmarks from canada.ca
4. **Consider**: Adding "Predict" button to current v4.0 as quick enhancement

---

## Files to Read on Resume

**Priority 1 (Must Read):**
```
.planning/PROJECT.md
.planning/RESUME-CONTEXT-v5.0.md (this file)
.planning/research/TBS-CLASSIFICATION-PROCESS.md
.planning/research/V5.0-DATA-REQUEST.md
```

**Priority 2 (Context):**
```
.planning/research/BENCHMARK-POSITIONS-RESEARCH.md
.planning/research/TBS-CLASSIFICATION-BPMN.md
.planning/milestones/v4.0-ROADMAP.md
```

**Priority 3 (Reference):**
```
~/.claude/skills/mapping-policy-provenance/SKILL.md
tests/uat_terminal.py
```

---

*Context paused: 2026-02-04*
*Ready for: v5.0 Job Evaluation Standard Application*
