# JD Builder — Written UI Walkthrough for v5.1

**Source:** Google Docs — [JD Builder Written Walkthrough](https://docs.google.com/document/d/1IO_d2zLJEvfNEnJp8kMnEnobgWq2s4te0UULTQvniRU/edit?usp=sharing)  
**Captured:** 2026-03-11  
**Purpose:** Design target for v5.1 UI redesign. Use this as the reference when planning and building the new UI.

---

## Overview

This walkthrough describes the desired look-and-feel and functionality for v5.1 of JD Builder.

Screenshots in this document are taken from a functioning prototype based on **v4.0** of JD Builder ([dubedad/JD-Builder-Lite master branch](https://github.com/dubedad/JD-Builder-Lite/tree/master)). That earlier version was not fully integrated with JobForge 2.0. We have since completed that integration in v5.0.

**Objective of v5.1:** Make the current v5.0 application look, feel, and function like the version captured in the screenshots. We do not have access to the v4.0 source code, so this walkthrough is the authoritative design reference.

> **NOTE:** The doc uses both "Version 5.1" and "Version 6" interchangeably. For our GSD planning, this is **milestone v5.1**.

---

## High-Level User Flow

1. Search: user types "Web Developer" → results appear with match %
2. User clicks "Civil Engineer" (21300) → profile loads
3. Tabs: Overview (lead statement), Core Competencies (list), Key Activities (checkboxes), etc.
4. User selects 3 items from Key Activities, 2 from Skills
4.1 User clicks "Preview Job Description" to preview the job description
5. User clicks "Continue to Classification" → Classify page generates
6. User clicks "Analyse and recommend occupational group" → display occupational group details per TBS Directive on Classification s.4.1.2
7. User clicks "Continue to Generate" → AI Overview page displays (not included in this walkthrough)
8. User clicks "Generate with Claude AI" → AI generates overview in text area (nt included in this walkthrough)
9. User clicks "Continue" → report options page with Provenance Annex and/or Audit Trail toggles (not included in this walkthrough)
10. User clicks "Download PDF" or "Download Word"

---

## Page-by-Page Walkthrough

### 1.0 JD Builder Home Page (Search)

**Screenshots:** see `screenshots/` folder (to be added)

**Page Elements:**

**1. Header**
- Government of Canada logo and Language toggle
- Application name and byline
- Session ID (truncated; not clickable)
- Audit Trail (clickable)
- Reset (begin a new session)

**2. Data Sources** (all links to source homepages)
- 2021 NOC
- CAF Careers
- OCHRO Job Architecture
- O\*NET SOC
- OaSIS

**3. Process Steps** (clickable navigation)
- Search → returns to Home page with search results
- Build → launches Section 2.0
- Classify → launches Section 3.0
- Generate → launches Section 4.0
- Export → launches Section 5.0

**4. Search Box**
- User enters Job Title, Keywords, or NOC code
- As user types, search results appear as occupation cards below; more typing narrows results
- A filter panel appears to the left of the results
  - Checkboxes to apply filters to the results list
  - Filter items are the same as currently offered in OaSIS and v5.0

**5. Occupation Cards**
- User clicks on an occupation card to view the full profile
- Click event launches the Profile Page (Section 2.0)

---

### 2.0 Build — Overview

**Screenshots:** see `screenshots/` folder (to be added)

**Page Elements:**
1. A summary version of the Occupation Card appears at the top of the page, just under the Process Step buttons
2. Below the summary card is a set of tabs, one for each section of the Occupation Profile
3. The Overview tab is active (underlined)
4. Immediately under the tab is a description of what the user will see in this tab

**Overview tab content elements:**
- Position Title
- Lead Statement
- Definition
- Employment Requirements
- Typical Workplaces

All content comes from JobForge.

**Comparison to v5.0:**
v5.1 will display more text-based descriptions than v5.0 for the Overview tab.

---

### 2.1 Build — Core Competencies

**Screenshots:** see `screenshots/` folder (to be added)

**Page Elements:**
1. Section description at the top explaining what the user will see
2. List of Core Competencies for this job based on JobForge data
   - Select All checkbox to select all competencies in one click
   - Individual checkboxes for each competency
3. Bottom navigation buttons: ← Back to Search | Preview Job Description | Continue to Classification →

**Comparison to v5.0:**
v5.0 listed Core Competencies but they were **not selectable**. v5.1 makes them selectable.

---

### 2.2 Build — Key Activities

**Screenshots:** see `screenshots/` folder (to be added)

Same layout as Core Competencies tab. User selects all Key Activities that apply to this job.

**Comparison to v5.0 — IMPORTANT:**
- v5.0 lists Main Duties and Work Activities **separately**
- The v5.1 reference screenshots do NOT show this distinction
- **REQUIREMENT: RETAIN the separation.** Display two lists with headings:
  - "Main Duties"
  - "Work Activities"
- Adopt the v5.1 look-and-feel but keep both lists as distinct sections
- **RETAIN the blue dot importance scores from v5.0** — this visual is more effective

---

### 2.3 Build — Skills

**Screenshots:** see `screenshots/` folder (to be added)

Same layout as Core Competencies tab. User selects all Skills that apply to this job.

**Comparison to v5.0:**
**RETAIN the blue dots and importance ratings from v5.0** in the new UI for Skills.

---

### 2.4 Build — Abilities

**Screenshots:** see `screenshots/` folder (to be added)

Same layout as Core Competencies tab. User selects all Abilities that apply to this job.

**Comparison to v5.0:**
**RETAIN the blue dots and importance ratings from v5.0** in the new UI for Abilities.

---

### 2.5 Build — Knowledge

**Screenshots:** see `screenshots/` folder (to be added)

Same layout as Core Competencies tab. User selects all Knowledge items that apply to this job.

**Comparison to v5.0:**
**RETAIN the blue dots and importance ratings from v5.0** in the new UI for Knowledge.

---

### 2.6 Build — Effort

**Screenshots:** see `screenshots/` folder (to be added)

Same layout as Core Competencies tab. User selects all Effort items that apply to this job.

**Comparison to v5.0:**
**RETAIN the blue dots and importance ratings from v5.0** in the new UI for Effort.

---

### 2.7 Build — Responsibilities

**Screenshots:** see `screenshots/` folder (to be added)

Same layout as Core Competencies tab. User selects Responsibilities that apply to this job.

**Comparison to v5.0:**
**RETAIN the blue dots and importance ratings from v5.0** in the new UI for Responsibilities.

---

### 2.8 Build — Navigation and Preview

**Bottom navigation buttons** appear at the bottom of every Build tab.

**Current v5.1 screenshots show:** ← Back to Search | Continue to Classification →

**MODIFICATION REQUIRED — add a third button:**

```
← Back to Search  |  Preview Job Description  |  Continue to Classification →
```

**Behaviour rules:**

1. **Back to Search:**
   - Returns to the Search page
   - **DO NOT clear selections** made in the Build step
   - Retain all selections until the user clicks a different occupation card
   - If user clicks the **same card** → retain all selections
   - If user clicks a **different card** → clear all checkboxes

2. **Preview Job Description** (new button):
   - On click → builds a JD from all selected items
   - Displays the JD as a **preview in a modal**
   - Modal header: "Return to Builder" button
   - Modal footer: "Advance to Classify" button + "Export PDF" / "Export Word" buttons
   - Look-and-feel of modal matches the new v5.1 UI (not v5.0 styling)

3. **Continue to Classification →:**
   - Advances to Section 3.0 Classification

---

### 3.0 Classification

**Screenshots:** see `screenshots/` folder (to be added)

Accessed by clicking "Continue to Classification →" from any Build tab.

The Classification page loads with data from v5.0 (existing functionality), but **must be restyled** to match the v5.1 look-and-feel from the previous pages.

---

### 4.0 Generate (UI only — functionality deferred)

Button "Generate" exists in the Process Steps navigation in v5.1.

**NOTE:** The Generate functionality does not yet exist in v5.0. For v5.1, **create the button in the UI** but defer the backend functionality to a later version.

---

### 5.0 Export (UI only — functionality deferred)

Button "Export" exists in the Process Steps navigation in v5.1.

**NOTE:** The Export functionality does not yet exist in v5.0 in this context. For v5.1, **create the button in the UI** but defer the backend functionality to a later version.

---

## Key Design Decisions Summary

| Area | Decision |
|------|----------|
| **Blue dots / importance ratings** | Retain from v5.0 for all tabs: Key Activities, Skills, Abilities, Knowledge, Effort, Responsibilities |
| **Main Duties vs Work Activities** | Keep as two separate lists under distinct headings (do NOT merge) |
| **Core Competencies** | Make selectable (was read-only in v5.0) |
| **Navigation buttons** | 3-button bar: Back to Search \| Preview Job Description \| Continue to Classification |
| **Selection persistence** | Keep selections when returning to Search; clear only when a different occupation card is selected |
| **Preview modal** | JD preview in modal with Return to Builder + Classify + Export options |
| **Generate/Export steps** | UI buttons present in v5.1; backend functionality deferred |
| **Data source** | All content from JobForge (as of v5.0 integration) |

---

## Screenshots

All 14 screenshots are saved in `.planning/ui-walkthrough-v5.1/screenshots/`. Actual filenames:

| File | Page |
|------|------|
| `1.0 Home_Page.png` | Home / Search (empty state) |
| `1.1 Search Results.png` | Search results for "Web developer" |
| `2.0 Build.png` | Build — Overview tab |
| `2.1 Core Competencies.png` | Build — Core Competencies tab |
| `2.2 Key Activities.png` | Build — Key Activities tab |
| `2.3 Skills.png` | Build — Skills tab |
| `2.4 Abilities.png` | Build — Abilities tab |
| `2.5 Knowledge.png` | Build — Knowledge tab |
| `2.6 Effort.png` | Build — Effort tab |
| `2.7 Responsibilities.png` | Build — Responsibility tab |
| `2.8 Preview.png` | Preview Job Description modal |
| `3.0 Classification.png` | Classification — pre-analysis state |
| `3.0a Classification Step 1.png` | Classification results (reference app style) |
| `3.1 Classified.png` | Classification results (v5.1 app style) |

---

## Detailed Visual Notes from Screenshots

### 1.0 Home Page (empty state)

- **Header (dark navy):** "JobForge — JD Builder 1.0" as app name; byline "Job Description Builder with Full Audit Trail Provenance"; Session ID (truncated); Audit Trail badge with count; Reset button
- **Data source pills (top right, coloured):** 2021 NOC (green), CAF Careers (orange), OCHRO Job Architecture (orange), O*NET SOC (green), OaSIS (purple/blue)
- **Process stepper:** 5 pills — Search (filled/active), Build, Classify, Generate, Export
- **Match quality legend:** 95-100% Title (green pill), 85% Description (blue pill), 75% Related (grey)
- **Search box:** Large centered input, placeholder "Search by job title, keyword, or NOC code..."
- **Source link below search box:** "Source: JobForge WiQ | All job taxonomies" (purple link)
- **Empty state icon:** Magnifying glass with "Start typing to search across all job taxonomies"
- **Subtext:** "All queries logged per TBS Directive on Automated Decision-Making and assessed using the Algorithmic Impact Assessment"
- **Compliance footer (bottom of page body):** Long paragraph listing DAMA DMBOK 2.0, GC Data Quality Management Framework, TBS Directive on Automated Decision-Making, Policy on Service and Digital, MISO HAPIE GSD Framework, Directive on Classification, Guide to Allocating Positions, Policy on Results, PuMP Performance Measurement, O*NET SOC, CAF Careers, TBS Occupational Groups, OCHRO Job Architecture
- **Page footer:** "JobForge — JD Builder 1.0 | Full Audit Trail Provenance" left; "Canada" wordmark right; O*NET logo + attribution disclaimer at very bottom
- **Right edge:** "Selections (0)" tab/drawer

---

### 1.1 Search Results

- Left **filter panel** with accordion sections:
  - OCHRO Job Architecture (collapsed, no results shown)
  - CAF Careers (collapsed, no results)
  - 2021 NOC — Broad Category → Major Group (checkboxes with counts)
  - 2021 NOC TEER (TEER 1 - University degree checked)
  - Occupational Groups (NR - Architecture, Engineering... checked)
  - O*NET SOC (US) — 10 matches by category (Computer & Mathematical checked)
  - "X Clear All Filters" button
  - Match Confidence legend at bottom of panel
- **Results area:** "6 results (filtered)" | "+ New Search" button | "Published: 2024-11-15 | Data Steward: ESDC"
- **Occupation cards:** Each card shows:
  - Small icon + Title in bold
  - Match badge pills (e.g. "O*NET SOC", "100% - All keywords in title", "Bright Outlook")
  - "Also known as:" with matched keywords in bold
  - Description paragraph
- **Right edge:** "Selections (0)" tab visible

---

### 2.0 Build — Overview Tab

- **Occupation header card (dark navy):** Settings gear icon + Title + NOC code; lead statement below; bottom row: "NOC 2021 v1.0", clock icon + "Retrieved: 5:27:30 PM", "Quality Verified" badge, "View Provenance Graph" button (right-aligned)
- **Tab row:** Overview (active, underlined), Core Competencies, Key Activities, Skills, Abilities, Knowledge, Effort, Responsibility — all with icons
- **Section description box (light blue-grey):** "ⓘ Overview — The Overview provides a high-level summary..."
- **Content layout:**
  - "Position Title" label + text field with value
  - Two-column row: "Lead Statement" (left) | "Definition" (right) — both as text blocks
  - "Employment Requirements" as bullet list
  - "Typical Workplaces" as horizontal pill tags (e.g. "Advertising agencies", "Computer software firms")
- **Bottom buttons:** "← Back to Search" (outline) | "Continue to Classification →" (dark filled)

---

### 2.1 Build — Core Competencies Tab

- Section description box: "Core competencies represent the fundamental capabilities and personal attributes that are essential for effective performance..."
- "Select All (5)" checkbox | "3 selected" count (right-aligned)
- "SOURCES: GC Core Competencies" badge
- Group heading: "Unrated (5 items)" — no level grouping for this tab
- Individual items: checkbox + label text only (no sub-description)
- Some items checked (blue checkboxes)

---

### 2.2 Build — Key Activities Tab

- Section description: "Key activities are the main duties and tasks performed in this occupation..."
- "Select All (13)" | "0 selected"
- Sources: "Lead Statement" badge + "OaSIS Work Activities" badge
- Group: "Unrated (13 items)" — no level grouping
- Items are plain text sentences (no sub-descriptions, no level indicators in this screenshot)
- **NOTE for v5.1:** Walkthrough requires retaining v5.0 separation of "Main Duties" and "Work Activities" as two distinct lists, plus blue dot importance ratings

---

### 2.3 Build — Skills Tab

- Section heading with icon: "Skills (OaSIS Category F)"
- Description: "Developed capabilities that an individual must have to be effective in a job, role, function, task or duty. Skills are organized into: Foundational Skills (verbal, reading/writing, mathematical), Analytical Skills, Technical Skills, Resource Management Skills, and Interpersonal Skills."
- "Select All (5)" — fully checked | "5 selected"
- Sources: "Common Skills"
- Group: "Unrated (5 items)" — simple list
- **NOTE for v5.1:** Retain blue dot importance ratings from v5.0

---

### 2.4 Build — Abilities Tab

- Section heading: "Abilities (OaSIS Category A)"
- Description: "Innate and developed aptitudes that facilitate the acquisition of knowledge and skills..."
- "Select All (31)" | "6 selected"
- Sources: "OaSIS Abilities"
- **Items grouped by LEVEL with coloured level badges** (e.g. "Level 4 (4 items)", "Level 3 (15 items)")
- Each item has a **sub-description** line below the label (e.g. "The ability to come up with multiple ideas about a topic.")
- **NOTE for v5.1:** This level-grouping pattern (with level badges) should be the model for tabs that have importance/level data

---

### 2.5 Build — Knowledge Tab

- Section heading: "Knowledge (OaSIS Category G)"
- Description: "Organized sets of principles and practices used for the execution of tasks and activities within a particular domain..."
- "Select All (3)" — fully checked | "3 selected"
- Sources: "Common Knowledge"
- Group: "Unrated (3 items)" — simple list

---

### 2.6 Build — Effort Tab

- Section heading: "Effort (OaSIS Work Context J03)"
- Description: "Physical demands the job requires the worker to perform. This includes body positioning (sitting, standing, climbing, bending), body exertion (lifting, carrying, pushing, pulling), and speaking/seeing requirements..."
- "Select All (34)" | "7 selected"
- Sources: "OaSIS Work Context"
- **Items grouped by LEVEL** with coloured level badges ("Level 5 (3 items)", "Level 4 (6 items)")
- Each item has a **sub-description** line

---

### 2.7 Build — Responsibility Tab

- Section heading: "Responsibility (OaSIS Work Context J04)"
- Description: "Interpersonal relations and accountability required to perform the job. This includes job interactions (conflict handling, contact with others, leading/coordinating), communication methods, and interpersonal responsibilities..."
- "Select All (4)" — fully checked | "4 selected"
- Sources: "OaSIS Work Context"
- **Items grouped by LEVEL** ("Level 3 (3 items)", "Level 2 (1 item)")
- Each item has a **sub-description** line

---

### 2.8 Build — Preview Job Description

- Full JD preview showing:
  - Job title + NOC code header
  - "Key Activities" section: bulleted list of selected statements
  - "Skills" section: items with **importance dots and ratings** (e.g. "3 | Expert rated" shown as coloured pill)
  - "Appendix A: Compliance Metadata" section with table showing: Data Sources, Session ID, Retrieved date/time, Source URL, Session PID, NOC Version
  - "Documented Decisions (Evidence of compliance with DADM Directive 4.2.1)" table with columns: Job Term, Job Description Statement, Source, Publication Date, Links
  - "b. Selection Audit Trail" section with provenance info
  - "Data Quality Validation" section
- Bottom buttons: "Preview" | "Export" | "Export as PDF"

---

### 3.0 Classification — Pre-analysis State

- Page title card: "Occupational Group Allocation" with sub-title "Classification Step 1 — Per TBS Directive on Classification"
- Top-right badges: "● DADM Compliant" (green) | "🔗 Full Provenance" (purple)
- Dark card: "■ TBS Prescribed Allocation Method" with 3 boxes:
  - §4.1.1 Primary Purpose — "Determine why the position exists"
  - §4.1.2 Definition Fit — "Match work to OG definitions"
  - §4.1.3 Inclusions/Exclusions — "Verify alignment and conflicts"
- Large **orange CTA button**: "✏ Analyze & Recommend Occupational Group"

---

### 3.0a Classification — Results (Reference App Style)

- Different app chrome (Canada.ca header, MENU nav) — this is the reference app at 146.190.253.197
- "Classification Step 1: Occupational Group Allocation" page title
- "Recommended Occupational Groups" heading
- Results as numbered cards: IT (58% MEDIUM), PA–PA (40% MEDIUM), TC–TC (34% LOW)
- Expanded IT card shows:
  - Full rationale paragraph
  - Supporting evidence quotes with "Highlight in JD" links
  - Allocation Checks: Inclusions / Exclusions text
  - Confidence Breakdown: Definition 84%, Accurate 0%, Labels 0%, Semantic 4%, Match
  - Source Provenance chain
- "Classification Step 1 Complete" green checkmark banner
- "Next Steps" bullet list
- "← Return to Builder" button

---

### 3.1 Classification — Results (v5.1 App Style)

- Same header/nav/stepper as other v5.1 pages
- "Occupational Group Allocation" card + DADM Compliant + Full Provenance badges
- TBS 3-step method bar (same as 3.0)
- Orange "Analyze & Recommend Occupational Group" button
- Result card below: "**95% IT – Information Technology** — Recommended Occupational Group" with "↗ TBS Definition" link
- Green progress bar under title
- Description sentence explaining the determination
- "■ Statement Alignment Comparison" — two columns:
  - Left: "Your Selected Statements" (list of items from Build)
  - Right: "IT Definition Statements" (list from TBS definition)
  - "Overall Alignment Score: 0/8 statements aligned"
- "Key Evidence" section: green check bullets
- "Caveats" section: amber warning bullets
- "Alternative Groups Considered: EL – Electronics (25%)"
- "Next Step" instructions box with bold links to Job Evaluation Standard
- Bottom buttons: "← Back to Edit" | "**Continue to Generate →**"

---

## How to use this in GSD planning

Reference this file in phase plans:

```
@.planning/ui-walkthrough-v5.1/walkthrough.md
```

Reference the screenshots folder:

```
@.planning/ui-walkthrough-v5.1/screenshots/
```

Use both when running `/gsd:plan-phase` for v5.1 UI phases.
