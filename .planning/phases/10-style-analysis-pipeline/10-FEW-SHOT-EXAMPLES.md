# Phase 10: Few-Shot Examples from Corpus

**Created:** 2026-02-03
**Source:** Curated from high-quality Government of Canada JD corpus
**Purpose:** Provide exemplar input/output pairs for constrained generation prompts in Phase 12

## Summary Table

| Section | Example Count | Primary Sources | Avg Quality Weight |
|---------|---------------|-----------------|-------------------|
| Key Activities | 6 | DND-AV-60581, DND-PA-58337, JC000947, DND-SH-49480 | 0.93 |
| Skills | 6 | DND-AV-60581, JC000947, JC426, DND-SH-49480 | 0.92 |
| Effort | 5 | DND-AV-60581, DND-SH-49480, JC000947, JC426 | 0.91 |
| Working Conditions | 5 | DND-AV-60581, DND-PA-58337, DND-SH-49480, JC000947 | 0.90 |
| **Total** | **22** | | **0.92** |

---

## Key Activities

### Example 1
- **Section:** key_activities
- **NOC Input:** "Interview clients"
- **Styled Output:** "Provides client services such as: informs clients of various established and routine procedures and requirements, verifies documentation for completeness, accuracy and validity of signatures, and provides related instructions."
- **Source JD:** DND-PA-58337 Procurement Support Assistant
- **Pattern Applied:** verb_first_enumerated
- **Quality Weight:** 0.95

### Example 2
- **Section:** key_activities
- **NOC Input:** "Prepare reports for management"
- **Styled Output:** "Prepares procurement, statistical and financial reports and briefings for management and inputs information and data in order to enable managers to prepare business plans and manage budgets."
- **Source JD:** DND-AV-60581 Base/Wing Procurement Manager
- **Pattern Applied:** verb_first_with_purpose
- **Quality Weight:** 0.95

### Example 3
- **Section:** key_activities
- **NOC Input:** "Conduct training"
- **Styled Output:** "Plans, and leads the delivery of EC security training programs (such as mandatory and enhanced security training and security intelligence training) and associated outreach to EC management and staff at HQ and in the field."
- **Source JD:** JC000947 Security Team Lead
- **Pattern Applied:** verb_first_with_specifics
- **Quality Weight:** 0.93

### Example 4
- **Section:** key_activities
- **NOC Input:** "Advise on policies"
- **Styled Output:** "Advises managers and employees on the application of HR policies, directives, guidelines, standards, processes and procedures to ensure their understanding and support of HR policies and programs or service delivery requirements and compliance with departmental or agency and central agency governance obligations."
- **Source JD:** JC426 Human Resources Advisor PE-02
- **Pattern Applied:** verb_first_with_purpose
- **Quality Weight:** 0.94

### Example 5
- **Section:** key_activities
- **NOC Input:** "Coordinate with other departments"
- **Styled Output:** "Consults with central agencies on the interpretation and application of policies and procedures, and leads or participates in project teams and working groups involved in planning procurement activities to provide input to operational and policy issues."
- **Source JD:** DND-AV-60581 Base/Wing Procurement Manager
- **Pattern Applied:** verb_first_compound
- **Quality Weight:** 0.92

### Example 6
- **Section:** key_activities
- **NOC Input:** "Assess patients"
- **Styled Output:** "Assesses the condition of patients under one's responsibility to plan nursing interventions, provide preventative, curative and palliative care, provide physical and psychological support and keep various documents relative to patients' state up to date."
- **Source JD:** DND-SH-49480 Primary Care Nurse
- **Pattern Applied:** verb_first_with_purpose
- **Quality Weight:** 0.91

---

## Skills

### Example 1
- **Section:** skills
- **NOC Input:** "Knowledge of procurement"
- **Styled Output:** "The work requires knowledge of federal acts and regulations governing procurement, contracting and supply activities, including but not limited to the Financial Administration Act (FAA), the Treasury Board Contracting Policy, Government Contracts Regulations (GCR), to ensure that staff administer assigned procurement and supply activities in accordance with them, to provide interpretations and advice to staff, management and clients, to recommend to clients the best course of action, to identify and develop options for resolving procurement and supply issues and to mediate and resolve contract disputes between clients and suppliers."
- **Source JD:** DND-AV-60581 Base/Wing Procurement Manager
- **Pattern Applied:** work_requires_knowledge
- **Quality Weight:** 0.95

### Example 2
- **Section:** skills
- **NOC Input:** "Communication skills"
- **Styled Output:** "Verbal and written communication skills are required to explain complex procurement, materiel management and financial policies, regulations and procedures to clients, staff, management and suppliers, to provide advice and direction and to provide information to staff on employment policies, performance and work objectives, evaluations and learning plans."
- **Source JD:** DND-AV-60581 Base/Wing Procurement Manager
- **Pattern Applied:** skills_required_to
- **Quality Weight:** 0.94

### Example 3
- **Section:** skills
- **NOC Input:** "Analytical skills"
- **Styled Output:** "Analytical and problem-solving skills and principles, methods, and techniques for conducting threat and risk assessments and analyses, and for developing, recommending, and implementing corrective action plans and strategies to mitigate threats and risks, and to resolve issues that are often complex in nature."
- **Source JD:** JC000947 Security Team Lead
- **Pattern Applied:** skills_required_to
- **Quality Weight:** 0.92

### Example 4
- **Section:** skills
- **NOC Input:** "Knowledge of HR policies"
- **Styled Output:** "Knowledge of the legislation, regulations, policies, guidelines, directives, standards, products and business processes and procedures in the assigned discipline(s) and general knowledge of human resources management policies and operations in the other disciplines is required in order to deliver routine HR management activities within limited delegation and scope."
- **Source JD:** JC426 Human Resources Advisor PE-02
- **Pattern Applied:** knowledge_of_to
- **Quality Weight:** 0.93

### Example 5
- **Section:** skills
- **NOC Input:** "Knowledge of medical procedures"
- **Styled Output:** "Knowledge of the principles of anatomy, physiology, psychology, code of ethics and delegated medical acts to assess patient symptoms during CDU triage activities, to deliver health care services, to assess patient progress and to guide staff members and provide patients with quality preventative and curative care."
- **Source JD:** DND-SH-49480 Primary Care Nurse
- **Pattern Applied:** knowledge_of_to
- **Quality Weight:** 0.90

### Example 6
- **Section:** skills
- **NOC Input:** "Interpersonal skills"
- **Styled Output:** "Skill in interpersonal communications and relationship building is required in order to participate in project teams and in working groups, to consult with clients, to use departmental or agency resources to deliver human resources management services and implement decisions, and to maintain current knowledge of existing and emerging human resources management issues in the federal public service."
- **Source JD:** JC426 Human Resources Advisor PE-02
- **Pattern Applied:** skills_required_to
- **Quality Weight:** 0.91

---

## Effort

### Example 1
- **Section:** effort
- **NOC Input:** "Analyze requirements"
- **Styled Output:** "The provision of procurement and contracting expertise, advice and support to clients requires intellectual effort to analyze client requirements, to research and synthesize information from multiple sources to develop strategies, plans and options to meet objectives, and to recommend to clients the best options to meet objectives and budgetary limitations."
- **Source JD:** DND-AV-60581 Base/Wing Procurement Manager
- **Pattern Applied:** intellectual_effort_to
- **Quality Weight:** 0.95

### Example 2
- **Section:** effort
- **NOC Input:** "Understand and explain regulations"
- **Styled Output:** "Intellectual effort is required to understand, apply and explain Treasury Board (TB) and departmental and other Federal acts, regulations, policies, directives and procedures for clients, staff and managers, to understand and develop options to implement changes to policies, procedures and guidelines and to provide technical procurement expertise."
- **Source JD:** DND-AV-60581 Base/Wing Procurement Manager
- **Pattern Applied:** intellectual_effort_to
- **Quality Weight:** 0.94

### Example 3
- **Section:** effort
- **NOC Input:** "Assess patient conditions"
- **Styled Output:** "Intellectual effort is required to assess patient complaints, conditions and progress and make appropriate referrals based on need."
- **Source JD:** DND-SH-49480 Primary Care Nurse
- **Pattern Applied:** intellectual_effort_to
- **Quality Weight:** 0.90

### Example 4
- **Section:** effort
- **NOC Input:** "Manage staff workload"
- **Styled Output:** "Managing the provision of services by subordinate staff requires intellectual effort to set goals, organizing and assigning work, develop performance measures and take corrective action as necessary."
- **Source JD:** DND-AV-60581 Base/Wing Procurement Manager
- **Pattern Applied:** work_requires_effort
- **Quality Weight:** 0.88

### Example 5
- **Section:** effort
- **NOC Input:** "Deliver HR services"
- **Styled Output:** "Effort is required to deliver human resources management client services (advisory, analytical, operations delivery, investigation and research) in one or more of the HR disciplines, where the supervisor defines the performance expectations and objectives to be reached and provides subject matter assistance, advice and mentoring on new or complex cases."
- **Source JD:** JC426 Human Resources Advisor PE-02
- **Pattern Applied:** effort_required_when
- **Quality Weight:** 0.89

---

## Working Conditions

### Example 1
- **Section:** working_conditions
- **NOC Input:** "Office work"
- **Styled Output:** "The work is performed in an open office environment with resulting daily exposure to office background noise and interruptions."
- **Source JD:** DND-AV-60581 Base/Wing Procurement Manager
- **Pattern Applied:** work_performed_in
- **Quality Weight:** 0.95

### Example 2
- **Section:** working_conditions
- **NOC Input:** "Some travel required"
- **Styled Output:** "The work involves occasional trips to other sites such as warehouses that may result in exposure to fumes, fluctuations of temperature, and noise from the movement of material handling equipment."
- **Source JD:** DND-AV-60581 Base/Wing Procurement Manager
- **Pattern Applied:** work_involves
- **Quality Weight:** 0.92

### Example 3
- **Section:** working_conditions
- **NOC Input:** "Deadline pressure"
- **Styled Output:** "The work involves exposure to a lack of privacy, deadlines, multiple, conflicting and unpredictable demands for services, complaints, as well as a lack of control over workload and pace of work and frequent interruptions from staff or superiors."
- **Source JD:** DND-PA-58337 Procurement Support Assistant
- **Pattern Applied:** work_involves
- **Quality Weight:** 0.90

### Example 4
- **Section:** working_conditions
- **NOC Input:** "Clinical environment"
- **Styled Output:** "The work is carried out in a busy clinic environment where patients present with a variety of psychological and physical ailments. There is a requirement to be empathetic and professional."
- **Source JD:** DND-SH-49480 Primary Care Nurse
- **Pattern Applied:** work_performed_in
- **Quality Weight:** 0.88

### Example 5
- **Section:** working_conditions
- **NOC Input:** "Hybrid work environment"
- **Styled Output:** "The work is performed in a hybrid environment, both from home and onsite at a government office, where there is exposure to distractions and interruptions by managers and staff as well as ambient noise and glare from a video screen."
- **Source JD:** JC000947 Security Team Lead
- **Pattern Applied:** work_performed_in
- **Quality Weight:** 0.87

---

## Usage Guidelines for Prompt Construction

### Optimal Example Count
- **Recommended:** 3-5 examples per section in actual prompts
- **Maximum:** 7 examples (research shows diminishing returns beyond 5)
- **Selection:** Prioritize by quality_weight, ensure variety of patterns

### Example Selection Strategy
1. Always include highest quality_weight examples
2. Mix pattern types (don't use 5x the same pattern)
3. Include variety of job families (admin, technical, healthcare, professional)
4. Avoid over-representation from single source JD

### Quality Weight Interpretation
| Weight | Meaning | Usage |
|--------|---------|-------|
| 0.95+ | Excellent - ideal exemplar | Always include |
| 0.90-0.94 | Very good - strong exemplar | Include for variety |
| 0.85-0.89 | Good - acceptable exemplar | Use when needed for pattern coverage |
| <0.85 | Below threshold | Do not use in production prompts |

### Avoided Sources
The following JD was NOT used for examples (represents baseline output to improve FROM):
- JD-41310.01-Police investigators.pdf (JD Builder Lite output)

---

## Traceability

All examples can be traced to:
1. **Source JD file** - Listed in each example
2. **Pattern from 10-STYLE-PATTERNS.md** - Listed as `pattern_applied`
3. **Quality assessment** - Documented as `quality_weight`

This enables verification that examples match documented patterns and come from appropriate quality sources.

---

*Document complete. Ready for translation to code constants in Plan 02.*
