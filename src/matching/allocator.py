"""Main allocation orchestrator for Classification Step 1.

Integrates all matching components into a single coherent pipeline:
1. Load occupational groups from database
2. Shortlist candidates using semantic similarity + labels
3. LLM classification with structured outputs
4. Multi-factor confidence scoring
5. Evidence extraction and provenance linking
6. Edge case detection and handling

Per CONTEXT.md: "Engine should feel like a classification advisor -
transparent about its reasoning, not a black box"
"""

from typing import Dict, List

from src.storage.db_manager import get_db
from src.storage.repository import OccupationalGroupRepository
from src.matching.models import AllocationResult, GroupRecommendation
from src.matching.shortlisting import shortlist_with_all_signals
from src.matching.classifier import LLMClassifier
from src.matching.confidence import ConfidenceCalculator, check_borderline, CONFIDENCE_THRESHOLD
from src.matching.evidence.extractor import EvidenceExtractor
from src.matching.edge_cases import EdgeCaseHandler


class OccupationalGroupAllocator:
    """
    Main allocation engine for Classification Step 1.

    Orchestrates:
    1. Load occupational groups from database
    2. Shortlist candidates using semantic similarity + labels
    3. LLM classification with structured outputs
    4. Multi-factor confidence scoring
    5. Evidence extraction and provenance linking
    6. Edge case detection and handling

    Per CONTEXT.md: "Engine should feel like a classification advisor -
    transparent about its reasoning, not a black box"
    """

    def __init__(self):
        """Initialize allocator with all component instances."""
        self.classifier = LLMClassifier()
        self.confidence_calc = ConfidenceCalculator()
        self.evidence_extractor = EvidenceExtractor()
        self.edge_case_handler = EdgeCaseHandler()

    def allocate(self, jd_data: Dict) -> AllocationResult:
        """
        Allocate JD to occupational group(s).

        Args:
            jd_data: Dict containing:
                - position_title: str (optional)
                - client_service_results: str
                - key_activities: List[str]

        Returns:
            AllocationResult with:
                - top_recommendations (max 3, above 0.3 threshold)
                - rejected_groups with explanations
                - provenance links to TBS sources
                - edge case flags and warnings
        """
        # Step 1: Load groups from database
        groups = self._load_groups_with_statements()
        if not groups:
            return self._empty_result("No occupational groups found in database")

        # Step 2: Extract primary purpose text
        jd_text = self._extract_primary_purpose_text(jd_data)
        if not jd_text.strip():
            return self._empty_result("Job description has no content")

        # Step 3: Shortlist candidates
        candidates = shortlist_with_all_signals(
            jd_text=jd_text,
            groups=groups,
            min_similarity=0.2,  # Lower for shortlisting, filter later
            max_candidates=10
        )

        if not candidates:
            return self._empty_result("No candidate groups found above similarity threshold")

        # Step 4: LLM classification
        llm_result = self.classifier.classify_with_fallback(jd_data, candidates)

        # Step 5: Enhance with multi-factor confidence
        enhanced = self._enhance_confidence(llm_result, candidates)

        # Step 6: Link evidence and provenance
        enhanced = self._link_evidence_and_provenance(enhanced, jd_data)

        # Step 7: Apply edge case checks
        enhanced = self.edge_case_handler.apply_all_checks(enhanced, jd_data)

        # Step 8: Filter by confidence threshold and limit to top 3
        enhanced = self._apply_threshold_and_limit(enhanced)

        # Step 9: Fill missing og_definition_statements from group definition text
        enhanced = self._fill_missing_og_statements(enhanced, groups)

        return enhanced

    def _load_groups_with_statements(self) -> List[Dict]:
        """Load all current groups with inclusions/exclusions.

        Returns:
            List of group dicts with definition, inclusions, exclusions
        """
        with get_db() as conn:
            repo = OccupationalGroupRepository(conn)
            return repo.get_groups_with_statements()

    def _extract_primary_purpose_text(self, jd_data: Dict) -> str:
        """
        Extract text for matching.

        Per CONTEXT.md: "Combined analysis using Client-Service Results +
        Key Activities together for fuller picture"

        Args:
            jd_data: Dict with client_service_results and key_activities

        Returns:
            Combined text for matching
        """
        parts = []

        if jd_data.get('client_service_results'):
            parts.append(f"Client-Service Results: {jd_data['client_service_results']}")

        for idx, activity in enumerate(jd_data.get('key_activities', []), 1):
            if activity and activity.strip():
                parts.append(f"Key Activity {idx}: {activity}")

        return "\n".join(parts)

    def _enhance_confidence(
        self,
        llm_result: AllocationResult,
        candidates: List[Dict]
    ) -> AllocationResult:
        """
        Recalculate confidence using multi-factor scoring.

        Per CONTEXT.md: Don't just use LLM-stated confidence.
        Combine with semantic similarity and labels boost.

        CRITICAL per CONTEXT.md decision: "Inclusion statements: Use for shortlisting
        candidates only, not for scoring or evidence"

        Therefore, inclusion_match is NOT passed to calculate_confidence().
        Inclusions helped identify candidates in shortlisting (Plan 15-02),
        but do not contribute to final confidence score.

        Args:
            llm_result: Result from LLM classification
            candidates: Shortlisted candidates with semantic scores

        Returns:
            AllocationResult with enhanced confidence scores
        """
        # Build lookup of candidate scores by group_code
        candidate_scores = {
            c['group']['group_code']: c
            for c in candidates
        }

        for rec in llm_result.top_recommendations:
            cand = candidate_scores.get(rec.group_code, {})

            new_conf, breakdown = self.confidence_calc.calculate_confidence(
                definition_fit_score=rec.confidence,  # LLM's score as definition fit
                semantic_similarity=cand.get('semantic_similarity', 0.5),
                exclusion_conflict='conflict' in rec.exclusion_check.lower(),
                labels_boost=cand.get('labels_boost', 0.0),
                inclusion_match_score=getattr(rec, 'inclusion_match_score', 0.0),
            )

            rec.confidence = new_conf
            rec.confidence_breakdown = breakdown

        # Re-sort by updated confidence
        llm_result.top_recommendations.sort(key=lambda r: r.confidence, reverse=True)

        # Update borderline flag based on new scores
        scores = [r.confidence for r in llm_result.top_recommendations]
        if scores:
            is_borderline, context = check_borderline(scores)
            llm_result.borderline_flag = is_borderline
            if is_borderline or llm_result.match_context == "error":
                # Preserve error context or update with borderline
                if llm_result.match_context != "error":
                    llm_result.match_context = context

        return llm_result

    def _link_evidence_and_provenance(
        self,
        result: AllocationResult,
        jd_data: Dict
    ) -> AllocationResult:
        """
        Link evidence spans to JD fields and add TBS provenance.

        Per CONTEXT.md: Evidence linking with "text spans, field references,
        and highlighted excerpts"

        Args:
            result: Current allocation result
            jd_data: Original job description data

        Returns:
            AllocationResult with enhanced evidence linking
        """
        # Extract evidence spans for each recommendation
        for rec in result.top_recommendations:
            # Collect quotes from reasoning steps
            quotes = [step.evidence for step in rec.reasoning_steps if step.evidence]

            # Extract spans with field references
            spans = self.evidence_extractor.extract_evidence_spans(jd_data, quotes)

            # Update evidence_spans (LLM already populated text, enhance with positions)
            # Convert to EvidenceSpan objects
            from src.matching.models import EvidenceSpan

            enhanced_spans = []
            for span in spans:
                enhanced_spans.append(
                    EvidenceSpan(
                        text=span['text'],
                        field=span['field'] or "Unknown",
                        start_char=span.get('start_char'),
                        end_char=span.get('end_char')
                    )
                )

            # Replace or merge with existing evidence_spans
            if enhanced_spans:
                rec.evidence_spans = enhanced_spans

        # Provenance URLs already included by LLM via provenance_url field
        # No additional linking needed - archive_path available in database
        # for audit verification via group_id foreign key

        return result

    def _apply_threshold_and_limit(
        self,
        result: AllocationResult
    ) -> AllocationResult:
        """
        Apply confidence threshold and limit to top 3.

        Per CONTEXT.md: "Minimum 0.3 confidence to appear in top-3"

        Args:
            result: Current allocation result

        Returns:
            AllocationResult with filtered recommendations
        """
        # Filter by threshold
        result.top_recommendations = [
            r for r in result.top_recommendations
            if r.confidence >= CONFIDENCE_THRESHOLD
        ]

        # Limit to 3
        if len(result.top_recommendations) > 3:
            # Move excess to rejected_groups
            from src.matching.models import RejectedGroup

            for rec in result.top_recommendations[3:]:
                result.rejected_groups.append(
                    RejectedGroup(
                        group_code=rec.group_code,
                        rejection_reason=f"Below top-3 threshold (ranked #{len([r for r in result.top_recommendations if r.confidence > rec.confidence]) + 1})",
                        exclusion_conflict=None,
                        confidence_if_considered=rec.confidence
                    )
                )

            result.top_recommendations = result.top_recommendations[:3]

        # Add warning if no recommendations above threshold
        if not result.top_recommendations:
            result.warnings.append(
                f"No recommendations above {CONFIDENCE_THRESHOLD} confidence threshold. "
                "Job description may need clarification or may not match standard occupational groups."
            )

        return result

    def _fill_missing_og_statements(
        self,
        result: AllocationResult,
        groups: List[Dict]
    ) -> AllocationResult:
        """
        Build og_definition_statements from the authoritative DB data:
        definition text + inclusion statements + exclusion statements.

        The LLM cross-contaminates this field (putting one group's text into
        another). We always rebuild from the DB to guarantee correctness.

        For groups that share a parent definition (e.g., PA sub-groups AS, CR,
        PM, DA, etc.), the inclusion and exclusion statements are the PRIMARY
        differentiator. This method ensures each group shows its own distinct
        statements regardless of shared definition text.

        Structure of output statements:
        - Up to 2 sentences from the group's own definition
        - Each inclusion statement prefixed with "Included: "
        - Each exclusion statement prefixed with "Not included: "

        Args:
            result: AllocationResult with top_recommendations
            groups: Full group list from _load_groups_with_statements()
                    (each dict has 'definition', 'inclusions', 'exclusions')

        Returns:
            AllocationResult with og_definition_statements sourced from DB
        """
        import re

        group_by_code = {g['group_code']: g for g in groups}

        for rec in result.top_recommendations:
            group = group_by_code.get(rec.group_code)
            if not group:
                continue

            statements = []

            # 1. Up to 2 sentences from the definition (for context)
            definition = group.get('definition', '').strip()
            if definition:
                sentences = re.split(r'(?<=[.!?])\s+', definition)
                statements.extend([s for s in sentences if s][:2])

            # 2. All inclusion statements (these differentiate sub-groups)
            for inc in group.get('inclusions', []):
                if inc and inc.strip():
                    statements.append(f"Included: {inc.strip()}")

            # 3. Exclusion statements (hard gates — equally important to show)
            for exc in group.get('exclusions', []):
                if exc and exc.strip():
                    statements.append(f"Not included: {exc.strip()}")

            if statements:
                rec.og_definition_statements = statements

        return result

    def _empty_result(self, reason: str) -> AllocationResult:
        """
        Return valid empty result with explanation.

        Args:
            reason: Explanation for why no recommendations

        Returns:
            AllocationResult with empty recommendations
        """
        return AllocationResult(
            primary_purpose_summary=reason,
            top_recommendations=[],
            rejected_groups=[],
            borderline_flag=False,
            match_context="no viable candidates",
            warnings=[reason]
        )


def allocate_jd(jd_data: Dict) -> AllocationResult:
    """
    Convenience function for single allocation call.

    Args:
        jd_data: Dict with position_title, client_service_results, key_activities

    Returns:
        AllocationResult with occupational group recommendations

    Example:
        >>> jd = {
        ...     'position_title': 'Policy Analyst',
        ...     'client_service_results': 'Develops policy recommendations...',
        ...     'key_activities': ['Conducts research', 'Prepares briefings']
        ... }
        >>> result = allocate_jd(jd)
        >>> print(result.top_recommendations[0].group_code)
        'EC'
    """
    allocator = OccupationalGroupAllocator()
    return allocator.allocate(jd_data)


__all__ = ['OccupationalGroupAllocator', 'allocate_jd']
