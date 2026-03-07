# Phase 22: Profile Service - Research

**Researched:** 2026-03-07
**Domain:** Parquet profile reader, OASIS fallback wiring, provenance extension, source badge UI
**Confidence:** HIGH

---

## Summary

Phase 22 adds parquet-sourced data for five profile tabs (Skills, Abilities, Knowledge, Work Activities, Work Context) and wires automatic OASIS fallback for all other tabs. It also adds per-tab source badges and extends the export provenance schema. All technical building blocks were verified against the live codebase.

The infrastructure from Phase 21 (CoverageStatus, ParquetResult, read_parquet_safe, lookup_profile) is complete and live in `src/models/parquet.py` and `src/services/parquet_reader.py`. The five target tabs currently pull data from OASIS live scraping via `parser.py` + `mapper.py`. Phase 22 replaces that path with parquet lookups in a new `ProfileParquetReader` service, falling back to the existing OASIS path when CoverageStatus is NOT_FOUND or LOAD_ERROR.

The UI tab system uses `profile_tabs.js` (TabController) and `accordion.js` (renderTabContent). Tab panels are static HTML elements in `templates/index.html`; content is injected by `renderTabContent()`. Source badges are a new UI element -- the existing badge styles (`.oasis-code-badge`, `.noc-badge`, `.holland-code__badge`) all use inline-block display with background-color; a new `.source-badge` CSS class is the right approach. The skeleton loader pattern (`.skeleton` + shimmer animation in `skeleton.css`) is already in place and should be used for any loading state treatment.

**Primary recommendation:** Create `src/services/profile_parquet_reader.py` as the parquet-to-profile adapter. Wire it into `src/services/mapper.py` as the first lookup path before OASIS, returning CoverageStatus-tagged results. Add `data_source` fields to the ProfileResponse JSON. Render source badges in `accordion.js` using new CSS classes in `main.css`. Extend the export provenance schema by adding a `section_sources` dict to `SourceMetadataExport` (or a parallel `SectionProvenanceExport` model).

---

## Standard Stack

### Core (existing -- no new installs needed)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pandas | 2.2.3 | Read parquet files | Already installed; parquet_reader.py uses it |
| pyarrow | 23.0.0 | Parquet engine | Already installed as pandas dep |
| pydantic v2 | 2.12.5 | Response models, provenance schema | All models/* already use it |
| Flask | ~3.x | Route serving | Existing app framework |
| stdlib logging | 3.14 | Warning logging | Established pattern in all service files |

### Supporting (existing)

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| src.models.parquet | Phase 21 | CoverageStatus + ParquetResult | All parquet reads in profile reader |
| src.services.parquet_reader | Phase 21 | read_parquet_safe, lookup_profile | Reading oasis_* parquet files |
| src.services.labels_loader | Existing | LabelsLoader singleton | Interests, Personal Attributes (no change needed) |
| src.services.scraper | Existing | OASISScraper.fetch_profile() | OASIS fallback path |
| src.services.mapper | Existing | JDMapper.to_jd_elements() | Existing mapper entry point to extend |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Extending mapper.py | New standalone service | Mapper is already the profile assembly point; extension avoids a second data assembly layer |
| Per-tab API endpoints | Single /api/profile with source tags | Single endpoint matches current architecture; no client routing changes needed |
| New provenance model | Extending existing SourceMetadataExport | Extension is safer -- existing exports continue working; parallel field is additive |

**Installation:** No new packages needed.

---

## Architecture Patterns

### Recommended Project Structure

```
src/
├── models/
│   ├── parquet.py              # Phase 21 -- CoverageStatus, ParquetResult (NO CHANGES)
│   └── responses.py            # Extend ProfileResponse: add data_source fields per tab
├── services/
│   ├── parquet_reader.py       # Phase 21 -- read_parquet_safe, lookup_profile (NO CHANGES)
│   ├── profile_parquet_reader.py  # NEW: reads 5 oasis_* files, returns typed results
│   └── mapper.py               # EXTEND: try parquet first, fall back to OASIS
├── utils/
│   └── oasis_provenance.py     # EXTEND: add JobForge source metadata entries
static/
├── css/
│   └── main.css                # ADD: .source-badge--jobforge, .source-badge--oasis
└── js/
    └── accordion.js            # EXTEND: renderTabContent injects source badge HTML
templates/
└── index.html                  # NO CHANGES (tab panels already exist)
```

### Pattern 1: ParquetProfileReader Service

**What:** A service class that reads the five oasis_* files for a given profile code and returns CoverageStatus-tagged results per tab.
**When to use:** Called from mapper.py before OASIS scraping.
**Key constraint:** oasis_* files use column `oasis_code` (NOT `oasis_profile_code`). This is the locked decision from Phase 21 and State.md. Do NOT use `unit_group_id` as the lookup column for these files.

```python
# File: src/services/profile_parquet_reader.py
# Source: project pattern from src/services/parquet_reader.py + DATA-INVENTORY.md

import logging
from pathlib import Path
from typing import Optional
import os

import pandas as pd

from src.models.parquet import CoverageStatus, ParquetResult
from src.services.parquet_reader import lookup_profile

logger = logging.getLogger(__name__)

GOLD_DATA_PATH = Path(os.getenv(
    "JOBFORGE_GOLD_PATH",
    "/Users/victornishi/Documents/GitHub/JobForge-2.0/data/gold"
))

# File paths for the 5 tabs Phase 22 serves from parquet
OASIS_FILES = {
    "skills":          GOLD_DATA_PATH / "oasis_skills.parquet",
    "abilities":       GOLD_DATA_PATH / "oasis_abilities.parquet",
    "knowledge":       GOLD_DATA_PATH / "oasis_knowledges.parquet",
    "work_activities": GOLD_DATA_PATH / "oasis_workactivities.parquet",
    "work_context":    GOLD_DATA_PATH / "oasis_workcontext.parquet",
}

# Each oasis_* file uses column 'oasis_code' (NOT 'oasis_profile_code')
# confirmed from DATA-INVENTORY.md -- all oasis_* files key on 'oasis_code'
OASIS_CODE_COL = "oasis_code"

# Metadata columns to exclude when extracting dimension values
METADATA_COLS = {
    "unit_group_id", "noc_element_code", "oasis_code", "oasis_label",
    "_source_file", "_ingested_at", "_batch_id", "_layer"
}


def get_profile_tab(tab_key: str, oasis_profile_code: str) -> ParquetResult[pd.DataFrame]:
    """Read one tab's data from parquet for a given oasis_profile_code.

    Args:
        tab_key: One of 'skills', 'abilities', 'knowledge', 'work_activities', 'work_context'
        oasis_profile_code: Format '21211.00' (with decimal)

    Returns:
        ParquetResult:
          LOAD_ERROR -- file missing or unreadable
          NOT_FOUND  -- file loaded but profile code not in file
          FOUND      -- DataFrame with single row for the profile
    """
    if tab_key not in OASIS_FILES:
        logger.warning("Unknown tab_key '%s' in get_profile_tab", tab_key)
        return ParquetResult(
            status=CoverageStatus.LOAD_ERROR,
            error=f"Unknown tab key: {tab_key}"
        )

    path = OASIS_FILES[tab_key]
    return lookup_profile(path, OASIS_CODE_COL, oasis_profile_code)


def extract_dimension_ratings(df_row: pd.DataFrame, tab_key: str) -> list[dict]:
    """Extract (name, level) pairs from a single-row parquet result.

    Column whitespace stripping is already done by read_parquet_safe()
    in parquet_reader.py -- no need to strip again here.

    Returns:
        List of {'name': str, 'level': int} dicts, sorted by level descending,
        filtered to non-zero values only.
    """
    if df_row is None or df_row.empty:
        return []

    row = df_row.iloc[0]
    results = []

    for col in df_row.columns:
        if col in METADATA_COLS:
            continue
        val = row[col]
        if pd.notna(val):
            try:
                level = int(val)
                if level > 0:
                    results.append({"name": col, "level": level})
            except (ValueError, TypeError):
                pass

    results.sort(key=lambda x: x["level"], reverse=True)
    return results
```

### Pattern 2: NOC Code to oasis_profile_code Transformation

**What:** The API receives a NOC code like `'21211'` (5 digits, no decimal). The oasis_* files use `oasis_profile_code` format `'21211.00'`. The transformation must try `.00` first and `.01` on NOT_FOUND.
**When to use:** Every parquet lookup in Phase 22.
**Source:** GAP-ANALYSIS.md and DATA-INVENTORY.md, Phase 21.

```python
# Source: DATA-INVENTORY.md profile code format note
def noc_to_oasis_code(noc_code: str) -> list[str]:
    """Generate candidate oasis_profile_codes for a NOC code.

    Most NOC codes map to a single profile '21211.00'.
    Some map to multiple sub-profiles: '10020.01', '10020.02', etc.
    Try primary (.00) first, then .01 as fallback.

    Args:
        noc_code: 5-digit NOC code string (e.g. '21211')

    Returns:
        List of candidate codes to try in order
    """
    base = noc_code.split('.')[0]  # Normalize if already has decimal
    return [f"{base}.00", f"{base}.01"]
```

### Pattern 3: Source Badge in API Response

**What:** Each tab in ProfileResponse carries a `data_source` string (`"jobforge"` or `"oasis"`) so the frontend can render the badge without knowing which path was taken.
**When to use:** Any tab that has a parquet path (parquet FOUND -> `"jobforge"`) or falls back to OASIS scraping (`"oasis"`).
**Boundary:** The badge is rendered by JavaScript in `renderTabContent()` in `accordion.js`. The badge HTML is injected at the bottom of each tab panel's content.

```python
# Extend EnrichedJDElementData in src/models/responses.py
class EnrichedJDElementData(BaseModel):
    """JD Element with enriched statements and category definition."""
    statements: List[EnrichedNOCStatement]
    category_definition: Optional[str] = None
    source_attribute: str
    data_source: str = "oasis"  # NEW: "jobforge" | "oasis"

# In profile_parquet_reader.py / mapper.py:
# If parquet lookup returns CoverageStatus.FOUND -> data_source = "jobforge"
# If fallback to OASIS -> data_source = "oasis"
```

### Pattern 4: Fallback Logic

**What:** For each of the 5 tabs, try parquet first. On NOT_FOUND or LOAD_ERROR, fall back to OASIS. Main Duties is unconditional OASIS -- never attempt parquet.
**When to use:** In mapper.py, replacing the direct OASIS-only path for the 5 covered tabs.

```python
# Pattern for each covered tab (Skills example):
result = get_profile_tab("skills", oasis_profile_code)
if result.status == CoverageStatus.FOUND:
    statements = extract_dimension_ratings(result.data, "skills")
    data_source = "jobforge"
else:
    # LOAD_ERROR or NOT_FOUND -- fall back to OASIS
    if result.status == CoverageStatus.LOAD_ERROR:
        logger.warning("Skills parquet LOAD_ERROR for %s: %s", oasis_profile_code, result.error)
    statements = oasis_scraped_skills  # from existing parser.py path
    data_source = "oasis"
```

### Pattern 5: Provenance Extension for Export

**What:** The export compliance block (Section 6.2.3 and 6.2.7 in `export_service.py`) currently cites a single OASIS source URL for all data. Phase 22 must extend this to record per-section data sources.
**When to use:** In `build_compliance_sections()` in `export_service.py`.
**Approach:** Add a `section_sources` dict to `ExportRequest` (or pass it through from frontend); extend `build_compliance_sections()` to iterate over it. Keep existing OASIS section as-is if no parquet sources are present.

```python
# Extend SourceMetadataExport in src/models/export_models.py
class SourceMetadataExport(BaseModel):
    """NOC source metadata for compliance appendix."""
    noc_code: str
    profile_url: str
    scraped_at: datetime
    version: str
    # NEW: per-section source tracking for TBS Directive 32592 compliance
    section_sources: Optional[dict[str, str]] = None
    # dict format: {"skills": "jobforge", "abilities": "jobforge", "key_activities": "oasis", ...}
    # "jobforge" means: source=JobForge gold parquet, file path traceable via JOBFORGE_GOLD_PATH
    # "oasis" means: source=OASIS live scraping, URL in profile_url

# In build_compliance_sections(), when section_sources is present:
# Add a per-tab provenance table to the Section 6.2.3 content block.
```

### Pattern 6: Source Badge CSS and HTML

**What:** Two visually distinct badge variants: green for JobForge, grey for OASIS. Injected at the bottom of each tab panel content area by `renderTabContent()` in `accordion.js`.
**When to use:** Every tab rendered by `renderTabContent()` that has a `data_source` field in the profile data.
**Placement:** Bottom of tab content, below the statement list (per CONTEXT.md decision).

```css
/* Add to static/css/main.css */

/* Source badge -- shown at the bottom of each tab panel */
.source-badge {
    display: inline-block;
    padding: 0.2rem 0.6rem;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 500;
    margin-top: 1rem;
}

.source-badge--jobforge {
    background: #e8f5e9;          /* Light green -- matches success states in app */
    color: #2e7d32;               /* Dark green text */
    border: 1px solid #a5d6a7;
}

.source-badge--oasis {
    background: #f5f5f5;          /* Light grey -- neutral, OASIS is baseline */
    color: #616161;               /* Medium grey text */
    border: 1px solid #e0e0e0;
}
```

```javascript
// In accordion.js renderTabContent(), at the bottom of each tab content block:
function renderSourceBadge(dataSource) {
    const label = dataSource === 'jobforge' ? 'Source: JobForge' : 'Source: OASIS';
    const cssClass = dataSource === 'jobforge' ? 'source-badge--jobforge' : 'source-badge--oasis';
    return `<div class="source-badge-container">
        <span class="source-badge ${cssClass}">${label}</span>
    </div>`;
}
```

### Anti-Patterns to Avoid

- **Using `unit_group_id` column for oasis_* file lookups:** oasis_skills/abilities/knowledges/workactivities/workcontext all use `oasis_code`, NOT `unit_group_id`. Confirmed from DATA-INVENTORY.md. Using `unit_group_id` will return NOT_FOUND for all profiles.
- **Reading element_main_duties.parquet:** This file has only 8 rows (3 profiles). OASIS fallback for Main Duties is unconditional. Never add a parquet path for Main Duties in Phase 22.
- **Stripping whitespace again in profile_parquet_reader.py:** `read_parquet_safe()` in `parquet_reader.py` already calls `df.columns = df.columns.str.strip()` at read time. `extract_dimension_ratings()` will receive clean column names automatically. Do not strip twice.
- **Treating EMPTY_VALID as FOUND:** When a parquet lookup returns FOUND but the dimension list is empty after filtering zeros, this is a genuinely empty profile -- show an empty state or fall back to OASIS. Do NOT display the "Source: JobForge" badge for content that came from OASIS.
- **Adding the source badge in the existing enrichment or mapper flow:** The badge belongs in the UI layer (accordion.js). The backend communicates source via `data_source` string field in the JSON response. Keep UI logic in JS, business logic in Python.
- **Modifying element_* files (labels, example_titles, etc.):** These files are already served correctly by `labels_loader.py`. Phase 22 only changes the 5 oasis_* tab files. Do not touch the element_* path.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Parquet file caching | Dict-based cache in profile_parquet_reader | `parquet_reader.read_parquet_safe()` already caches | Reimplementing cache creates two caches with the same DataFrame; wastes memory and creates staleness risk |
| Column whitespace stripping | `.strip()` in profile_parquet_reader | Already done by `read_parquet_safe()` at read time | Double-stripping is harmless but signals misunderstanding of the infrastructure |
| OASIS scraping fallback | Custom HTTP call in profile_parquet_reader | `OASISScraper.fetch_profile()` + `parser.parse_profile()` in existing `mapper.py` | The existing path is battle-tested; profile_parquet_reader should return CoverageStatus and let mapper decide fallback |
| Tab rendering from scratch | New JS module for parquet tabs | Extend existing `renderTabContent()` in accordion.js | The tab system, skeleton loader, and statement rendering patterns are all already there |
| Custom provenance format | New compliance schema | Extend `SourceMetadataExport.section_sources` | The existing ComplianceSection/ExportData pattern is what the templates consume |
| Source badge accessibility | Custom ARIA widget | Simple `<span>` with `.source-badge` class | Badge is informational-only; a span with readable text is accessible without extra ARIA |

**Key insight:** The entire Phase 22 implementation is plumbing between two already-working systems (parquet_reader + OASIS scraper) and wiring the result to an already-working UI (accordion.js tab panels). Almost nothing needs to be invented from scratch.

---

## Common Pitfalls

### Pitfall 1: oasis_code vs oasis_profile_code Column Name Mismatch

**What goes wrong:** Code calls `lookup_profile(path, "oasis_profile_code", code)` but the oasis_* files use column `"oasis_code"`. Returns NOT_FOUND for every profile.
**Why it happens:** element_* files use `oasis_profile_code`; oasis_* files use `oasis_code`. Two different column names for semantically equivalent data. The DATA-INVENTORY.md documents this clearly.
**How to avoid:** In `profile_parquet_reader.py`, hardcode `OASIS_CODE_COL = "oasis_code"`. Do NOT use `"oasis_profile_code"` for the oasis_* files.
**Warning signs:** Every tab lookup returns NOT_FOUND and falls back to OASIS despite all 900 profiles being present in the parquet.

### Pitfall 2: NOC Code Format Mismatch

**What goes wrong:** API receives `'21211'` (5 digits). Parquet lookup uses `'21211'` unchanged. Returns NOT_FOUND because the parquet stores `'21211.00'`.
**Why it happens:** The profile endpoint receives a NOC code; some NOC codes map to multiple sub-profiles (e.g. `'10020.01'`, `'10020.02'`). The primary sub-profile is usually `.00` but sometimes `.01`.
**How to avoid:** Apply `noc_to_oasis_code()` before any lookup. Try `.00` first; if NOT_FOUND try `.01`. Log a debug message if `.01` was needed (useful for monitoring).
**Warning signs:** NOT_FOUND on a lookup for a known common NOC code like `21211` (Software Engineers).

### Pitfall 3: data_source = "jobforge" When Content Is Empty

**What goes wrong:** Profile has parquet entry (CoverageStatus.FOUND) but all dimension ratings are 0 after filtering. Code still sets `data_source = "jobforge"`. Frontend shows "Source: JobForge" badge for an empty tab.
**Why it happens:** CoverageStatus.FOUND means the profile row exists, not that there is meaningful content. An empty-after-filtering row is an edge case -- profiles can have all-zero ratings for a dimension category.
**How to avoid:** After `extract_dimension_ratings()`, if result is empty list, treat as NOT_FOUND for UI purposes (fall back to OASIS if available, or show empty state). Do NOT mark source as "jobforge" for an empty list. The CONTEXT.md leaves the EMPTY_VALID trigger decision to Claude's discretion -- the recommendation here is: EMPTY_VALID triggers OASIS fallback (empty parquet row is no better than no row for the user).
**Warning signs:** "Source: JobForge" badge on a tab with no content, or tab shows "No data available" with JobForge badge.

### Pitfall 4: Double-Nesting Skills / Abilities / Knowledge

**What goes wrong:** Currently, `mapper._map_skills_enriched()` combines Skills + Abilities + Knowledge into a single `skills` element. Phase 22 needs them as separate tabs. If Phase 22 changes the enrichment path without updating `renderTabContent()` in accordion.js, the Abilities and Knowledge tabs will show the same data as Skills.
**Why it happens:** Existing `TAB_CONFIG.abilities` and `TAB_CONFIG.knowledge` in accordion.js both use `dataKey: 'skills'` and filter by `source_attribute`. When parquet data is separate per-tab, the `source_attribute` filter approach may not work because parquet rows don't carry a `source_attribute` -- they carry column names.
**How to avoid:** Phase 22 must add separate top-level keys in `ProfileResponse`: `skills_tab`, `abilities_tab`, `knowledge_tab` (or similar) so each tab has its own statement list. Alternatively, keep the combined `skills` key but add properly tagged `source_attribute` to each statement. The safest approach is to keep the combined `skills` field (OASIS path unchanged) and add parquet-sourced per-tab fields separately, with `data_source` per tab.
**Warning signs:** All three tabs (Skills, Abilities, Knowledge) showing identical content.

### Pitfall 5: Export Provenance Breaking Existing Exports

**What goes wrong:** Adding `section_sources` to `SourceMetadataExport` breaks existing exports that serialize this model.
**Why it happens:** Pydantic v2 serialization is strict; any non-optional new field breaks existing callers that provide `SourceMetadataExport` without it.
**How to avoid:** Make `section_sources` Optional with default `None`. Existing exports that do not pass this field continue to work. The compliance block generation checks `if request.source_metadata.section_sources` before rendering the per-tab provenance table.
**Warning signs:** 422 Validation Error on `/api/export/pdf` or `/api/export/docx` after adding the field.

### Pitfall 6: Loading State Mismatch

**What goes wrong:** Phase 22 adds parquet reads to the profile load path. Parquet reads are synchronous and fast (< 5ms for cached data). If a developer adds them as async calls, they will break the existing synchronous profile load flow.
**Why it happens:** Parquet is disk I/O; developers assume it needs async treatment.
**How to avoid:** Keep parquet reads synchronous. The existing `handleResultClick()` in `main.js` is async because of the OASIS HTTP call (`api.getProfile(code)`). Parquet reads return in memory (after first load, data is cached). No additional loading state is needed for the parquet path -- the existing skeleton on `jdSections` covers the full profile load including parquet.
**Warning signs:** A new loading spinner appears for the parquet portion of the profile load, creating visual jitter.

### Pitfall 7: Source Badge Tooltip for Main Duties

**What goes wrong:** Main Duties tab always shows "Source: OASIS" even when the user might not understand why (permanent ETL gap). No additional indication that this is permanent vs per-profile.
**Why it happens:** CONTEXT.md leaves this to Claude's discretion. The decision: add an optional `title` attribute to the OASIS badge for Main Duties tabs that reads "Main Duties always served from OASIS (ETL pending)". This is low-friction -- it does not change the badge text or layout, but surfaces the reason on hover.
**How to avoid:** Pass an optional `badge_tooltip` string alongside `data_source` for tabs where a tooltip is meaningful.
**Warning signs:** Support questions about why Main Duties is OASIS when the user expects JobForge data.

---

## Code Examples

### Reading a Single Tab from Parquet

```python
# Source: parquet_reader.py + DATA-INVENTORY.md profile code format
from src.services.profile_parquet_reader import get_profile_tab, extract_dimension_ratings
from src.models.parquet import CoverageStatus

def get_skills_from_parquet(noc_code: str):
    """Try parquet first, return (statements, data_source) tuple."""
    for candidate_code in [f"{noc_code}.00", f"{noc_code}.01"]:
        result = get_profile_tab("skills", candidate_code)

        if result.status == CoverageStatus.FOUND:
            ratings = extract_dimension_ratings(result.data, "skills")
            if ratings:  # Non-empty ratings = real JobForge data
                return ratings, "jobforge"
            # Empty ratings after filtering = treat as not found
            break  # Don't try .01 if .00 found but empty

        elif result.status == CoverageStatus.NOT_FOUND:
            continue  # Try next candidate code

        else:  # LOAD_ERROR
            logger.warning("Skills parquet LOAD_ERROR for %s: %s", noc_code, result.error)
            break

    return None, "oasis"  # Signal: use OASIS fallback
```

### Adding data_source to ProfileResponse

```python
# In src/models/responses.py -- extend EnrichedJDElementData
class EnrichedJDElementData(BaseModel):
    """JD Element with enriched statements and category definition."""
    statements: List[EnrichedNOCStatement]
    category_definition: Optional[str] = None
    source_attribute: str
    data_source: str = "oasis"  # "jobforge" or "oasis"

# Usage in mapper.py (skills example):
skills_statements, skills_source = get_skills_from_parquet(noc_code)
if skills_source == "oasis":
    skills_statements = [existing OASIS path...]

return {
    ...
    'skills': EnrichedJDElementData(
        statements=skills_statements,
        category_definition=guide_csv.get_category_definition('skills'),
        source_attribute="Skills",
        data_source=skills_source,  # NEW
    ),
    ...
}
```

### Source Badge in accordion.js

```javascript
// Source: existing renderTabContent() pattern in accordion.js

function renderSourceBadge(dataSource, tooltip) {
    const label = dataSource === 'jobforge' ? 'Source: JobForge' : 'Source: OASIS';
    const cssClass = dataSource === 'jobforge'
        ? 'source-badge source-badge--jobforge'
        : 'source-badge source-badge--oasis';
    const titleAttr = tooltip ? ` title="${escapeHtml(tooltip)}"` : '';
    return `<div class="source-badge-container">
                <span class="${cssClass}"${titleAttr}>${label}</span>
            </div>`;
}

// Usage inside renderTabContent() for the skills panel:
const skillsData = profile.skills;
skillsPanel.innerHTML = renderStatementsPanel(
    skillsData?.statements || [],
    TAB_CONFIG.skills.sections,
    'skills',
    state.selections.skills || []
) + renderSourceBadge(skillsData?.data_source || 'oasis');
```

### Provenance Extension in export_service.py

```python
# Source: existing build_compliance_sections() in src/services/export_service.py
# Extend Section 6.2.3 to include per-tab source table

def build_compliance_sections(request: ExportRequest) -> List[ComplianceSection]:
    sections = []

    # Section 6.2.3: Data Sources (extend for per-tab provenance)
    source_content = {
        "data_steward": "Employment and Social Development Canada (ESDC)",
        "authoritative_source": "National Occupational Classification (NOC)",
        "access_method": "Direct retrieval from OASIS and JobForge 2.0 gold parquet",
        "source_url": request.source_metadata.profile_url,
        "retrieval_timestamp": request.source_metadata.scraped_at.isoformat(),
        "noc_version": request.source_metadata.version,
    }

    # Add per-section sources if provided (PROF-03 requirement)
    section_sources = getattr(request.source_metadata, 'section_sources', None)
    if section_sources:
        source_content["section_sources"] = {
            section: {
                "source": src,
                "detail": (
                    f"JobForge 2.0 gold parquet (JOBFORGE_GOLD_PATH/oasis_{section}.parquet)"
                    if src == "jobforge"
                    else f"OASIS live scraping ({request.source_metadata.profile_url})"
                )
            }
            for section, src in section_sources.items()
        }

    sections.append(ComplianceSection(
        section_id="6.2.3",
        title="Data Sources (Directive 6.2.3)",
        content=source_content,
    ))
    # ... rest of compliance sections unchanged
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| All 5 tabs from OASIS scraping | 5 tabs from parquet with OASIS fallback | Phase 22 | Eliminates live HTTP dependency for covered tabs |
| Single OASIS source in compliance block | Per-section sources in compliance block | Phase 22 | Satisfies TBS Directive 32592 traceability requirement |
| No source indication in UI | Source badge per tab | Phase 22 | Users see where each tab's data originates |
| labels_loader serves work_context | work_context stays in labels_loader | Unchanged by Phase 22 | Work context already served from parquet; no regression |

**Note on existing labels_loader:** `labels_loader.get_work_context_filtered()` already reads `oasis_workcontext.parquet` for the Work Context tab (effort/responsibility split). Phase 22 should NOT replace this with `profile_parquet_reader.get_profile_tab("work_context", ...)` unless the data shapes are compatible. Verify whether `labels_loader` and the new parquet_reader would both cache the same DataFrame (they should, since `parquet_reader.read_parquet_safe()` uses a module-level dict keyed by path string). If labels_loader continues to read work_context directly via `pd.read_parquet()`, that is a second cache -- investigate and unify if possible. This is a Phase 22 decision point, not a blocker.

---

## Open Questions

1. **Labels_loader work_context overlap**
   - What we know: `labels_loader.get_work_context_filtered()` reads `oasis_workcontext.parquet` directly via `pd.read_parquet()` (not via `parquet_reader.py`). Phase 22 will also read this file via `profile_parquet_reader.get_profile_tab("work_context", ...)`.
   - What's unclear: Will there be two caches for the same file (labels_loader's `self._work_context_df` dict and parquet_reader's `_cache` dict)?
   - Recommendation: If Phase 22 adds a parquet path for work_context display (the badge), wire it to `parquet_reader.lookup_profile()` and keep labels_loader as-is for the effort/responsibility split. They can both cache the same DataFrame separately -- the file is small and this avoids a labels_loader refactor.

2. **Double-failure (both parquet LOAD_ERROR and OASIS down)**
   - What we know: CONTEXT.md defers to Claude's discretion for double-failure treatment, consistent with existing error handling.
   - Recommendation: Render the tab with a friendly "Data temporarily unavailable" message and `aria-live="polite"` for screen reader announcement. Do NOT show the source badge in double-failure state. This is consistent with the existing `showError()` pattern in `main.js`.

3. **Separate top-level keys vs combined skills field**
   - What we know: Currently `profile.skills.statements` contains Skills + Abilities + Knowledge combined (from `_map_skills_enriched()`). The accordion.js tabs filter by `source_attribute`. Phase 22 needs parquet data to appear per-tab.
   - What's unclear: Whether to split into `skills_tab`, `abilities_tab`, `knowledge_tab` top-level keys (breaking change to ProfileResponse) or keep the combined `skills` key (no breaking change, but adds complexity to badge assignment).
   - Recommendation: Add separate top-level keys (`abilities` and `knowledge`) alongside the existing `skills` key. `skills` continues to serve the combined view (for backward compatibility with accordion sections). New keys serve the per-tab views with their own `data_source`. This is the safest schema evolution.

4. **EMPTY_VALID trigger for OASIS fallback**
   - What we know: CONTEXT.md leaves this to Claude's discretion.
   - Recommendation: EMPTY_VALID (parquet FOUND but all ratings are 0 after filtering) triggers OASIS fallback. An all-zero parquet row is no better than an OASIS miss for the user -- the content would be an empty tab. If OASIS also has no data, show empty state.

---

## Sources

### Primary (HIGH confidence)

- Direct codebase inspection:
  - `src/models/parquet.py` -- CoverageStatus, ParquetResult (Phase 21 output)
  - `src/services/parquet_reader.py` -- read_parquet_safe, lookup_profile (Phase 21 output)
  - `src/services/labels_loader.py` -- LabelsLoader, existing work_context path
  - `src/services/mapper.py` -- JDMapper.to_jd_elements(), _map_skills_enriched()
  - `src/models/responses.py` -- ProfileResponse, EnrichedJDElementData
  - `src/models/export_models.py` -- SourceMetadataExport, ComplianceSection, ExportData
  - `src/services/export_service.py` -- build_compliance_sections()
  - `src/utils/oasis_provenance.py` -- OASIS_SOURCE_MAPPING, OaSISTableMetadata
  - `static/js/accordion.js` -- renderTabContent(), TAB_CONFIG, renderSourceBadge pattern
  - `static/js/profile_tabs.js` -- TabController, ARIA tab management
  - `templates/index.html` -- tab panel HTML structure (panel-skills, panel-abilities, etc.)
  - `static/css/main.css` -- .oasis-code-badge, .noc-badge, .tab-button, .tab-panel patterns
  - `static/css/skeleton.css` -- .skeleton shimmer animation
  - `src/routes/api.py` -- /api/profile endpoint

- Planning artifacts from Phase 21:
  - `.planning/phases/21-data-exploration/DATA-INVENTORY.md` -- oasis_* file schemas, column names, key column names
  - `.planning/phases/21-data-exploration/GAP-ANALYSIS.md` -- which tabs use parquet vs OASIS

### Secondary (MEDIUM confidence)

- Phase 22 CONTEXT.md -- locked decisions on badge placement, badge text, fallback behavior, provenance format
- `.planning/STATE.md` -- locked decisions on column names and element_main_duties.parquet exclusion

### Tertiary (LOW confidence)

None -- all claims verified from codebase inspection and Phase 21 planning artifacts.

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- all libraries verified present, no new dependencies
- Architecture: HIGH -- all patterns derived from existing project code and Phase 21 artifacts
- Pitfalls: HIGH -- all pitfalls derived from actual code inspection and Phase 21 research
- Schema extensions: HIGH -- pydantic v2 optional field pattern verified in existing models

**Research date:** 2026-03-07
**Valid until:** 2026-06-07 (parquet files stable; project dependencies stable)
