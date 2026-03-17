---
phase: 07-l2-job-family
plan: "01"
subsystem: ps_careers_site
tags: [fastapi, jinja2, l2, job-family, sqlite]
dependency_graph:
  requires: [05-01]
  provides: [L2-01, L2-02, L2-03, L2-04]
  affects: [ps_careers_site/main.py, ps_careers_site/templates/family.html]
tech_stack:
  added: []
  patterns: [TemplateResponse, SQLite row_factory, HTTPException 404 guard, Jinja2 extends]
key_files:
  created:
    - ps_careers_site/templates/family.html
  modified:
    - ps_careers_site/main.py
key_decisions:
  - "Route already present in main.py from prior session — committed with minor cleanup (removed CARD_IMAGE_STATIC dict, updated WHERE clause)"
  - "job-family slug query uses WHERE job_family_slug = ? with ORDER BY job_title ASC"
  - "Overview excerpt: (overview or '')[:150] — null-safe, no crash on missing data"
  - "Digital badge: conditional class badge-digital vs badge-nondigital based on value equality"
metrics:
  duration: "~10 min"
  completed_date: "2026-03-17"
  tasks_completed: 2
  files_modified: 2
---

# Phase 7 Plan 01: L2 Job Family Page Summary

**One-liner:** L2 Job Family page — `/careers/{family_slug}` route with 404 guard and `family.html` template listing job titles with NOC badge, managerial level tag, digital indicator, and breadcrumb.

## What Was Built

Added the L2 Job Family page that sits between the card grid (L1) and the job title detail page (L3). When a visitor clicks a family card on `/careers`, they land on `/careers/{family_slug}` and see all job titles within that family, each with metadata badges and a 150-char overview excerpt.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Add GET /careers/{family_slug} route to main.py | 6363604 | ps_careers_site/main.py |
| 2 | Create ps_careers_site/templates/family.html | 94b77dd | ps_careers_site/templates/family.html |

## Verification Results

- `GET /careers/administrative-support` → HTTP 200
- `GET /careers/does-not-exist` → HTTP 404
- Administrative Support family: 9 job titles confirmed
- NOC badges render (e.g., "NOC 13110", "NOC 14100")
- Breadcrumb renders: Home > Careers > [Family Name]
- Job title links: `/career/administrative-assistant`, `/career/administrative-clerk`, etc.

## Sample Family Tested

**Administrative Support** — 9 job titles:
- administrative-assistant, administrative-clerk, administrative-officer, etc.
- All NOC UIDs present, managerial level tags render, digital indicators present
- No null-crash issues observed — null overview gracefully shows no excerpt

## Badge Rendering Notes

- NOC badge: all rows in Administrative Support had valid `noc_2021_uid` values — no null edge cases triggered
- Managerial level: values present; badge renders inline
- Digital indicator: conditional class works correctly (`badge-digital` vs `badge-nondigital`)
- Overview excerpt: null-safe via `(overview or '')[:150]` — no crashes observed

## Deviations from Plan

### Auto-fixed Issues

None.

### Notes

Task 1 route (`GET /careers/{family_slug}`) was already present in `main.py` from a prior session (committed alongside the L3 route). The commit for Task 1 captured minor cleanup: removal of the `CARD_IMAGE_STATIC` dict (image mapping moved to DB `card_image_key` column) and a WHERE clause update (`card_image_key IS NOT NULL` → `job_family != ''`). These changes were leftover from the Phase 06 work and required committing before proceeding.

## Self-Check

- [x] `ps_careers_site/templates/family.html` exists
- [x] `ps_careers_site/main.py` committed
- [x] Task 1 commit 6363604 exists
- [x] Task 2 commit 94b77dd exists
- [x] Live verification: 200/404/9 titles/badges/breadcrumb/L3-links all confirmed
