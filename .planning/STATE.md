# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-02-04)

**Core value:** Classification Step 1 — Match job descriptions to occupational groups using the prescribed TBS allocation method with full policy provenance.
**Current focus:** v4.0 SHIPPED - Ready for demo

## Current Position

Milestone: v4.0 Occupational Group Allocation
Phase: 17 of 17 (UI Layer) - COMPLETE
Status: **SHIPPED**
Last activity: 2026-02-04 - Phase 17 complete with UAT fixes

Progress: [##########] 100% (17/17 phases complete)

## Milestone History

| Milestone | Status | Shipped |
|-----------|--------|---------|
| v1.0 MVP | SHIPPED | 2026-01-22 |
| v1.1 Enhanced Data Display + Export | SHIPPED | 2026-01-23 |
| v2.0 UI Redesign | SHIPPED | 2026-01-25 |
| v2.1 OaSIS Provenance | SHIPPED | 2026-02-02 |
| v3.0 Style-Enhanced Writing | SHIPPED | 2026-02-03 |
| v4.0 Occupational Group Allocation | **SHIPPED** | 2026-02-04 |

## v4.0 Demo Highlights

**What to show:**
1. **Search & Select** - Search for occupation, select profile
2. **Build JD** - Select statements from tabs (use Select All for speed)
3. **Create JD** - Generate job description with Style Selected
4. **Classify** - Step 5 shows occupational group recommendations
   - Top 3 ranked by confidence
   - Expand cards to see rationale, evidence, allocation checks
   - Links to TBS definitions

**Test cases that work:**
- Software Engineer → IT (#1)
- Administrative Assistant → AS (#1)
- Printer → PR (#1)

## Performance Metrics

**Velocity:**
- Total plans completed: 12 (v4.0)
- Average duration: ~9min
- Total execution time: ~2h

**By Phase (v4.0):**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 14-data-layer | 3/3 | 26min | 8.7min |
| 15-matching-engine | 5/5 | 66min | 13.2min |
| 16-api-layer | 2/2 | 13min | 6.5min |
| 17-ui-layer | 3/3 | ~15min | 5min |

## Gap Closure: 08-C-04 (2026-02-04)

Arrow key navigation added to TabController:
- ArrowRight/ArrowLeft with wrap-around
- Home/End for first/last tab
- Roving tabindex (active=0, inactive=-1)
- W3C ARIA Authoring Practices compliant

See: `.planning/phases/08-C-profile-page-tabs/08-C-04-SUMMARY.md`

## Phase 17 UAT Fixes (2026-02-04)

Critical algorithm fixes applied during UAT:
1. **De-duplication** - Database had 426 entries, 85 unique codes. Fixed.
2. **Inclusion ranking** - Uses max(definition, inclusion) similarity
3. **Keyword boost** - +15% for obvious title-to-group matches
4. **Exclusion penalty tooltip** - Added missing tooltip

See: `.planning/HANDOFF-PHASE17.md` for full details

## Future Work (v5.0+)

Documented in: `.planning/HANDOFF-PHASE17.md`

1. **JobForge Integration** - NOC→OG concordance table, shared gold models
2. **Two-column recommendation cards** - JD info | OG info side-by-side
3. **LLM improvement suggestions** - Generate proposed activities when brief
4. **Interactive statement adoption** - Add suggestions to Key Activities

## Session Continuity

Last session: 2026-02-04
Status: v4.0 SHIPPED
Resume file: `.planning/HANDOFF-PHASE17.md`
Next: Demo v4.0, then open JobForge for concordance iteration

---
*Last updated: 2026-02-04 - v4.0 milestone shipped*
