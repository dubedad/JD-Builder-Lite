# Feature Landscape: JD Builder Lite

**Domain:** Job Description Builder with NOC Data + Compliance/Provenance
**Researched:** 2026-01-22 (Updated for v1.1)
**Scope:** Single-user, local-only, demo-quality application

---

## v1.0 Features (Completed)

### Table Stakes (Built)

| Feature | Why Expected | Complexity | Status |
|---------|--------------|------------|--------|
| **NOC Search** | Core value: find occupational profiles by title | Medium | ✓ Complete |
| **Profile Selection** | Users need to pick from multiple matches | Low | ✓ Complete |
| **NOC Data Display** | Must show scraped content organized by JD element | Medium | ✓ Complete |
| **Statement Selection** | Core interaction: pick which NOC statements to include | Low | ✓ Complete |
| **JD Preview** | Users must see what they're building | Low | ✓ Complete |
| **PDF Export** | Final deliverable format for compliance | Medium | ✓ Complete |
| **Clear Data Attribution** | Users expect to know where content comes from | Low | ✓ Complete |

### Differentiators (Built)

| Feature | Value Proposition | Status |
|---------|-------------------|--------|
| **Full Provenance Trail** | Compliance with Directive on Automated Decision-Making | ✓ Complete |
| **AI-Generated Overview with Attribution** | Saves time while maintaining traceability | ✓ Complete |
| **NOC Source Metadata in Export** | Audit-ready documentation | ✓ Complete |
| **Compliance Metadata Block** | Machine-readable provenance in PDF | ✓ Complete |

---

## v1.1 Features: Enhanced Data Display + Export

**Context:** v1.1 adds enhanced data display features (grid view toggle, star ratings, category definitions, statement descriptions) and DOCX export with an Annex section. Research confirms these are standard UX patterns with well-established best practices.

---

### Grid View Toggle

**Context:** Search results currently display as cards only. v1.1 adds toggle between card view and grid/table view.

#### Table Stakes

- **Toggle control with clear visual state** — Button or segmented control showing current view (card/grid) with visual feedback on selection. User must immediately understand which view is active. — Complexity: **Low**

- **Persistent view preference** — View selection survives page refresh via localStorage. User shouldn't have to re-select their preference every session. — Complexity: **Low**

- **Grid displays key comparison columns** — Table columns for: Broad category, Training/Education level, Lead statement (truncated). Enables vertical scanning for comparison. — Complexity: **Low**

- **Keyboard accessible toggle** — Toggle button uses proper ARIA attributes (aria-pressed) and keyboard navigation (Space/Enter to activate). Screen reader announces current state. — Complexity: **Low**

- **Touch target minimum 44x44px** — Mobile-friendly tap target meets accessibility standards. — Complexity: **Low**

#### Differentiators

- **Column sorting in grid view** — Click column headers to sort (alphabetically for text, numerically for TEER levels). Provides quick filtering for users comparing multiple profiles. — Complexity: **Medium**

- **Column customization** — "Customize View" option lets users show/hide columns. Accommodates different user roles (manager vs. HR specialist) with different information priorities. — Complexity: **Medium**

- **Density control** — Compact/comfortable/relaxed row height options in grid view. Lets power users see more data at once or casual users have easier scanning. — Complexity: **Low**

---

### Proficiency Ratings Display

**Context:** NOC uses 1-5 scales for Skills (proficiency), Abilities (proficiency), Personal Attributes (importance), Work Activities (complexity), Work Context (frequency/duration/responsibility). Statements need visual ratings.

#### Table Stakes

- **Visual star display (1-5 filled stars)** — Standard 5-star rating component showing proficiency/importance/complexity level. Universally understood metaphor. — Complexity: **Low**

- **Scale meaning label** — Text next to stars explaining scale: "5 - Highest Level" or "5 - Every day, many times per day". Prevents misinterpretation (5 stars means what?). — Complexity: **Low**

- **Correct scale per statement type** — Skills/Abilities use "Proficiency (1-5)", Personal Attributes use "Importance (1-5)", Work Activities use "Complexity (1-5)", Work Context uses dimension-specific scales (Frequency, Duration, Degree of responsibility, etc.). — Complexity: **Medium**

- **Non-interactive stars** — Read-only display (not clickable rating input). This is display, not data entry. — Complexity: **Low**

- **Accessible text alternative** — Screen readers announce "Proficiency level 4 of 5" or equivalent. Stars alone are insufficient for accessibility. — Complexity: **Low**

#### Differentiators

- **Visual distinction for scale types** — Different colors or icons for Proficiency vs Importance vs Complexity (e.g., blue stars for proficiency, orange for importance). Helps users quickly identify scale type. — Complexity: **Low**

- **Inline scale definition tooltip** — Hovering "i" icon explains scale (1=Lowest, 5=Highest for proficiency; 1=Rarely, 5=Every day for frequency). Provides just-in-time help. — Complexity: **Low**

- **Filter by rating level** — In statement selection UI, filter to show only Level 4-5 statements. Helps managers focus on critical skills. — Complexity: **Medium**

---

### Category Definitions

**Context:** Each JD Element tab (Skills, Work Context, etc.) represents an NOC category. Users may not understand what "Work Context" encompasses. guide.csv provides category definitions.

#### Table Stakes

- **Definition displayed at section top** — Short paragraph explaining category before statements list. E.g., "Skills: Developed capacities that facilitate learning or the more rapid acquisition of knowledge." — Complexity: **Low**

- **Collapsible definition** — Uses `<details>/<summary>` or expand/collapse control. Definition visible by default but can be minimized to reduce screen space. — Complexity: **Low**

- **Accessible implementation** — If using custom accordion, uses button element with aria-expanded attribute. Keyboard navigable (Space/Enter to toggle). — Complexity: **Low**

- **Visual hierarchy** — Definition styled distinctly from statements (background color, border, or typography) to indicate meta-information. — Complexity: **Low**

#### Differentiators

- **"Learn More" link to OASIS** — Link to official NOC documentation for category. Provides authoritative source for users wanting deeper understanding. — Complexity: **Low**

- **Category metadata display** — Shows statement count in category: "Skills (24 statements)". Helps users understand scope. — Complexity: **Low**

---

### Statement Descriptions

**Context:** Each statement has an OASIS label (e.g., "Arm-Hand Steadiness"). guide.csv provides description for each label. Helps users understand statement meaning without visiting OASIS.

#### Table Stakes

- **Description on hover/focus** — Tooltip or popover displays description when hovering statement label. Provides contextual help without cluttering UI. — Complexity: **Low**

- **Brief inline text** — Description text is concise (1-2 sentences). Avoids overwhelming users with lengthy explanations. — Complexity: **Low**

- **Mobile-friendly display** — On touch devices, tapping "i" icon or label shows description (hover doesn't work). Ensures mobile accessibility. — Complexity: **Low**

- **Keyboard accessible** — Focus on tooltip trigger (icon or label) via Tab, press Space/Enter to reveal description. — Complexity: **Low**

#### Differentiators

- **"Show all descriptions" toggle** — Checkbox at section top to expand all descriptions vs. hover-only. Accommodates different user preferences. — Complexity: **Low**

- **Search includes descriptions** — Section search filters by statement text AND description. User searching "precision" finds "Arm-Hand Steadiness" via description match. — Complexity: **Low**

---

### DOCX Export

**Context:** v1.0 has PDF export via WeasyPrint. v1.1 adds Word/DOCX export for editability. Must match PDF structure (main content + compliance appendix).

#### Table Stakes

- **Document structure matches PDF** — Same sections in same order: Title, NOC Code, General Overview, JD Elements, Appendix A (Compliance Metadata). User expects format consistency. — Complexity: **Low**

- **Compliance appendix included** — DOCX contains same TBS Directive sections as PDF (6.2.3 Data Sources, 6.2.7 Manager Decisions, 6.3.5 Data Quality, AI Disclosure). Demonstrates regulatory compliance. — Complexity: **Low**

- **Editable text** — All content is native Word text (not images or locked fields). User can modify directly in Word. — Complexity: **Low**

- **Page break before appendix** — Appendix starts on new page. Separates compliance metadata from job description content. — Complexity: **Low**

- **Basic styling (headings, bullets, tables)** — Uses Word styles: Heading 1/2, List Bullet, Table Grid. Provides professional appearance. — Complexity: **Low**

- **File downloads with descriptive name** — Filename: "JD_[JobTitle]_[NOCCode]_[Date].docx". User can identify file without opening. — Complexity: **Low**

#### Differentiators

- **Header/footer with NOC code** — Document header shows job title + NOC code, footer shows compliance note. Provides context on every page. — Complexity: **Low** (python-docx supports headers/footers)

- **Custom styles for compliance sections** — Applies distinct style to compliance metadata (e.g., grey background for tables, smaller font). Visually separates regulatory content from JD content. — Complexity: **Low**

- **Metadata properties set** — Document properties (Author, Title, Subject) populated with job title, NOC code, generation date. Improves document management. — Complexity: **Low**

---

### Annex Section

**Context:** NOC profiles contain reference attributes (example job titles, career mobility paths, employment requirements, interests) not used in main JD. v1.1 adds Annex section to preserve this information for context.

#### Table Stakes

- **Annex section after compliance appendix** — Structure: Main JD → Appendix A (Compliance) → Annex A (Reference NOC Attributes). Clearly separates regulatory compliance from supplementary information. — Complexity: **Low**

- **Includes unused NOC attributes** — Lists: Example Titles, Employment Requirements, Career Mobility, Interests, Personal Attributes (if not selected). User has full NOC context. — Complexity: **Medium**

- **Clear labeling** — "Annex A: Reference NOC Attributes" or "Annex: Additional NOC Profile Information". Title indicates supplementary nature. — Complexity: **Low**

- **Formatted for readability** — Uses bullets or tables for lists. Employment Requirements shown in structured format (not paragraph dump). — Complexity: **Low**

- **Included in both PDF and DOCX** — Annex appears in both export formats. Consistency across outputs. — Complexity: **Low**

#### Differentiators

- **"Include Annex" checkbox** — User opts in/out of Annex section at export time. Some users want minimal JD, others want full context. — Complexity: **Low**

- **Annex summary table** — Table showing attribute categories and count: "Example Titles (8), Employment Requirements (5), Interests (6)". Provides overview before detail. — Complexity: **Low**

- **Annex uses smaller font** — Visual distinction (10pt for Annex vs 11pt for main JD). Signals "reference material, not primary content". — Complexity: **Low**

---

### Work Context Dimensions Display

**Context:** Work Context statements have multiple dimensions (Frequency, Duration, Degree of responsibility, etc.). Each dimension uses different scale. Must display correct dimension and scale meaning.

#### Table Stakes

- **Dimension label shown** — Statement displays "Frequency: 5 (Every day, many times per day)" not just "5 stars". User understands what the rating measures. — Complexity: **Low**

- **Correct dimension per statement** — Lookup dimension type from guide.csv (based on Work Context item code). Some items use Frequency, others use Duration or Responsibility. — Complexity: **Medium**

- **Scale meaning for dimension** — "Frequency: 1=Never, 5=Many times per day" shown in tooltip or inline. User interprets rating correctly. — Complexity: **Low**

- **Multiple dimensions per statement** — If statement has both Frequency and Duration, show both. E.g., "Face-to-Face Discussions: Frequency 4, Duration 3". — Complexity: **Medium**

#### Differentiators

- **Visual encoding for dimensions** — Different icons for Frequency (clock), Duration (hourglass), Responsibility (shield). Provides quick visual differentiation. — Complexity: **Low**

- **Dimension filter** — Filter Work Context statements by dimension type: "Show only high-responsibility items". Helps managers focus on decision-making aspects. — Complexity: **Medium**

---

## Anti-Features (Updated for v1.1)

Features to explicitly NOT build. Common mistakes in data display and export tools.

### Anti-Feature: Inline Editing of Ratings
**Why Avoid:** Ratings come from authoritative NOC data. Allowing managers to override ratings (e.g., change Proficiency from 3 to 5) breaks provenance chain and compliance. Directive 6.2.3 requires data integrity from authoritative source.

**What to Do Instead:** Display ratings as read-only. If manager disagrees with NOC rating, they can add note in General Overview or exclude statement entirely. Compliance metadata documents unmodified source data.

### Anti-Feature: Custom Statement Creation
**Why Avoid:** User-written statements lack NOC provenance. Entire compliance model depends on tracing content to authoritative source. Custom statements break audit trail.

**What to Do Instead:** Encourage statement selection from NOC. If truly custom content needed (e.g., org-specific tools), add as separate section with clear "User-Created Content" label and no NOC attribution. Keep NOC-sourced content pure.

### Anti-Feature: Exporting to Other Formats (Excel, JSON, etc.)
**Why Avoid:** Scope creep. PDF (print/archive) and DOCX (edit) cover use cases. Excel export implies data analysis workflow not core to JD creation. JSON export implies programmatic consumption (API use case, not single-user demo).

**What to Do Instead:** Focus on PDF and DOCX quality. If users need data in other formats, they can copy from Word. Don't build export formats without validated use case.

### Anti-Feature: Animated Star Filling
**Why Avoid:** Animated stars (filling from empty to proficiency level on page load) are visual gimmick without functional value. Adds complexity, slows perceived performance, and can distract from content.

**What to Do Instead:** Render stars in final state immediately. Use CSS (filled/empty star classes) not animation. Performance and clarity over decoration.

### Anti-Feature: Printing Grid View Directly
**Why Avoid:** Grid view is interactive comparison tool. Printing card view or grid view results in poor layout (wide tables, truncated text). Users should select profile first, then export formatted JD.

**What to Do Instead:** Grid view is screen-only. Disable print CSS for grid view or show message "Select a profile to export formatted job description." Export functionality (PDF/DOCX) provides proper print output.

---

## v1.1 Feature Dependencies

```
Search Results Grid View
  ↓ requires
  Additional OASIS Fields (Broad category, Training level)

Proficiency Stars
  ↓ requires
  guide.csv Scale Definitions
  ↓ requires
  Scale Meaning Labels

Category Definitions
  ↓ requires
  guide.csv Category Descriptions

Statement Descriptions
  ↓ requires
  guide.csv OASIS Label Descriptions

Work Context Dimensions
  ↓ requires
  guide.csv Dimension Types
  ↓ requires
  Dimension-Specific Scales

DOCX Export
  ↓ requires
  Annex Section Data
  ↓ optional
  Word Template (.docx file)

Annex Section
  ↓ requires
  Expanded NOC Scraping (Example Titles, Employment Requirements, etc.)
```

### Critical Path for v1.1
1. **guide.csv loading** — Multiple features depend on this. Load and parse guide.csv in backend service (csv_loader.py or similar). Expose via API or include in profile scrape response.
2. **Annex data scraping** — DOCX export depends on Annex, which depends on scraping additional OASIS fields. Expand scraper.py to capture Example Titles, Employment Requirements, Interests, Career Mobility.
3. **Statement rendering updates** — Stars, descriptions, dimensions all modify statement display. Update statement HTML template/rendering component once to accommodate all features.

---

## v1.1 MVP Recommendation

For v1.1 milestone, prioritize:

1. **Proficiency star display with scale meanings** — Table stakes feature, high user value (visual understanding of levels). Low complexity.
2. **Category definitions at section top** — Table stakes feature, helps users understand NOC structure. Low complexity.
3. **Statement descriptions in tooltip** — Differentiator feature, provides just-in-time help. Low complexity.
4. **DOCX export with basic structure** — Table stakes feature, matches PDF. Low-Medium complexity (python-docx basics).
5. **Annex section in exports** — Table stakes feature, preserves NOC context. Medium complexity (requires scraping expansion).

### Defer to post-v1.1:
- **Grid view toggle** — Differentiator feature, adds comparison workflow. Defer unless user testing shows strong need. Alternative: Enhance card view with more details instead.
- **Work Context dimensions display** — Table stakes for Work Context accuracy, but adds complexity. Include if time permits, otherwise defer to v1.2.
- **Column sorting in grid view** — Medium complexity, nice-to-have.
- **Filter by rating level** — Medium complexity, power user feature.

---

## v1.1 Implementation Complexity Summary

| Feature | Complexity | Effort (dev-days) | Dependencies |
|---------|------------|-------------------|--------------|
| Grid view toggle | Low-Medium | 2-3 | OASIS field expansion |
| Proficiency stars (visual) | Low | 1 | guide.csv loading |
| Scale meaning labels | Low | 0.5 | guide.csv loading |
| Category definitions | Low | 1 | guide.csv loading |
| Statement descriptions | Low | 1 | guide.csv loading |
| Work Context dimensions | Medium | 2 | guide.csv loading |
| DOCX export (basic) | Low-Medium | 2 | Existing ExportData |
| Annex section | Medium | 2-3 | OASIS scraping expansion |

**Total estimated effort (prioritized features only): 7-10 dev-days**

---

## Sources (Updated 2026-01-22)

### v1.1 Research: Grid View / Table Toggle
- [Table design UX guide](https://www.eleken.co/blog-posts/table-design-ux)
- [Data Table Design UX Patterns](https://www.pencilandpaper.io/articles/ux-pattern-analysis-enterprise-data-tables)
- [Table vs List vs Cards: When to Use Each](https://uxpatterns.dev/pattern-guide/table-vs-list-vs-cards)
- [Cards versus Table UX Patterns](https://cwcorbin.medium.com/redux-cards-versus-table-ux-patterns-1911e3ca4b16)

### v1.1 Research: Star Ratings / Proficiency Levels
- [What are Proficiency Levels in 2026?](https://www.talentguard.com/what-are-proficiency-levels)
- [Rating Scales in UX Research](https://www.interaction-design.org/literature/article/rating-scales-for-ux-research)
- [Navigating the Skills Proficiency Scale](https://www.tilr.com/blog/skills-proficiency-scale)

### v1.1 Research: Collapsible Sections / Tooltips
- [Accordion UI Examples: Best Practices](https://www.eleken.co/blog-posts/accordion-ui)
- [Accordion Pattern | UX Patterns](https://uxpatterns.dev/patterns/content-management/accordion)
- [Expand/Collapse design pattern - Canada.ca](https://design.canada.ca/common-design-patterns/collapsible-content.html)
- [Inline Help Examples](https://baymard.com/blog/inline-help)
- [Contextual Help UX Patterns](https://www.chameleon.io/blog/contextual-help-ux)

### v1.1 Research: python-docx / DOCX Export
- [python-docx Comprehensive Guide](https://medium.com/@HeCanThink/python-docx-a-comprehensive-guide-to-creating-and-manipulating-word-documents-in-python-a765cf4b4cb9)
- [Working with python-docx: Creating and Optimizing](https://coderivers.org/blog/pythondocx/)
- [python-docx Official Documentation](https://python-docx.readthedocs.io/)
- [8 Ways to Supercharge Microsoft Word Automation with Python](https://www.softkraft.co/python-word-automation/)
- [python-docx-template Documentation](https://docxtpl.readthedocs.io/)

### v1.1 Research: Annex / Appendix Best Practices
- [Annex vs Appendix: What is the difference?](https://researcher.life/blog/article/annex-vs-appendix-what-is-the-difference/)
- [Best practices for formatting appendices and annexes](https://www.linkedin.com/advice/1/what-best-practices-formatting-referencing-appendices)
- [Use an Appendix or Annex in Your Research Paper?](https://www.aje.com/arc/use-an-appendix-or-annex-in-research-paper)

### v1.1 Research: Statement Descriptions / Inline Help
- [UX writing | Grafana Toolkit](https://grafana.com/docs/writers-toolkit/write/style-guide/ux-writing/)
- [Form UI/UX Design Best Practices 2026](https://www.designstudiouiux.com/blog/form-ux-design-best-practices/)
- [How to Provide Contextual Help](https://userpilot.com/blog/contextual-help/)

### v1.1 Research: Toggle Buttons / Accessibility
- [Building accessible toggle buttons](https://joshcollinsworth.com/blog/accessible-toggle-buttons)
- [Toggle UX: Tips on Getting it Right](https://www.eleken.co/blog-posts/toggle-ux)
- [Accessibility of Toggle Buttons](https://dev.to/gzamann/accessibility-of-toggle-buttons-3ca9)

### v1.1 Research: NOC Proficiency Scales / Work Context
- [National Occupational Classification - Canada.ca](https://noc.esdc.gc.ca/)
- [OaSIS 2022 Dataset - Open Government Portal](https://open.canada.ca/data/en/dataset/eeb3e442-9f19-4d12-8b38-c488fe4f6e5e)
- [About the National Occupational Classification](https://noc.esdc.gc.ca/Home/AboutNOC)
- [NOC 2026 Revision Report](https://www.statcan.gc.ca/en/consultation/2024/noc/results-report)

### v1.1 Research: Data Visualization / Complexity Patterns
- [Data Visualization UX Best Practices (Updated 2026)](https://www.designstudiouiux.com/blog/data-visualization-ux-best-practices/)
- [UI considerations for designing large data tables](https://coyleandrew.medium.com/ui-considerations-for-designing-large-data-tables-aa6c1ea93797)

### v1.0 Research: Job Description Software Features
- [Gartner Peer Insights - Job Description Software](https://www.gartner.com/reviews/market/job-description-software)
- [Ongig - Job Description Software](https://www.ongig.com)
- [JDXpert Features](https://jdxpert.com/features/)
- [CompTool Job Description Manager](https://comptool.com/solutions/job-description-manager/)
- [Best Job Description Software 2025 - Ongig Blog](https://blog.ongig.com/job-descriptions/best-job-description-software/)

### v1.0 Research: Compliance & Audit Trail
- [Canada Directive on Automated Decision-Making](https://www.tbs-sct.canada.ca/pol/doc-eng.aspx?id=32592)
- [Guide on Scope of Directive](https://www.canada.ca/en/government/system/digital-government/digital-government-innovations/responsible-use-ai/guide-scope-directive-automated-decision-making.html)
- [HR Cloud - Compliance Audit Trail](https://www.hrcloud.com/resources/glossary/compliance-audit-trail)
- [Qandle Audit Trail Software](https://www.qandle.com/audit-trail-software.html)

### v1.0 Research: NOC Classification
- [Statistics Canada NOC 2021 Introduction](https://www.statcan.gc.ca/en/subjects/standard/noc/2021/introductionV1)
- [Job Bank and NOC](https://www.jobbank.gc.ca/trend-analysis/resources/national-occupational-classification)

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| v1.0 Table Stakes | HIGH | Well-documented across commercial tools |
| v1.0 Differentiators | HIGH | Directive requirements are explicit |
| v1.1 Display Features | HIGH | Standard UX patterns, multiple authoritative sources |
| v1.1 DOCX Export | HIGH | python-docx well-documented, existing implementation |
| v1.1 Annex Section | MEDIUM-HIGH | Annex best practices clear, NOC data availability confirmed |
| v1.1 Dependencies | HIGH | Logical flow from data sources |
