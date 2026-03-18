# New Version Build: Findings & Issues to Address

**Purpose:** Capture findings from codebase review to inform Claude Code when building a new version of JD-Builder-Lite using the GSD framework.

**Created:** 2026-03-04  
**Source:** Chat review of JD-Builder-Lite (master branch)  
**Target:** New version build via GSD (`/gsd:new-project`, `/gsd:plan-phase`)

---

## 1. Application Overview (For Context)

**JobForge (JD-Builder-Lite)** is a Government of Canada job description builder that:
- Searches NOC occupational profiles (ESDC OASIS)
- Lets managers select statements from structured profiles
- Uses AI to generate overviews and style statements
- Exports PDF/Word with compliance metadata
- Classifies jobs into TBS occupational groups (Step 1)

**Tech Stack:** Flask, Python 3.11, vanilla JS, SQLite, OpenAI API

---

## 2. Critical Issues to Fix in New Version

### 2.1 JobForge 2.0 Integration (Architectural)

| Issue | Current State | Target State |
|-------|---------------|--------------|
| **Primary data source** | OASIS scraping (live HTTP) for search and profiles | JobForge 2.0 gold parquet as primary; OASIS only for gaps |
| **Integration depth** | Supplemental only (vocabulary, labels, classification shortlisting) | Seamless: JobForge-first for all search/profile data |
| **Paths** | Hardcoded Windows: `C:/Users/Administrator/Dropbox/++ Results Kit/JobForge 2.0/data/bronze` | Environment variables: `JOBFORGE_BRONZE_PATH`, `JOBFORGE_GOLD_PATH` |
| **Deployment** | JD-Builder expects JobForge parquet on disk; no shared deployment | Configurable paths; optional JobForge API if available |

**Reference:** `.planning/JOBFORGE-DATA-REQUIREMENTS.md`, `.planning/UAT-FINDINGS.md` (S1-10)

### 2.2 Data Pipeline Duplication

**Current:** JD-Builder-Lite replicates JobForge's pipeline:
- Own scraper → parser → mapper for search and profiles
- JobForge already has medallion pipeline (bronze → silver → gold)

**Target:** Consume JobForge gold parquet as primary source; eliminate OASIS scraping for data JobForge already provides.

### 2.3 Configuration & Portability

| Issue | Location | Fix |
|-------|----------|-----|
| Hardcoded JobForge paths | `src/config.py`, `src/services/labels_loader.py` | Use `os.getenv("JOBFORGE_BRONZE_PATH")` etc. |
| Windows-specific paths | Multiple files | Cross-platform path handling |
| No `.env.example` for JobForge | `.env.example` | Add `JOBFORGE_BRONZE_PATH`, `JOBFORGE_GOLD_PATH` |

**Reference:** `.planning/codebase/CONCERNS.md` (lines 158–161)

### 2.4 Hardcoded Paths (Critical for Local Run)

**Files requiring path updates:**

1. **`src/config.py`** (line 20):
   - Current: `JOBFORGE_BRONZE_PATH = "C:/Users/Administrator/Dropbox/++ Results Kit/JobForge 2.0/data/bronze"`
   - Should use env var with fallback, e.g. `os.getenv("JOBFORGE_BRONZE_PATH", "/path/to/JobForge-2.0/data/bronze")`

2. **`src/services/labels_loader.py`** (lines 99–101):
   - Current: `GOLD_DATA_PATH` and `SOURCE_DATA_PATH` hardcoded to Windows paths
   - Should use env vars: `JOBFORGE_GOLD_PATH`, `JOBFORGE_SOURCE_PATH`

**Example local path (macOS):** `/Users/victornishi/Documents/GitHub/JobForge-2.0/data/bronze` (and `/data/gold`, `/data/source`)

### 2.5 README & Setup Documentation

| Issue | Severity | Description |
|-------|----------|-------------|
| **README init_db step** | Medium | References non-existent `scripts/init_db.py`; correct command is `python -c "from src.storage.db_manager import init_db; init_db(); print('DB initialized')"` |
| **Cross-platform paths** | Medium | Windows-specific paths prevent running on macOS/Linux without manual edits |

---

## 3. UI Status & Running the App

### 3.1 Full UI Exists

The app has a complete single-page UI:
- **Templates:** `templates/index.html`
- **Styles:** `static/css/` (main, accordion, sidebar, classify, export, etc.)
- **Scripts:** `static/js/` (search, profile_tabs, selection, generate, export, classify, filters, etc.)
- **Features:** Search, profile selection, JD building, AI overview, PDF/Word export, classification

### 3.2 Setup Steps (With Local JobForge 2.0)

**Prerequisites:** Python 3.11+, JobForge 2.0 cloned locally (e.g. `/Users/victornishi/Documents/GitHub/JobForge-2.0`)

1. **Install dependencies:** `pip install -r requirements.txt`
2. **Create `.env`:** `OPENAI_API_KEY`, `SECRET_KEY`
3. **Update paths** in `src/config.py` and `src/services/labels_loader.py` to point to local JobForge 2.0 `data/bronze`, `data/gold`, `data/source`
4. **Initialize DB:** `python -c "from src.storage.db_manager import init_db; init_db(); print('DB initialized')"`
5. **Load TBS data (for classification):** `python -m src.cli.refresh_occupational`
6. **Run:** `python -m src.app` → open http://localhost:5000

### 3.3 JobForge 2.0 Data Requirements

Vocabulary needs these in `data/bronze/`:
- `oasis_abilities.parquet`
- `oasis_skills.parquet`
- `oasis_knowledges.parquet`
- `oasis_workactivities.parquet`

Labels loader needs in `data/gold/`:
- `element_labels.parquet`, `element_example_titles.parquet`, `element_exclusions.parquet`, `oasis_workcontext.parquet`, etc.

---

## 4. Codebase Structure (For Navigation)

```
JD-Builder-Lite/
├── src/
│   ├── app.py              # Entry point
│   ├── routes/api.py       # All API endpoints
│   ├── services/           # Scraper, parser, mapper, LLM, export
│   ├── matching/           # Classification engine (allocator, shortlisting)
│   ├── vocabulary/         # JobForge parquet vocabulary index
│   ├── storage/            # SQLite, schema
│   └── scrapers/           # OASIS, TBS HTTP clients
├── static/js/              # Frontend modules (main, search, export, classify)
├── templates/              # index.html, export templates
└── .planning/              # GSD planning, research, phases
```

---

## 5. Key Data Flows (Current)

1. **Search:** User query → `/api/search` → scraper.search() → parser → results (OASIS)
2. **Profile:** NOC code → `/api/profile` → scraper.fetch_profile() → parser → mapper → JD elements (OASIS + JobForge labels supplement)
3. **Vocabulary:** App startup → VocabularyIndex(JOBFORGE_BRONZE_PATH) → 4 parquet files (JobForge)
4. **Labels/Enrichment:** Mapper → labels_loader (JobForge gold parquet) for labels, example titles, work context
5. **Classification:** `/api/allocate` → allocator → shortlisting (JobForge labels) → LLM → recommendations

---

## 5.5 UI Redesign Target: v5.1 Walkthrough

A full written walkthrough of the desired v5.1 UI is saved here:

```
.planning/ui-walkthrough-v5.1/walkthrough.md
```

Reference in GSD phase plans: `@.planning/ui-walkthrough-v5.1/walkthrough.md`

**Key design decisions from the walkthrough:**

| Area | Decision |
|------|----------|
| **Blue dots / importance ratings** | Retain from v5.0 for Key Activities, Skills, Abilities, Knowledge, Effort, Responsibilities |
| **Main Duties vs Work Activities** | Keep as TWO separate lists under distinct headings (do NOT merge) |
| **Core Competencies** | Make selectable (was read-only in v5.0) |
| **Navigation buttons** | 3-button bar: ← Back to Search \| Preview Job Description \| Continue to Classification → |
| **Selection persistence** | Keep selections when returning to Search; clear only when a different occupation card is selected |
| **Preview modal** | JD preview in a modal with Return to Builder + Classify + Export options |
| **Generate/Export steps** | UI buttons present in v5.1; backend functionality deferred to later version |

**Screenshots:** The walkthrough text references screenshots from the Google Doc. Screenshots were NOT included in the text export. Add them manually:
1. Open the Google Doc: https://docs.google.com/document/d/1IO_d2zLJEvfNEnJp8kMnEnobgWq2s4te0UULTQvniRU/edit?usp=sharing
2. Save each screenshot to `.planning/ui-walkthrough-v5.1/screenshots/`
3. Suggested names: `01-search.png`, `02-overview.png`, `02.1-core-competencies.png`, `02.2-key-activities.png`, `02.3-skills.png`, `02.4-abilities.png`, `02.5-knowledge.png`, `02.6-effort.png`, `02.7-responsibilities.png`, `02.8-preview-modal.png`, `03-classification.png`

---

## 6. GSD Integration Notes

- **Phase planning:** Reference this file via `@.planning/NEW-VERSION-FINDINGS.md` in PLAN.md files
- **New project:** Use findings in Section 2 as input to `/gsd:new-project` requirements
- **Phase research:** GSD phase-researcher can use this for context on architectural decisions
- **Continue-here:** Consider updating `.planning/.continue-here.md` to point Claude to this document when resuming

---

## 7. Changelog

| Date | Section | Update |
|------|---------|--------|
| 2026-03-04 | All | Initial creation from chat: orientation, codebase exploration, JobForge integration analysis |
| 2026-03-04 | 2.4, 2.5, 3 | Added hardcoded path details, README init_db fix, UI status, setup steps with local JobForge 2.0 |
| 2026-03-11 | 5.5 | Added v5.1 UI walkthrough reference; walkthrough saved to `.planning/ui-walkthrough-v5.1/walkthrough.md` |
