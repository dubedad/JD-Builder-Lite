# JobForge Data Requirements for JD Builder Lite

**Date:** 2026-02-06
**Source:** UAT walkthrough findings (S1-10, S2-06, S2-07)
**Purpose:** What JobForge gold needs to provide so JD Builder can switch from OASIS scraping to local parquet reads.

---

## Already in JobForge Gold (no action needed)

| Table | Columns Used | JD Builder Use |
|-------|-------------|----------------|
| `dim_noc` | unit_group_id, code, title, teer, broad_category | Search results, NOC hierarchy |
| `element_labels` | unit_group_id, label text | Profile enrichment, search matching |
| `element_example_titles` | unit_group_id, example titles | Profile reference, search matching |
| `element_exclusions` | unit_group_id, exclusion text | Profile reference |
| `element_employment_requirements` | unit_group_id, requirements text | Profile reference |
| `element_workplaces_employers` | unit_group_id, workplace text | Profile reference, search matching (S1-04) |
| `element_lead_statement` | unit_group_id, lead statement text | Search cards, profile header |
| `element_main_duties` | unit_group_id, duty text | Key Activities tab |
| `element_additional_information` | unit_group_id, info text | Profile reference |
| `oasis_skills` | unit_group_id, skill name, score | Skills tab (with level circles) |
| `oasis_abilities` | unit_group_id, ability name, score | Abilities tab (with level circles) |
| `oasis_knowledges` | unit_group_id, knowledge name, score | Knowledge tab (with level circles) |
| `oasis_workactivities` | unit_group_id, activity name, score | Key Activities tab (with level circles) |
| `oasis_workcontext` | unit_group_id, context item, score, dimension | Effort/Responsibility tabs |
| `job_architecture` | job_title, job_family, job_function, managerial_level, 40+ skill scores | Search source (S1-06), filters (S1-11) |
| `bridge_noc_og` | noc_code, og_code | NOC-to-OG neighborhood mapping (S2-06) |
| `bridge_caf_noc` | caf_id, noc_code | CAF taxonomy search (S1-08) |
| `bridge_caf_ja` | caf_id, ja fields | CAF-to-JA crosswalk |
| `dim_caf_occupation` | occupation details | CAF search source (S1-08) |
| `dim_caf_job_family` | family details | CAF search source (S1-08) |
| `dim_og` | og_code, name, description | Classification, OG enrichment (S2-06) |
| `dim_og_subgroup` | subgroup details | Classification detail |
| `dim_og_job_evaluation_standard` | og_code, standard details | OG enrichment (S2-06), v5.0 JES scoring |
| `dim_og_qualification_standard` | og_code, qualification details | OG enrichment (S2-06) |
| `fact_og_pay_rates` | og_code, level, pay rate | Future use |
| `fact_og_allowances` | og_code, allowance details | Future use |

---

## MISSING — Needs to be added to JobForge Gold

### 1. Interests (PRIORITY: HIGH)

- **Source CSV:** `data/source/interests_oasis_2023_v1.0.csv`
- **Needed columns:** unit_group_id, interest_name, score
- **JD Builder use:** Profile reference (currently scraped from OASIS HTML)
- **Suggested table name:** `oasis_interests`
- **ETL:** Simple — same pattern as `oasis_skills`, `oasis_abilities`

### 2. Personal Attributes (PRIORITY: HIGH)

- **Source CSV:** `data/source/personal-attributes_oasis_2023_v1.0.csv`
- **Needed columns:** unit_group_id, attribute_name, score (importance 1-5)
- **JD Builder use:** Profile reference (currently scraped from OASIS HTML)
- **Suggested table name:** `oasis_personal_attributes`
- **ETL:** Simple — same pattern as `oasis_skills`

### 3. Core Competencies (PRIORITY: MEDIUM)

- **Source:** Need to identify source — may be on OASIS website or a separate dataset
- **Needed columns:** unit_group_id, competency_name, score/level
- **JD Builder use:** New Core Competencies tab (S2-03)
- **Suggested table name:** `oasis_core_competencies`
- **ETL:** Depends on source identification

### 4. Guide / Scale Definitions (PRIORITY: HIGH)

- **Source CSV:** `data/source/guide_oasis_2023_v1.0.csv`
- **Needed columns:** element_id, element_name, category, description, scale_type, scale_meanings
- **JD Builder use:**
  - Tooltip descriptions for each statement (what does this skill/ability mean?)
  - **Dimension type labels** (S2-07): What do the level circles represent?
    - Skills → Proficiency (1-5)
    - Abilities → Proficiency (1-5)
    - Knowledge → Knowledge Level (1-3)
    - Work Activities → Complexity (1-5)
    - Personal Attributes → Importance (1-5)
    - Work Context → varies by item: Frequency, Duration, Degree of responsibility, etc.
  - Category definitions (section headers in profile tabs)
- **Suggested table name:** `oasis_guide`
- **ETL:** Parse guide CSV, normalize scale definitions into structured columns

### 5. NOC Hierarchy Levels for Search (PRIORITY: MEDIUM)

- **Source:** `dim_noc` already has hierarchy but needs explicit level tagging
- **Needed:** For each search result, know whether match was at:
  - Level 5: Unit Group (e.g., `40040`)
  - Level 6: Label (e.g., `40040.00`)
  - Level 7: Example Title (under a label)
- **JD Builder use:** Match rationale specificity (S1-03), granularity scoring
- **Note:** May already be derivable from existing `dim_noc` + `element_labels` + `element_example_titles` — just needs the search logic to distinguish

---

## Data Flow Architecture

```
JobForge Gold (parquet)
    │
    ├── dim_noc ──────────────┐
    ├── element_* ────────────┤
    ├── oasis_* ──────────────┤── JD Builder reads all from local parquet
    ├── job_architecture ─────┤
    ├── bridge_* ─────────────┤
    ├── dim_og_* ─────────────┤
    ├── oasis_guide (NEW) ────┤
    ├── oasis_interests (NEW) ┤
    ├── oasis_personal_attributes (NEW)
    └── oasis_core_competencies (NEW)
                              │
                              ▼
                    JD Builder Lite
                    (no more OASIS scraping)
                              │
                    ┌─────────┴──────────┐
                    │  Deterministic      │  Semantic
                    │  (SQL joins on      │  (sentence-transformers
                    │   bridge tables)    │   for ambiguous cases)
                    └─────────┬──────────┘
                              │
                              ▼
                    Search, Profile, Enrich, Classify
```

---

## Summary

| Status | Count | Tables |
|--------|-------|--------|
| Already in gold | 26 | dim_noc, element_*, oasis_*, job_architecture, bridge_*, dim_og_*, dim_caf_*, cops_*, fact_* |
| Needs new gold table | 4 | oasis_interests, oasis_personal_attributes, oasis_core_competencies, oasis_guide |
| Needs enhancement | 1 | dim_noc (explicit hierarchy level tagging for search) |

**Total effort:** 4 new ETL pipelines (3 are copy-paste of existing oasis_* pattern) + 1 guide CSV parser + 1 minor enhancement to dim_noc.

---
*Generated: 2026-02-06 from UAT findings S1-10, S2-06, S2-07*
