# Phase 26: Global Chrome & Search — Research

**Researched:** 2026-03-11
**Domain:** Flask/Jinja2 single-page app UI redesign — CSS/HTML/JS only, no new backend
**Confidence:** HIGH (all findings from direct codebase inspection + screenshot analysis)

---

## Summary

This phase is a pure front-end redesign of an existing, working Flask single-page application. The backend is complete; Phase 26 rebuilds what users see and how they interact with it. All content already flows correctly; the job is to wrap it in new chrome and redesign the search experience.

The app lives in a single Jinja2 template (`templates/index.html`) with roughly 570 lines of HTML. Multiple CSS files (combined ~2,500+ lines) and 15 JS files handle all interactivity. The app has no Jinja2 includes/partials — it is one monolithic template file. This is the right pattern to continue: do not split into partials. The existing GC header, stepper, and footer structures already exist in the HTML and CSS; they need to be replaced/updated, not created from scratch.

The two plans in Phase 26 (26-01 Global Chrome, 26-02 Search Redesign) are independent of each other and can be worked in sequence. The chrome changes affect every visible "page" within the single template (different sections shown/hidden by JS). The search redesign replaces the welcome section and search results section markup and CSS.

**Primary recommendation:** Work from the screenshots as pixel-perfect targets. The screenshots are authoritative (from a working prototype). Every chrome element is already documented in the walkthrough. Do not invent — replicate.

---

## Standard Stack

### Core (already in project — no new installs needed)

| Library/Tool | Version | Purpose | Note |
|---|---|---|---|
| Flask + Jinja2 | 3.x | Serves `index.html` template | Single route `/` renders all |
| Font Awesome | 6.5.1 (CDN) | Icons throughout | Already in `<head>` |
| SortableJS | 1.15.0 (CDN) | Drag-and-drop (existing) | Already in `</body>` |
| Vanilla JS modules | — | All interactivity | No framework |
| CSS custom properties | — | Design tokens | Already in `:root` |

### Supporting

| Tool | Purpose | When to Use |
|---|---|---|
| CSS `position: fixed` | Right-edge Selections tab | Anchors to viewport right edge |
| CSS `position: sticky` | App bar stays on scroll | Keeps navy bar visible |
| `localStorage` | Session ID persistence | Generated once per browser session |
| `store.subscribe()` | Live selection count | Already wired — reuse for Selections tab counter |

### No new npm packages needed

The entire phase is HTML + CSS + vanilla JS changes. Do not introduce any new library or package.

---

## Architecture Patterns

### Template Structure (current)

```
templates/index.html (570 lines)
├── <head> — CSS links, meta
├── <body>
│   ├── .gc-header         — GC white header (exists, needs rework)
│   ├── .jd-stepper        — 5-step stepper (exists, needs rework)
│   ├── <main.container>
│   │   ├── #welcome-section       — REPLACE with new search UI
│   │   ├── #profile-header        — Keep, restyle
│   │   ├── #search-results        — Restyle filter panel + cards
│   │   ├── #classify-section      — Keep, restyle
│   │   ├── #profile-tabs-container — Keep, restyle
│   │   ├── #jd-sections           — Keep
│   │   ├── #overview-section      — Keep
│   │   └── #explore-section       — Remove or hide (replaced by new search UI)
│   ├── #sidebar           — REPLACE with new Selections tab
│   ├── #action-bar        — Keep (sticky bottom bar)
│   └── .gc-footer         — REPLACE with new dark footer + O*NET attribution
└── <scripts>
```

### Recommended New DOM Structure (26-01 Chrome additions)

```
<body>
  <!-- NEW: GoC identity header -->
  <header class="gc-identity-header">
    flag + "Government of Canada / Gouvernement du Canada"    right: "Français"
  </header>

  <!-- REPLACE: Dark navy app bar (was .jd-stepper nav containing stepper) -->
  <div class="app-bar">
    "JobForge" + "JD Builder 1.0" badge | left
    session-id + audit trail badge + reset | right
  </div>

  <!-- REPLACE: Data source pills row -->
  <div class="data-sources-bar">
    "Data Sources:" + 5 coloured pills (links)
  </div>

  <!-- REPLACE: 5-step stepper -->
  <nav class="process-stepper">
    1 Search > 2 Build > 3 Classify > 4 Generate > 5 Export
  </nav>

  <!-- UNCHANGED: main content -->
  <main class="container"> ... </main>

  <!-- REPLACE: compliance paragraph (above footer, in body) -->
  <div class="compliance-bar"> ... long paragraph ... </div>

  <!-- REPLACE: dark footer -->
  <footer class="app-footer">
    left: "JobForge – JD Builder 1.0 | Full Audit Trail Provenance"
    right: "Canada" wordmark
  </footer>
  <!-- O*NET attribution strip below footer -->
  <div class="onet-attribution"> O*NET logo + text </div>

  <!-- NEW: Selections right-edge tab (fixed position) -->
  <div class="selections-tab" id="selections-tab"> Selections (N) </div>
</body>
```

### Pattern: Session ID in Frontend

The current app does NOT expose Flask session ID to the frontend. The truncated session ID shown in the screenshots (e.g., `8180f55f...`) must be generated and stored client-side in `localStorage` on first load.

```javascript
// Pattern: generate once, persist in localStorage
function getOrCreateSessionId() {
    let id = localStorage.getItem('jdb_session_id');
    if (!id) {
        id = crypto.randomUUID().replace(/-/g, '').substring(0, 12);
        localStorage.setItem('jdb_session_id', id);
    }
    return id;
}
// Display: id.substring(0, 8) + '...'
```

### Pattern: Audit Trail Counter

The current app already tracks selection events. The audit trail count shown in the app bar badge is the total count of user actions (selections made, searches performed, profile loads). This can be stored in `localStorage` and incremented on each significant action.

```javascript
function incrementAuditCount() {
    const count = parseInt(localStorage.getItem('jdb_audit_count') || '0') + 1;
    localStorage.setItem('jdb_audit_count', String(count));
    document.getElementById('audit-count-badge').textContent = count;
}
```

### Pattern: Selections Tab Counter

The selections count for the right-edge tab is available from `store.getState()`. The existing `store.subscribe()` pattern is already used throughout the app and is the correct approach.

```javascript
store.subscribe((state) => {
    const total = Object.values(state.selections)
        .reduce((sum, arr) => sum + arr.length, 0);
    document.getElementById('selections-count').textContent = total;
});
```

### Pattern: Right-Edge Fixed Vertical Tab

The "Selections (N)" tab is a fixed-position element on the right edge, rotated text. The existing `#sidebar` element uses a `collapsed`/`open` class toggle — the new Selections tab replaces this interaction point.

```css
.selections-tab {
    position: fixed;
    right: 0;
    top: 50%;
    transform: translateY(-50%) rotate(90deg);  /* vertical text */
    transform-origin: right center;
    background: #26374a; /* dark navy */
    color: white;
    padding: 0.75rem 1.5rem;
    cursor: pointer;
    z-index: 200;
    border-radius: 4px 4px 0 0;
    /* Note: rotate requires careful positioning — see gotchas */
}
```

**Important gotcha:** Using `transform: rotate(90deg)` on a fixed element requires adjustment of the `right`/`top` values because the rotation pivot changes the element's layout box. Use `writing-mode: vertical-rl` instead — it avoids transform gotchas:

```css
.selections-tab {
    position: fixed;
    right: 0;
    top: 50%;
    transform: translateY(-50%);
    writing-mode: vertical-rl;
    text-orientation: mixed;
    background: #26374a;
    color: white;
    padding: 1rem 0.5rem;
    cursor: pointer;
    z-index: 200;
    border-radius: 4px 0 0 4px;
}
```

### Anti-Patterns to Avoid

- **Do not split index.html into Jinja2 includes**: This is a single-page JS app. Splitting into `{% include %}` partials would require Flask restarts to test changes and adds no value. Keep one template file.
- **Do not introduce a CSS framework** (Bootstrap, Tailwind): The existing CSS is custom and coherent. Adding a framework causes class conflicts and doubles bundle size.
- **Do not add `position: fixed` to the app bar without testing scroll**: The stepper and app bar together will push content down. The app bar should be `position: sticky` (not fixed) to avoid overlapping content.
- **Do not create a new `filterModule` from scratch**: The existing `filterModule` in `filters.js` handles the Occupational Category filter. Phase 26 needs to ADD 5 more filter sections (OCHRO Job Architecture, CAF Careers, NOC TEER, Occupational Groups, O*NET SOC) while keeping the existing one.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---|---|---|---|
| Session UUID generation | Custom entropy function | `crypto.randomUUID()` | Available in all modern browsers, zero deps |
| Icon rotation for vertical tab | CSS transform matrix math | `writing-mode: vertical-rl` | Cleaner, no pixel-pushing |
| Audit trail persistence | IndexedDB or server session | `localStorage` counter | Matches existing storage.js pattern |
| Data source pill colours | New colour system | Hardcode per pill (5 pills, fixed) | No dynamic theming needed |
| Keyword highlighting in "Also known as" | regex replace on DOM | innerHTML with `<strong>` wrap | Sufficient for this use case |

---

## Common Pitfalls

### Pitfall 1: Stepper Step Labels Mismatch

**What goes wrong:** The current stepper in `index.html` has steps labelled "Search", "Select Profile", "Build JD", "Export", "Classify" (in that order). The v5.1 design requires "Search", "Build", "Classify", "Generate", "Export" (in that order with different labels).

**Why it happens:** The current stepper was built at an earlier milestone with different step numbering. The `initStepper()` function in `main.js` hardcodes `step === 5` for Classify.

**How to avoid:** When replacing the stepper HTML, update the step numbers and labels, then update `initStepper()` in `main.js` to reflect the new step mapping: 1=Search, 2=Build, 3=Classify, 4=Generate, 5=Export. The `navigateToStep()` switch statement needs to be updated alongside the HTML.

**Warning signs:** If `case 5:` in `navigateToStep()` shows the Classify section but the stepper label says "Classify" is step 3, the steps are mismatched.

### Pitfall 2: Existing Sidebar vs New Selections Tab

**What goes wrong:** The existing `#sidebar` element (right-side collapsible panel) and the new "Selections (N)" vertical tab serve the same purpose. If both exist, they conflict visually and functionally.

**Why it happens:** Phase 26 introduces a new UX pattern (fixed vertical tab) for what the sidebar previously did.

**How to avoid:** The right approach is to repurpose the sidebar: hide the old sidebar toggle button, add the new fixed vertical tab as a separate element, and make the tab's click event open/close the same `#sidebar` panel. This avoids rewriting all the sidebar JS (which subscribes to state, renders selections, etc.).

**Implementation pattern:**
```html
<!-- Keep #sidebar element, just restyle it -->
<aside id="sidebar" class="sidebar collapsed">
    <div class="sidebar-content"> ... </div>
</aside>

<!-- Add new trigger (fixed tab) -->
<button class="selections-tab" id="selections-tab-btn"
        onclick="document.getElementById('sidebar').classList.toggle('open')">
    <span id="selections-count">0</span>
    Selections
</button>
```

### Pitfall 3: Filter Panel — Data Not Available for 5 of 6 Accordion Sections

**What goes wrong:** The design requires 6 accordion filter sections. The current search API only returns data sufficient for 1 of them (Occupational Category, derived from NOC code digits). The other 5 sections (OCHRO Job Architecture, CAF Careers, NOC TEER, Occupational Groups, O*NET SOC) require data that is NOT currently in `EnrichedSearchResult`.

**What IS available in search results** (from `EnrichedSearchResult` model):
- `noc_code` — 5-digit code
- `title` — occupation title
- `lead_statement` — lead statement text
- `broad_category` — first digit (0-9)
- `broad_category_name` — e.g. "Natural and Applied Sciences"
- `sub_major_group` — first 3 digits
- `unit_group` — first 4 digits
- `relevance_score` — 50/80/90/95/100
- `match_reason` — string like "Title contains 'web developer'"

**What is NOT available** (would require parquet enrichment or backend changes):
- `teer_level` — not in current search results (TEER 0-5)
- `ochro_job_family` — not in search results
- `caf_careers_category` — not in search results
- `occupational_group` — not in search results
- `onet_soc_category` — not in search results

**How to avoid:** The v5.1 design shows filters with "No results" state for OCHRO and CAF when nothing matches. For Phase 26, render all 6 accordion sections but only POPULATE the ones where data exists. Show "No results" (matching the screenshot) for OCHRO Job Architecture and CAF Careers always. For NOC TEER: derive from the first digit of the 5-digit NOC code (TEER is the second digit — e.g. code `21234` → TEER 1). For Occupational Groups and O*NET SOC: show "No results" unless the parquet data provides it.

**TEER derivation from NOC code:**
```javascript
// TEER is the second digit of the 5-digit NOC code
// e.g., 21234 → TEER 1 (digit at index 1)
function getTeer(nocCode) {
    const code = String(nocCode).replace('.', '');
    if (code.length >= 2) return parseInt(code[1]);
    return null;
}
const TEER_LABELS = {
    0: 'TEER 0 - Management',
    1: 'TEER 1 - University degree',
    2: 'TEER 2 - College/apprenticeship',
    3: 'TEER 3 - College/secondary school',
    4: 'TEER 4 - Secondary school',
    5: 'TEER 5 - No formal credentials'
};
```

### Pitfall 4: GoC Header — The MENU Nav Bar

**What goes wrong:** The current GC header has a dark navy MENU nav bar below the white flag/title row. The v5.1 screenshots show NO MENU nav bar. The dark navy bar is the JobForge app bar, not a GC MENU bar.

**Why it happens:** The current template follows a Canada.ca CDTS pattern with a MENU bar, but the design target removes this and replaces it with the JobForge app bar.

**How to avoid:** Remove the `<nav class="gc-header__nav">` element (the MENU button row). Replace it with a new `.app-bar` div that contains the JobForge brand, session ID, audit trail badge, and reset button.

### Pitfall 5: Match Badge Pills in Result Cards

**What goes wrong:** The v5.1 design shows coloured match badge pills (e.g., "O*NET SOC", "100% - All keywords in title", "Bright Outlook") but the current `EnrichedSearchResult` has only `relevance_score` (int) and `match_reason` (string). There is no `source` field (O*NET SOC vs NOC vs OaSIS) in the search result.

**Why it happens:** The parquet search searches all taxonomies together and returns a single merged score. Source attribution per result is not currently tracked.

**How to avoid:** For Phase 26, construct the source badge from the NOC code itself (all parquet results come from the NOC/OaSIS taxonomy). The "O*NET SOC" badge visible in the screenshots is because those are O*NET-based occupations — derive this from the `match_reason` text or add a `source` field to `EnrichedSearchResult`. The simplest approach is to add a `source_label` field that defaults to `"O*NET SOC"` for parquet results (since the parquet uses O*NET-mapped occupations) and is set per the match tier.

### Pitfall 6: `also_known_as` / Example Titles for "Also known as:" line

**What goes wrong:** The design requires an "Also known as:" line with matched keywords highlighted in bold. Current `EnrichedSearchResult` has `example_titles: Optional[str]` but this field is `None` for parquet search results (the model accepts it but `SearchParquetReader._build_result()` never populates it).

**Why it happens:** Example titles come from the `element_example_titles.parquet` file (loaded by `SearchParquetReader`) but were not included in the result objects for Phase 23.

**How to avoid:** Modify `SearchParquetReader._build_result()` to populate `example_titles` by looking up the job titles from `titles_df` for the matching `unit_group_id`. The data exists in the parquet — it just isn't being put into the result object. This is a small backend change needed to support the "Also known as:" display.

### Pitfall 7: Data Sources Pills — Hardcoded Colours

**What goes wrong:** The five data source pills must have specific colours (confirmed from screenshots):
- 2021 NOC: grey/dark
- CAF Careers: green
- OCHRO Job Architecture: orange
- O*NET SOC: green/blue
- OaSIS: purple/blue

**The walkthrough text says:** "2021 NOC (grey), CAF Careers (green), OCHRO Job Architecture (orange), O*NET SOC (blue), OaSIS (purple/blue)"

**Screenshot inspection reveals:**
- 2021 NOC: dark grey (`#555` or similar)
- CAF Careers: green (`#28a745` or similar)
- OCHRO Job Architecture: orange (`#fd7e14` or similar)
- O*NET SOC: teal/green (`#17a2b8` or similar)
- OaSIS: purple (`#6f42c1` or similar)

**How to avoid:** Hardcode these 5 colours as CSS classes, not as dynamic values. They never change.

---

## Code Examples

### GoC Identity Header (verified from screenshot)

```html
<!-- Source: screenshot 1.0 Home_Page.png + index.html existing pattern -->
<header class="gc-identity-header">
    <div class="container gc-identity-header__inner">
        <div class="gc-identity-header__brand">
            <!-- Canadian flag: use existing .gc-flag CSS classes -->
            <div class="gc-flag">
                <div class="gc-flag__red"></div>
                <div class="gc-flag__white"><span class="gc-flag__leaf">&#127809;</span></div>
                <div class="gc-flag__red"></div>
            </div>
            <div class="gc-identity-header__titles">
                <span class="gc-identity-header__en">Government of Canada</span>
                <span class="gc-identity-header__fr">Gouvernement du Canada</span>
            </div>
        </div>
        <div class="gc-identity-header__lang">
            <a href="#" lang="fr" hreflang="fr" class="gc-lang-toggle">Français</a>
        </div>
    </div>
</header>
```

### Dark Navy App Bar

```html
<!-- Source: screenshot analysis — dark navy (#26374a) bar -->
<div class="app-bar">
    <div class="container app-bar__inner">
        <div class="app-bar__brand">
            <span class="app-bar__name">JobForge</span>
            <span class="app-bar__badge">JD Builder 1.0</span>
            <span class="app-bar__byline">Job Description Builder with Full Audit Trail Provenance</span>
        </div>
        <div class="app-bar__actions">
            <span class="app-bar__session">
                <i class="fas fa-fingerprint"></i>
                <span id="session-id-display">8180f55f...</span>
            </span>
            <span class="app-bar__separator">|</span>
            <button class="app-bar__audit-btn" id="audit-trail-btn">
                <i class="fas fa-clipboard-list"></i>
                Audit Trail
                <span class="app-bar__audit-count" id="audit-count">1</span>
            </button>
            <span class="app-bar__separator">|</span>
            <button class="app-bar__reset-btn" id="reset-btn">
                <i class="fas fa-redo"></i>
                Reset
            </button>
        </div>
    </div>
</div>
```

### Data Source Pills

```html
<!-- Source: screenshots + requirements CHROME-03 -->
<div class="data-sources-bar">
    <div class="container data-sources-bar__inner">
        <span class="data-sources-bar__label">Data Sources:</span>
        <a href="https://noc.esdc.gc.ca/" target="_blank" rel="noopener" class="source-pill source-pill--noc">2021 NOC</a>
        <a href="https://www.canada.ca/en/department-national-defence/services/caf-jobs.html" target="_blank" rel="noopener" class="source-pill source-pill--caf">CAF Careers</a>
        <a href="https://www.tbs-sct.canada.ca/tbsf-fsct/350-79-eng.asp" target="_blank" rel="noopener" class="source-pill source-pill--ochro">OCHRO Job Architecture</a>
        <a href="https://www.onetonline.org/" target="_blank" rel="noopener" class="source-pill source-pill--onet">O*NET SOC</a>
        <a href="https://noc.esdc.gc.ca/OaSIS/welcome" target="_blank" rel="noopener" class="source-pill source-pill--oasis">OaSIS</a>
    </div>
</div>
```

### Process Stepper

```html
<!-- Source: screenshots — pill-style stepper with > separators -->
<nav class="process-stepper" id="process-stepper" aria-label="Job description workflow">
    <div class="container process-stepper__inner">
        <ol class="process-stepper__steps">
            <li class="process-stepper__step process-stepper__step--active" data-step="1">
                <button class="process-stepper__btn" data-step="1">
                    <span class="process-stepper__num">1</span>
                    <span class="process-stepper__label">Search</span>
                </button>
            </li>
            <li class="process-stepper__sep" aria-hidden="true">&#62;</li>
            <li class="process-stepper__step" data-step="2">
                <button class="process-stepper__btn" data-step="2">
                    <span class="process-stepper__num">2</span>
                    <span class="process-stepper__label">Build</span>
                </button>
            </li>
            <!-- repeat for Classify (3), Generate (4), Export (5) -->
        </ol>
    </div>
</nav>
```

### Search Page "Find your Job" Empty State

```html
<!-- Source: screenshot 1.0 Home_Page.png, requirements SRCH-01 SRCH-02 -->
<section id="search-section" class="search-section">
    <div class="container">
        <h1 class="search-heading">Find your Job</h1>
        <p class="search-subtitle">Search across 2500+ occupations with full provenance</p>

        <div class="match-quality-legend">
            <span class="mq-label"><i class="fas fa-info-circle"></i> Match Quality:</span>
            <span class="mq-pill mq-pill--green">95-100% Title</span>
            <span class="mq-pill mq-pill--blue">85% Description</span>
            <span class="mq-pill mq-pill--grey">75% Related</span>
        </div>

        <div class="search-input-wrapper">
            <input type="search" id="search-input"
                   placeholder="Search by job title, keyword, or NOC code..."
                   class="search-input-field">
        </div>

        <p class="search-source-link">
            <i class="fas fa-layer-group"></i>
            <a href="#" class="search-source-link__link">Source: JobForge WiQ | All job taxonomies</a>
        </p>

        <!-- Empty state (shown when no query) -->
        <div id="search-empty-state" class="search-empty-state">
            <i class="fas fa-search search-empty-state__icon"></i>
            <p class="search-empty-state__text">Start typing to search across all job taxonomies</p>
            <p class="search-empty-state__compliance">
                <em>All queries logged per TBS Directive on Automated Decision-Making and assessed
                using the Algorithmic Impact Assessment</em>
            </p>
        </div>

        <!-- Results area (shown after search) -->
        <div id="search-results-area" class="search-results-area hidden">
            <!-- results header bar -->
            <div class="results-header">
                <span id="results-count-label">6 results (filtered)</span>
                <button id="new-search-btn" class="btn-new-search">+ New Search</button>
                <span class="results-meta-line">Published: 2024-11-15 | Data Steward: ESDC</span>
            </div>
            <!-- two-column layout: filter panel + cards -->
            <div class="results-layout">
                <aside id="filter-panel" class="filter-panel">
                    <!-- filter accordions -->
                </aside>
                <div id="results-list" class="results-cards-container"></div>
            </div>
        </div>
    </div>
</section>
```

### v5.1 Result Card

```html
<!-- Source: screenshot 1.1 Search Results.png, requirements SRCH-04 -->
<div class="result-card" data-code="21300">
    <div class="result-card__header">
        <i class="fas fa-laptop-code result-card__icon"></i>
        <span class="result-card__title">Web Developers</span>
    </div>
    <div class="result-card__badges">
        <span class="badge badge--source">O*NET SOC</span>
        <span class="badge badge--score badge--green">100% - All keywords in title</span>
        <span class="badge badge--outlook">Bright Outlook</span>
    </div>
    <p class="result-card__aka">
        <strong>Also known as:</strong>
        <em><strong>Web</strong> Architect, <strong>Web</strong> Design Specialist,
        <strong>Web</strong> <strong>Developer</strong></em>
    </p>
    <p class="result-card__description">
        Develop and implement websites, web applications...
    </p>
</div>
```

### Compliance Framework Paragraph

```html
<!-- Source: screenshot 1.0 Home_Page.png, requirements CHROME-06 -->
<div class="compliance-bar">
    <div class="container">
        <p class="compliance-text">
            <strong>Compliance Framework:</strong> JobForge data management complies with
            <em>DAMA DMBOK 2.0</em> and the <em>GC Data Quality Management Framework</em>.
            AI policy complies with the <em>TBS Directive on Automated Decision-Making</em>
            and the <em>Algorithmic Impact Assessment</em>. Design complies with the
            <em>Policy on Service and Digital</em> and the <em>MISO HAPIE GSD Framework</em>.
            Classification complies with the <em>Directive on Classification</em> and the
            <em>Guide to Allocating Positions</em>. Performance complies with the
            <em>Policy on Results</em> and <em>PuMP Performance Measurement</em>.
            Authoritative sources: 2021 NOC (ESDC), O*NET SOC, CAF Careers,
            TBS Occupational Groups, OCHRO Job Architecture.
        </p>
    </div>
</div>
```

### Dark Footer

```html
<!-- Source: screenshot 1.0 Home_Page.png, requirements CHROME-07 -->
<footer class="app-footer">
    <div class="container app-footer__inner">
        <span class="app-footer__left">JobForge — JD Builder 1.0 | Full Audit Trail Provenance</span>
        <span class="app-footer__right">
            <strong class="app-footer__canada">Canada</strong>
            <span class="app-footer__flag">&#127809;</span>
        </span>
    </div>
</footer>
<div class="onet-attribution">
    <div class="container onet-attribution__inner">
        <!-- O*NET logo (inline or img) -->
        <span class="onet-attribution__text">
            This site incorporates information from
            <a href="https://www.onetonline.org/" target="_blank" rel="noopener">O*NET Web Services</a>
            by the U.S. Department of Labor, Employment and Training Administration (USDOL/ETA).
            O*NET® is a trademark of USDOL/ETA.
        </span>
    </div>
</div>
```

---

## Key Design Tokens (from screenshot analysis)

```css
:root {
    /* Chrome colours */
    --app-bar-bg: #26374a;         /* dark navy — app bar, profile header card */
    --app-bar-text: #ffffff;
    --app-bar-badge-bg: #4a6fa5;   /* lighter navy for "JD Builder 1.0" badge */

    /* Data source pill colours */
    --pill-noc-bg: #555555;        /* grey */
    --pill-noc-text: #ffffff;
    --pill-caf-bg: #28a745;        /* green */
    --pill-caf-text: #ffffff;
    --pill-ochro-bg: #fd7e14;      /* orange */
    --pill-ochro-text: #ffffff;
    --pill-onet-bg: #17a2b8;       /* teal/blue-green */
    --pill-onet-text: #ffffff;
    --pill-oasis-bg: #6f42c1;      /* purple */
    --pill-oasis-text: #ffffff;

    /* Match quality badge colours */
    --badge-green-bg: #d4edda;
    --badge-green-text: #155724;
    --badge-blue-bg: #cce5ff;
    --badge-blue-text: #004085;
    --badge-grey-bg: #e2e3e5;
    --badge-grey-text: #383d41;

    /* Stepper colours */
    --stepper-active-bg: #26374a;
    --stepper-inactive-bg: #e0e0e0;
    --stepper-completed-bg: #28a745;

    /* Footer */
    --footer-bg: #26374a;          /* same dark navy as app bar */
    --footer-text: #ffffff;
}
```

---

## State of the Art

| Old Approach (current v5.0) | New Approach (v5.1 target) | Impact |
|---|---|---|
| White GC header with MENU nav bar | White GoC identity strip (flag + bilingual name + Français only) | Remove MENU nav entirely |
| No app bar / no brand bar | Dark navy JobForge app bar with session ID + audit + reset | New DOM element |
| No data source pills row | Coloured pills row below app bar | New DOM element |
| Stepper embedded in old nav | New pill-style stepper as separate nav | Replace stepper HTML + update JS step mapping |
| Welcome section with search in it | Standalone "Find your Job" page (always visible as Step 1 default) | Replace #welcome-section |
| Single occupational category filter | 6 accordion filter sections (most show "No results" initially) | Extend filterModule |
| Old card format: header/rows/footer | New card: icon + title + badge pills + aka + description | Replace renderCardView() |
| Right-side collapsible sidebar | Fixed vertical "Selections (N)" tab on right edge | Repurpose sidebar, add new tab trigger |
| Light GC footer with links | Dark navy footer with Canada wordmark + O*NET attribution | Replace footer HTML+CSS |
| No compliance paragraph | Compliance paragraph above footer | New DOM element |

---

## Open Questions

1. **O*NET SOC filter data source**
   - What we know: The parquet contains `element_labels.parquet` with NOC codes. O*NET SOC categories (Computer & Mathematical, Business & Financial, etc.) are NOT in `EnrichedSearchResult`.
   - What's unclear: Does any parquet file contain an O*NET SOC major group field? The `_build_result()` method does not populate it.
   - Recommendation: Show O*NET SOC accordion section with "No results" for Phase 26. Defer actual O*NET filtering to a later phase when the parquet mapping is enriched.

2. **OCHRO Job Architecture and CAF Careers filter data**
   - What we know: Screenshots show these sections collapsed with "No Job Architecture results" and "No CAF results" text.
   - What's unclear: Is this the intended behavior for Phase 26, or is there existing parquet data for these?
   - Recommendation: Render both sections but always show "No results" text (matching screenshots exactly). This is correct behavior for the current data.

3. **Session ID scope: browser vs Flask session**
   - What we know: Flask session exists (`app.secret_key` is set). The session ID shown in the app bar appears to be the first 8 chars of a UUID-like value.
   - What's unclear: Should the Session ID exposed in the UI be the Flask server-side session cookie ID, or a client-generated ID stored in localStorage?
   - Recommendation: Use client-generated UUID in localStorage. This is simpler, requires no backend changes, and the session ID's purpose is display/audit only (not security).

4. **Audit Trail click behavior (CHROME-08 scope)**
   - What we know: CHROME-08 says Français toggle and "View Provenance Graph" are cosmetic-only. The requirements say "Audit Trail badge" is in CHROME-02 but CHROME-08 does not list it as cosmetic.
   - What's unclear: Does clicking the Audit Trail badge open anything in Phase 26?
   - Recommendation: Make the Audit Trail badge cosmetic-only in Phase 26 (render the count but clicking does nothing). The walkthrough does not show a clicked state for this element.

5. **`also_known_as` / example titles backend change**
   - What we know: `SearchParquetReader` loads `element_example_titles.parquet` and uses it for T4 scoring, but the titles are NOT included in the `EnrichedSearchResult` objects returned from search.
   - What's unclear: This requires a 2-line change in `search_parquet_reader.py` (`_build_result()`) to populate `example_titles`.
   - Recommendation: Plan 26-02 must include a small backend task: "populate example_titles in SearchParquetReader._build_result() from titles_df lookup." This is a 10-line change; do not defer it as it is required for the SRCH-04 "Also known as:" card element.

---

## Sources

### Primary (HIGH confidence)

- Direct inspection of `templates/index.html` (570 lines) — current template structure
- Direct inspection of `static/css/main.css` (2,201 lines) — all current CSS variables and patterns
- Direct inspection of `static/css/filters.css` — filter panel CSS
- Direct inspection of `static/css/results-cards.css` — card CSS
- Direct inspection of `static/js/main.js` — stepper logic, search render, handleSearch
- Direct inspection of `static/js/filters.js` — filterModule implementation
- Direct inspection of `static/js/sidebar.js` — sidebar/selections pattern
- Direct inspection of `static/js/state.js` — store pattern, localStorage
- Direct inspection of `static/js/selection.js` — audit trail timestamp pattern
- Direct inspection of `src/routes/api.py` — search endpoint, EnrichedSearchResult fields returned
- Direct inspection of `src/models/noc.py` — EnrichedSearchResult data model
- Direct inspection of `src/services/search_parquet_reader.py` — what fields are populated
- Direct inspection of `src/app.py` — Flask session setup
- Screenshot analysis: `1.0 Home_Page.png` — chrome layout, colours, typography
- Screenshot analysis: `1.1 Search Results.png` — filter panel, result cards, results header
- Screenshot analysis: `2.0 Build.png` — profile header card, tabs, bottom nav
- Screenshot analysis: `2.9 Selections drawer.png` — selections drawer layout and content
- `.planning/ui-walkthrough-v5.1/walkthrough.md` — written design spec

### Tertiary (LOW confidence — not verified against external sources)

- Specific hex colour values for data source pills: inferred from screenshot visual inspection. The exact hex values should be confirmed against the screenshots before committing to CSS. The screenshot colours are JPEG-compressed so exact values may differ slightly.

---

## Metadata

**Confidence breakdown:**
- Current template structure: HIGH — directly read the file
- Current CSS architecture: HIGH — directly read all CSS files
- Search API response shape: HIGH — directly read models and route
- Session ID mechanism: HIGH — directly read app.py and state.js
- Filter panel data availability: HIGH — directly read EnrichedSearchResult model
- Design tokens/colours: MEDIUM — inferred from JPEG screenshots (may be ±5 hex)
- Right-edge vertical tab CSS pattern: HIGH — standard CSS, writing-mode well-supported
- Stepper step renumbering impact: HIGH — read initStepper() in full

**Research date:** 2026-03-11
**Valid until:** 2026-04-11 (stable codebase — valid for 30 days)
