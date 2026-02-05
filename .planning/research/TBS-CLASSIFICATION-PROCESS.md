# TBS Job Classification: Complete Process Map

**Research Date:** 2026-02-04
**Purpose:** Document the TBS-prescribed job classification process to inform full automation roadmap (v5.0+)

---

## Policy Provenance Index

This document derives all process steps, requirements, and decision rules from the following authoritative TBS sources. Each requirement is tagged with its source reference (e.g., `[GUIDE-S2.P1]`) for traceability.

### Source Documents

| ID | Document | URL | Effective Date |
|----|----------|-----|----------------|
| **GUIDE** | Guide to Allocating Positions Using Occupational Group Definitions | https://www.canada.ca/en/treasury-board-secretariat/services/collective-agreements/occupational-groups/guide-allocating-positions-using-occupational-group-definitions.html | 1999-03-27 (current) |
| **DOC** | Directive on Classification | https://www.tbs-sct.canada.ca/pol/doc-eng.aspx?id=28700 | 2020-04-01 (current) |
| **JES** | Job Evaluation Standards for Public Service Employees | https://www.canada.ca/en/treasury-board-secretariat/services/collective-agreements/job-evaluation/job-evaluation-standards-public-service-employees.html | Various (per standard) |
| **TOC** | Table of Concordance (Occupational Groups) | https://www.canada.ca/en/treasury-board-secretariat/services/collective-agreements/occupational-groups.html | Current |

### Guide to Allocating Positions - Section Index

| Reference | Section | Content |
|-----------|---------|---------|
| GUIDE-S1.P1 | Section 1, Introduction | "This Guide provides advice on allocating work in the Public Service to occupational groups" |
| GUIDE-S1.P7 | Section 1, Format of Definitions | Structure of definition statements, inclusions, exclusions |
| GUIDE-S1.P9 | Section 1, Classification Process | 4-step procedure overview |
| GUIDE-S2.P1 | Section 2, Identify Primary Purpose | "The primary purpose of the work is determined through the review of the work description" |
| GUIDE-S2.P2 | Section 2, Examine Group Definitions | Holistic matching guidance, not keyword-based |
| GUIDE-S2.P3 | Section 2, Check Preliminary Selection | Inclusion/exclusion verification |
| GUIDE-S2.P4 | Section 2, Make Final Allocation | Subgroup allocation and documentation |
| GUIDE-S3.P1 | Section 3, Understanding Distinctions | Group disambiguation guidance |
| GUIDE-S3.P2 | Section 3, Difficulty in Determining | Edge case resolution |
| GUIDE-S3.P3 | Section 3, Combinations of Work | Split duties, invalid combinations |

### Directive on Classification - Section Index

| Reference | Section | Content |
|-----------|---------|---------|
| DOC-4.1.1 | Section 4.1.1 | Head of HR ensures classification per directive and standards |
| DOC-4.2.2 | Section 4.2.2 | Managers seek advice from accredited persons |
| DOC-4.2.3 | Section 4.2.3 | Managers provide all information required for classification |
| DOC-4.2.5 | Section 4.2.5 | Managers maintain accurate org structures and current JDs |
| DOC-4.2.6 | Section 4.2.6 | Managers determine effective date with evidence |
| DOC-B.2.2.1 | Appendix B.2.2.1 | JD must be written in bias-free plain language, contain all significant aspects |
| DOC-B.2.2.1a | Appendix B.2.2.1(a) | JD must include organizational context, mandate, supervisor relationships |
| DOC-B.2.2.1b | Appendix B.2.2.1(b) | JD must include title reflecting functions and nature of work |
| DOC-B.2.2.1c | Appendix B.2.2.1(c) | JD must include manager's signature and date |
| DOC-B.2.2.2 | Appendix B.2.2.2 | Identifying information including supervisor's position, group, level |
| DOC-B.2.2.3 | Appendix B.2.2.3 | New/updated JD required when new work assigned |

---

## BPMN Swimlane Process Map

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                              TBS JOB CLASSIFICATION PROCESS - FULL AUTOMATION                                                                            │
│                                                                                                                                                                          │
│  STEP 1: WORK DESCRIPTION          STEP 2: GROUP ALLOCATION           STEP 3: VERIFY SELECTION         STEP 4: SUBGROUP            STEP 5: JOB EVALUATION              │
│  ─────────────────────────         ───────────────────────            ────────────────────────         ──────────────────          ─────────────────────               │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                                                                                          │
│  MANAGER                                                                                                                                                                 │
│  ════════                                                                                                                                                                │
│                                                                                                                                                                          │
│    ┌──────────────┐      ┌──────────────┐                                                           ┌──────────────┐                        ┌──────────────┐            │
│    │   Initiate   │      │   Provide    │                                                           │   Review &   │                        │   Accept     │            │
│    │     JD       │─────▶│   Org Unit   │──────────────────────────────────────────────────────────▶│   Validate   │───────────────────────▶│   or Appeal  │            │
│    │   Request    │      │   Context    │                                                           │   Results    │                        │   Decision   │            │
│    └──────────────┘      └──────────────┘                                                           └──────────────┘                        └──────────────┘            │
│           │                     │                                                                          │                                       │                    │
│           ▼                     ▼                                                                          │                                       │                    │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                                                                                          │
│  JD BUILDER (Application)                                                                                                                                                │
│  ════════════════════════                                                                                                                                                │
│                                                                                                                                                                          │
│    ┌──────────────┐      ┌──────────────┐      ┌──────────────┐      ┌──────────────┐      ┌──────────────┐      ┌──────────────┐      ┌──────────────┐                │
│    │   Search     │      │   Select     │      │   Select     │      │   Generate   │      │   Preview    │      │   Export     │      │  "Predict    │                │
│    │   OASIS      │─────▶│   NOC        │─────▶│   Statements │─────▶│   Overview   │─────▶│   JD         │─────▶│   PDF/DOCX   │─────▶│   Classified │                │
│    │   Profiles   │      │   Profile    │      │   (per tab)  │      │   (LLM)      │      │              │      │              │      │   Group"     │                │
│    └──────────────┘      └──────────────┘      └──────────────┘      └──────────────┘      └──────────────┘      └──────────────┘      └──────┬───────┘                │
│           │                     │                     │                     │                                                                  │                        │
│           │                     │                     │                     │                                                                  ▼                        │
│           │                     │                     │                     │                                                    ┌──────────────────────┐               │
│           │                     │                     │                     │                                                    │  Call /api/allocate  │               │
│           │                     │                     │                     │                                                    │  (v4.0 API)          │               │
│           │                     │                     │                     │                                                    └──────────┬───────────┘               │
│           ▼                     ▼                     ▼                     ▼                                                               │                           │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                                                                                          │
│  JOBFORGE (Gold Tables / Matching Engine)                                                                                                                                │
│  ════════════════════════════════════════                                                                                                                                │
│                                                                                                                                                                          │
│                                          ┌──────────────┐      ┌──────────────┐      ┌──────────────┐      ┌──────────────┐      ┌──────────────┐                       │
│                                          │   Extract    │      │   Semantic   │      │   LLM        │      │   Check      │      │   Apply Job  │                       │
│                                          │   Primary    │─────▶│   Shortlist  │─────▶│   Classify   │─────▶│   Inclusions/│─────▶│   Evaluation │                       │
│                                          │   Purpose    │      │   Candidates │      │   (Holistic) │      │   Exclusions │      │   Standard   │                       │
│                                          └──────────────┘      └──────────────┘      └──────────────┘      └──────────────┘      └──────┬───────┘                       │
│                                                 │                     │                     │                     │                     │                               │
│                                                 │                     │                     │                     │                     ▼                               │
│                                                 │                     │                     │                     │           ┌──────────────────┐                      │
│                                                 │                     │                     │                     │           │  Score Factors   │                      │
│                                                 │                     │                     │                     │           │  (Skill, Effort, │                      │
│                                                 │                     │                     │                     │           │  Responsibility, │                      │
│                                                 │                     │                     │                     │           │  Working Cond.)  │                      │
│                                                 │                     │                     │                     │           └────────┬─────────┘                      │
│                                                 │                     │                     │                     │                    │                               │
│                                                 │                     │                     │                     │                    ▼                               │
│                                                 │                     │                     │                     │           ┌──────────────────┐                      │
│                                                 │                     │                     │                     │           │  Determine Level │                      │
│                                                 │                     │                     │                     │           │  (Points → Level)│                      │
│                                                 │                     │                     │                     │           └────────┬─────────┘                      │
│                                                 │                     │                     │                     │                    │                               │
│                                                 ▼                     ▼                     ▼                     ▼                    ▼                               │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                                                                                          │
│  CLASSIFICATION ADVISOR (Human-in-Loop for Edge Cases)                                                                                                                   │
│  ═════════════════════════════════════════════════════                                                                                                                   │
│                                                                                                                                                                          │
│                                                                              ┌──────────────┐      ┌──────────────┐      ┌──────────────┐                               │
│                                                                              │   Review     │      │   Resolve    │      │   Approve    │                               │
│                                                                              │   Borderline │─────▶│   AP vs TC   │─────▶│   Final      │                               │
│                                                                              │   Cases      │      │   Edge Cases │      │   Decision   │                               │
│                                                                              │   (<10% gap) │      │              │      │              │                               │
│                                                                              └──────────────┘      └──────────────┘      └──────────────┘                               │
│                                                                                     ▲                                           │                                        │
│                                                                                     │                                           │                                        │
│                                                                                     │ Flagged                                   │ Ratified                               │
│                                                                                     │ Cases                                     │ Decision                               │
│                                                                                     │                                           ▼                                        │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                                                                                          │
│  AUTHORITATIVE DATA SOURCES                                                                                                                                              │
│  ══════════════════════════                                                                                                                                              │
│                                                                                                                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐    │
│  │                                                                                                                                                                 │    │
│  │   ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐                 │    │
│  │   │                  │    │                  │    │                  │    │                  │    │                  │    │                  │                 │    │
│  │   │   OASIS / NOC    │    │   TBS Group      │    │   Job Evaluation │    │   Table of       │    │   Benchmark      │    │   Organizational │                 │    │
│  │   │   (ESDC)         │    │   Definitions    │    │   Standards      │    │   Concordance    │    │   Positions      │    │   Data           │                 │    │
│  │   │                  │    │   (TBS)          │    │   (TBS)          │    │   (TBS)          │    │   (TBS)          │    │   (Department)   │                 │    │
│  │   │   ─────────────  │    │   ─────────────  │    │   ─────────────  │    │   ─────────────  │    │   ─────────────  │    │   ─────────────  │                 │    │
│  │   │   • NOC codes    │    │   • 29 groups    │    │   • 18 standards │    │   • Group ↔      │    │   • Reference    │    │   • Org context  │                 │    │
│  │   │   • Profiles     │    │   • Definitions  │    │   • Factors      │    │     Standard     │    │     positions    │    │   • Mandates     │                 │    │
│  │   │   • Tasks        │    │   • Inclusions   │    │   • Degree levels│    │     mapping      │    │   • Scored       │    │   • Supervisor   │                 │    │
│  │   │   • Skills       │    │   • Exclusions   │    │   • Point values │    │   • Subgroups    │    │     examples     │    │     relationships│                 │    │
│  │   │   • Work Context │    │   • Subgroups    │    │   • Level ranges │    │                  │    │                  │    │   • Unit structure│                │    │
│  │   │                  │    │                  │    │                  │    │                  │    │                  │    │                  │                 │    │
│  │   └────────┬─────────┘    └────────┬─────────┘    └────────┬─────────┘    └────────┬─────────┘    └────────┬─────────┘    └────────┬─────────┘                 │    │
│  │            │                       │                       │                       │                       │                       │                           │    │
│  │            │                       │                       │                       │                       │                       │                           │    │
│  │            ▼                       ▼                       ▼                       ▼                       ▼                       ▼                           │    │
│  │   ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐   │    │
│  │   │                                                                                                                                                        │   │    │
│  │   │                                          DIM_OCCUPATIONAL (SQLite Gold Table)                                                                          │   │    │
│  │   │                                                                                                                                                        │   │    │
│  │   │    ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │   │    │
│  │   │    │ dim_occupational│  │ dim_occupational│  │ dim_occupational│  │ dim_job_eval    │  │ dim_eval_factor │  │ dim_benchmark   │  │ dim_org_context │   │   │    │
│  │   │    │ _group          │  │ _inclusion      │  │ _exclusion      │  │ _standard       │  │                 │  │ _position       │  │                 │   │   │    │
│  │   │    └─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘   │   │    │
│  │   │                                                                                                                                                        │   │    │
│  │   │    ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                                                                                       │   │    │
│  │   │    │ scrape_         │  │ verification_   │  │ provenance_     │                                                                                       │   │    │
│  │   │    │ provenance      │  │ event           │  │ chain           │                                                                                       │   │    │
│  │   │    └─────────────────┘  └─────────────────┘  └─────────────────┘                                                                                       │   │    │
│  │   │                                                                                                                                                        │   │    │
│  │   └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘   │    │
│  │                                                                                                                                                                 │    │
│  └─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                                                                                                          │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘


LEGEND
══════

    ┌──────────────┐
    │   Activity   │     Process step / task
    └──────────────┘

    ─────▶              Sequence flow

    ═════               Swimlane separator

    ▲ │ ▼               Message flow between lanes

```

---

## The 5 Prescribed Steps

> **Source:** Steps 1-4 derive from `[GUIDE-S1.P9]` Classification Process. Step 5 derives from `[JES]` Job Evaluation Standards.

### Step 1: Review and Understand Work Description

**TBS Requirement:** Extract the **primary purpose** of the position. `[GUIDE-S2.P1]`

| Input | Source | Policy Provenance | Description |
|-------|--------|-------------------|-------------|
| Work Description | Manager | `[DOC-4.2.5]` | Complete description of assigned work |
| Organizational Chart | Department | `[DOC-B.2.2.1a]` | Reporting relationships, unit structure |
| Client-Service Results | Manager/JD | `[GUIDE-S2.P1]` | Why the position exists, outcomes delivered |
| Key Activities | Manager/JD | `[DOC-B.2.2.1]` | Major tasks and responsibilities |

**Decision Rule:** `[GUIDE-S2.P1]` If primary purpose unclear from Client-Service Results and Key Activities alone, examine entire work description plus supporting documentation (legislation, mandates, business plans).

**Output:** Primary purpose summary statement.

---

### Step 2: Allocate Position to Occupational Group

**TBS Requirement:** Match primary purpose to group definitions using **holistic semantic judgment** (not keyword matching). `[GUIDE-S2.P2]`

| Input | Source | Policy Provenance | Description |
|-------|--------|-------------------|-------------|
| 29 Group Definitions | TBS | `[GUIDE-S1.P7]` | Definition statements for each occupational group |
| Inclusion Statements | TBS | `[GUIDE-S1.P7]` | Examples of work included in each group |
| Exclusion Statements | TBS | `[GUIDE-S1.P7]` | Examples of work excluded from each group |
| Primary Purpose | Step 1 | `[GUIDE-S2.P1]` | Extracted from work description |

**Decision Rules:** `[GUIDE-S2.P2]`
1. Review multiple potentially relevant group definitions
2. Use definition statement as PRIMARY basis (not inclusions) — *"all occupational group allocations should be made primarily with the definition statement in mind"*
3. Treat definitions holistically—don't cherry-pick terms — *"not 'cherry-picked' for specific terms or phrases"*
4. Where work could fit multiple groups, identify "best fit" by determining why position was created

**Output:** Preliminary group allocation (e.g., "CS", "EC", "PM").

---

### Step 3: Check Preliminary Selection

**TBS Requirement:** Verify selection using inclusions, exclusions, and benchmarks. `[GUIDE-S2.P3]`

| Verification Check | Question | Policy Provenance | Action if Failed |
|--------------------|----------|-------------------|------------------|
| Inclusion Support | Does primary purpose appear in inclusions? | `[GUIDE-S2.P3]` | Note: inclusions are non-exhaustive |
| Exclusion Conflict | Do exclusions reflect primary purpose? | `[GUIDE-S2.P3]` | If YES → eliminate group, return to Step 2 |
| Benchmark Comparison | How does position compare to benchmarks? | `[GUIDE-S2.P3]` | Adjust if significant mismatch |
| Similar Positions | Consistent with similar roles in organization? | `[DOC-4.1.1]` | Flag for Classification Advisor if inconsistent |

**Decision Rule:** `[GUIDE-S2.P3]` Exclusion statements are **hard gates**—if primary purpose matches an exclusion, the group must be rejected. *"Exclusion statements must not reflect the work's primary purpose."*

**Output:** Confirmed group allocation OR return to Step 2.

---

### Step 4: Allocate to Occupational Subgroup (Where Applicable)

**TBS Requirement:** Apply same holistic matching process to subgroup definitions. `[GUIDE-S2.P4]`

| Input | Source | Policy Provenance | Description |
|-------|--------|-------------------|-------------|
| Subgroup Definitions | Table of Concordance | `[TOC]` | Definition statements for subgroups |
| Subgroup Inclusions/Exclusions | TBS | `[GUIDE-S1.P7]` | Same structure as group-level |
| Confirmed Group | Step 3 | `[GUIDE-S2.P3]` | Group allocation from previous step |

**Groups with Subgroups:** AI, AO, CP, EB, NR, RE, SH, SP (and others per `[TOC]`)

**Output:** Full allocation code (e.g., "CS", "SH-NU", "EB-ED").

---

### Step 5: Apply Job Evaluation Standard

**TBS Requirement:** Determine **level** using point-rating system specific to the allocated group. `[JES]`

| Input | Source | Policy Provenance | Description |
|-------|--------|-------------------|-------------|
| Job Evaluation Standard | TBS | `[JES]`, `[TOC]` | Standard for allocated group (18 standards exist) |
| Evaluation Factors | Standard | `[JES]` | 7-9 factors covering Skill, Effort, Responsibility, Working Conditions |
| Degree Definitions | Standard | `[JES]` | Level descriptors for each factor |
| Point Values | Standard | `[JES]` | Points assigned to each degree |
| Benchmark Positions | TBS | `[JES]` | Pre-scored reference positions |
| Work Description | Manager | `[DOC-4.2.3]` | Evidence for factor scoring |

**The Four Statutory Criteria (Pay Equity Act compliant):** `[JES]`

| Criterion | Weight (typical) | Example Factors |
|-----------|-----------------|-----------------|
| **Skill** | 30-45% | Knowledge, Research & Analysis, Contextual Knowledge |
| **Responsibility** | 40-55% | Decision Making, Leadership, Communication |
| **Effort** | 2-5% | Physical Effort, Sensory Effort |
| **Working Conditions** | 2-5% | Environmental factors, psychological stress |

**Process:** `[JES]`
1. For each factor, select degree that best matches work description evidence
2. Sum points across all factors
3. Map total points to classification level

**Example (EC Standard):** `[JES-EC]`

| Level | Point Range | Typical Scope |
|-------|-------------|---------------|
| EC-01 | 40-99 | Entry-level analyst |
| EC-04 | 250-344 | Senior analyst/team lead |
| EC-07 | 585-749 | Director-level |
| EC-08 | 750-1,000 | Executive advisor |

**Output:** Full classification (e.g., "EC-04", "CS-02", "PM-05").

---

## Required Work Description Elements

> **Source:** All requirements derive from `[DOC-B.2.2.1]` through `[DOC-B.2.2.3]` (Directive on Classification, Appendix B).

### Mandatory Content Sections `[DOC-B.2.2.1]`

| Section | Purpose | Policy Provenance | Required Content |
|---------|---------|-------------------|------------------|
| **Organizational Context** | Situate position | `[DOC-B.2.2.1a]` | Mandate, supervisor-subordinate relationships, branch/division |
| **Client-Service Results** | Define purpose | `[GUIDE-S2.P1]` | Primary purpose, outcomes delivered, clients served |
| **Key Activities** | Describe work | `[DOC-B.2.2.1]` | Major tasks, responsibilities, accountabilities |
| **Job Title** | Identify role | `[DOC-B.2.2.1b]` | Must reflect functions and nature of work |
| **Manager Attestation** | Authorize | `[DOC-B.2.2.1c]`, `[DOC-4.2.6]` | Signature, date, effective date justification |

### Mandatory Identifying Fields (14 fields) `[DOC-B.2.2.2]`

| # | Field | Policy Provenance | Purpose |
|---|-------|-------------------|---------|
| 1 | Job number | `[DOC-B.2.2.2]` | Unique identifier |
| 2 | Position number | `[DOC-B.2.2.2]` | HR system reference |
| 3 | Authorized group and level | `[DOC-B.2.2.2]` | Current classification |
| 4 | NOC code | `[DOC-B.2.2.2]` | National Occupational Classification |
| 5 | Effective date | `[DOC-B.2.2.2]`, `[DOC-4.2.6]` | When classification applies |
| 6 | Organization/department | `[DOC-B.2.2.2]` | Parent organization |
| 7 | Branch/division | `[DOC-B.2.2.2]` | Organizational unit |
| 8 | Geographic location | `[DOC-B.2.2.2]` | Work location |
| 9 | Official languages requirements | `[DOC-B.2.2.2]` | Bilingual profile |
| 10 | Security requirements | `[DOC-B.2.2.2]` | Clearance level |
| 11 | Communication requirements | `[DOC-B.2.2.2]` | Language needs |
| 12 | Supervisor's position number | `[DOC-B.2.2.2]` | Reporting relationship |
| 13 | Supervisor's group | `[DOC-B.2.2.2]` | Supervisor's classification group |
| 14 | Supervisor's level | `[DOC-B.2.2.2]` | Supervisor's classification level |

### When Updates Are Required `[DOC-B.2.2.3]`

A new or updated job description is required when:
- New work is assigned
- Significant changes in work occur
- Organizational restructuring affects the position

---

## Gap Analysis: Current State vs. Full Automation

### What JD Builder Lite Currently Provides (v2.0)

| Element | Source | Status |
|---------|--------|--------|
| NOC Code | OASIS scrape | ✓ Available |
| Profile Title | OASIS scrape | ✓ Available |
| Key Activities | OASIS Tasks | ✓ Available (as selectable statements) |
| Skills & Abilities | OASIS scrape | ✓ Available |
| Work Context | OASIS scrape | ✓ Available |
| Employment Requirements | OASIS scrape | ✓ Available |

### What v4.0 Adds (Occupational Group Allocation)

| Element | Source | Status |
|---------|--------|--------|
| Group Definitions | TBS scrape → DIM_OCCUPATIONAL | ✓ Complete |
| Inclusion Statements | TBS scrape | ✓ Complete |
| Exclusion Statements | TBS scrape | ✓ Complete |
| Semantic Matching | sentence-transformers | ✓ Complete |
| LLM Classification | OpenAI structured outputs | ✓ Complete |
| Provenance Chain | scrape_provenance table | ✓ Complete |

### What's Missing for Full Automation (v5.0+ Scope)

| Missing Element | TBS Requirement | Potential Data Source | Priority |
|-----------------|-----------------|----------------------|----------|
| **Organizational Context** | Mandate, supervisor relationships | Departmental org data, PeopleSoft | HIGH |
| **Client-Service Results** | Primary purpose statement | Derived from NOC + manager input | HIGH |
| **Job Evaluation Standards** | Factor definitions, degree levels, points | TBS standards (scrape or data entry) | HIGH |
| **Benchmark Positions** | Pre-scored reference positions | TBS benchmark database | MEDIUM |
| **Physical Effort Scoring** | Exertion intensity/frequency | OASIS Physical Activities + mapping | MEDIUM |
| **Working Conditions Scoring** | Environmental/psychological factors | OASIS Work Context + mapping | MEDIUM |
| **Decision-Making Scope** | Latitude, impact, precedent | Role level mappings, org hierarchy | MEDIUM |
| **Leadership Scope** | Resources managed, supervisory duties | Org data, position relationships | MEDIUM |
| **Communication Requirements** | Audience, complexity, persuasion | Derived from duties + stakeholder map | LOW |

---

## Edge Cases Requiring Human-in-Loop

> **Source:** Edge case guidance derives from `[GUIDE-S3]` Troubleshooting section.

| Edge Case | Detection | Policy Provenance | Resolution |
|-----------|-----------|-------------------|------------|
| **Borderline Match** | Top 2 scores within 10% | `[GUIDE-S3.P2]` | Classification Advisor review |
| **AP vs TC Disambiguation** | Both groups in top candidates | `[GUIDE-S3.P1]` | Apply TBS guidance: theoretical (AP) vs practical (TC) |
| **Split Duties** | Work spans multiple group definitions | `[GUIDE-S3.P3]` | Recommend position splitting |
| **Invalid Combination** | Same JD allocated to different groups | `[GUIDE-S3.P3]` | Flag for work description revision — *"The same unique, generic or broad-based work description cannot be allocated to different occupational groups"* |
| **Specialized Groups** | EX, LC, MD in recommendations | `[DOC-4.1.1]` | Route to specialized classification process |
| **Insufficient JD Quality** | Low confidence on all candidates | `[DOC-4.2.3]` | Generate remediation checklist for Manager |

### Critical Constraint `[GUIDE-S2.P2]`

> *"Remember to consider the requirements of the work, rather than the educational or skill attributes of the incumbent."*

This principle—**evaluate the work, not the person**—must be enforced at every step of the classification process.

---

## Automation Roadmap

| Milestone | Capability | Steps Automated | Dependencies |
|-----------|------------|-----------------|--------------|
| **v4.0** (current) | Allocate to Group/Subgroup | Steps 1-4 | ✓ DIM_OCCUPATIONAL complete |
| **v4.0.1** | UI for allocation results | Display top-3 recommendations | v4.0 API complete |
| **v5.0** | Apply Job Evaluation Standard | Step 5 | Job eval standards data, factor scoring engine |
| **v5.1** | Work Description Gap Filling | Pre-populate missing elements | Org context data, client-service derivation |
| **v5.2** | Full Provenance Chain | Link every decision to evidence | Provenance architecture extension |
| **v5.3** | Benchmark Comparison | Compare to reference positions | Benchmark position database |

---

## Data Architecture for Full Automation

### New Gold Tables Required (v5.0+)

```sql
-- Job Evaluation Standards (one per occupational group)
CREATE TABLE dim_job_eval_standard (
    id INTEGER PRIMARY KEY,
    group_code TEXT NOT NULL,           -- e.g., 'EC', 'CS', 'PM'
    standard_name TEXT NOT NULL,        -- e.g., 'Economics and Social Science Services'
    total_points INTEGER NOT NULL,      -- e.g., 1000
    effective_from TEXT NOT NULL,
    source_url TEXT NOT NULL,
    source_provenance_id INTEGER,
    FOREIGN KEY (source_provenance_id) REFERENCES scrape_provenance(id)
);

-- Evaluation Factors (7-9 per standard)
CREATE TABLE dim_eval_factor (
    id INTEGER PRIMARY KEY,
    standard_id INTEGER NOT NULL,
    factor_name TEXT NOT NULL,          -- e.g., 'Decision Making'
    factor_code TEXT NOT NULL,          -- e.g., 'DM'
    criterion TEXT NOT NULL,            -- 'skill' | 'effort' | 'responsibility' | 'working_conditions'
    max_points INTEGER NOT NULL,
    weight_percent REAL NOT NULL,
    definition TEXT NOT NULL,
    FOREIGN KEY (standard_id) REFERENCES dim_job_eval_standard(id)
);

-- Factor Degree Levels (4-8 per factor)
CREATE TABLE dim_factor_degree (
    id INTEGER PRIMARY KEY,
    factor_id INTEGER NOT NULL,
    degree_number INTEGER NOT NULL,     -- 1, 2, 3, ...
    points INTEGER NOT NULL,
    description TEXT NOT NULL,
    scope_examples TEXT,                -- JSON array of examples
    FOREIGN KEY (factor_id) REFERENCES dim_eval_factor(id)
);

-- Level Ranges (mapping points to classification levels)
CREATE TABLE dim_level_range (
    id INTEGER PRIMARY KEY,
    standard_id INTEGER NOT NULL,
    level_code TEXT NOT NULL,           -- e.g., 'EC-04'
    min_points INTEGER NOT NULL,
    max_points INTEGER NOT NULL,
    FOREIGN KEY (standard_id) REFERENCES dim_job_eval_standard(id)
);

-- Benchmark Positions (pre-scored reference positions)
CREATE TABLE dim_benchmark_position (
    id INTEGER PRIMARY KEY,
    standard_id INTEGER NOT NULL,
    position_title TEXT NOT NULL,
    level_code TEXT NOT NULL,
    total_points INTEGER NOT NULL,
    factor_scores TEXT NOT NULL,        -- JSON: {"DM": 5, "LA": 3, ...}
    description TEXT,
    source_url TEXT,
    FOREIGN KEY (standard_id) REFERENCES dim_job_eval_standard(id)
);

-- Organizational Context (department-specific)
CREATE TABLE dim_org_context (
    id INTEGER PRIMARY KEY,
    org_code TEXT NOT NULL,             -- e.g., 'ESDC', 'TBS'
    unit_code TEXT NOT NULL,
    unit_name TEXT NOT NULL,
    mandate TEXT,
    supervisor_position_number TEXT,
    supervisor_group TEXT,
    supervisor_level TEXT,
    effective_from TEXT NOT NULL
);
```

---

## Provenance Requirements (DADM Compliance)

Every classification decision must be traceable to:

| Provenance Element | What It Links | TBS Requirement |
|--------------------|---------------|-----------------|
| **Source URL** | TBS definition page | Sections 6.2.3, 6.2.7 |
| **Paragraph Label** | Specific definition/inclusion/exclusion | Audit trail |
| **Scraped Timestamp** | When data was retrieved | Data currency |
| **Content Hash** | Integrity verification | Change detection |
| **Reasoning Steps** | LLM chain-of-thought | Transparency |
| **Evidence Spans** | JD text supporting decision | Accountability |
| **Human Verification** | Classification Advisor sign-off | Human oversight |

---

## Authoritative Sources (Policy Provenance Master Reference)

| ID | Source | URL | Data Provided | Last Verified |
|----|--------|-----|---------------|---------------|
| `[GUIDE]` | Guide to Allocating Positions Using Occupational Group Definitions | https://www.canada.ca/en/treasury-board-secretariat/services/collective-agreements/occupational-groups/guide-allocating-positions-using-occupational-group-definitions.html | Steps 1-4 process, holistic matching rules, edge case guidance | 2026-02-04 |
| `[DOC]` | Directive on Classification | https://www.tbs-sct.canada.ca/pol/doc-eng.aspx?id=28700 | Work description requirements, manager/HR responsibilities, mandatory fields | 2026-02-04 |
| `[TOC]` | Occupational Groups (Table of Concordance) | https://www.canada.ca/en/treasury-board-secretariat/services/collective-agreements/occupational-groups.html | Group ↔ Standard mapping, subgroup definitions | 2026-02-04 |
| `[JES]` | Job Evaluation Standards for Public Service Employees | https://www.canada.ca/en/treasury-board-secretariat/services/collective-agreements/job-evaluation/job-evaluation-standards-public-service-employees.html | Step 5 standards, factors, degree levels, point values | 2026-02-04 |
| `[OASIS]` | OASIS (Occupational and Skills Information System) | https://noc.esdc.gc.ca/OaSIS/OaSISWelcome | NOC profiles, tasks, skills, work context | 2026-02-04 |
| `[DADM]` | Directive on Automated Decision-Making | https://www.tbs-sct.canada.ca/pol/doc-eng.aspx?id=32592 | Transparency, accountability, human oversight requirements | 2026-02-04 |

---

## Policy Provenance Compliance Statement

This document implements policy provenance in accordance with:

- **DADM Section 6.2.3:** Transparency requirements — all decision rules traced to authoritative source
- **DADM Section 6.2.7:** Accountability requirements — clear audit trail from decision to policy paragraph
- **DADM Section 6.3.5:** Human oversight requirements — edge cases flagged for Classification Advisor review

Every requirement, decision rule, and process step in this document includes a bracketed reference (e.g., `[GUIDE-S2.P1]`) linking to the specific authoritative source paragraph. This enables:

1. **Verification:** Any stakeholder can verify the rule against the original source
2. **Auditability:** Classification decisions can be traced back to policy authority
3. **Maintenance:** When TBS updates policy, affected rules can be identified and updated
4. **Compliance:** DADM requirements for transparency and traceability are satisfied

---

*Document created: 2026-02-04*
*Policy provenance added: 2026-02-04*
*Purpose: Inform v5.0+ roadmap for full job classification automation*
*DADM Compliance: Sections 6.2.3, 6.2.7, 6.3.5*
