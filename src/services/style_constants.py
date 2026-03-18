"""
Style constants for JD writing style transfer.

Source: Corpus analysis from Examples of Job Descriptions/
Patterns documented in: .planning/phases/10-style-analysis-pipeline/10-STYLE-PATTERNS.md
Used by: Phase 12 Constrained Generation for few-shot prompts
"""

from typing import Dict, List, TypedDict


class SectionStyle(TypedDict):
    """Type definition for section-specific writing style rules."""
    sentence_structure: str
    verb_tense: str
    perspective: str
    typical_starters: List[str]
    typical_patterns: List[str]


# High-frequency action verbs for Key Activities (appeared in 5+ JDs)
KEY_ACTIVITY_VERBS: List[str] = [
    "Provides",
    "Delivers",
    "Manages",
    "Maintains",
    "Prepares",
    "Reviews",
    "Develops",
    "Coordinates",
    "Participates",
    "Advises",
    "Analyzes",
    "Consults",
    "Ensures",
    "Conducts",
    "Implements",
    "Supports",
    "Assists",
    "Monitors",
    "Evaluates",
    "Plans",
    "Leads",
    "Establishes",
    "Processes",
    "Inputs",
    # Medium-frequency verbs (appeared in 2-4 JDs)
    "Administers",
    "Certifies",
    "Authorizes",
    "Drafts",
    "Investigates",
    "Initiates",
    "Reconciles",
    "Promotes",
    "Collaborates",
    "Assesses",
    "Extracts",
    "Compiles",
    "Receives",
    "Logs",
    "Forwards",
    # Healthcare-specific verbs
    "Performs",
    "Collects",
    "Directs",
    "Exchanges",
    "Offers",
    "Works",
]


# Skills/Knowledge section pattern templates
SKILLS_PATTERNS: List[str] = [
    "Knowledge of {topic} is required to {purpose}.",
    "The work requires knowledge of {topic} to {purpose}.",
    "{Type} skills are required to {action}.",
    "Knowledge is required of {topic_list}.",
    "Knowledge is required of: {detailed_context}.",
    "Verbal and written communication skills are required to {action}.",
    "Analytical skills are required to {action}.",
    "Dexterity and coordination skills are required to {action}.",
    "Skill in {skill_area} is required in order to {purpose}.",
]


# Effort section pattern templates
EFFORT_PATTERNS: List[str] = [
    "Intellectual effort is required to {action}.",
    "Physical effort is required to {action}.",
    "Effort is required to {action} when {condition}.",
    "The work requires {effort_type} to {purpose}.",
    "There is a requirement to {action}.",
    "Psychological and emotional effort is required to {action}.",
    "Sustained attention is required to {action}.",
    "{Context} requires intellectual effort to {action}.",
]


# Working Conditions section pattern templates
WORKING_CONDITIONS_PATTERNS: List[str] = [
    "The work is performed in {environment}.",
    "There is {frequency} exposure to {condition}.",
    "The work involves {activity} in {context}.",
    "There may be {requirement} to {action}.",
    "Daily exposure to {condition}.",
    "The work is carried out in {environment}.",
    "There is exposure to {condition}.",
    "There may be exposure to {condition}.",
]


# Connecting phrases used across all sections
CONNECTING_PHRASES: List[str] = [
    "in order to",
    "to ensure",
    "such as",
    "including but not limited to",
    "in accordance with",
    "to provide",
    "as well as",
    "within delegated authority",
    "in compliance with",
    "to enable",
    "to support",
    "to deliver",
    "to analyze",
    "to assess",
    "to develop",
    "to prepare",
    "to comply with",
]


# Formality transformations (informal -> formal)
FORMALITY_MARKERS: Dict[str, str] = {
    "You need": "The work requires",
    "Should": "is required to",
    "Must": "There is a requirement to",
    "Has to": "is expected to",
    "Does": "{Verb}s",  # Third person
}


# Sentence length guidelines by section
SENTENCE_LENGTH_GUIDELINES: Dict[str, Dict[str, int]] = {
    "key_activities": {"typical_min": 25, "typical_max": 50, "maximum": 75},
    "skills": {"typical_min": 40, "typical_max": 80, "maximum": 120},
    "effort": {"typical_min": 30, "typical_max": 60, "maximum": 90},
    "working_conditions": {"typical_min": 15, "typical_max": 35, "maximum": 50},
}


# Environment descriptors for Working Conditions
ENVIRONMENT_DESCRIPTORS: List[str] = [
    "open office environment",
    "standard office environment",
    "clinic environment",
    "warehouse environment",
    "hybrid environment",
    "busy clinic environment",
]


# Exposure/condition phrases for Working Conditions
EXPOSURE_CONDITIONS: List[str] = [
    "office background noise and interruptions",
    "dust",
    "noxious fumes",
    "noise",
    "fluctuations of temperature",
    "deadlines",
    "multiple and conflicting demands",
    "lack of privacy",
    "complaints",
    "frequent interruptions",
    "distractions",
]


# Effort qualifiers
EFFORT_QUALIFIERS: List[str] = [
    "intellectual",
    "physical",
    "psychological",
    "emotional",
    "sensory",
    "sustained attention",
]


# Main style rules dictionary
STYLE_RULES: Dict[str, SectionStyle] = {
    "key_activities": {
        "sentence_structure": "Verb-first imperative/declarative (observed frequency: ~95%)",
        "verb_tense": "Present tense, third person impersonal",
        "perspective": "Never 'you' or 'I' - always impersonal ('Provides...', not 'You provide...')",
        "typical_starters": [
            "Provides",
            "Delivers",
            "Manages",
            "Maintains",
            "Prepares",
            "Reviews",
            "Develops",
            "Coordinates",
            "Participates",
            "Advises",
            "Analyzes",
            "Consults",
            "Ensures",
            "Conducts",
            "Implements",
            "Supports",
        ],
        "typical_patterns": [
            "{Verb} {object}.",
            "{Verb} {object} to {purpose}.",
            "{Verb} {object}, including {specifics}.",
            "{Verb} and {verb} {object} to {purpose}.",
            "{Verb} {object} such as: {item1}, {item2}, {item3}.",
        ],
    },
    "skills": {
        "sentence_structure": "Knowledge-of statements (observed frequency: ~90%)",
        "verb_tense": "Present tense, impersonal",
        "perspective": "Impersonal ('The work requires...', 'Knowledge of...')",
        "typical_starters": [
            "The work requires knowledge of",
            "Knowledge of",
            "Knowledge is required of",
            "The work requires",
            "Verbal and written communication skills are required to",
            "Analytical skills are required to",
            "Dexterity and coordination skills are required to",
            "Skill in",
        ],
        "typical_patterns": [
            "Knowledge of {topic} is required to {purpose}.",
            "The work requires knowledge of {topic} to {purpose}.",
            "{Type} skills are required to {action}.",
            "Knowledge is required of {topic_list}.",
            "Knowledge is required of: {detailed_context}.",
        ],
    },
    "effort": {
        "sentence_structure": "Requirement statements (observed frequency: ~85%)",
        "verb_tense": "Present tense, impersonal",
        "perspective": "Impersonal",
        "typical_starters": [
            "Intellectual effort is required to",
            "Physical effort is required to",
            "Effort is required to",
            "The work requires",
            "There is a requirement to",
            "Psychological and emotional effort is required to",
            "Sustained attention is required",
        ],
        "typical_patterns": [
            "Intellectual effort is required to {action}.",
            "Physical effort is required to {action}.",
            "Effort is required to {action} when {condition}.",
            "The work requires {effort_type} to {purpose}.",
            "There is a requirement to {action}.",
        ],
    },
    "working_conditions": {
        "sentence_structure": "Environment descriptions (observed frequency: ~100%)",
        "verb_tense": "Present tense, impersonal",
        "perspective": "Impersonal",
        "typical_starters": [
            "The work is performed in",
            "There is exposure to",
            "There may be exposure to",
            "The work involves",
            "Daily exposure to",
            "The work requires",
            "The work is carried out in",
        ],
        "typical_patterns": [
            "The work is performed in {environment}.",
            "There is {frequency} exposure to {condition}.",
            "The work involves {activity} in {context}.",
            "There may be {requirement} to {action}.",
        ],
    },
}


# Anti-patterns to avoid (for validation)
ANTI_PATTERNS: List[str] = [
    "you",
    "your",
    "you will",
    "I",
    "we",
    "our",
    "help out",
    "deal with",
    "get things done",
    "isn't",
    "don't",
    "won't",
    "can't",
    "handle",
    "do",
    "work on",
    "The employee",
]
