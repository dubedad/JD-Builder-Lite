# Phase 27: Build Page Redesign - Research

**Researched:** 2026-03-11
**Domain:** Vanilla JS + HTML/CSS UI redesign — no external framework
**Confidence:** HIGH (all findings from direct codebase inspection and screenshot analysis)

## Summary

Phase 27 redesigns the Build page to match the v5.1 reference prototype. All nine screenshots were read directly. The codebase was fully analysed. All data fields, rendering functions, CSS variables, icon library, and selection architecture were confirmed from source files.

The app uses Font Awesome 6.5.1 (CDN), vanilla JS with a proxy-based reactive store, and server-side-rendered templates. The Build page is driven by `accordion.js` (which despite its name now renders tab content) and the `TabController` class in `profile_tabs.js`. The occupation header card is a separate `#profile-header` element rendered by `renderProfileHeader()` in accordion.js.

The largest architectural gap: Core Competencies are currently rendered as a read-only `<ul>` of plain strings (no checkboxes, no sub-descriptions). The data model `ReferenceAttributes.core_competencies` is `List[str]` — there are NO sub-descriptions for competencies in the current data model. The v5.1 screenshot shows competencies WITHOUT sub-descriptions (just label text with checkbox). This is consistent.

Level grouping for Abilities/Effort/Responsibility: statements already carry `stmt.proficiency.level` (int 1–5). The v5.1 screenshot groups by level with coloured badges. This requires new JS grouping logic — not a backend change. Items ARE selectable (checkboxes visible in all three tabs). Items DO show sub-descriptions (stmt.description field is already populated by enrichment_service via guide.csv).

**Primary recommendation:** This is a pure frontend redesign. No backend API changes required. All data fields are available. Work is confined to `accordion.js` (rendering logic) + `index.html` (tab button HTML for icons) + CSS additions.

---

## Screenshots Analysis

### 2.0 Build — Overview tab (HIGH confidence)

**Occupation Header Card:**
- Dark navy background (~`#2d3748` or matching `--primary: #26374a`)
- Gear icon (`fa-cog`) on left of title — REPLACES current dynamic NOC-category icon
- Title "Web developers and programmers" in white, bold, ~24px
- NOC code "NOC  21234" below title (plain text, slightly smaller, grey/muted white)
- Lead statement paragraph below NOC code, white text, smaller font
- Bottom row left: `fa-file-alt` icon + "NOC 2021 v1.0" text | clock icon + "Retrieved: 5:27:30 PM" | "Quality Verified" text (no badge, plain text with check)
- Bottom row right: grey button "View Provenance Graph" with tree-diagram icon (cosmetic — no real action)
- `×` close button top-right (white)
- No "OASIS" link visible in header — header is self-contained

**Tab Row (below header card):**
- 8 tabs: Overview, Core Competencies, Key Activities, Skills, Abilities, Knowledge, Effort, Responsibility
- Icons preceding each tab label:
  - Overview: `fa-eye` (circle/eye icon)
  - Core Competencies: `fa-star` (star)
  - Key Activities: `fa-list-alt` or `fa-tasks` (3 lines with checkboxes)
  - Skills: `fa-lightbulb` (lightbulb)
  - Abilities: `fa-brain` or `fa-dumbbell` (brain-like icon — likely `fa-brain`)
  - Knowledge: `fa-book-open` or `fa-book` (open book)
  - Effort: `fa-arrows-alt` or `fa-exchange-alt` (arrows — `fa-exchange-alt` matches two opposing arrows)
  - Responsibility: `fa-user` (person/user silhouette)
- Active tab underlined with dark navy border (same pattern as current)

**Section Description Box — Overview tab:**
- Light blue-grey box, left border accent (dark blue ~4px)
- `fa-info-circle` icon (ⓘ) + bold "Overview" header
- Text: "The Overview provides a high-level summary of the occupation, including the lead statement, definition, and key characteristics from NOC and OaSIS data sources."
- Position: immediately below tab row, before content

**Overview tab content:**
- "Position Title" label + text input field (editable, shows occupation title as default)
- Two-column layout: "Lead Statement" (left) | "Definition" (right)
  - Lead Statement: paragraph text from `profile.reference_attributes.lead_statement` or profile title
  - Definition: longer paragraph — IMPORTANT: This is the LLM-generated description from `descEl.textContent` (rendered by `renderProfileHeader` async)
- "Employment Requirements" section: bold heading + bullet list
- "Typical Workplaces" section: bold heading + pill/tag chips (inline tags)

### 2.1 Core Competencies tab (HIGH confidence)

**Section Description Box:**
- Icon: `fa-star`
- Bold heading: "Core Competencies"
- Text: "Core competencies represent the fundamental capabilities and personal attributes that are essential for effective performance in this occupation. These include behavioral competencies, work styles, and professional values."

**Select All control:**
- Checkbox + "Select All (5)" label — positioned ABOVE the items list, left-aligned
- No count right-aligned at this row (unlike other tabs — the "3 selected" counter is at the far right of the Select All row)
- Specifically: `[ ] Select All (5)` on left, `3 selected` on far right of same row
- SOURCES badge below Select All row: "GC Core Competencies"

**Level group header:**
- "Unrated   (5 items)" — pill/badge styled as subtle label, not a coloured level badge
- This means core competencies have no proficiency level — they come from a separate data source

**Item rows:**
- Blue checkbox (checked state is blue fill)
- Label text only — NO sub-description line visible in this screenshot
- NOTE: CONTEXT.md says "Inline sub-descriptions: Yes" but screenshot shows NO sub-descriptions. The data model has only List[str] for core_competencies. This is an OPEN QUESTION — see below.

**Item IDs for selection:**
- Each item needs a unique ID. Must be assigned sequentially e.g. `core_competencies-0`, `core_competencies-1`

### 2.2 Key Activities tab (HIGH confidence)

**Section Description Box:**
- Icon: `fa-list-alt` (matches tab icon)
- Bold heading: "Key Activities"
- Text: "Key activities are the main duties and tasks performed in this occupation. They describe what workers in this role typically do on a regular basis."

**Select All + count:**
- "[ ] Select All (13)" left-aligned, "0 selected" right-aligned
- SOURCES: "Lead Statement" badge + "OaSIS Work Activities" badge — two separate source badges

**Level group header:**
- "Unrated   (13 items)" — same grey group header as Core Competencies
- NOTE: No Main Duties / Work Activities split visible in this screenshot — all items appear in one flat list under "Unrated"
- CRITICAL: The screenshot does NOT show a "Main Duties" vs "Work Activities" section separator. CONTEXT.md says separate Select All per section. The screenshot contradicts this — there is ONE Select All for all 13 items.
- Recommendation: The screenshot is authoritative. Use single Select All, single "Unrated" group. The per-section headers may only appear when there are both Main Duties AND Work Activities with different counts.

**Item rows:**
- Checkbox + label text only — no sub-descriptions visible
- Items include both "Web developers and programmers use a variety of..." (Main Duties text style) and "Estimate Quantifiable Charact. of Prod. ... (Level 3)" (Work Activities text with level in parentheses)

### 2.3 Skills tab (HIGH confidence)

**Section Description Box:**
- Icon: `fa-lightbulb`
- Bold heading: "Skills (OaSIS Category F)"
- Bold inline text: "Developed capabilities" + italic continuation: "that an individual must have to be effective in a job, role, function, task or duty. Skills are organized into: Foundational Skills (verbal, reading/writing, mathematical), Analytical Skills, Technical Skills, Resource Management Skills, and Interpersonal Skills."

**Select All + count:**
- Checked "Select All (5)" — "5 selected" right-aligned
- Sub-line below Select All: "Developed capabilities that an individual must have to be effective in a job, role, function, task or duty."
- SOURCES: "Common Skills" badge

**Level group:**
- "Unrated   (5 items)"
- Items: Critical Thinking, Problem Solving, Communication, Time Management, Decision Making
- No sub-descriptions visible

**Note on blue dot rating:** BUILD-09 says to retain blue dot importance rating. The current `renderProficiency()` renders filled/empty circles. The screenshot shows NO proficiency dots visible in Skills tab (items are unrated). This likely means the dots show only when proficiency.level > 0.

### 2.4 Abilities tab (HIGH confidence)

**Section Description Box:**
- Icon: `fa-brain` (brain-like shape)
- Bold heading: "Abilities (OaSIS Category A)"
- Bold inline text: "Innate and developed aptitudes" + italic: "that facilitate the acquisition of knowledge and skills to carry out expected work. Abilities include: Cognitive Abilities (reasoning, quantitative, memory, spatial, communication), Physical Abilities (strength, flexibility, endurance), Psychomotor Abilities (fine manipulation, control movement), and Sensory Abilities (auditory, visual, tactile)."

**Select All + count:**
- "[ ] Select All (31)" — "6 selected" right-aligned
- Sub-line: "Innate and developed aptitudes that facilitate the acquisition of knowledge and skills to carry out expected work."
- SOURCES: "OaSIS Abilities"

**CRITICAL — Level grouping:**
- Level 4 badge: blue pill/tag — text "Level 4   (4 items)"
  - Badge color appears to be a blue/teal — specifically `#4a90d9` or similar medium-blue pill
- Level 3 badge: orange/amber pill — text "Level 3   (15 items)"
  - Badge color appears amber/gold — `#f0a500` or similar
- Items ARE selectable (checkboxes present, some checked)
- Each item shows sub-description: e.g., "Fluency of Ideas (L4 proficiency level - Advanced)" with sub-text "The ability to come up with multiple ideas about a topic."

**Level badge color scheme (Abilities):**
- Level 5: Not visible in screenshot — likely darkest blue or green (highest)
- Level 4: Medium blue (~`#1565c0` or `#4a90d9`) — pill with white text
- Level 3: Amber/orange (~`#f57c00` or `#e6a817`) — pill with white or dark text
- Level 2: Not clearly visible — likely yellow or lighter
- Level 1: Not visible

### 2.5 Knowledge tab (HIGH confidence)

**Section Description Box:**
- Icon: `fa-book` (book/journal icon visible)
- Bold heading: "Knowledge (OaSIS Category G)"
- Bold inline text: "Organized sets of principles and practices" + italic: "used for the execution of tasks and activities within a particular domain. Knowledge areas include: Administration & Management, Communication, Education, Health & Wellbeing, Law/Government/Safety, Logistics & Design, Natural Resources, Physical Sciences, Socioeconomic Systems, Technology, and Foundational Knowledge."

**Select All:**
- Checked "[ ] Select All (3)" — "3 selected" right-aligned
- Sub-line: "Organized sets of principles and practices used for the execution of tasks and activities within a particular domain."
- SOURCES: "Common Knowledge"

**Level group:** "Unrated   (3 items)" — items have no proficiency levels
Items: English Language, Customer Service, Administration and Management — no sub-descriptions shown

### 2.6 Effort tab (HIGH confidence)

**Section Description Box:**
- Icon: `fa-exchange-alt` (matches tab — opposing arrows)
- Bold heading: "Effort (OaSIS Work Context J03)"
- Bold inline text: "Physical demands" + italic: "the job requires the worker to perform. This includes body positioning (sitting, standing, climbing, bending), body exertion (lifting, carrying, pushing, pulling), and speaking/seeing requirements. Effort descriptors help ensure job descriptions accurately reflect the physical requirements of the position."

**Select All:**
- "[ ] Select All (34)" — "7 selected" right-aligned
- Sub-line: "Physical activities the job requires the worker to perform."
- SOURCES: "OaSIS Work Context"

**CRITICAL — Level grouping:**
- Level 5 badge: GREEN pill — "Level 5   (3 items)" — green color, likely `#2e7d32` or `#28a745` with white text
- Level 4 badge: BLUE pill — "Level 4   (6 items)" — medium blue
- Items ARE selectable (checkboxes present, some checked)
- Each item shows sub-description: e.g., "Indoors, Environmentally Controlled (L5 frequency - Daily or more)" + "The job requires working inside a building with controlled temperature and humidity conditions."

**Level badge color scheme (Effort — Work Context):**
- Level 5: Green (`#28a745` or `#2e7d32`) — highest
- Level 4: Blue (`#1976d2` or `#4a90d9`) — high
- Level 3: Not visible in this screenshot
- Level 2: Not visible
- Level 1: Not visible

### 2.7 Responsibility tab (HIGH confidence)

**Section Description Box:**
- Icon: `fa-user` (person silhouette — matches tab icon)
- Bold heading: "Responsibility (OaSIS Work Context J04)"
- Bold inline text: "Interpersonal relations and accountability" + italic: "required to perform the job. This includes job interactions (conflict handling, contact with others, leading/coordinating), communication methods (email, face-to-face, public speaking), and interpersonal responsibilities (responsibility for others' outcomes, health and safety)."

**Select All:**
- Checked "[ ] Select All (4)" — "4 selected" right-aligned
- Sub-line: "Human interactions required to perform the job."
- SOURCES: "OaSIS Work Context"

**Level grouping:**
- Level 3 badge: AMBER/YELLOW pill — "Level 3   (3 items)" — amber color (~`#f57c00`)
- Level 2 badge: GREY/LIGHT pill — "Level 2   (1 items)" — lighter grey-blue or grey
- Items ARE selectable with sub-descriptions

**Level badge color scheme (Responsibility — Work Context):**
- Level 5: Green
- Level 4: Blue
- Level 3: Amber/Yellow (`#f57c00` or `#ff9800`)
- Level 2: Light grey-blue (`#90a4ae` or `#78909c`)
- Level 1: Lightest grey

**Consolidated Level Badge Color Scheme (applies to Abilities, Effort, Responsibility):**
| Level | Color | Hex Approx | CSS |
|-------|-------|------------|-----|
| Level 5 | Green | `#28a745` | `--level-5-bg: #28a745; --level-5-text: #fff` |
| Level 4 | Blue | `#1976d2` | `--level-4-bg: #1976d2; --level-4-text: #fff` |
| Level 3 | Amber | `#f57c00` | `--level-3-bg: #f57c00; --level-3-text: #fff` |
| Level 2 | Grey-blue | `#78909c` | `--level-2-bg: #78909c; --level-2-text: #fff` |
| Level 1 | Light grey | `#9e9e9e` | `--level-1-bg: #9e9e9e; --level-1-text: #fff` |

---

## Standard Stack

### Core (all already in project)
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Font Awesome | 6.5.1 (CDN) | Icons for tab icons and section headers | Already loaded in `<head>` — no installation needed |
| Vanilla JS | ES2020+ | All rendering logic | Project standard — no build system |
| CSS Custom Properties | Native | Design tokens | Project uses `--primary`, `--accent` etc. |

### No New Libraries Required
This phase adds no dependencies. All icons are Font Awesome. All JS is vanilla. All CSS is added to existing `.css` files.

**Installation:** None required.

---

## Architecture Patterns

### Current Build Page Architecture

```
index.html
├── #profile-header            (occupation header — rendered by renderProfileHeader() in accordion.js)
├── #profile-tabs-container    (tab nav + panels — rendered by renderTabContent() in accordion.js)
│   ├── .tabs-bar              (tab buttons — HTML in index.html, enhanced by TabController)
│   └── #panel-{name}         (tab panel divs — innerHTML set by renderTabContent())
└── #sidebar                   (selections drawer — Phase 28 scope)
```

### Files to Modify

| File | What Changes |
|------|-------------|
| `templates/index.html` | Add icons to tab buttons; add NOC version/timestamp/verified to header area |
| `static/js/accordion.js` | All rendering functions rewritten; new `renderLevelGroups()` helper; `renderCoreCompetenciesContent()` upgraded |
| `static/css/main.css` | Level badge CSS, section description box CSS, occupation header redesign |
| `static/css/accordion.css` | Tab item row CSS if separate file |
| `static/js/state.js` | Add `core_competencies` to default selections state |

### Pattern 1: Section Description Box

**What:** Blue-grey info box at top of each tab panel with left border accent, info icon, bold title, description text.
**When to use:** Every tab panel, before the Select All row and items list.

```html
<!-- Source: v5.1 screenshots — design spec -->
<div class="section-description-box">
  <i class="fas fa-info-circle section-description-box__icon"></i>
  <div class="section-description-box__content">
    <strong class="section-description-box__title">
      <i class="fas fa-star"></i> Core Competencies
    </strong>
    <p class="section-description-box__text">
      Core competencies represent the fundamental capabilities...
    </p>
  </div>
</div>
```

```css
/* Source: extracted from v5.1 screenshots */
.section-description-box {
  background: #f0f4f8;      /* light blue-grey */
  border-left: 4px solid #26374a;  /* var(--primary) */
  border-radius: 4px;
  padding: 0.75rem 1rem;
  margin-bottom: 1rem;
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
}
.section-description-box__title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.95rem;
  color: var(--primary);
  margin-bottom: 0.25rem;
}
.section-description-box__text {
  font-size: 0.875rem;
  color: var(--text-light);
  margin: 0;
}
```

### Pattern 2: Select All Row (v5.1 format)

**What:** Checkbox "Select All (N)" on left, "N selected" count on right, SOURCES badges below.
**Current state:** Exists but styled differently — currently uses `select-all-label` + `style-selected-btn`. The `style-selected-btn` must be REMOVED in v5.1.

```html
<!-- Source: v5.1 screenshots -->
<div class="select-all-row">
  <label class="select-all-label">
    <input type="checkbox" class="select-all-checkbox" data-section="core_competencies">
    Select All (5)
  </label>
  <span class="selection-count" id="count-core_competencies">3 selected</span>
</div>
<div class="sources-row">
  <span class="sources-label">SOURCES:</span>
  <span class="source-chip source-chip--gc">GC Core Competencies</span>
</div>
```

### Pattern 3: Level Group Header

**What:** Coloured pill badge + item count, used as group separator for Abilities/Effort/Responsibility.
**Also used for:** "Unrated" group in Core Competencies, Key Activities, Skills, Knowledge.

```html
<!-- Level group header for Abilities/Effort/Responsibility -->
<div class="level-group-header">
  <span class="level-badge level-badge--4">Level 4</span>
  <span class="level-group-count">(4 items)</span>
</div>

<!-- "Unrated" group header (Core Comp, Key Activities, Skills, Knowledge) -->
<div class="level-group-header">
  <span class="level-badge level-badge--unrated">Unrated</span>
  <span class="level-group-count">(5 items)</span>
</div>
```

```css
/* Level badge colors — extracted from v5.1 screenshots */
.level-badge {
  display: inline-block;
  padding: 0.2rem 0.6rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  color: white;
}
.level-badge--5 { background: #28a745; }
.level-badge--4 { background: #1976d2; }
.level-badge--3 { background: #f57c00; }
.level-badge--2 { background: #78909c; }
.level-badge--1 { background: #9e9e9e; }
.level-badge--unrated { background: #9e9e9e; color: white; }
```

### Pattern 4: Item Row with Sub-Description

**What:** Checkbox + label text on first line, sub-description in smaller grey text below.
**Data source:** `stmt.description` field (already present in `EnrichedNOCStatement`).

```html
<li class="statement tab-panel__item" data-id="abilities-0">
  <label class="statement__label">
    <input type="checkbox" class="statement__checkbox"
           data-section="abilities" data-id="abilities-0">
    <span class="statement__content">
      <span class="statement__text">Fluency of Ideas (L4 proficiency level - Advanced)</span>
      <span class="statement__description">The ability to come up with multiple ideas about a topic.</span>
    </span>
  </label>
</li>
```

Note: `statement__description` class already exists in `accordion.js` rendering — just needs CSS styling consistent with v5.1.

### Pattern 5: Level Grouping Logic (NEW)

**What:** Group statements by `stmt.proficiency.level` before rendering. Descending order (Level 5 first).
**Applies to:** Abilities, Effort, Responsibility tabs only.
**Unrated tabs:** Core Competencies, Key Activities, Skills, Knowledge use single "Unrated" group.

```javascript
// Source: derived from v5.1 screenshots + codebase analysis
function groupStatementsByLevel(statements) {
  const groups = {};
  statements.forEach(stmt => {
    const level = stmt.proficiency?.level || 0;
    if (!groups[level]) groups[level] = [];
    groups[level].push(stmt);
  });
  // Return sorted descending (Level 5 first, then 4, 3, 2, 1, 0/Unrated)
  return Object.entries(groups)
    .sort(([a], [b]) => parseInt(b) - parseInt(a));
}
```

### Pattern 6: Occupation Header Card (v5.1)

**What:** Dark navy card with gear icon, title, NOC code, lead statement, metadata row, provenance button.
**Current state:** `#profile-header` with class `blueBG` — needs complete restyle and HTML restructure.

New HTML structure needed in `index.html`:
```html
<section id="profile-header" class="occupation-header-card hidden">
  <div class="occupation-header-card__top">
    <div class="occupation-header-card__icon-title">
      <i class="fas fa-cog occupation-header-card__gear" aria-hidden="true"></i>
      <div>
        <h2 id="profile-title" class="occupation-header-card__title"></h2>
        <span id="profile-code-badge" class="occupation-header-card__noc-code"></span>
      </div>
    </div>
    <button class="occupation-header-card__close" id="profile-header-close" aria-label="Close">×</button>
  </div>
  <p id="profile-lead-statement" class="occupation-header-card__lead"></p>
  <div class="occupation-header-card__meta">
    <span id="profile-noc-version" class="occupation-header-card__meta-item">
      <i class="fas fa-file-alt"></i> NOC 2021 v1.0
    </span>
    <span id="profile-timestamp" class="occupation-header-card__meta-item">
      <i class="fas fa-clock"></i> Retrieved: ...
    </span>
    <span class="occupation-header-card__meta-item">Quality Verified</span>
    <button class="occupation-header-card__provenance btn btn--ghost btn--sm" id="provenance-graph-btn-2">
      <i class="fas fa-project-diagram"></i> View Provenance Graph
    </button>
  </div>
</section>
```

### Anti-Patterns to Avoid

- **Do NOT change backend API:** All data fields are already present. Zero Python changes required.
- **Do NOT add selection row highlight on check:** CONTEXT.md locked this — checkbox state only, no background tint on `.statement--selected`.
- **Do NOT call renderTabContent() without re-initializing TabController:** The `TabController` must be recreated each time renderTabContent() runs (already done in existing code).
- **Do NOT break existing selection.js event delegation:** Uses `document.addEventListener('change')` on `.statement__checkbox` and `.select-all-checkbox`. New `core_competencies` items must use the SAME classes.
- **Do NOT duplicate the provenance button:** There is already `#provenance-graph-btn` in the app bar. The header card button should be cosmetic (`onclick="event.preventDefault()"`) or trigger the same modal.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Tab switching | Custom JS | Existing `TabController` in `profile_tabs.js` | Already works, handles ARIA keyboard nav |
| Checkbox state management | Custom event handling | Existing `selection.js` `handleSelection()` + `handleSelectAll()` | Already handles state, sidebar, action bar updates |
| Reactive state | Custom store | Existing `store` in `state.js` | Proxy-based, persists to localStorage |
| Icon rendering | SVG assets | Font Awesome 6.5.1 (already loaded) | CDN already in `<head>` |

---

## Common Pitfalls

### Pitfall 1: Core Competencies selection state not persisted

**What goes wrong:** Adding competency checkboxes without updating `state.js` default state means selections clear on page reload.
**Why it happens:** `defaultState.selections` in `state.js` does not include `core_competencies` key.
**How to avoid:** Add `core_competencies: []` to both the `defaultState.selections` object and the `resetSelectionsForProfile()` function in `state.js`.
**Warning signs:** Checking a competency and reloading page — selection disappears.

### Pitfall 2: `renderTabContent()` called before profile-header DOM is updated

**What goes wrong:** The occupation header card has a `×` close button. If the close button hides the entire `#profile-tabs-container`, returning to Build step via stepper shows nothing.
**Why it happens:** Close button removes `hidden` from search results but tab container stays hidden.
**How to avoid:** The close button (×) should navigate to Step 1 (Search) via `window.jdStepper.goToStep(1)` — same as "Back to Search" button — NOT hide elements directly.

### Pitfall 3: Level grouping breaks when proficiency is null

**What goes wrong:** Skills/Knowledge items have `proficiency: null` and will error when `stmt.proficiency.level` is accessed.
**Why it happens:** Parquet-sourced items without ratings have null proficiency.
**How to avoid:** Use `stmt.proficiency?.level || 0` throughout. Level 0 maps to "Unrated" group.

### Pitfall 4: Key Activities screenshot contradicts CONTEXT.md per-section Select All

**What goes wrong:** CONTEXT.md says "Select All: Per section — separate Select All for Main Duties and Work Activities." But screenshot 2.2 shows ONE Select All (13) with mixed items.
**Why it happens:** Screenshot is authoritative per CONTEXT.md decision protocol.
**How to avoid:** Planner must resolve this ambiguity. Recommendation: implement single Select All for Key Activities (matching screenshot). The per-section Select All may only apply when the two sections are visually separated — which the screenshot doesn't show for this occupation.

### Pitfall 5: `updateSelectionCount()` not called for new `core_competencies` section

**What goes wrong:** The selection count badge in the tab button or sidebar doesn't update when competencies are selected.
**Why it happens:** `store.subscribe` in `selection.js` calls `updateSelectionCount(sectionId)` for each key in `state.selections`. If `core_competencies` is not in default state, it won't be subscribed.
**Warning signs:** "N selected" count stays at 0 despite checking items.

### Pitfall 6: Overview tab "Definition" column has no backend field

**What goes wrong:** The v5.1 screenshot shows a two-column "Lead Statement | Definition" layout. The "Definition" column contains the longer LLM-generated description.
**Current state:** `profile-description` element is populated asynchronously by `api.fetchOccupationDescription()`. This is the "Definition" in v5.1.
**How to avoid:** Wire the Overview tab's "Definition" column to `#profile-description` content. Since it loads async, show a loading spinner or placeholder until the description arrives.

---

## Data Field Mapping

| v5.1 UI Element | Data Source | Field Path | Notes |
|----------------|-------------|-----------|-------|
| Occupation title | Profile API | `profile.title` | Direct |
| NOC code | Profile API | `profile.noc_code` | Direct |
| Lead statement (header) | Profile API | `profile.reference_attributes.lead_statement` | Parser extracts from OASIS HTML — may be empty |
| NOC version badge | Hardcoded | "NOC 2021 v1.0" | No API field — hardcode |
| Retrieved timestamp | Profile API | `profile.metadata.scraped_at` | Format as "Retrieved: H:MM AM/PM" |
| Quality Verified badge | Hardcoded | "Quality Verified" | No API field — hardcode |
| Position Title input | Editable field | `profile.title` as default | User can edit — store in state |
| Lead Statement (Overview tab) | Profile API | `profile.reference_attributes.lead_statement` | |
| Definition (Overview tab) | LLM async | `#profile-description` element text | Async — wait for API |
| Employment Requirements | Profile API | `profile.other_job_info.employment_requirements` | Already fetched |
| Typical Workplaces | Profile API | `profile.other_job_info.workplaces` | Already fetched |
| Core Competencies items | Profile API | `profile.reference_attributes.core_competencies` | `List[str]` — label only, no sub-descriptions |
| Core Comp sub-descriptions | NOT AVAILABLE | — | Data model has no descriptions for competencies |
| Key Activities items | Profile API | `profile.key_activities.statements` | `source_attribute` = "Main Duties" or "Work Activities" |
| Skills items | Profile API | `profile.skills.statements` where `source_attribute === "Skills"` | |
| Abilities items | Profile API | `profile.skills.statements` where `source_attribute === "Abilities"` | Yes, same `skills` field |
| Knowledge items | Profile API | `profile.skills.statements` where `source_attribute === "Knowledge"` | Yes, same `skills` field |
| Effort items | Profile API | `profile.effort.statements` | From Work Context parquet |
| Responsibility items | Profile API | `profile.responsibility.statements` | From Work Context parquet |
| Level grouping key | Statement | `stmt.proficiency.level` (int 1-5, null=unrated) | |
| Item sub-description | Statement | `stmt.description` | Populated by enrichment_service from guide.csv |
| Importance dots (BUILD-09) | Statement | `stmt.proficiency` | `renderProficiency()` already exists |
| SOURCES badges | Profile API | `profile.*.data_source` ("jobforge" or "oasis") | Map to human-readable label |

---

## Selection Architecture

### Current State

```javascript
// state.js default state
selections: {
  key_activities: [],
  skills: [],
  effort: [],
  responsibility: [],
  working_conditions: []
}
```

Core Competencies selections are NOT currently stored. `core_competencies` key is ABSENT.

### Required Change

Add `core_competencies: []` to:
1. `defaultState.selections` in `state.js`
2. The reset block in `resetSelectionsForProfile()` in `state.js`

No other state changes needed. The existing `handleSelection()` and `handleSelectAll()` functions in `selection.js` work via event delegation — they will handle Core Competencies automatically as long as:
- Item checkboxes have `class="statement__checkbox"` + `data-section="core_competencies"` + `data-id="core_competencies-{n}"`
- Select All checkbox has `class="select-all-checkbox"` + `data-section="core_competencies"`

### Selection ID Format for Core Competencies

```javascript
// Pattern matching existing tabs
const stmtId = `core_competencies-${index}`;
```

### Abilities/Knowledge/Skills Selection Keys

Currently abilities, knowledge are stored under their own keys but the current code uses `abilities` and `knowledge` as separate sections. Check `state.js` default state — currently missing `abilities` and `knowledge` keys! The current `accordion.js` passes `state.selections.abilities || []` but state.js doesn't initialize them.

**Finding:** `state.js` default state lacks `abilities` and `knowledge` keys. These tabs are already rendered with checkboxes but selections may not persist. This is a pre-existing bug. Phase 27 should add these keys too.

---

## Level Badge Colors (Authoritative)

Extracted from screenshots 2.4 (Abilities) and 2.6 (Effort) and 2.7 (Responsibility):

| Level | Label | Badge Color | Text Color | Screenshot Evidence |
|-------|-------|-------------|------------|---------------------|
| Level 5 | Highest | `#28a745` (green) | white | 2.6 Effort — "Level 5  (3 items)" green pill |
| Level 4 | High | `#1976d2` (blue) | white | 2.4 Abilities — "Level 4  (4 items)" blue pill |
| Level 3 | Medium | `#f57c00` (amber) | white | 2.7 Responsibility — "Level 3  (3 items)" amber pill |
| Level 2 | Low | `#78909c` (grey-blue) | white | 2.7 Responsibility — "Level 2  (1 items)" light grey |
| Level 1 | Basic | `#9e9e9e` (grey) | white | Not in screenshot — interpolated |
| Unrated | — | `#9e9e9e` (grey) | white | 2.1/2.2/2.3/2.5 all use same grey "Unrated" header |

---

## Section Description Box Text (Exact, Authoritative)

Extracted verbatim from screenshots:

### Overview tab
- Title: "Overview"
- Text: "The Overview provides a high-level summary of the occupation, including the lead statement, definition, and key characteristics from NOC and OaSIS data sources."

### Core Competencies tab
- Title: "Core Competencies"
- Text: "Core competencies represent the fundamental capabilities and personal attributes that are essential for effective performance in this occupation. These include behavioral competencies, work styles, and professional values."

### Key Activities tab
- Title: "Key Activities"
- Text: "Key activities are the main duties and tasks performed in this occupation. They describe what workers in this role typically do on a regular basis."

### Skills tab
- Title: "Skills (OaSIS Category F)"
- Text (first part bold): "Developed capabilities" (remaining italic): "that an individual must have to be effective in a job, role, function, task or duty. Skills are organized into: Foundational Skills (verbal, reading/writing, mathematical), Analytical Skills, Technical Skills, Resource Management Skills, and Interpersonal Skills."

### Abilities tab
- Title: "Abilities (OaSIS Category A)"
- Text (bold): "Innate and developed aptitudes" (italic): "that facilitate the acquisition of knowledge and skills to carry out expected work. Abilities include: Cognitive Abilities (reasoning, quantitative, memory, spatial, communication), Physical Abilities (strength, flexibility, endurance), Psychomotor Abilities (fine manipulation, control movement), and Sensory Abilities (auditory, visual, tactile)."

### Knowledge tab
- Title: "Knowledge (OaSIS Category G)"
- Text (bold): "Organized sets of principles and practices" (italic): "used for the execution of tasks and activities within a particular domain. Knowledge areas include: Administration & Management, Communication, Education, Health & Wellbeing, Law/Government/Safety, Logistics & Design, Natural Resources, Physical Sciences, Socioeconomic Systems, Technology, and Foundational Knowledge."

### Effort tab
- Title: "Effort (OaSIS Work Context J03)"
- Text (bold): "Physical demands" (italic): "the job requires the worker to perform. This includes body positioning (sitting, standing, climbing, bending), body exertion (lifting, carrying, pushing, pulling), and speaking/seeing requirements. Effort descriptors help ensure job descriptions accurately reflect the physical requirements of the position."

### Responsibility tab
- Title: "Responsibility (OaSIS Work Context J04)"
- Text (bold): "Interpersonal relations and accountability" (italic): "required to perform the job. This includes job interactions (conflict handling, contact with others, leading/coordinating), communication methods (email, face-to-face, public speaking), and interpersonal responsibilities (responsibility for others' outcomes, health and safety)."

---

## Icon Library Available

Font Awesome 6.5.1 is loaded via CDN:
```html
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
```

### Tab Icon Recommendations

| Tab | Icon Class | Rationale |
|-----|-----------|-----------|
| Overview | `fa-eye` | Eye = observe/overview — visible in screenshot |
| Core Competencies | `fa-star` | Star = important attributes — matches screenshot |
| Key Activities | `fa-list-check` or `fa-tasks` | Checklist = tasks/duties — matches screenshot (3 lines with check marks) |
| Skills | `fa-lightbulb` | Lightbulb = capability/knowledge — matches screenshot |
| Abilities | `fa-brain` | Brain = cognitive/physical aptitudes — matches screenshot brain icon |
| Knowledge | `fa-book-open` | Open book = organized knowledge — matches screenshot open book |
| Effort | `fa-exchange-alt` | Two opposing arrows = physical effort/exertion — matches screenshot |
| Responsibility | `fa-user` | Person silhouette = interpersonal/human role — matches screenshot |

Note: FA 6.x uses `fa-solid` prefix or just `fas`. Some icon names differ between FA 5 and FA 6. `fa-tasks` was renamed to `fa-list-check` in FA 6. Since the project uses `fas fa-*` syntax, verify: `fas fa-list-check` (FA6) vs `fas fa-tasks` (FA5/6 both work).

---

## Code Examples

### Rendering Level Groups (New Function)

```javascript
// Source: derived from v5.1 screenshots + EnrichedNOCStatement data model
function renderLevelGroups(statements, sectionId, selectedIds, showSelectAll = true) {
    // Group by proficiency level
    const groups = {};
    statements.forEach(stmt => {
        const level = stmt.proficiency?.level || 0;
        if (!groups[level]) groups[level] = [];
        groups[level].push(stmt);
    });

    const totalCount = statements.length;
    const totalSelected = selectedIds.length;
    const allSelected = totalSelected === totalCount && totalCount > 0;

    let html = '';

    // Select All row
    if (showSelectAll) {
        html += `
            <div class="select-all-row">
                <label class="select-all-label">
                    <input type="checkbox" class="select-all-checkbox"
                           data-section="${sectionId}"
                           ${allSelected ? 'checked' : ''}>
                    Select All (${totalCount})
                </label>
                <span class="selection-count" id="count-${sectionId}">
                    ${totalSelected > 0 ? totalSelected + ' selected' : ''}
                </span>
            </div>
        `;
    }

    // Groups descending by level (5, 4, 3, 2, 1, 0=unrated)
    const sortedGroups = Object.entries(groups)
        .sort(([a], [b]) => parseInt(b) - parseInt(a));

    sortedGroups.forEach(([levelStr, items]) => {
        const level = parseInt(levelStr);
        const levelLabel = level === 0 ? 'Unrated' : `Level ${level}`;
        const badgeClass = level === 0 ? 'level-badge--unrated' : `level-badge--${level}`;

        html += `
            <div class="level-group-header">
                <span class="level-badge ${badgeClass}">${levelLabel}</span>
                <span class="level-group-count">(${items.length} items)</span>
            </div>
            <ul class="tab-panel__list jd-section__list">
        `;

        items.forEach(stmt => {
            const globalIdx = statements.indexOf(stmt);
            const stmtId = `${sectionId}-${globalIdx}`;
            const isSelected = selectedIds.includes(stmtId);
            const descHtml = stmt.description
                ? `<span class="statement__description">${escapeHtml(stmt.description)}</span>`
                : '';
            // Importance dots (BUILD-09) — only when proficiency exists
            const profHtml = stmt.proficiency ? renderProficiency(stmt.proficiency, stmt.source_attribute) : '';

            html += `
                <li class="statement tab-panel__item${isSelected ? ' statement--selected' : ''}" data-id="${stmtId}">
                    <label class="statement__label">
                        <input type="checkbox" class="statement__checkbox"
                               data-section="${sectionId}"
                               data-id="${stmtId}"
                               ${isSelected ? 'checked' : ''}>
                        <span class="statement__content">
                            <span class="statement__text">${escapeHtml(stmt.text)}</span>
                            ${descHtml}
                        </span>
                        ${profHtml}
                    </label>
                </li>
            `;
        });

        html += '</ul>';
    });

    return html;
}
```

### Updated state.js defaultState

```javascript
// Source: state.js — add core_competencies, abilities, knowledge
const defaultState = {
    selections: {
        core_competencies: [],     // NEW
        key_activities: [],
        skills: [],
        abilities: [],             // NEW (was missing)
        knowledge: [],             // NEW (was missing)
        effort: [],
        responsibility: [],
        working_conditions: []
    },
    sectionOrder: ['key_activities', 'skills', 'effort', 'responsibility', 'working_conditions'],
    currentProfileCode: null
};
```

---

## State of the Art

| Old Approach (v5.0) | v5.1 Approach | Impact |
|---------------------|---------------|--------|
| Core Competencies: read-only `<ul>` of strings | Selectable with checkboxes | Must add to store state + selection.js |
| Abilities/Knowledge rendered in same panel as Skills | Separate tabs with own panels | Already separate in current code |
| No level badges on tab items | Level badges group items | New CSS + new JS grouping function |
| No section description box | Blue-grey info box per tab | New CSS + HTML pattern |
| Occupation header: `profile-header blueBG` with briefcase icon | Dark navy card with gear icon, metadata row, provenance btn | HTML restructure + CSS rewrite |
| Tab buttons: text only | Tab buttons: icon + text | HTML change in index.html |
| Select All row includes "Style Selected" button | No "Style Selected" button | Remove from rendering |

---

## Open Questions

1. **Core Competencies sub-descriptions (CONTEXT.md says "Yes" but screenshot shows "No")**
   - What we know: CONTEXT.md decision says "Inline sub-descriptions: Yes — each competency shows a brief description below its label". Screenshot 2.1 shows NO sub-description text below competency labels (just label text only). The data model `ReferenceAttributes.core_competencies` is `List[str]` with no descriptions.
   - What's unclear: Does the v5.1 spec intend descriptions that are not yet in the data, or did the decision mean something different?
   - Recommendation: Implement as label-only (matching screenshot). If sub-descriptions are needed later, they require a backend data model change to `core_competencies: List[CoreCompetency]` where `CoreCompetency` has `{label, description}`. Flag this to planner to confirm.

2. **Key Activities: Single Select All vs per-section Select All**
   - What we know: Screenshot shows ONE "Select All (13)" for both Main Duties + Work Activities combined. CONTEXT.md says separate Select All per section.
   - What's unclear: Whether the per-section UI only appears when there is a visible section separator.
   - Recommendation: Match screenshot — implement single Select All. Add per-section Select All only if there are visible "Main Duties" and "Work Activities" headings separating the items.

3. **Overview tab: Position Title field — is it truly editable?**
   - What we know: Screenshot shows a text input field with "Web developers and programmers" as value.
   - What's unclear: Whether changes to Position Title need to be stored in state or just used for display.
   - Recommendation: Implement as editable `<input>` that updates a `positionTitle` key in the store. This persists locally for the session.

4. **Header × close button behavior**
   - What we know: × button appears top-right of occupation header card.
   - What's unclear: Should it navigate back to search (Step 1) or just hide the header?
   - Recommendation: Navigate to Step 1 — same as "Back to Search" button behavior.

---

## Sources

### Primary (HIGH confidence)
- Direct screenshot analysis: `.planning/ui-walkthrough-v5.1/screenshots/2.0 Build.png` through `2.7 Responsibilities.png` — all 8 Build screenshots read as images
- Direct codebase inspection: `templates/index.html`, `static/js/accordion.js`, `static/js/main.js`, `static/js/selection.js`, `static/js/state.js`, `static/js/profile_tabs.js`
- Direct model inspection: `src/models/noc.py`, `src/models/responses.py`
- Direct service inspection: `src/services/mapper.py`, `src/services/profile_parquet_reader.py`, `src/services/labels_loader.py`
- CSS: `static/css/main.css` — design tokens confirmed

### No External Research Required
This phase is a pure internal redesign. No third-party library APIs need verification. All icons are Font Awesome 6.5.1, which is already loaded.

---

## Metadata

**Confidence breakdown:**
- Screenshots analysis: HIGH — read directly as images
- Current codebase state: HIGH — read all key files directly
- Data field mapping: HIGH — traced from API model through mapper to frontend
- Level badge colors: MEDIUM — extracted from screenshots, exact hex approximated from visual analysis
- Core competencies sub-descriptions: LOW — contradictory signals between CONTEXT.md and screenshot

**Research date:** 2026-03-11
**Valid until:** 2026-04-11 (stable codebase — 30 days)
