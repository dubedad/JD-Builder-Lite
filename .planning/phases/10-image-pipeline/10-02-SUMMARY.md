---
phase: 10-image-pipeline
plan: "02"
subsystem: ps_careers_site
tags: [css, gradients, frontend, image-fallback, unsplash, attribution]
dependency_graph:
  requires: [10-01-PLAN.md]
  provides: [gradient-css-classes, unsplash-attribution]
  affects: [ps_careers_site/templates/base.html, Phase 11 card templates]
tech_stack:
  added: []
  patterns: [per-function-css-gradient-fallback, css-only-no-js]
key_files:
  created:
    - ps_careers_site/static/css/gradients.css
  modified:
    - ps_careers_site/templates/base.html
decisions:
  - "Used 160deg gradient angle matching existing .card-no-image class for visual consistency"
  - "Unsplash attribution placed between social icons and terms links in footer-bottom flex row"
  - "CSS link inserted between Google Fonts link and inline style tag in head"
metrics:
  duration_seconds: 275
  completed_date: "2026-03-29"
  tasks_completed: 2
  files_modified: 2
---

# Phase 10 Plan 02: Gradient Fallback CSS and Unsplash Attribution Summary

**One-liner:** 22 per-function CSS gradient fallbacks (160deg, muted federal palette) + Unsplash footer attribution — pure CSS, zero JS, ready for Phase 11 template consumption.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Create per-function gradient CSS file | ba0dc4e | ps_careers_site/static/css/gradients.css (created) |
| 2 | Add gradient CSS link and Unsplash attribution to base.html | dbafca7 | ps_careers_site/templates/base.html (modified) |

## What Was Built

### gradients.css (new file)

22 CSS classes, one per job function slug from the `job_functions` table. Each class applies a `linear-gradient(160deg, {dark-from} 0%, {darker-to} 100%)` — matching the existing `.card-no-image` gradient angle. Colors are muted/desaturated dark tones appropriate for a federal government site (D-10).

Classes follow the pattern `.gradient-{function-slug}`. Phase 11 templates will apply these as:
```
class="card-inner card-no-image gradient-{{ entity.job_function_slug }}"
```

### base.html changes

- **Head:** Added `<link rel="stylesheet" href="{{ url_for('static', path='css/gradients.css') }}">` between Google Fonts link and the inline `<style>` block (line 10). Available on all pages site-wide.
- **Footer:** Added `Photos by Unsplash` credit span with `utm_source=dnd_civilian_careers&utm_medium=referral` tracking between the social icons div and terms/Français links div in `footer-bottom`.

## Verification Results

| Check | Result |
|-------|--------|
| `test -f ps_careers_site/static/css/gradients.css` | PASS |
| `grep -c "\.gradient-" gradients.css` = 22 | PASS |
| `grep "gradients.css" templates/base.html` | PASS |
| `grep -i "unsplash" templates/base.html` | PASS |
| CSS link in `<head>` before `</head>` | PASS |
| Attribution inside `<footer>` | PASS |

## Deviations from Plan

None — plan executed exactly as written. The `static/css/` directory did not exist (as anticipated in the plan) and was created as part of Task 1.

## Known Stubs

None. The gradient classes are complete and functional. They will only be visible to end-users once Phase 11 template updates apply `gradient-{slug}` to card markup — but the CSS infrastructure is fully wired and linked.

## Self-Check: PASSED
