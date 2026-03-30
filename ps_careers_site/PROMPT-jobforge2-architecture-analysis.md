# PROMPT: JobForge 2.0 Codebase Analysis & JD Builder Integration Architecture

> **Target**: Claude Code (GSD)
> **Entry command**: `map-codebase` against `https://github.com/dubedad/JobForge-2.0`
> **Output**: Architecture understanding → integration plan → build sequence

---

## 1 — MAP THE CODEBASE

Run `map-codebase` on `https://github.com/dubedad/JobForge-2.0`.

This is the **data layer** for the JD Builder product. Identify and document:

### 1a. Medallion Data Pipeline
- Locate the Bronze → Silver → Gold pipeline stages
- Map which NOC 2021 taxonomy tables are ingested at each stage
- Identify transformation logic and any O*NET harmonization
- Document the pipeline's current state (complete? partial? broken?)

### 1b. Provenance System
- Locate all provenance/lineage tracking mechanisms
- Map how source attribution flows through the pipeline
- Identify where provenance is captured, stored, and surfaced
- Flag any gaps where transformations occur without provenance

### 1c. Job Intelligence Layer
- Identify the domain entities: Job, Occupation, Skill, Competency, etc.
- Map which NOC 2021 tables back each entity
- Document the query/API surface that consumers (like JD Builder) would use
- Identify the data schema that downstream applications must conform to

### 1d. Repo Health
- Branches, tags, CI/CD, test coverage
- Dependencies and their status
- README accuracy vs actual state
- Any `.claude/`, `.planning/`, or `CLAUDE.md` files present

---

## 2 — INTEGRATION TARGET: JD BUILDER WIREFRAME

**Live wireframe**: http://146.190.253.197/jd/

JD Builder is the **application layer** that consumes JobForge 2.0's data layer. The wireframe demonstrates a guided job description creation workflow.

**Integration question**: What does JD Builder need from JobForge 2.0?
- Which API endpoints or data access patterns does the wireframe assume?
- What schema contract must exist between the two layers?
- Where does the wireframe currently stub or hardcode data that should come from JobForge?

---

## 3 — THE UNIFIED DATA MODEL (Architecture Context)

JobForge 2.0 is not just a JD Builder backend. It is the **canonical data layer** for a workforce planning platform with two UX surfaces over the same data:

### Surface A: "Careers Website" (Workforce Supply)
- **Audience**: Employees, job seekers
- **UX**: Browse job families → view job titles → read job descriptions
- **Data positioning**: "Here's what this job is and what it requires"
- **Existing source**: CAF Careers site (https://forces.ca/en/careers)

### Surface B: "Job Management Portal" (Workforce Demand)
- **Audience**: Managers, HR practitioners
- **UX**: Search/browse jobs → select titles → "add to org" → build team
- **Data positioning**: "Here's what I need on my team"
- **Mental model**: "Amazon for org building" — search, filter by job family, select, add to cart (org), checkout with job descriptions

### The Gap Equation
```
Workforce Demand (positions with JDs) − Workforce Supply (people in roles)
= Qualified & Quantified GAPS
```
These gaps inform downstream HR functions: training volumes, staffing plans, recruitment targets, contracting needs.

> **For this prompt**: Document this architecture context in the repo's planning docs.
> Do NOT build Surface B yet. It is vision-tier.
> The immediate build target is: JobForge 2.0 data layer → JD Builder integration.

---

## 4 — DATA INGESTION: CAF SCRAPER

The CAF Careers scraper feeds job data from `forces.ca/en/careers` into JobForge 2.0.

- **Google Drive location**: https://drive.google.com/drive/folders/1XldzKnUf0VHPOwHnPMqy6wY20iscGjxp
- **Local path (reference)**: `C:\Users\Administrator\Dropbox\++ Results Kit\C Best Practices\caf_scraper`
- **Source site**: https://forces.ca/en/careers

**Analysis tasks**:
1. Review the scraper code in the Drive folder
2. Map scraper output schema → JobForge 2.0 ingestion schema
3. Identify transformation gaps (what the scraper produces vs what JobForge expects)
4. Document the ingestion pathway as a data flow diagram

---

## 5 — DELIVERABLES (Priority Order)

| # | Deliverable | Scope |
|---|---|---|
| 1 | **Codebase map** | Complete `map-codebase` output for JobForge 2.0 |
| 2 | **Data layer inventory** | Medallion pipeline status, provenance coverage, job intelligence entities |
| 3 | **Integration contract** | Schema/API contract between JobForge 2.0 and JD Builder |
| 4 | **CAF scraper assessment** | Scraper → JobForge ingestion pathway analysis |
| 5 | **Architecture context doc** | Unified data model vision (Supply/Demand surfaces, gap equation) |

---

## 6 — PARKING LOT (Captured, Not In Scope)

These are real requirements. They are parked here for future prompts:

- [ ] **Surface B UX**: "Amazon for org building" manager workflow
- [ ] **Org chart generation**: Manager checks out team → auto-generate org chart
- [ ] **Gap calculation engine**: Supply − Demand = Gaps → HR function forecasting
- [ ] **HR function integrations**: Training, staffing, recruitment, contracting volume forecasting
- [ ] **Dual-surface routing**: Same data, different UX by user role (employee vs manager)

---

## CONSTRAINTS

- **Do not merge** JD Builder and JobForge repos. They are separate layers with intentional separation.
- **JobForge 2.0 is the authoritative data layer**. Any new data entities for JD Builder or the careers website must be created in JobForge 2.0, not in application-layer repos.
- **Provenance is non-negotiable**. Every data element surfaced to users must trace back to its source (NOC table, O*NET crosswalk, CAF scraper record).
- **NOC 2021 is the canonical taxonomy**. O*NET enriches; NOC governs.

---

## HOW TO USE THIS PROMPT

1. Open Claude Code in the JobForge 2.0 repo directory
2. Run: `map-codebase`
3. Then paste this prompt (or reference it as a planning doc)
4. Work through deliverables 1–5 in order
5. Park anything that drifts into the Parking Lot items
