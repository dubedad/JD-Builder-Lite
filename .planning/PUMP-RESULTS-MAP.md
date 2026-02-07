# PuMP Results Map: Classification Decision System

**Methodology:** Stacey Barr's PuMP (Performance Measurement Process)
**Applied to:** JD Builder Lite — Occupational Group Allocation
**PuMP Steps Covered:** Step 2 (Mapping Measurable Results) + Step 3 (Designing Meaningful Measures)
**Date:** 2026-02-06

---

## Results Map (Theory of Change)

This results map formalizes the causal chain from raw authoritative data to classification decision. Every outcome is defined using TBS policy language with paragraph-level provenance.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ULTIMATE OUTCOME (THE DECISION)                  │
│                                                                     │
│  "Allocate the position to an occupational group"                   │
│   — Guide to Allocating Positions, Step 2                           │
│                                                                     │
│  Composite Indicator: Occupational Group Allocation Recommendation  │
│  Official status: Classification decision (Directive 28700, B.2.2.4)│
└────────────────────────────┬────────────────────────────────────────┘
                             │
            ┌────────────────┼────────────────┐
            │                │                │
            ▼                ▼                ▼
┌───────────────────┐ ┌──────────────┐ ┌──────────────────────┐
│ INTERMEDIATE      │ │ INTERMEDIATE │ │ INTERMEDIATE          │
│ OUTCOME 1         │ │ OUTCOME 2    │ │ OUTCOME 3             │
│                   │ │              │ │                        │
│ "Classification   │ │ "Decisions   │ │ "Meaningful            │
│  decisions are    │ │  are data-   │ │  explanation to        │
│  sound"           │ │  driven and  │ │  clients of how and    │
│                   │ │  responsible"│ │  why the decision      │
│ Directive 28700   │ │              │ │  was made"             │
│ Section 3.2.2     │ │ DADM 32592   │ │                        │
│                   │ │ Section 4.2.1│ │ DADM 32592             │
│ Index: Definition │ │              │ │ Section 6.2.3          │
│ Fit + Similarity  │ │ Index:       │ │                        │
│                   │ │ Provenance + │ │ Index: Granularity     │
│                   │ │ Granularity  │ │ + Evidence Grid        │
└────────┬──────────┘ └──────┬───────┘ └───────────┬────────────┘
         │                   │                      │
         └───────────┬───────┘                      │
                     │                              │
         ┌───────────▼──────────────────────────────▼──────────┐
         │                 ENABLING OUTCOMES                     │
         │                                                      │
         │  EO-1: "Primary purpose of the work is determined    │
         │         through the review of the work description"  │
         │         — Guide to Allocating Positions, Step 1      │
         │         KPI: Element Consensus Score (horizontal)    │
         │                                                      │
         │  EO-2: "All occupational group allocations should    │
         │         be made primarily with the definition        │
         │         statement in mind"                           │
         │         — Guide to Allocating Positions              │
         │         KPI: Definition-Statement Alignment Score    │
         │                                                      │
         │  EO-3: "Evaluate the work, not the person"           │
         │         — Guide to Allocating Positions              │
         │         KPI: Content Objectivity Score               │
         │                                                      │
         │  EO-4: "Information is traceable, protected and      │
         │         accessed appropriately"                      │
         │         — DADM 32592, Section 6.3.6                  │
         │         KPI: Taxonomy Coverage Score (column total)  │
         └────────────────────┬─────────────────────────────────┘
                              │
         ┌────────────────────▼─────────────────────────────────┐
         │                    OUTPUTS                            │
         │                                                      │
         │  O-1: Normalized taxonomy comparison grid populated  │
         │       (S5-09 evidence artifact)                      │
         │       Performance Indicator: Taxonomy-Element        │
         │       Alignment Score (per cell)                     │
         │                                                      │
         │  O-2: Bubble matrix visualization rendered           │
         │       (S5-06 summary artifact)                       │
         │       Performance Indicator: Index values computed   │
         │                                                      │
         │  O-3: Provenance chain validated                     │
         │       Performance Indicator: Source Data             │
         │       Completeness Rate + Verification Score         │
         └────────────────────┬─────────────────────────────────┘
                              │
         ┌────────────────────▼─────────────────────────────────┐
         │                   ACTIVITIES                          │
         │                                                      │
         │  A-1: Extract source data with gold provenance       │
         │       (ETL from gold parquet, API, scrape+archive)   │
         │                                                      │
         │  A-2: Normalize data elements across taxonomies      │
         │       (map to common dimensions: Description,        │
         │        Skills, Abilities, Knowledge, Quals, etc.)    │
         │                                                      │
         │  A-3: Compare each taxonomy element against OG       │
         │       baseline (semantic similarity + term overlap)  │
         │                                                      │
         │  A-4: Aggregate cell scores → row/column KPIs        │
         │       → indices → composite indicator                │
         │                                                      │
         │  A-5: Present evidence for human oversight            │
         │       "The final decision must be made by a human"   │
         │       — DADM 32592, Appendix C (Level III-IV)        │
         └────────────────────┬─────────────────────────────────┘
                              │
         ┌────────────────────▼─────────────────────────────────┐
         │                    INPUTS                             │
         │                                                      │
         │  I-1: Job description content                        │
         │       "Written concisely in bias-free plain          │
         │        language, contain all significant aspects     │
         │        of the work"                                  │
         │       — Directive 28700, Section B.2.2.1             │
         │                                                      │
         │  I-2: Occupational group definitions                 │
         │       "Describes in general terms the type of work   │
         │        allocated to the occupational group"          │
         │       — Guide to Allocating Positions                │
         │                                                      │
         │  I-3: Inclusion & exclusion statements               │
         │       "Provide examples of the types of work that    │
         │        are included in or excluded from the          │
         │        occupational group"                           │
         │       — Guide to Allocating Positions                │
         │                                                      │
         │  I-4: Authoritative taxonomy sources                 │
         │       NOC 2025v1 | O*NET | CAF | OG Standards |     │
         │       WIQ | Job Architecture                         │
         │       Each with gold provenance:                     │
         │       source, timestamp, hash, archive path          │
         │                                                      │
         │  I-5: Table of Concordance                           │
         │       "Links the sub-group definitions to the 1999   │
         │        occupational group definitions and the        │
         │        appropriate job evaluation standard"          │
         │       — Guide to Allocating Positions                │
         │       Published Canada Gazette, July 17, 2004        │
         └──────────────────────────────────────────────────────┘
```

---

## Measure Design (PuMP Step 3)

### Hierarchy: Data Point → Indicator → KPI → Index → Composite Indicator

Each measure follows PuMP's 5-step evidence-based design: result → evidence → quantification → evaluation → selection.

---

### LAYER 1: Data Points (Foundation)

**What we observe:** Raw authoritative text in each grid cell.

#### M1.1: Source Data Completeness Rate

| Element | Specification |
|---------|---------------|
| **Result measured** | I-4: Authoritative taxonomy sources are available and extracted |
| **Evidence of result** | Grid cells contain actual text from each taxonomy for each data element |
| **Operational definition** | % of grid cells (taxonomy x data element combinations) that contain extracted text, out of all possible cells for selected taxonomies |
| **Formula** | `(cells with content / total possible cells) x 100` |
| **Data source** | Normalized comparison grid (S5-09) |
| **Provenance chain** | Each cell traces to: source taxonomy → ETL pipeline → gold parquet table → extraction timestamp → content hash |
| **Frequency** | Per classification run |
| **Owner** | System (automated) |

#### M1.2: Provenance Verification Score

| Element | Specification |
|---------|---------------|
| **Result measured** | EO-4: "Information is traceable, protected and accessed appropriately" (DADM 6.3.6) |
| **Evidence of result** | Every data point has verified gold provenance metadata |
| **Operational definition** | % of data points with complete provenance chain: source authority + extraction method + timestamp + content hash + archive path. All 5 elements required for "gold." |
| **Formula** | `(data points with 5/5 provenance elements / total data points) x 100` |
| **Data source** | `scrape_provenance` table, ETL metadata, archive filesystem |
| **Provenance chain** | Self-referential — this measure validates the provenance system itself |
| **Frequency** | Per classification run |
| **Signal rule** | < 100% triggers amber warning on all dependent measures; < 80% triggers red degradation cascade |

---

### LAYER 2: Performance Indicators (Cell Level)

**What we observe:** How well each taxonomy's text aligns with the OG baseline for a specific data element.

#### M2.1: Taxonomy-Element Alignment Score

| Element | Specification |
|---------|---------------|
| **Result measured** | O-1: Normalized comparison grid populated with meaningful alignment data |
| **Evidence of result** | Each cell's text is semantically compared to the OG baseline cell in the same row |
| **Operational definition** | Semantic similarity (0.0-1.0) between the taxonomy's text for data element X and the OG definition's text for data element X. Computed via sentence-transformer embedding cosine similarity + term overlap ratio. |
| **Formula** | `(0.7 x cosine_similarity) + (0.3 x term_overlap_ratio)` |
| **Data source** | Cell text from each taxonomy column vs. OG baseline column, per row |
| **Provenance chain** | Cell text → M1.2 (provenance verified?) → embedding model version → similarity computation |
| **Frequency** | Per cell, per classification run |
| **Degradation** | If M1.2 < gold for this cell's data point, alignment score is flagged as "unverified" |

#### M2.2: Granularity Level Indicator

| Element | Specification |
|---------|---------------|
| **Result measured** | IO-2: "Decisions are data-driven and responsible" — data quality dimension |
| **Evidence of result** | The NOC hierarchy level at which the match was found |
| **Operational definition** | JobForge 2.0 semantic model level of the NOC data that matched: Level 5 (Unit Group) = most authoritative, Level 6 (Label) = moderate, Level 7 (Example Title) = least authoritative |
| **Data source** | JobForge gold `dim_noc` hierarchy + match location tracking |
| **Encoding** | Level 5 → green (1.0), Level 6 → amber (0.6), Level 7 → red (0.3) |
| **Provenance chain** | NOC match → hierarchy level → JobForge `dim_noc` table → ETL timestamp |

---

### LAYER 3: KPIs (Row/Column Aggregates)

**What we observe:** Patterns across the grid — consistency and coverage.

#### M3.1: Element Consensus Score (Horizontal — per row)

| Element | Specification |
|---------|---------------|
| **Result measured** | EO-1: "Primary purpose of the work is determined" — consensus across sources |
| **Evidence of result** | All selected authoritative sources describe this data element consistently for this OG |
| **Operational definition** | Weighted average of M2.1 alignment scores across all taxonomy columns for one data element row. Weighted by M1.2 provenance quality of each source. |
| **Formula** | `Σ(M2.1_cell × M1.2_weight) / Σ(M1.2_weight)` for all cells in row |
| **Interpretation** | High (>0.7): Strong consensus — all authorities agree on this element. Low (<0.4): Weak — sources disagree or coverage is sparse. |
| **Data source** | Row of M2.1 scores from normalized grid |
| **Provenance chain** | M2.1 cells → M1.2 weights → aggregation formula → row score |

#### M3.2: Taxonomy Coverage Score (Vertical — per column)

| Element | Specification |
|---------|---------------|
| **Result measured** | EO-4: Traceability — how complete is this authority's contribution? |
| **Evidence of result** | This taxonomy provides data across all relevant data elements |
| **Operational definition** | Weighted average of M2.1 alignment scores down one taxonomy column, weighted by element importance (Description > Skills > Abilities > Knowledge > Quals). Missing cells score 0. |
| **Formula** | `Σ(M2.1_cell × element_weight) / Σ(element_weight)` for all rows in column |
| **Interpretation** | High (>0.7): Comprehensive authority — covers most elements with strong alignment. Low (<0.4): Thin authority — sparse or weak coverage. |
| **Data source** | Column of M2.1 scores from normalized grid |

#### M3.3: Definition-Statement Alignment Score

| Element | Specification |
|---------|---------------|
| **Result measured** | EO-2: "All occupational group allocations should be made primarily with the definition statement in mind" |
| **Evidence of result** | The JD's primary purpose aligns with the OG's definition statement specifically (not just inclusions) |
| **Operational definition** | Semantic similarity between the JD's key activities + client-service results and the OG definition statement text, independent of inclusion/exclusion matching. This is the single most important measure — TBS explicitly says definition > inclusions. |
| **Formula** | `cosine_similarity(JD_primary_purpose_embedding, OG_definition_embedding)` |
| **Data source** | JD content (key activities, CSR) vs. `dim_occupational_group.definition` |
| **Provenance chain** | JD selections (manager provenance) → OG definition (TBS provenance, `scrape_provenance` table) |

---

### LAYER 4: Indices (Bubble Chart Dimensions)

**What we observe:** Multi-dimensional quality assessment per OG recommendation.

#### M4.1: Similarity Index (X-axis)

| Element | Specification |
|---------|---------------|
| **Result measured** | IO-1: "Classification decisions are sound" — fit dimension |
| **Evidence of result** | The JD content aligns with the OG definition across multiple data elements |
| **Operational definition** | Weighted composite of M3.1 element consensus scores (all rows) + M3.3 definition-statement alignment. Definition alignment weighted 60% (per TBS guidance "primarily with the definition statement in mind"). |
| **Formula** | `(0.6 × M3.3) + (0.4 × mean(M3.1_all_rows))` |
| **Range** | 0.0 (no similarity) → 1.0 (perfect alignment) |
| **Provenance chain** | M3.1 row scores + M3.3 definition score → weighted aggregation |
| **Policy basis** | Guide to Allocating Positions: "primary purpose" + definition-first allocation |

#### M4.2: Provenance Index (Y-axis)

| Element | Specification |
|---------|---------------|
| **Result measured** | IO-2: "Decisions are data-driven and responsible" + EO-4: "traceable" |
| **Evidence of result** | The evidence base is well-sourced from multiple verified authorities |
| **Operational definition** | Composite of: M1.2 provenance verification score (40%) + mean M3.2 taxonomy coverage scores across all selected sources (40%) + source diversity factor (20%, rewarding more independent authorities). |
| **Formula** | `(0.4 × M1.2) + (0.4 × mean(M3.2_all_columns)) + (0.2 × source_diversity)` |
| **Source diversity** | `min(1.0, selected_taxonomies / 4)` — caps at 4 independent sources |
| **Range** | 0.0 (no provenance) → 1.0 (fully verified, diverse, comprehensive) |
| **Provenance chain** | M1.2 + M3.2 column scores + taxonomy count → weighted aggregation |
| **Policy basis** | DADM 6.3.6: traceability; DADM 4.2.1: data-driven |

#### M4.3: Definition Fit Index (Bubble Size)

| Element | Specification |
|---------|---------------|
| **Result measured** | EO-2: "Allocations made primarily with the definition statement in mind" |
| **Evidence of result** | Holistic assessment of how well the JD fits the OG definition |
| **Operational definition** | LLM-assessed holistic fit (0.0-1.0) between JD content and OG definition, informed by all KPI-layer scores as context. The LLM sees the normalized grid and scores, then provides a holistic "best fit" assessment. |
| **Formula** | `LLM_assessment(JD, OG_definition, grid_context)` |
| **Range** | 0.0 → 1.0 |
| **Provenance chain** | JD + OG definition + grid KPIs → LLM (model version, timestamp) → assessment |
| **Policy basis** | Guide to Allocating Positions: "best fit" determination for overlapping definitions |

#### M4.4: Granularity Index (Bubble Color)

| Element | Specification |
|---------|---------------|
| **Result measured** | IO-3: "Meaningful explanation of how and why the decision was made" — evidence quality |
| **Evidence of result** | The classification is based on granular, authoritative NOC data (not thin example title matches) |
| **Operational definition** | Weighted average of M2.2 granularity level indicators across all matched data points. Higher = match found at more authoritative NOC hierarchy levels. |
| **Formula** | `mean(M2.2_all_matched_cells)` |
| **Encoding** | ≥ 0.8 → green (authoritative), 0.5-0.8 → amber (moderate), < 0.5 → red (thin) |
| **Provenance chain** | M2.2 cell-level granularity → mean aggregation |

---

### LAYER 5: Composite Indicator = THE DECISION

#### M5.1: Occupational Group Allocation Recommendation

| Element | Specification |
|---------|---------------|
| **Result measured** | ULTIMATE OUTCOME: "Allocate the position to an occupational group" (Guide to Allocating Positions, Step 2) |
| **Official status** | Classification decision (Directive 28700, B.2.2.4) |
| **Evidence of result** | The system recommends an OG allocation supported by a fully auditable measurement hierarchy |
| **Operational definition** | The composite indicator is the recommendation itself — "Position [X] is recommended for allocation to Occupational Group [OG Code]." This is NOT a confidence percentage. It is THE DECISION — the automated recommendation that the manager validates or overrides per DADM Appendix C (Level III-IV): "The final decision must be made by a human." |
| **Formula** | `rank(M4.1 × 0.35 + M4.2 × 0.25 + M4.3 × 0.30 + M4.4 × 0.10)` — top-ranked OG is the primary recommendation |
| **Weight rationale** | Similarity (35%) + Definition Fit (30%) = 65% aligns with TBS "primarily with the definition statement in mind." Provenance (25%) ensures data-driven responsibility per DADM 4.2.1. Granularity (10%) rewards authoritative depth. |
| **Decision output** | OG code, OG name, composite score, + full drill-down chain: M4 indices → M3 KPIs → M2 indicators → M1 data points with provenance |
| **DADM compliance** | The recommendation satisfies: |
| | - **Transparency** (6.2.3): Full grid with actual text shows how/why |
| | - **Accountability** (6.2.7): Every cell traces to authoritative source |
| | - **Human oversight** (Appendix C): Manager sees evidence, validates/overrides |
| | - **Traceability** (6.3.6): Gold provenance on every data point |
| | - **Data-driven** (4.2.1): Multi-source normalized comparison |
| **Provenance chain** | M4 indices → M3 KPIs → M2 indicators → M1 data points → authoritative sources with gold provenance → TBS policy language defining the outcome |

---

## Provenance Chain Validation

The "house of cards" principle: if ANY layer's provenance breaks, everything above it is degraded.

```
COMPOSITE (M5.1) ─── depends on ──→ all M4 indices
  │                                    │
  │ If M4 degraded:                    │ If M3 degraded:
  │ Decision marked "low confidence"   │ Index marked "partially verified"
  │                                    │
  ▼                                    ▼
M4 Indices ─── depend on ──→ M3 KPIs
  │                            │
  │                            │ If M2 degraded:
  │                            │ KPI marked "unverified inputs"
  │                            │
  ▼                            ▼
M3 KPIs ─── depend on ──→ M2 Performance Indicators
  │                          │
  │                          │ If M1 degraded:
  │                          │ Indicator flagged "no gold provenance"
  │                          │
  ▼                          ▼
M2 Indicators ─── depend on ──→ M1 Data Points
                                  │
                                  │ FOUNDATION
                                  │ Gold provenance required:
                                  │ ✓ Source authority
                                  │ ✓ Extraction method
                                  │ ✓ Timestamp
                                  │ ✓ Content hash
                                  │ ✓ Archive path
                                  │
                                  │ Missing ANY element:
                                  │ ⚠ Entire chain above degraded
```

### Visual Health Indicators

| Chain Status | Icon | Meaning |
|---|---|---|
| All gold | Green chain | Every data point has 5/5 provenance elements |
| Some gaps | Amber chain | 80-99% of data points have full provenance |
| Critical gaps | Red chain | < 80% gold provenance — decision reliability compromised |
| Broken | Red X | Missing source data or unverifiable provenance |

---

## Policy Provenance Index

Every outcome in this results map traces to an authoritative TBS source:

| Outcome | Policy Language | Source | Section |
|---------|----------------|--------|---------|
| Ultimate | "Allocate the position to an occupational group" | Guide to Allocating Positions | Step 2 |
| Ultimate | "Classification decision" | Directive on Classification (28700) | B.2.2.4 |
| IO-1 | "Classification decisions are sound" | Directive on Classification (28700) | 3.2.2 |
| IO-2 | "Decisions are data-driven and responsible" | DADM (32592) | 4.2.1 |
| IO-3 | "Meaningful explanation of how and why the decision was made" | DADM (32592) | 6.2.3 |
| EO-1 | "Primary purpose of the work is determined through the review of the work description" | Guide to Allocating Positions | Step 1 |
| EO-2 | "All occupational group allocations should be made primarily with the definition statement in mind" | Guide to Allocating Positions | Guidance |
| EO-3 | "Evaluate the work, not the person" | Guide to Allocating Positions | Guidance |
| EO-4 | "Information is traceable, protected and accessed appropriately" | DADM (32592) | 6.3.6 |
| Human oversight | "The final decision must be made by a human" | DADM (32592) | Appendix C, Level III-IV |
| JD quality | "Written concisely in bias-free plain language, contain all significant aspects of the work" | Directive on Classification (28700) | B.2.2.1 |
| Definitions | "Describes in general terms the type of work allocated to the occupational group" | Guide to Allocating Positions | Format |
| Inclusions | "Provide examples of the types of work that are included in or excluded from the occupational group" | Guide to Allocating Positions | Format |
| Best fit | Establish "best fit" by determining which group best reflects primary purpose | Guide to Allocating Positions | Decision logic |

---

## Sources

- [Directive on Classification (28700)](https://www.tbs-sct.canada.ca/pol/doc-eng.aspx?id=28700)
- [Directive on Automated Decision-Making (32592)](https://www.tbs-sct.canada.ca/pol/doc-eng.aspx?id=32592)
- [Guide to Allocating Positions Using Occupational Group Definitions](https://www.canada.ca/en/treasury-board-secretariat/services/collective-agreements/occupational-groups/guide-allocating-positions-using-occupational-group-definitions.html)

---
*Generated via PuMP methodology (Steps 2-3) applied to JD Builder Lite classification decision system*
