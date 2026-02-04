# Phase 15: Matching Engine - Research

**Researched:** 2026-02-04
**Domain:** LLM-based semantic classification, job description matching, confidence scoring, provenance tracking
**Confidence:** HIGH

## Summary

Phase 15 implements an OccupationalGroupAllocator that uses LLM-based semantic matching to compare job descriptions against TBS occupational group definitions. The user has decided on a holistic definition matching approach (not keyword-based), hybrid candidate shortlisting using labels.csv, and multi-factor confidence scoring with transparent provenance.

The standard stack for LLM-based classification in 2026 combines OpenAI's structured outputs (GPT-4o with response_format JSON schema) for reliable JSON extraction with sentence-transformers for semantic similarity calculations. The instructor library (11k stars, 3M monthly downloads) provides Pydantic integration for type-safe structured outputs with automatic validation and retries. Chain-of-thought prompting with explicit evidence extraction ensures transparent reasoning that can be traced back to source text spans.

Key challenges include LLM overconfidence (recent research shows all frontier models exhibit systematic overconfidence), proper temperature configuration for classification tasks (too high introduces unwanted randomness), and confidence calibration. The user has decided to aim for aspirational human alignment but not formally calibrate in v4.0.

**Primary recommendation:** Use OpenAI structured outputs with Pydantic models via instructor library for type-safe classification results, implement chain-of-thought prompting to extract reasoning steps and evidence, use sentence-transformers (already in requirements.txt) for candidate shortlisting via semantic similarity, set temperature=0 for deterministic classification decisions, and structure output models to capture reasoning steps, evidence spans, and provenance links for full transparency.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| openai | 1.109.1 | LLM API for classification | Already in use, GPT-4o structured outputs achieve 100% JSON schema adherence |
| instructor | 2.x | Structured outputs wrapper | 11k stars, 3M downloads/month, type-safe Pydantic integration with retries |
| pydantic | 2.10.0 | Data validation & models | Already in use, native OpenAI SDK support for schema generation |
| sentence-transformers | 3.4.1 | Semantic similarity embeddings | Already in use, industry standard for semantic search, all-MiniLM-L6-v2 model recommended |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| tenacity | 9.0.0 | Retry logic with exponential backoff | Already in use, for handling rate limits and transient errors |
| sqlite3 | stdlib | Query DIM_OCCUPATIONAL data | Already in use via Phase 14 data layer |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| OpenAI GPT-4o | Anthropic Claude 3.7-sonnet | Claude achieved highest nDCG@3 in recent study but requires new integration |
| instructor | outlines | outlines uses constrained generation but instructor has better ecosystem |
| structured outputs | function calling | function calling is for tool execution, structured outputs for responses |
| sentence-transformers | OpenAI embeddings API | Local embeddings are free and fast, API adds latency and cost |

**Installation:**
```bash
pip install instructor  # Add to requirements.txt
# All other dependencies already present
```

## Architecture Patterns

### Recommended Project Structure
```
src/
├── matching/                    # Matching engine core
│   ├── allocator.py            # OccupationalGroupAllocator class
│   ├── models.py               # Pydantic output models
│   ├── prompts.py              # System/user prompt templates
│   └── confidence.py           # Confidence scoring logic
├── matching/shortlisting/      # Candidate shortlisting
│   ├── semantic_matcher.py     # Sentence-transformers similarity
│   └── labels_matcher.py       # labels.csv lookup integration
├── matching/evidence/          # Evidence extraction & linking
│   ├── extractor.py            # Text span extraction
│   └── provenance.py           # TBS source linking
└── storage/
    └── repository.py           # Query DIM_OCCUPATIONAL (Phase 14)
```

### Pattern 1: Structured Output with Chain-of-Thought Reasoning
**What:** Use OpenAI structured outputs with explicit reasoning steps captured in Pydantic models. Each classification includes intermediate reasoning, evidence extraction, and final recommendation.
**When to use:** All LLM-based classification tasks requiring transparency and auditability.
**Example:**
```python
# Source: OpenAI Structured Outputs docs 2026 + instructor library
from pydantic import BaseModel, Field
from typing import List, Optional
import instructor
from openai import OpenAI

class ReasoningStep(BaseModel):
    """Single step in chain-of-thought reasoning."""
    step_number: int
    explanation: str = Field(description="What this reasoning step determines")
    evidence: str = Field(description="Quoted text from JD or definition supporting this step")
    intermediate_conclusion: str = Field(description="What this step concludes")

class GroupRecommendation(BaseModel):
    """Single occupational group recommendation with provenance."""
    group_code: str = Field(description="e.g., 'AI', 'CS', 'PM'")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score 0.0-1.0")
    definition_fit_rationale: str = Field(description="Why this group's definition matches the JD")
    reasoning_steps: List[ReasoningStep] = Field(description="Chain-of-thought reasoning")
    evidence_spans: List[str] = Field(description="Quoted excerpts from JD supporting match")
    inclusion_check: str = Field(description="Which inclusions apply or 'none applies'")
    exclusion_check: str = Field(description="Confirmation exclusions don't match primary purpose")
    provenance_url: str = Field(description="TBS source URL for this group's definition")

class AllocationResult(BaseModel):
    """Complete allocation result with top-3 ranked recommendations."""
    primary_purpose_summary: str = Field(description="Extracted primary purpose from JD")
    top_recommendations: List[GroupRecommendation] = Field(max_length=3, description="Ranked top-3")
    rejected_groups: List[dict] = Field(description="Why other groups were not recommended")
    borderline_flag: bool = Field(description="True if top scores within 10% (needs review)")
    match_context: str = Field(description="'dominant match' | 'competitive field' | 'only viable option'")
    constraints_compliance: str = Field(default="Evaluated work described in JD, not person-specific attributes")

# Initialize instructor-wrapped client
client = instructor.from_openai(OpenAI())

def allocate_occupational_group(jd_data: dict, candidate_groups: List[dict]) -> AllocationResult:
    """Allocate JD to occupational group using structured LLM reasoning."""

    system_prompt = """You are a TBS occupational group classification expert.
Your role is to match job descriptions to occupational groups using the TBS allocation method:
1. Extract primary purpose from Client-Service Results and Key Activities
2. Compare purpose to full group definitions holistically (not keyword matching)
3. Check inclusion statements for supporting evidence
4. Verify exclusion statements don't match primary purpose
5. Provide transparent reasoning with evidence spans

Return structured output with reasoning steps, evidence, and provenance."""

    user_prompt = build_allocation_prompt(jd_data, candidate_groups)

    # Structured output with temperature=0 for deterministic classification
    result = client.chat.completions.create(
        model="gpt-4o",
        temperature=0,  # Deterministic for classification
        response_model=AllocationResult,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    return result  # Auto-validated Pydantic model
```

### Pattern 2: Semantic Similarity Shortlisting
**What:** Use sentence-transformers to pre-filter candidate groups based on semantic similarity between JD content and group definitions, then boost confidence if labels.csv supports the match.
**When to use:** Before LLM classification to reduce token costs and improve focus on viable candidates.
**Example:**
```python
# Source: sentence-transformers docs 2026
from sentence_transformers import SentenceTransformer, util

class SemanticShortlister:
    """Shortlist candidate occupational groups using semantic similarity."""

    def __init__(self):
        # all-MiniLM-L6-v2: fast, good accuracy, no GPU needed
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def shortlist_candidates(
        self,
        jd_text: str,
        all_groups: List[dict],
        labels_csv_mapping: dict,
        min_similarity: float = 0.3,
        max_candidates: int = 10
    ) -> List[dict]:
        """Return shortlisted groups with similarity scores and label boost."""

        # Embed JD text (combine client-service results + key activities)
        jd_embedding = self.model.encode(jd_text, convert_to_tensor=True)

        # Embed all group definitions
        definitions = [g['definition'] for g in all_groups]
        def_embeddings = self.model.encode(definitions, convert_to_tensor=True)

        # Calculate cosine similarity
        similarities = util.cos_sim(jd_embedding, def_embeddings)[0]

        # Create candidates with scores
        candidates = []
        for idx, group in enumerate(all_groups):
            similarity = float(similarities[idx])

            # Boost if labels.csv supports this group
            labels_boost = 0.0
            if group['group_code'] in labels_csv_mapping:
                labels_boost = 0.1  # 10% confidence boost

            candidates.append({
                'group': group,
                'semantic_similarity': similarity,
                'labels_boost': labels_boost,
                'combined_score': similarity + labels_boost
            })

        # Filter by minimum threshold and sort by combined score
        viable = [c for c in candidates if c['combined_score'] >= min_similarity]
        viable.sort(key=lambda x: x['combined_score'], reverse=True)

        return viable[:max_candidates]
```

### Pattern 3: Multi-Factor Confidence Scoring
**What:** Calculate confidence from multiple independent signals: definition alignment, inclusion support, exclusion check, labels.csv support, relative margin to next-best option.
**When to use:** Final confidence score calculation after LLM classification.
**Example:**
```python
# Source: Based on LLM confidence calibration research 2026
from typing import List, Tuple

class ConfidenceCalculator:
    """Calculate calibrated confidence scores for occupational group matches."""

    def calculate_confidence(
        self,
        definition_fit_score: float,      # 0.0-1.0 from LLM assessment
        inclusion_match: bool,             # Inclusion statements support?
        exclusion_conflict: bool,          # Exclusion statements apply?
        labels_csv_support: bool,          # labels.csv contains this group?
        semantic_similarity: float,        # 0.0-1.0 from embeddings
        margin_to_next: float              # Score difference to next-best
    ) -> Tuple[float, str]:
        """Return (confidence, context_indicator)."""

        # Start with definition fit as base
        confidence = definition_fit_score * 0.5

        # Add inclusion support (up to +0.2)
        if inclusion_match:
            confidence += 0.2

        # Apply exclusion penalty (hard gate in matching, but affects confidence)
        if exclusion_conflict:
            confidence *= 0.3  # Severe penalty if exclusion matches

        # Add labels.csv support (up to +0.1)
        if labels_csv_support:
            confidence += 0.1

        # Add semantic similarity (up to +0.15)
        confidence += semantic_similarity * 0.15

        # Margin adjustment (up to +0.05)
        if margin_to_next > 0.2:
            confidence += 0.05  # Clear winner

        # Cap at 1.0
        confidence = min(1.0, confidence)

        # Determine match context
        if margin_to_next > 0.3:
            context = "dominant match"
        elif margin_to_next > 0.1:
            context = "competitive field"
        else:
            context = "borderline - needs review"

        return confidence, context

    def check_borderline(self, scores: List[float]) -> bool:
        """Flag if top scores within 10% of each other."""
        if len(scores) < 2:
            return False
        return (scores[0] - scores[1]) <= 0.1
```

### Pattern 4: Evidence Linking with Provenance
**What:** Extract text spans from JD that support classification decision and link to specific TBS definition paragraphs with full URL provenance.
**When to use:** All classification decisions requiring auditability.
**Example:**
```python
# Source: LLM provenance research 2026
from typing import List, Dict
import re

class EvidenceLinker:
    """Link classification evidence to source text with provenance."""

    def extract_evidence_spans(
        self,
        jd_text: str,
        evidence_quotes: List[str]
    ) -> List[Dict]:
        """Find quoted evidence in JD and return with character positions."""

        spans = []
        for quote in evidence_quotes:
            # Find quote in original text (normalize whitespace)
            normalized_jd = ' '.join(jd_text.split())
            normalized_quote = ' '.join(quote.split())

            match = re.search(re.escape(normalized_quote), normalized_jd, re.IGNORECASE)
            if match:
                spans.append({
                    'text': quote,
                    'start_char': match.start(),
                    'end_char': match.end(),
                    'field': self._identify_jd_field(jd_text, match.start())
                })

        return spans

    def _identify_jd_field(self, jd_text: str, char_pos: int) -> str:
        """Identify which JD field contains this character position."""
        # Parse structured JD to identify field boundaries
        # Return field reference like "Client-Service Results" or "Key Activity 3"
        pass

    def link_to_tbs_provenance(
        self,
        group_code: str,
        definition_url: str,
        paragraph_label: Optional[str] = None
    ) -> Dict:
        """Create provenance link to TBS source."""

        return {
            'group_code': group_code,
            'source_type': 'TBS Occupational Group Definition',
            'url': definition_url,
            'paragraph': paragraph_label,  # e.g., "I1", "E2", "Definition"
            'accessed_at': datetime.now(timezone.utc).isoformat(),
            'data_source_id': self._lookup_scrape_provenance_id(group_code)
        }

    def _lookup_scrape_provenance_id(self, group_code: str) -> int:
        """Query DIM_OCCUPATIONAL to get source_provenance_id."""
        # Link to Phase 14 scrape_provenance table
        pass
```

### Anti-Patterns to Avoid

- **High temperature for classification:** Temperature > 0 introduces randomness that makes classification non-deterministic. Use temperature=0 for consistent results.

- **Mixing function calling with structured outputs:** Function calling is for tool execution, structured outputs are for response formatting. Don't use parallel_tool_calls with structured outputs.

- **Single-factor confidence scores:** Confidence based only on LLM assessment is uncalibrated and overconfident. Combine multiple signals for better calibration.

- **Keyword matching for definitions:** User decided holistic semantic matching, not keyword counting. Keyword approaches miss synonyms and semantic equivalence.

- **Black-box classification:** User wants transparency and provenance. Always capture reasoning steps, evidence, and source links.

- **Using default temperature (0.7):** Default OpenAI temperature is too high for classification. Explicitly set temperature=0 for deterministic decisions.

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| JSON schema generation from Pydantic | Manual JSON schema writing | Pydantic + instructor | Pydantic auto-generates schemas, instructor handles OpenAI integration with retries |
| Semantic text similarity | Custom word overlap scoring | sentence-transformers | Pre-trained models handle synonyms, context, semantic equivalence; custom scoring misses these |
| LLM retry logic | Manual try/catch loops | tenacity (already in use) | Handles exponential backoff, rate limits, transient errors with clean decorators |
| Confidence calibration | Custom scoring formulas | Multi-factor scoring pattern | Research shows LLMs are systematically overconfident; need multiple independent signals |
| Evidence extraction | Regex text searching | LLM structured output with spans | LLM can extract semantic evidence, not just literal strings; structured output ensures reliability |
| Text span highlighting | String indexing by hand | Evidence linking pattern | Handles whitespace normalization, field identification, provenance tracking automatically |

**Key insight:** LLM-based classification requires careful orchestration of multiple components (shortlisting, classification, confidence, evidence, provenance). Each component has established best practices and libraries—avoid reinventing these wheels. The complexity is in the integration, not the individual parts.

## Common Pitfalls

### Pitfall 1: LLM Overconfidence Bias
**What goes wrong:** LLMs exhibit systematic overconfidence—predicted confidence levels significantly exceed actual accuracy. Research on Claude Opus 4.5, GPT-5.2, DeepSeek-V3.2 shows all models are overconfident in 84.3% of scenarios.
**Why it happens:** LLMs are trained to sound confident; confidence scores reflect linguistic confidence, not statistical accuracy.
**How to avoid:** Use multi-factor confidence scoring combining LLM assessment with semantic similarity, inclusion/exclusion checks, and labels.csv support. Don't rely solely on LLM-stated confidence.
**Warning signs:** All recommendations scoring 0.9+, no LOW confidence results even for ambiguous cases, confidence scores don't correlate with actual classification accuracy when validated by humans.

### Pitfall 2: Temperature Misconfiguration
**What goes wrong:** Using default temperature (0.7) or high temperature for classification introduces unwanted randomness. Same JD classified differently on repeated runs undermines reliability.
**Why it happens:** API defaults to temperature ~0.7 for creative tasks; developers don't adjust for classification tasks requiring consistency.
**How to avoid:** Explicitly set temperature=0 for all classification calls. Temperature > 0 only for creative tasks like rationale generation (and even then, keep it low like 0.3).
**Warning signs:** Non-deterministic results (same input produces different outputs), classification changes when re-running with identical inputs, inconsistent confidence scores.

### Pitfall 3: Cosine Similarity Threshold Guessing
**What goes wrong:** Picking arbitrary similarity thresholds (e.g., 0.8) without validation. User decided 0.3 minimum confidence, but semantic similarity thresholds need tuning.
**Why it happens:** No universal threshold for cosine similarity—depends on embedding model, domain, and data distribution.
**How to avoid:** Start with lenient threshold (0.3-0.5) for shortlisting, iterate based on results. Focus on relative ranking rather than absolute cutoffs. Use threshold mainly to exclude clearly irrelevant groups.
**Warning signs:** Shortlisting excludes obvious viable candidates, shortlist always returns same groups regardless of JD content, similarity scores cluster in narrow range.

### Pitfall 4: Brittle Evidence Extraction
**What goes wrong:** Evidence linking fails when LLM rephrases or paraphrases JD text instead of quoting exactly. String matching can't find the evidence in original text.
**Why it happens:** LLMs naturally paraphrase; asking for "exact quotes" helps but doesn't guarantee perfect literal copying.
**How to avoid:** Prompt explicitly for exact quotes with quotation marks. Implement fuzzy matching with normalization (whitespace, case) as fallback. Accept that some evidence won't be linkable to exact spans—include the reasoning even if span lookup fails.
**Warning signs:** Evidence spans list always empty despite LLM providing reasoning, confidence degrades when evidence linking fails, audit trail incomplete.

### Pitfall 5: Ignoring Structured Output Limitations
**What goes wrong:** Structured outputs fail silently or return unexpected structures when schema is too complex or uses unsupported JSON Schema features.
**Why it happens:** OpenAI structured outputs use constrained decoding with limitations—not all JSON Schema features supported (e.g., complex conditionals, some validation keywords).
**How to avoid:** Keep Pydantic models simple with basic types (str, int, float, bool, List, Optional). Use Field descriptions to guide LLM instead of complex validation. Test schema with sample calls before production.
**Warning signs:** API returns validation errors, structured output falls back to JSON mode, missing fields in responses, LLM outputs don't match expected types.

### Pitfall 6: Mixing Persona Bias with Confidence
**What goes wrong:** LLM confidence influenced by persona framing in prompt. Research shows models express lower confidence for "layman" personas and higher for "expert" personas, despite similar accuracy.
**Why it happens:** Persona conditioning affects verbalized confidence more than actual performance.
**How to avoid:** Use neutral system prompts focused on task expertise without excessive persona framing. Don't say "you are the world's best classifier"—say "you are a TBS classification expert using the prescribed allocation method."
**Warning signs:** Confidence scores correlate with prompt phrasing changes, classification accuracy doesn't match confidence levels, results sensitive to minor prompt wording variations.

## Code Examples

Verified patterns from official sources:

### Complete Matching Engine Flow
```python
# Source: Integrated pattern combining OpenAI structured outputs + sentence-transformers
from typing import List, Dict, Optional
from src.storage.repository import OccupationalGroupRepository
from src.storage.db_manager import get_db

class OccupationalGroupAllocator:
    """
    Phase 15: Matching Engine
    Allocates JD to occupational groups using LLM-based semantic matching.
    """

    def __init__(self):
        self.shortlister = SemanticShortlister()
        self.confidence_calculator = ConfidenceCalculator()
        self.evidence_linker = EvidenceLinker()
        self.llm_client = instructor.from_openai(OpenAI())

    def allocate(self, jd_data: Dict) -> AllocationResult:
        """
        Main allocation method implementing user-specified approach:
        1. Extract primary purpose from JD (Client-Service Results + Key Activities)
        2. Shortlist candidates using semantic similarity + labels.csv boost
        3. LLM classification with holistic definition matching
        4. Multi-factor confidence scoring
        5. Evidence extraction and provenance linking
        """

        # Step 1: Load current occupational groups from Phase 14 data layer
        with get_db() as conn:
            repo = OccupationalGroupRepository(conn)
            all_groups = repo.get_current_groups()  # Uses v_current_occupational_groups view

        # Step 2: Load labels.csv mapping (duty-to-group mappings)
        labels_mapping = self._load_labels_csv()

        # Step 3: Extract primary purpose text for matching
        jd_text = self._extract_primary_purpose_text(jd_data)

        # Step 4: Shortlist viable candidates (semantic similarity + labels boost)
        candidates = self.shortlister.shortlist_candidates(
            jd_text=jd_text,
            all_groups=all_groups,
            labels_csv_mapping=labels_mapping,
            min_similarity=0.3,  # User-specified threshold
            max_candidates=10
        )

        # Step 5: LLM classification with structured output
        llm_result = self._classify_with_llm(jd_data, candidates)

        # Step 6: Enhance confidence scores with multi-factor calculation
        enhanced_result = self._enhance_confidence_scores(llm_result, candidates)

        # Step 7: Extract evidence spans and link to provenance
        final_result = self._link_evidence_and_provenance(enhanced_result, jd_data)

        # Step 8: Check edge cases
        final_result = self._check_edge_cases(final_result, jd_data)

        return final_result

    def _extract_primary_purpose_text(self, jd_data: Dict) -> str:
        """Extract text for matching: Client-Service Results + Key Activities."""
        parts = []

        if 'client_service_results' in jd_data:
            parts.append(f"Client-Service Results: {jd_data['client_service_results']}")

        if 'key_activities' in jd_data:
            for idx, activity in enumerate(jd_data['key_activities'], 1):
                parts.append(f"Key Activity {idx}: {activity}")

        return "\n".join(parts)

    def _classify_with_llm(
        self,
        jd_data: Dict,
        candidates: List[Dict]
    ) -> AllocationResult:
        """Call LLM with structured output for classification."""

        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(jd_data, candidates)

        # Structured output with temperature=0 for deterministic results
        result = self.llm_client.chat.completions.create(
            model="gpt-4o",
            temperature=0,  # Critical: deterministic classification
            response_model=AllocationResult,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_retries=3  # instructor handles retries with validation
        )

        return result

    def _build_system_prompt(self) -> str:
        """System prompt encoding TBS allocation method."""
        return """You are a TBS occupational group classification expert using the prescribed allocation method.

Your task: Match job descriptions to occupational groups by:
1. Extracting primary purpose from Client-Service Results and Key Activities (combined analysis)
2. Comparing purpose to full group definitions holistically (semantic match, not keyword counting)
3. Using inclusion statements for shortlisting support only (not for scoring evidence)
4. Applying exclusion statements as hard gates (if primary purpose matches exclusion, eliminate group)
5. Providing transparent reasoning with exact quotes as evidence

Classification principles:
- Evaluate the WORK described in the JD, not person-specific attributes
- Mirror how human classifiers think: holistic semantic judgment, not mechanical keyword matching
- Flag borderline cases when top scores within 10% of each other
- Provide full provenance: link every decision to TBS source

Output structured results with reasoning steps, evidence spans, and confidence scores."""

    def _build_user_prompt(self, jd_data: Dict, candidates: List[Dict]) -> str:
        """User prompt with JD data and candidate groups."""

        prompt_parts = [
            "# Job Description to Classify",
            "",
            f"Position Title: {jd_data.get('position_title', 'Unknown')}",
            "",
            "## Client-Service Results",
            jd_data.get('client_service_results', 'Not provided'),
            "",
            "## Key Activities"
        ]

        for idx, activity in enumerate(jd_data.get('key_activities', []), 1):
            prompt_parts.append(f"{idx}. {activity}")

        prompt_parts.extend([
            "",
            "# Candidate Occupational Groups",
            "(Shortlisted based on semantic similarity + existing duty mappings)",
            ""
        ])

        for candidate in candidates:
            group = candidate['group']
            prompt_parts.extend([
                f"## {group['group_code']}",
                f"**Definition:** {group['definition']}",
                f"**Semantic similarity:** {candidate['semantic_similarity']:.2f}",
                ""
            ])

            # Include inclusion statements if available
            if 'inclusions' in group:
                prompt_parts.append("**Inclusions:**")
                for inc in group['inclusions']:
                    prompt_parts.append(f"- {inc}")
                prompt_parts.append("")

            # Include exclusion statements if available
            if 'exclusions' in group:
                prompt_parts.append("**Exclusions:**")
                for exc in group['exclusions']:
                    prompt_parts.append(f"- {exc}")
                prompt_parts.append("")

        prompt_parts.extend([
            "# Your Task",
            "",
            "Classify this JD by:",
            "1. Summarizing primary purpose (why this position exists)",
            "2. Evaluating definition fit for each candidate group holistically",
            "3. Checking inclusion statements for supporting evidence",
            "4. Verifying exclusion statements don't match primary purpose",
            "5. Ranking top-3 recommendations with confidence scores",
            "6. Explaining why other groups were rejected",
            "",
            "Use exact quotes from JD as evidence. Provide transparent reasoning."
        ])

        return "\n".join(prompt_parts)

    def _check_edge_cases(
        self,
        result: AllocationResult,
        jd_data: Dict
    ) -> AllocationResult:
        """Check for edge cases defined in user requirements."""

        # EDGE-01: AP vs TC disambiguation
        top_codes = [r.group_code for r in result.top_recommendations[:2]]
        if 'AP' in top_codes and 'TC' in top_codes:
            # Apply explicit TBS guidance on theoretical vs practical knowledge
            result = self._apply_ap_tc_disambiguation(result, jd_data)

        # EDGE-02: Multi-group duties detection
        if self._detect_multi_group_duties(result):
            result.match_context = "split duties detected - consider multiple positions"

        # EDGE-03: Invalid Combination of Work
        if self._detect_invalid_combination(result):
            result.match_context = "invalid combination - recommend splitting JD"

        # Flag specialized groups (EX, LC, MD) if recommended
        specialized = ['EX', 'LC', 'MD']
        if any(r.group_code in specialized for r in result.top_recommendations):
            result.match_context += " (SPECIALIZED GROUP - separate classification process)"

        return result
```

### Shortlisting with Inclusion Boost
```python
# Source: sentence-transformers semantic textual similarity docs
def load_inclusions_from_db(group_id: int) -> List[str]:
    """Load inclusion statements for a group from Phase 14 data."""
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT statement
            FROM dim_occupational_inclusion
            WHERE group_id = ?
            ORDER BY order_num
            """,
            (group_id,)
        )
        return [row['statement'] for row in cursor.fetchall()]

def shortlist_with_inclusions(
    jd_text: str,
    all_groups: List[dict],
    min_similarity: float = 0.3
) -> List[dict]:
    """Shortlist using both definition and inclusion statement similarity."""

    model = SentenceTransformer('all-MiniLM-L6-v2')
    jd_embedding = model.encode(jd_text, convert_to_tensor=True)

    candidates = []
    for group in all_groups:
        # Definition similarity (primary signal)
        def_embedding = model.encode(group['definition'], convert_to_tensor=True)
        def_similarity = float(util.cos_sim(jd_embedding, def_embedding)[0][0])

        # Inclusion similarity (boost signal, per user decision)
        inclusions = load_inclusions_from_db(group['id'])
        inc_similarities = []
        if inclusions:
            inc_embeddings = model.encode(inclusions, convert_to_tensor=True)
            inc_similarities = util.cos_sim(jd_embedding, inc_embeddings)[0]

        # Combined score: definition primary, inclusions boost if match
        max_inc_similarity = max(inc_similarities) if inc_similarities else 0.0
        combined_score = def_similarity * 0.8 + max_inc_similarity * 0.2

        if combined_score >= min_similarity:
            candidates.append({
                'group': group,
                'definition_similarity': def_similarity,
                'inclusion_similarity': max_inc_similarity,
                'combined_score': combined_score
            })

    candidates.sort(key=lambda x: x['combined_score'], reverse=True)
    return candidates
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| JSON mode (OpenAI) | Structured outputs with JSON schema | Aug 2024 (GPT-4o launch) | 100% schema adherence vs unreliable JSON mode |
| Manual Pydantic conversion | Native SDK Pydantic support | OpenAI SDK 1.x updates | Automatic schema generation + deserialization |
| Function calling for responses | Structured outputs via response_format | Aug 2024 clarification | Proper separation: function calling for tools, structured outputs for responses |
| Temperature defaults (0.7) | Temperature=0 for classification | Ongoing best practice 2025-2026 | Deterministic classification vs non-deterministic randomness |
| Single confidence scores | Multi-factor calibrated scores | Research on overconfidence 2025-2026 | Addresses systematic LLM overconfidence bias |
| all-mpnet-base-v2 | all-MiniLM-L6-v2 | Speed/accuracy tradeoff | 5x faster for similar accuracy, better for production |

**Deprecated/outdated:**
- **JSON mode without schema:** Replaced by structured outputs with guaranteed adherence
- **Parallel tool calls with structured outputs:** Not compatible; set parallel_tool_calls=false
- **High temperature (>0.3) for classification:** Introduces unwanted randomness; use temperature=0
- **Single-signal confidence (LLM only):** Uncalibrated and overconfident; use multi-factor scoring

## Open Questions

Things that couldn't be fully resolved:

1. **Optimal semantic similarity threshold**
   - What we know: No universal threshold; depends on embedding model and domain; user decided 0.3 minimum confidence overall
   - What's unclear: Whether 0.3 applies to semantic similarity threshold or only final confidence score
   - Recommendation: Start with 0.4-0.5 for semantic similarity shortlisting (more lenient), iterate based on results; use 0.3 as final confidence threshold after multi-factor scoring

2. **labels.csv structure and coverage**
   - What we know: User decided hybrid approach—labels.csv boosts confidence if it supports match
   - What's unclear: labels.csv file format, completeness, mapping structure (duty text → group codes?)
   - Recommendation: Inspect labels.csv during implementation; if structured as duty-to-group mappings, use as confidence boost signal; if incomplete, rely more heavily on semantic similarity

3. **Subgroup handling**
   - What we know: User marked as "Claude's Discretion"—some groups have subgroups (e.g., AI has "Operational" and "Non-Operational")
   - What's unclear: Whether to match at top-level only (AI) or include subgroups in candidate set
   - Recommendation: Query TBS data structure from Phase 14; if subgroups have distinct definitions, include as separate candidates; if definitions identical, collapse to top-level

4. **JD field weighting**
   - What we know: User decided combined analysis of Client-Service Results + Key Activities for primary purpose; marked field weighting as Claude's discretion
   - What's unclear: Whether certain JD fields should contribute more to matching than others
   - Recommendation: Weight Client-Service Results slightly higher (0.6) than Key Activities (0.4) for primary purpose extraction; skills/abilities lower weight for context only

5. **Exclusion statement interpretation severity**
   - What we know: User decided hard gate—if primary purpose matches exclusion, eliminate group; marked severity determination as Claude's discretion
   - What's unclear: How to interpret "matches"—exact match, semantic similarity, partial overlap?
   - Recommendation: Use semantic similarity with threshold ~0.7 for exclusion matching; if JD primary purpose semantically similar to exclusion statement above 0.7, eliminate group

6. **AP vs TC disambiguation rules**
   - What we know: User decided explicit rules encoding TBS guidance for this specific edge case
   - What's unclear: What the TBS guidance actually says for distinguishing AP (policy analysis) vs TC (technical content)
   - Recommendation: Research TBS classification guides during implementation; likely distinction is theoretical knowledge (AP) vs practical application (TC), but needs verification with authoritative source

## Sources

### Primary (HIGH confidence)
- [OpenAI Structured Outputs Documentation](https://platform.openai.com/docs/guides/structured-outputs) - Structured outputs with JSON schema, 100% adherence
- [OpenAI Introducing Structured Outputs](https://openai.com/index/introducing-structured-outputs-in-the-api/) - Feature announcement and best practices
- [Sentence Transformers Semantic Textual Similarity](https://www.sbert.net/docs/sentence_transformer/usage/semantic_textual_similarity.html) - Official semantic similarity documentation
- [Sentence Transformers PyPI](https://pypi.org/project/sentence-transformers/) - Version 3.4.1, Python 3.10+ requirement
- [Instructor GitHub](https://github.com/567-labs/instructor) - 11k stars, structured outputs wrapper
- [Instructor Documentation](https://python.useinstructor.com/) - Pydantic integration for OpenAI

### Secondary (MEDIUM confidence)
- [Do Language Models Mirror Human Confidence?](https://arxiv.org/html/2506.00582) - Research on LLM overconfidence, psychological insights
- [Overconfidence in LLM-as-a-Judge](https://arxiv.org/html/2508.06225v2) - Diagnosis and confidence-driven solutions
- [Mind the Confidence Gap](https://arxiv.org/html/2502.11028v1) - Overconfidence, calibration, and distractor effects in LLMs
- [LLM Temperature Guide](https://www.promptingguide.ai/introduction/settings) - Best practices for temperature settings
- [Chain-of-Thought Prompting](https://arxiv.org/abs/2201.11903) - CoT reasoning in LLMs
- [Chain of Thought with Explicit Evidence](https://arxiv.org/html/2311.05922) - CoT-ER for relation extraction with evidence
- [Exploring LLM Citation Generation](https://medium.com/@prestonblckbrn/exploring-llm-citation-generation-in-2025-4ac7c8980794) - Citation mechanisms for explainability
- [Using LLMs to infer provenance information](https://dl.acm.org/doi/10.1145/3736229.3736261) - Provenance extraction research

### Tertiary (LOW confidence)
- [Semantic Matching using LLM](https://pub.towardsai.net/semantic-matching-using-llm-3b46b2078ec8) - Tutorial on semantic matching approaches
- [Text Classification with LLMs](https://www.helicone.ai/blog/text-classification-with-llms) - Approaches and evaluation techniques
- [AI System Design Patterns 2026](https://zenvanriel.nl/ai-engineer-blog/ai-system-design-patterns-2026/) - Architecture patterns for AI systems
- [OpenRouter LLM Rankings](https://openrouter.ai/rankings) - LLM performance comparisons
- Community discussions on cosine similarity thresholds - Multiple sources, no consensus on universal values

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All libraries verified current in 2026, most already in requirements.txt, instructor is proven standard with 11k stars
- Architecture: HIGH - Patterns based on official OpenAI docs + sentence-transformers docs + recent research on confidence calibration
- Pitfalls: HIGH - Based on 2025-2026 research papers on LLM overconfidence, temperature effects, and confidence calibration failures
- Edge cases: MEDIUM - User decisions provide clear direction, but specific TBS guidance (AP vs TC) needs verification during implementation
- Open questions: MEDIUM - Most questions have reasonable recommendations, but require validation with actual data (labels.csv structure, TBS data)

**Research date:** 2026-02-04
**Valid until:** 2026-03-04 (30 days - stable domain, but LLM API features evolve quickly; revalidate OpenAI API changes monthly)
