"""Prompt templates for LLM occupational group classification.

Encodes the TBS allocation method: extract primary purpose from JD,
evaluate holistic definition fit, check inclusions/exclusions, rank groups.
"""

from typing import Dict, List

# Version tracking for provenance
PROMPT_VERSION = "v1.0-allocation"


def build_system_prompt() -> str:
    """
    System prompt encoding TBS classification method.

    Per CONTEXT.md decisions:
    - Combined analysis of Client-Service Results + Key Activities
    - Holistic definition matching (not keyword)
    - Inclusions for shortlisting support, exclusions as hard gate
    - Transparent reasoning with evidence
    """
    return '''You are a TBS occupational group classification expert using the prescribed allocation method.

Your task: Match job descriptions to occupational groups by:

1. EXTRACT PRIMARY PURPOSE
   - Analyze Client-Service Results and Key Activities together
   - Determine WHY this position exists (its primary purpose)
   - Focus on the WORK described, not person attributes

2. EVALUATE DEFINITION FIT
   - Compare primary purpose to each group's full definition holistically
   - Think like a human classifier: semantic meaning, not keyword matching
   - Consider the overall intent and focus of the work

3. CHECK INCLUSIONS (for support only)
   - Review inclusion statements for supporting evidence
   - Inclusions help confirm a match but don't determine it
   - Report which inclusions apply or "none applies"

4. CHECK EXCLUSIONS (hard gate)
   - If primary purpose matches an exclusion, ELIMINATE the group
   - Exclusion match means the work explicitly does NOT belong to this group
   - Be specific about which exclusion conflicts, if any

5. RANK RECOMMENDATIONS
   - Provide top 3 recommendations with confidence scores (0.0-1.0)
   - High confidence (0.85+) requires: definition fit + inclusion support + no exclusions + strong semantic match
   - Include reasoning steps with exact quotes from JD as evidence (use quotation marks)
   - Explain why other groups were rejected
   - For each recommended group, list 2-4 "caveats": concerns, borderline aspects, or limitations of the match (e.g., "Position's data analysis duties could also fit EC group")
   - For each recommended group, extract 3-5 key sentences from the group definition text that are most relevant to this job's primary purpose as "og_definition_statements"

Classification principles:
- Evaluate the WORK described in the JD, not person-specific attributes
- When in doubt, favor the group whose definition most closely describes the primary purpose
- Flag borderline cases where top scores are within 10% of each other
- Surface any title-duty mismatches as observations

Output structured results with reasoning steps, evidence spans, and confidence scores.'''


def build_user_prompt(jd_data: Dict, candidates: List[Dict], max_activities: int = 15) -> str:
    """
    Build user prompt with JD data and shortlisted candidate groups.

    Args:
        jd_data: Dict with position_title, client_service_results, key_activities
        candidates: List of candidate dicts from shortlister, each containing:
            - group: dict with group_code, definition, inclusions, exclusions, source_url
            - semantic_similarity: float
        max_activities: Maximum number of activities to include (prevents token overflow)

    Returns:
        Formatted prompt string with JD content and candidates
    """
    # Extract JD content
    title = jd_data.get("position_title", "Unknown")
    results = jd_data.get("client_service_results", "")
    activities = jd_data.get("key_activities", [])[:max_activities]  # Limit to prevent token overflow

    # Format key activities list
    activities_str = "\n".join([f"- {act}" for act in activities]) if activities else "None specified"

    # Build prompt
    prompt = f"""# JOB DESCRIPTION TO CLASSIFY

## Position Title
{title}

## Client-Service Results
{results}

## Key Activities
{activities_str}

---

# CANDIDATE OCCUPATIONAL GROUPS

You have {len(candidates)} shortlisted candidate groups to evaluate:

"""

    # Add each candidate group
    for idx, candidate in enumerate(candidates, 1):
        group = candidate["group"]
        sim = candidate.get("semantic_similarity", 0.0)

        group_code = group.get("group_code", "Unknown")
        definition = group.get("definition", "")
        inclusions = group.get("inclusions", [])
        exclusions = group.get("exclusions", [])
        source_url = group.get("source_url", "")

        # Format inclusions
        if inclusions:
            inclusions_str = "\n".join([f"  - {inc}" for inc in inclusions])
        else:
            inclusions_str = "  None"

        # Format exclusions
        if exclusions:
            exclusions_str = "\n".join([f"  - {exc}" for exc in exclusions])
        else:
            exclusions_str = "  None"

        prompt += f"""## Candidate {idx}: {group_code}
**Semantic similarity:** {sim:.3f}

**Definition:**
{definition}

**Inclusions:**
{inclusions_str}

**Exclusions:**
{exclusions_str}

**Source:** {source_url}

---

"""

    # Add task instructions
    prompt += """# YOUR TASK

Classify this job description against the candidate groups above:

1. Extract and summarize the primary purpose of the position
2. Evaluate each candidate group's definition fit holistically
3. Check inclusions (supportive evidence) and exclusions (hard gate)
4. Provide top 3 recommendations with confidence scores, reasoning, and evidence
5. Explain why other groups were rejected
6. Flag borderline cases (top scores within 10% margin)

Remember to quote exact text from the JD using quotation marks when providing evidence.
"""

    return prompt
