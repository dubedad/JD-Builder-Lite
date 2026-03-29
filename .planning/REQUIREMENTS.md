# Requirements — v1.1 Full Browse Experience

**Milestone:** v1.1 — Full Browse Experience
**Status:** Roadmap defined 2026-03-28
**Carries forward from:** v1.0 (phases 1–8 complete)

---

## v1.1 Requirements

### DATA — Schema migration & CSV import

- [x] **DATA-01**: careers.sqlite extended with `job_functions` table (`job_function`, `job_function_slug`, `job_function_description`, `image_path`)
- [x] **DATA-02**: careers.sqlite extended with `job_families` table (`job_family`, `job_family_slug`, `job_function` FK, `job_family_description`, `image_path`)
- [x] **DATA-03**: `careers` table extended with `job_title_description`, `key_responsibilities`, `required_skills`, `typical_education`, `image_path` columns
- [x] **DATA-04**: All 23 job functions imported from CSV with descriptions and slugs
- [x] **DATA-05**: All 210 job families imported from CSV with descriptions, function relationships, and slugs
- [x] **DATA-06**: All 1,989 job titles updated with `job_title_description`, `key_responsibilities`, `required_skills`, `typical_education` from CSV

### NAV — Navigation restructure

- [ ] **NAV-01**: `/careers` serves 23 Job Function image cards (4-col → 3-col → 1-col, CAF card format)
- [ ] **NAV-02**: `/careers/{function-slug}` serves Job Family image cards for that function (same card format)
- [ ] **NAV-03**: `/careers/{function-slug}/{family-slug}` serves Job Title image cards for that family (same card format)
- [ ] **NAV-04**: All 3 browse levels use identical card CSS from `CAF-CAREERS-SITE-REFERENCE.md` (300px height, 3-layer gradient overlay, Exo 2 title font, VIEW CAREERS button)
- [ ] **NAV-05**: Hero banner on each browse page showing the current level name and description
- [ ] **NAV-06**: Breadcrumb on every page: Home > Careers > [Function] > [Family] > [Title]
- [ ] **NAV-07**: Keyword search on L1 (`/careers`) searches across function names

### IMG — Image pipeline

- [x] **IMG-01**: Pipeline script queries Unsplash API with job-relevant keyword per function/family/title
- [x] **IMG-02**: Images downloaded to `/static/images/functions/`, `/static/images/families/`, `/static/images/titles/`
- [x] **IMG-03**: `image_path` updated in DB for each record after successful download
- [x] **IMG-04**: Pipeline is concurrent (5 workers) and resumable (skips already-fetched images)
- [ ] **IMG-05**: Cards display a styled fallback (gradient, no photo) when `image_path` is null

### DETAIL — Enhanced career detail page

- [ ] **DETAIL-01**: Key Responsibilities section added to career detail page
- [ ] **DETAIL-02**: Required Skills section added to career detail page
- [ ] **DETAIL-03**: Typical Education section added to career detail page
- [ ] **DETAIL-04**: Breadcrumb updated to reflect full path: Home > Careers > [Function] > [Family] > [Title]

---

## Future Requirements (deferred)

- Bilingual support (EN/FR toggle, French fields from CSV available)
- Managerial Level and Digital flag filters on browse pages
- Full-text search across all LLM-generated content
- WCAG 2.1 AA formal audit
- Human content review workflow (draft → reviewed → published)
- CAF pixel-parity audit (re-measure live forces.ca DevTools values)
- Manager/employee routing gate at site entry
- "Use this title / Build JD" CTA on detail page (manager path)

## Out of Scope (v1.1)

| Feature | Reason |
|---------|--------|
| JD Builder integration | Separate milestone |
| Bilingual (EN/FR) | French fields in CSV available but deferred |
| Filter dialog on browse pages | Deferred — browse hierarchy is the primary navigation |
| AI-generated images (Gemini/Imagen) | Unsplash API sufficient for this milestone |
| User authentication | Public read-only site |

---

## Traceability

| REQ-ID | Phase | Status |
|--------|-------|--------|
| DATA-01 | Phase 9 — Data Migration | Complete |
| DATA-02 | Phase 9 — Data Migration | Complete |
| DATA-03 | Phase 9 — Data Migration | Complete |
| DATA-04 | Phase 9 — Data Migration | Complete |
| DATA-05 | Phase 9 — Data Migration | Complete |
| DATA-06 | Phase 9 — Data Migration | Complete |
| IMG-01 | Phase 10 — Image Pipeline | Complete |
| IMG-02 | Phase 10 — Image Pipeline | Complete |
| IMG-03 | Phase 10 — Image Pipeline | Complete |
| IMG-04 | Phase 10 — Image Pipeline | Complete |
| IMG-05 | Phase 10 — Image Pipeline | Pending |
| NAV-01 | Phase 11 — Navigation Restructure | Pending |
| NAV-02 | Phase 11 — Navigation Restructure | Pending |
| NAV-03 | Phase 11 — Navigation Restructure | Pending |
| NAV-04 | Phase 11 — Navigation Restructure | Pending |
| NAV-05 | Phase 11 — Navigation Restructure | Pending |
| NAV-06 | Phase 11 — Navigation Restructure | Pending |
| NAV-07 | Phase 11 — Navigation Restructure | Pending |
| DETAIL-01 | Phase 12 — Enhanced Detail Page | Pending |
| DETAIL-02 | Phase 12 — Enhanced Detail Page | Pending |
| DETAIL-03 | Phase 12 — Enhanced Detail Page | Pending |
| DETAIL-04 | Phase 12 — Enhanced Detail Page | Pending |
