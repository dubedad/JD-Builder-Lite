# UAT Findings — Full UX Walkthrough

**Date:** 2026-02-06
**App:** JD Builder Lite (localhost:5000)
**Version:** v4.0 + quick-001

---

## Step 1: Search (Nav Bar)

### S1-01: Hide low-confidence results
- **Issue:** Results with 20% or less confidence are shown
- **Want:** Filter out / hide results at or below 20% confidence
- **Category:** Quick fix

### S1-02: Occupational category filter — show hierarchy
- **Issue:** Occupational category filter doesn't show sub-major and minor group headings
- **Want:** Filter items should display sub-major group and minor group headings the user can filter by
- **Category:** Enhancement

### S1-03: Match rationale — specify WHERE in the NOC hierarchy the match occurred
- **Issue:** Rationale currently says generic things like `Title contains "police"`
- **Want:** Rationale must specify the NOC hierarchy level where the match was found:
  - **Unit Group** match — e.g., `40040.00 - Commissioned police officers...` → rationale: `Unit Group contains "police"`
  - **Unit Group Label** match — e.g., `42100.01 - Police Investigators` → rationale: `Unit Group Label contains "police"`
  - **Example Title** match — keyword found in an example title listed under a label
- **Alternative considered:** Instead of text labels, provide a **granularity score** based on NOC hierarchy level:
  - Unit Group = level 5
  - Label = level 6
  - Example Title = level 7
- **Decision needed at triage:** Text labels vs. granularity score vs. both

### S1-04: Matching Search Criteria — show the actual matched content in the card
- **Issue:** User can't see WHAT content within the NOC attributes matched their keyword
- **Want:**
  - Each result card gets a **magnifying glass bullet** section: "Matching Search Criteria:"
  - Under it, show the **actual content** from each NOC attribute where the keyword appears
  - Example: keyword "police", result "14404.00 - Dispatchers" → show the text from Workplaces/employers that references "police"
  - Show matches from **ALL attributes** where the keyword appears, not just the first one
- **Category:** Enhancement (significant — requires attribute-level search indexing)

### S1-05: Sort by matched NOC attribute
- **Issue:** Sort options don't relate to search match quality
- **Want:** "Sort by" selections should sort by whichever NOC attributes appeared as matching search criteria
- **Category:** Enhancement

### S1-06: Search from JobForge Gold Tables
- **Issue:** Currently only searches OASIS/NOC data
- **Want:** User can search using fields from the GOld Job Architecture table in JobForge 2.0:
  - Job Titles
  - Job Families
  - Job Functions
  - Managerial Level
- **Dependency:** Requires a lookup table built from the JobForge job architecture
- **Category:** SEED — requires JobForge integration + lookup table creation

### S1-07: JobForge-first search priority
- **Issue:** Currently OASIS is the only data source
- **Want:** JD Builder must reference JobForge gold tables FIRST, then OASIS website, before presenting search results
- **Category:** SEED — architectural change, data source priority ordering

### S1-08: CAF Careers Taxonomy as additional result source
- **Issue:** Results only come from NOC taxonomy
- **Want:** Results can come from NOC taxonomy OR the CAF Careers Taxonomy
- **Category:** SEED — requires CAF taxonomy integration

### S1-09: Multi-result selection for JD building
- **Issue:** Currently user selects a single profile to build a JD from
- **Want:** User can select **multiple results** from search, and statements from all selected results appear in the "BUILD JD" step
- **Category:** Enhancement (significant — changes JD assembly flow)

### S1-11: Replace "Feeder Group Mobility" and "Career Progression" filters
- **Issue:** Search results screen has filter items for "Feeder Group Mobility" and "Career Progression" — not useful
- **Want:** Remove both and replace with:
  - **TEER Level** (0-5) — filter by education/training tier (data already in search results)
  - **Confidence Threshold** (slider) — user-controlled minimum confidence cutoff (relates to S1-01)
  - **Match Type** — where keyword was found: Unit Group / Label / Example Title / Attribute content (requires S1-10)
  - **Job Family** — from JobForge `job_architecture` (requires S1-06/S1-10)
  - **Managerial Level** — from JobForge `job_architecture` (requires S1-06/S1-10)
  - **Data Source** — NOC / CAF / JobForge, once multi-taxonomy exists (requires S1-08)
- **Phasing:** TEER Level + Confidence Threshold are immediate (current data). Match Type, Job Family, Managerial Level, Data Source require S1-10 first.
- **Category:** Enhancement (phased — some quick, some depend on S1-10)

### S1-12: Search quality — "data engineer" misses obvious results
- **Issue:** Searching "data engineer" only returns "Data Scientist" but misses "Database analysts", "Data Administrators", "Network system and data communication engineers"
- **Root cause:** Search is delegated to OASIS website which has limited keyword matching (likely unit group title only). JD Builder has no control over OASIS's search algorithm.
- **Want:** Search should match across all NOC text fields (titles, labels, example titles, lead statements, main duties) and return all relevant occupations
- **Dependency:** Requires S1-10 (local data source) to control the search algorithm
- **Note:** Also a case for semantic/fuzzy search — "data engineer" is conceptually close to "database administrator" even without exact word overlap
- **Category:** Enhancement (blocked by S1-10)

### S1-10: SEED — Switch primary data source from OASIS scraping to JobForge gold
- **Issue:** JD Builder scrapes OASIS HTML live for all data (slow, fragile). JobForge gold already contains ~90% of the same data in local parquet files.
- **Want:** JD Builder reads from JobForge gold parquet as primary source; OASIS only for anything missing.
- **Gap analysis (what JobForge gold is missing):**
  - Interests — source CSV exists, needs gold ETL
  - Personal attributes — source CSV exists, needs gold ETL
  - Core competencies — needs sourcing
  - Guide/scale definitions — static reference, can bundle
- **JobForge gold coverage:**
  - `dim_noc` — NOC hierarchy (codes, titles, TEER, broad category)
  - `element_*` (7 tables) — lead statements, main duties, example titles, exclusions, employment requirements, workplaces, labels, additional info
  - `oasis_*` (4 tables) — skills, abilities, knowledges, work activities, work context (all with scores)
  - `job_architecture` — job titles, families, functions, managerial levels + 40+ skill scores
  - `bridge_*` — NOC-to-OG, CAF-to-NOC, CAF-to-JA crosswalks
  - `dim_caf_*` — CAF occupations, families, training
  - `dim_og_*` — OG subgroups, qualifications, evaluation standards
  - `cops_*` — employment forecasts
- **Impact:** Eliminates live scraping dependency, enables local full-text search across all attributes, enables S1-03/S1-04/S1-05/S1-06
- **Category:** SEED — architectural (prerequisite for many S1 enhancements)

### S1-13: GitHub repo needs updating (README, docs)
- **Issue:** GitHub repo for JD Builder Lite has outdated README and documentation — doesn't reflect current v4.0 state
- **Want:** Update README and repo docs to reflect shipped features, current architecture, setup instructions
- **Category:** Housekeeping (not UX — but flagged during walkthrough)

### S1-15: Scoring needs a 100% tier for exact title matches
- **Issue:** Searching "administrative assistant" → "Administrative assistants" scores 95%, same as results where the query is just a phrase within a longer title. No distinction between "query IS the title" and "query is IN the title".
- **Root cause:** Scoring logic (`api.py:112-113`) has one tier for all "title contains query" cases (95%).
- **Want:** Three-tier title matching:
  - **100%** — query ≈ title (near-exact after normalizing plurals/case): "administrative assistant" = "Administrative assistants"
  - **95%** — full query phrase is a substring of a longer title: "administrative assistants" found inside "Secretaries, administrative assistants and related occupations"
  - **85%** — only stem matches in title: "administrat" in title (already works)
- **Confirmed by UAT:** Results 2 and 3 correctly score higher than stem-only matches, but lower than the exact match. The 95% tier is correct for "query is a subset of the Unit Group Title" — just needs the 100% tier added above it.
- **Category:** Quick fix

### S1-16: Show scoring legend in lower-left white space on search results
- **Issue:** User sees confidence percentages (100%, 95%, 85%, etc.) but has no key explaining what they mean
- **Want:** Small legend in the lower-left open white space of the search results screen:
  - 100% — Exact title match
  - 95% — Title contains full search phrase
  - 85% — Title contains word stem
  - 60% — Description contains search phrase
  - 50% — Description contains word stem
- **Category:** Quick fix (static HTML/CSS)

### S1-14: Nav bar missing on JD Preview screen
- **Issue:** When preview loads, the GC CDTS header/navbar disappears — preview replaces entire body
- **Want:** GC header visible on preview screen same as all other screens
- **Category:** Quick fix
- **Status:** FIXED in-session (added GC header to jd_preview.html)

---

## Step 2: Select Profile (Nav Bar)

### S2-01: Remove redundant provenance labels under grouped headers
- **Issue:** Statements under "Main Duties" header each say "from Main Duties" — redundant since the header already says it
- **Want:** Remove "from [source]" labels when the statement is already under a matching header
- **Exception:** Keep provenance labels on Effort and Responsibility tabs (work context items come from different dimensions)
- **Category:** Quick fix

### S2-02: Split Skills tab — Abilities and Knowledge get their own tabs
- **Issue:** Abilities and Knowledge are lumped under the Skills tab
- **Want:** Three separate tabs: Skills, Abilities, Knowledge
- **Category:** Enhancement (tab restructure)

### S2-03: Core Competencies — move out of Overview into its own tab
- **Issue:** Core Competencies are currently inside the Overview section
- **Want:** Create a new dedicated tab for Core Competencies
- **Category:** Enhancement (tab restructure)

### S2-04: Move navy blue description section into Overview tab
- **Issue:** The description that appears at the top (navy blue sections) sits outside the tab structure
- **Want:** Move it inside the "Overview" tab content
- **Category:** Enhancement (layout change)

### S2-05: Consolidate into Overview — remove Feeder Group Mobility, Career Progression, and Other Job Information tabs
- **Issue:** "Feeder Group Mobility & Career Progression" and "Other Job Information" are separate tabs with limited content
- **Want:**
  - Move all content from "Feeder Group Mobility & Career Progression" into Overview
  - Move all content from "Other Job Information" into Overview
  - Remove both tabs entirely
- **Category:** Enhancement (tab restructure)

### S2-06: Repurpose "Style Selected" → OG-enrichment button
- **Issue:** "Style Selected" button doesn't do anything useful
- **Want:** Repurpose to enrich selected JD statements with Occupational Group attribute content:
  1. User selects NOC statements across tabs
  2. User clicks repurposed button
  3. System looks up NOC-to-OG mapping (from `bridge_noc_og` / `DIM_OCCUPATIONAL`) to identify candidate OGs — narrows the neighborhood (e.g., Database analysts → CS, IS — not PR, SR)
  4. System pulls statements from candidate OG attributes (qualification standards, evaluation standards, etc.)
  5. User sees OG-sourced statements with provenance tags (e.g., "from OG: CS - Computer Systems")
  6. User selects which to append to their existing JD statements
  7. Enriched JD has more detail aligned with OG classification language → better classification results
- **Provenance:** Every appended statement traces to a specific OG code + attribute
- **Dependencies:** Requires `dim_og_*` tables from JobForge (evaluation standards, qualification standards) + NOC-to-OG bridge mapping
- **Note:** NOC-to-OG pre-mapping eliminates the chicken-and-egg problem — system knows the OG neighborhood before classification runs
- **Architecture principle:** JobForge bridge tables provide **deterministic matching first** (SQL joins — fast, reliable, auditable), semantic matching (sentence-transformers, LLM) only fires for ambiguous cases within the narrowed neighborhood. This optimizes cost/latency and keeps provenance clean.
- **Category:** SEED — significant feature (bridges Step 2 and classification)

### S2-07: Show what the level circles represent (dimension type)
- **Issue:** Level circles (1-5) appear next to statements but user can't tell what they measure — is it Proficiency? Importance? Duration? Frequency? Complexity?
- **Want:** Display the dimension type alongside the level (e.g., "Proficiency: 4/5", "Importance: 3/5", "Frequency: 5/5")
- **Source:** guide.csv contains scale definitions per category — Skills=Proficiency, Abilities=Proficiency, Knowledge=Knowledge Level, Work Activities=Complexity, Personal Attributes=Importance, Work Context=varies (Frequency, Duration, Degree of responsibility, etc.)
- **Note:** This data also needs to be in JobForge gold — see `.planning/JOBFORGE-DATA-REQUIREMENTS.md`
- **Category:** Enhancement

---

## Step 3: JD Preview

### S3-01: Remove per-statement provenance from JD body
- **Issue:** Each statement in the preview shows "Source: Main Duties" etc. — makes the JD look like a data dump, not a real work description
- **Want:** JD body should look like the example work descriptions (DND, JC, etc.) — clean text, no source labels. Provenance stays in Appendix A.
- **Category:** Quick fix
- **Status:** FIXED in-session (removed source span from jd_preview.html)

### S3-02: Proficiency circles need scale meaning labels
- **Issue:** Circles show "L4" — meaningless without knowing what the scale measures
- **Want:** Show the full label from guide.csv (e.g., "4 - High Level", "3 - Moderate Complexity") — reuse what the manager already saw during selection
- **Category:** Quick fix
- **Status:** FIXED in-session (template now renders proficiency.label)

### S3-03: Appendix A headers — reference DADM directive properly
- **Issue:** Section headers say "(Directive 6.2.3)" — generic, not actionable
- **Want:** "(Evidence of compliance with DADM Directive X.X.X)" with "DADM Directive X.X.X" hyperlinked to the actual TBS directive page
- **Category:** Quick fix
- **Status:** FIXED in-session (template constructs hyperlink from section_id)

### S3-04: Appendix A intro paragraph — update attribution
- **Issue:** Says "This job description was created in compliance with the Treasury Board of Canada's Directive on Automated Decision-Making"
- **Want:** "Created using JobForge Work Descriptions. Content selections made by Section 34 Authorized manager using authoritative sources compliant with ESDC NOC 2025v.1 and O*NET Standards, the Directive on Classification, and DADM Directive." — with both directives hyperlinked
- **Category:** Quick fix
- **Status:** FIXED in-session (template + export_service.py updated)

### S3-05: "Back to Edit" returns to search screen instead of profile/edit
- **Issue:** Clicking "Back to Edit" on the preview reloads the page, which drops the user back to the search screen (Step 1) instead of the profile editing view (Step 2)
- **Want:** Return to the profile page with all selections preserved — user should land back where they were building the JD
- **Category:** Bug

### S3-06: Preview screen needs Classify (Step 5) as a navigation option
- **Issue:** From the preview screen, user can only Export or "Back to Edit" — no way to proceed to classification
- **Want:** Three actions available from preview:
  1. **Export** (PDF/DOCX) — existing
  2. **Classify** (Step 5) — run occupational group allocation on the assembled JD
  3. **Return to Builder** (Step 3) — go back to profile/selection, not search
- **Note:** "Back to Edit" should be relabeled "Return to Builder" and fixed per S3-05
- **Category:** Enhancement

### S3-07: Export classification results from Step 5
- **Issue:** Classification results (occupational group recommendations, confidence scores, evidence) can only be viewed on-screen — no way to export them
- **Want:** User can export Step 5 classification results (recommendations, rationale, evidence, provenance) as part of the JD export or as a separate document
- **Category:** Enhancement

---

## Step 5: Classify (Occupational Group Allocation)

### S5-01: "Invalid Combination" should not be red / error-styled
- **Issue:** Classification returns "Invalid Combination" displayed as a red error card — makes it look like something broke or the user did something wrong
- **Want:** Reframe as a **coaching moment**, not an error. This is where the manager learns how to improve their JD:
  - Neutral/informational styling (blue or amber, not red)
  - Explain WHY the combination is invalid
  - Suggest what to adjust (which statements conflict, what's missing)
  - Provide a "Return to Builder" button so the manager can go back and refine
- **Category:** Enhancement (UX tone — error → guidance)

### S5-02: Return to Builder from classification results
- **Issue:** No way to go back to the profile/selection screen from classification results to make adjustments
- **Want:** "Return to Builder" button that takes the user back to Step 2/3 with selections preserved — informed by classification feedback, they can adjust statements
- **Relates to:** S3-05 (same "return to edit" navigation problem), S3-06 (preview navigation)
- **Category:** Enhancement

### S5-03: Style button should enable JD refinement informed by authoritative sources
- **Issue:** After seeing classification results, user has no way to enrich/adjust their JD using authoritative data to improve classification fit
- **Want:** The Style button (repurposed per S2-06) becomes a refinement tool informed by multiple authoritative sources under JobForge's hood:
  - **CAF Careers website data** — military occupation attributes
  - **Job Architecture** — job families, functions, managerial levels
  - **O*NET via API** — as second resort for international enrichment
  - **Other international job taxonomies** — cross-border harmonization
  - **WIQ data** — Work Information Questionnaire standards
  - **OG evaluation/qualification standards** — from `dim_og_*` tables
- **Architecture:** These sources feed a **RAG model** — retrieval-augmented generation where the LLM draws from authoritative indexed sources to suggest JD improvements
- **Category:** SEED — significant (RAG infrastructure + multi-source integration)

### S5-04: Classification speed — slow due to live internet scraping + full semantic search
- **Issue:** "Analysing job description..." takes noticeably long — runs semantic matching against all 426 OG groups over the internet
- **Root cause:** No deterministic pre-filtering. Every classification runs full semantic matching without narrowing the neighborhood first.
- **Want:** Deterministic-first architecture (per S1-10 / S2-06 theme):
  1. Bridge table join (NOC → OG) narrows to candidate OGs instantly (SQL, milliseconds)
  2. Semantic matching only fires for ambiguous cases within the narrowed neighborhood
  3. Result: faster classification, lower API cost, cleaner provenance
- **Note:** Prime example of the gains from moving to JobForge gold model. Most noticeable performance improvement users will see.
- **Category:** SEED — blocked by S1-10 (JobForge gold integration)

### S5-05: NOC → OG cross-reference display in classify results
- **Issue:** Classification results show OG recommendations but don't show which NOC groups informed the cross-reference
- **Want:** Classify results should display the NOC groups used in cross-referencing with OG attributes — user sees the bridge logic (e.g., "NOC 21232 → CS, IS" per `bridge_noc_og`)
- **Relates to:** S2-06 (NOC → OG neighborhood narrowing), S5-04 (deterministic bridge table joins)
- **Dependency:** Requires S1-10 (JobForge bridge tables)
- **Category:** Enhancement — blocked by S1-10

### S5-06: Bubble matrix report for classification results
- **Issue:** Classification results display as flat recommendation cards — no visual way to compare the 3 recommendations across multiple quality dimensions simultaneously
- **Want:** A **bubble matrix chart** (heat map style) showing the top 3 OG recommendations as positioned bubbles:
  - **X-axis:** Similarity between JD content and OG definition (existing `semantic_similarity` score)
  - **Y-axis:** Provenance score — traceability quality (low = bottom, high = top). Measures how well-sourced and auditable the supporting data is.
  - **Bubble size:** Definition Fit — how well the JD holistically fits the OG definition (existing `definition_fit` from LLM assessment, 0.0-1.0)
  - **Bubble color:** Green → Red gradient based on **NOC data granularity** from JobForge 2.0 semantic model:
    - **Level 5** (Unit Group) = most granular / greenest — authoritative, direct match
    - **Level 6** (Label) = moderate granularity
    - **Level 7** (Example Title) = least granular / reddest — weakest authoritative basis
  - **Bubble label:** OG code + name (e.g., "CS - Computer Systems")
- **Visual logic:** Ideal recommendation = large green bubble in upper-right (high similarity, high provenance, strong definition fit, granular authoritative source). Red small bubble in lower-left = weak candidate.
- **Relates to:** S1-03 (NOC hierarchy granularity levels 5/6/7)
- **Dependency:** Requires S1-10 (JobForge gold for granularity data)
- **Category:** SEED — significant (new visualization component + data dimensions)

### S5-07: Authoritative source mix description per bubble
- **Issue:** Classification results don't reveal which authoritative taxonomies contributed to the JD statements that drove each recommendation
- **Want:** Each bubble in the matrix report (S5-06) includes a **description panel** showing the "authoritative source mix" — a breakdown of which taxonomies were used to create the statements in the JD builder via the Stylize button:
  - e.g., "NOC 2025v1: 60%, OG Standards: 20%, O*NET: 15%, CAF: 5%"
  - Shows the composition of authoritative sources behind the JD content that drove this particular OG recommendation
  - Makes the provenance Y-axis concrete — high provenance = diverse, authoritative source mix; low provenance = single-source or unverified
- **Relates to:** S5-03 (RAG from authoritative sources via Stylize), S2-06 (Stylize → OG enrichment)
- **Category:** SEED — requires multi-source tracking in Stylize pipeline

### S5-09: Normalized taxonomy comparison grid — DADM automated decision evidence
- **Issue:** The bubble matrix (S5-06) gives a visual summary but doesn't show the actual evidence basis for the classification recommendation. There's no transparent, auditable comparison of what each authoritative source says about the same data elements.
- **Core concept:** A **normalized comparison table** where all taxonomies are compared using the same data elements. This is the proof of concept for DADM-compliant automated decision-making — the system transparently shows HOW and WHY it recommended a classification, broken down by authoritative source and normalized data dimension.
- **Want:** A **heatmapped grid view** per OG recommendation (one grid per bubble):
  - **Rows:** Normalized data elements common across taxonomies — Description, Skills, Abilities, Knowledge, Work Activities, Competencies, Qualifications, etc. — whatever can be normalized to the OG as a reference point to justify the match confidence
  - **Columns:** One column per taxonomy selected by the user (via S5-08) — e.g., OG Standards, NOC, CAF, O*NET, WIQ, Job Architecture
  - **Baseline column (OG):** The OG definition's version of each data element (far left, highlighted) — this is the reference point. Every other column is compared against this baseline.
  - **Cell content:** The **actual words/text** from each taxonomy's version of that data element — not scores. User reads real authoritative content:
    - e.g., Row "Skills" / Column "NOC" → the actual skill statements from the NOC profile
    - e.g., Row "Description" / Column "O*NET" → O*NET's occupation summary text
    - e.g., Row "Qualifications" / Column "OG Standards" → the OG qualification standard text
    - Empty cells where a taxonomy doesn't have that data element
  - **Cell heatmap overlay:** Background color encodes alignment quality using bubble chart measures:
    - Similarity to OG baseline (from X-axis) — how closely this taxonomy's text matches the OG reference
    - Provenance quality (from Y-axis) — traceability/auditability of this data
    - Granularity level (from bubble color) — green→red per NOC data level 5/6/7
  - **Far-right column:** "Horizontal Score" — aggregate across all taxonomy columns for each data element row. Answers: "How consistently do all authoritative sources describe this data element for this OG?"
  - **Bottom row:** Column totals — aggregate down each taxonomy column. Answers: "How complete and aligned is this taxonomy overall for this OG recommendation?"
- **DADM compliance significance:** This grid IS the automated decision evidence artifact. It demonstrates:
  1. **Transparency** — user sees exactly what data from which sources drove the recommendation
  2. **Accountability** — every cell traces to a specific authoritative source and data element
  3. **Justification** — the horizontal/vertical scores quantify how well-supported the recommendation is across multiple independent authorities
  4. **Human oversight** — manager reads actual content and can challenge or accept the recommendation with full visibility
  - This is a **HUGE proof of concept** for DADM-compliant automated classification — the system doesn't just say "CS at 85% confidence." It shows: "Here's what NOC says about skills for CS, here's what O*NET says, here's what the OG standard says — and here's how they all compare. You decide."
- **Visual logic:** Reading across a row = "What do all my selected authorities say about [Skills] for this OG?" Reading down a column = "How complete is [NOC]'s coverage of this OG?" Green cells = strong alignment with OG baseline. Red/pale = weak or missing. Empty = taxonomy doesn't cover this element.
- **Interaction:** Grid and bubble chart are linked views — each grid corresponds to one bubble. Selecting a bubble opens its detailed grid. Horizontal score feeds back into the bubble chart's provenance Y-axis.
- **Relates to:** S5-06 (bubble matrix — summary view), S5-07 (source mix — grid is the full breakdown), S5-08 (taxonomy selection determines columns)
- **Category:** SEED — significant (DADM proof of concept, normalized multi-taxonomy comparison)

### S5-10: Composite scoring hierarchy — performance measurement house of cards on gold provenance
- **Issue:** The classification confidence score (e.g., "CS at 85%") is a single opaque number. There's no visible hierarchy showing how that number was built, what it depends on, or where it breaks if the underlying data is weak.
- **Core concept:** The classification score is a **composite index** built from a hierarchy of measures — like a performance measurement framework where each layer rolls up from the one below. Every layer MUST have **gold provenance** or the entire structure above it is unreliable. It's a "house of cards" — the top-level score is only as trustworthy as the weakest provenance link in the chain.
- **Scoring hierarchy (bottom → top):**
  1. **Data Points** (foundation) — the actual words/text in each grid cell from each taxonomy. Raw authoritative content. Each must have gold provenance: verified source, extraction timestamp, archive path, content hash.
  2. **Performance Indicators** — individual cell-level scores in the S5-09 grid. How well does this taxonomy's text for this data element align with the OG baseline? Computed from semantic similarity, exact match ratio, term overlap. Only valid if the underlying data point has gold provenance.
  3. **KPIs** — aggregated measures:
     - **Horizontal Score** (per row) — how consistently do all taxonomies describe this data element for this OG? Rolls up from cell-level performance indicators across a row.
     - **Column Total** (per taxonomy) — how complete and aligned is this taxonomy overall? Rolls up from cell-level performance indicators down a column.
  4. **Indices** — the bubble chart dimensions, each an index built from KPIs:
     - **X-axis (Similarity Index)** — aggregated JD ↔ OG alignment across all data elements
     - **Y-axis (Provenance Index)** — aggregated traceability quality across all sources used
     - **Bubble size (Definition Fit Index)** — holistic fit assessment informed by all KPIs
     - **Bubble color (Granularity Index)** — weighted NOC hierarchy level across matched data
  5. **Composite Index = THE DECISION** — this IS the automated decision. Not a "confidence score" — it's the classification recommendation itself. The composite index, built from all layers below, is what the system is recommending to the manager. The manager then exercises human oversight by drilling into the hierarchy to validate or override. This is what DADM regulates — and every layer beneath it is the auditable justification chain.
- **Gold provenance requirement:** Every data point at the foundation MUST have verified provenance:
  - Source authority (NOC 2025v1, O*NET 29.0, TBS Classification Policy, etc.)
  - Extraction method (ETL from gold parquet, API call, scrape with archive)
  - Timestamp (when extracted)
  - Content hash (integrity verification)
  - Archive path (reproducibility)
  - If ANY data point in the chain lacks gold provenance, it's flagged — and every measure above it that depends on it is marked as degraded. The house of cards visually shows where it's weak.
- **Drill-down UX:** User sees composite score → clicks to see indices (bubble chart) → clicks bubble to see KPIs (grid horizontal/column scores) → clicks cell to see performance indicator (alignment detail) → clicks to see raw data point with full provenance metadata
- **Visual indicator:** Provenance chain health — green chain icon = all gold, amber = some gaps, red = critical gaps. Appears at every level of the hierarchy.
- **Relates to:** S5-09 (grid provides the KPI and data point layers), S5-06 (bubble chart provides the index layer), S5-07 (source mix feeds the provenance index)
- **Category:** SEED — architectural (measurement framework design, provenance chain validation)

### S5-11: PuMP results map — formalize the scoring hierarchy as a theory of change
- **Issue:** The scoring hierarchy (S5-10) looks like a measurement framework, but it's informal. There's no validated logic model proving that the data points actually lead to the decision through legitimate causal links. Without this, the hierarchy is just an assertion — not an auditable theory of change.
- **Core concept:** The S5-10 scoring hierarchy IS a **PuMP results map** (logic model / theory of change). It needs to be formalized using PuMP methodology to establish legitimacy:
  - **Inputs:** Data points and authoritative sources (NOC, O*NET, CAF, OG Standards, etc.) — each with gold provenance
  - **Activities:** Normalization, semantic comparison, alignment scoring, aggregation — the processing steps that transform inputs into measures
  - **Outputs:** Performance indicators, KPIs, indices — the measurable artifacts at each layer
  - **Outcomes:** Defined using **TBS policy language with provenance** — traced to specific directive sections:
    - Intermediate outcomes tied to DADM transparency/accountability requirements
    - Ultimate outcome = the official TBS term for "the job description has been mapped to an occupational group" (the classification decision)
  - **Measures designed bottom-up:** Data Points → Performance Indicators → KPIs → Indices → Composite Indicator (= ultimate outcome / the decision)
- **PuMP steps to complete:**
  1. **Define Results** — articulate each outcome using official TBS Classification Policy and DADM Directive language, with paragraph-level provenance to the authoritative source
  2. **Design Measures** — map the S5-10 hierarchy layers to PuMP measure types: data → indicators → KPIs → indices → composite indicator. Each measure has a clear operational definition, data source, and provenance chain.
  3. **Build Results Map** — connect inputs → activities → outputs → outcomes in a validated logic model showing the causal chain from raw authoritative data to classification decision
- **Why this matters:** This turns the classification feature from "an AI that recommends an OG" into "a formally validated measurement system with auditable causal logic, where the decision is the measurable outcome of a provenance-backed theory of change." That's the DADM proof of concept.
- **Relates to:** S5-10 (scoring hierarchy = the raw logic model), S5-09 (grid = the evidence layer), S5-06 (bubble chart = the index layer)
- **Category:** SEED — architectural (measurement framework formalization via PuMP)

### S5-08: Right-click authoritative source selection on bubbles
- **Issue:** User has no control over which authoritative sources feed the Stylize/Enrich button
- **Want:** User can **right-click a bubble** in the matrix report and make their "authoritative source selection" — choosing which taxonomies the Stylize button should draw from for enrichment:
  - Context menu lists available sources: NOC, OG Standards, CAF, O*NET, WIQ, Job Architecture, etc.
  - User checks/unchecks sources per their preference
  - Selected sources become the retrieval corpus for the RAG model when Stylize is next used
  - This gives managers control over the provenance composition of their JD — they decide which authorities matter for their context
- **UX flow:** View bubble matrix → right-click a recommendation bubble → select authoritative sources → return to builder → Stylize now uses those sources → re-classify to see updated bubble positions
- **Relates to:** S5-03 (RAG architecture), S5-06 (bubble matrix), S5-07 (source mix)
- **Category:** SEED — significant (user-controlled RAG source selection)

---
