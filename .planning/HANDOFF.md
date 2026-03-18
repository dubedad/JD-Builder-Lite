# Session Handoff — 2026-03-18

## Session Goal
Reconcile GitHub so all work is safe and the codebase is unified. ✅ Done.

---

## What Was Accomplished

**Step 1 — Git reconciliation** ✅
- `legacy/jd-builder-lite` — old JD Builder backed up on GitHub
- `vic/jd-builder-lite-work` — Vic's parquet integration saved
- `master` — DND Careers Site promoted to new main codebase

**Step 2 — One app, two surfaces** ✅
- Vic's JD Builder (Flask) merged into this repo as the foundation
- Careers site ported from FastAPI → Flask Blueprint (`src/routes/careers.py`)
- Step 0 routing gate added at `/` (`templates/landing.html`)
- Careers site at `/careers/*`, JD Builder at `/builder/`

**Step 3 — Parquet data layer** ✅
- `src/services/careers_parquet_reader.py` reads `job_architecture.parquet`
  and `bridge_caf_ja.parquet` from JOBFORGE_GOLD_PATH
- L1/L2 browse driven by parquet (209 families, 1,987 titles)
- L3 still overlays enriched content from `ps_careers_site/careers.sqlite`

---

## Known Bug (Next Session Priority 1)

**`/careers/` returns 500 Internal Server Error**

The template fix was applied (`{% extends "careers/base.html" %}`) and committed,
but the error persists. Root cause not yet confirmed — needs debug mode to see
the actual traceback.

**To diagnose:** run with `--debug` flag and click the employee button:
```
python -m flask --app src/app.py run --debug
```
Paste the terminal output to identify the real error.

---

## App Setup

**To run:**
```
cd C:\Users\Administrator\Projects\jd-builder
python -m flask --app src/app.py run
```

**Rob's `.env`** — saved at project root. Contains:
- `JOBFORGE_GOLD_PATH=C:/Users/Administrator/Projects/jobforge/data/gold`
- `JOBFORGE_BRONZE_PATH=C:/Users/Administrator/Projects/jobforge/data/bronze`
- `OPENAI_API_KEY` and `SECRET_KEY`

**Vic's `.env`** — still needs to be created at his project root:
```
JOBFORGE_GOLD_PATH=/Users/victornishi/Documents/GitHub/JobForge-2.0/data/gold
JOBFORGE_BRONZE_PATH=/Users/victornishi/Documents/GitHub/JobForge-2.0/data/bronze
OPENAI_API_KEY=key-here
SECRET_KEY=dev-secret-change-in-production
```

---

## Remaining Steps

| Step | What | Status |
|------|------|--------|
| Bug | `/careers/` 500 error | Fix first |
| 4 | CAF pixel-parity audit — live verify forces.ca | Not started |
| 5 | Unified taxonomy in JobForge 2.0 | Not started |

---

## How to Resume

After `/clear`, say:
> "Review the handoff file and resume. Debug the /careers/ 500 error first."
