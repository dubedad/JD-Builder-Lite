# Requirements: JD Builder Lite v5.1

**Defined:** 2026-03-11
**Core Value:** Every piece of content in the JD can be traced to its authoritative source, with clear documentation of human decisions and AI involvement.

## v5.1 Requirements

Full UI redesign to match the JobForge reference prototype. Design reference: `.planning/ui-walkthrough-v5.1/`.

### Chrome (Global Layout)

- [x] **CHROME-01**: All pages render a Government of Canada identity header (maple leaf logo, bilingual org name, Français toggle — cosmetic only)
- [x] **CHROME-02**: All pages render a dark navy JobForge app bar with brand badge ("JD Builder 1.0"), truncated Session ID, Audit Trail badge with running count, and Reset button
- [x] **CHROME-03**: All pages render a row of coloured data source pills: 2021 NOC (grey), CAF Careers (green), OCHRO Job Architecture (orange), O*NET SOC (blue), OaSIS (purple) — each linking to its source homepage
- [x] **CHROME-04**: All pages render a 5-step process stepper (Search → Build → Classify → Generate → Export) with the current step highlighted
- [x] **CHROME-05**: All pages render a "Selections (N)" vertical tab on the right edge showing the current selection count
- [x] **CHROME-06**: All pages render a compliance framework paragraph in the page body above the footer
- [x] **CHROME-07**: All pages render a dark footer ("JobForge — JD Builder 1.0 | Full Audit Trail Provenance" left, Canada wordmark right) and O*NET attribution below
- [x] **CHROME-08**: Français toggle and "View Provenance Graph" button render as cosmetic-only UI elements (non-functional in v5.1)

### Search

- [x] **SRCH-01**: Search page displays "Find your Job" heading, subtitle, Match Quality legend (95-100% Title green / 85% Description blue / 75% Related grey), centered search input, and "Source: JobForge WiQ | All job taxonomies" link
- [x] **SRCH-02**: Search page shows magnifying glass empty-state with "Start typing to search across all job taxonomies" and compliance reminder text when no query is entered
- [x] **SRCH-03**: Search results render a left filter panel with 6 accordion sections (OCHRO Job Architecture, CAF Careers, 2021 NOC Broad→Major, 2021 NOC TEER, Occupational Groups, O*NET SOC), each showing available filters or "No results" state, with a "Clear All Filters" button and Match Confidence legend
- [x] **SRCH-04**: Search result cards display occupation icon, bold title, match badge pills (score % and source), "Also known as:" line with matched keywords highlighted, and description paragraph
- [x] **SRCH-05**: Results header shows "[N] results (filtered)", a "+ New Search" button, and "Published: [date] | Data Steward: ESDC" metadata line

### Build

- [ ] **BUILD-01**: Build page displays a dark navy occupation header card with gear icon, title, NOC code, lead statement paragraph, NOC version badge, Retrieved timestamp, Quality Verified badge, View Provenance Graph button (cosmetic), and × close button
- [ ] **BUILD-02**: Build tabs include icons and a blue-grey section description box (left border accent, ⓘ icon) below the tab row explaining what the tab contains
- [ ] **BUILD-03**: Overview tab displays: Position Title (text field), Lead Statement + Definition (two-column), Employment Requirements (bullet list), Typical Workplaces (pill tags)
- [ ] **BUILD-04**: Core Competencies tab items are individually selectable with checkboxes (previously read-only in v5.0)
- [ ] **BUILD-05**: Key Activities tab displays Main Duties and Work Activities as two distinct labelled lists with separate headings within the same tab
- [ ] **BUILD-06**: Abilities, Effort, and Responsibility tabs group items by level with coloured level badges (e.g. "Level 4 (4 items)", "Level 3 (15 items)")
- [ ] **BUILD-07**: All tabs with item-level data show an inline sub-description line below each item label
- [ ] **BUILD-08**: All selectable tabs show a "Select All (N)" checkbox, "N selected" count (right-aligned), and SOURCES badge(s) identifying the data source
- [ ] **BUILD-09**: Skills, Abilities, Knowledge, Effort, and Responsibility tabs retain the blue dot importance rating display from v5.0

### Navigation & Selection Persistence

- [ ] **NAV-01**: Every Build tab shows a 3-button bottom navigation bar: "← Back to Search" (left) | "Preview Job Description" (centre) | "Continue to Classification →" (right)
- [ ] **NAV-02**: Clicking "Back to Search" returns to the Search page and preserves all current selections
- [ ] **NAV-03**: Clicking a different occupation card in Search clears all prior selections; clicking the same card preserves them
- [ ] **NAV-04**: Classification page bottom shows "← Back to Edit" and "Continue to Generate →" buttons
- [ ] **NAV-05**: Generate page bottom shows "↺ Regenerate" and "Continue →" buttons

### Preview Modal

- [ ] **PREV-01**: "Preview Job Description" opens a modal displaying the assembled JD from all selected items, styled in v5.1 design language
- [ ] **PREV-02**: Preview modal header has a "Return to Builder" button; footer has "Advance to Classify", "Export PDF", and "Export Word" buttons

### Selections Drawer

- [ ] **SEL-01**: Clicking the "Selections (N)" right-edge tab opens an overlay panel titled "Selection Summary — Your selected JD elements" showing all selected items grouped by tab
- [ ] **SEL-02**: Each item in the Selections panel has a × button that deselects it and removes it from the panel
- [ ] **SEL-03**: Selections panel shows "Total Selected: N" count at the bottom and a red "Clear All" button

### Classification

- [x] **CLASS-01**: Classification page renders in v5.1 chrome with occupation header card, DADM Compliant (green) and Full Provenance (purple) badges, and TBS 3-step dark card (§4.1.1, §4.1.2, §4.1.3)
- [x] **CLASS-02**: Post-analysis result includes a Statement Alignment Comparison section with two columns (Your Selected Statements vs. OG Definition Statements) and an Overall Alignment Score
- [x] **CLASS-03**: Post-analysis result includes Key Evidence (green check bullets), Caveats (amber warning bullets), and Alternative Groups Considered
- [x] **CLASS-04**: Post-analysis result includes a Next Step instructions box with links to the relevant Job Evaluation Standard

### Generate

- [x] **GEN-01**: Generate page renders in v5.1 chrome with a "Generate AI Overview" card, "DADM Level 2" badge, "Human Review Required" badge, and a yellow DADM Compliance Notice warning box
- [x] **GEN-02**: Generate page includes an optional "Additional Context" textarea (placeholder: "Department-specific requirements, organizational context...")
- [x] **GEN-03**: "Generate with AI" button triggers OpenAI LLM generation of multi-paragraph Position Overview prose using the user's selected statements as context
- [x] **GEN-04**: Generated prose appears below the button with an "AI Generated" badge; a "↺ Regenerate" button allows re-generation

### Export

- [ ] **EXP-01**: Export page renders in v5.1 chrome with "Export with Full Provenance" title and a scrollable JD preview card showing title, NOC code, Classification result badge, and Overview text
- [ ] **EXP-02**: Export page displays three compliance summary cards: DAMA DMBOK (green), TBS Directives, Full Lineage (purple)
- [ ] **EXP-03**: Export page includes "Include provenance annex" and "Include audit trail" checkboxes
- [ ] **EXP-04**: "Download PDF — With embedded provenance" (red button) generates and downloads the restructured PDF
- [ ] **EXP-05**: "Download Word — With audit trail annex" (blue button) generates and downloads the restructured DOCX
- [ ] **EXP-06**: "Download Full Audit Trail (JSON)" (outline button) downloads a JSON file containing all session selections, provenance metadata, classification result, and AI-generated content

### PDF & DOCX Format

- [ ] **PDF-01**: PDF structured JD sections: Position Overview (AI prose), Key Duties and Responsibilities (with [Custom] source tags per item), Qualifications and Requirements (Skills / Abilities / Knowledge / Core Competencies sub-sections), Effort & Physical Demands, Responsibilities
- [ ] **PDF-02**: PDF "Data Provenance & Compliance" section with: Source Information (NOC code, data source, source authority, generated by, generation date), DAMA DMBOK Compliance, DADM Directive Compliance, and Directive on Classification Compliance
- [ ] **PDF-03**: PDF "Policy Provenance" section with Authoritative Data Sources table (Source / Data Steward / Publication / Times Removed columns), Degrees of Separation legend (0 Direct / 1 Crosswalked / 2+ Derived), and AI-Generated Content subsection
- [ ] **PDF-04**: PDF "Data Quality (DAMA DMBOK)" section listing Accuracy, Completeness, Consistency, and Timeliness
- [ ] **PDF-05**: Word export uses the same section structure as the new PDF (PDF-01 through PDF-04 equivalent content)

---

## Future Requirements

### v5.2+ Candidates

- MAIN-01/02: Main Duties from parquet (blocked on element_main_duties.parquet ETL — 8 rows / 3 profiles)
- ENH-01: Search result cards show which NOC attribute matched
- ENH-02: Search filtering by OCHRO Job Architecture taxonomy (requires data)
- ENH-03: NOC-to-OG pre-filtering using bridge_noc_og.parquet
- FRAN-01: Français toggle switches app to French-language content
- PROV-01: View Provenance Graph shows interactive provenance visualization

### v6.0+

- Classification Step 2: Job Evaluation Standards scoring
- Benchmark position comparison UI
- Manager consultation workflow

---

## Out of Scope (v5.1)

| Feature | Reason |
|---------|--------|
| Français content | Single-language demo; toggle is cosmetic only |
| View Provenance Graph | Complex visualization; button cosmetic only |
| O*NET SOC filter data | No O*NET parquet in current data layer |
| OCHRO Job Architecture filter data | No OCHRO parquet in current data layer |
| CAF Careers filter data | No CAF parquet in current data layer |
| "Bright Outlook" badge on search cards | No O*NET outlook data available |
| Classification Step 2 (Job Evaluation) | v6.0 scope |
| Real-time collaboration / multi-user | Demo is single-user |

---

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| CHROME-01 | Phase 26 | Complete |
| CHROME-02 | Phase 26 | Complete |
| CHROME-03 | Phase 26 | Complete |
| CHROME-04 | Phase 26 | Complete |
| CHROME-05 | Phase 26 | Complete |
| CHROME-06 | Phase 26 | Complete |
| CHROME-07 | Phase 26 | Complete |
| CHROME-08 | Phase 26 | Complete |
| SRCH-01 | Phase 26 | Complete |
| SRCH-02 | Phase 26 | Complete |
| SRCH-03 | Phase 26 | Complete |
| SRCH-04 | Phase 26 | Complete |
| SRCH-05 | Phase 26 | Complete |
| BUILD-01 | Phase 27 | Pending |
| BUILD-02 | Phase 27 | Pending |
| BUILD-03 | Phase 27 | Pending |
| BUILD-04 | Phase 27 | Pending |
| BUILD-05 | Phase 27 | Pending |
| BUILD-06 | Phase 27 | Pending |
| BUILD-07 | Phase 27 | Pending |
| BUILD-08 | Phase 27 | Pending |
| BUILD-09 | Phase 27 | Pending |
| NAV-01 | Phase 28 | Pending |
| NAV-02 | Phase 28 | Pending |
| NAV-03 | Phase 28 | Pending |
| NAV-04 | Phase 28 | Pending |
| NAV-05 | Phase 28 | Pending |
| PREV-01 | Phase 28 | Pending |
| PREV-02 | Phase 28 | Pending |
| SEL-01 | Phase 28 | Pending |
| SEL-02 | Phase 28 | Pending |
| SEL-03 | Phase 28 | Pending |
| CLASS-01 | Phase 29 | Complete |
| CLASS-02 | Phase 29 | Complete |
| CLASS-03 | Phase 29 | Complete |
| CLASS-04 | Phase 29 | Complete |
| GEN-01 | Phase 29 | Complete |
| GEN-02 | Phase 29 | Complete |
| GEN-03 | Phase 29 | Complete |
| GEN-04 | Phase 29 | Complete |
| EXP-01 | Phase 30 | Pending |
| EXP-02 | Phase 30 | Pending |
| EXP-03 | Phase 30 | Pending |
| EXP-04 | Phase 30 | Pending |
| EXP-05 | Phase 30 | Pending |
| EXP-06 | Phase 30 | Pending |
| PDF-01 | Phase 30 | Pending |
| PDF-02 | Phase 30 | Pending |
| PDF-03 | Phase 30 | Pending |
| PDF-04 | Phase 30 | Pending |
| PDF-05 | Phase 30 | Pending |

**Coverage:**
- v5.1 requirements: 51 total
- Mapped to phases: 51
- Unmapped: 0 ✓

**Coverage note:** Initial traceability stub listed 48; actual count from listed requirements is 51 (8 CHROME + 5 SRCH + 9 BUILD + 5 NAV + 2 PREV + 3 SEL + 4 CLASS + 4 GEN + 6 EXP + 5 PDF = 51).

---
*Requirements defined: 2026-03-11*
*Last updated: 2026-03-11 — traceability populated during roadmap creation*
