"""LLM service for generating job description overviews."""

import os
from typing import Generator, List
from openai import OpenAI
from src.config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_MAX_TOKENS, OPENAI_TEMPERATURE
from src.models.ai import StatementInput, JobContext

# Prompt version for provenance tracking
PROMPT_VERSION = "v1.1"

# JD Element display names
JD_ELEMENT_LABELS = {
    "key_activities": "Key Activities",
    "skills": "Skills",
    "effort": "Effort",
    "responsibility": "Responsibility",
    "working_conditions": "Working Conditions"
}

# Icon options for occupation icon selection
ICON_OPTIONS = {
    "legislative": "fa-landmark",
    "management": "fa-users-cog",
    "business": "fa-briefcase",
    "finance": "fa-chart-line",
    "administrative": "fa-clipboard",
    "sciences": "fa-atom",
    "technology": "fa-laptop-code",
    "health": "fa-heartbeat",
    "nursing": "fa-user-nurse",
    "education": "fa-graduation-cap",
    "law": "fa-balance-scale",
    "social": "fa-hands-helping",
    "arts": "fa-palette",
    "culture": "fa-theater-masks",
    "sports": "fa-running",
    "sales": "fa-handshake",
    "service": "fa-concierge-bell",
    "transport": "fa-plane",
    "aviation": "fa-plane",
    "shipping": "fa-ship",
    "trucking": "fa-truck",
    "trades": "fa-tools",
    "construction": "fa-hard-hat",
    "agriculture": "fa-tractor",
    "manufacturing": "fa-industry",
    "security": "fa-shield-alt",
    "military": "fa-medal",
    "default": "fa-briefcase"
}

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)


def build_system_prompt() -> str:
    """Build the system prompt for GPT-4o."""
    return """You are an expert HR consultant specializing in Canadian job descriptions.
You create professional General Overview sections that accurately reflect the role based on NOC (National Occupational Classification) data.

Guidelines:
- Write 3-4 paragraphs of professional prose (approximately 200-300 words total)
- Paragraph 1: Role purpose and organizational context
- Paragraph 2: Primary responsibilities and key activities
- Paragraph 3: Required expertise, skills, and working conditions
- Paragraph 4 (optional): Unique aspects of the role or additional context provided
- Use professional, clear language appropriate for a Government of Canada job posting
- Synthesize information from all provided NOC elements
- Do NOT copy NOC statements verbatim - synthesize and contextualize
- The overview should give a reader a clear understanding of what this job entails"""


def build_user_prompt(statements: List[StatementInput], context: JobContext, additional_context: str = "") -> str:
    """Build the user prompt with job context and grouped statements."""
    # Group statements by JD element
    grouped = {}
    for stmt in statements:
        element = stmt.jd_element
        if element not in grouped:
            grouped[element] = []
        grouped[element].append(stmt)

    # Build prompt parts
    parts = [
        f"Job Title: {context.job_title}",
        f"NOC Code: {context.noc_code} - {context.noc_title}",
    ]

    if context.occupation_code:
        parts.append(f"Occupation Code: {context.occupation_code}")

    parts.extend(["", "Selected NOC Statements:", ""])

    # Add grouped statements
    for element_key in ["key_activities", "skills", "effort", "responsibility", "working_conditions"]:
        if element_key in grouped:
            label = JD_ELEMENT_LABELS.get(element_key, element_key)
            parts.append(f"{label}:")
            for stmt in grouped[element_key]:
                parts.append(f"  - {stmt.text}")
            parts.append("")

    if additional_context:
        parts.extend(["", f"Additional Context from Hiring Manager:", f"{additional_context}", ""])

    parts.append("Generate a professional General Overview section (3-4 paragraphs) for this job description:")

    return "\n".join(parts)


def generate_stream(statements: List[StatementInput], context: JobContext, additional_context: str = "") -> Generator[str, None, None]:
    """
    Stream GPT-4o response token-by-token.

    Yields SSE-formatted data events:
    - "data: <token>\\n\\n" for content tokens
    - "data: [DONE]\\n\\n" on success
    - "data: [ERROR] <message>\\n\\n" on failure
    """
    try:
        system_prompt = build_system_prompt()
        user_prompt = build_user_prompt(statements, context, additional_context)

        stream = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=OPENAI_TEMPERATURE,
            max_tokens=OPENAI_MAX_TOKENS,
            stream=True
        )

        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                token = chunk.choices[0].delta.content
                yield f"data: {token}\n\n"

        yield "data: [DONE]\n\n"

    except Exception as e:
        error_msg = str(e)
        # Sanitize error message for client
        if "api_key" in error_msg.lower():
            error_msg = "API key error - check OPENAI_API_KEY configuration"
        yield f"data: [ERROR] {error_msg}\n\n"


def get_model_name() -> str:
    """Return the model name for provenance tracking."""
    return OPENAI_MODEL


def get_prompt_version() -> str:
    """Return the prompt version for provenance tracking."""
    return PROMPT_VERSION


def select_occupation_icon(occupation_title: str, lead_statement: str) -> str:
    """
    Select an appropriate Font Awesome icon class for an occupation.

    Uses LLM to choose the most appropriate icon from ICON_OPTIONS based on
    the occupation title and lead statement.

    Args:
        occupation_title: The NOC occupation title
        lead_statement: The NOC lead statement/description

    Returns:
        Font Awesome icon class (e.g., "fa-atom")
        Falls back to "fa-briefcase" on error or invalid response
    """
    try:
        # Build available icons list for the prompt
        icon_list = "\n".join([f"- {category}: {icon_class}" for category, icon_class in ICON_OPTIONS.items()])

        system_prompt = "You are an icon selection expert. Select ONE icon class from the list that best represents this occupation. Return ONLY the icon class name."

        user_prompt = f"""Occupation: {occupation_title}

Description: {lead_statement}

Available icon classes:
{icon_list}

Select the most appropriate icon class. Return ONLY the icon class name (e.g., "fa-atom")."""

        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0,  # Deterministic
            max_tokens=30
        )

        # Extract and validate response
        icon_class = response.choices[0].message.content.strip()

        # Validate it's in our allowed list
        if icon_class in ICON_OPTIONS.values():
            return icon_class
        else:
            # Fallback to default
            return "fa-briefcase"

    except Exception as e:
        # Log error but return fallback gracefully
        print(f"Icon selection error: {e}")
        return "fa-briefcase"


def generate_occupation_description(occupation_title: str, lead_statement: str, main_duties: List[str]) -> str:
    """
    Generate a concise occupation description paragraph.

    Uses LLM to synthesize a 3-4 sentence paragraph describing what workers
    in this occupation do, based on NOC data.

    Args:
        occupation_title: The NOC occupation title
        lead_statement: The NOC lead statement
        main_duties: List of main duty statements (uses first 5)

    Returns:
        Generated description paragraph (~100 words)
        Returns empty string on error
    """
    try:
        # Limit to first 5 duties
        duties_subset = main_duties[:5] if main_duties else []
        duties_text = "\n".join([f"- {duty}" for duty in duties_subset])

        system_prompt = "You are an expert HR consultant. Generate a concise 3-4 sentence paragraph (~100 words) describing what workers in this occupation do. Write in third person present tense. Synthesize the information - do not copy verbatim."

        user_prompt = f"""Occupation: {occupation_title}

Lead Statement: {lead_statement}

Main Duties:
{duties_text}

Generate a professional 3-4 sentence description of what workers in this occupation do."""

        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,  # Slight creativity
            max_tokens=200
        )

        # Extract and clean response
        description = response.choices[0].message.content.strip()
        return description

    except Exception as e:
        # Log error but return empty string gracefully
        print(f"Description generation error: {e}")
        return ""
