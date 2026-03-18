# Session Handoff — 2026-03-18

## Where We Are

Steps 1, 2, and 3 are complete and pushed to GitHub master.

### What Was Built This Session

**Step 1 — Git reconciliation** ✅
- `legacy/jd-builder-lite` — old JD Builder backed up on GitHub
- `vic/jd-builder-lite-work` — Vic's parquet integration saved
- `master` — DND Careers Site promoted to new main codebase

**Step 2 — One app, two surfaces** ✅
- Vic's JD Builder (Flask) merged into this repo as the foundation
- Careers site ported from FastAPI → Flask Blueprint (`src/routes/careers.py`)
- Step 0 routing gate added at `/` (`templates/landing.html`)
- Careers site lives at `/careers/*`, JD Builder at `/builder/`

**Step 3 — Parquet data layer** ✅
- `src/services/careers_parquet_reader.py` created
- L1/L2 browse now reads from `job_architecture.parquet` (209 families, 1,987 titles)
- CAF bridge reads from `bridge_caf_ja.parquet`
- L3 still overlays enriched content from `ps_careers_site/careers.sqlite`

---

## Immediate Bug to Fix (First Thing Next Session)

**Error:** `/careers/` returns 500 — Internal Server Error

**Root cause:** `templates/careers/careers.html` extends `"base.html"` but Flask
looks for it in the root `templates/` folder. It lives at `templates/careers/base.html`.

**Fix needed:** In all three careers templates, change:
```
{% extends "base.html" %}
```
to:
```
{% extends "careers/base.html" %}
```

Files to fix:
- `templates/careers/careers.html` line 1
- `templates/careers/family.html` line 1
- `templates/careers/career_detail.html` line 1

After fixing, commit and test `/careers/` in the browser.

---

## Current App State

- App runs: `python -m flask --app src/app.py run`
- `/` → Step 0 landing page (working)
- `/builder/` → JD Builder (working)
- `/careers/` → 500 error (fix above)
- Rob's `.env` is saved at project root with JOBFORGE_GOLD_PATH set
- Vic's `.env` still needs to be created — same format as Rob's but with Mac paths:
  ```
  JOBFORGE_GOLD_PATH=/Users/victornishi/Documents/GitHub/JobForge-2.0/data/gold
  JOBFORGE_BRONZE_PATH=/Users/victornishi/Documents/GitHub/JobForge-2.0/data/bronze
  OPENAI_API_KEY=his-actual-key
  SECRET_KEY=dev-secret-change-in-production
  ```

---

## Remaining Steps (from original plan)

| Step | What | Status |
|------|------|--------|
| 4 | CAF pixel-parity audit — live verify forces.ca | Not started |
| 5 | Unified taxonomy in JobForge 2.0 | Not started |

---

## How to Resume

After `/clear`, say:
> "Review the handoff file and resume. Fix the careers template bug first, then move to Step 4."
