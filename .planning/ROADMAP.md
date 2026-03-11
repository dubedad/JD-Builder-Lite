# Roadmap: JD Builder Lite

## Milestones

- 🚧 **v5.1 UI Overhaul** — Phases 26-30 (in progress, started 2026-03-11)
- ✅ **v5.0 JobForge 2.0 Integration** -- Phases 21-25 (shipped 2026-03-10) — [archive](milestones/v5.0-ROADMAP.md)
- ✅ **v4.1 Polish** -- Phases 18-20 (shipped 2026-02-07; Phase 20 deferred indefinitely)
- ✅ **v4.0 Occupational Group Allocation** -- Phases 14-17 (shipped 2026-02-04)
- ✅ **v3.0 Style-Enhanced Writing** -- Phases 09-13 (shipped 2026-02-03)
- ✅ **v2.0 UI Redesign** -- Phases 08-A through 08-D (shipped 2026-01-25)
- ✅ **v1.1 Enhanced Data Display + Export** -- Phases 05-07 (shipped 2026-01-23)
- ✅ **v1.0 MVP** -- Phases 01-04 (shipped 2026-01-22)

## Deferred

**Phase 20: Evidence & Provenance Display** — Deferred indefinitely (v4.1 scope).
Evidence highlighting requires LLM returning verbatim quotes (currently paraphrased); proper fix needs allocator prompt changes or v6+ PuMP grid. Plans: 20-01 (provenance tree), 20-02 (human verification) — both unstarted.

---

## 🚧 v5.1 UI Overhaul (In Progress)

**Milestone Goal:** Redesign the entire application UI to match the JobForge reference prototype — new global chrome applied across all pages, redesigned search/build/classify pages, and two new functional pages (Generate, Export) with restructured PDF/DOCX/JSON output.

### Phase 26: Global Chrome & Search

**Goal:** Users experience a consistent, fully-branded application shell across all pages and a redesigned search experience that delivers match-quality results with rich filtering.

**Depends on:** Phase 25 (v5.0 complete)

**Requirements:** CHROME-01, CHROME-02, CHROME-03, CHROME-04, CHROME-05, CHROME-06, CHROME-07, CHROME-08, SRCH-01, SRCH-02, SRCH-03, SRCH-04, SRCH-05

**Success Criteria** (what must be TRUE):
1. Every page in the app shows the Government of Canada header, dark navy app bar, coloured data source pills, 5-step stepper, right-edge Selections tab, compliance paragraph, and dark footer — all in the correct positions and styles.
2. The search page displays "Find your Job" with an empty-state magnifying glass when no query is entered.
3. After a search, a left filter panel with 6 accordion sections appears alongside result cards that show occupation icon, match badge pills, "Also known as:" line with keyword highlighting, and a description paragraph.
4. The results header shows the result count, a "+ New Search" button, and ESDC metadata.
5. Cosmetic-only elements (Français toggle, View Provenance Graph button) render visually but take no action when clicked.

**Plans:** 2 plans

Plans:
- [ ] 26-01-PLAN.md — Global chrome layout (GoC header, app bar, data source pills, stepper, selections tab, compliance paragraph, footer)
- [ ] 26-02-PLAN.md — Search page redesign (Find your Job heading, empty state, result cards, filter panel, results header)

---

### Phase 27: Build Page Redesign

**Goal:** Users can build their job description on a fully redesigned Build page that groups content logically, shows inline descriptions, and makes Core Competencies selectable.

**Depends on:** Phase 26

**Requirements:** BUILD-01, BUILD-02, BUILD-03, BUILD-04, BUILD-05, BUILD-06, BUILD-07, BUILD-08, BUILD-09

**Success Criteria** (what must be TRUE):
1. The Build page shows a dark navy occupation header card with gear icon, NOC code, lead statement, NOC version badge, Retrieved timestamp, and Quality Verified badge.
2. Each tab has an icon and a blue-grey section description box explaining what the tab contains.
3. Core Competencies items have checkboxes and are individually selectable.
4. Key Activities tab displays Main Duties and Work Activities as two clearly labelled lists within the same tab.
5. Abilities, Effort, and Responsibility tabs group items by level with coloured level badges; all item-level tabs show inline sub-descriptions below each item label.

**Plans:** TBD

Plans:
- [ ] 27-01: Occupation header card + tab icons + section description boxes
- [ ] 27-02: Tab content redesign (Overview, Core Competencies, Key Activities, level-grouped tabs, Select All, blue dot ratings)

---

### Phase 28: Navigation, Preview Modal & Selections Drawer

**Goal:** Users can move through the workflow with a 3-button navigation bar, preview their assembled JD in a modal, and manage selections via a slide-out drawer — with all selections persisting correctly across navigation.

**Depends on:** Phase 27

**Requirements:** NAV-01, NAV-02, NAV-03, NAV-04, NAV-05, PREV-01, PREV-02, SEL-01, SEL-02, SEL-03

**Success Criteria** (what must be TRUE):
1. Every Build tab shows a 3-button bottom bar: "Back to Search" (left), "Preview Job Description" (centre), "Continue to Classification" (right).
2. Navigating back to Search preserves selections; clicking a different occupation card clears them while clicking the same card preserves them.
3. "Preview Job Description" opens a modal with the assembled JD; the modal header has "Return to Builder" and the footer has "Advance to Classify", "Export PDF", and "Export Word" buttons.
4. The right-edge Selections tab opens an overlay panel showing all selected items grouped by tab, each with a × deselect button, a total count, and a "Clear All" button.
5. Classification page shows "Back to Edit" and "Continue to Generate" buttons; Generate page shows "Regenerate" and "Continue" buttons.

**Plans:** TBD

Plans:
- [ ] 28-01: 3-button navigation bar + selection persistence (back/same/different card logic)
- [ ] 28-02: Preview modal (open, content, header/footer buttons)
- [ ] 28-03: Selections drawer (open, items grouped by tab, deselect, clear all, count)

---

### Phase 29: Classification Restyle + Generate Page

**Goal:** Users see classification results in the v5.1 chrome with enriched post-analysis sections, and can generate an AI-written Position Overview on a new, dedicated Generate page.

**Depends on:** Phase 28

**Requirements:** CLASS-01, CLASS-02, CLASS-03, CLASS-04, GEN-01, GEN-02, GEN-03, GEN-04

**Success Criteria** (what must be TRUE):
1. The Classification page renders in v5.1 chrome with DADM Compliant and Full Provenance badges and the TBS 3-step dark card.
2. Post-analysis results include Statement Alignment Comparison (two columns + Overall Alignment Score), Key Evidence (green bullets), Caveats (amber bullets), Alternative Groups Considered, and a Next Step box linking to the relevant Job Evaluation Standard.
3. The Generate page renders with a "Generate AI Overview" card, DADM Level 2 badge, Human Review Required badge, and a yellow DADM Compliance Notice.
4. Clicking "Generate with AI" sends selected statements to OpenAI and displays multi-paragraph prose with an "AI Generated" badge; a "Regenerate" button allows re-generation.

**Plans:** TBD

Plans:
- [ ] 29-01: Classification page restyle (chrome, badges, TBS card, post-analysis enriched sections)
- [ ] 29-02: Generate page (new page, DADM card, compliance notice, textarea, Generate with AI button, AI output + Regenerate)

---

### Phase 30: Export Page + New PDF/DOCX/JSON

**Goal:** Users can export a fully provenance-traced JD from a new Export page that offers PDF, Word, and JSON downloads — all using the restructured compliance-first format.

**Depends on:** Phase 29

**Requirements:** EXP-01, EXP-02, EXP-03, EXP-04, EXP-05, EXP-06, PDF-01, PDF-02, PDF-03, PDF-04, PDF-05

**Success Criteria** (what must be TRUE):
1. The Export page renders in v5.1 chrome with a scrollable JD preview card, three compliance summary cards (DAMA DMBOK, TBS Directives, Full Lineage), and "Include provenance annex" / "Include audit trail" checkboxes.
2. "Download PDF" generates a PDF with the restructured sections: Position Overview, Key Duties and Responsibilities (with source tags), Qualifications (Skills/Abilities/Knowledge/Core Competencies), Effort & Physical Demands, Responsibilities, Data Provenance & Compliance, Policy Provenance table, and Data Quality (DAMA DMBOK).
3. "Download Word" generates a DOCX with equivalent section structure to the new PDF.
4. "Download Full Audit Trail (JSON)" generates a JSON file containing all session selections, provenance metadata, classification result, and AI-generated content.

**Plans:** TBD

Plans:
- [ ] 30-01: Export page (v5.1 chrome, JD preview card, compliance cards, checkboxes, three download buttons)
- [ ] 30-02: Restructured PDF + DOCX (new section structure: PDF-01 through PDF-04 + Word equivalent)
- [ ] 30-03: JSON audit trail export

---

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 26. Global Chrome & Search | v5.1 | 0/2 | In progress | - |
| 27. Build Page Redesign | v5.1 | 0/2 | Not started | - |
| 28. Navigation, Preview & Selections | v5.1 | 0/3 | Not started | - |
| 29. Classification Restyle + Generate | v5.1 | 0/2 | Not started | - |
| 30. Export Page + New PDF/DOCX/JSON | v5.1 | 0/3 | Not started | - |
| 21. Data Exploration | v5.0 | 3/3 | Complete | 2026-03-07 |
| 22. Profile Service | v5.0 | 2/2 | Complete | 2026-03-08 |
| 23. Search Service | v5.0 | 2/2 | Complete | 2026-03-09 |
| 24. Compliance Hardening | v5.0 | 1/1 | Complete | 2026-03-09 |
| 25. Tech Debt Cleanup | v5.0 | 2/2 | Complete | 2026-03-10 |
| 18. Profile Page Overhaul | v4.1 | 2/2 | Complete | 2026-02-07 |
| 19. Flow and Export Polish | v4.1 | 3/3 | Complete | 2026-02-07 |
| 20. Evidence & Provenance Display | v4.1 | 0/2 | Deferred | - |

---
*Roadmap updated: 2026-03-11 — Phase 26 planned (2 plans in 2 waves)*
