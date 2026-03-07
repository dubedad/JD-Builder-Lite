# Phase 21: Data Exploration - Research

**Researched:** 2026-03-07
**Domain:** Pandas parquet reading, Python type design, stdlib logging
**Confidence:** HIGH

---

## Summary

Phase 21 has two deliverables: a developer-facing inventory/gap analysis document (DATA-01, DATA-02) and a code change introducing `CoverageStatus` with warning logging (DATA-03, DATA-04). Both deliverables were researched against the actual gold parquet files on disk at `/Users/victornishi/Documents/GitHub/JobForge-2.0/data/gold/`.

The gold directory contains **25 parquet files**. Five files (oasis_skills, oasis_abilities, oasis_knowledges, oasis_workactivities, oasis_workcontext) provide full 900-profile coverage for the profile tab data Phase 22 will consume. Four OASIS data fields have **no adequate parquet equivalent** and must continue using live OASIS scraping: Main Duties (parquet has only 3 profiles), Interests, Personal Attributes, and Core Competencies/Career Mobility. This gap is confirmed from file inspection, not inference.

`CoverageStatus` does not exist in the codebase yet. The project uses pydantic v2 and Python 3.14's `enum.StrEnum` for typed enumerations. The existing pattern in `src/models/noc.py` (using `str, Enum` for `EnrichmentSource`) is the correct model to follow. Warning logging uses stdlib `logging` with `logger = logging.getLogger(__name__)` — the pattern is already established in `src/services/enrichment_service.py` and five other service files.

**Primary recommendation:** Define `CoverageStatus` as a `StrEnum` in `src/models/parquet.py` (a new file), add a `ParquetReader` helper in `src/services/parquet_reader.py` that wraps `pd.read_parquet` with the three distinct error states, and wire `logger.warning()` for load errors and unexpected data. Write the inventory and gap analysis documents to `.planning/phases/21-data-exploration/`.

---

## Standard Stack

The established libraries for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pandas | 2.2.3 | Read parquet files | Already installed and used throughout project |
| pyarrow | 23.0.0 | Parquet engine used by pandas | Already installed as pandas dependency |
| stdlib logging | 3.14 stdlib | Warning emission | Project-wide pattern: `logging.getLogger(__name__)` |
| enum.StrEnum | 3.11+ stdlib | CoverageStatus type | Project already uses `str, Enum`; StrEnum is cleaner |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pydantic v2 | 2.12.5 | Data validation/typing for result wrapper | If CoverageResult needs to be serialisable to JSON |
| typing.Literal | 3.14 stdlib | Narrow type annotations | Type hints only — no runtime overhead |
| pathlib.Path | 3.14 stdlib | File path handling | Already used in `labels_loader.py` |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| stdlib logging | print() | print() is already used in labels_loader; logging is preferred in new code for level control and handler configurability |
| StrEnum | TypedDict with Literal | TypedDict is structural, not nominal; StrEnum gives .value access and is more idiomatic for state enums |
| pydantic BaseModel | dataclass | Either works; pydantic preferred since models/ already uses it exclusively |

**Installation:** No new packages required. All needed libraries are already installed.

---

## Architecture Patterns

### Recommended File Layout for Phase 21

```
src/
├── models/
│   ├── parquet.py          # NEW: CoverageStatus enum + ParquetResult dataclass
│   └── noc.py              # Existing — do NOT modify
├── services/
│   └── parquet_reader.py   # NEW: read_parquet_with_status() helper + warning logging
.planning/
└── phases/
    └── 21-data-exploration/
        ├── 21-RESEARCH.md  # This file
        ├── DATA-INVENTORY.md   # DATA-01: inventory document
        └── GAP-ANALYSIS.md     # DATA-02: gap analysis document
```

The two documents (DATA-INVENTORY.md, GAP-ANALYSIS.md) are developer-facing planning artifacts, not runtime code. They live in the phase directory alongside this RESEARCH.md.

### Pattern 1: CoverageStatus as StrEnum

**What:** A three-state enum distinguishing parquet failure modes.
**When to use:** Wherever code reads from a parquet file and must signal result state to the caller.
**Why three states matter:** The existing `labels_loader.py` collapses all failures into `return []`. A `[]` result is ambiguous — it could mean file missing, profile not in file, or profile has no data. Phase 22 and 23 need to know the difference to decide whether to fall back to OASIS.

```python
# Source: project pattern from src/models/noc.py (EnrichmentSource uses str + Enum)
# File: src/models/parquet.py

import enum
from dataclasses import dataclass, field
from typing import Generic, TypeVar, Optional

T = TypeVar("T")


class CoverageStatus(str, enum.Enum):
    """Outcome of a parquet read operation.

    Three distinct states that must NOT be collapsed:
    - LOAD_ERROR: file is missing, corrupt, or unreadable
    - NOT_FOUND: file loaded, but no row matches the requested profile code
    - FOUND: file loaded and row(s) matched (data may still be empty)
    """
    LOAD_ERROR = "load_error"
    NOT_FOUND = "not_found"
    FOUND = "found"


@dataclass
class ParquetResult(Generic[T]):
    """Typed result of a parquet lookup with coverage status."""
    status: CoverageStatus
    data: Optional[T] = None
    error: Optional[str] = None   # Populated when status == LOAD_ERROR
```

### Pattern 2: ParquetReader with Warning Logging

**What:** A helper that wraps `pd.read_parquet` and returns `ParquetResult`, emitting `logger.warning()` for the two error states.
**When to use:** All parquet reads in Phase 22 and Phase 23 go through this helper.

```python
# File: src/services/parquet_reader.py
# Source: pattern from src/services/enrichment_service.py (logger = logging.getLogger(__name__))

import logging
import pandas as pd
from pathlib import Path
from src.models.parquet import CoverageStatus, ParquetResult

logger = logging.getLogger(__name__)

# Module-level cache: path -> DataFrame (loaded once per process)
_cache: dict[str, pd.DataFrame] = {}


def read_parquet_safe(path: Path) -> "tuple[CoverageStatus, pd.DataFrame | None, str | None]":
    """Load a parquet file with explicit status reporting.

    Returns:
        (LOAD_ERROR, None, error_msg)  -- file missing or corrupt
        (FOUND, df, None)              -- file loaded (df may have zero rows for profile)

    Emits logger.warning() on LOAD_ERROR.
    Caller is responsible for checking if df is empty after filtering.
    """
    key = str(path)
    if key in _cache:
        return CoverageStatus.FOUND, _cache[key], None

    if not path.exists():
        msg = f"Parquet file not found: {path}"
        logger.warning("[ParquetReader] %s", msg)
        return CoverageStatus.LOAD_ERROR, None, msg

    try:
        df = pd.read_parquet(path)
        _cache[key] = df
        return CoverageStatus.FOUND, df, None
    except Exception as exc:
        msg = f"Failed to load parquet {path}: {exc}"
        logger.warning("[ParquetReader] %s", msg)
        return CoverageStatus.LOAD_ERROR, None, msg


def lookup_profile(
    path: Path,
    code_col: str,
    profile_code: str,
    data_col: str,
) -> "ParquetResult[list]":
    """Look up rows for a profile code and return the data column values.

    Returns:
        ParquetResult with status:
          - LOAD_ERROR if file cannot be read
          - NOT_FOUND if no rows match profile_code
          - FOUND with data list (may be empty list if rows exist but data_col is null)
    """
    status, df, error = read_parquet_safe(path)
    if status == CoverageStatus.LOAD_ERROR:
        return ParquetResult(status=CoverageStatus.LOAD_ERROR, error=error)

    matching = df[df[code_col] == profile_code]
    if matching.empty:
        logger.warning(
            "[ParquetReader] Profile %s not found in %s (NOT_FOUND)",
            profile_code, path.name
        )
        return ParquetResult(status=CoverageStatus.NOT_FOUND)

    values = matching[data_col].dropna().tolist()
    return ParquetResult(status=CoverageStatus.FOUND, data=values)
```

### Pattern 3: Inventory and Gap Analysis Documents

**What:** Two markdown files written as planning artifacts, not committed as code.
**Format for DATA-INVENTORY.md:**

```markdown
# JobForge Gold Parquet Inventory
**Path:** /Users/victornishi/Documents/GitHub/JobForge-2.0/data/gold/
**Last verified:** 2026-03-07

| File | Rows | Unique Profiles | Key Columns | OASIS Element Replaced |
|------|------|-----------------|-------------|------------------------|
| element_labels.parquet | 900 | 900 oasis_profile_codes | Label | NOC occupational label |
...
```

**Format for GAP-ANALYSIS.md:**

```markdown
# OASIS Data Gap Analysis
**Named gaps — not inferred:**

| OASIS Data Field | Gap Status | Reason | Action |
|------------------|------------|--------|--------|
| Main Duties / Key Activities | PERMANENT GAP | element_main_duties.parquet has 8 rows / 3 profiles | OASIS scraping |
...
```

### Anti-Patterns to Avoid

- **Collapsing CoverageStatus states:** `return []` for all failures is the existing bug. The new code must return `CoverageStatus` so callers can distinguish file error from missing profile from found-but-empty.
- **Caching disabled parquet at module import:** Labels loader loads lazily. Match this pattern — don't load all 25 parquet files at startup. Use module-level cache keyed by path.
- **Using `print()` for warnings in new code:** Existing `labels_loader.py` uses `print(f"[LabelsLoader] ...")`. New `parquet_reader.py` must use `logger.warning()` so it participates in Flask's log handler configuration.
- **Silent exception swallowing:** The existing `_load_exclusions` etc. methods in `labels_loader.py` have bare `except: return False` — no logging at all. The new reader must not replicate this.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Parquet reading | Custom binary parser | `pd.read_parquet(path)` | pandas+pyarrow already installed, handles all parquet formats |
| File existence check | Manual `open()` try/except | `path.exists()` then `pd.read_parquet()` | Gives cleaner error separation: FileNotFoundError vs ArrowInvalid |
| Column whitespace stripping | Regex replace | `col.strip()` on each column name after read | Sufficient for the space-only contamination observed in gold files |
| Module-level singleton | Class with complex lifecycle | Dict cache `_cache: dict[str, pd.DataFrame]` at module level | Files change rarely; simple dict per process is appropriate for single-user app |

**Key insight:** All gold parquet files fit comfortably in memory (27 MB total across 25 files). No lazy streaming or chunked reading is needed — load once, cache in dict, filter in pandas.

---

## Common Pitfalls

### Pitfall 1: Conflating NOT_FOUND with LOAD_ERROR

**What goes wrong:** Caller treats both as "fallback to OASIS" when actually LOAD_ERROR means infrastructure problem (broken config, wrong path) while NOT_FOUND means data gap (profile exists in OASIS but not in parquet). These require different responses.
**Why it happens:** Current `labels_loader.py` returns `[]` for everything; callers never needed to distinguish.
**How to avoid:** `CoverageStatus` enum forces callers to handle each case explicitly. Phase 22 fallback logic: `if result.status in (NOT_FOUND, LOAD_ERROR)` — but log differently: `LOAD_ERROR` should also alert developer that path config may be broken.
**Warning signs:** Search for `return []` or `return False` in parquet-reading code.

### Pitfall 2: Column Whitespace Contamination in OASIS Files

**What goes wrong:** Code does `df['Writing']` but the column is actually `'Writing  '` (two trailing spaces). KeyError at runtime.
**Why it happens:** Gold parquet inherits column names from source CSVs which have whitespace. Confirmed in: oasis_skills (6 cols), oasis_abilities (14 cols), oasis_workactivities (3 cols), oasis_workcontext (3 cols), oasis_knowledges (1 col).
**How to avoid:** After `pd.read_parquet()`, run `df.columns = df.columns.str.strip()` before any column access. This is the blanket fix for all OASIS-prefix files. Alternatively normalize at read time in `read_parquet_safe`.
**Warning signs:** KeyError on a column name that looks correct when printed, or column access returning NaN for values that exist.

### Pitfall 3: element_main_duties.parquet Looks Like a Valid Parquet

**What goes wrong:** Code reads `element_main_duties.parquet`, gets `CoverageStatus.FOUND`, and concludes parquet coverage is adequate. In fact only 3 of 900 profiles are present.
**Why it happens:** The file is structurally valid; `NOT_FOUND` only fires per-profile-lookup, not on load.
**How to avoid:** The gap analysis document (DATA-02) must explicitly document that `element_main_duties.parquet` has 8 rows / 3 profiles, and Phase 22 OASIS fallback for Main Duties is unconditional (do not even attempt parquet read). Code comment in Phase 22 should reference the gap analysis.
**Warning signs:** Main Duties parquet lookup returning `NOT_FOUND` for every real query in production.

### Pitfall 4: ArrowInvalid vs FileNotFoundError vs PermissionError

**What goes wrong:** Generic `except Exception` catches all three but logs the same message. Debugging path errors is impossible.
**Why it happens:** Convenience.
**How to avoid:** In `read_parquet_safe`, check `path.exists()` first (FileNotFoundError and PermissionError become explicit), then `pd.read_parquet()` in a try/except that catches `Exception` and logs the exception type. This is sufficient — don't over-engineer.
**Warning signs:** Warning log says "Failed to load parquet" but doesn't clarify if file is missing vs corrupt.

### Pitfall 5: oasis_profile_code Format Mismatch

**What goes wrong:** Caller queries with `'10020'` but profile codes in parquet are `'10020.01'`, `'10020.02'`, etc. Returns `NOT_FOUND` when data exists under sub-profile codes.
**Why it happens:** 516 NOC unit groups map to 900 OASIS profile codes — some NOC codes have multiple sub-profiles (e.g. `10020.01` through `10020.04`).
**How to avoid:** The inventory document (DATA-01) must call out the 900-vs-516 discrepancy. Phase 22 lookup must use `oasis_profile_code` (with decimal) not `unit_group_id` or `noc_code`. The `element_labels.parquet` lookup column is `oasis_profile_code`, not `noc_code`.
**Warning signs:** `NOT_FOUND` for a NOC code that ends in a round number like `10020` when the parquet has `10020.01`, etc.

---

## Code Examples

Verified patterns from official sources and actual project code:

### Reading parquet with pandas

```python
# Source: pandas 2.2.3, verified by running against actual gold files
import pandas as pd
from pathlib import Path

path = Path("/Users/victornishi/Documents/GitHub/JobForge-2.0/data/gold/element_labels.parquet")

# FileNotFoundError raised if file missing (not ArrowInvalid)
# ArrowInvalid raised if file exists but is corrupt
df = pd.read_parquet(path)

# Column whitespace strip (verified needed for oasis_* files)
df.columns = df.columns.str.strip()

# Filtering by profile code
matching = df[df["oasis_profile_code"] == "21211.00"]
# matching is empty DataFrame (not None) if not found
values = matching["Label"].tolist()  # [] if empty
```

### CoverageStatus type design

```python
# Source: project pattern from src/models/noc.py (EnrichmentSource)
import enum

class CoverageStatus(str, enum.Enum):
    LOAD_ERROR = "load_error"
    NOT_FOUND = "not_found"
    FOUND = "found"

# Usage: callers pattern-match on status
result = lookup_profile(...)
if result.status == CoverageStatus.LOAD_ERROR:
    logger.warning("Infrastructure problem: %s", result.error)
    # fall back to OASIS
elif result.status == CoverageStatus.NOT_FOUND:
    # Profile not in parquet — expected for many profiles
    # fall back to OASIS
else:  # FOUND
    return result.data
```

### Warning logging pattern

```python
# Source: src/services/enrichment_service.py lines 4-8 (project convention)
import logging

logger = logging.getLogger(__name__)

# Load error
logger.warning("[ParquetReader] Parquet file not found: %s", path)

# Not found (lower severity — expected data gap)
logger.warning("[ParquetReader] Profile %s not found in %s", profile_code, path.name)
```

### Confirming exception types

```python
# Verified by test against actual pyarrow 23.0.0:
# - Path does not exist -> FileNotFoundError (from pathlib check, before pd.read_parquet)
# - File exists but corrupt -> pyarrow.lib.ArrowInvalid
# - File exists and valid -> returns DataFrame

# Recommended separation:
if not path.exists():
    # FileNotFoundError / PermissionError territory
    msg = f"File not found: {path}"
    logger.warning("[ParquetReader] %s", msg)
    return CoverageStatus.LOAD_ERROR, None, msg

try:
    df = pd.read_parquet(path)
except Exception as exc:
    # ArrowInvalid or other read failure
    msg = f"Failed to read {path.name}: {type(exc).__name__}: {exc}"
    logger.warning("[ParquetReader] %s", msg)
    return CoverageStatus.LOAD_ERROR, None, msg
```

---

## Complete Gold Parquet Inventory (DATA-01 Source Data)

Verified by direct file inspection on 2026-03-07. Path: `/Users/victornishi/Documents/GitHub/JobForge-2.0/data/gold/`

### Profile / Occupational Content (element_* and oasis_* files)

| File | Rows | Unique Profiles | OASIS Field Replaced/Supplemented | Whitespace Cols |
|------|------|-----------------|------------------------------------|-----------------|
| element_labels.parquet | 900 | 900 oasis_profile_codes | NOC occupational label / title | None |
| element_lead_statement.parquet | 900 | 900 oasis_profile_codes | Lead statement / career overview | None |
| element_example_titles.parquet | 18,666 | 900 oasis_profile_codes | Example job titles ("Also known as") | None |
| element_employment_requirements.parquet | 2,851 | 900 oasis_profile_codes | Employment requirements | None |
| element_exclusions.parquet | 3,074 | 870 oasis_profile_codes | NOC exclusions (30 profiles have none) | None |
| element_workplaces_employers.parquet | 3,418 | 900 oasis_profile_codes | Workplaces and employers | None |
| element_additional_information.parquet | 1,158 | 695 oasis_profile_codes | Additional information (EN) | None |
| **element_main_duties.parquet** | **8** | **3 oasis_profile_codes** | **Main Duties — CRITICAL GAP** | None |
| oasis_abilities.parquet | 900 | 900 oasis_codes (=profile codes) | Abilities ratings (50 ability dimensions) | 14 cols |
| oasis_skills.parquet | 900 | 900 oasis_codes | Skills ratings (37 skill dimensions) | 6 cols |
| oasis_knowledges.parquet | 900 | 900 oasis_codes | Knowledge ratings (48 knowledge areas) | 1 col |
| oasis_workactivities.parquet | 900 | 900 oasis_codes | Work Activities ratings (44 dimensions) | 3 cols |
| oasis_workcontext.parquet | 900 | 900 oasis_codes | Work Context ratings (70 context dimensions) | 3 cols |

### Dimensional / Reference Files

| File | Rows | Unique IDs | Purpose | Replaces OASIS? |
|------|------|-----------|---------|-----------------|
| dim_noc.parquet | 516 | 516 noc_codes | NOC unit group definitions and class_definition text | Supplements — class_definition matches OASIS profile text |
| dim_occupations.parquet | 212 | 210 occupation_group_ids | Job Architecture taxonomy (job families/functions) | No OASIS equivalent |
| job_architecture.parquet | 1,987 | 363 noc_2021_uids | GC job titles mapped to NOC codes | No OASIS equivalent |

### Labour Market / Financial Files (not relevant to profile service)

| File | Rows | Purpose |
|------|------|---------|
| cops_employment.parquet | 516 | Employment projections 2023–2033 |
| cops_employment_growth.parquet | 516 | Employment growth projections |
| cops_immigration.parquet | 516 | Immigration intake data |
| cops_other_replacement.parquet | 516 | Other replacement labour data |
| cops_other_seekers.parquet | 516 | Other job seekers data |
| cops_retirement_rates.parquet | 516 | Retirement rate projections |
| cops_retirements.parquet | 516 | Retirement count projections |
| cops_school_leavers.parquet | 516 | School leavers data |
| fact_og_pay_rates.parquet | 991 | TBS occupational group pay rates |

---

## Gap Analysis (DATA-02 Source Data)

Verified by direct file inspection. These gaps are named, not inferred.

| OASIS Data Field | Gap Status | Evidence | Required Action |
|-----------------|------------|----------|-----------------|
| Main Duties / Key Activities | PERMANENT UNTIL ETL RUNS | element_main_duties.parquet: 8 rows, 3 profiles only (source CSV has 4,991 rows / 900 profiles) | OASIS live scraping is the only source; no parquet lookup should be attempted |
| Interests / Holland Codes | NO GOLD PARQUET | interests_oasis_2023_v1.0.csv exists in source/ but no gold equivalent | Continue serving from source CSV via existing LabelsLoader |
| Personal Attributes | NO GOLD PARQUET | personal-attributes_oasis_2023_v1.0.csv exists in source/ but no gold equivalent | Continue serving from source CSV via existing LabelsLoader |
| Core Competencies | NO DATA AT ALL | No gold parquet, no silver, no source CSV | OASIS live scraping only |
| Career Mobility / Progression | NO DATA AT ALL | No parquet file or source CSV found | OASIS live scraping only |

**Note:** Interests and Personal Attributes are served from **source CSVs** (not live OASIS scraping). The gap is "no gold parquet" but the current LabelsLoader already handles this correctly. No regression risk.

---

## State of the Art

| Old Approach | Current Approach | Impact |
|--------------|------------------|--------|
| Hardcoded exception swallowing (`except: return False`) in labels_loader | `CoverageStatus` enum + `logger.warning()` | Failures are visible and distinguishable |
| `return []` for all failure modes | Three-state `ParquetResult` | Phase 22/23 callers can decide whether to fall back |
| `print()` in labels_loader for load confirmation | `logger.warning()` / `logger.info()` in new code | Participates in Flask log handler; level-filterable |

**Deprecated/outdated patterns to avoid in Phase 21 code:**
- `print(f"[LabelsLoader] ...")` — use `logger.*` in new files
- `except Exception: return False` — always log before returning error state

---

## Open Questions

1. **Should labels_loader.py be migrated to use CoverageStatus in Phase 21?**
   - What we know: labels_loader already reads 8 parquet files successfully; CoverageStatus is defined in Phase 21 but the labels_loader refactor is listed as "out of scope" in REQUIREMENTS.md ("Rewrite labels_loader as full replacement — Risky scope; DATA-04 fixes the silent failure; full rewrite is v5.1 hardening")
   - What's unclear: DATA-04 says "any parquet file that fails to load produces a visible warning" — does this require retroactively fixing labels_loader or only new parquet_reader code?
   - Recommendation: Wire warning logging into labels_loader's silent exception paths (one-line `logger.warning()` additions only), do NOT refactor to CoverageStatus. New parquet_reader uses CoverageStatus. This satisfies DATA-04 without the v5.1 refactor scope.

2. **Where should the module-level parquet cache live?**
   - What we know: parquet_reader.py will be imported by Phase 22 (profile service) and Phase 23 (search service). Both need the same cached DataFrames.
   - What's unclear: Whether a module-level dict (process-scoped singleton) is sufficient or if Flask app context is needed.
   - Recommendation: Module-level dict is sufficient for a single-process single-user local app. Flask app context is overkill here.

3. **Which lookup key to use: oasis_profile_code or unit_group_id?**
   - What we know: oasis_skills/abilities/knowledges/workactivities/workcontext use `oasis_code` (= oasis_profile_code format: `'00010.00'`). element_* files use `oasis_profile_code`. dim_noc uses `noc_code` (= 5-digit string, no decimal).
   - What's unclear: What key will Phase 22 receive from the profile endpoint? Currently it receives a NOC code like `'21211'`.
   - Recommendation: Phase 22 plan must document the key transformation: `noc_code '21211'` -> `oasis_profile_code '21211.00'` for element_* and oasis_* files; `unit_group_id '21211'` for dim_noc. Document this in parquet_reader lookup calls.

---

## Sources

### Primary (HIGH confidence)
- Direct file inspection via `pd.read_parquet()` on all 25 gold parquet files — schemas, row counts, unique profile counts, whitespace contamination all verified by running Python against actual data
- Project source code inspection: `src/models/noc.py`, `src/models/responses.py`, `src/services/labels_loader.py`, `src/services/enrichment_service.py`, `src/app.py`
- `pyarrow 23.0.0` exception type verified by creating a corrupt temp file and catching the error
- Python 3.14.3 available types (`enum.StrEnum`, `typing.Literal`, `dataclasses`) verified by import test

### Secondary (MEDIUM confidence)
- `element_main_duties.parquet` gap confirmed against source CSV `main-duties_oasis-2023_v1.0.csv` (4,991 rows, 900 profiles in source vs 8 rows / 3 profiles in parquet)
- Interests / Personal Attributes gap confirmed by checking all filenames in `data/source/` — source CSVs exist, no gold parquet equivalent
- Core Competencies gap confirmed: no file matching "core_competencies" or "competenc" in any of gold/, silver/, bronze/, or source/

### Tertiary (LOW confidence)
- None — all claims verified directly against files on disk

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all libraries verified present with exact versions
- Architecture: HIGH — CoverageStatus pattern derived from existing project conventions in src/models/noc.py
- Pitfalls: HIGH — column whitespace contamination verified against actual files; oasis_profile_code format verified by inspection; exception types verified by code execution
- Gap analysis: HIGH — verified by reading actual parquet files and source CSVs

**Research date:** 2026-03-07
**Valid until:** 2026-06-07 (stable — parquet files change only when JobForge ETL runs; Python/pandas versions stable)
