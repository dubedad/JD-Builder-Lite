"""LLM service for generating job description overviews."""

import os
from typing import Generator, List
from openai import OpenAI
from src.config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_MAX_TOKENS, OPENAI_TEMPERATURE
from src.models.ai import StatementInput, JobContext

# Prompt version for provenance tracking
PROMPT_VERSION = "v1.0"

# JD Element display names
JD_ELEMENT_LABELS = {
    "key_activities": "Key Activities",
    "skills": "Skills",
    "effort": "Effort",
    "responsibility": "Responsibility",
    "working_conditions": "Working Conditions"
}

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)


def build_system_prompt() -> str:
    """Build the system prompt for GPT-4o."""
    return """You are an expert HR consultant specializing in Canadian job descriptions.
You create concise, professional General Overview sections that accurately reflect the role based on NOC (National Occupational Classification) data.

Guidelines:
- Write 4-6 sentences (approximately 150-200 words)
- Focus on the role's purpose and key responsibilities
- Use professional, clear language
- Synthesize information from all provided NOC elements
- Do NOT copy NOC statements verbatim - synthesize and contextualize
- The overview should give a reader a clear understanding of what this job entails"""


def build_user_prompt(statements: List[StatementInput], context: JobContext) -> str:
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

    parts.append("Generate a professional General Overview section (4-6 sentences) for this job description:")

    return "\n".join(parts)


def generate_stream(statements: List[StatementInput], context: JobContext) -> Generator[str, None, None]:
    """
    Stream GPT-4o response token-by-token.

    Yields SSE-formatted data events:
    - "data: <token>\\n\\n" for content tokens
    - "data: [DONE]\\n\\n" on success
    - "data: [ERROR] <message>\\n\\n" on failure
    """
    try:
        system_prompt = build_system_prompt()
        user_prompt = build_user_prompt(statements, context)

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
