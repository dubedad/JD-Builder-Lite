# JobForge Gold Parquet Inventory

**Path:** `/Users/victornishi/Documents/GitHub/JobForge-2.0/data/gold/`
**Last verified:** 2026-03-07
**File count:** 25 parquet files
**Total profiles in gold tier:** 900 OASIS profiles (516 NOC unit groups)

---

## Quick Reference Summary Table

| File | Rows | Profiles | Profile Key | OASIS Mapping |
|------|------|----------|-------------|---------------|
| element_labels.parquet | 900 | 900 | oasis_profile_code | NOC occupational label/title |
| element_lead_statement.parquet | 900 | 900 | oasis_profile_code | Lead statement / career overview |
| element_example_titles.parquet | 18,666 | 900 | oasis_profile_code | Example job titles ("Also known as") |
| element_employment_requirements.parquet | 2,851 | 900 | oasis_profile_code | Employment requirements |
| element_exclusions.parquet | 3,074 | 870 | oasis_profile_code | NOC exclusions (30 profiles have none) |
| element_workplaces_employers.parquet | 3,418 | 900 | oasis_profile_code | Workplaces and employers |
| element_additional_information.parquet | 1,158 | 695 | oasis_profile_code | Additional information (partial coverage) |
| element_main_duties.parquet | **8** | **3** | oasis_profile_code | **CRITICAL GAP: Main duties/key activities** |
| oasis_abilities.parquet | 900 | 900 | oasis_code | Abilities ratings (50 dimensions) |
| oasis_skills.parquet | 900 | 900 | oasis_code | Skills ratings (37 dimensions) |
| oasis_knowledges.parquet | 900 | 900 | oasis_code | Knowledge ratings (48 areas) |
| oasis_workactivities.parquet | 900 | 900 | oasis_code | Work Activities ratings (44 dimensions) |
| oasis_workcontext.parquet | 900 | 900 | oasis_code | Work Context ratings (70 dimensions) |
| dim_noc.parquet | 516 | 516 | noc_code | NOC unit group definitions |
| dim_occupations.parquet | 212 | N/A | occupation_group_id | Job Architecture taxonomy |
| job_architecture.parquet | 1,987 | N/A | jt_id | GC job titles to NOC mapping |
| fact_og_pay_rates.parquet | 991 | N/A | og_subgroup_code | TBS occupational group pay rates |
| cops_employment.parquet | 516 | N/A | unit_group_id | Employment projections 2023-2033 |
| cops_employment_growth.parquet | 516 | N/A | unit_group_id | Employment growth projections |
| cops_immigration.parquet | 516 | N/A | unit_group_id | Immigration intake data |
| cops_other_replacement.parquet | 516 | N/A | unit_group_id | Other replacement labour data |
| cops_other_seekers.parquet | 516 | N/A | unit_group_id | Other job seekers data |
| cops_retirement_rates.parquet | 516 | N/A | unit_group_id | Retirement rate projections |
| cops_retirements.parquet | 516 | N/A | unit_group_id | Retirement count projections |
| cops_school_leavers.parquet | 516 | N/A | unit_group_id | School leavers data |

---

## Profile Data Files

These files contain occupational profile content that maps directly to OASIS profile tabs. They are keyed by `oasis_profile_code` (format: `'21211.00'`) or `oasis_code` for the oasis_* rating files. 516 NOC unit groups expand to 900 OASIS profiles (some NOC codes have multiple sub-profiles, e.g. `10020.01`, `10020.02`).

---

### element_labels.parquet

- **Rows:** 900
- **Profiles:** 900 distinct (column: `oasis_profile_code`)
- **Columns:** `unit_group_id`, `noc_element_code`, `oasis_profile_code`, `Label`, `_source_file`, `_ingested_at`, `_batch_id`, `_layer`
- **OASIS mapping:** NOC occupational label and title -- the official name of the occupational profile (e.g. "Software Engineers and Designers")
- **Notes:** Full 900-profile coverage. No whitespace-contaminated column names. This is the primary lookup file for profile titles. Used by existing `labels_loader.py`.

---

### element_lead_statement.parquet

- **Rows:** 900
- **Profiles:** 900 distinct (column: `oasis_profile_code`)
- **Columns:** `unit_group_id`, `noc_element_code`, `oasis_profile_code`, `Lead statement`, `_source_file`, `_ingested_at`, `_batch_id`, `_layer`
- **OASIS mapping:** Lead statement / career overview -- the introductory paragraph describing what workers in the group do
- **Notes:** Full 900-profile coverage. Column name `Lead statement` contains a space but no trailing whitespace contamination. Phase 22 must access via `df['Lead statement']` exactly.

---

### element_example_titles.parquet

- **Rows:** 18,666
- **Profiles:** 900 distinct (column: `oasis_profile_code`)
- **Columns:** `unit_group_id`, `noc_element_code`, `oasis_profile_code`, `Concordance number`, `Job title type`, `Job title text`, `_source_file`, `_ingested_at`, `_batch_id`, `_layer`
- **OASIS mapping:** Example job titles ("Also known as" section in NOC profiles) -- alternative occupational titles
- **Notes:** Full 900-profile coverage. Multiple rows per profile (average ~20 titles per profile). Used by existing `labels_loader.py` for title lookup.

---

### element_employment_requirements.parquet

- **Rows:** 2,851
- **Profiles:** 900 distinct (column: `oasis_profile_code`)
- **Columns:** `unit_group_id`, `noc_element_code`, `oasis_profile_code`, `Employment requirement`, `_source_file`, `_ingested_at`, `_batch_id`, `_layer`
- **OASIS mapping:** Employment requirements -- education, training, certification, and experience requirements for the occupation
- **Notes:** Full 900-profile coverage. Multiple rows per profile (average ~3 requirements). Replaces OASIS scraping for this section.

---

### element_exclusions.parquet

- **Rows:** 3,074
- **Profiles:** 870 distinct (column: `oasis_profile_code`)
- **Columns:** `unit_group_id`, `noc_element_code`, `oasis_profile_code`, `Excluded code`, `Job title`, `_source_file`, `_ingested_at`, `_batch_id`, `_layer`
- **OASIS mapping:** NOC exclusions -- related occupations explicitly excluded from this profile group
- **Notes:** 870 of 900 profiles have exclusions; 30 profiles legitimately have none (e.g. single-occupation NOC codes). Used by existing `labels_loader.py`.

---

### element_workplaces_employers.parquet

- **Rows:** 3,418
- **Profiles:** 900 distinct (column: `oasis_profile_code`)
- **Columns:** `unit_group_id`, `noc_element_code`, `oasis_profile_code`, `Workplace/employer name`, `Profile name`, `_source_file`, `_ingested_at`, `_batch_id`, `_layer`
- **OASIS mapping:** Workplaces and employers -- types of employers and work settings for the occupation
- **Notes:** Full 900-profile coverage. Multiple rows per profile (average ~4 workplaces). Replaces OASIS scraping for this section.

---

### element_additional_information.parquet

- **Rows:** 1,158
- **Profiles:** 695 distinct (column: `oasis_profile_code`)
- **Columns:** `unit_group_id`, `noc_element_code`, `oasis_profile_code`, `Additional information (EN)`, `_source_file`, `_ingested_at`, `_batch_id`, `_layer`
- **OASIS mapping:** Additional information (English) -- supplementary occupational notes not covered by other elements
- **Notes:** Partial coverage -- 695 of 900 profiles (77%). 205 profiles have no additional information entry; this is expected (not all profiles have supplementary notes in OASIS source). Column name contains parentheses: `Additional information (EN)`.

---

### element_main_duties.parquet

- **Rows:** 8
- **Profiles:** 3 distinct (column: `oasis_profile_code`)
- **Columns:** `unit_group_id`, `noc_element_code`, `oasis_profile_code`, `Main Duty`, `_source_file`, `_ingested_at`, `_batch_id`, `_layer`
- **OASIS mapping:** Main Duties / Key Activities -- the primary work activities performed by workers in this group
- **Notes:** CRITICAL GAP. ETL is incomplete. Source CSV (`main-duties_oasis-2023_v1.0.csv`) contains 4,991 rows / 900 profiles; gold parquet has only 8 rows / 3 profiles. Phase 22 must NOT attempt parquet lookup for Main Duties -- use OASIS live scraping unconditionally until JobForge ETL runs. See GAP-ANALYSIS.md.

---

### oasis_abilities.parquet

- **Rows:** 900
- **Profiles:** 900 distinct (column: `oasis_code`)
- **Columns (57 total):** `unit_group_id`, `noc_element_code`, `oasis_code`, `oasis_label`, plus 50 ability dimension columns, plus `_source_file`, `_ingested_at`, `_batch_id`, `_layer`
- **Ability dimensions (50):** Categorization Flexibility, Deductive Reasoning, Fluency of Ideas, Inductive Reasoning, Information Ordering, Mathematical Reasoning, Memorizing, Multitasking, Numerical Ability, Pattern Identification, Pattern Organization Speed, Perceptual Speed, Problem Identification, Selective Attention, Spatial Orientation, Spatial Visualization, Verbal Ability, Written Comprehension, Written Expression, Body Flexibility, Dynamic Strength, Explosive Strength, Gross Body Coordination, Gross Body Equilibrium, Multi-Limb Coordination, Stamina, Static Strength, Trunk Strength, Arm-Hand Steadiness, Control of Settings, Finger Dexterity, Manual Dexterity, Multi-Signal Response, Rate Control, Reaction Time, Speed of Limb Movement, Finger-Hand-Wrist Motion, Auditory Attention, Depth Perception, Far Vision, Glare Tolerance, Hearing Sensitivity, Near Vision, Night Vision, Peripheral Vision, Speech Clarity, Speech Recognition, Sound Localization, Colour Perception
- **OASIS mapping:** Abilities ratings -- OASIS ability requirements for the occupation (each column is a rated ability dimension)
- **Notes:** Full 900-profile coverage. 14 WHITESPACE-CONTAMINATED column names (trailing spaces): `Categorization Flexibility `, `Deductive Reasoning `, `Fluency of Ideas `, `Information Ordering `, `Numerical Ability `, `Pattern Identification `, `Selective Attention `, `Spatial Orientation `, `Explosive Strength `, `Static Strength `, `Arm-Hand Steadiness `, `Auditory Attention `, `Far Vision `, `Glare Tolerance `. Must call `df.columns = df.columns.str.strip()` after reading. Used by vocabulary index in `src/vocabulary/`.

---

### oasis_skills.parquet

- **Rows:** 900
- **Profiles:** 900 distinct (column: `oasis_code`)
- **Columns (41 total):** `unit_group_id`, `noc_element_code`, `oasis_code`, `oasis_label`, plus 37 skill dimension columns, plus `_source_file`, `_ingested_at`, `_batch_id`, `_layer`
- **Skill dimensions (37):** Reading Comprehension, Writing, Numeracy, Digital Literacy, Oral Communication: Active Listening, Oral Communication: Oral Comprehension, Oral Communication: Oral Expression, Critical Thinking, Decision Making, Evaluation, Learning and Teaching Strategies, Problem Solving, Systems Analysis, Digital Production, Preventative Maintenance, Equipment and Tool Selection, Operation and Control, Operation Monitoring of Machinery and Equipment, Quality Control Testing, Repairing, Setting up, Product Design, Troubleshooting, Management of Financial Resources, Management of Material Resources, Management of Personnel Resources, Monitoring, Time Management, Coordinating, Instructing, Negotiating, Persuading, Social Perceptiveness
- **OASIS mapping:** Skills ratings -- OASIS skill requirements for the occupation
- **Notes:** Full 900-profile coverage. 6 WHITESPACE-CONTAMINATED column names: `Writing  ` (2 trailing spaces), `Numeracy `, ` Digital Literacy` (leading space), `Oral Communication: Active Listening   ` (3 trailing spaces), `Oral Communication: Oral Comprehension   ` (3 trailing spaces), `Oral Communication: Oral Expression `. Must call `df.columns = df.columns.str.strip()` after reading. Used by vocabulary index in `src/vocabulary/`.

---

### oasis_knowledges.parquet

- **Rows:** 900
- **Profiles:** 900 distinct (column: `oasis_code`)
- **Columns (52 total):** `unit_group_id`, `noc_element_code`, `oasis_code`, `oasis_label`, plus 48 knowledge area columns, plus `_source_file`, `_ingested_at`, `_batch_id`, `_layer`
- **Knowledge areas (48):** Accounting, Business Administration, Clerical, Finance, Human Resources and Labour relations, Sale and Marketing, Client Services, Communications and Media, Teaching, Training, Mentoring and Coaching, Hospitality, Mental Health, Physical Health, Recreation, Leisure and Fitness, Veterinarian and Animal Care, Law, Public Affairs and Government relations, Public Safety and Security, Manufacturing Processing and Production, Logistics, Performance Measurement, Technical Design, Agriculture and horticulture, Forestry, Geological Resources, Livestock Farm animals and Wildlife, Water Resources, Biology, Chemistry, Geoscience, Physics, Arts, Economics, Humanities, Library Conservation and Heritage, Theology and Philosophy, Building and Construction, Computer technology and Information Systems, Electrical and Electronics, Mechanics and Machinery, Telecommunications, Vehicles and Machinery Operations, Languages, Mathematics
- **OASIS mapping:** Knowledge ratings -- OASIS knowledge requirements for the occupation
- **Notes:** Full 900-profile coverage. 1 WHITESPACE-CONTAMINATED column name: `Physics ` (trailing space). Must call `df.columns = df.columns.str.strip()` after reading. Used by vocabulary index in `src/vocabulary/`.

---

### oasis_workactivities.parquet

- **Rows:** 900
- **Profiles:** 900 distinct (column: `oasis_code`)
- **Columns (48 total):** `unit_group_id`, `noc_element_code`, `oasis_code`, `oasis_label`, plus 44 work activity dimension columns, plus `_source_file`, `_ingested_at`, `_batch_id`, `_layer`
- **Work activity dimensions (44):** Estimate Quantifiable Charact. of Prod. Events or Info., Getting Information, Identifying Objects Actions and Events, Inspecting Equipment Structures or Material, Monitoring Processes Materials or Surroundings, Controlling Machines and Processes, Developing Technical Instructions, Clerical Activities, Electronic Maintenance, Handling and Moving Objects, Interacting with Computers, Managing Resources, Mechanical Maintenance, Operating Vehicles Mechanized Devices or Equipment, Performing General Physical Activities, Processing Information, Analyzing Data or Information, Developing Objectives and Strategies, Evaluating Information to Determine Compliance with Standards, Judging Quality, Making Decisions, Planning and Organizing, Scheduling Work and Activities, Thinking Creatively, Using New Relevant Knowledge, Assisting and Caring for Others, Coaching and Developing Others, Communicating with Persons Outside Organization, Communicating with Coworkers, Coordinating the Work and Activities of Others, Establishing and Maintaining Interpersonal Relationships, Interpreting the Meaning of Information for Others, Performing for or Working Directly with the Public, Providing Consultation and Advice, Resolving Conflicts and Negotiating with Others, Selling or Influencing Others, Staffing, Supervising Subordinates, Team Building, Training and Teaching
- **OASIS mapping:** Work Activities ratings -- OASIS work activity requirements (what workers do on the job)
- **Notes:** Full 900-profile coverage. 3 WHITESPACE-CONTAMINATED column names: `Monitoring Processes, Materials, or Surroundings `, `Staffing `, `Training and Teaching `. Must call `df.columns = df.columns.str.strip()` after reading. Used by vocabulary index in `src/vocabulary/`.

---

### oasis_workcontext.parquet

- **Rows:** 900
- **Profiles:** 900 distinct (column: `oasis_code`)
- **Columns (74 total):** `unit_group_id`, `noc_element_code`, `oasis_code`, `oasis_label`, plus 70 work context dimension columns, plus `_source_file`, `_ingested_at`, `_batch_id`, `_layer`
- **Work context dimensions (70):** Automation, Competition, Consequence of Error, Freedom to Make Decisions, Frequency of Decision Making, Impact of Decisions, Pace Determined by Speed of Equipment, Precision, Structured versus Unstructured Work, Tasks Repetition, Time Pressure, Time Pressure2, Work Schedule, Work Week Duration, Biological Agents, Dangerous Chemical Substances, Extremely Bright or Inadequate Lighting, Extreme Temperatures, Hazardous Conditions, Hazardous Equipment Machinery Tools, High Places, In an Enclosed Vehicle or Equipment (x2), In an Open Vehicle or Equipment (x2), Indoors Environmentally Controlled (x2), Indoors Not Environmentally Controlled (x2), Outside Exposed to Weather (x2), Outside Under Cover (x2), Physical Proximity, Radiation, Sound and Noise (x2), Specialized Safety Equipment, Standard Safety Equipment, Vibration, Skin Injury, Bending or Twisting the Body, Climbing, Cramped Work Space Awkward Positions, Handling Material Manually, Keeping or Regaining Balance, Making Repetitive Motions, Sitting, Standing, Walking and Running, Conflict Situations, Contact With Others (x2), Coordinating or Leading Others, Deal With External Customers, Deal With Physically Aggressive People, Dealing With Unpleasant or Angry People, Electronic Mail, Face-to-Face Discussions, Written Communications, Public Speaking, Responsibility for Outcomes and Results of Other Workers, Responsible for Others Health and Safety, Telephone, Work With Work Group or Team (x2)
- **OASIS mapping:** Work Context ratings -- physical and social work environment characteristics. Used in existing `labels_loader.py` for work context tab.
- **Notes:** Full 900-profile coverage. 3 WHITESPACE-CONTAMINATED column names: `Radiation `, `Sound and Noise `, `Climbing `. Must call `df.columns = df.columns.str.strip()` after reading. Several dimensions appear twice with a numeric suffix (e.g. `Time Pressure2`, `Contact With Others10`) -- these are duplicate columns from the source OASIS export; Phase 22 should be aware.

---

## Reference / Dimensional Files

These files provide lookup and taxonomy data. They do not map to OASIS profile tabs directly but support search, classification, and job architecture features.

---

### dim_noc.parquet

- **Rows:** 516
- **Profiles:** 516 distinct (column: `noc_code`)
- **Columns:** `unit_group_id`, `noc_code`, `class_title`, `class_definition`, `hierarchical_structure`, `_source_file`, `_ingested_at`, `_batch_id`, `_layer`
- **OASIS mapping:** Supplements OASIS -- `class_definition` matches the profile description text shown on OASIS profile pages. `class_title` matches the occupational group title. This file covers all 516 NOC unit groups (not 900 OASIS profiles -- NOC codes do not have sub-profiles).
- **Notes:** Key column is `noc_code` (5-digit string, no decimal, e.g. `'21211'`) -- different from `oasis_profile_code` format (`'21211.00'`). Phase 22 must not conflate these. This is the file to use for NOC unit group definitions when the 516-vs-900 mapping is not needed.

---

### dim_occupations.parquet

- **Rows:** 212
- **Profiles:** No profile key (no `oasis_profile_code` or `noc_code` column)
- **Columns:** `job_family_en`, `job_family_fr`, `job_function_en`, `job_function_fr`, `occupation_group_id`, `_source_file`, `_ingested_at`, `_batch_id`, `_layer`
- **OASIS mapping:** N/A -- reference data. This is the GC Job Architecture taxonomy (job families and functions) -- no direct OASIS equivalent.
- **Notes:** 212 rows representing the GC job family/function taxonomy. Used for occupational group classification. No profile lookup capability.

---

### job_architecture.parquet

- **Rows:** 1,987
- **Profiles:** No standard profile key (has `noc_2021_uid` and `jt_id` columns)
- **Columns:** `jt_id`, `unit_group_id`, `job_title_en`, `job_title_fr`, `job_function_en`, `job_function_fr`, `job_family_en`, `job_family_fr`, `managerial_level_en`, `managerial_level_fr`, `noc_2021_uid`, `noc_2021_title`, `_source_file`, `_ingested_at`, `_batch_id`, `_layer`
- **OASIS mapping:** N/A -- reference data. Maps GC-specific job titles to NOC 2021 codes, job functions, and job families. No OASIS equivalent.
- **Notes:** 1,987 GC job title records mapped to 363 distinct `noc_2021_uid` values. Used for job title search and classification matching. Bilingual (English/French) job titles and taxonomy labels.

---

## Labour Market Files

These files contain COPS (Canadian Occupational Projection System) employment projections and TBS pay rate data. They are not relevant to OASIS profile tab display but may be used for future labour market insights.

---

### cops_employment.parquet

- **Rows:** 516
- **Profiles:** No profile key (no `oasis_profile_code` or `noc_code` column; uses `unit_group_id` and `code`)
- **Columns:** `unit_group_id`, `code`, `occupation_name_en`, `occupation_name_fr`, `2023`, `2024`, `2025`, `2026`, `2027`, `2028`, `2029`, `2030`, `2031`, `2032`, `2033`, `_source_file`, `_ingested_at`, `_batch_id`, `_layer`
- **OASIS mapping:** N/A -- reference data. Employment counts by year (2023-2033 projections) for each of 516 NOC unit groups.
- **Notes:** Columns `2023` through `2033` are year-keyed employment count projections. Same schema as all other cops_* files.

---

### cops_employment_growth.parquet

- **Rows:** 516
- **Profiles:** No profile key (column: `unit_group_id`)
- **Columns:** `unit_group_id`, `code`, `occupation_name_en`, `occupation_name_fr`, `2023`-`2033`, `_source_file`, `_ingested_at`, `_batch_id`, `_layer`
- **OASIS mapping:** N/A -- reference data. Employment growth projections by year for 516 NOC unit groups.
- **Notes:** Same schema as cops_employment.parquet. Values represent growth rates or growth counts (not raw employment).

---

### cops_immigration.parquet

- **Rows:** 516
- **Profiles:** No profile key (column: `unit_group_id`)
- **Columns:** `unit_group_id`, `code`, `occupation_name_en`, `occupation_name_fr`, `2023`-`2033`, `_source_file`, `_ingested_at`, `_batch_id`, `_layer`
- **OASIS mapping:** N/A -- reference data. Immigration intake data by year for 516 NOC unit groups.
- **Notes:** Same schema as other cops_* files.

---

### cops_other_replacement.parquet

- **Rows:** 516
- **Profiles:** No profile key (column: `unit_group_id`)
- **Columns:** `unit_group_id`, `code`, `occupation_name_en`, `occupation_name_fr`, `2023`-`2033`, `_source_file`, `_ingested_at`, `_batch_id`, `_layer`
- **OASIS mapping:** N/A -- reference data. Other replacement demand (non-retirement) by year for 516 NOC unit groups.
- **Notes:** Same schema as other cops_* files.

---

### cops_other_seekers.parquet

- **Rows:** 516
- **Profiles:** No profile key (column: `unit_group_id`)
- **Columns:** `unit_group_id`, `code`, `occupation_name_en`, `occupation_name_fr`, `2023`-`2033`, `_source_file`, `_ingested_at`, `_batch_id`, `_layer`
- **OASIS mapping:** N/A -- reference data. Other job seekers data by year for 516 NOC unit groups.
- **Notes:** Same schema as other cops_* files.

---

### cops_retirement_rates.parquet

- **Rows:** 516
- **Profiles:** No profile key (column: `unit_group_id`)
- **Columns:** `unit_group_id`, `code`, `occupation_name_en`, `occupation_name_fr`, `2023`-`2033`, `_source_file`, `_ingested_at`, `_batch_id`, `_layer`
- **OASIS mapping:** N/A -- reference data. Retirement rate projections by year for 516 NOC unit groups.
- **Notes:** Same schema as other cops_* files.

---

### cops_retirements.parquet

- **Rows:** 516
- **Profiles:** No profile key (column: `unit_group_id`)
- **Columns:** `unit_group_id`, `code`, `occupation_name_en`, `occupation_name_fr`, `2023`-`2033`, `_source_file`, `_ingested_at`, `_batch_id`, `_layer`
- **OASIS mapping:** N/A -- reference data. Retirement count projections by year for 516 NOC unit groups.
- **Notes:** Same schema as other cops_* files.

---

### cops_school_leavers.parquet

- **Rows:** 516
- **Profiles:** No profile key (column: `unit_group_id`)
- **Columns:** `unit_group_id`, `code`, `occupation_name_en`, `occupation_name_fr`, `2023`-`2033`, `_source_file`, `_ingested_at`, `_batch_id`, `_layer`
- **OASIS mapping:** N/A -- reference data. School leavers entering the labour market by year for 516 NOC unit groups.
- **Notes:** Same schema as other cops_* files. All cops_* files share identical column structure.

---

### fact_og_pay_rates.parquet

- **Rows:** 991
- **Profiles:** No profile key (no `oasis_profile_code` or `noc_code`; uses `og_subgroup_code` and `og_code`)
- **Columns:** `og_subgroup_code`, `og_code`, `classification_level`, `step`, `annual_rate`, `hourly_rate`, `effective_date`, `is_represented`, `collective_agreement`, `_source_url`, `_scraped_at`, `_source_file`, `_ingested_at`, `_batch_id`, `_layer`
- **OASIS mapping:** N/A -- reference data. TBS occupational group pay rates by classification level and step. No OASIS equivalent.
- **Notes:** 991 rows covering TBS occupational group pay scales. Used for classification pay rate lookup. Keyed by `og_subgroup_code` (e.g. `'CS'`) and `classification_level` (e.g. `'CS-01'`).

---

## Key Technical Notes for Phase 22 and Phase 23

### Profile Code Format

Two distinct key formats exist in the gold tier:

| Format | Example | Used In | Phase 22 Action |
|--------|---------|---------|-----------------|
| `oasis_profile_code` | `'21211.00'` | element_* and oasis_* files | NOC code `'21211'` must be transformed to `'21211.00'` before lookup |
| `noc_code` | `'21211'` | dim_noc.parquet | Use directly -- no transformation needed |
| `unit_group_id` | `'21211'` | cops_* files, dim_noc | Same as noc_code for unit group lookups |

**Rule:** When querying `element_labels.parquet`, `oasis_abilities.parquet`, and all other element_* or oasis_* files, append `.00` to a 5-digit NOC code. Some NOC codes have multiple sub-profiles (`10020.01`, `10020.02`, etc.); the primary profile is typically `.01` or `.00`. Phase 22 must handle the case where `.00` returns no results by also trying `.01`.

### Column Whitespace Contamination

Five OASIS-prefix parquet files have column names with leading or trailing whitespace:

| File | Count | Examples |
|------|-------|---------|
| oasis_abilities.parquet | 14 cols | `'Categorization Flexibility '`, `'Far Vision '` |
| oasis_skills.parquet | 6 cols | `'Writing  '`, `' Digital Literacy'`, `'Oral Communication: Active Listening   '` |
| oasis_workactivities.parquet | 3 cols | `'Monitoring Processes, Materials, or Surroundings '` |
| oasis_workcontext.parquet | 3 cols | `'Radiation '`, `'Sound and Noise '` |
| oasis_knowledges.parquet | 1 col | `'Physics '` |

**Required fix:** After `pd.read_parquet(path)`, always call `df.columns = df.columns.str.strip()` before any column access for these files. The `parquet_reader.py` helper introduced in DATA-03 applies this automatically.

### element_main_duties.parquet is a Known Bad File

Do not attempt parquet lookup for Main Duties in Phase 22. The file reads without error (it is structurally valid) but covers only 3 of 900 profiles. Any lookup will return `NOT_FOUND` for 99.7% of profiles. The OASIS fallback is unconditional for Main Duties until JobForge ETL completes the full pipeline. See GAP-ANALYSIS.md for full gap documentation.
