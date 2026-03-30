# Classification Engine Design

Last updated: 2026-03-26

## Overview

The classification engine allocates a job description to one or more TBS
occupational groups using a multi-factor scoring pipeline. Results are
transparent — every score is broken down into components, and all evidence
is traceable to the source JD text or TBS policy definition.

---

## Pipeline Stages

```
JD Input
  → 1. Load Groups (DB)
  → 2. Shortlist Candidates (semantic + labels)
  → 3. LLM Classification (structured output)
  → 4. Multi-Factor Confidence Scoring
  → 5. Evidence Extraction + Provenance Linking
  → 6. Edge Case Detection
  → 7. Threshold Filter (min 0.3) + Top-3 Limit
  → 8. OG Definition Statements Population (DB)
  → API Response
```

---

## Confidence Scoring

### Weights (current — updated 2026-03-26)

| Component | Weight | Source |
|-----------|--------|--------|
| Definition fit | 50% | LLM holistic definition match score |
| Semantic similarity | 25% | TF-IDF / embedding distance to definition text |
| **Inclusion match** | **15%** | **LLM-scored fraction of inclusion statements that apply** |
| Labels boost | 10% | labels.csv keyword match |

Total: 100% (before exclusion penalty)

**Exclusion conflict**: Hard-gate multiplier of 0.3 applied to base score
when any exclusion statement matches the JD's primary purpose.

### Previous Weights (pre-2026-03-26)

| Component | Old Weight | New Weight |
|-----------|-----------|-----------|
| Definition fit | 60% | 50% |
| Semantic similarity | 30% | 25% |
| Inclusion match | 0% | **15%** |
| Labels boost | 10% | 10% |

### Rationale for Adding Inclusion Weight

Many TBS occupational groups are **sub-groups of the Programme and
Administrative Services (PA) group**: AS, CR, PM, DA, IS, CM, OE, OM, ST,
WP. These sub-groups **share the same parent definition text** in the DB.
Without inclusion scoring, the classifier cannot distinguish between
sub-groups — they all score identically on definition fit and semantic
similarity.

Inclusion statements are the **primary differentiator** between PA
sub-groups. For example:

- **AS** (Administrative Services): includes positions involved in planning,
  development, delivery or management of policies in two or more
  administrative fields (finance, HR, purchasing, etc.)
- **CR** (Clerical and Regulatory): includes positions performing
  administrative services involving adapting, modifying or devising methods
  and procedures
- **PM** (Programme Administration): includes positions managing or
  administering specific programme delivery

Adding 15% inclusion weight surfaces this differentiation in confidence
scores and prevents AS/CR/PM from appearing interchangeable to users.

---

## Parent-Child Group Hierarchy

The DB table `dim_occupational_group` encodes a two-level hierarchy:

```
group_code  subgroup   Description
----------  ---------  ----------------------------------------------------
PA          None       Parent: Programme and Administrative Services Group
AS          None       Child of PA — Administrative Services
CR          None       Child of PA — Clerical and Regulatory
PM          None       Child of PA — Programme Administration
CM          None       Child of PA — Communications
DA          None       Child of PA — Data Administration (parent row)
DA          CON        Sub-group of DA — Data Conversion
DA          PRO        Sub-group of DA — Data Processing
OE          None       Child of PA — Office Equipment Operations (parent row)
OE          BEO/CEO/...  Sub-groups of OE
ST          None       Child of PA — Secretarial/Typing (parent row)
ST          COR/SCY/...  Sub-groups of ST
```

When `subgroup = None`, the row represents the group's own definition.
When `subgroup` has a value (e.g., `CON`), it is a named sub-group within
that group with its own specific definition.

**All PA child groups (`subgroup = None`) store the same PA parent
definition sentence as their `definition` field.** Their distinguishing
characteristics are encoded exclusively in their inclusion and exclusion
statements.

---

## OG Definition Statements

Displayed in the "Statement Alignment Comparison" section of the Classify
UI. Populated in `_fill_missing_og_statements()` in `allocator.py`.

**Always rebuilt from DB** — the LLM was found to cross-contaminate this
field (putting one group's text into another recommendation). DB data is
authoritative.

### Structure

For each recommended group, `og_definition_statements` is built as:

1. **Up to 2 sentences** from the group's own definition text
2. **All inclusion statements**, prefixed with `"Included: "`
3. **All exclusion statements**, prefixed with `"Not included: "`

This structure ensures:
- PA sub-groups show distinct, group-specific content
- Users see both what qualifies a position for the group AND what disqualifies it
- The same structure applies to all groups (not just PA sub-groups)

---

## LLM Prompt Design

### System Prompt

See `src/matching/prompts.py` → `build_system_prompt()`.

Key instructions:
1. Extract primary purpose from JD (Client-Service Results + Key Activities)
2. Evaluate definition fit holistically (no keyword matching)
3. Score inclusion match 0.0–1.0 → stored in `inclusion_match_score` field
4. Apply exclusion hard gate
5. Rank top 3 recommendations
6. Evidence must be quoted from JD only (NEVER from group definitions)
7. Caveats must be group-specific (no generic statements across groups)
8. `og_definition_statements` populated by LLM (overridden by DB in Step 8)

### User Prompt

See `src/matching/prompts.py` → `build_user_prompt()`.

For each shortlisted candidate group, the prompt includes:
- Group code + semantic similarity score
- Full definition text
- All inclusion statements
- All exclusion statements
- TBS source URL

---

## Key Files

| File | Purpose |
|------|---------|
| `src/matching/allocator.py` | Pipeline orchestrator |
| `src/matching/classifier.py` | LLM structured output call |
| `src/matching/confidence.py` | Multi-factor scoring weights |
| `src/matching/models.py` | Pydantic models (GroupRecommendation, etc.) |
| `src/matching/prompts.py` | LLM system + user prompt templates |
| `src/matching/evidence/extractor.py` | Evidence span extraction |
| `src/matching/shortlisting/` | Semantic + labels shortlisting |
| `src/storage/repository.py` | DB access (groups, inclusions, exclusions) |
| `static/js/classify.js` | UI rendering (Switch button, alignment section) |

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| Pre-v5.1 | Inclusions used for shortlisting only, not scoring | Avoided inflating scores; inclusions seen as supporting not determinative |
| 2026-03-26 | **Inclusions added to scoring at 15% weight** | PA sub-groups share definition text; inclusions are the only differentiator; without this, AS/CR/PM score identically |
| 2026-03-26 | og_definition_statements always rebuilt from DB (not LLM) | LLM cross-contaminates groups; DB is authoritative and includes inclusions/exclusions |
| 2026-03-26 | og_definition_statements shows definition + inclusions + exclusions | Provides complete group-specific context, especially for PA sub-groups |
| Pre-v5.1 | Exclusions are hard gate (0.3 multiplier) | TBS policy: exclusion match means work explicitly does not belong here |
