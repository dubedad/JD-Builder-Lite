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
- L3 overlays enriched content from `ps_careers_site/careers.sqlite`

---

## Known Bug — `/careers/` returns 500

**Status:** Not resolved. All tests pass (200) but the running server returns 500.
The error is being swallowed — no traceback visible in terminal or browser.

**What has been tried:**
- Fixed `{% extends "base.html" %}` → `{% extends "careers/base.html" %}` ✅
- Fixed Jinja2 quote conflict in card image url_for ✅
- Added try/except with print() to route — still no visible error
- Cleared __pycache__ — no change
- Debug mode — generic 500 still shown, no Werkzeug traceback in browser

**Most likely remaining causes to investigate next session:**
1. Run `python -m flask --app src/app.py run --debug` and visit `/careers/`
   — browser should show Werkzeug debugger with full traceback
2. If still generic 500, something is intercepting before Flask error handler
3. Check if `pandas` or `pyarrow` is causing a non-Exception crash at render time

**Quick workaround to run original careers site while debugging:**
```
cd C:\Users\Administrator\Projects\jd-builder\ps_careers_site
python main.py
```
Then visit `http://localhost:8000/careers`
(Note: must cd INTO ps_careers_site folder first, not run from root)

---

## App Setup

**To run the merged app:**
```
cd C:\Users\Administrator\Projects\jd-builder
python -m flask --app src/app.py run
```

**Rob's `.env`** — saved at `C:\Users\Administrator\Projects\jd-builder\.env`
Contains JOBFORGE_GOLD_PATH, JOBFORGE_BRONZE_PATH, OPENAI_API_KEY, SECRET_KEY

**Vic's `.env`** — still needs to be created at his project root:
```
JOBFORGE_GOLD_PATH=/Users/victornishi/Documents/GitHub/JobForge-2.0/data/gold
JOBFORGE_BRONZE_PATH=/Users/victornishi/Documents/GitHub/JobForge-2.0/data/bronze
OPENAI_API_KEY=key-here
SECRET_KEY=dev-secret-change-in-production
```

**Vic sync instructions** (not yet done — do this next session):
```
git pull origin master
pip install -r requirements.txt
# create .env as above
python -m flask --app src/app.py run
```

---

## Remaining Steps

| Step | What | Status |
|------|------|--------|
| Bug | `/careers/` 500 error | Unresolved — investigate first |
| 4 | CAF pixel-parity audit — live verify forces.ca | Not started |
| 5 | Unified taxonomy in JobForge 2.0 | Not started |

---

## How to Resume

After `/clear`, say:
> "Review the handoff file and resume. Debug the /careers/ 500 error first."
