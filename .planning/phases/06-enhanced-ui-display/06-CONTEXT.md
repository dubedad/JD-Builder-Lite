# Phase 6 Context: Enhanced UI Display

**Phase Goal:** Frontend renders enriched data with visual enhancements including star ratings, descriptions, scale meanings, NOC codes in search results, and grid view toggle.

**Requirements:**
- SRCH-04: Search results display grid view toggle (card vs table views)
- SRCH-05: Search results show NOC code next to profile title

**Created:** 2026-01-22
**Source:** User discussion session

---

## Star Rating Visuals

### Style
- **Use filled circles** (OASIS style): ●●●●○ not traditional stars
- Match OASIS site exactly for visual consistency

### Colors
- **Filled circles:** OASIS Blue (match the teal/blue from OASIS site)
- **Empty circles:** Lighter shade or outline version

### Label Display
- **Abbreviated text always visible** (e.g., "L5")
- **Full text on hover/focus** (e.g., "5 - Highest Level")
- Provides quick glance info with detail on demand

### Position
- **Dedicated column on right** of statement row
- Matches OASIS table layout with "Proficiency or complexity level" column
- Column header: "Proficiency" or "Level"

### Reference
- See Slide 12 in `overview for job lite process milestone 2/` for exact visual

---

## Grid View Layout

### Columns (user-selected)
1. **OASIS Profile** - NOC code + title as clickable link
2. **Example Titles** - Alternative job titles from "Also known as"
3. **Lead Statement** - Main occupation description
4. **Training/Education/Experience** - TEER requirements text

### Column Sorting
- **All columns sortable** via column header click
- Click to sort ascending, click again for descending
- Visual indicator (arrow) shows current sort direction

### Responsive Behavior
- **Auto-switch to cards below 768px**
- Grid view only available on tablet/desktop widths
- Card view works at all screen sizes

### Toggle Button
- Located in same position as OASIS (right side, above results)
- Shows "Card view" button when in grid mode, "Grid view" button when in card mode

---

## NOC Code Formatting

### In Search Results
- **Format:** "Air pilots (72600.01)" - title first, code in parentheses after
- **Style:** NOC code in muted/lighter gray color
- Title remains bold/dark, NOC code provides reference without competing

### On Profile Page Header
- **Badge/chip below title** (like Slide 9 shows)
- NOC code in small styled badge under the large profile title
- Visually distinct but secondary to the title

### Consistency
- Same NOC format used everywhere: parentheses style with muted color
- Profile header adds badge treatment for prominence

---

## Accessibility

### Proficiency Rating Announcements
- **Minimal:** Screen reader announces "Level 4"
- Relies on visible label for full context
- Keeps announcements brief for efficiency

### View Toggle Button
- **Icon only** with tooltip on hover/focus
- Grid icon (☰) / card icon (▦)
- `aria-label` provides accessible name (e.g., "Switch to grid view")
- Tooltip shows on hover for sighted users

### Keyboard Navigation
- **Tab only (standard)** - no arrow key enhancement
- Tab moves between interactive elements using default browser behavior
- Keeps implementation simple and predictable

### Color Contrast
- **Match OASIS site** contrast levels
- Consistency with source system over strict WCAG compliance
- Note: Should still meet minimum AA requirements

---

## Deferred Ideas

*None captured during this discussion.*

---

## Implementation Notes

### Critical from ROADMAP.md
- Use Unicode characters for circles (U+25CF filled, U+25CB empty)
- Implement aria-hidden on decorative circles, single aria-label on container
- Grid view uses CSS Grid for responsive table layout
- Persist grid preference in localStorage with quota check
- Test with NVDA/VoiceOver before shipping

### Reference Materials
- Slide 5-8: Search results card and grid views
- Slide 9: Profile page with NOC hierarchy breakdown
- Slide 12: Statement selection with proficiency circles

---

## MILESTONE 2 UI REDESIGN - SLIDE REFERENCE

*Added: 2026-01-23*
*Source: `overview for job lite process milestone 2/` slides*

---

### SWIMLANE PROCESS MAP (Slide 2)

**Three Swim Lanes:**
1. **Manager** - User actions
2. **Oasis site (Proxy for Gold Model)** - External API/data source
3. **Job Builder** - Our application

**Numbered Steps in Sequence:**

| Step | Lane | Action |
|------|------|--------|
| 1 | Manager | Enters a job title |
| 2 | Job Builder | Receives job title, makes API call to OaSIS site |
| 3 | Oasis site | Returns L6 results (Occupation Profiles) for job title search |
| 4 | Job Builder | Provides manager with Occupational Profile Menu |
| 5 | Manager | Selects best Occupational Profile |
| 6 | Job Builder | Receives selection, makes API call to scrape ALL content |
| 7 | Oasis site | Returns Occupational Profile details |
| 8 | Job Builder | Reformats Occ details into Job Desc "Headers" using NOC data to Job Desc map |
| 9 | Job Builder | Provides manager with Occupational Profile Details in Job Desc Element Menu format |
| 10 | Manager | Selects text blurbs PER HEADER, hits "Create JD" |
| 11 | Job Builder | Creates JD using authoritative JD text from NOC universe |
| Final | Manager | Hit Print to PDF button |

---

### STEP 1: JOB SEARCH WINDOW (Slide 4) - FINALIZED

**Position:** Search bar appears ABOVE the results grid

**UI Layout:**
```
┌─────────────────────────────────────────────────────────────────────┐
│ Job Builder   Search results - Pilot                                │
├─────────────────────────────────────────────────────────────────────┤
│ ┌──────────┐                             Search by keyword          │
│ │ Keyword  │                             ┌──────────────┐ ┌────────┐│
│ ├──────────┤                             │pilot         │ │ Search ││
│ │ Code     │                             └──────────────┘ └────────┘│
│ └──────────┘                                                        │
│                                                                     │
│ Authoritative Sources: ESDC OaSIS 2025 NOC v1.0 / ONET (R) 27.2    │
│ Database (USDOL/ETA)                                    [small font]│
└─────────────────────────────────────────────────────────────────────┘
```

**CONFIRMED Elements:**
- **Keyword/Code toggle** - pill buttons, BOTH options (Keyword selected by default)
- **Search by keyword** - text input field with placeholder
- **Search button** - primary action button (dark blue)
- **Authoritative Sources footnote** - small font below search controls:
  `"Authoritative Sources: ESDC OaSIS 2025 NOC v1.0 / ONET (R) 27.2 Database (USDOL/ETA)"`

**REMOVED Elements:**
- ~~Version dropdown~~ - replaced with footnote above
- ~~View all occupations A-Z link~~
- ~~Advanced search link~~

---

### STEP 4: OCCUPATIONAL PROFILE MENU (Slides 5, 6, 7, 8, 13) - FINALIZED

**Click Behavior:** Selecting a card takes user to Step 9 (Profile Details page)

**Display:** Replicate OaSIS search results page EXACTLY - use same HTML structure

---

**CARD VIEW (Default):**
Replicate OaSIS card structure exactly. Each card contains:
```
┌────────────────────────────────────────────────────────────────────┐
│ 72600.01 – Air pilots                                    [link]    │
├────────────────────────────────────────────────────────────────────┤
│ 🚚 Trades, transport and equipment operators...     [BOC category] │
│                                                                    │
│ 📑 Occupations usually require a college diploma... [TEER]        │
│                                                                    │
│ 📖 Air pilots fly fixed wing aircraft and...        [Lead stmt]   │
│                                                                    │
│ ─────────────────────────────────────────────────────────────────  │
│ 🔍 Matching search criteria                                        │
│    Label, Job titles                                               │
└────────────────────────────────────────────────────────────────────┘
```

**Card Content (6 data points per card):**
a) **Leading statement** for the OaSIS code (e.g., "Air pilots fly fixed wing aircraft...")
b) **Example titles** from "Also known as" section
c) **Educational requirement** from TEER (Training, Education, Experience and Responsibilities)
d) **Mobility and progression** content from "Additional Information" → "Feeder group mobility and career progression"
e) **Authoritative table** - source table the data came from
f) **Publication date** of that data file

---

**GRID VIEW (Toggle):**
Use grey icon button labeled "Grid view" with `fa-th-list` icon

**CUSTOM Grid Columns (NOT same as OaSIS page):**
| Column A: OaSIS Profile | Column B: Top 10 Skills | Column C: Top Abilities | Column D: Top Knowledge | Column E: Matching search criteria |

- Column A = NOC code + title (clickable link to Step 9)
- Column B = Top 10 skill titles for this occupation
- Column C = Top ability titles
- Column D = Top knowledge titles
- Column E = Same as OaSIS "Matching search criteria" column

---

**FILTER ITEMS (Custom - NOT same as OaSIS):**

Replace OaSIS filters with:
1. **Minor Unit Group** - filter by NOC minor group
2. **Feeder Group Mobility** - filter by career progression paths
3. **Career Progression** - filter by advancement opportunities

(Remove: Broad occupational category, TEER, Alphabetical listing)

---

**Sort/Display Controls (same as OaSIS):**
- **Sort by:** dropdown with options:
  - Label - A to Z
  - Label - Z to A
  - Code - Ascending
  - Code - Descending
  - Matching search criteria (default)
- **Grid view** toggle button (grey, with `fa-th-list` icon)
- **Pagination:** Show X entries dropdown, "Showing X to Y of Z entries"

---

### STEP 9: OCCUPATIONAL PROFILE DETAILS (Slides 9, 10) - FINALIZED

**Page Layout:**
```
┌──────────────────────────────────────────────────────────────────────┐
│ Air pilots                                        [LLM-driven icon]  │
│ ┌──────────┐                                                         │
│ │ 72600.01 │                                                         │
│ └──────────┘                                                         │
│ Air pilots fly fixed wing aircraft and helicopters...  [Lead stmt]  │
│                                                                      │
│ [LLM-generated paragraph description of occupational profile]       │
│                                                                      │
├──────────────────────────────────────────────────────────────────────┤
│ [Overview] [Key Activities] [Skills] [Effort] [Responsibility]      │
│            [Feeder Group Mobility & Career Progression]             │
└──────────────────────────────────────────────────────────────────────┘
```

**Header Section:**
- Occupation title (large)
- OaSIS code badge (e.g., "72600.01")
- Leading statement (below code)
- **LLM-generated paragraph** describing the occupational profile (above Overview/NOC hierarchy)
- **LLM-driven icon** based on minor group description

---

**TAB STRUCTURE (Job Description Headers/Elements):**

| Tab # | Tab Name | OaSIS Source Categories |
|-------|----------|------------------------|
| 1 | **Overview** | Also known as, Core competencies, Main duties, NOC hierarchy breakdown |
| 2 | **Key Activities** | Main Duties, Work Activities |
| 3 | **Skills** | Skills, Abilities, Knowledge |
| 4 | **Effort** | Work Context (filter for "effort") |
| 5 | **Responsibility** | Work Context (filter for "responsib" and "decision") |
| 6 | **Feeder Group Mobility & Career Progression** | Additional Information content |

**Content NOT in Job Description tabs (Overview only):**
- Job requirements
- Career mobility
- Example titles
- Labels
- Leading statements
- Interests
- Personal attributes

---

### STEP 9/10: STATEMENT SELECTION (Slides 10, 12) - FINALIZED

**Tab Content Format:**
Use EXACT same format as OaSIS profile page. Each Job Header tab shows selectable statements.

**Statement Row Components:**
1. **Checkbox** - for selection
2. **Statement text** - the actual content
3. **Proficiency circles** - ●●●●○ (keep as-is from OaSIS)
4. **Provenance label** - "from Main Duties", "from Work Activities", etc.
5. **Description tooltip** - MOUSEOVER shows OaSIS attribute description (for items with proficiency levels)

**Statement Row Example:**
```
☐ Analyzing Data or Information  [hover for description]  ●●●●● 5 - Highest Level
  from Work Activities
```

**Tooltip Behavior:**
- Hover over statement text → shows OaSIS attribute description
- Example: Hover "Analyzing Data or Information" → tooltip shows:
  "Identifying the underlying principles, reasons or facts of information by breaking down information or data into separate parts."
- Only applies to categories WITH proficiency levels (Work Activities, Skills, Abilities, etc.)
- Use standard HTML `title` attribute or custom tooltip component

**Proficiency Level Display:**
- ●●●●● 5 - Highest Level
- ●●●●○ 4 - High Level
- ●●●○○ 3 - Moderate Level
- ●●○○○ 2 - Low Level
- ●○○○○ 1 - Lowest Level

**Provenance:**
- Always visible (not on hover)
- Small italics below statement
- Shows source table name

---

**ACTION BUTTON (Single):**
- **"Create Job Description"** - primary blue button
- Shows count of selected items: "Create Job Description (X selected)"

(Removed: "Generate Overview" button)

---

### STEP 13: SEARCH RESULTS ENHANCEMENT (Slide 13)

**Current State (needs improvement):**
Simple list showing job titles with NOC codes only.

**Required Enhancement:**
Add leading statements to each result (scraped from OaSIS or via code lookup)

---

### DATA MAPPING (Slide 3)

**Job Description Headers (Elements):**
- **Key Activities** → NOC attributes: Main Duties, Work Activities
- **Skills** → NOC attributes: Skills, Abilities, Knowledge
- **Effort** → Work Context filtering for "effort"
- **Responsibility** → Work Context filtering for "responsib" and "decision"

**Organizational Context Elements (out of scope for v2.0):**
- Organizational Context, Client Service Results, Working Conditions (PARTLY from NOC workcontext)

**Manager Decision Points:**
1. Enter job title into text box
2. Select Occupational Profile from menu
3. Select Element statements under each Job Header
4. Hit "Create JD" button
5. Hit "Print to PDF" button

---

### TECHNICAL NOTES

**API Endpoint Pattern:**
```
https://noc.esdc.gc.ca/OaSIS/OaSISSearchResult?searchType=Keyword&searchText={keyword}&version=2025.0
```

**Scraping Requirements (Step 6):**
Scrape ALL content from: Overview, Work Characteristics, Skills and Abilities, Interests, Employment Requirements, Skills for Success

---

### QUESTIONS FOR CLARIFICATION

**Step 1 Questions:** ✅ RESOLVED
1. ✅ Search bar appears ABOVE results grid - YES
2. ✅ Version dropdown - REMOVED, replaced with small footnote: "Authoritative Sources: ESDC OaSIS 2025 NOC v1.0 / ONET (R) 27.2 Database (USDOL/ETA)"
3. ✅ Advanced search - REMOVED
4. ✅ View all occupations A-Z - REMOVED
5. ✅ Keyword/Code toggle - BOTH options included

**Step 4 Questions:** ✅ RESOLVED
1. ✅ Filter replacements: Minor Unit Group, Feeder Group Mobility, Career Progression
2. ✅ Card click → Navigate to Step 9 (Profile Details page)
3. ✅ Grid view toggle - replicate OaSIS grey button with fa-th-list icon
4. ✅ Card content: 6 data points (lead statement, example titles, TEER, mobility/progression, source table, publication date)
5. ✅ Grid columns: OaSIS Profile | Top 10 Skills | Top Abilities | Top Knowledge | Matching search criteria

**Step 9 Questions:** ✅ RESOLVED
1. ✅ Tab navigation - Keep horizontal tabs, change titles to Job Headers: Overview | Key Activities | Skills | Effort | Responsibility | Feeder Group Mobility & Career Progression
2. ✅ Statement provenance - ALWAYS visible (small italics below statement)
3. ✅ Level circles - Keep proficiency circles exactly as OaSIS (●●●●○)
4. ✅ LLM-generated paragraph above Overview/NOC hierarchy
5. ✅ LLM-driven icon based on minor group description
6. ✅ Leading statement appears under title and OaSIS code

**Step 10 Questions:** ✅ RESOLVED
1. ✅ Multi-select - checkboxes on all statements in all Job Header tabs
2. ✅ Single button only: "Create Job Description" (removed "Generate Overview")
3. ✅ All Job Description Elements/Headers are selectable

---

### DESIGN INSPIRATION

Replicate OaSIS site styling:
- Color scheme: Dark blue header (#003366), white content, purple links
- Typography: System fonts, clear hierarchy
- Card shadows and borders
- Button styles (blue primary, white secondary)
- Icon set (simple black icons per Slide 7)

Can extract actual HTML/CSS from:
- https://noc.esdc.gc.ca/OaSIS/OaSISWelcome
- Search results pages
- Profile detail pages

---
*Context captured: 2026-01-22*
*Milestone 2 slides added: 2026-01-23*
*Ready for: Research and planning*
