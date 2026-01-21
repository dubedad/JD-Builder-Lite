# Feature Landscape: JD Builder Lite

**Domain:** Job Description Builder with NOC Data + Compliance/Provenance
**Researched:** 2026-01-21
**Scope:** Single-user, local-only, demo-quality application

---

## Table Stakes

Features users expect. Missing these = tool feels incomplete or broken.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **NOC Search** | Core value: find occupational profiles by title | Medium | Must query OASIS API or scrape; fuzzy matching expected |
| **Profile Selection** | Users need to pick from multiple matches | Low | Simple list UI with basic profile info |
| **NOC Data Display** | Must show scraped content organized by JD element | Medium | Requires mapping NOC structure to JD sections |
| **Statement Selection** | Core interaction: pick which NOC statements to include | Low | Checkbox/toggle UI pattern |
| **JD Preview** | Users must see what they're building | Low | Real-time preview as selections change |
| **PDF Export** | Final deliverable format for compliance | Medium | Print-to-PDF or PDF generation library |
| **Clear Data Attribution** | Users expect to know where content comes from | Low | Visual indicators showing NOC source |

### Table Stakes Rationale

These features form the minimum user journey described in the project context. Without any one of these, the core flow breaks:
1. Search --> 2. Select Profile --> 3. View Data --> 4. Pick Statements --> 5. Preview --> 6. Export

Commercial JD tools (JDXpert, Ongig) all provide search, selection, preview, and export as baseline functionality.

---

## Differentiators

Features that set JD Builder Lite apart. Not expected, but provide competitive/demo value.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Full Provenance Trail** | Compliance with Directive on Automated Decision-Making | High | Track every data source, timestamp, selection |
| **AI-Generated Overview with Attribution** | Saves time while maintaining traceability | Medium | OpenAI integration with clear "AI-generated" labeling |
| **NOC Source Metadata in Export** | Audit-ready documentation | Medium | Include NOC codes, scrape timestamps, source URLs |
| **Explainability Section** | Directive compliance: explain HOW decisions were made | Medium | Document which NOC elements mapped to which JD sections |
| **Selection Rationale Capture** | Why user chose specific statements | Low | Optional notes field per selection |
| **Compliance Metadata Block** | Machine-readable provenance in PDF | Medium | Structured data section at end of document |
| **Version Tracking** | Show document evolution | Medium | Track changes between sessions (requires persistence) |

### Differentiator Rationale

**Provenance/Traceability is the key differentiator.** Per Canada's Directive on Automated Decision-Making:
- Section 6.3.6 requires data traceability
- Must provide "meaningful explanation" of how/why decisions were made
- Must document data sources, processing, and outputs

Most commercial JD tools focus on:
- Bias elimination (Ongig, Textio)
- Template libraries (JDXpert)
- ATS integration (all enterprise tools)

None emphasize audit-trail provenance for government compliance. This is the unique value.

---

## Anti-Features

Features to explicitly NOT build. Common mistakes or scope creep traps.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| **User Authentication** | Single-user demo; adds complexity without value | Local-only storage, no login |
| **Multi-User Collaboration** | Out of scope for demo; requires backend infrastructure | Design for single user |
| **ATS/HRIS Integration** | Enterprise feature; requires partnerships, APIs | Focus on PDF export |
| **Template Library** | Time-consuming to create; NOC data IS the content | Use NOC as source of truth |
| **Bias Detection/Inclusive Language** | Specialized feature; well-served by competitors | Use NOC language verbatim (government-vetted) |
| **SEO Optimization** | Not relevant for internal job descriptions | Skip entirely |
| **Job Posting/Distribution** | Publishing workflow out of scope | PDF is final output |
| **Compensation Data** | Separate data source; different compliance concerns | Exclude from scope |
| **Version History UI** | Nice-to-have but complex; demo doesn't need it | Single-session workflow |
| **Offline Caching of NOC Data** | Licensing/data freshness concerns | Always fetch fresh |
| **Custom Styling/Branding** | Scope creep; demo doesn't need it | Single clean design |
| **Multi-Language Support** | Enterprise feature; NOC data is in specific language | English only (or French as separate effort) |

### Anti-Feature Rationale

**Scope discipline is critical for demo-quality.** The project explicitly states:
- Single user
- Local-only
- Demo quality

Commercial tools (JDXpert at ~$8-10K/year, Ongig enterprise pricing) justify cost through:
- Multi-user collaboration
- Integration ecosystems
- Content libraries
- Bias detection

JD Builder Lite differentiates through provenance, not feature breadth.

---

## Feature Dependencies

```
                    +------------------+
                    |   NOC Search     |
                    +--------+---------+
                             |
                             v
                    +------------------+
                    | Profile Selection|
                    +--------+---------+
                             |
                             v
                    +------------------+
                    |  OASIS Scraping  |
                    +--------+---------+
                             |
                    +--------+---------+
                    |                  |
                    v                  v
           +---------------+   +------------------+
           | Data Display  |   | Provenance Store |
           +-------+-------+   +--------+---------+
                   |                    |
                   v                    |
           +---------------+            |
           | Statement     |            |
           | Selection     +------------+
           +-------+-------+            |
                   |                    |
                   v                    |
           +---------------+            |
           | AI Overview   +------------+
           | Generation    |            |
           +-------+-------+            |
                   |                    |
                   v                    v
           +---------------+   +------------------+
           | JD Preview    |   | Compliance       |
           +-------+-------+   | Metadata         |
                   |           +--------+---------+
                   |                    |
                   +----------+---------+
                              |
                              v
                    +------------------+
                    |   PDF Export     |
                    +------------------+
```

### Dependency Notes

1. **Provenance Store** must be populated at every step:
   - Search query + timestamp
   - Selected profile + NOC code
   - Scraped data + source URLs + scrape timestamp
   - User selections + selection timestamps
   - AI generation + prompt used + model version

2. **PDF Export** depends on BOTH content AND provenance metadata

3. **AI Overview** is optional but requires:
   - Selected statements (input)
   - Provenance tracking (for explainability)

---

## MVP Recommendation

For MVP, prioritize these table stakes + one differentiator:

### MVP Features (Phase 1)

1. **NOC Search** - Find profiles by job title
2. **Profile Selection** - Pick from results
3. **OASIS Scraping** - Get full NOC data
4. **Data Display by JD Element** - Organize for user
5. **Statement Selection** - Core interaction
6. **JD Preview** - See what you're building
7. **PDF Export** - Final deliverable
8. **Basic Provenance** - NOC code + source URL in export

### Defer to Post-MVP

| Feature | Reason to Defer |
|---------|----------------|
| AI-Generated Overview | Adds OpenAI dependency; can work without it |
| Full Provenance Trail | Basic provenance sufficient for demo |
| Selection Rationale Capture | Nice-to-have, not essential |
| Compliance Metadata Block | Can add structured data later |
| Version Tracking | Requires persistence layer |

### Phase 2 (AI Enhancement)

- AI-Generated Overview with OpenAI
- AI provenance tracking (prompt, model, timestamp)
- "AI-generated" visual labeling

### Phase 3 (Full Compliance)

- Complete provenance trail
- Compliance metadata block in PDF
- Explainability section
- Audit-ready formatting

---

## Compliance-Specific Features

Given the Directive on Automated Decision-Making requirements, these features are not just differentiators but potentially required for the intended use case.

### Mandatory for Compliance

| Requirement (Directive) | Feature Implementation |
|------------------------|----------------------|
| Data traceability (6.3.6) | Provenance store tracking all data sources |
| Meaningful explanation | Explainability section showing NOC-to-JD mapping |
| Document decisions | Audit trail of user selections |
| Lawful collection | Clear attribution to public NOC data |

### Provenance Data Model

Each JD element should track:

```
{
  "element_id": "uuid",
  "content": "statement text",
  "source": {
    "type": "NOC" | "AI_GENERATED" | "USER_INPUT",
    "noc_code": "12345" (if NOC),
    "noc_element": "Main duties" (if NOC),
    "source_url": "https://noc.esdc.gc.ca/...",
    "scraped_at": "2026-01-21T10:30:00Z"
  },
  "ai_metadata": {
    "model": "gpt-4" (if AI),
    "prompt_hash": "abc123",
    "generated_at": "timestamp"
  },
  "selection": {
    "selected_by": "user",
    "selected_at": "timestamp",
    "rationale": "optional user note"
  }
}
```

---

## Competitive Landscape Summary

| Tool | Focus | Pricing | Key Features |
|------|-------|---------|--------------|
| JDXpert | Job data management | ~$8-10K/year | 4,500+ templates, version control, integrations |
| Ongig | Inclusive language | Enterprise | Bias detection, SEO, ATS integration |
| Textio | Language optimization | Enterprise | Real-time bias scoring, predictive analytics |
| CompTool | Compensation alignment | Varies | ChatGPT integration, team collaboration |
| **JD Builder Lite** | NOC provenance/compliance | Demo/Free | Audit trail, government data integration |

JD Builder Lite occupies a unique niche: government compliance-focused, NOC-specific, provenance-first.

---

## Sources

### Job Description Software Features
- [Gartner Peer Insights - Job Description Software](https://www.gartner.com/reviews/market/job-description-software)
- [Ongig - Job Description Software](https://www.ongig.com)
- [JDXpert Features](https://jdxpert.com/features/)
- [CompTool Job Description Manager](https://comptool.com/solutions/job-description-manager/)
- [Best Job Description Software 2025 - Ongig Blog](https://blog.ongig.com/job-descriptions/best-job-description-software/)

### Compliance & Audit Trail
- [Canada Directive on Automated Decision-Making](https://www.tbs-sct.canada.ca/pol/doc-eng.aspx?id=32592)
- [Guide on Scope of Directive](https://www.canada.ca/en/government/system/digital-government/digital-government-innovations/responsible-use-ai/guide-scope-directive-automated-decision-making.html)
- [HR Cloud - Compliance Audit Trail](https://www.hrcloud.com/resources/glossary/compliance-audit-trail)
- [Qandle Audit Trail Software](https://www.qandle.com/audit-trail-software.html)

### NOC Classification
- [National Occupational Classification - Canada.ca](https://noc.esdc.gc.ca/)
- [Statistics Canada NOC 2021 Introduction](https://www.statcan.gc.ca/en/subjects/standard/noc/2021/introductionV1)
- [Job Bank and NOC](https://www.jobbank.gc.ca/trend-analysis/resources/national-occupational-classification)

### Web Scraping Compliance
- [Web Scraping Legal Issues 2025](https://groupbwt.com/blog/is-web-scraping-legal/)
- [Is Web Scraping Legal - Apify](https://blog.apify.com/is-web-scraping-legal/)

### Anti-Patterns in Job Descriptions
- [Randstad - Mistakes to Avoid](https://www.randstadusa.com/business/business-insights/employer-branding/mistakes-avoid-job-description/)
- [LinkedIn - What Not to Include](https://www.linkedin.com/business/talent/blog/talent-acquisition/what-not-to-include-when-writing-job-descriptions)
- [Ongig Blog - Job Description Mistakes](https://blog.ongig.com/job-descriptions/job-description-mistakes/)

### MVP Development
- [MVP Web Development - Netguru](https://www.netguru.com/blog/mvp-web-development)
- [How to Build MVP - TopFlight Apps](https://topflightapps.com/ideas/how-to-develop-an-mvp/)

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Table Stakes | HIGH | Well-documented across commercial tools |
| Differentiators | HIGH | Directive requirements are explicit |
| Anti-Features | MEDIUM | Based on scope constraints; may need adjustment |
| Dependencies | HIGH | Logical flow from user journey |
| Compliance Features | HIGH | Directive text is authoritative source |
