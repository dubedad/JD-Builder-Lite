"""Generation service for constrained style transfer with vocabulary validation.

This module implements the core generation mechanics for transforming NOC statements
into styled variants using few-shot prompting with post-validation. Follows the
generation lifecycle: construct prompt -> call GPT-4o -> validate vocabulary ->
retry if validation fails -> fall back to original on exhaustion -> track provenance.

Key components:
- GenerationService: Main orchestrator for styled statement generation
- VocabularyValidationError: Raised when vocabulary coverage fails threshold
- SemanticEquivalenceError: Raised when semantic similarity fails threshold

Used by: Phase 12 generation endpoints (to be implemented in 12-02)
"""

import logging
import math
import os
from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

import openai
from openai import OpenAI
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
    retry_if_exception_type,
    RetryError,
)

from src.config import OPENAI_API_KEY
from src.models.ai import StyleContentType
from src.models.styled_content import StyledStatement
from src.models.vocabulary_audit import VocabularyAudit, VocabularyTerm
from src.services.few_shot_examples import get_high_quality_examples
from src.services.semantic_checker import check_semantic_equivalence
from src.services.style_constants import STYLE_RULES
from src.vocabulary.index import VocabularyIndex
from src.vocabulary.validator import VocabularyValidator


# Configuration constants
MAX_RETRIES = 3  # Per RESEARCH.md: 3-5 retries typical, start with 3
VOCABULARY_COVERAGE_THRESHOLD = 95.0  # 95% NOC words required
STYLE_PROMPT_VERSION = "v1.0"  # For provenance tracking

# Logger for this module
logger = logging.getLogger(__name__)


class VocabularyValidationError(Exception):
    """Raised when generated text fails vocabulary coverage validation.

    This exception triggers tenacity retry since vocabulary compliance can
    sometimes succeed on regeneration with a different LLM output.
    """

    pass


class SemanticEquivalenceError(Exception):
    """Raised when styled text doesn't preserve original meaning.

    This exception indicates the styled variant has drifted too far from
    the original NOC statement's meaning.
    """

    pass


class GenerationService:
    """Service for constrained generation with vocabulary validation.

    Handles full generation lifecycle:
    1. Few-shot prompt construction per section patterns
    2. GPT-4o generation with tenacity retry
    3. Vocabulary post-validation against NOC vocabulary
    4. Semantic equivalence checking with sentence embeddings
    5. Confidence score calculation from token log probabilities
    6. Graceful degradation to original NOC on failure

    Attributes:
        vocab_index: VocabularyIndex for term lookup
        validator: VocabularyValidator for coverage calculation
        client: OpenAI API client
    """

    def __init__(self, vocab_index: VocabularyIndex) -> None:
        """Initialize generation service.

        Args:
            vocab_index: Loaded VocabularyIndex for validation
        """
        self.vocab_index = vocab_index
        self.validator = VocabularyValidator(vocab_index)
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self._logger = logging.getLogger(__name__)

    def build_few_shot_prompt(
        self, section: str, noc_statement: str, n_examples: int = 5
    ) -> tuple[str, str]:
        """Build system and user prompts for styled generation.

        Constructs prompts following RESEARCH.md Pattern 1: few-shot with
        clear delimiters and purpose clauses. Uses high-quality examples
        from the curated corpus.

        Args:
            section: JD element (key_activities, skills, effort, working_conditions)
            noc_statement: Original NOC statement to style
            n_examples: Number of examples (default 5, per research diminishing returns beyond 5)

        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        # Get style rule for section
        style_rule = STYLE_RULES.get(section, {})
        sentence_structure = style_rule.get("sentence_structure", "")
        perspective = style_rule.get("perspective", "")

        # Get high-quality examples (quality_weight >= 0.85)
        examples = get_high_quality_examples(section, min_weight=0.85)[:n_examples]

        # Build system prompt per RESEARCH.md Pattern 1
        system_prompt = f"""You are a Canadian federal job description stylist. Transform concise NOC statements into detailed, professional job description statements.

Guidelines:
- Follow the {sentence_structure} pattern
- {perspective}
- Use ONLY words from the NOC vocabulary (no invented terms)
- Preserve the original meaning exactly (semantic equivalence required)
- Expand abbreviations and add context for clarity
- Write in professional, formal government style
- Output a single complete sentence"""

        # Build user prompt with few-shot examples
        example_parts: List[str] = []
        for ex in examples:
            example_parts.append(f"NOC Input: {ex['noc_input']}")
            example_parts.append(f"Styled Output: {ex['styled_output']}")
            example_parts.append("")

        example_text = "\n".join(example_parts)

        user_prompt = f"""Here are examples of the {section} styling pattern:

{example_text}
Now style this NOC statement using the same pattern:
NOC Input: {noc_statement}
Styled Output:"""

        return system_prompt, user_prompt

    def _create_vocabulary_audit(
        self, validation_result: Dict, styled_text: str
    ) -> VocabularyAudit:
        """Convert validation result to VocabularyAudit model.

        Args:
            validation_result: Result from VocabularyValidator.validate_text()
            styled_text: The styled text that was validated

        Returns:
            VocabularyAudit model with full audit data
        """
        # Note: VocabularyValidator doesn't return term categories,
        # so we use "unknown" for category field as per task spec
        noc_terms_used: List[VocabularyTerm] = []

        # The validator doesn't return the actual NOC terms found,
        # only non-NOC terms. We need to derive NOC terms from the coverage.
        # For now, create placeholder terms based on noc_words count.
        # In a more complete implementation, we'd track which words matched.
        noc_word_count = validation_result.get("noc_words", 0)
        total_words = validation_result.get("total_words", 0)

        # We don't have individual NOC terms from validator, but we have the count
        # The audit model expects a list, so we note this limitation

        return VocabularyAudit(
            noc_terms_used=noc_terms_used,  # Empty list - validator doesn't return matched terms
            non_noc_terms=validation_result.get("non_noc_words", []),
            coverage_percentage=validation_result.get("coverage_percentage", 0.0),
            total_content_words=total_words,
            noc_word_count=noc_word_count,
        )

    def _calculate_confidence(self, logprobs_data) -> float:
        """Calculate confidence score from OpenAI logprobs.

        Uses mean token probability as confidence indicator per RESEARCH.md
        Pattern 4. Token probability measures fluency/certainty of generation.

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

    @retry(
        wait=wait_random_exponential(min=1, max=10),
        stop=stop_after_attempt(MAX_RETRIES),
        retry=retry_if_exception_type(
            (VocabularyValidationError, openai.RateLimitError, openai.APITimeoutError)
        ),
    )
    def _generate_with_validation(self, section: str, noc_statement: str) -> Dict:
        """Generate styled statement with vocabulary validation and retry.

        This method has tenacity retry decorator that automatically retries
        on VocabularyValidationError, RateLimitError, and APITimeoutError.

        Args:
            section: JD element section
            noc_statement: Original NOC statement to style

        Returns:
            Dict with styled_text, validation_result, logprobs

        Raises:
            VocabularyValidationError: When coverage < threshold (triggers retry)
            openai.RateLimitError: Rate limit hit (triggers retry)
            openai.APITimeoutError: Request timeout (triggers retry)
        """
        system_prompt, user_prompt = self.build_few_shot_prompt(section, noc_statement)

        # Call GPT-4o with logprobs enabled for confidence calculation
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,  # Lower than overview (0.7) - less creativity needed
            max_tokens=200,
            logprobs=True,  # Enable for confidence calculation
            top_logprobs=1,
        )

        styled_text = response.choices[0].message.content.strip()

        # Validate vocabulary coverage
        validation = self.validator.validate_text(styled_text)

        if validation["coverage_percentage"] < VOCABULARY_COVERAGE_THRESHOLD:
            # Log the attempt for debugging
            non_noc = ", ".join(validation["non_noc_words"][:5])  # First 5
            self._logger.info(
                f"Vocabulary validation failed: {validation['coverage_percentage']:.1f}% < "
                f"{VOCABULARY_COVERAGE_THRESHOLD}%. Non-NOC words: {non_noc}"
            )
            raise VocabularyValidationError(
                f"Coverage {validation['coverage_percentage']}% < {VOCABULARY_COVERAGE_THRESHOLD}%. "
                f"Non-NOC words: {non_noc}"
            )

        return {
            "styled_text": styled_text,
            "validation_result": validation,
            "logprobs": response.choices[0].logprobs,
        }

    def generate_styled_statement(
        self, noc_statement_id: str, noc_text: str, section: str
    ) -> StyledStatement:
        """Generate styled statement with graceful fallback.

        Orchestrates the full generation lifecycle per RESEARCH.md Pattern 5:
        1. Attempt generation with retry
        2. Validate vocabulary coverage
        3. Check semantic equivalence
        4. Calculate confidence
        5. Fall back to original NOC on failure

        Args:
            noc_statement_id: Statement ID (e.g., "key_activities-0")
            noc_text: Original NOC statement text
            section: JD element section (key_activities, skills, effort, working_conditions)

        Returns:
            StyledStatement with either AI_STYLED or ORIGINAL_NOC content_type
        """
        try:
            # Attempt generation with retry
            result = self._generate_with_validation(section, noc_text)

            # Check semantic equivalence
            semantic_check = check_semantic_equivalence(noc_text, result["styled_text"])

            if not semantic_check["is_equivalent"]:
                self._logger.info(
                    f"Semantic equivalence failed: {semantic_check['similarity_score']:.4f} < "
                    f"{semantic_check['threshold']}"
                )
                raise SemanticEquivalenceError(
                    f"Similarity {semantic_check['similarity_score']} < "
                    f"{semantic_check['threshold']}"
                )

            # Success - calculate confidence from logprobs
            confidence = self._calculate_confidence(result.get("logprobs"))

            # Create vocabulary audit from validation result
            vocabulary_audit = self._create_vocabulary_audit(
                result["validation_result"], result["styled_text"]
            )

            return StyledStatement(
                original_noc_statement_id=noc_statement_id,
                original_noc_text=noc_text,
                styled_text=result["styled_text"],
                content_type=StyleContentType.AI_STYLED,
                confidence_score=confidence,
                retry_count=0,  # Success on first valid attempt
                vocabulary_coverage=result["validation_result"]["coverage_percentage"],
                vocabulary_audit=vocabulary_audit,
                generated_at=datetime.utcnow(),
                version_id=str(uuid4()),
            )

        except (VocabularyValidationError, SemanticEquivalenceError, RetryError) as e:
            # Retry budget exhausted or semantic check failed
            # Fall back to original NOC statement
            self._logger.warning(
                f"Generation failed for {noc_statement_id}, falling back to original: {e}"
            )

            # Create fallback vocabulary audit (100% coverage by definition)
            fallback_audit = VocabularyAudit(
                noc_terms_used=[],  # Original NOC is assumed compliant
                non_noc_terms=[],
                coverage_percentage=100.0,
                total_content_words=0,  # Not computed for fallback
                noc_word_count=0,
            )

            return StyledStatement(
                original_noc_statement_id=noc_statement_id,
                original_noc_text=noc_text,
                styled_text=noc_text,  # Use original as styled
                content_type=StyleContentType.ORIGINAL_NOC,  # Mark as fallback
                confidence_score=1.0,  # Original is always "confident"
                retry_count=MAX_RETRIES,  # Indicate exhausted retries
                vocabulary_coverage=100.0,  # Original is 100% NOC by definition
                vocabulary_audit=fallback_audit,
                generated_at=datetime.utcnow(),
                version_id=str(uuid4()),
            )


# Module-level singleton pattern for lazy initialization
_generation_service: Optional[GenerationService] = None


def get_generation_service(vocab_index: VocabularyIndex) -> GenerationService:
    """Get or create the GenerationService singleton.

    Allows lazy initialization with the vocab_index from app startup.

    Args:
        vocab_index: VocabularyIndex instance for validation

    Returns:
        GenerationService singleton instance
    """
    global _generation_service
    if _generation_service is None:
        _generation_service = GenerationService(vocab_index)
    return _generation_service
