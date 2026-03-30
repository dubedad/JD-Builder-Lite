# DND Civilian Careers — Product Specification

> **Target repo:** `dubedad/JD-Builder-Lite` (GSD production build)
> **Data dependency:** `dubedad/JobForge` (NOC + O*NET data layer)
> **Reference site:** https://forces.ca/en/careers/ (CAF Careers)
> **Static prototype:** `DND-Civilian-Careers-GC.html` (delivered, 12 cards, self-contained)
> **Data source:** `Job_Architecture_TBS.xlsx` — 1,989 job titles, 209 job families, 22 job functions

---

## 1. Product Overview

Build an interactive DND Civilian Workforce careers site that mirrors the Canadian Armed Forces (CAF) Careers site at `forces.ca/en/careers/`. The civilian site uses the same UX patterns, visual language, and navigation flow — but populated entirely with civilian Public Service job data sourced from the TBS Job Architecture table.

**The two sites share a common data bridge:** CAF career pages include a "Related Civilian Occupations" section. This field is the join key that links military job titles to civilian job titles, enabling cross-referencing and career pathway discovery.

---

## 2. Architecture

```
┌──────────────────────────────────────────┐
│  DND Civilian Careers (this build)       │
│  FastAPI + React/HTML                    │
│  ├─ Browse page (Job Family grid)        │
│  ├─ Category page (Job Titles list)      │
│  └─ Detail page (Overview/Training/etc)  │
├──────────────────────────────────────────┤
│  Data Pipeline                           │
│  ├─ Job Architecture TBS ingest          │
│  ├─ CAF scraper (Related Civilian Occs)  │
│  ├─ LLM enrichment (Overview, Training)  │
│  └─ Bridge table builder                 │
├──────────────────────────────────────────┤
│  JobForge (data layer — separate repo)   │
│  ├─ NOC 2021 codes                       │
│  ├─ O*NET crosswalk                      │
│  └─ ChromaDB embeddings                  │
└──────────────────────────────────────────┘
```

**Dependency rule:** JobForge must be active and stable before this build proceeds. The civilian careers site consumes JobForge's harmonized occupational data for NOC alignment and O*NET enrichment.

---

## 3. Data Layer

### 3.1 Source: TBS Job Architecture Table

**File:** `Job_Architecture_TBS.xlsx` → Sheet: `DRAFT_JA_EN-FR`
**Records:** 1,989 job titles
**Key columns:**

| Column | Description | Example |
|--------|-------------|---------|
| `JT_ID` | Unique job title ID | `2` |
| `Job_Title` | English title | `Administrative Assistant` |
| `Titre_de_poste` | French title | `Adjoint(e) administratif(ive)` |
| `Job_Function` | Top-level grouping (22 values) | `Administration` |
| `Job_Family` | Mid-level grouping (209 values) | `Administrative Support` |
| `Managerial_Level` | Seniority band | `Employee` |
| `2021_NOC_UID` | NOC 2021 code | `13110` |
| `2021_NOC_Title` | NOC 2021 title | `Administrative Assistants` |
| `Digital` | Digital flag | `Non-Digital` / `Digital` |
| `Digital_Category` | Digital sub-category | (varies) |

### 3.2 Job Families for Display (12 selected for MVP)

These 12 families were selected for the prototype site. They map to Job Families in the TBS table:

| # | Display Label | TBS `Job_Family` value | Title Count |
|---|--------------|------------------------|-------------|
| 1 | Administrative Support | `Administrative Support` | 9 |
| 2 | AI Strategy & Integration | `Artificial Intelligence (AI) Strategy & Integration` | 12 |
| 3 | Organization Design & Classification | `Organization and Classification` | 9 |
| 4 | Information & Data Architecture | `Information and Data Architecture` | 7 |
| 5 | Data Management | `Data Management` | 19 |
| 6 | Enterprise Architecture | `Enterprise Architecture` | 7 |
| 7 | Innovation & Change Management | `Innovation and Change Management` | 11 |
| 8 | Project Management | `Project Management` | 14 |
| 9 | Database & Data Administration | `Database and Database Administration` | 9 |
| 10 | Electronics Technician | `Electrical` | 15 |
| 11 | Food Services | `Food Services` | 10 |
| 12 | Nursing | `Nursing` | 9 |

**Note:** The full site should support all 209 Job Families. The 12 above are the MVP set with hero images already prepared.

### 3.3 Target Schema (Unified Table)

Extend the Job Architecture table with CAF-patterned content columns:

```sql
CREATE TABLE careers (
    jt_id           INTEGER PRIMARY KEY,
    job_title       TEXT NOT NULL,
    titre_de_poste  TEXT,
    job_function    TEXT NOT NULL,        -- 22 values
    job_family      TEXT NOT NULL,        -- 209 values
    managerial_level TEXT,
    noc_2021_uid    TEXT,
    noc_2021_title  TEXT,
    digital         TEXT,
    
    -- NEW: CAF-patterned content columns
    overview        TEXT,                 -- Role description, responsibilities, work environment
    training        TEXT,                 -- Education requirements, certifications, development
    entry_plans     TEXT,                 -- How to enter this career path in the PS
    part_time       TEXT,                 -- Part-time/flexible work options
    related_careers TEXT,                 -- JSON array of related job_title IDs
    
    -- NEW: Bridge columns
    caf_related     TEXT,                 -- JSON array of CAF occupation slugs that map here
    card_image_key  TEXT,                 -- Image asset reference for card display
    
    -- Metadata
    content_status  TEXT DEFAULT 'empty', -- empty | draft | reviewed | published
    enriched_at     TIMESTAMP
);
```

### 3.4 LLM Enrichment Pipeline

Populate the content columns using Anthropic API calls:

```python
ENRICHMENT_PROMPT = """
You are a Government of Canada HR specialist writing career content 
for the DND Civilian Workforce careers website.

Given this job title from the TBS Job Architecture:
- Job Title: {job_title}
- Job Family: {job_family}  
- Job Function: {job_function}
- NOC 2021: {noc_2021_title}
- Managerial Level: {managerial_level}

Generate content for each section following the exact structure used 
on the CAF Careers site (forces.ca). Write in plain, professional 
Government of Canada tone.

Return JSON with these keys:
- overview: 2-3 paragraphs covering role description, responsibilities, 
  and work environment
- training: Education requirements, certifications, professional 
  development opportunities  
- entry_plans: How someone enters this career in the federal Public 
  Service (competitions, pools, student programs, lateral moves)
- part_time: Part-time, flexible work, and remote options typical 
  for this role
"""
```

**Pipeline steps:**
1. Ingest `Job_Architecture_TBS.xlsx` → SQLite/Postgres
2. For each job title, call Anthropic API with enrichment prompt
3. Store results in `overview`, `training`, `entry_plans`, `part_time` columns
4. Set `content_status = 'draft'` and `enriched_at = now()`

### 3.5 CAF Bridge Table

The CAF site's career detail pages (e.g., `forces.ca/en/career/cook/`) include a "Related Careers" tab that lists civilian occupations. This is the bridge.

**Pipeline:**
1. Scrape all CAF career detail pages
2. Extract the "Related Civilian Occupations" from each page's Overview or Related Careers tab
3. Fuzzy-match those civilian occupation strings to `Job_Title` in the TBS table
4. Store the mapping in the `caf_related` column as JSON

```python
# Example bridge data
{
    "caf_slug": "cook",
    "caf_title": "Cook",
    "caf_category": "Hospitality & Support",
    "related_civilian_occupations": [
        "Food Services Worker",
        "Cook (Institutional)",
        "Dietary Aide"
    ],
    "matched_jt_ids": [1245, 1246, 1248]  # from TBS table
}
```

This enables bidirectional navigation:
- Civilian career page → "Related Military Careers" section
- CAF career page → "Related Civilian Occupations" (already exists)

---

## 4. Transaction Layer (UX)

### 4.1 Page Flow

```
Browse Careers (grid) → Job Family (list) → Job Title (detail)
       ↕                       ↕                    ↕
  Filter/Search          View Careers          Discover/Prepare/Apply
```

### 4.2 Browse Careers Page (L1)

**Layout:** Exact match to `forces.ca/en/careers/`

| Element | Specification |
|---------|--------------|
| Header | GC FIP signature (`GC_Canada_Logo.png` embedded), dark background `#222`, 64px height |
| Breadcrumb | `#333` background, 40px, Home → Careers |
| Hero Banner | Background image (`public_service_hero.png`), 55% dark overlay, briefcase icon (60×60), subtitle "DEPARTMENT OF NATIONAL DEFENCE — CIVILIAN WORKFORCE" (white, uppercase, 16px, 1.5px letter-spacing), heading "BROWSE CAREERS" (42px, weight 600, 2.4px letter-spacing, uppercase) |
| Search | White box (520×50px), gray magnifying glass left, 16px placeholder text. "FILTER CAREERS" button: uppercase, 2.4px letter-spacing, funnel SVG icon, gold double chevrons `#C8A835` |
| Browse Strip | `#e8e8e8` background, italic "Browse careers based on your area of interest.", "BROWSE ALL CAREERS" button |
| Card Grid | Full-width (no max-width), 4 columns, cards: `calc(25% - 12px)` width × 300px height, 6px horizontal margin, 4px vertical. Overlay: `rgba(0,0,0,.25)` flat + bottom gradient `transparent → rgba(0,0,0,.5) → rgba(0,0,0,.9)`. Title: 20px weight-600 `rgb(245,245,245)`. Button: transparent, 1px solid `rgb(245,245,245)`, 16px, padding 6.5px 30px |
| Footer | 5-column link grid on `#2a2a2a`, bottom bar on `#1a1a1a` with Canada wordmark + social icons + legal links |

**Card click behavior:** Navigate to `/careers/{job_family_slug}` (L2 page)

### 4.3 Job Family Page (L2)

**URL:** `/careers/{job_family_slug}`
**Content:** List of all Job Titles within that family, pulled from TBS table.

Display as a list or card sub-grid matching CAF's category drill-down:
- Job Title name
- NOC code badge
- Managerial level tag
- Digital/Non-Digital indicator
- Brief excerpt from `overview` (first 150 chars)

### 4.4 Job Title Detail Page (L3)

**URL:** `/career/{job_title_slug}`
**Layout:** Match `forces.ca/en/career/cook/` exactly.

**Tabs (anchored sections):**

| Tab | Source |
|-----|--------|
| Overview | `overview` column — role description, responsibilities, work environment |
| Training | `training` column — education, certs, professional development |
| Entry Plans | `entry_plans` column — how to join PS in this role |
| Part-Time Options | `part_time` column — flexible work, remote, part-time |
| Related Careers | `related_careers` + `caf_related` — links to other civilian titles AND to CAF equivalents |

**Action buttons (top of page):**
- **Discover** — scrolls to Overview
- **Prepare** — scrolls to Training
- **Apply** — links to GC Jobs / PSRS

---

## 5. Frontend Specifications

### 5.1 CSS Extracted from Live CAF Site

All values below were measured from `forces.ca/en/careers/` via Chrome DevTools:

```css
/* === VERIFIED CAF VALUES === */

/* Header */
.navbar { height: 58px; background: transparent; }

/* Banner */
.banner { height: 306px; background-size: cover; background-position: center 50%; }
.banner h1 { font-size: 42px; font-weight: 600; letter-spacing: 2.4px; text-transform: uppercase; }

/* Search */
.banner input { width: ~520px; height: 56px; font-size: 16px; background: #fff; color: #495057; }

/* Filter button */
.filter-btn { font-size: 16px; font-weight: 500; text-transform: uppercase; letter-spacing: 2.4px; color: rgb(245,245,245); }

/* Cards */
.category-card-inner {
    height: 300px;
    display: flex; flex-direction: column; justify-content: flex-end;
    padding: 16px;
    background-image: 
        linear-gradient(rgba(0,0,0,0.25)),
        linear-gradient(rgba(0,0,0,0) 0%, rgba(0,0,0,0) 30%, rgba(0,0,0,0.5) 65%, rgba(0,0,0,0.9) 100%),
        url("image.jpg");
    background-size: cover;
    box-shadow: 0 3px 5px -1px rgba(0,0,0,.1), 0 6px 10px rgba(0,0,0,.07), 0 1px 18px rgba(0,0,0,.08);
}
.category-card-inner h3 { font-size: 23.2px; font-weight: 600; color: rgb(245,245,245); }
.view-btn { 
    background: transparent; 
    border: 0.667px solid rgb(245,245,245); 
    color: rgb(245,245,245);
    padding: 6.5px 30px; 
    font-size: 16px; 
}

/* Grid: full-width, no max-width constraint */
.row { display: flex; flex-wrap: wrap; width: 100%; }
.category-card { width: 25%; } /* col-lg-3 */

/* Footer */
footer { background: rgb(42,42,42); }
```

### 5.2 Image Assets

12 card images are embedded as base64 in the prototype HTML. For the production build, extract and serve as static files:

| Card | Filename | Format |
|------|----------|--------|
| Administrative Support | `administrative_support.webp` | WebP |
| AI Strategy & Integration | `Artificial_Intelligence_Strategy___Integration.webp` | WebP |
| Organization Design & Classification | `Organizational_Design_and_Classification.jpg` | JPEG |
| Information & Data Architecture | `Information_and_Data_Architecture.jpg` | JPEG |
| Data Management | `data_management.webp` | WebP |
| Enterprise Architecture | `enterprise_architecture.png` | PNG |
| Innovation & Change Management | `innovation_and_change_management.jpg` | JPEG |
| Project Management | `project_management.jpg` | JPEG |
| Database & Data Administration | `database_administration.png` | PNG |
| Electronics Technician | `electronic_engineering.jpg` | JPEG |
| Food Services | `food_services.jpg` | JPEG |
| Nursing | `nursing.jpg` | JPEG |

**Other assets:**
- `GC_Canada_Logo.png` — GC FIP header signature (white on dark)
- `public_service_hero.png` — Hero banner background (GC building)

---

## 6. Implementation Plan

### Phase 1: Data Pipeline (Week 1-2)

1. **Ingest Job Architecture** — Parse `Job_Architecture_TBS.xlsx`, load into SQLite
2. **Create schema** — Add `overview`, `training`, `entry_plans`, `part_time`, `related_careers`, `caf_related` columns
3. **LLM enrichment** — Batch-process all 1,989 titles through Anthropic API
4. **Validate** — Spot-check 10% of enriched records for quality

### Phase 2: CAF Bridge (Week 2-3)

1. **Scrape CAF career pages** — All career detail URLs from `forces.ca/en/career/*`
2. **Extract "Related Civilian Occupations"** — Parse Overview tab content
3. **Fuzzy match** — Map CAF civilian occupation strings to TBS `Job_Title` values
4. **Build bridge table** — Store bidirectional mappings
5. **Validate** — Confirm bridge coverage (% of civilian titles with CAF links)

### Phase 3: Frontend (Week 3-4)

1. **Convert prototype to FastAPI + Jinja2** (or React) — Port the static HTML to a server-rendered app
2. **L1: Browse page** — Card grid with search/filter, dynamic from database
3. **L2: Category page** — Job title listing within a family
4. **L3: Detail page** — Tabbed layout with Overview/Training/Entry/Part-Time/Related
5. **Static assets** — Extract base64 images to `/static/images/`

### Phase 4: Integration (Week 4-5)

1. **Connect to JobForge** — Pull NOC descriptions and O*NET enrichment
2. **Search** — Implement full-text search across job titles and content
3. **Filter** — Category, digital/non-digital, managerial level, NOC code
4. **Related careers** — Wire up the bridge table for cross-navigation

---

## 7. CAF Site Structure Reference

### 7.1 CAF Job Categories (12)

```
Transport & Logistics | Naval Operations | Aviation | Health Care
Combat Operations | Computing & Intelligence | Safety & Emergency Services | Engineering & Infrastructure
Administration | Hospitality & Support | Public Relations | Equipment & Vehicle Maintenance
```

### 7.2 CAF Career Detail Tabs

Every career at `forces.ca/en/career/{slug}/` has these anchored sections:

```
#sec-overview    → Overview (role, responsibilities, work environment)
#sec-training    → Training (education, duration, location)  
#sec-entry       → Entry Plans (Regular Force, Reserve, Officer entry)
#sec-parttime    → Part-Time Options (Reserve Force details)
#sec-related     → Related Careers (other military + civilian occupations)
```

### 7.3 CAF Filter Categories

The CAF site offers these filters (our civilian version should mirror where applicable):

- **Category** — Job Family equivalent
- **Environment** — N/A for civilian (replace with Department or Region)
- **Hours** — Full-time / Part-time
- **Paid Education** — Student programs
- **Minimum Required Education** — Graduate / Bachelor / College / High School / Grade 10

---

## 8. Compliance & Constraints

- **DADM** — All automated content generation must comply with the Directive on Automated Decision-Making. LLM-generated content must be flagged as `content_status: draft` until human-reviewed.
- **GC HR Data Standard for NOC** — All job titles must carry valid NOC 2021 codes from the TBS table.
- **No Protected B data** — Only open occupational data (NOC, O*NET, TBS Job Architecture). No internal departmental data.
- **Bilingual** — The TBS table includes French equivalents. Full bilingual support is required for production but not for MVP.
- **Accessibility** — WCAG 2.1 AA compliance. Use GC Web Experience Toolkit (WET) patterns where possible.

---

## 9. File Manifest

```
ps_careers_site/
├── DND-Civilian-Careers-GC.html     # Static prototype (self-contained, 1.7MB)
├── DND-Civilian-Careers-GC.png      # Screenshot
├── Job_Architecture_TBS.xlsx        # Source data (1,989 titles)
├── images/
│   ├── GC_Canada_Logo.png           # FIP header
│   ├── public_service_hero.png      # Hero banner
│   ├── administrative_support.webp
│   ├── ai_strategy.webp
│   ├── org_design.jpg
│   ├── info_data_arch.jpg
│   ├── data_management.webp
│   ├── enterprise_architecture.png
│   ├── innovation_change.jpg
│   ├── project_management.jpg
│   ├── database_admin.png
│   ├── electronics_technician.jpg
│   ├── food_services.jpg
│   └── nursing.jpg
└── spec/
    └── DND-Civilian-Careers-SPEC.md  # This file
```

---

## 10. Definition of Done

- [ ] All 1,989 job titles ingested from TBS table
- [ ] 12 MVP Job Families display as card grid matching CAF proportions
- [ ] Click-through to Job Family → Job Title list works
- [ ] Click-through to Job Title → Detail page with 5 tabs works
- [ ] LLM-generated content populates all 5 tab sections
- [ ] CAF bridge table connects military ↔ civilian career paths
- [ ] Search returns relevant results across titles and content
- [ ] Filter by category, education level, and digital flag works
- [ ] GC FIP header and footer render correctly
- [ ] Responsive: 4-col → 2-col → 1-col at breakpoints
- [ ] No external dependencies in static prototype mode
