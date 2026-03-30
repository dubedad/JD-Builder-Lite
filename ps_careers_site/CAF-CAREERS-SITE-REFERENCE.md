# CAF Careers Site — Software Analysis Reference

> **Source:** https://forces.ca/en/careers/
> **Analyzed:** 2026-03-13 via Chrome DevTools on live production site
> **Purpose:** Reference document for Claude Code to build the DND Civilian Workforce careers site as a structural mirror of the CAF site

---

## 1. Site Architecture Overview

### 1.1 Page Hierarchy

```
L0  forces.ca/en/                          → Homepage
L1  forces.ca/en/careers                   → Browse Careers (category card grid)
L2  (no separate URL — filter applies)     → Category filter (same-page JS filter)
L3  forces.ca/en/career/{slug}/            → Career Detail (tabbed content page)
```

**Key finding:** The CAF site does NOT have separate category pages. Clicking a Job Family card applies a JS filter on the same `/en/careers` page. The detail pages are at `/en/career/{slug}/`.

### 1.2 Technology Stack

| Component | Value |
|-----------|-------|
| Framework | Custom (no Vue, React, Angular, or Nuxt detected) |
| CSS framework | Bootstrap 4 (grid classes: `row`, `col-lg-3`, `col-md-4`) |
| Fonts | **Exo 2** (headings) + **Roboto** (body) via Google Fonts |
| Icons | Font Awesome (SVG inline, e.g., `fa-filter`) |
| Rendering | Server-rendered HTML, JS-enhanced interactivity |
| Image format | JPEG for card backgrounds, SVG for icons/logos |

### 1.3 Font Strategy

| Context | Font Family | Weights Used |
|---------|-------------|-------------|
| Body text, buttons, links | `Roboto, sans-serif` | 400, 500 |
| Headings (h1-h4), banner, card titles, footer headings | `"Exo 2", sans-serif` | 100, 400, 600 |

---

## 2. L1 — Browse Careers Page

**URL:** `https://forces.ca/en/careers`

### 2.1 Page Structure (DOM)

```
<body>
  <a class="sr-only">                           ← Skip link
  <nav class="navbar sticky-top">               ← Global header (58px)
  <main class="main">
    <div>                                        ← Spacer
    <div class="d-none">                         ← Hidden mobile content
    <div>                                        ← Main content wrapper (1444px)
      <section class="banner banner-primary">    ← Hero banner (306px)
        <div class="banner-content pt-5">        ← Inner content
      <section>                                  ← Browse strip + card grid
        <div class="row">                        ← Browse header row
        <div class="row m-0 pb-4">               ← Card grid (flex wrap)
          <div class="category-card col-lg-3">   ← Card column (×12)
            <div class="category-card-inner">    ← Card visual
  <footer class="base-foot pt-5 pb-3">          ← Footer (569px)
```

### 2.2 Global Navigation (`<nav>`)

```
Height:        58px
Position:      sticky (top: 0, z-index: 1020)
Background:    transparent (rgba(0,0,0,0))
```

**Left side:**
- GC FIP signature: `GovofCanadaSIG_CanadaWordmark-11.svg` (300×30, white version)
  - URL: `forces.ca/assets/images/SVG/GovofCanadaSIG_CanadaWordmark-11.svg`
  - Dark version: `GovofCanadaSIG_CanadaWordmark-08.svg`
- Canadian flag mini: `can-flag-mini.png` (43×22)

**Right side (items in order):**
1. Search icon (magnifying glass)
2. "Apply Now" link → `/en/apply-now/`
3. "Browse Careers" link → `/en/careers`
4. "FR" language toggle → `/fr/carrieres`
5. Hamburger "MENU" button

**Breadcrumb sub-nav (within navbar):**
- Home → Careers (bold/active)
- Background: implied via navbar structure
- Font: 13px, white on dark

### 2.3 Hero Banner

```css
.banner.banner-primary {
    height:              306px;
    background-image:    url("browse-header-2-2000w.9a1738f9.jpg");
    background-size:     cover;
    background-position: 0px 50%;
    padding:             0px 0px 16px;
}
```

**Asset:** `forces.ca/build/images/browse-header-2-2000w.9a1738f9.jpg` — dark helicopter scene

**Inner content (`.banner-content.pt-5`):**

| Element | CSS |
|---------|-----|
| Career icon | `icon-career.43c3227f.svg`, 60×60px, centered |
| Subtitle "The Canadian Armed Forces" | `"Exo 2"`, 16px, weight 100, white, letter-spacing 0.64px, uppercase |
| Heading "BROWSE CAREERS" | `"Exo 2"`, **42px**, weight **600**, white, letter-spacing **2.4px**, uppercase |

### 2.4 Search Bar

The search bar is an `input-group` (Bootstrap):

```
┌─────────────────────────────────────────────────┐ ┌──────────────────────┐
│ 🔍 │ Search for careers...                       │ │ ≡ FILTER CAREERS ≫≫  │
└─────────────────────────────────────────────────┘ └──────────────────────┘
```

**Search input:**

```css
input {
    width:            ~520px (flexible within input-group);
    height:           56px;
    font-size:        16px;
    background-color: rgb(255, 255, 255);  /* white */
    color:            rgb(73, 80, 87);     /* dark gray text */
    border:           none (inherited from input-group);
    padding:          6px 12px;
    border-radius:    0px;
}
input::placeholder { color: #999; }
```

**Search icon prepend:**
- SVG magnifying glass, fill `#666`
- Inside `.input-group-prepend.form-control`
- Background: white (same as input)

**Filter Careers button:**

```css
button {
    font-size:        16px;
    font-weight:      500;
    color:            rgb(245, 245, 245);
    background:       transparent;
    border:           none;
    text-transform:   uppercase;
    letter-spacing:   2.4px;
}
```

**Filter button contents:**
1. Font Awesome filter/funnel SVG (`fa-filter`), fill: `currentColor` (gray-white)
2. Text: "FILTER CAREERS"
3. Double chevron SVG (gold/amber colored: `#C8A835`)

### 2.5 Browse Strip

```
┌─────────────────────────────────────────────────────────────────┐
│ Browse careers based on your area of interest.   [BROWSE ALL]   │
└─────────────────────────────────────────────────────────────────┘
```

**Row:** `.col` layout inside `.row`
**Heading:** `<h2>`, italic-styled, "Browse careers based on your area of interest."
**Button:** "Browse All Careers"

```css
.browse-all-btn {
    font-size:    12.8px;
    font-weight:  500;
    color:        rgb(38, 38, 38);
    background:   transparent;
    border:       1.33px solid rgb(133, 130, 130);
    padding:      4.8px 12px;
}
```

### 2.6 Card Grid

**Grid container:**
```css
.row.m-0.pb-4 {
    display:    flex;
    flex-wrap:  wrap;
    width:      100%;          /* FULL VIEWPORT WIDTH — no max-width */
    padding:    0 0 24px 0;
    margin:     0;
}
```

**Card column:**
```css
.category-card.col-lg-3.col-md-4.pl-0.pb-3 {
    width:          25%;       /* at lg breakpoint */
    max-width:      25%;
    padding-left:   0;
    padding-bottom: 16px;      /* pb-3 = 16px = vertical gap */
    /* No horizontal gap — cards are edge-to-edge within columns */
}
```

**Card inner (the visual card):**
```css
.category-card-inner.darkContent.box-shadow.p-3 {
    height:           300px;
    display:          flex;
    flex-direction:   column;
    justify-content:  flex-end;
    padding:          16px;
    border-radius:    0px;
    background-image: linear-gradient(rgba(0,0,0,0.25)),
                      linear-gradient(
                          rgba(0,0,0,0) 0%,
                          rgba(0,0,0,0) 30%,
                          rgba(0,0,0,0.5) 65%,
                          rgba(0,0,0,0.9) 100%
                      ),
                      url("category-image.jpg");
    background-size:  cover;
    background-position: center;
    box-shadow:       0 3px 5px -1px rgba(0,0,0,.1),
                      0 6px 10px 0 rgba(0,0,0,.07),
                      0 1px 18px 0 rgba(0,0,0,.08);
}
```

**Overlay technique:** Three-layer `background-image`:
1. Flat darken: `linear-gradient(rgba(0,0,0,0.25))` — uniform 25% darkening
2. Bottom fade: `linear-gradient(transparent → transparent → 0.5 → 0.9)` — readability gradient
3. Photo: `url("image.jpg")`

**Card title:**
```css
.category-card-inner h3.mb-3 {
    font-family:    "Exo 2", sans-serif;
    font-size:      23.2px;
    font-weight:    600;
    color:          rgb(245, 245, 245);
    line-height:    27.84px;
    margin-bottom:  16px;
    text-transform: none;
}
```

**"VIEW CAREERS" button:**
```css
.call-to-action-btn {
    font-family:    Roboto, sans-serif;
    font-size:      16px;
    font-weight:    500;
    color:          rgb(245, 245, 245);
    background:     transparent;
    border:         1.33px solid rgb(245, 245, 245);
    padding:        6.53px 30.4px;
    text-transform: uppercase;
    letter-spacing: 2.4px;
    border-radius:  0px;
}
```

### 2.7 CAF Job Categories (12 cards)

| # | Title | Image URL |
|---|-------|-----------|
| 1 | Transport & Logistics | `forces.ca/assets/images/index/category-imgs/transport.jpg` |
| 2 | Naval Operations | `forces.ca/assets/images/index/category-imgs/naval.jpg` |
| 3 | Aviation | `forces.ca/assets/images/index/category-imgs/aviation.jpg` |
| 4 | Health Care | `forces.ca/assets/images/index/category-imgs/health.jpg` |
| 5 | Combat Operations | `forces.ca/assets/images/index/category-imgs/combat.jpg` |
| 6 | Computing & intelligence | `forces.ca/assets/images/index/category-imgs/computing.jpg` |
| 7 | Safety & Emergency Services | `forces.ca/assets/images/index/category-imgs/safety.jpg` |
| 8 | Engineering & Infrastructure | `forces.ca/assets/images/index/category-imgs/engineering.jpg` |
| 9 | Administration | `forces.ca/assets/images/index/category-imgs/administration.jpg` |
| 10 | Hospitality & Support | `forces.ca/assets/images/index/category-imgs/hospitality.jpg` |
| 11 | Public Relations | `forces.ca/assets/images/index/category-imgs/public-relations.jpg` |
| 12 | Equipment & Vehicle Maintenance | `forces.ca/assets/images/index/category-imgs/vehicle-maintenance.jpg` |

**Image URL pattern:** `forces.ca/assets/images/index/category-imgs/{slug}.jpg`

### 2.8 Filter System

The filter dialog overlays the card grid (modal/dialog pattern). Clicking a category card or "FILTER CAREERS" opens it.

**Filter sections:**
1. **Incentives** (checkboxes): Priority Application Processing, Signing Bonus, Recruiting Allowance, Accelerated Pay Increment
2. **Category** (radio buttons): Same 12 categories as cards
3. **Environment** (checkboxes): Navy, Army, Air Force
4. **Hours** (checkboxes): Full-time, Part-time
5. **Paid Education** (checkboxes): College/University (NCMSTEP), University (ROTP), University Undergraduate/Graduate
6. **Minimum Required Education** (checkboxes): Graduate Degree, Bachelor Degree, College Degree, High School, Grade 10

**Filter buttons:** "Clear All" + "Close"

---

## 3. L3 — Career Detail Page

**URL pattern:** `https://forces.ca/en/career/{slug}/`
**Example:** `https://forces.ca/en/career/cook/`

### 3.1 Page Structure

```
<nav class="navbar sticky-top">              ← Same global nav
<main>
  <article>
    <header>                                  ← Career title + badges + Apply CTA
      <h1>Cook</h1>                           ← 26px, weight 600, "Exo 2"
      <badges>                                ← "Signing Bonus", "Accelerated Pay" etc
      <a>Apply Now</a>                        ← CTA button
    <nav>                                     ← Tab anchor nav (51px)
      <a href="#sec-overview">Overview</a>
      <a href="#sec-training">Training</a>
      <a href="#sec-entry">Entry plans</a>
      <a href="#sec-parttime">Part time options</a>
      <a href="#sec-related">Related Careers</a>
    <section id="sec-overview">               ← Overview content
    <section id="sec-training">               ← Training content
    <section id="sec-entry">                  ← Entry plans content
    <section id="sec-parttime">               ← Part-time options
    <section id="sec-related">                ← Related careers
<footer>
```

### 3.2 Career Title & Header

```css
h1 {
    font-family: "Exo 2", sans-serif;
    font-size:   26px;
    font-weight: 600;
}
```

**Badges** (appear below title when applicable):
- "Signing Bonus is offered" — class `signing-bonus`
- "Accelerated Pay Increment" — class `signing-bonus`

**Apply Now CTA:** Link to `/en/apply-now/`

### 3.3 Tab Navigation Bar

```css
tab-nav {
    height:     51px;
    background: transparent;
    position:   static (becomes sticky on scroll via JS);
}
tab-link {
    font-size:      16px;
    font-weight:    400;
    color:          rgb(255, 255, 255);
    text-transform: uppercase;
}
```

**Anchor targets:**
- `#sec-overview`
- `#sec-training`
- `#sec-entry`
- `#sec-parttime`
- `#sec-related`

### 3.4 Section: Overview (`#sec-overview`)

Content length: ~6,177 characters (for Cook)

**Structure:**
```
<h2>Overview</h2>
<p>Role description paragraph(s)...</p>
<p>Responsibilities intro:</p>
<ul>
  <li>Responsibility 1</li>
  <li>Responsibility 2</li>
  ...
</ul>
<h4>Work environment</h4>
<p>Work environment description...</p>
<h4>Related Civilian Occupations</h4>    ← THE BRIDGE DATA
<ul>
  <li>Civilian occupation 1</li>
  <li>Civilian occupation 2</li>
  ...
</ul>
```

**"Related Civilian Occupations" (critical for bridge table):**

This subsection appears in every career's Overview tab and lists civilian equivalents. Example for Cook:
- Institutional or Restaurant Cook
- Baker
- Food Services Instructor in high schools or colleges
- Food Services Manager or Supervisor (Food Service Establishment)

Example for Signals Officer:
- Physicists
- Aerospace Engineers
- Computer Engineers
- Other Professional Engineers, N.E.C.
- Computer Systems Analysts
- Computer Programmers
- Electrical & Electronic Engineering Technologists and Technicians

### 3.5 Section: Training (`#sec-training`)

**Structure:**
```
<h2>Training</h2>
<h2>Basic Military Qualification</h2>     ← with SVG icon
<p>Description of basic training...</p>
<h2>Basic Occupational Qualification Training</h2>
<p>Duration, location, content...</p>
<h2>Available Specialty Training</h2>
<p>Advanced training options...</p>
```

Each training subsection may include:
- Duration (weeks/months)
- Location
- Curriculum overview
- Inline SVG decorative icons (connecting lines/paths)

### 3.6 Section: Entry Plans (`#sec-entry`)

**Structure:**
```
<h2>Entry plans</h2>
<p>Entry requirements and pathways...</p>
```

Contains entry options like:
- Regular Force (full-time)
- Reserve Force (part-time)
- Direct Entry Officer / Non-Commissioned Member
- Paid Education programs (ROTP, NCMSTEP)
- Education requirements

### 3.7 Section: Part-Time Options (`#sec-parttime`)

**Structure:**
```
<h2>Part time options</h2>
<p>Reserve Force part-time schedule, commitments, pay...</p>
```

### 3.8 Section: Related Careers (`#sec-related`)

**Structure:**
```
<h2>Related Careers</h2>
<div>
  <a href="/en/career/{slug}/">            ← Card-style link to related CAF career
    Career title + image
  </a>
  ...
</div>
```

Related career links follow the same `/en/career/{slug}/` URL pattern and display as mini-cards.

Example related careers for Cook:
- Financial Services Administrator → `/en/career/financial-services-administrator/`
- Materials Technician → `/en/career/materials-technician/`
- Logistics Officer → `/en/career/logistics-officer/`

---

## 4. Footer

```css
footer.base-foot {
    background-color: rgb(26, 26, 26);   /* #1a1a1a */
    padding:          48px 0px 16px;
}
```

### 4.1 Footer Link Grid (5 columns)

| Column | Heading | Links |
|--------|---------|-------|
| Browse Careers | All Careers, Army Careers, Navy Careers, Air Force Careers, Reserve Careers |
| Joining the Forces | Can I Join, Ways to Join, Steps to Join, Basic Training, Paid Education, Reserve Force, Naval Experience Program, Programs for Indigenous Peoples, Applicant Portal, **Apply Now** |
| Life In The Forces | Pay & Benefits, Community, Success Stories |
| About Us | Army, Navy, Air Force, Women in the CAF, Values & Ethos |
| Get in Touch | Help Centre, Find a Recruiting Centre or Reserve Unit, Recruiting Events, Contact Us |

**Heading style:** `<h4>`, font "Exo 2"

### 4.2 Bottom Bar

**Canada Wordmark:** `GovofCanadaSIG_CanadaWordmark-13.svg`

**Social Media Icons (6):**
1. Facebook → `facebook.com/ForcesJobs.ForcesEmplois.CA`
2. X (Twitter) → `twitter.com/CanadianForces`
3. LinkedIn → `linkedin.com/company/canadianforces-forcescanada`
4. Instagram → `instagram.com/forcesjobs.forcesemplois/`
5. YouTube → `youtube.com/@CanadianForcescanadiennes`
6. Flickr → `flickr.com/photos/cafcombatcameradecombatfac/`

**Legal links:** "Terms and Conditions" + "Français"

---

## 5. Asset Inventory

### 5.1 Image Assets

| Asset | URL | Dimensions | Usage |
|-------|-----|-----------|-------|
| GC Sig (white) | `assets/images/SVG/GovofCanadaSIG_CanadaWordmark-11.svg` | 300×30 | Header (dark bg) |
| GC Sig (dark) | `assets/images/SVG/GovofCanadaSIG_CanadaWordmark-08.svg` | 300×30 | Header (light bg) |
| Flag mini | `assets/images/can-flag-mini.png` | 43×22 | Mobile header |
| Career icon | `build/images/icon-career.43c3227f.svg` | 150×150 (displayed 60×60) | Banner icon |
| Hero banner | `build/images/browse-header-2-2000w.9a1738f9.jpg` | 2000px wide | Banner background |
| Category images | `assets/images/index/category-imgs/{slug}.jpg` | Various | Card backgrounds |
| Close icon | `build/images/close-lt.0d7379d7.svg` | 150×150 | Modal close |
| Footer wordmark | `assets/images/SVG/GovofCanadaSIG_CanadaWordmark-13.svg` | - | Footer |

### 5.2 SVG Icons

| Icon | Usage |
|------|-------|
| `icon-career.svg` | Briefcase — Browse Careers banner |
| `icon-navy-white.svg` | Navy environment badge |
| `fa-filter` (inline) | Filter funnel icon |
| `fa-search` (inline) | Search magnifying glass |

---

## 6. Responsive Breakpoints

Bootstrap 4 breakpoints used:

| Breakpoint | Grid Class | Cards Per Row |
|------------|-----------|---------------|
| ≥1200px (xl) | `col-lg-3` | **4** |
| ≥768px (md) | `col-md-4` | **3** |
| <768px (sm) | Default stacking | **1** |

Card height remains **300px** at all breakpoints. Only width changes.

---

## 7. Color Palette

| Token | Value | Usage |
|-------|-------|-------|
| Card text | `rgb(245, 245, 245)` / `#f5f5f5` | Card titles, button text |
| White | `rgb(255, 255, 255)` | Banner heading, nav links |
| Card overlay dark | `rgba(0,0,0,0.9)` | Bottom of card gradient |
| Card overlay mid | `rgba(0,0,0,0.5)` | Middle of card gradient |
| Card overlay flat | `rgba(0,0,0,0.25)` | Uniform darken layer |
| Footer bg | `rgb(26, 26, 26)` / `#1a1a1a` | Footer background |
| Body text | `rgb(73, 80, 87)` / `#495057` | Search input text, body |
| Page bg | `rgb(245, 245, 245)` / `#f5f5f5` | Main content area |
| Border gray | `rgb(133, 130, 130)` | Browse All button border |
| Gold accent | `#C8A835` | Filter chevrons |

---

## 8. URL Schema

```
/en/careers                    → Browse page (L1)
/en/careers/env_{n}            → Environment filter (e.g., env_1 = Army)
/en/careers/reserve            → Reserve filter
/en/career/{slug}/             → Career detail (L3)
/en/apply-now/                 → Application portal
/en/how-to-join/               → How to join pages
/en/help-centre/               → Help/FAQ
/en/life-in-the-military/      → Life info pages
/fr/carrieres                  → French browse page
/fr/carriere/{slug}/           → French career detail
```

**Career slug pattern:** lowercase, hyphenated job title (e.g., `cook`, `signals-officer`, `financial-services-administrator`)

---

## 9. Data Model (Reverse-Engineered)

### 9.1 Career Entity

Based on the detail page structure, each career record contains:

```
Career {
    slug:                     string     // URL slug (e.g., "cook")
    title:                    string     // Display title (e.g., "Cook")
    category:                 string     // One of 12 categories
    category_image:           string     // Card background image URL
    environment:              string[]   // [Navy, Army, Air Force]
    hours:                    string[]   // [Full-time, Part-time]
    education_required:       string     // Minimum education level
    paid_education:           string[]   // Available programs
    incentives:               string[]   // [Signing Bonus, Accelerated Pay, etc.]
    
    overview: {
        description:          string     // 2-3 paragraphs
        responsibilities:     string[]   // Bullet list
        work_environment:     string     // 1-2 paragraphs
        related_civilian:     string[]   // THE BRIDGE: civilian occupation names
    }
    
    training: {
        basic_qualification:  string     // BMQ description
        occupational_training: string    // Trade-specific training
        specialty_training:   string     // Advanced options
    }
    
    entry_plans:              string     // Entry pathways description
    part_time_options:        string     // Reserve Force details
    related_careers:          slug[]     // Links to other career slugs
}
```

### 9.2 Category Entity

```
Category {
    name:       string    // e.g., "Transport & Logistics"
    slug:       string    // e.g., "transport"
    image_url:  string    // Card background image
    careers:    slug[]    // Career slugs in this category
}
```

### 9.3 Bridge Data: "Related Civilian Occupations"

Located in: `Career.overview.related_civilian`

This is the critical join point between CAF and civilian careers. Every CAF career detail page has a "Related Civilian Occupations" subsection under its Overview tab that lists civilian job titles as plain text strings.

**Extraction pattern:**
```
Page: /en/career/{slug}/
Section: #sec-overview
Element: <h4>Related Civilian Occupations</h4> → following <ul><li>...</li></ul>
```

**Bridge mapping strategy:**
```
CAF Career → Related Civilian Occupations (strings)
                     ↓ fuzzy match
            TBS Job Architecture table (Job_Title column)
                     ↓
            Civilian Career record
```

---

## 10. Interaction Patterns

### 10.1 Card Click → Filter

On the Browse page, clicking a category card button triggers a JS filter that:
1. Highlights the selected category
2. Reveals individual career cards within that category
3. Does NOT navigate to a new URL (same-page interaction)

The button has class `call-to-action-btn` with no `href` — behavior is JS-driven.

### 10.2 Tab Navigation (Detail Page)

The 5 section tabs use anchor links (`#sec-overview`, etc.) with smooth scroll. The tab nav bar becomes sticky on scroll (position changes from static to sticky via JS).

### 10.3 Filter Dialog

Triggered by "FILTER CAREERS" button. Opens as a dialog/modal overlay with:
- Checkbox groups for multi-select filters
- Radio buttons for category (single-select)
- "Clear All" reset
- "Close" dismiss

---

## 11. Implementation Notes for Civilian Site

### 11.1 Structural Decisions

| CAF Pattern | Civilian Adaptation |
|-------------|-------------------|
| 12 Job Categories | 12 MVP Job Families (from TBS Job Architecture) |
| Category → careers filter (same-page) | Can keep same-page filter OR add /careers/{family-slug}/ L2 pages |
| `/en/career/{slug}/` detail | `/career/{slug}/` detail with same 5-tab structure |
| "Discover / Prepare / Join" actions | "Discover / Prepare / Apply" (Apply → GC Jobs) |
| "Related Civilian Occupations" in Overview | "Related Military Careers" — reverse bridge |
| Environment filter (Navy/Army/Air Force) | Department or Region filter |
| Incentives filter | N/A (or replace with student programs, bilingual bonus, etc.) |

### 11.2 CSS Replication Checklist

When building the civilian site, these are the exact values to match:

- [ ] Font: "Exo 2" for headings, Roboto for body
- [ ] Banner: 306px height, background-size cover, bg-position center 50%
- [ ] Banner h1: 42px, weight 600, letter-spacing 2.4px, uppercase, "Exo 2"
- [ ] Banner subtitle: 16px, weight 100, letter-spacing 0.64px, uppercase
- [ ] Search input: white bg, 56px height, 16px font, no border-radius
- [ ] Filter button: uppercase, 2.4px letter-spacing, weight 500, gold chevrons #C8A835
- [ ] Card grid: full viewport width, NO max-width constraint
- [ ] Card columns: 25% width (col-lg-3), no horizontal padding-left, 16px padding-bottom
- [ ] Card inner: 300px height, flex column, justify-end, 16px padding
- [ ] Card overlay: 3-layer background-image (flat darken + bottom gradient + photo)
- [ ] Card title: 23.2px, weight 600, "Exo 2", color #f5f5f5
- [ ] Card button: 16px, weight 500, uppercase, 2.4px spacing, 1.33px border, transparent bg
- [ ] Card shadow: `0 3px 5px -1px rgba(0,0,0,.1), 0 6px 10px 0 rgba(0,0,0,.07), 0 1px 18px 0 rgba(0,0,0,.08)`
- [ ] Footer: #1a1a1a bg, 5-column link grid, Canada wordmark, 6 social icons
- [ ] Detail page title: 26px, weight 600, "Exo 2"
- [ ] Detail tab nav: 51px, 16px font, uppercase, white on dark
- [ ] Responsive: 4-col → 3-col → 1-col at Bootstrap 4 breakpoints
