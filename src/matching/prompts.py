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

3. CHECK INCLUSIONS (active evidence — weighted in confidence scoring)
   - Inclusion statements define SPECIFIC types of work that belong to this group
   - CRITICAL for PA sub-groups (AS, CR, PM, DA, IS, CM, OE, OM, ST, WP): these
     groups share the same parent definition, so inclusions are the PRIMARY
     differentiator. A position belongs to AS vs CR vs PM based on which inclusion
     statements match, not the shared definition text.
   - Score inclusion match from 0.0–1.0 in the "inclusion_match_score" field:
       1.0 = all/most inclusions clearly apply
       0.5 = some inclusions apply
       0.0 = no inclusions apply
   - Report which specific inclusions apply with JD quotes supporting each match

4. CHECK EXCLUSIONS (hard gate — eliminates the group if matched)
   - If the primary purpose matches an exclusion statement, ELIMINATE the group
   - Exclusion match means the work explicitly does NOT belong to this group
   - Be specific about which exclusion conflicts, if any
   - A strong exclusion match should set confidence near 0.0

5. RANK RECOMMENDATIONS
   - Provide top 3 recommendations with confidence scores (0.0-1.0)
   - High confidence (0.85+) requires: strong definition fit + inclusion match (0.7+) + no exclusions + strong semantic match
   - Include reasoning steps with exact quotes from the JOB DESCRIPTION as evidence (use quotation marks). NEVER quote from the occupational group definitions — only quote text that appears verbatim in Client-Service Results or Key Activities.
   - Explain why other groups were rejected, citing specific exclusions or inclusion mismatches
   - For each recommended group, list 2-4 "caveats" that are SPECIFIC to this group's match: concerns or limitations unique to this particular group (e.g., "Position's data analysis duties could also fit EC group"). Do NOT repeat the same caveats across multiple groups.
   - For each recommended group, populate "og_definition_statements" with 3-5 items that together describe WHY this group fits. Include:
       (a) 1-2 sentences from THIS group's definition text (not the parent group)
       (b) The specific inclusion statements from THIS group that match this job (prefix with "Included: ")
       (c) Any relevant exclusions that were ruled out (prefix with "Not included: ")
     Each group must have its own distinct, group-specific statements.

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
