"""Edge case detection and handling for occupational group allocation.

Per CONTEXT.md decisions:
- EDGE-01: AP vs TC disambiguation (theoretical vs practical)
- EDGE-02: Work appears in multiple groups (split duties)
- EDGE-03: Invalid Combination of Work
- EDGE-04: Vague JD content

These handlers surface edge cases for expert review while providing
actionable guidance.
"""

from typing import List, Dict, Optional

from src.matching.models import AllocationResult, GroupRecommendation


class EdgeCaseHandler:
    """
    Detect and handle edge cases in occupational group allocation.

    Per CONTEXT.md:
    - EDGE-01: AP vs TC disambiguation (theoretical vs practical)
    - EDGE-02: Work appears in multiple groups (split duties)
    - EDGE-03: Invalid Combination of Work
    - EDGE-04: Vague JD content
    """

    # Groups requiring special handling
    SPECIALIZED_GROUPS = ['EX', 'LC', 'MD']  # Separate classification processes

    # AP vs TC disambiguation rules (per TBS guidance)
    AP_TC_RULES = {
        'AP_indicators': [
            'theoretical',
            'applied science principles',
            'scientific method',
            'research methodology',
            'hypothesis',
            'experimental design',
            'scientific research',
            'theoretical framework',
            'research design'
        ],
        'TC_indicators': [
            'practical application',
            'technical procedures',
            'hands-on',
            'operational',
            'maintenance',
            'installation',
            'inspection',
            'repair',
            'equipment operation',
            'technical support'
        ]
    }

    def detect_ap_tc_ambiguity(
        self,
        recommendations: List[GroupRecommendation],
        jd_data: Dict
    ) -> Optional[str]:
        """
        Detect AP vs TC ambiguity and return disambiguation guidance.

        Per CONTEXT.md: "Explicit rules encoding TBS guidance on this specific disambiguation"

        Args:
            recommendations: List of group recommendations
            jd_data: Job description data with key_activities

        Returns:
            Disambiguation guidance string, or None if not applicable
        """
        # Check if both AP and TC are in top recommendations
        group_codes = [rec.group_code for rec in recommendations]
        has_ap = 'AP' in group_codes
        has_tc = 'TC' in group_codes

        if not (has_ap and has_tc):
            return None

        # Analyze JD text for indicators
        jd_text = self._extract_jd_text(jd_data).lower()

        ap_count = sum(1 for indicator in self.AP_TC_RULES['AP_indicators'] if indicator in jd_text)
        tc_count = sum(1 for indicator in self.AP_TC_RULES['TC_indicators'] if indicator in jd_text)

        if ap_count > tc_count:
            guidance = (
                f"AP vs TC ambiguity detected. Job description shows {ap_count} theoretical/research "
                f"indicators vs {tc_count} practical/technical indicators. "
                "Consider AP (Applied Science Research) if work focuses on theoretical knowledge "
                "application, scientific method, and research design."
            )
        elif tc_count > ap_count:
            guidance = (
                f"AP vs TC ambiguity detected. Job description shows {tc_count} practical/technical "
                f"indicators vs {ap_count} theoretical/research indicators. "
                "Consider TC (Technical) if work focuses on hands-on technical procedures, "
                "equipment operation, and practical applications."
            )
        else:
            guidance = (
                "AP vs TC ambiguity detected. Job description shows equal theoretical and practical "
                "indicators. Expert review recommended to determine if work is primarily research-oriented "
                "(AP) or technically operational (TC)."
            )

        return guidance

    def detect_split_duties(
        self,
        recommendations: List[GroupRecommendation]
    ) -> Optional[Dict[str, float]]:
        """
        Detect when duties split across multiple groups.

        Per CONTEXT.md: "Surface the split - show distribution and recommend
        based on primary, but flag the split (e.g., '40% AS, 35% PM, 25% CS')"

        Args:
            recommendations: List of group recommendations

        Returns:
            Dict with group percentages, or None if single-group dominant
        """
        if len(recommendations) < 2:
            return None

        # Check if top 2-3 scores are close (within 0.15 margin)
        scores = [rec.confidence for rec in recommendations]
        top_score = scores[0]

        # Count how many scores are within 15% of top score
        close_scores = [s for s in scores if (top_score - s) < 0.15]

        if len(close_scores) < 2:
            # Single dominant group
            return None

        # Calculate duty distribution (normalize to percentages)
        total = sum(close_scores)
        if total == 0:
            return None

        distribution = {}
        for idx, rec in enumerate(recommendations[:len(close_scores)]):
            percentage = (scores[idx] / total)
            distribution[rec.group_code] = round(percentage, 2)

        # Only flag as split if no single group dominates (>60%)
        max_percentage = max(distribution.values())
        if max_percentage >= 0.60:
            return None

        return distribution

    def detect_invalid_combination(
        self,
        recommendations: List[GroupRecommendation],
        jd_data: Dict
    ) -> bool:
        """
        Detect Invalid Combination of Work.

        Per CONTEXT.md: "suggest the JD may need to be split into multiple positions"

        This is a more severe version of split duties - when the work described
        spans fundamentally incompatible occupational categories.

        Args:
            recommendations: List of group recommendations
            jd_data: Job description data

        Returns:
            True if work combination is invalid (should be split)
        """
        if len(recommendations) < 2:
            return False

        # Detect incompatible group combinations
        group_codes = [rec.group_code for rec in recommendations[:3]]

        # Define incompatible pairs (administrative vs technical vs professional)
        INCOMPATIBLE_PAIRS = [
            ({'AS', 'CR'}, {'PM', 'PE'}),  # Admin support vs program management
            ({'CS', 'IT'}, {'AS', 'CR'}),  # IT technical vs admin support
            ({'EN', 'BI'}, {'PM', 'EC'}),  # Engineering vs economics/policy
        ]

        for pair_a, pair_b in INCOMPATIBLE_PAIRS:
            has_from_a = any(code in pair_a for code in group_codes)
            has_from_b = any(code in pair_b for code in group_codes)

            if has_from_a and has_from_b:
                # Check if both have significant confidence (>0.5)
                conf_a = max([rec.confidence for rec in recommendations if rec.group_code in pair_a] or [0])
                conf_b = max([rec.confidence for rec in recommendations if rec.group_code in pair_b] or [0])

                if conf_a >= 0.5 and conf_b >= 0.5:
                    return True

        return False

    def detect_vague_jd(
        self,
        jd_data: Dict,
        top_confidence: float
    ) -> Optional[List[str]]:
        """
        Detect insufficient JD content.

        Per CONTEXT.md: Return "Needs Work Description Clarification"
        with specific questions about what's missing.

        Args:
            jd_data: Job description data
            top_confidence: Confidence of top recommendation

        Returns:
            List of clarification questions, or None if JD is adequate
        """
        questions = []

        # Check for missing or very short client-service results
        csr = jd_data.get('client_service_results', '')
        if not csr or len(csr.strip()) < 30:
            questions.append(
                "What specific client-service results does this position deliver? "
                "Describe the main outcomes or deliverables."
            )

        # Check for missing or insufficient key activities
        activities = jd_data.get('key_activities', [])
        if not activities or len(activities) < 2:
            questions.append(
                "What are the key activities performed in this position? "
                "List at least 3-5 primary duties."
            )
        elif any(len(activity.strip()) < 20 for activity in activities):
            questions.append(
                "Key activities are too brief. Provide more detail about what the position actually does."
            )

        # Check if top confidence is low (indicates vague match)
        if top_confidence < 0.5 and not questions:
            questions.append(
                "The job description matches weakly with occupational groups. "
                "Provide more specific details about the nature of the work, "
                "required expertise, and primary responsibilities."
            )

        return questions if questions else None

    def check_specialized_group(
        self,
        group_code: str
    ) -> bool:
        """
        Check if group has separate classification process.

        Per CONTEXT.md: "Match normally but flag if recommending"

        Args:
            group_code: Occupational group code

        Returns:
            True if group has separate classification process
        """
        return group_code in self.SPECIALIZED_GROUPS

    def apply_all_checks(
        self,
        result: AllocationResult,
        jd_data: Dict
    ) -> AllocationResult:
        """
        Apply all edge case checks and update result accordingly.

        Modifies result in place:
        - Updates match_context if split/ambiguity detected
        - Adds warnings for specialized groups
        - Adds duty_split if multi-group work detected
        - Updates warnings list with clarification needs

        Args:
            result: Current allocation result
            jd_data: Job description data

        Returns:
            Modified AllocationResult with edge case flags
        """
        if not result.top_recommendations:
            return result

        # Check for AP/TC ambiguity
        ap_tc_guidance = self.detect_ap_tc_ambiguity(result.top_recommendations, jd_data)
        if ap_tc_guidance:
            result.warnings.append(ap_tc_guidance)

        # Check for split duties
        duty_split = self.detect_split_duties(result.top_recommendations)
        if duty_split:
            result.duty_split = duty_split
            # Format split for human readability
            split_str = ", ".join([f"{pct*100:.0f}% {code}" for code, pct in duty_split.items()])
            result.match_context = f"split duties detected: {split_str}"
            result.warnings.append(
                f"Work appears split across multiple groups: {split_str}. "
                "Consider if position should be restructured or if one group is primary."
            )

        # Check for invalid combination
        if self.detect_invalid_combination(result.top_recommendations, jd_data):
            result.warnings.append(
                "Invalid Combination of Work detected. This JD describes work spanning "
                "fundamentally different occupational categories. Consider splitting into "
                "multiple positions with focused duties."
            )

        # Check for vague JD
        top_confidence = result.top_recommendations[0].confidence if result.top_recommendations else 0.0
        clarification_questions = self.detect_vague_jd(jd_data, top_confidence)
        if clarification_questions:
            result.warnings.append("Needs Work Description Clarification:")
            result.warnings.extend([f"  - {q}" for q in clarification_questions])

        # Check for specialized groups
        for rec in result.top_recommendations:
            if self.check_specialized_group(rec.group_code):
                result.warnings.append(
                    f"Note: {rec.group_code} group has a separate classification process. "
                    "This recommendation indicates potential fit, but formal classification "
                    "requires specialized review."
                )

        return result

    def _extract_jd_text(self, jd_data: Dict) -> str:
        """Extract all JD text for analysis."""
        parts = []
        if jd_data.get('position_title'):
            parts.append(jd_data['position_title'])
        if jd_data.get('client_service_results'):
            parts.append(jd_data['client_service_results'])
        for activity in jd_data.get('key_activities', []):
            parts.append(activity)
        return " ".join(parts)


# Convenience functions for standalone usage
def detect_ap_tc_ambiguity(recommendations: List[GroupRecommendation], jd_data: Dict) -> Optional[str]:
    """Convenience function for AP/TC ambiguity detection."""
    handler = EdgeCaseHandler()
    return handler.detect_ap_tc_ambiguity(recommendations, jd_data)


def detect_split_duties(recommendations: List[GroupRecommendation]) -> Optional[Dict[str, float]]:
    """Convenience function for split duties detection."""
    handler = EdgeCaseHandler()
    return handler.detect_split_duties(recommendations)


def detect_vague_jd(jd_data: Dict, top_confidence: float) -> Optional[List[str]]:
    """Convenience function for vague JD detection."""
    handler = EdgeCaseHandler()
    return handler.detect_vague_jd(jd_data, top_confidence)


__all__ = [
    'EdgeCaseHandler',
    'detect_ap_tc_ambiguity',
    'detect_split_duties',
    'detect_vague_jd',
]
