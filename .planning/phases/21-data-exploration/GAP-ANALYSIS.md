# OASIS Data Gap Analysis

**Path:** `/Users/victornishi/Documents/GitHub/JobForge-2.0/data/gold/`
**Last verified:** 2026-03-07
**Authority:** Direct file inspection of all 25 gold parquet files plus source CSV directory
**Status:** All gaps named explicitly. No gap is inferred.

---

## Summary

Of the OASIS profile fields that JD-Builder-Lite currently serves, **8 fields are fully covered by parquet** and **5 fields have no adequate parquet equivalent** and must continue using OASIS live scraping (or source CSV fallback via LabelsLoader). Coverage was assessed by reading actual parquet files with pandas -- not by examining metadata, filenames, or assumptions.

The most critical gap is Main Duties / Key Activities: a parquet file exists (`element_main_duties.parquet`) but the JobForge ETL pipeline did not complete -- only 8 of an expected 4,991 rows are present, covering 3 of 900 profiles. This gap is permanent until the JobForge ETL pipeline runs against the source CSV.

Interests, Personal Attributes, Core Competencies, and Career Mobility have no gold parquet at all. Interests and Personal Attributes are covered by source CSVs served via the existing LabelsLoader. Core Competencies and Career Mobility have no data in any tier.

---

## Gap Table

Every OASIS field with no adequate parquet equivalent is named here with its evidence and fallback strategy.

| OASIS Field | Parquet File Exists? | Why It Is a Gap | Fallback Strategy |
|-------------|---------------------|-----------------|-------------------|
| Main Duties / Key Activities | Yes -- `element_main_duties.parquet` | ETL incomplete: only 8 rows / 3 profiles in gold; source CSV has 4,991 rows / 900 profiles. File loads without error but covers 0.3% of profiles. | OASIS live scraping (unconditional -- do NOT attempt parquet lookup until JobForge ETL runs) |
| Interests / Holland Codes | No gold parquet | `interests_oasis_2023_v1.0.csv` exists in `data/source/` but was never promoted to gold tier. No `interests_*.parquet` exists in gold. | Source CSV via existing LabelsLoader (no regression risk -- already handled) |
| Personal Attributes | No gold parquet | `personal-attributes_oasis_2023_v1.0.csv` exists in `data/source/` but was never promoted to gold tier. No `personal_attributes_*.parquet` exists in gold. | Source CSV via existing LabelsLoader (no regression risk -- already handled) |
| Core Competencies | No data at all | No gold parquet, no silver parquet, no source CSV matching "core_competencies" or "competenc" found in any data tier. OASIS does provide this data on profile pages; JobForge has not ingested it. | OASIS live scraping only |
| Career Mobility / Progression | No data at all | No gold parquet, no silver parquet, no source CSV found. No JobForge file matching "career", "mobility", or "progression" in any tier. | OASIS live scraping only |

---

## Covered Fields Table

Every OASIS field with adequate parquet coverage is confirmed here.

| OASIS Field | Parquet File | Profiles Covered | Status |
|-------------|-------------|------------------|--------|
| Skills | `oasis_skills.parquet` | 900 / 900 | Full coverage |
| Abilities | `oasis_abilities.parquet` | 900 / 900 | Full coverage |
| Knowledge | `oasis_knowledges.parquet` | 900 / 900 | Full coverage |
| Work Activities | `oasis_workactivities.parquet` | 900 / 900 | Full coverage |
| Work Context | `oasis_workcontext.parquet` | 900 / 900 | Full coverage |
| Occupational Label / Title | `element_labels.parquet` | 900 / 900 | Full coverage |
| Lead Statement | `element_lead_statement.parquet` | 900 / 900 | Full coverage |
| Example Titles ("Also known as") | `element_example_titles.parquet` | 900 / 900 | Full coverage |
| Employment Requirements | `element_employment_requirements.parquet` | 900 / 900 | Full coverage |
| Workplaces and Employers | `element_workplaces_employers.parquet` | 900 / 900 | Full coverage |
| NOC Exclusions | `element_exclusions.parquet` | 870 / 900 | Near-full (30 profiles have no exclusions -- expected, not a gap) |
| Additional Information | `element_additional_information.parquet` | 695 / 900 | Partial (77%) -- 205 profiles have no additional info in OASIS source; partial coverage is expected, not a gap |
| NOC Unit Group Definition | `dim_noc.parquet` | 516 / 516 | Full coverage (NOC level, not profile level) |

---

## Gap Detail: Main Duties / Key Activities

This gap requires special treatment because the parquet file looks valid but is not.

**Evidence:**
- `element_main_duties.parquet` reads without error
- Row count: 8 rows
- Distinct `oasis_profile_code` values: 3 (verified by `df["oasis_profile_code"].nunique()`)
- Source CSV `main-duties_oasis-2023_v1.0.csv` (in `data/source/`): 4,991 rows / 900 profiles
- Gap size: 897 profiles not in gold parquet

**Root cause:** The JobForge ETL pipeline ingested only 3 profiles into the gold `element_main_duties.parquet`. The source data is complete; the ETL run is incomplete.

**Phase 22 instruction:** Do NOT read `element_main_duties.parquet` in Phase 22 profile service code. The file will return `CoverageStatus.FOUND` on load but `CoverageStatus.NOT_FOUND` for all but 3 profiles. This creates a false success signal. The OASIS fallback for Main Duties must be unconditional (always call OASIS scraper for this field). Add a code comment referencing this document.

**When this gap closes:** When JobForge ETL runs successfully against `main-duties_oasis-2023_v1.0.csv` and reloads the gold parquet. At that point Phase 22 code can switch from unconditional OASIS to parquet-first.

---

## Gap Detail: Interests / Holland Codes and Personal Attributes

These two gaps are already handled correctly by the existing LabelsLoader and require no Phase 22 changes.

**Evidence for Interests:**
- No gold parquet file matching "interest" or "holland" exists in `/data/gold/`
- `interests_oasis_2023_v1.0.csv` confirmed present in `/data/source/`
- LabelsLoader currently serves this from the source CSV

**Evidence for Personal Attributes:**
- No gold parquet file matching "personal" or "attribute" exists in `/data/gold/`
- `personal-attributes_oasis_2023_v1.0.csv` confirmed present in `/data/source/`
- LabelsLoader currently serves this from the source CSV

**Phase 22 instruction:** No changes required for these two fields. The existing LabelsLoader source CSV fallback is correct and complete.

---

## Gap Detail: Core Competencies and Career Mobility

These two gaps have no available data in any tier.

**Evidence for Core Competencies:**
- No gold, silver, or bronze parquet matching "competenc" found
- No source CSV matching "competenc" found
- OASIS profile pages do display "Core Competencies" sections; this data exists upstream but has never been ingested by JobForge

**Evidence for Career Mobility:**
- No gold, silver, or bronze parquet matching "career", "mobility", or "progression" found
- No source CSV found
- Some OASIS profile pages include career progression information; not all do

**Phase 22 instruction:** For both fields, use OASIS live scraping. If the OASIS scraper does not currently parse these sections, Phase 22 must either add parser support or document them as out of scope.

---

## Profile Code Format Note

Phase 22 developers must be aware of two distinct key formats used in the gold tier.

**Format 1: `oasis_profile_code`**
- Used in: all `element_*` files, all `oasis_*` files
- Format: 5-digit NOC code + decimal sub-profile suffix (e.g. `'21211.00'`, `'10020.01'`)
- Total distinct values: 900 across all covered files
- Mapping: 516 NOC unit groups expand to 900 OASIS profiles (some NOC codes have multiple sub-profiles)

**Format 2: `noc_code`**
- Used in: `dim_noc.parquet` only
- Format: 5-digit string, no decimal (e.g. `'21211'`, `'10020'`)
- Total distinct values: 516

**Required transformation in Phase 22:**
When a user requests profile `21211` (a standard NOC code), the lookup into element_* and oasis_* files must use `'21211.00'`. If `'21211.00'` returns no results, try `'21211.01'`. The `dim_noc.parquet` lookup uses `'21211'` directly with no transformation.

**Do not conflate** `oasis_profile_code` with `noc_code`. They are semantically different keys. The 900-vs-516 discrepancy is intentional: OASIS creates sub-profiles for NOC unit groups with meaningfully different occupational profiles within the same code.

---

## Column Whitespace Warning

Five gold parquet files have column names with leading or trailing whitespace characters. These were inherited from the source CSVs during JobForge ETL ingestion and were not cleaned before promotion to gold tier.

| File | Contaminated Column Count | Example Bad Column Names |
|------|--------------------------|--------------------------|
| `oasis_abilities.parquet` | 14 | `'Categorization Flexibility '`, `'Deductive Reasoning '`, `'Far Vision '` |
| `oasis_skills.parquet` | 6 | `'Writing  '` (2 spaces), `' Digital Literacy'` (leading), `'Oral Communication: Active Listening   '` (3 trailing spaces) |
| `oasis_workactivities.parquet` | 3 | `'Monitoring Processes, Materials, or Surroundings '` |
| `oasis_workcontext.parquet` | 3 | `'Radiation '`, `'Sound and Noise '`, `'Climbing '` |
| `oasis_knowledges.parquet` | 1 | `'Physics '` |

**Required fix for all Phase 22 and Phase 23 code reading these files:**

```python
df = pd.read_parquet(path)
df.columns = df.columns.str.strip()  # Must be called before any column access
```

The `parquet_reader.py` helper introduced in DATA-03 applies this automatically so Phase 22 code that uses the reader helper gets the fix for free.

**Risk if not fixed:** `KeyError` at runtime when accessing columns like `df['Writing']` when the actual column name is `df['Writing  ']`. The error message will show the column name you used, not the actual name with whitespace, making debugging confusing.

---

## Decision Summary for Phase 22 Implementers

| OASIS Field | Action in Phase 22 | Notes |
|-------------|-------------------|-------|
| Skills | Use `oasis_skills.parquet` | Strip column whitespace |
| Abilities | Use `oasis_abilities.parquet` | Strip column whitespace (14 cols) |
| Knowledge | Use `oasis_knowledges.parquet` | Strip column whitespace (1 col) |
| Work Activities | Use `oasis_workactivities.parquet` | Strip column whitespace |
| Work Context | Use `oasis_workcontext.parquet` | Strip column whitespace |
| Label / Title | Use `element_labels.parquet` | No whitespace issues |
| Lead Statement | Use `element_lead_statement.parquet` | No whitespace issues |
| Example Titles | Use `element_example_titles.parquet` | No whitespace issues |
| Employment Requirements | Use `element_employment_requirements.parquet` | No whitespace issues |
| Workplaces and Employers | Use `element_workplaces_employers.parquet` | No whitespace issues |
| Exclusions | Use `element_exclusions.parquet` | 30 profiles legitimately absent |
| Additional Info | Use `element_additional_information.parquet` | 205 profiles legitimately absent |
| Main Duties / Key Activities | OASIS scraping (unconditional) | Never read element_main_duties.parquet |
| Interests / Holland Codes | Source CSV via LabelsLoader (existing) | No change needed |
| Personal Attributes | Source CSV via LabelsLoader (existing) | No change needed |
| Core Competencies | OASIS scraping only | No parquet or CSV exists |
| Career Mobility | OASIS scraping only | No parquet or CSV exists |
