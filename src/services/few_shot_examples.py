"""
Few-shot examples for JD style transfer prompts.

Source: Curated from Examples of Job Descriptions/
Examples documented in: .planning/phases/10-style-analysis-pipeline/10-FEW-SHOT-EXAMPLES.md
Used by: Phase 12 Constrained Generation for few-shot prompt construction
"""

from typing import Dict, List, TypedDict


class FewShotExample(TypedDict):
    """Type definition for a few-shot example."""
    section: str
    noc_input: str
    styled_output: str
    source_jd: str
    pattern_applied: str
    quality_weight: float


# Key Activities examples (6 examples)
FEW_SHOT_KEY_ACTIVITIES: List[FewShotExample] = [
    {
        "section": "key_activities",
        "noc_input": "Interview clients",
        "styled_output": "Provides client services such as: informs clients of various established and routine procedures and requirements, verifies documentation for completeness, accuracy and validity of signatures, and provides related instructions.",
        "source_jd": "DND-PA-58337 Procurement Support Assistant",
        "pattern_applied": "verb_first_enumerated",
        "quality_weight": 0.95,
    },
    {
        "section": "key_activities",
        "noc_input": "Prepare reports for management",
        "styled_output": "Prepares procurement, statistical and financial reports and briefings for management and inputs information and data in order to enable managers to prepare business plans and manage budgets.",
        "source_jd": "DND-AV-60581 Base/Wing Procurement Manager",
        "pattern_applied": "verb_first_with_purpose",
        "quality_weight": 0.95,
    },
    {
        "section": "key_activities",
        "noc_input": "Conduct training",
        "styled_output": "Plans, and leads the delivery of EC security training programs (such as mandatory and enhanced security training and security intelligence training) and associated outreach to EC management and staff at HQ and in the field.",
        "source_jd": "JC000947 Security Team Lead",
        "pattern_applied": "verb_first_with_specifics",
        "quality_weight": 0.93,
    },
    {
        "section": "key_activities",
        "noc_input": "Advise on policies",
        "styled_output": "Advises managers and employees on the application of HR policies, directives, guidelines, standards, processes and procedures to ensure their understanding and support of HR policies and programs or service delivery requirements and compliance with departmental or agency and central agency governance obligations.",
        "source_jd": "JC426 Human Resources Advisor PE-02",
        "pattern_applied": "verb_first_with_purpose",
        "quality_weight": 0.94,
    },
    {
        "section": "key_activities",
        "noc_input": "Coordinate with other departments",
        "styled_output": "Consults with central agencies on the interpretation and application of policies and procedures, and leads or participates in project teams and working groups involved in planning procurement activities to provide input to operational and policy issues.",
        "source_jd": "DND-AV-60581 Base/Wing Procurement Manager",
        "pattern_applied": "verb_first_compound",
        "quality_weight": 0.92,
    },
    {
        "section": "key_activities",
        "noc_input": "Assess patients",
        "styled_output": "Assesses the condition of patients under one's responsibility to plan nursing interventions, provide preventative, curative and palliative care, provide physical and psychological support and keep various documents relative to patients' state up to date.",
        "source_jd": "DND-SH-49480 Primary Care Nurse",
        "pattern_applied": "verb_first_with_purpose",
        "quality_weight": 0.91,
    },
]


# Skills examples (6 examples)
FEW_SHOT_SKILLS: List[FewShotExample] = [
    {
        "section": "skills",
        "noc_input": "Knowledge of procurement",
        "styled_output": "The work requires knowledge of federal acts and regulations governing procurement, contracting and supply activities, including but not limited to the Financial Administration Act (FAA), the Treasury Board Contracting Policy, Government Contracts Regulations (GCR), to ensure that staff administer assigned procurement and supply activities in accordance with them, to provide interpretations and advice to staff, management and clients, to recommend to clients the best course of action, to identify and develop options for resolving procurement and supply issues and to mediate and resolve contract disputes between clients and suppliers.",
        "source_jd": "DND-AV-60581 Base/Wing Procurement Manager",
        "pattern_applied": "work_requires_knowledge",
        "quality_weight": 0.95,
    },
    {
        "section": "skills",
        "noc_input": "Communication skills",
        "styled_output": "Verbal and written communication skills are required to explain complex procurement, materiel management and financial policies, regulations and procedures to clients, staff, management and suppliers, to provide advice and direction and to provide information to staff on employment policies, performance and work objectives, evaluations and learning plans.",
        "source_jd": "DND-AV-60581 Base/Wing Procurement Manager",
        "pattern_applied": "skills_required_to",
        "quality_weight": 0.94,
    },
    {
        "section": "skills",
        "noc_input": "Analytical skills",
        "styled_output": "Analytical and problem-solving skills and principles, methods, and techniques for conducting threat and risk assessments and analyses, and for developing, recommending, and implementing corrective action plans and strategies to mitigate threats and risks, and to resolve issues that are often complex in nature.",
        "source_jd": "JC000947 Security Team Lead",
        "pattern_applied": "skills_required_to",
        "quality_weight": 0.92,
    },
    {
        "section": "skills",
        "noc_input": "Knowledge of HR policies",
        "styled_output": "Knowledge of the legislation, regulations, policies, guidelines, directives, standards, products and business processes and procedures in the assigned discipline(s) and general knowledge of human resources management policies and operations in the other disciplines is required in order to deliver routine HR management activities within limited delegation and scope.",
        "source_jd": "JC426 Human Resources Advisor PE-02",
        "pattern_applied": "knowledge_of_to",
        "quality_weight": 0.93,
    },
    {
        "section": "skills",
        "noc_input": "Knowledge of medical procedures",
        "styled_output": "Knowledge of the principles of anatomy, physiology, psychology, code of ethics and delegated medical acts to assess patient symptoms during CDU triage activities, to deliver health care services, to assess patient progress and to guide staff members and provide patients with quality preventative and curative care.",
        "source_jd": "DND-SH-49480 Primary Care Nurse",
        "pattern_applied": "knowledge_of_to",
        "quality_weight": 0.90,
    },
    {
        "section": "skills",
        "noc_input": "Interpersonal skills",
        "styled_output": "Skill in interpersonal communications and relationship building is required in order to participate in project teams and in working groups, to consult with clients, to use departmental or agency resources to deliver human resources management services and implement decisions, and to maintain current knowledge of existing and emerging human resources management issues in the federal public service.",
        "source_jd": "JC426 Human Resources Advisor PE-02",
        "pattern_applied": "skills_required_to",
        "quality_weight": 0.91,
    },
]


# Effort examples (5 examples)
FEW_SHOT_EFFORT: List[FewShotExample] = [
    {
        "section": "effort",
        "noc_input": "Analyze requirements",
        "styled_output": "The provision of procurement and contracting expertise, advice and support to clients requires intellectual effort to analyze client requirements, to research and synthesize information from multiple sources to develop strategies, plans and options to meet objectives, and to recommend to clients the best options to meet objectives and budgetary limitations.",
        "source_jd": "DND-AV-60581 Base/Wing Procurement Manager",
        "pattern_applied": "intellectual_effort_to",
        "quality_weight": 0.95,
    },
    {
        "section": "effort",
        "noc_input": "Understand and explain regulations",
        "styled_output": "Intellectual effort is required to understand, apply and explain Treasury Board (TB) and departmental and other Federal acts, regulations, policies, directives and procedures for clients, staff and managers, to understand and develop options to implement changes to policies, procedures and guidelines and to provide technical procurement expertise.",
        "source_jd": "DND-AV-60581 Base/Wing Procurement Manager",
        "pattern_applied": "intellectual_effort_to",
        "quality_weight": 0.94,
    },
    {
        "section": "effort",
        "noc_input": "Assess patient conditions",
        "styled_output": "Intellectual effort is required to assess patient complaints, conditions and progress and make appropriate referrals based on need.",
        "source_jd": "DND-SH-49480 Primary Care Nurse",
        "pattern_applied": "intellectual_effort_to",
        "quality_weight": 0.90,
    },
    {
        "section": "effort",
        "noc_input": "Manage staff workload",
        "styled_output": "Managing the provision of services by subordinate staff requires intellectual effort to set goals, organizing and assigning work, develop performance measures and take corrective action as necessary.",
        "source_jd": "DND-AV-60581 Base/Wing Procurement Manager",
        "pattern_applied": "work_requires_effort",
        "quality_weight": 0.88,
    },
    {
        "section": "effort",
        "noc_input": "Deliver HR services",
        "styled_output": "Effort is required to deliver human resources management client services (advisory, analytical, operations delivery, investigation and research) in one or more of the HR disciplines, where the supervisor defines the performance expectations and objectives to be reached and provides subject matter assistance, advice and mentoring on new or complex cases.",
        "source_jd": "JC426 Human Resources Advisor PE-02",
        "pattern_applied": "effort_required_when",
        "quality_weight": 0.89,
    },
]


# Working Conditions examples (5 examples)
FEW_SHOT_WORKING_CONDITIONS: List[FewShotExample] = [
    {
        "section": "working_conditions",
        "noc_input": "Office work",
        "styled_output": "The work is performed in an open office environment with resulting daily exposure to office background noise and interruptions.",
        "source_jd": "DND-AV-60581 Base/Wing Procurement Manager",
        "pattern_applied": "work_performed_in",
        "quality_weight": 0.95,
    },
    {
        "section": "working_conditions",
        "noc_input": "Some travel required",
        "styled_output": "The work involves occasional trips to other sites such as warehouses that may result in exposure to fumes, fluctuations of temperature, and noise from the movement of material handling equipment.",
        "source_jd": "DND-AV-60581 Base/Wing Procurement Manager",
        "pattern_applied": "work_involves",
        "quality_weight": 0.92,
    },
    {
        "section": "working_conditions",
        "noc_input": "Deadline pressure",
        "styled_output": "The work involves exposure to a lack of privacy, deadlines, multiple, conflicting and unpredictable demands for services, complaints, as well as a lack of control over workload and pace of work and frequent interruptions from staff or superiors.",
        "source_jd": "DND-PA-58337 Procurement Support Assistant",
        "pattern_applied": "work_involves",
        "quality_weight": 0.90,
    },
    {
        "section": "working_conditions",
        "noc_input": "Clinical environment",
        "styled_output": "The work is carried out in a busy clinic environment where patients present with a variety of psychological and physical ailments. There is a requirement to be empathetic and professional.",
        "source_jd": "DND-SH-49480 Primary Care Nurse",
        "pattern_applied": "work_performed_in",
        "quality_weight": 0.88,
    },
    {
        "section": "working_conditions",
        "noc_input": "Hybrid work environment",
        "styled_output": "The work is performed in a hybrid environment, both from home and onsite at a government office, where there is exposure to distractions and interruptions by managers and staff as well as ambient noise and glare from a video screen.",
        "source_jd": "JC000947 Security Team Lead",
        "pattern_applied": "work_performed_in",
        "quality_weight": 0.87,
    },
]


# Aggregate dictionary for all examples
ALL_FEW_SHOT_EXAMPLES: Dict[str, List[FewShotExample]] = {
    "key_activities": FEW_SHOT_KEY_ACTIVITIES,
    "skills": FEW_SHOT_SKILLS,
    "effort": FEW_SHOT_EFFORT,
    "working_conditions": FEW_SHOT_WORKING_CONDITIONS,
}


def get_few_shot_prompt(section: str, n_examples: int = 3) -> str:
    """
    Build few-shot prompt section for a given JD element.

    Args:
        section: One of 'key_activities', 'skills', 'effort', 'working_conditions'
        n_examples: Number of examples to include (default 3, max 5 recommended)

    Returns:
        Formatted string with NOC Input / Styled Output pairs
    """
    examples = ALL_FEW_SHOT_EXAMPLES.get(section, [])[:n_examples]

    prompt_parts = []
    for ex in examples:
        prompt_parts.append(f"NOC Input: {ex['noc_input']}")
        prompt_parts.append(f"Styled Output: {ex['styled_output']}")
        prompt_parts.append("")

    return "\n".join(prompt_parts)


def get_high_quality_examples(section: str, min_weight: float = 0.85) -> List[FewShotExample]:
    """
    Get examples above a quality weight threshold.

    Args:
        section: One of 'key_activities', 'skills', 'effort', 'working_conditions'
        min_weight: Minimum quality weight threshold (default 0.85)

    Returns:
        List of FewShotExample dicts with quality_weight >= min_weight
    """
    examples = ALL_FEW_SHOT_EXAMPLES.get(section, [])
    return [ex for ex in examples if ex["quality_weight"] >= min_weight]


def get_examples_by_pattern(section: str, pattern: str) -> List[FewShotExample]:
    """
    Get examples that use a specific pattern.

    Args:
        section: One of 'key_activities', 'skills', 'effort', 'working_conditions'
        pattern: Pattern name (e.g., 'verb_first_with_purpose', 'knowledge_of_to')

    Returns:
        List of FewShotExample dicts that apply the specified pattern
    """
    examples = ALL_FEW_SHOT_EXAMPLES.get(section, [])
    return [ex for ex in examples if ex["pattern_applied"] == pattern]
