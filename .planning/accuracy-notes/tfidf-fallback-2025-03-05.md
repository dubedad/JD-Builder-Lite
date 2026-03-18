# Accuracy Note: TF-IDF Shortlisting Fallback

**Date introduced:** 2025-03-05
**Status:** Active (torch/sentence-transformers unavailable on Python 3.14)
**Files affected:**
- `src/matching/shortlisting/semantic_matcher.py`
- `src/matching/shortlisting/__init__.py`

---

## Why This Exists

PyTorch does not publish binary wheels for Python 3.14 as of 2025-03-05.
`sentence-transformers` requires `torch`, so it cannot be installed.
The classification pipeline would 503 on every `/api/allocate` call without a fallback.

The TF-IDF fallback keeps the pipeline functional but reduces shortlisting quality.
This document captures what changed, the accuracy risks, and how to evaluate impact
when Python 3.14 PyTorch wheels become available.

---

## What Changed

### Change 1 — `semantic_matcher.py`: TF-IDF fallback

**Original behaviour:** Imported `sentence_transformers` unconditionally at module level.
If not installed, any import of `SemanticMatcher` raised `ModuleNotFoundError`.

**New behaviour:** Tries to import `sentence_transformers` in a `try/except`. If it
fails, falls back to `_tfidf_cosine()`: a stemmed bag-of-words cosine similarity
implemented with Python `math` and no external dependencies.

**Fallback algorithm:**
1. Tokenize both texts: extract alpha tokens ≥ 3 chars, lowercase, remove stopwords
2. Apply 5-char prefix stem: `developer → devel`, `development → devel`, `managing → manag`
3. Build log-TF vectors over the union vocabulary of both texts
4. Compute cosine similarity: `dot(va, vb) / (||va|| * ||vb||)`

**Stemming rationale:** Without stemming, "software developer" vs a definition containing
"development" would score 0.0 despite sharing a root. Prefix stemming to 5 chars captures
the most common morphological variants without requiring a stemming library.

---

### Change 2 — `shortlisting/__init__.py`: keyword_boost safety net in filter

**Original filter:**
```python
if semantic_similarity >= min_similarity or best_inclusion_sim >= min_similarity:
```

**New filter:**
```python
if (semantic_similarity >= min_similarity
        or best_inclusion_sim >= min_similarity
        or keyword_boost > 0):
```

**Rationale:** TF-IDF frequently returns 0.0 for semantically related but lexically
distinct pairs (JD plain language vs TBS bureaucratic definition language). A group
like IT can have keyword_boost=0.15 (because "software" or "developer" appears in the
JD) but TF-IDF score 0.0, which would filter it out entirely before the LLM sees it.
The `keyword_boost > 0` condition ensures keyword-matched groups always reach the LLM.

---

## Accuracy Risk Assessment

### Risk 1: Missed candidates (HIGH under TF-IDF fallback)

**Mechanism:** TF-IDF scores 0.0 for groups where the JD vocabulary and definition
vocabulary don't overlap at the 5-char prefix level. The group never enters the
shortlist, so the LLM never considers it.

**Mitigated by:** `keyword_boost` safety net (Change 2). Groups in `TITLE_KEYWORD_GROUPS`
with a keyword match in the JD are always included.

**Not mitigated:** Groups not in `TITLE_KEYWORD_GROUPS`, or where the JD uses vocabulary
not covered by the keyword list. Example: a "Welfare Officer" (→ WP group) using language
like "counselling, community support, social services" may not be captured.

**Severity:** High for edge cases, low for common professional titles covered by the
keyword list (IT, AS, EN, EC, FI, PE, NU, etc.).

### Risk 2: Score scale difference (MEDIUM)

**Mechanism:** Neural cosine similarity meaningful range: ~0.2–0.8.
TF-IDF cosine similarity meaningful range: ~0.05–0.25.
The `min_similarity` threshold of 0.2 (set in `allocator.py`) was calibrated for neural
embeddings. Under TF-IDF, 0.2 is already a high score — many genuinely related texts
will fall below it.

**Mitigated by:** The keyword_boost safety net catches the most obvious cases.

**Not mitigated:** Subtler matches that would score 0.25–0.35 under neural embeddings
but only 0.05–0.15 under TF-IDF. These are cases where the JD is clearly in the right
domain but not using the exact vocabulary from the definition.

**Recommendation for future work:** When PyTorch 3.14 wheels are available, compare
shortlisting results side-by-side for 10 test JDs using both backends. Adjust
`min_similarity` in `allocator.py` accordingly.

### Risk 3: Prefix stem collisions (LOW)

**Mechanism:** `policy → polic`, `police → polic`. Unrelated terms that share a 5-char
prefix are treated as the same token, artificially inflating similarity.

**Severity:** Very low in the GoC occupational classification domain. The corpus does
not mix law enforcement ("police") with public policy ("policy") in the same contexts.

### Risk 4: No synonym or paraphrase capture (HIGH under TF-IDF fallback)

**Mechanism:** "Supervises staff" (JD) vs "involves the management of personnel" (definition).
Neural embeddings would score this ~0.5+. TF-IDF scores 0.0 — no shared stems.

**Mitigated by:** None directly. This is the fundamental limitation of lexical matching.

**Note:** The LLM classification step (Phase 4 of allocator pipeline) is NOT affected
by this — it uses the OpenAI API and has full language understanding. The risk is only
that groups eliminated at shortlisting never reach the LLM at all.

---

## How to Evaluate When PyTorch 3.14 Support Arrives

When `pip install sentence-transformers` succeeds on Python 3.14, run this evaluation:

### Step 1: Install dependencies
```bash
pip install sentence-transformers
```

### Step 2: Run the comparison script (to be written)
Create `scripts/compare_shortlisting.py` that:
1. Loads a set of test JDs (see Test Cases below)
2. Runs `shortlist_with_all_signals()` with neural backend
3. Stores results
4. Forces TF-IDF backend (monkey-patch `_semantic_matcher._use_neural = False`)
5. Runs again
6. Compares: Which candidates appeared in one but not the other? What rank?

### Step 3: Test cases to use

| Test JD                              | Expected top group | Risk area               |
|--------------------------------------|--------------------|-------------------------|
| Software developer, REST APIs        | IT                 | keyword covers this     |
| Policy analyst, federal budget       | EC                 | keyword covers this     |
| Registered nurse, acute care unit    | NU                 | keyword covers this     |
| Welfare officer, community programs  | WP                 | NOT in keyword list     |
| Translation, French/English          | TR                 | keyword covers this     |
| Correctional officer, federal penal  | CX                 | NOT in keyword list     |
| Drafting technician, mechanical      | DD or EG           | NOT in keyword list     |
| Meteorologist, climate research      | SE                 | NOT in keyword list     |

Groups NOT in `TITLE_KEYWORD_GROUPS`: CX, WP, DD, EG, SE, SRE, SRW, GT, etc.
These are the highest-risk cases for missed shortlisting under TF-IDF.

### Step 4: Metrics to record

For each test JD, record:
- Correct group in shortlist? (Y/N) — under neural and TF-IDF
- Rank of correct group — under neural and TF-IDF
- combined_score of correct group — under neural and TF-IDF
- Any false positives introduced by keyword_boost safety net?

---

## Removal Criteria

Remove the TF-IDF fallback code (revert to unconditional import) when:
1. `pip install torch` succeeds on the target Python version, AND
2. All test cases in the evaluation above pass with neural backend, AND
3. TF-IDF code is cleanly separable (it is — just remove the try/except and fallback functions)

Or: retain the fallback permanently as a graceful degradation path for environments
where torch cannot be installed (CI, minimal Docker images, etc.).

---

## Related Files

- `src/matching/shortlisting/semantic_matcher.py` — full accuracy analysis in module docstring
- `src/matching/shortlisting/__init__.py` — filter condition change with inline rationale
- `src/matching/allocator.py` — sets `min_similarity=0.2` for shortlist call
