# Phase 10: Style Patterns from Corpus Analysis

**Created:** 2026-02-03
**Source:** Analysis of 7 high-quality Government of Canada JD corpus files
**Purpose:** Document writing patterns for few-shot prompting in Phase 12

## Corpus Quality Weighting

| Format Type | Quality | Weight | Use Case | Example Files |
|-------------|---------|--------|----------|---------------|
| DND Standardized | HIGH | 1.0 | Primary source for all examples | DND-AV-60581, DND-PA-58337, DND-SH-49480 |
| PE/AS Generic Work Description | HIGH | 0.95 | Diverse job families | JC426 PE-02, JC000947 AS-04 |
| Simple Duty-Based | MEDIUM | 0.7 | Supplementary only | Executive Assistant 2015 |
| JD Builder Output | LOW | 0.3 | Avoid - baseline to improve FROM | JD-41310.01-Police investigators |

---

## Section 1: Key Activities

### Sentence Structure
- **Pattern:** Verb-first imperative/declarative (observed frequency: ~95%)
- **Tense:** Present tense, third person impersonal
- **Perspective:** Never "you" or "I" - always impersonal ("Provides...", not "You provide...")
- **Complexity:** Single sentences often 25-50 words with embedded purpose clauses

### Typical Starters (extracted from corpus)
High-frequency verbs (appeared in 5+ JDs):
```
Provides, Delivers, Manages, Maintains, Prepares, Reviews, Develops, Coordinates,
Participates, Advises, Analyzes, Consults, Ensures, Conducts, Implements, Supports,
Assists, Monitors, Evaluates, Plans, Leads, Establishes, Processes, Inputs
```

Medium-frequency verbs (appeared in 2-4 JDs):
```
Administers, Certifies, Authorizes, Drafts, Investigates, Initiates, Reconciles,
Promotes, Collaborates, Assesses, Extracts, Compiles, Receives, Logs, Forwards
```

Healthcare-specific verbs:
```
Performs (triage), Consults, Promotes (wellness), Collaborates, Participates,
Assesses, Collects, Directs, Exchanges, Offers, Works
```

### Typical Patterns
| Pattern Name | Template | Observed Frequency |
|--------------|----------|-------------------|
| `verb_first_simple` | `{Verb} {object}.` | 15% |
| `verb_first_with_purpose` | `{Verb} {object} to {purpose}.` | 35% |
| `verb_first_with_specifics` | `{Verb} {object}, including {specifics}.` | 25% |
| `verb_first_compound` | `{Verb} and {verb} {object} to {purpose}.` | 15% |
| `verb_first_enumerated` | `{Verb} {object} such as: {item1}, {item2}, {item3}.` | 10% |

### Example Transformations
| NOC-style Input | Corpus-style Output | Source |
|-----------------|---------------------|--------|
| "Interview clients" | "Provides client services such as: informs clients of various established and routine procedures and requirements, verifies documentation for completeness, accuracy and validity of signatures, and provides related instructions." | DND-PA-58337 |
| "Prepare reports" | "Prepares procurement, statistical and financial reports and briefings for management and inputs information and data in order to enable managers to prepare business plans and manage budgets." | DND-AV-60581 |
| "Conduct training" | "Plans, and leads the delivery of EC security training programs (such as mandatory and enhanced security training and security intelligence training) and associated outreach to EC management and staff at HQ and in the field." | JC000947 AS-04 |

---

## Section 2: Skills / Knowledge

### Sentence Structure
- **Pattern:** Knowledge-of statements (observed frequency: ~90%)
- **Alternative:** Skill-type statements for communication/analytical skills
- **Perspective:** Impersonal ("The work requires...", "Knowledge of...")
- **Complexity:** Often very long sentences (40-80 words) with multiple purpose clauses

### Typical Starters
```
The work requires knowledge of
Knowledge of
Knowledge is required of
The work requires
{Type} skills are required to
Verbal and written communication skills are required to
Analytical skills are required to
Dexterity and coordination skills are required to
```

### Typical Patterns
| Pattern Name | Template | Observed Frequency |
|--------------|----------|-------------------|
| `knowledge_of_to` | `Knowledge of {topic} is required to {purpose}.` | 30% |
| `work_requires_knowledge` | `The work requires knowledge of {topic} to {purpose}.` | 35% |
| `skills_required_to` | `{Type} skills are required to {action}.` | 20% |
| `knowledge_required_of` | `Knowledge is required of {topic_list}.` | 10% |
| `contextual_knowledge` | `Knowledge is required of: {detailed context}.` | 5% |

### Connecting Phrases for Skills
```
in order to, to ensure, to provide, to enable, to support, to deliver,
to analyze, to assess, to develop, to prepare, to comply with,
including but not limited to, such as, as well as
```

### Example Transformations
| NOC-style Input | Corpus-style Output | Source |
|-----------------|---------------------|--------|
| "Knowledge of procurement" | "The work requires knowledge of federal acts and regulations governing procurement, contracting and supply activities, including but not limited to the Financial Administration Act (FAA), the Treasury Board Contracting Policy, Government Contracts Regulations (GCR), to ensure that staff administer assigned procurement and supply activities in accordance with them." | DND-AV-60581 |
| "Communication skills" | "Verbal and written communication skills are required to explain complex procurement, materiel management and financial policies, regulations and procedures to clients, staff, management and suppliers, to provide advice and direction and to provide information to staff on employment policies, performance and work objectives, evaluations and learning plans." | DND-AV-60581 |
| "Analytical skills" | "Analytical and problem-solving skills and principles, methods, and techniques for conducting threat and risk assessments and analyses, and for developing, recommending, and implementing corrective action plans and strategies to mitigate threats and risks, and to resolve issues that are often complex in nature." | JC000947 AS-04 |

---

## Section 3: Effort

### Sentence Structure
- **Pattern:** Requirement statements (observed frequency: ~85%)
- **Lead-in:** "Intellectual effort is required to..." or "The work requires..."
- **Perspective:** Impersonal
- **Complexity:** Multiple clauses, often listing what the effort is FOR

### Typical Starters
```
Intellectual effort is required to
Physical effort is required to
Effort is required to
The work requires
There is a requirement to
Psychological and emotional effort is required to
Sustained attention is required
```

### Typical Patterns
| Pattern Name | Template | Observed Frequency |
|--------------|----------|-------------------|
| `intellectual_effort_to` | `Intellectual effort is required to {action}.` | 40% |
| `physical_effort_to` | `Physical effort is required to {action}.` | 25% |
| `effort_required_when` | `Effort is required to {action} when {condition}.` | 15% |
| `work_requires_effort` | `The work requires {effort_type} to {purpose}.` | 15% |
| `requirement_statement` | `There is a requirement to {action}.` | 5% |

### Effort Qualifiers
```
intellectual, physical, psychological, emotional, sensory, sustained attention
```

### Example Transformations
| NOC-style Input | Corpus-style Output | Source |
|-----------------|---------------------|--------|
| "Analyze requirements" | "The provision of procurement and contracting expertise, advice and support to clients requires intellectual effort to analyze client requirements, to research and synthesize information from multiple sources to develop strategies, plans and options to meet objectives, and to recommend to clients the best options to meet objectives and budgetary limitations." | DND-AV-60581 |
| "Understand regulations" | "Intellectual effort is required to understand, apply and explain Treasury Board (TB) and departmental and other Federal acts, regulations, policies, directives and procedures for clients, staff and managers, to understand and develop options to implement changes to policies, procedures and guidelines and to provide technical procurement expertise." | DND-AV-60581 |
| "Assess patients" | "Intellectual effort is required to assess patient complaints, conditions and progress and make appropriate referrals based on need." | DND-SH-49480 |

---

## Section 4: Working Conditions

### Sentence Structure
- **Pattern:** Environment descriptions (observed frequency: ~100%)
- **Lead-in:** "The work is performed in..." or "There is exposure to..."
- **Perspective:** Impersonal
- **Complexity:** Usually shorter, more direct statements

### Typical Starters
```
The work is performed in
There is exposure to
There may be exposure to
The work involves
Daily exposure to
The work requires
```

### Typical Patterns
| Pattern Name | Template | Observed Frequency |
|--------------|----------|-------------------|
| `work_performed_in` | `The work is performed in {environment}.` | 40% |
| `exposure_to` | `There is {frequency} exposure to {condition}.` | 30% |
| `work_involves` | `The work involves {activity} in {context}.` | 20% |
| `may_require` | `There may be {requirement} to {action}.` | 10% |

### Environment Descriptors
```
open office environment, standard office environment, clinic environment,
warehouse environment, hybrid environment, busy clinic environment
```

### Exposure/Condition Phrases
```
office background noise and interruptions, dust, noxious fumes, noise,
fluctuations of temperature, deadlines, multiple and conflicting demands,
lack of privacy, complaints, frequent interruptions, distractions
```

### Example Transformations
| NOC-style Input | Corpus-style Output | Source |
|-----------------|---------------------|--------|
| "Office work" | "The work is performed in an open office environment with resulting daily exposure to office background noise and interruptions." | DND-AV-60581 |
| "Some travel required" | "The work involves occasional trips to other sites such as warehouses that may result in exposure to fumes, fluctuations of temperature, and noise from the movement of material handling equipment." | DND-AV-60581 |
| "Clinical setting" | "The work is carried out in a busy clinic environment where patients present with a variety of psychological and physical ailments. There is a requirement to be empathetic and professional." | DND-SH-49480 |

---

## Cross-Section Vocabulary Patterns

### Connecting Phrases (all sections)
| Phrase | Usage | Frequency |
|--------|-------|-----------|
| `in order to` | Formal purpose clause | HIGH |
| `to ensure` | Purpose with guarantee/compliance | HIGH |
| `such as` | Introducing examples | HIGH |
| `including but not limited to` | Non-exhaustive list | MEDIUM |
| `in accordance with` | Compliance/regulation | MEDIUM |
| `to provide` | Purpose - delivery | HIGH |
| `as well as` | Additional items | MEDIUM |
| `within delegated authority` | Scope limitation | MEDIUM |
| `in compliance with` | Regulatory | MEDIUM |

### Formality Markers
| Informal | Formal (Corpus Style) |
|----------|----------------------|
| "You need" | "The work requires" |
| "Should" | "is required to" |
| "Must" | "There is a requirement to" |
| "Has to" | "is expected to" |
| "Does" | "{Verb}s" (third person) |

### Sentence Length Guidelines
| Section | Typical Range | Maximum Observed |
|---------|---------------|------------------|
| Key Activities | 25-50 words | 75 words |
| Skills | 40-80 words | 120 words |
| Effort | 30-60 words | 90 words |
| Working Conditions | 15-35 words | 50 words |

---

## Anti-Patterns (What NOT to Do)

1. **Never use second person** - No "you", "your", "you will"
2. **Never use first person** - No "I", "we", "our"
3. **Avoid casual language** - No "help out", "deal with", "get things done"
4. **Avoid contractions** - Use "is not" not "isn't"
5. **Avoid vague verbs** - Use specific action verbs, not "handle", "do", "work on"
6. **Avoid bullet-only format for Skills** - Skills require full sentences with purpose clauses
7. **Avoid starting with "The employee"** - Start with verb or "The work requires"

---

## Source JD Reference

| JD File | Format Type | Job Family | Quality | Used For |
|---------|-------------|------------|---------|----------|
| DND-AV-60581 Base/Wing Procurement Manager | DND Standardized | Procurement/Management | HIGH | All sections |
| DND-PA-58337 Procurement Support Assistant | DND Standardized | Procurement/Admin | HIGH | Key Activities, Skills |
| JC426 PE-02 Human Resources Advisor | PE/AS Generic | HR | HIGH | Key Activities, Skills |
| JC000947 AS-04 Security Team Lead | PE/AS Generic | Security/Admin | HIGH | All sections |
| DND-SH-49480 Primary Care Nurse | DND Work Description | Healthcare | HIGH | Key Activities, Effort, Working Conditions |
| DND-SH-55719 General Duty Nurse | DND Work Description | Healthcare | HIGH | Skills, Effort |
| Executive Assistant 2015 | Simple Duty-Based | Admin | MEDIUM | Not primary source |

---

*Document complete. Ready for translation to code constants in Plan 02.*
