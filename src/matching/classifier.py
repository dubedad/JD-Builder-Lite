"""LLM-based occupational group classifier using structured outputs.

Uses instructor library to wrap OpenAI for type-safe Pydantic integration,
enforcing AllocationResult schema with chain-of-thought reasoning.
"""

from typing import Dict, List
import instructor
from openai import OpenAI

from src.config import OPENAI_API_KEY, OPENAI_MODEL
from src.matching.models import AllocationResult
from src.matching.prompts import build_system_prompt, build_user_prompt


class LLMClassifier:
    """
    Classify JD against occupational groups using LLM structured outputs.

    Per CONTEXT.md decisions:
    - Holistic definition matching via LLM
    - Temperature=0 for deterministic classification
    - Chain-of-thought reasoning with evidence extraction
    - Structured output guarantees valid AllocationResult

    Uses instructor library for Pydantic response validation.
    """

    def __init__(self):
        """Initialize LLM classifier with instructor-wrapped OpenAI client."""
        # Wrap OpenAI client with instructor for structured outputs
        self.client = instructor.from_openai(OpenAI(api_key=OPENAI_API_KEY))
        self.model = OPENAI_MODEL  # e.g., "gpt-4o"

    def classify(
        self,
        jd_data: Dict,
        candidates: List[Dict],
        max_retries: int = 3
    ) -> AllocationResult:
        """
        Classify JD against candidate groups using LLM.

        Args:
            jd_data: Dict with position_title, client_service_results, key_activities
            candidates: Shortlisted candidates from semantic matching, each with:
                - group: dict with group_code, definition, inclusions, exclusions, source_url
                - semantic_similarity: float
            max_retries: Retry count for validation failures (instructor handles)

        Returns:
            AllocationResult with validated structure

        Raises:
            Exception: If LLM fails after retries
        """
        system_prompt = build_system_prompt()
        user_prompt = build_user_prompt(jd_data, candidates)

        # Call LLM with structured output
        # CRITICAL: temperature=0 for deterministic classification (per RESEARCH.md)
        result = self.client.chat.completions.create(
            model=self.model,
            temperature=0,  # Deterministic for classification
            response_model=AllocationResult,  # Enforce Pydantic schema
            max_retries=max_retries,  # instructor handles validation retries
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )

        return result

    def classify_with_fallback(
        self,
        jd_data: Dict,
        candidates: List[Dict]
    ) -> AllocationResult:
        """
        Classify with graceful fallback on LLM failure.

        If LLM fails but candidates exist, creates minimal fallback result
        using first candidate with low confidence and error warning.

        If no candidates or critical error, re-raises with better context.

        Args:
            jd_data: Dict with position_title, client_service_results, key_activities
            candidates: Shortlisted candidates from semantic matching

        Returns:
            AllocationResult (either successful or minimal fallback)

        Raises:
            Exception: If LLM fails and no fallback possible
        """
        try:
            return self.classify(jd_data, candidates)
        except Exception as e:
            # If no candidates, can't create valid fallback
            if not candidates:
                raise Exception(f"LLM classification failed and no candidates available: {str(e)}")

            # Create minimal fallback using first candidate
            from src.matching.models import GroupRecommendation
            first_candidate = candidates[0]
            group = first_candidate["group"]

            fallback_rec = GroupRecommendation(
                group_code=group.get("group_code", "UNKNOWN"),
                group_id=group.get("id", 0),
                confidence=0.0,  # Zero confidence for error state
                confidence_breakdown={
                    "definition_fit": 0.0,
                    "semantic_similarity": first_candidate.get("semantic_similarity", 0.0),
                    "exclusion_clear": 1.0,
                    "inclusion_support": 0.0,
                    "labels_boost": 0.0
                },
                definition_fit_rationale="Classification failed due to LLM error",
                reasoning_steps=[],
                evidence_spans=[],
                inclusion_check="Unable to evaluate due to error",
                exclusion_check="Unable to evaluate due to error",
                provenance_url=group.get("source_url", ""),
                provenance_paragraph=None
            )

            return AllocationResult(
                primary_purpose_summary=f"Classification failed: {str(e)}",
                top_recommendations=[fallback_rec],
                rejected_groups=[],
                borderline_flag=False,
                match_context="error",
                warnings=[f"LLM classification error: {str(e)}", "Fallback recommendation has zero confidence"]
            )


def classify_jd(jd_data: Dict, candidates: List[Dict]) -> AllocationResult:
    """
    Convenience function for single classification call.

    Args:
        jd_data: Dict with position_title, client_service_results, key_activities
        candidates: Shortlisted candidates from semantic matching

    Returns:
        AllocationResult with classification results
    """
    classifier = LLMClassifier()
    return classifier.classify(jd_data, candidates)
