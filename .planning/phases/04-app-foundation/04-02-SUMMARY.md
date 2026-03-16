# Plan 04-02 Summary: Jinja2 Base Template + GC FIP Chrome

**Completed:** 2026-03-16
**Requirements covered:** FOUND-03, FOUND-04

## What Was Built

### Files Created/Modified
- `ps_careers_site/templates/base.html` — Jinja2 base template with full GC FIP chrome
- `ps_careers_site/main.py` — Updated GET "/" to render base.html via TemplateResponse

## Template Structure

### Blocks Defined
- `{% block title %}` — page title (default: "DND Civilian Careers")
- `{% block extra_head %}` — page-specific CSS/meta in `<head>`
- `{% block content %}` — main page content inside `<main>`

### Document Structure
```
<!DOCTYPE html>
<html lang="en">
<head>
  charset, viewport
  Google Fonts (Exo 2 + Roboto)
  {% block extra_head %}
  inline <style> (base reset + font defaults)
</head>
<body>
  <header class="gc-header">       ← sticky, #222, 64px
    GC Canada Logo (wordmark)
    Nav: Browse Careers | Apply Now | FR
  </header>
  <main>
    {% block content %}
  </main>
  <footer>
    <div class="footer-grid">      ← 5-column grid, #2a2a2a
    <div class="footer-bottom">    ← wordmark + social icons + legal, #1a1a1a
  </footer>
</body>
```

## Header Markup Decisions
- **Inline styles** chosen over external CSS classes — consistent with CAF reference site's approach, avoids a separate CSS file dependency for structural chrome
- **Sticky positioning** (`position:sticky; top:0; z-index:1020`) — matches CAF reference nav behavior
- **url_for() for all static paths** — ensures paths work regardless of app mount point

## Footer Column Content (DND adaptations from CAF original)
CAF footer had military-specific columns (Careers, Training, Benefits, Bases, About CAF). Adapted for DND civilian context:
1. Browse Careers — links to /careers with function filters
2. Joining the Public Service — PSC job postings, how to apply, student programs, FSWEP
3. Life in DND — pay & benefits, D&I, career development
4. About DND — organization, policies, contact us
5. Get in Touch — help centre, HR contacts, email

Social icons use inline SVG (no external icon library dependency). Facebook, X/Twitter, LinkedIn, Instagram, YouTube — all link to official DND/Canadian Forces accounts.

## Deviations
None. Plan executed as specified.
