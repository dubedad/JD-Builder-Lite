# TBS Job Classification - BPMN Swimlane Diagram

**Document Type:** BPMN 2.0 Compliant Process Map
**Created:** 2026-02-04
**Purpose:** Visual representation of end-to-end job classification automation

---

## Mermaid Swimlane Diagram

```mermaid
flowchart TB
    subgraph MANAGER["MANAGER"]
        M1[Initiate JD Request]
        M2[Provide Org Unit Context]
        M3[Review & Validate Results]
        M4[Accept or Appeal Decision]
    end

    subgraph JDBUILDER["JD BUILDER (Application)"]
        JD1[Search OASIS Profiles]
        JD2[Select NOC Profile]
        JD3[Select Statements per Tab]
        JD4[Generate Overview - LLM]
        JD5[Preview JD]
        JD6[Export PDF/DOCX]
        JD7["'Predict Classified Group' Button"]
        JD8[Call /api/allocate]
        JD9[Display Allocation Results]
    end

    subgraph JOBFORGE["JOBFORGE (Gold Tables / Matching Engine)"]
        JF1[Extract Primary Purpose]
        JF2[Semantic Shortlist Candidates]
        JF3[LLM Classify - Holistic Match]
        JF4[Check Inclusions/Exclusions]
        JF5[Allocate to Subgroup]
        JF6[Apply Job Evaluation Standard]
        JF7[Score Factors]
        JF8[Determine Level - Points to Level]
        JF9[Generate Provenance Map]
    end

    subgraph CLASSADVISOR["CLASSIFICATION ADVISOR (Human-in-Loop)"]
        CA1[Review Borderline Cases]
        CA2[Resolve AP vs TC Edge Cases]
        CA3[Approve Final Decision]
    end

    subgraph DATASOURCES["AUTHORITATIVE DATA SOURCES"]
        DS1[(OASIS / NOC - ESDC)]
        DS2[(TBS Group Definitions)]
        DS3[(Job Evaluation Standards)]
        DS4[(Table of Concordance)]
        DS5[(Benchmark Positions)]
        DS6[(Organizational Data - Dept)]
    end

    subgraph GOLDTABLES["DIM_OCCUPATIONAL (SQLite Gold Tables)"]
        GT1[dim_occupational_group]
        GT2[dim_occupational_inclusion]
        GT3[dim_occupational_exclusion]
        GT4[dim_job_eval_standard]
        GT5[dim_eval_factor]
        GT6[dim_benchmark_position]
        GT7[dim_org_context]
        GT8[scrape_provenance]
    end

    %% Manager Flow
    M1 --> M2
    M2 --> JD1
    M3 --> M4

    %% JD Builder Flow
    JD1 --> JD2
    JD2 --> JD3
    JD3 --> JD4
    JD4 --> JD5
    JD5 --> JD6
    JD6 --> JD7
    JD7 --> JD8
    JD8 --> JF1
    JD9 --> M3

    %% JobForge Flow
    JF1 --> JF2
    JF2 --> JF3
    JF3 --> JF4
    JF4 -->|Pass| JF5
    JF4 -->|Fail - Exclusion Match| JF2
    JF5 --> JF6
    JF6 --> JF7
    JF7 --> JF8
    JF8 --> JF9
    JF9 --> JD9

    %% Edge Case Flow
    JF3 -->|Borderline < 10%| CA1
    CA1 --> CA2
    CA2 --> CA3
    CA3 --> JF9

    %% Data Source to Gold Tables
    DS1 --> GT1
    DS2 --> GT1
    DS2 --> GT2
    DS2 --> GT3
    DS3 --> GT4
    DS3 --> GT5
    DS4 --> GT1
    DS5 --> GT6
    DS6 --> GT7

    %% Gold Tables to JobForge
    GT1 --> JF2
    GT2 --> JF4
    GT3 --> JF4
    GT4 --> JF6
    GT5 --> JF7
    GT6 --> JF6
    GT7 --> JF1
    GT8 --> JF9
```

---

## Swimlane Actors

| Lane | Actor | Role | Automation Status |
|------|-------|------|-------------------|
| **Manager** | Hiring Manager | Initiates request, provides context, validates results | Manual input required |
| **JD Builder** | JD Builder Lite Application | User interface for JD creation | ✓ Automated (v2.0) |
| **JobForge** | Matching Engine + Gold Tables | Classification logic and reference data | Partial (v4.0 = Steps 1-4) |
| **Classification Advisor** | HR Classification Specialist | Edge case resolution, final approval | Human-in-loop |
| **Data Sources** | External Authoritative Systems | TBS, ESDC, Departmental data | Scraped/imported |
| **Gold Tables** | DIM_OCCUPATIONAL Database | Normalized reference data with provenance | ✓ Automated (v4.0) |

---

## Process Steps by Lane

### Manager Lane

| Step | Activity | Input | Output | Automation |
|------|----------|-------|--------|------------|
| M1 | Initiate JD Request | Business need | Request created | Manual |
| M2 | Provide Org Unit Context | Organizational knowledge | Context data | Manual (v5.1 can pre-populate) |
| M3 | Review & Validate Results | Classification recommendation | Validation decision | Manual |
| M4 | Accept or Appeal Decision | Review outcome | Final decision | Manual |

### JD Builder Lane

| Step | Activity | Input | Output | Automation |
|------|----------|-------|--------|------------|
| JD1 | Search OASIS Profiles | Search query | Profile list | ✓ Automated |
| JD2 | Select NOC Profile | Profile selection | Selected profile | ✓ Automated |
| JD3 | Select Statements | Statement checkboxes | Selected statements | ✓ Automated |
| JD4 | Generate Overview | Selected statements | LLM overview | ✓ Automated |
| JD5 | Preview JD | All selections | JD preview | ✓ Automated |
| JD6 | Export PDF/DOCX | JD data | Exported document | ✓ Automated |
| JD7 | "Predict Classified Group" | Button click | API call trigger | v4.0 Phase 17 |
| JD8 | Call /api/allocate | JD data | API request | ✓ v4.0 API ready |
| JD9 | Display Allocation Results | API response | UI display | v4.0 Phase 17 |

### JobForge Lane

| Step | Activity | Input | Output | Automation |
|------|----------|-------|--------|------------|
| JF1 | Extract Primary Purpose | JD text | Purpose summary | ✓ v4.0 |
| JF2 | Semantic Shortlist | Purpose + definitions | Candidate groups | ✓ v4.0 |
| JF3 | LLM Classify | Candidates + JD | Ranked recommendations | ✓ v4.0 |
| JF4 | Check Inclusions/Exclusions | Recommendations | Verified/rejected | ✓ v4.0 |
| JF5 | Allocate to Subgroup | Verified group | Full allocation code | ✓ v4.0 |
| JF6 | Apply Job Evaluation Standard | Allocation + JD | Factor inputs | v5.0 |
| JF7 | Score Factors | Factor inputs | Point scores | v5.0 |
| JF8 | Determine Level | Total points | Classification level | v5.0 |
| JF9 | Generate Provenance Map | All decisions | Audit trail | ✓ v4.0 |

### Classification Advisor Lane

| Step | Activity | Input | Output | Automation |
|------|----------|-------|--------|------------|
| CA1 | Review Borderline Cases | Flagged recommendations | Review decision | Human-in-loop |
| CA2 | Resolve AP vs TC Edge Cases | Edge case details | Resolution | Human-in-loop |
| CA3 | Approve Final Decision | Review outcome | Ratified decision | Human-in-loop |

### Data Sources Lane

| Source | Type | Data Provided | Refresh Frequency |
|--------|------|---------------|-------------------|
| OASIS / NOC | ESDC Web | NOC profiles, tasks, skills, work context | Daily (live scrape) |
| TBS Group Definitions | TBS Web | 29 group definitions, inclusions, exclusions | Monthly |
| Job Evaluation Standards | TBS Web/PDF | Factor definitions, degree levels, points | Annually |
| Table of Concordance | TBS Web | Group ↔ Standard mapping, subgroups | Annually |
| Benchmark Positions | TBS Database | Pre-scored reference positions | As published |
| Organizational Data | Department | Org context, mandates, supervisor relationships | Real-time |

### Gold Tables Lane

| Table | Source | Records | Purpose |
|-------|--------|---------|---------|
| dim_occupational_group | TBS scrape | ~29 groups | Group definitions |
| dim_occupational_inclusion | TBS scrape | ~200 statements | Inclusion examples |
| dim_occupational_exclusion | TBS scrape | ~150 statements | Exclusion examples |
| dim_job_eval_standard | TBS (v5.0) | 18 standards | Evaluation standards |
| dim_eval_factor | TBS (v5.0) | ~150 factors | Factor definitions |
| dim_benchmark_position | TBS (v5.0) | TBD | Reference positions |
| dim_org_context | Dept (v5.1) | TBD | Organizational context |
| scrape_provenance | System | Per scrape | Data lineage |

---

## Gateway Decisions

| Gateway | Condition | True Path | False Path |
|---------|-----------|-----------|------------|
| Exclusion Check | Primary purpose matches exclusion? | Return to Shortlist (JF2) | Proceed to Subgroup (JF5) |
| Borderline Flag | Top 2 scores within 10%? | Route to Classification Advisor (CA1) | Proceed to Provenance (JF9) |
| Manager Acceptance | Manager accepts recommendation? | Complete | Appeal/Revise |

---

## Data Flow Summary

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              DATA FLOW DIRECTION                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   EXTERNAL SOURCES          GOLD TABLES              PROCESSING            UI   │
│   ════════════════          ═══════════              ══════════            ══   │
│                                                                                  │
│   ┌──────────┐                                                                   │
│   │  OASIS   │────────┐                                                          │
│   └──────────┘        │                                                          │
│                       ▼                                                          │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│   │   TBS    │───▶│   DIM_   │───▶│ JobForge │───▶│   API    │───▶│    JD    │  │
│   │  Defs    │    │OCCUPATION│    │  Engine  │    │ Response │    │ Builder  │  │
│   └──────────┘    │   AL     │    └──────────┘    └──────────┘    └──────────┘  │
│                   └──────────┘         │                               │         │
│   ┌──────────┐         ▲               │                               │         │
│   │   Org    │─────────┘               ▼                               ▼         │
│   │   Data   │                   ┌──────────┐                    ┌──────────┐    │
│   └──────────┘                   │ Classif. │                    │  Manager │    │
│                                  │ Advisor  │                    │          │    │
│                                  └──────────┘                    └──────────┘    │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## BPMN Notation Reference

| Symbol | Meaning | Usage |
|--------|---------|-------|
| Rectangle | Activity/Task | Process step |
| Diamond | Gateway | Decision point |
| Circle (thin) | Start Event | Process begins |
| Circle (thick) | End Event | Process completes |
| Solid Arrow | Sequence Flow | Process order within lane |
| Dashed Arrow | Message Flow | Communication between lanes |
| Pool | Participant | Organization or system |
| Lane | Actor | Role within participant |
| Data Store | Database | Persistent storage |

---

*Diagram created: 2026-02-04*
*BPMN Version: 2.0 compliant notation*
*Rendering: Mermaid.js compatible*
