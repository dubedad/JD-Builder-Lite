# Feature Landscape: Style-Enhanced JD Generation

**Domain:** Vocabulary-Constrained Style Transfer for Job Descriptions
**Researched:** 2026-02-03
**Scope:** v3.0 Feature — Style learning from example JDs with NOC vocabulary constraint

---

## Context

The user's requirement defines a unique challenge:

> "Use example JDs as style references. Continue using authoritative NOC language from JobForge 2.0. For each statement: keep the authoritative NOC sentence, PLUS add a 'styled' sentence that mimics the example JD writing style BUT using NOC words."

This is **vocabulary-constrained style transfer** — a specific variant of text style transfer where:
1. Style patterns are learned from example documents
2. Generated content must use ONLY vocabulary from a predefined authoritative source (NOC)
3. Output is dual-format: original authoritative sentence + styled companion sentence

---

## Table Stakes

Features users expect for style-enhanced JD generation. Missing = feature feels incomplete or broken.

### Style Reference Upload

| Feature | Why Expected | Complexity | Dependencies |
|---------|--------------|------------|--------------|
| **Upload example JDs** | Users need to provide style references; PDF/DOCX/TXT formats expected | Medium | File parsing libraries |
| **Multiple reference support** | Single JD may not capture full style; 2-5 examples provide better style signal | Low | Upload UI extension |
| **Reference persistence** | Users expect uploaded references to persist within session | Low | localStorage or session state |
| **Reference preview** | Users need to verify correct file was uploaded | Low | Document viewer |

**Rationale:** Research on few-shot prompting confirms that "examples act as templates, showing LLMs the tone, structure, and style to replicate" ([PromptHub Guide](https://www.prompthub.us/blog/the-few-shot-prompting-guide)). Multiple diverse examples significantly improve style consistency.

### Style Extraction Display

| Feature | Why Expected | Complexity | Dependencies |
|---------|--------------|------------|--------------|
| **Style analysis feedback** | Users need confirmation that style was captured | Medium | LLM style analysis |
| **Extracted style characteristics** | Show what patterns were detected (sentence length, tone, structure) | Medium | Style feature extraction |
| **Style confidence indicator** | Users should know if uploaded examples provide sufficient style signal | Low | Analysis metrics |

**Rationale:** Research shows LLMs analyze "sentence length, vocabulary, punctuation, paragraph structure, and even how transitions are handled" ([Latitude Blog](https://latitude-blog.ghost.io/blog/how-examples-improve-llm-style-consistency/)). Making these visible builds user trust.

### Dual-Format Statement Output

| Feature | Why Expected | Complexity | Dependencies |
|---------|--------------|------------|--------------|
| **Original NOC statement displayed** | User requirement: "keep the authoritative NOC sentence" | Low | Existing statement display |
| **Styled companion sentence** | User requirement: "add a 'styled' sentence" | High | Style transfer generation |
| **Visual distinction between formats** | Users must clearly see which is authoritative vs styled | Low | CSS styling |
| **Both versions in export** | Compliance requires authoritative source; usability wants styled version | Low | Export template extension |

**Rationale:** This is the core differentiator of the feature. The dual-format preserves compliance (TBS Directive 6.2.3 requires traceable authoritative sources) while delivering improved readability.

### Vocabulary Constraint Enforcement

| Feature | Why Expected | Complexity | Dependencies |
|---------|--------------|------------|--------------|
| **NOC vocabulary extraction** | Build word list from NOC profile for constraint | Medium | NLP tokenization |
| **Constraint violation detection** | Flag if styled sentence uses non-NOC words | Medium | Vocabulary matching |
| **Regeneration on violation** | Automatically retry if constraint violated | Low | Retry logic |
| **Constraint report in export** | Compliance audit: prove all words from NOC | Medium | Provenance tracking |

**Rationale:** OpenAI's API supports `logit_bias` for token probability adjustment, but is limited to 300 tokens ([OpenAI Help Center](https://help.openai.com/en/articles/5247780-using-logit-bias-to-alter-token-probability-with-the-openai-api)). For strict vocabulary constraint, post-generation validation with regeneration is more reliable than attempting token-level constraint.

### Statement-Level Control

| Feature | Why Expected | Complexity | Dependencies |
|---------|--------------|------------|--------------|
| **Toggle styled version on/off per statement** | User may want original for some, styled for others | Low | Checkbox per statement |
| **Edit styled sentence** | User may want to tweak AI output | Low | Inline editing |
| **Regenerate single statement** | Retry without regenerating entire JD | Low | Single-statement API call |
| **Accept/reject styled version** | Explicit approval before including in export | Low | State management |

**Rationale:** Fine-grained control matches existing v2.0 patterns (checkbox selection per statement) and supports compliance by ensuring human oversight of AI-generated content.

---

## Differentiators

Features that set this implementation apart. Not expected, but valued.

### Advanced Style Learning

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Style template library** | Pre-loaded organizational style templates (formal GC, plain language, technical) | Medium | Reduces upload friction |
| **Style comparison view** | Side-by-side: original vs multiple style options | Medium | Helps users choose |
| **Style persistence across sessions** | Save learned styles for reuse | Medium | Requires storage |
| **Style mixing** | Combine attributes from multiple references (e.g., tone from A, structure from B) | High | Advanced prompt engineering |

**Research basis:** ZeroStylus research demonstrates "hierarchical template acquisition from reference texts" enables "selective adaptation using reference subsets without reprocessing entire corpora" ([arXiv](https://arxiv.org/html/2505.07888v1)).

### Intelligent Vocabulary Handling

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Vocabulary expansion suggestions** | If NOC vocabulary too limited, suggest related terms from NOC hierarchy | Medium | Requires NOC ontology |
| **Synonym mapping within NOC** | Use NOC-authorized synonyms to enable style variation | Medium | NOC thesaurus data |
| **Vocabulary coverage report** | Show % of style patterns achievable with available vocabulary | Low | Analytics display |
| **Domain-specific stop word handling** | Preserve domain terms during vocabulary constraint | Low | Configurable stop word list |

**Research basis:** "Even advanced Large Language Models encounter difficulties when dealing with out-of-vocabulary terms or unique jargon that are characteristic of specialized fields" ([ACM DL](https://dl.acm.org/doi/fullHtml/10.1145/3669754.3669784)). Smart vocabulary handling addresses this.

### Generation Quality Features

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Style fidelity score** | Quantify how well output matches reference style | Medium | Style similarity metrics |
| **Content preservation score** | Verify meaning unchanged from original NOC statement | Medium | Semantic similarity |
| **Readability metrics** | Show Flesch-Kincaid or similar for styled vs original | Low | Standard metrics |
| **A/B comparison mode** | Generate multiple style variations for user selection | Medium | Multiple generation calls |

**Research basis:** Text style transfer evaluation uses "tri-axial metrics assessing style consistency, content preservation, and expression quality" ([arXiv](https://arxiv.org/html/2505.07888v1)). Exposing these builds trust.

### Workflow Enhancements

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Batch styling** | Apply style to all selected statements at once | Medium | Bulk generation |
| **Style preview before generation** | Show expected output format before full generation | Low | Sample generation |
| **Undo/redo for style changes** | Non-destructive editing workflow | Low | State history |
| **Style export for sharing** | Export learned style profile for organizational reuse | Medium | Style serialization |

---

## Anti-Features

Features to explicitly NOT build. Common mistakes in vocabulary-constrained generation systems.

### Anti-Feature: Real-Time Token Constraint

**Why Avoid:** OpenAI's `logit_bias` parameter limits constraint to 300 tokens. NOC vocabulary for a single occupation can exceed 1,000 unique terms. Token-level constraint during generation is technically infeasible with current API limitations.

**What to Do Instead:** Post-generation validation with regeneration. Generate freely, validate vocabulary compliance, regenerate if violated. More reliable and avoids API limitations.

### Anti-Feature: Style Fine-Tuning

**Why Avoid:** Fine-tuning requires substantial training data (hundreds of examples), costs money, and creates model maintenance burden. For 2-5 example documents, fine-tuning is overkill and produces worse results than few-shot prompting.

**What to Do Instead:** Few-shot prompting with reference examples in context. Research confirms "few-shot prompting can be particularly helpful in specialized domains where gathering vast amounts of data can be difficult" ([IBM](https://www.ibm.com/think/topics/few-shot-prompting)).

### Anti-Feature: Creative Word Generation

**Why Avoid:** The user requirement explicitly states "NEVER fabricate content — all words must come from NOC vocabulary." Any creative generation that introduces non-NOC words breaks the provenance chain and compliance requirements.

**What to Do Instead:** Enforce vocabulary constraint rigorously. If styling is impossible with available vocabulary, degrade gracefully to original NOC statement rather than fabricate.

### Anti-Feature: Automated Style Detection Without User Confirmation

**Why Avoid:** Style is subjective. What the system detects as "formal" may not match user's intent. Automated style application without user review leads to unexpected outputs.

**What to Do Instead:** Always show extracted style characteristics and get user confirmation before applying. Provide "style preview" before committing to generation.

### Anti-Feature: Replacing Original NOC Statement

**Why Avoid:** TBS Directive compliance requires traceable authoritative source. Styled sentence is AI-generated derivative, not authoritative source. Replacing original breaks audit trail.

**What to Do Instead:** Dual-format output as specified. Original NOC statement is the compliance anchor; styled sentence is value-add. Both must be present in export with clear labeling.

### Anti-Feature: Unrestricted Style Mixing

**Why Avoid:** Mixing incompatible styles (e.g., casual social media + formal legal) produces incoherent output. Users may upload inappropriate examples without understanding impact.

**What to Do Instead:** Style compatibility checking. Warn if uploaded references have conflicting characteristics. Recommend organizational template library for consistent results.

### Anti-Feature: Sentence-Level Hallucination Tolerance

**Why Avoid:** Even one hallucinated term in a job description can have legal/compliance implications. Zero tolerance for vocabulary violations is appropriate for this domain.

**What to Do Instead:** Strict validation with graceful degradation. If styled sentence cannot be generated within vocabulary constraint after N attempts, fall back to original NOC statement with explanation.

---

## Feature Dependencies

```
Style Reference Upload
  |
  v
Style Extraction & Analysis
  |
  +---> Style Template Library (optional)
  |
  v
NOC Vocabulary Extraction (from existing profile scrape)
  |
  v
Styled Sentence Generation
  |
  +---> Post-Generation Vocabulary Validation
  |       |
  |       v
  |     Regeneration Loop (if constraint violated)
  |
  v
Dual-Format Statement Display
  |
  +---> Statement-Level Controls (toggle, edit, regenerate)
  |
  v
Export with Both Versions
  |
  +---> Constraint Compliance Report
```

### Critical Path

1. **NOC Vocabulary Extraction** — Foundation for constraint enforcement. Extract all words from scraped NOC profile (already available in v2.0 data model).

2. **Style Reference Processing** — Parse uploaded documents, extract text, feed to style analysis. Depends on file format handling (PDF, DOCX, TXT).

3. **Styled Sentence Generator** — Core LLM integration. Few-shot prompt with style examples + vocabulary constraint instruction + post-validation.

4. **Dual-Format Display** — UI modification to show original + styled side-by-side or stacked. Extends existing statement display component.

---

## Implementation Complexity Summary

| Feature | Complexity | Effort (dev-days) | Dependencies |
|---------|------------|-------------------|--------------|
| **Table Stakes** ||||
| Style reference upload | Medium | 2-3 | PDF/DOCX parsing |
| Style extraction display | Medium | 2 | LLM style analysis |
| Dual-format statement output | Medium | 2-3 | UI component extension |
| Vocabulary constraint enforcement | Medium | 2-3 | NLP tokenization |
| Statement-level control | Low | 1-2 | Existing UI patterns |
| **Differentiators** ||||
| Style template library | Medium | 2-3 | Content curation |
| Vocabulary expansion suggestions | Medium | 3 | NOC hierarchy data |
| Style fidelity score | Medium | 2 | Similarity metrics |
| Batch styling | Medium | 2 | Bulk API handling |

**Estimated total (table stakes only): 10-14 dev-days**

---

## Expected Behavior Patterns

Based on research, users expect these behavior patterns for vocabulary-constrained style transfer:

### 1. Graceful Degradation

When vocabulary constraint cannot be satisfied:
- Attempt regeneration (up to 3 times)
- If still failing, show original NOC statement with explanation
- Never show fabricated content
- Log failure for analysis

### 2. Transparent Processing

Users expect to see:
- What style characteristics were extracted
- What vocabulary is available for constraint
- Why a particular styled sentence was generated
- Confidence level of the output

### 3. Human-in-the-Loop

AI-generated content requires human approval:
- Preview before committing
- Edit capability
- Accept/reject per statement
- Clear labeling of AI vs authoritative content

### 4. Compliance Preservation

Styled content must not compromise compliance:
- Original NOC statement always preserved
- Styled sentence clearly marked as AI-generated
- Vocabulary constraint report in export
- Audit trail for style decisions

---

## Sources

### Style Transfer Research
- [Long Text Style Transfer with LLMs - arXiv](https://arxiv.org/html/2505.07888v1) — ZeroStylus hierarchical framework
- [LLM-Based Text Style Transfer Survey - IEEE](https://ieeexplore.ieee.org/document/10915631/) — Overview of TST methods
- [Text Style Transfer Introduction - Cloudera](https://text-style-transfer.fastforwardlabs.com/) — Foundational concepts
- [Deep Learning for Text Style Transfer Survey - MIT Press](https://direct.mit.edu/coli/article/48/1/155/108845/Deep-Learning-for-Text-Style-Transfer-A-Survey) — Academic survey

### Constrained Generation
- [Constrained Decoding Guide - Michael Brenndoerfer](https://mbrenndoerfer.com/writing/constrained-decoding-structured-llm-output) — Grammar-guided generation
- [Controlling Your LLM - Medium](https://medium.com/@docherty/controlling-your-llm-deep-dive-into-constrained-generation-1e561c736a20) — Practical implementation
- [Guiding LLMs The Right Way - arXiv](https://arxiv.org/html/2403.06988v1) — DOMINO algorithm
- [Controllable Text Generation Survey - arXiv](https://arxiv.org/html/2408.12599v1) — CTG methods overview

### Few-Shot Prompting
- [Few-Shot Prompting Guide - PromptingGuide.ai](https://www.promptingguide.ai/techniques/fewshot) — Best practices
- [How Examples Improve LLM Style Consistency - Latitude](https://latitude-blog.ghost.io/blog/how-examples-improve-llm-style-consistency/) — Example-based learning
- [What is Few Shot Prompting - IBM](https://www.ibm.com/think/topics/few-shot-prompting) — Industry perspective
- [The Few Shot Prompting Guide - PromptHub](https://www.prompthub.us/blog/the-few-shot-prompting-guide) — Practical examples

### Vocabulary Constraints
- [Logit Bias in OpenAI API - OpenAI Help](https://help.openai.com/en/articles/5247780-using-logit-bias-to-alter-token-probability-with-the-openai-api) — Token control (300 limit)
- [Improving Paraphrase Quality - ACM DL](https://dl.acm.org/doi/fullHtml/10.1145/3669754.3669784) — Domain-specific paraphrasing
- [Paraphrase Strategy - Yale](https://poorvucenter.yale.edu/Paraphrase-Strategy3) — Handling specialized vocabulary

### Job Description Writing
- [Writing Effective Job Descriptions - Wright State](https://www.wright.edu/human-resources/writing-an-effective-job-description) — Style guidelines
- [Job Description Guide - SHRM](https://www.shrm.org/topics-tools/tools/job-descriptions) — HR best practices
- [RewriteLM - arXiv](https://arxiv.org/html/2305.15685v2) — Instruction-tuned rewriting

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Style extraction via few-shot | HIGH | Well-documented technique, multiple authoritative sources |
| Vocabulary constraint approach | MEDIUM-HIGH | Post-validation more reliable than token-level; logit_bias limitation confirmed |
| Dual-format output UX | HIGH | Standard comparison pattern, existing v2.0 UI precedent |
| Content preservation | MEDIUM | Trade-off inherent in style transfer; metrics available |
| Generation quality | MEDIUM | Depends on vocabulary richness; graceful degradation needed |
| Compliance preservation | HIGH | Clear requirements, existing provenance patterns |

---

## MVP Recommendation

For initial v3.0 style-enhanced generation, prioritize:

1. **Style reference upload (PDF/DOCX)** — Core capability, enables all else
2. **Simple style extraction feedback** — "Detected: formal tone, complex sentences"
3. **Dual-format output** — Original + styled, clearly labeled
4. **Basic vocabulary constraint** — Post-generation validation, regenerate on violation
5. **Statement-level toggle** — Use styled / use original per statement

### Defer to post-v3.0:
- Style template library (requires content curation)
- Style mixing (complex prompt engineering)
- Vocabulary expansion suggestions (requires NOC ontology work)
- Style fidelity scoring (nice-to-have, not blocking)

---

*Last updated: 2026-02-03 — Style-enhanced JD generation feature research*
