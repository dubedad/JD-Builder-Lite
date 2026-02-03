# Phase 12: Constrained Generation - Research

**Researched:** 2026-02-03
**Domain:** Few-shot LLM prompting, vocabulary-constrained generation with retry logic, semantic equivalence validation, graceful degradation
**Confidence:** HIGH

## Summary

This phase implements the generation mechanics for styling NOC statements using few-shot prompting with vocabulary validation and retry logic. The research examined best practices for OpenAI GPT-4 few-shot prompting, retry strategies with the tenacity library (already in project dependencies), vocabulary post-validation patterns, semantic similarity checking, and graceful degradation when generation fails.

The existing codebase already has the foundation: OpenAI client (v1.109.1), tenacity library (v9.0.0) for retry logic, VocabularyValidator for post-validation, and FewShotExample data structures with 5-7 curated examples per section. Phase 11 established the provenance schema (StyledStatement, VersionHistory, confidence scores). This phase implements the generation loop: construct few-shot prompt → call GPT-4o → validate vocabulary → retry if validation fails → fall back to original on exhaustion → track full provenance.

The research confirms that few-shot prompting with post-validation is the appropriate approach for this domain (not constrained decoding, which would require custom inference infrastructure). GPT-4 best practices recommend 2-5 examples with clear delimiters and purpose clauses. Retry logic should use exponential backoff with jitter (3-5 retries typical). Semantic equivalence checking requires sentence-transformers library with lightweight models like all-MiniLM-L6-v2 (22MB, 5x faster than alternatives, 84-85% accuracy). Graceful degradation to original NOC statements is a standard fallback pattern for LLM applications.

**Primary recommendation:** Build generation service using existing OpenAI client with tenacity retry decorator, validate with existing VocabularyValidator, use sentence-transformers for semantic similarity (cosine similarity ≥0.75 threshold), implement retry budget of 3 attempts with exponential backoff, fall back to original NOC statement with clear ORIGINAL_NOC content type on failure.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| openai | 1.109.1 (existing) | GPT-4o API client for few-shot generation | Modern v1.x client with streaming support; already used for overview generation |
| tenacity | 9.0.0 (existing) | Retry logic with exponential backoff | Official OpenAI recommendation; declarative retry patterns with wait strategies |
| sentence-transformers | 3.x (NEW) | Semantic similarity checking for equivalence validation | State-of-the-art sentence embeddings; 15k+ pre-trained models on Hugging Face |
| VocabularyValidator | (existing) | Post-validation against NOC vocabulary | Already implements tokenization, stop word filtering, coverage calculation |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| typing | stdlib | Type hints for generation functions | All new generation service code |
| dataclasses | stdlib | Configuration structures | Retry configuration, threshold constants |
| datetime | stdlib | Timestamp tracking | Generation attempt metadata per PROV-05 |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| sentence-transformers | OpenAI embeddings API | sentence-transformers runs locally (no API cost/latency), sufficient accuracy for binary equivalence check |
| all-MiniLM-L6-v2 | all-mpnet-base-v2 | MiniLM is 5x faster (22MB vs 110MB), 84% vs 87% accuracy - speed matters more for real-time generation |
| Retry with tenacity | Manual backoff logic | tenacity is declarative, handles jitter automatically, recommended by OpenAI |
| Post-validation | Constrained decoding | Post-validation simpler, doesn't require custom inference, sufficient for vocabulary constraints |

**Installation:**
```bash
pip install sentence-transformers
```

## Architecture Patterns

### Recommended Service Structure
```
src/services/
├── generation_service.py    # NEW: Core generation orchestrator
├── llm_service.py           # EXTEND: Add few-shot prompt builder
├── few_shot_examples.py     # EXISTING: Examples database
└── vocabulary/
    └── validator.py          # EXISTING: Post-validation
```

### Pattern 1: Few-Shot Prompt Construction

**What:** Build system prompt + few-shot examples + user input with clear delimiters.
**When to use:** Every styled statement generation request.
**Example:**
```python
# Source: OpenAI best practices + existing few_shot_examples.py pattern
from src.services.few_shot_examples import get_high_quality_examples
from src.services.style_constants import STYLE_RULES

def build_few_shot_prompt(
    section: str,
    noc_statement: str,
    n_examples: int = 5
) -> tuple[str, str]:
    """Build system and user prompts for styled generation.

    Args:
        section: JD element (key_activities, skills, effort, working_conditions)
        noc_statement: Original NOC statement to style
        n_examples: Number of examples (3-5 recommended per research)

    Returns:
        (system_prompt, user_prompt) tuple
    """
    # Get style rule for section
    style_rule = STYLE_RULES.get(section, {})
    pattern = style_rule.get("pattern", "")
    purpose = style_rule.get("purpose", "")

    # Get high-quality examples (quality_weight >= 0.85)
    examples = get_high_quality_examples(section, min_weight=0.85)[:n_examples]

    # Build system prompt
    system_prompt = f"""You are a Canadian federal job description stylist. Transform concise NOC statements into detailed, professional job description statements.

Guidelines:
- Follow the {pattern} pattern: {purpose}
- Use ONLY words from the NOC vocabulary (no invented terms)
- Preserve the original meaning exactly (semantic equivalence required)
- Expand abbreviations and add context for clarity
- Write in professional, formal government style
- Output a single complete sentence"""

    # Build user prompt with few-shot examples
    example_text = "\n\n".join([
        f"NOC Input: {ex['noc_input']}\nStyled Output: {ex['styled_output']}"
        for ex in examples
    ])

    user_prompt = f"""Here are examples of the {section} styling pattern:

{example_text}

Now style this NOC statement using the same pattern:
NOC Input: {noc_statement}
Styled Output:"""

    return system_prompt, user_prompt
```

### Pattern 2: Generation with Retry and Validation

**What:** Orchestrate generation → validation → retry loop with tenacity.
**When to use:** All styled statement generation.
**Example:**
```python
# Source: OpenAI Cookbook + tenacity documentation + research findings
from openai import OpenAI
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
    retry_if_exception_type
)
from src.vocabulary.validator import VocabularyValidator

client = OpenAI()

# Retry configuration (3-5 attempts per research)
MAX_RETRIES = 3
VOCABULARY_COVERAGE_THRESHOLD = 95.0  # 95% NOC words required

@retry(
    wait=wait_random_exponential(min=1, max=10),  # 1-10 sec exponential backoff
    stop=stop_after_attempt(MAX_RETRIES),
    retry_if_exception_type=VocabularyValidationError
)
def generate_with_validation(
    section: str,
    noc_statement: str,
    validator: VocabularyValidator
) -> dict:
    """Generate styled statement with vocabulary validation and retry.

    Raises VocabularyValidationError to trigger tenacity retry.

    Returns:
        {
            "styled_text": str,
            "validation_result": dict,
            "attempt_count": int
        }
    """
    system_prompt, user_prompt = build_few_shot_prompt(section, noc_statement)

    # Call GPT-4o
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3,  # Lower than overview (0.7) - less creativity needed
        max_tokens=200,
        logprobs=True,  # Enable for confidence calculation
        top_logprobs=1
    )

    styled_text = response.choices[0].message.content.strip()

    # Validate vocabulary coverage
    validation = validator.validate_text(styled_text)

    if validation["coverage_percentage"] < VOCABULARY_COVERAGE_THRESHOLD:
        # Log the attempt for debugging
        non_noc = ", ".join(validation["non_noc_words"][:5])  # First 5
        raise VocabularyValidationError(
            f"Coverage {validation['coverage_percentage']}% < {VOCABULARY_COVERAGE_THRESHOLD}%. "
            f"Non-NOC words: {non_noc}"
        )

    return {
        "styled_text": styled_text,
        "validation_result": validation,
        "logprobs": response.choices[0].logprobs  # For confidence calculation
    }

class VocabularyValidationError(Exception):
    """Raised when generated text fails vocabulary validation."""
    pass
```

### Pattern 3: Semantic Equivalence Checking

**What:** Verify styled output preserves original meaning using sentence embeddings.
**When to use:** Post-generation validation before accepting styled variant.
**Example:**
```python
# Source: sentence-transformers documentation + research findings
from sentence_transformers import SentenceTransformer, util
import torch

# Load model once at service initialization (lightweight: 22MB)
semantic_model = SentenceTransformer("all-MiniLM-L6-v2")

# Threshold per research: 0.75-0.85 range, use 0.75 for conservative acceptance
SEMANTIC_SIMILARITY_THRESHOLD = 0.75

def check_semantic_equivalence(
    original: str,
    styled: str
) -> dict:
    """Check if styled text preserves original meaning.

    Args:
        original: Original NOC statement
        styled: Styled variant

    Returns:
        {
            "is_equivalent": bool,
            "similarity_score": float (0-1),
            "threshold": float
        }
    """
    # Encode both texts to embeddings (384-dimensional vectors)
    embeddings = semantic_model.encode(
        [original, styled],
        convert_to_tensor=True
    )

    # Compute cosine similarity (default metric)
    similarity = util.cos_sim(embeddings[0], embeddings[1]).item()

    return {
        "is_equivalent": similarity >= SEMANTIC_SIMILARITY_THRESHOLD,
        "similarity_score": round(similarity, 4),
        "threshold": SEMANTIC_SIMILARITY_THRESHOLD
    }
```

### Pattern 4: Confidence Score from LogProbs

**What:** Calculate generation confidence from token log probabilities.
**When to use:** Every generation to populate StyledStatement.confidence_score.
**Example:**
```python
# Source: Research on LLM confidence scoring + OpenAI logprobs
import math

def calculate_confidence_score(logprobs_data) -> float:
    """Calculate confidence score from OpenAI logprobs.

    Uses mean token probability as confidence indicator per research.

    Args:
        logprobs_data: LogProbs object from OpenAI response

    Returns:
        float: Confidence score 0-1 (0=low, 1=high)
    """
    if not logprobs_data or not logprobs_data.content:
        return 0.5  # Default medium confidence if no logprobs

    # Extract log probabilities for each token
    log_probs = [
        token.logprob
        for token in logprobs_data.content
        if token.logprob is not None
    ]

    if not log_probs:
        return 0.5

    # Convert log probs to probabilities and take mean
    # logprob is natural log, so exp(logprob) = probability
    probs = [math.exp(lp) for lp in log_probs]
    mean_prob = sum(probs) / len(probs)

    # Clip to 0-1 range (should already be, but ensure)
    return max(0.0, min(1.0, mean_prob))
```

### Pattern 5: Graceful Degradation with Fallback

**What:** Fall back to original NOC statement when retry budget exhausted.
**When to use:** After all retry attempts fail validation.
**Example:**
```python
# Source: Research on graceful degradation + Phase 11 CONTEXT
from src.models.ai import StyleContentType, StyledStatement
from datetime import datetime
import uuid

def generate_styled_statement(
    noc_statement_id: str,
    noc_text: str,
    section: str,
    validator: VocabularyValidator
) -> StyledStatement:
    """Generate styled statement with graceful fallback.

    Tries generation with retry, falls back to original on failure.

    Args:
        noc_statement_id: Statement ID (e.g., "key_activities-0")
        noc_text: Original NOC statement text
        section: JD element section
        validator: VocabularyValidator instance

    Returns:
        StyledStatement with either AI_STYLED or ORIGINAL_NOC content_type
    """
    try:
        # Attempt generation with retry
        result = generate_with_validation(section, noc_text, validator)

        # Check semantic equivalence
        semantic_check = check_semantic_equivalence(noc_text, result["styled_text"])

        if not semantic_check["is_equivalent"]:
            raise SemanticEquivalenceError(
                f"Similarity {semantic_check['similarity_score']} < "
                f"{SEMANTIC_SIMILARITY_THRESHOLD}"
            )

        # Success - calculate confidence from logprobs
        confidence = calculate_confidence_score(result.get("logprobs"))

        return StyledStatement(
            original_noc_statement_id=noc_statement_id,
            original_noc_text=noc_text,
            styled_text=result["styled_text"],
            content_type=StyleContentType.AI_STYLED,
            confidence_score=confidence,
            retry_count=0,  # Track via tenacity context if needed
            vocabulary_coverage=result["validation_result"]["coverage_percentage"],
            generated_at=datetime.utcnow(),
            version_id=str(uuid.uuid4())
        )

    except (VocabularyValidationError, SemanticEquivalenceError) as e:
        # Retry budget exhausted or semantic check failed
        # Fall back to original NOC statement
        return StyledStatement(
            original_noc_statement_id=noc_statement_id,
            original_noc_text=noc_text,
            styled_text=noc_text,  # Use original as styled
            content_type=StyleContentType.ORIGINAL_NOC,  # Mark as fallback
            confidence_score=1.0,  # Original is always "confident"
            retry_count=MAX_RETRIES,  # Indicate exhausted retries
            vocabulary_coverage=100.0,  # Original is 100% NOC by definition
            generated_at=datetime.utcnow(),
            version_id=str(uuid.uuid4())
        )

class SemanticEquivalenceError(Exception):
    """Raised when styled text doesn't preserve original meaning."""
    pass
```

### Anti-Patterns to Avoid

- **Infinite retry loops:** Always set stop_after_attempt limit (3-5 max). Research shows diminishing returns beyond 5 attempts.
- **Synchronous blocking on generation:** Use streaming or async patterns for UI responsiveness during multi-statement generation.
- **Ignoring semantic equivalence:** Vocabulary validation alone is insufficient; must verify meaning preservation.
- **Discarding failed attempts:** All attempts should be logged to StyleVersionHistory for audit trail per Phase 11.
- **Self-reported confidence scores:** Research shows prompting LLM for confidence is unreliable; use logprobs instead.
- **Hardcoded prompts:** Keep system/user prompt construction in dedicated functions for easy iteration and testing.

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Retry with backoff | Custom sleep() loops with manual jitter | tenacity library decorators | Handles exponential backoff, jitter, conditional retry, max attempts declaratively |
| Sentence embeddings | Custom word vector averaging | sentence-transformers library | State-of-the-art models; 15k+ pre-trained options; handles tokenization, pooling |
| Vocabulary validation | Reimplement word checking | Existing VocabularyValidator | Already handles stop words, case folding, coverage calculation |
| Prompt version tracking | Manual version strings | Existing PROMPT_VERSION in llm_service.py | Already established pattern for provenance |
| Token probability parsing | Manual logprob extraction | OpenAI client logprobs parameter | Returns structured LogProbs object with token data |

**Key insight:** The OpenAI + tenacity + sentence-transformers stack is the industry standard for constrained LLM generation with post-validation. Don't reinvent these patterns.

## Common Pitfalls

### Pitfall 1: Over-Prompting for Style Adherence

**What goes wrong:** Including too many instructions or examples causes GPT-4 to prioritize style over vocabulary constraints.
**Why it happens:** GPT-4 is highly instruction-following; verbose prompts can override implicit vocabulary constraints.
**How to avoid:** Keep system prompt concise (3-5 guidelines max). Use 3-5 examples, not 10+. Research shows diminishing returns beyond 5 examples.
**Warning signs:** High retry rates (>50% of generations failing vocabulary validation); non-NOC words consistently appearing in outputs.

### Pitfall 2: Semantic Similarity Threshold Too High

**What goes wrong:** Setting threshold >0.85 causes excessive fallbacks to original statements.
**Why it happens:** all-MiniLM-L6-v2 achieves ~84% accuracy on STS benchmarks; higher thresholds reject valid paraphrases.
**How to avoid:** Start with 0.75 threshold; monitor fallback rate. If >30% fallback, lower threshold to 0.70. If <5%, can raise to 0.80.
**Warning signs:** Most styled statements marked ORIGINAL_NOC despite passing vocabulary validation; similarity scores clustering in 0.70-0.75 range.

### Pitfall 3: Not Handling Model Failures Gracefully

**What goes wrong:** OpenAI API errors (rate limits, timeouts) crash generation service.
**Why it happens:** Tenacity retry_if_exception_type only retries specified exceptions; API errors not included by default.
**How to avoid:** Use retry_if_exception_type=(VocabularyValidationError, openai.RateLimitError, openai.APITimeoutError).
**Warning signs:** Generation requests failing with unhandled exceptions; no fallback to ORIGINAL_NOC on network errors.

### Pitfall 4: Batch Generation Without Progress Feedback

**What goes wrong:** Styling 20+ statements locks UI with no feedback; users assume app is frozen.
**Why it happens:** Synchronous generation loop blocks request thread.
**How to avoid:** Implement streaming SSE endpoint or async generation with progress events. Phase 12 CONTEXT leaves this to Claude's discretion.
**Warning signs:** User complaints about "app freezing"; high bounce rate during multi-statement styling.

### Pitfall 5: Confidence Score Miscalibration

**What goes wrong:** Logprobs-based confidence doesn't correlate with actual quality; users lose trust in green/yellow/red indicators.
**Why it happens:** Token probability measures fluency, not semantic correctness or vocabulary compliance.
**How to avoid:** Use composite score: (logprobs_confidence * 0.3) + (vocabulary_coverage/100 * 0.4) + (semantic_similarity * 0.3). Weight vocabulary and semantics higher than fluency.
**Warning signs:** High-confidence (green) outputs frequently rejected by users; vocabulary validation failures on "green" statements.

## Code Examples

Verified patterns from research sources:

### Complete Generation Service Initialization

```python
# Source: Integration of all research findings
from sentence_transformers import SentenceTransformer
from src.vocabulary.index import VocabularyIndex
from src.vocabulary.validator import VocabularyValidator
from openai import OpenAI

class GenerationService:
    """Service for constrained generation with vocabulary validation.

    Handles full generation lifecycle:
    1. Few-shot prompt construction
    2. GPT-4o generation with retry
    3. Vocabulary post-validation
    4. Semantic equivalence checking
    5. Confidence score calculation
    6. Graceful degradation to original
    """

    def __init__(self, vocab_index: VocabularyIndex):
        """Initialize generation service.

        Args:
            vocab_index: Loaded VocabularyIndex for validation
        """
        self.openai_client = OpenAI()  # Uses OPENAI_API_KEY from env
        self.validator = VocabularyValidator(vocab_index)

        # Load semantic similarity model (22MB, fast)
        self.semantic_model = SentenceTransformer("all-MiniLM-L6-v2")

        # Configuration
        self.max_retries = 3
        self.vocab_threshold = 95.0  # 95% NOC coverage required
        self.semantic_threshold = 0.75  # Cosine similarity minimum

    def generate_styled_statement(
        self,
        noc_statement_id: str,
        noc_text: str,
        section: str
    ) -> StyledStatement:
        """Generate styled statement with full validation and fallback.

        Implementation per patterns 1-5 above.
        """
        # Implementation from Pattern 5
        pass
```

### Tenacity Retry with Error Logging

```python
# Source: OpenAI Cookbook + tenacity best practices
from tenacity import retry, stop_after_attempt, wait_random_exponential, before_log, after_log
import logging

logger = logging.getLogger(__name__)

@retry(
    wait=wait_random_exponential(min=1, max=10),
    stop=stop_after_attempt(3),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.INFO),
    retry=retry_if_exception_type((VocabularyValidationError, openai.RateLimitError))
)
def generate_with_retry(**kwargs):
    """Generate with comprehensive retry logging."""
    pass
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Constrained decoding | Few-shot prompting + post-validation | 2024-2025 | Simpler infrastructure; no custom inference needed; OpenAI API sufficient |
| Self-reported confidence | Token log probabilities | 2024-2025 | Research shows logprobs far more reliable than prompted confidence scores |
| all-mpnet-base-v2 | all-MiniLM-L6-v2 | 2024-2026 | 5x faster for only 3% accuracy loss; better for real-time generation |
| Manual retry loops | Declarative tenacity decorators | 2023-2026 | Exponential backoff with jitter built-in; less error-prone |

**Deprecated/outdated:**
- Constrained decoding frameworks (Guidance, LMQL): Require custom inference; overkill for vocabulary-only constraints
- Verbalized confidence (prompting LLM to output score): Research shows unreliable, high variance
- Synchronous batch generation: Blocks UI; use streaming SSE or async for multi-statement styling

## Open Questions

Things that couldn't be fully resolved:

1. **Optimal Retry Budget**
   - What we know: Research recommends 3-5 retries; OpenAI examples use 6 for rate limits
   - What's unclear: Whether vocabulary validation failures warrant 3 or 5 retries
   - Recommendation: Start with 3 retries (faster feedback); monitor success rate and increase to 5 if <80% success after 3

2. **Composite vs Simple Confidence Score**
   - What we know: Logprobs measure fluency, not semantic/vocabulary correctness
   - What's unclear: Whether weighted composite (logprobs + vocab + semantic) is worth complexity vs simple logprobs
   - Recommendation: Start with logprobs-only (simpler); add composite if Phase 13 testing shows poor correlation with quality

3. **Semantic Similarity Threshold Calibration**
   - What we know: Research shows 0.75-0.85 range typical; no definitive threshold for "equivalence"
   - What's unclear: Optimal threshold for NOC statement styling (different domain from research benchmarks)
   - Recommendation: Start with 0.75 conservative threshold; collect metrics (fallback rate, user acceptance) to tune

4. **Streaming vs Batch Generation UX**
   - What we know: Phase 12 CONTEXT defers streaming/progress UX to Claude's discretion
   - What's unclear: Whether to implement SSE streaming per statement or async batch with polling
   - Recommendation: Start with synchronous single-statement generation; add streaming if user testing shows need

5. **Model Size for Production**
   - What we know: all-MiniLM-L6-v2 is 22MB; loads fast; runs on CPU
   - What's unclear: Whether server deployment needs GPU for faster batch processing
   - Recommendation: CPU-only sufficient for single-statement generation; monitor latency and consider GPU if >2sec per statement

## Sources

### Primary (HIGH confidence)
- [OpenAI Cookbook - Rate Limit Handling](https://github.com/openai/openai-cookbook/blob/main/examples/How_to_handle_rate_limits.ipynb) - Retry patterns with tenacity
- [Tenacity Documentation](https://tenacity.readthedocs.io/) - Retry strategies and decorators
- [Sentence Transformers Documentation](https://www.sbert.net/docs/sentence_transformer/usage/semantic_textual_similarity.html) - Semantic similarity implementation
- Existing codebase: `src/services/llm_service.py`, `src/vocabulary/validator.py`, `src/services/few_shot_examples.py`
- Project requirements.txt: openai==1.109.1, tenacity==9.0.0

### Secondary (MEDIUM confidence)
- [Few-Shot Prompting Guide](https://www.promptingguide.ai/techniques/fewshot) - Best practices for few-shot examples
- [OpenAI Best Practices](https://help.openai.com/en/articles/6654000-best-practices-for-prompt-engineering-with-the-openai-api) - Prompt engineering guidelines
- [Python Retry Logic with Tenacity](https://python.useinstructor.com/concepts/retrying/) - Advanced retry patterns
- [Semantic Similarity Models Comparison](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) - all-MiniLM-L6-v2 specs
- [LLM Confidence Scoring Research](https://www.confident-ai.com/blog/llm-evaluation-metrics-everything-you-need-for-llm-evaluation) - Token logprobs as confidence
- [Graceful Degradation in LLM Apps](https://medium.com/@mota_ai/building-ai-that-never-goes-down-the-graceful-degradation-playbook-d7428dc34ca3) - Fallback patterns

### Tertiary (LOW confidence)
- [Constrained Decoding vs Post-Validation](https://www.aidancooper.co.uk/constrained-decoding/) - Approach comparison (informational only, not used for decisions)
- General semantic similarity threshold practices - No authoritative source; thresholds domain-specific

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All libraries verified (openai, tenacity existing; sentence-transformers from official docs)
- Few-shot prompting: HIGH - OpenAI official guidance + existing few_shot_examples.py structure
- Retry patterns: HIGH - OpenAI Cookbook + tenacity documentation + existing dependency
- Semantic similarity: HIGH - sentence-transformers official docs + Hugging Face model specs
- Confidence scoring: MEDIUM - Research-backed but no single definitive method; logprobs recommended
- Thresholds (vocab, semantic): MEDIUM - Reasonable defaults from research, but domain-specific tuning needed

**Research date:** 2026-02-03
**Valid until:** 14 days (fast-moving LLM domain; library APIs stable but best practices evolve)
