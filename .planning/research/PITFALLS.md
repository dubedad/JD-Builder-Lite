# Domain Pitfalls

**Domain:** Government website scraping, LLM integration, compliance/provenance tracking
**Project:** JD Builder Lite (NOC/OASIS scraper with OpenAI integration)
**Researched:** 2026-01-21
**Confidence:** HIGH (verified with official documentation and multiple sources)

---

## Critical Pitfalls

Mistakes that cause rewrites, compliance failures, or major blockers.

---

### CRITICAL-1: Brittle CSS Selectors Break on Government Site Updates

**What goes wrong:** Scrapers built with tightly-coupled CSS selectors (e.g., `div.content > table:nth-child(3) > tr > td.data`) break silently when Canada.ca or OASIS restructures HTML. The NOC classification underwent major structural changes in 2021 (moving from 4-digit to 5-digit codes) and NOC 2026 updates are already in research phase.

**Why it happens:**
- Developers use browser DevTools to copy exact selectors without considering fragility
- Government sites undergo periodic redesigns and accessibility improvements
- No monitoring alerts when scraping returns unexpected/empty results

**Consequences:**
- Scraper returns empty or malformed data
- Users receive incomplete job descriptions
- Compliance audit trail shows gaps or errors
- Trust in the tool erodes

**Prevention:**
1. Use semantic selectors when possible (IDs, data attributes, ARIA labels) over positional selectors
2. Build multiple fallback selector strategies for critical data points
3. Implement content validation - check that scraped text matches expected patterns (e.g., NOC codes match `\d{5}` pattern)
4. Add automated health checks that run daily against known-good pages
5. Store raw HTML snapshots for debugging when parsing fails
6. Consider AI-assisted extraction as a fallback (Claude/GPT can parse HTML contextually)

**Warning signs:**
- Scraper returns empty arrays where data was expected
- Field values are truncated or contain HTML fragments
- Console shows parsing errors without crashing
- Data validation fails silently

**Detection:** Implement schema validation on scraped output. If `occupation_title` is empty or `noc_code` doesn't match expected format, fail loudly.

**Phase mapping:** Address in Phase 1 (scraping foundation). Build selector abstraction layer with validation from day one.

**Sources:**
- [Browserless: State of Web Scraping 2026](https://www.browserless.io/blog/state-of-web-scraping-2026)
- [BrightData: How to Fix Inaccurate Web Scraping Data](https://brightdata.com/blog/web-data/fix-inaccurate-web-scraping-data)
- [Canada.ca NOC 2021 structure changes](https://noc.esdc.gc.ca/)

---

### CRITICAL-2: LLM Hallucinations in Compliance-Critical Output

**What goes wrong:** OpenAI models generate plausible but fabricated job requirements, qualifications, or responsibilities that don't exist in the source NOC/OASIS data. This is catastrophic for a compliance tool where provenance/traceability is the core value proposition.

**Why it happens:**
- LLMs interpolate from training data when source context is insufficient
- Prompts don't explicitly constrain output to provided source material
- JSON mode doesn't guarantee schema compliance (only that output is valid JSON)
- No validation that generated content maps back to source data

**Consequences:**
- Job descriptions contain fabricated requirements
- Audit trail shows LLM-generated content that can't be traced to source
- Compliance with Directive on Automated Decision-Making is compromised
- Legal/HR liability for incorrect job requirements

**Prevention:**
1. Use OpenAI Structured Outputs (not just JSON mode) with strict schema enforcement
2. Include explicit source citations in prompts: "Generate ONLY from the following source text. If information is not present, state 'Not specified in source.'"
3. Implement post-generation validation: cross-reference generated fields against source data
4. Add confidence scoring: flag any generated content that doesn't have direct source mapping
5. Store source text alongside generated output for audit comparison
6. Consider RAG architecture: retrieve relevant NOC/OASIS sections before generation

**Warning signs:**
- Generated content is longer/more detailed than source material
- Output contains industry-standard language not present in scraped data
- Validation against source text fails silently
- Users report requirements they can't find in NOC documentation

**Detection:** Implement semantic similarity checking between generated content and source text. Flag any paragraph with low similarity score for human review.

**Phase mapping:** Address in Phase 2 (LLM integration). Never allow unvalidated LLM output in compliance-critical fields.

**Sources:**
- [OpenAI Structured Outputs documentation](https://platform.openai.com/docs/guides/structured-outputs)
- [MDPI: Mitigating LLM Hallucinations Using Multi-Agent Framework](https://www.mdpi.com/2078-2489/16/7/517)
- [AWS: Prevent factual errors with Automated Reasoning checks](https://aws.amazon.com/blogs/aws/prevent-factual-errors-from-llm-hallucinations-with-mathematically-sound-automated-reasoning-checks-preview/)

---

### CRITICAL-3: Incomplete Audit Trail Breaks Directive Compliance

**What goes wrong:** Provenance metadata is captured inconsistently - some fields populated, others missing timestamps, source URLs change or expire, no chain of custody from scrape to generation to output.

**Why it happens:**
- Audit logging added as afterthought rather than designed in
- Manual processes create gaps (humans miss timestamps, backdate entries)
- No schema enforcement on provenance records
- Source URLs not captured at scrape time (only at generation time)

**Consequences:**
- Cannot demonstrate compliance with Directive on Automated Decision-Making
- Audit reveals gaps that trigger compliance review
- Cannot reproduce how a specific job description was generated
- Legal exposure if challenged on hiring decisions

**Prevention:**
1. Design provenance schema first, before any feature code
2. Every data transformation must create an immutable audit record
3. Capture: source URL, scrape timestamp, raw HTML hash, parsed data, LLM prompt, LLM response, model version, generation timestamp
4. Use append-only storage for audit trail (no updates/deletes)
5. Implement automated completeness checks: reject any output missing required provenance fields
6. Store all artifacts needed to reproduce the exact output (prompts, model versions, parsed data)

**Warning signs:**
- Audit records have NULL timestamps or missing fields
- Cannot answer "where did this requirement come from?"
- Source URLs in audit trail return 404
- Different team members log different fields inconsistently

**Detection:** Run completeness validation on every audit record before allowing output. Require 100% field population.

**Phase mapping:** Design in Phase 1 (data model), enforce throughout all phases. Treat incomplete audit records as system errors.

**Sources:**
- [Canada Directive on Automated Decision-Making](https://www.tbs-sct.canada.ca/pol/doc-eng.aspx?id=32592)
- [InscopeHQ: Audit Trail Requirements Guidelines](https://www.inscopehq.com/post/audit-trail-requirements-guidelines-for-compliance-and-best-practices)
- [Nutrient: Audit trail for compliance](https://www.nutrient.io/blog/audit-trail/)

---

## Moderate Pitfalls

Mistakes that cause delays, technical debt, or degraded user experience.

---

### MODERATE-1: OpenAI Rate Limits Crash Application

**What goes wrong:** Application sends requests without throttling, hits 429 errors, and either crashes or returns errors to users during peak usage.

**Why it happens:**
- No client-side rate limiting implemented
- Exponential backoff not configured
- max_tokens set too high (rate limits calculated on max, not actual)
- Shared API keys aggregate usage across environments

**Consequences:**
- Users see errors during generation
- Batch processing jobs fail mid-execution
- Development/staging environments consume production quota
- Application appears unreliable

**Prevention:**
1. Implement exponential backoff with jitter (use tenacity or similar library)
2. Set max_tokens to match expected response size (not arbitrary high values)
3. Use separate API keys for dev/staging/production
4. Cache LLM responses - same NOC code + same prompt = same output
5. Implement request queuing with configurable rate limiting
6. Monitor rate limit headers to predict approaching limits

**Warning signs:**
- Intermittent 429 errors in logs
- Generation takes much longer during certain times
- Users report "try again later" messages
- API costs spike unexpectedly (retry storms)

**Detection:** Log all API calls with timestamps. Alert if 429 rate exceeds threshold (e.g., >5% of requests).

**Phase mapping:** Implement in Phase 2 (LLM integration). Use tenacity decorator pattern from day one.

**Sources:**
- [OpenAI Cookbook: How to handle rate limits](https://cookbook.openai.com/examples/how_to_handle_rate_limits)
- [OpenAI Help: Rate limit best practices](https://help.openai.com/en/articles/6891753-what-are-the-best-practices-for-managing-my-rate-limits-in-the-api)

---

### MODERATE-2: PDF Generation Layout Breaks with Dynamic Content

**What goes wrong:** PDF output has broken page breaks (tables split mid-row, headers cut off), missing fonts, or content overlapping headers/footers.

**Why it happens:**
- HTML designed for screen rendering, not print
- No print stylesheet (`@media print`)
- Relying on CSS Grid/Flexbox which PDF engines handle inconsistently
- Custom fonts not embedded or served from inaccessible URLs
- Header/footer templates overlap content due to margin misconfiguration

**Consequences:**
- Professional appearance compromised
- Job descriptions difficult to read when printed
- Tables unreadable when split across pages
- Branding fonts replaced with system defaults

**Prevention:**
1. Create dedicated print stylesheet with explicit page-break rules
2. Use web-safe fonts or embed fonts with @font-face
3. Avoid CSS Grid/Flexbox for critical layout - use explicit positioning
4. Set explicit widths/heights (PDFs don't handle auto-sizing well)
5. Reserve margin space for headers/footers using `@page` CSS rules
6. Test with actual Puppeteer/Playwright PDF generation, not browser print preview
7. For tables: use `break-inside: avoid` and `thead { display: table-header-group }`

**Warning signs:**
- Table rows split across pages
- Fonts look different in PDF vs. browser
- Headers/footers overlap content
- Users complain about printing issues

**Detection:** Generate test PDFs with various content lengths during CI. Visual regression testing against reference PDFs.

**Phase mapping:** Address in Phase 3 (PDF export). Create print stylesheet before implementing PDF generation.

**Sources:**
- [Smallpdf: HTML PDF Conversion Formatting Issues](https://smallpdf.com/blog/html-pdf-conversion-formatting-issues-resolve)
- [Puppeteer issue #10505: Header overlap](https://github.com/puppeteer/puppeteer/issues/10505)
- [Browserless: PDF generation with Puppeteer](https://www.browserless.io/blog/puppeteer-pdf-generator)

---

### MODERATE-3: Scraper Blocked by Government Site Changes

**What goes wrong:** Canada.ca or OASIS site implements new bot protection, changes URL structure, or requires JavaScript rendering, and scraper silently fails or gets blocked.

**Why it happens:**
- Government sites periodically update security measures
- Simple HTTP requests don't execute JavaScript
- No monitoring of scraper success/failure rates
- robots.txt changes not detected

**Consequences:**
- Scraping stops working without warning
- Users can't generate new job descriptions
- Cached data becomes stale
- Trust in tool reliability erodes

**Prevention:**
1. Use headless browser (Playwright/Puppeteer) for JavaScript-rendered content
2. Monitor robots.txt before each scraping session
3. Implement health checks that validate scraping works against known pages
4. Add respectful delays between requests (3-6 seconds minimum)
5. Store user-agent and request patterns in config (easy to adjust)
6. Consider caching NOC data locally with periodic refresh (NOC data is relatively static)
7. Implement graceful degradation - use cached data if live scraping fails

**Warning signs:**
- Scraper returns HTML error pages instead of content
- Response times increase dramatically
- robots.txt contains new disallow rules
- HTTP 403 or 429 errors in logs

**Detection:** Validate scraped content against expected patterns. Alert on consecutive failures or unexpected response codes.

**Phase mapping:** Address in Phase 1 (scraping). Use headless browser from start, implement health monitoring.

**Sources:**
- [PromptCloud: Web Scraping Challenges](https://www.promptcloud.com/blog/web-scraping-challenges/)
- [Zyte: Challenges of scaling Playwright and Puppeteer](https://www.zyte.com/blog/challenges-of-scaling-playwright-and-puppeteer-for-web-scraping/)

---

### MODERATE-4: JSON Mode vs Structured Outputs Confusion

**What goes wrong:** Developer uses `response_format: { type: "json_object" }` (JSON mode) thinking it enforces schema, but LLM returns valid JSON with wrong/missing fields.

**Why it happens:**
- Documentation confusion between JSON mode and Structured Outputs
- JSON mode only guarantees valid JSON syntax, not schema compliance
- Missing `strict: true` flag in structured outputs configuration
- Schema not properly defined with `additionalProperties: false`

**Consequences:**
- Generated job descriptions missing required fields
- Parsing code crashes on unexpected structure
- Data validation catches errors late in pipeline
- Inconsistent output format across requests

**Prevention:**
1. Use Structured Outputs (not JSON mode) with explicit JSON schema
2. Always set `strict: true` and `additionalProperties: false`
3. Use Pydantic (Python) or Zod (JS) for schema definition in SDK
4. Validate response against schema even with Structured Outputs (defense in depth)
5. Document expected schema with examples in codebase

**Warning signs:**
- LLM adds unexpected fields to response
- Required fields sometimes missing
- Response structure varies between requests
- Parsing errors on "valid" JSON responses

**Detection:** Schema validation on every LLM response. Fail fast on schema mismatch.

**Phase mapping:** Address in Phase 2 (LLM integration). Use Structured Outputs from first API call.

**Sources:**
- [OpenAI: Introducing Structured Outputs](https://openai.com/index/introducing-structured-outputs-in-the-api/)
- [eesel.ai: Guide to OpenAI JSON Mode](https://www.eesel.ai/blog/openai-json-mode)

---

## Minor Pitfalls

Mistakes that cause annoyance or minor issues but are easily fixed.

---

### MINOR-1: Timeout Defaults Too Short for Complex Pages

**What goes wrong:** Playwright/Puppeteer times out on slow government pages before content loads, but works fine in development.

**Why it happens:**
- Default timeouts (30s) insufficient for slow government servers
- Network conditions in production differ from development
- Heavy pages with many assets take longer to reach "networkidle"

**Consequences:**
- Intermittent scraping failures
- Difficult to reproduce in development
- Users see random errors

**Prevention:**
1. Set explicit timeouts based on observed load times (60-90s for government sites)
2. Use `networkidle` or specific element selectors rather than fixed delays
3. Implement retry logic for timeout errors specifically
4. Block unnecessary resources (images, fonts, analytics) to speed loading

**Phase mapping:** Configure in Phase 1 (scraping infrastructure).

---

### MINOR-2: Not Capturing OpenAI Model Version in Audit

**What goes wrong:** Audit trail shows a request was made to "gpt-4" but doesn't capture the specific model snapshot, making reproduction impossible when model is updated.

**Why it happens:**
- Model version seems like a minor detail
- OpenAI continuously updates models behind version aliases

**Consequences:**
- Cannot reproduce exact output for audit purposes
- Different results when re-running same prompt

**Prevention:**
1. Log the full model identifier from API response
2. Capture the `system_fingerprint` from response headers
3. Document model selection rationale in audit trail

**Phase mapping:** Include in Phase 2 audit schema design.

---

### MINOR-3: Source URLs Expire or Change

**What goes wrong:** Audit trail contains URLs that no longer resolve to the original content, breaking provenance verification.

**Why it happens:**
- Government sites restructure URLs
- Content is moved or archived
- No snapshot of source content captured

**Consequences:**
- Audit verification fails on old records
- Cannot prove what content was scraped

**Prevention:**
1. Store HTML snapshot hash alongside URL
2. Archive scraped HTML in storage (not just parsed data)
3. Use web archive (archive.org) links as backup references

**Phase mapping:** Design in Phase 1 data model.

---

## Phase-Specific Warnings

| Phase | Topic | Likely Pitfall | Mitigation |
|-------|-------|---------------|------------|
| Phase 1 | Scraping foundation | CRITICAL-1 (brittle selectors) | Build selector abstraction with validation |
| Phase 1 | Data model | CRITICAL-3 (incomplete audit) | Design provenance schema first |
| Phase 1 | Scraping | MODERATE-3 (site blocking) | Use headless browser, implement health checks |
| Phase 2 | LLM integration | CRITICAL-2 (hallucinations) | Structured Outputs + source validation |
| Phase 2 | LLM integration | MODERATE-1 (rate limits) | Exponential backoff from day one |
| Phase 2 | LLM integration | MODERATE-4 (JSON confusion) | Structured Outputs, not JSON mode |
| Phase 3 | PDF export | MODERATE-2 (layout breaks) | Print stylesheet, explicit positioning |
| All | Compliance | CRITICAL-3 (audit gaps) | Treat incomplete audit as system error |

---

## Risk Matrix Summary

| Pitfall | Likelihood | Impact | Detection Difficulty | Mitigation Cost |
|---------|------------|--------|---------------------|-----------------|
| CRITICAL-1: Brittle selectors | HIGH | HIGH | MEDIUM | LOW |
| CRITICAL-2: LLM hallucinations | HIGH | CRITICAL | HIGH | MEDIUM |
| CRITICAL-3: Incomplete audit | MEDIUM | CRITICAL | LOW | LOW |
| MODERATE-1: Rate limits | HIGH | MEDIUM | LOW | LOW |
| MODERATE-2: PDF layout | MEDIUM | LOW | LOW | MEDIUM |
| MODERATE-3: Site blocking | LOW | HIGH | LOW | MEDIUM |
| MODERATE-4: JSON confusion | MEDIUM | MEDIUM | LOW | LOW |

---

## Directive on Automated Decision-Making Considerations

For compliance with Canada's Directive on Automated Decision-Making, this tool must:

1. **Complete Algorithmic Impact Assessment (AIA)** before production use
2. **Provide meaningful explanation** to users of how job descriptions were generated
3. **Maintain audit trail** that allows reconstruction of the decision process
4. **Monitor outcomes** to verify compliance with human rights obligations
5. **Provide recourse mechanism** for users to challenge or request human review

The CRITICAL-2 (hallucinations) and CRITICAL-3 (incomplete audit) pitfalls directly threaten Directive compliance and must be prioritized.

**Sources:**
- [Canada.ca: Directive on Automated Decision-Making](https://www.tbs-sct.canada.ca/pol/doc-eng.aspx?id=32592)
- [Canada.ca: Algorithmic Impact Assessment tool](https://www.canada.ca/en/government/system/digital-government/digital-government-innovations/responsible-use-ai/algorithmic-impact-assessment.html)
- [Canada.ca: Guide to Peer Review of Automated Decision Systems](https://www.canada.ca/en/government/system/digital-government/digital-government-innovations/responsible-use-ai/guide-peer-review-automated-decision-systems.html)
