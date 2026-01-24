# Phase 08-C: Profile Page Tabs - Research

**Researched:** 2026-01-24
**Domain:** Flask/Jinja2 templates with vanilla JavaScript ARIA tabs, LLM-driven icon selection
**Confidence:** HIGH

## Summary

Phase 08-C redesigns the Step 9 profile page with three main technical challenges: (1) implementing ARIA-compliant horizontal tabs to replace current accordion pattern, (2) integrating LLM-driven icon selection based on NOC minor group descriptions, and (3) generating contextual occupation descriptions via LLM.

The application already has LLM integration via OpenAI client for job description generation. We'll extend this with a new prompt for icon selection and occupation description. The tab implementation follows W3C ARIA Authoring Practices Guide patterns with vanilla JavaScript for state management and keyboard navigation.

**Primary recommendation:** Build server-side tab structure with Jinja2 templates, implement client-side ARIA tab pattern with focus management, extend existing LLM service with two new endpoints (icon selection + occupation description).

## Standard Stack

### Core (Already in Application)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Flask | Current | Backend templating | Already used for all routes |
| Jinja2 | Current | HTML rendering | Built into Flask, used throughout app |
| OpenAI Python | Current | LLM integration | Already integrated in llm_service.py |
| Vanilla JavaScript | ES6+ | Tab interaction | Current pattern, no new dependencies |
| Font Awesome | 5.x or 6.x | Icon library | Already referenced in OaSIS HTML |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Bootstrap Grid | 4.x/5.x | Layout structure | For responsive blue banner matching OaSIS |
| BeautifulSoup | Current | Minor group description extraction | If scraping minor group text from OaSIS hierarchy |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Vanilla JS tabs | React/Vue tabs | Would require new build toolchain; current stack is vanilla JS |
| OpenAI | Anthropic Claude | App already uses OpenAI; switching requires config changes |
| Font Awesome | SVG sprite | FA already used in OaSIS reference; consistency matters more |

**Installation:**
No new packages required. All dependencies already in environment.

## Architecture Patterns

### Recommended Project Structure

```
templates/
├── profile.html              # New profile page template (Step 9)
└── components/
    ├── profile_header.html   # Header with icon, badge, description
    └── profile_tabs.html     # Tab navigation component

static/js/
├── profile_tabs.js           # NEW: ARIA tab controller
└── api.js                    # EXTEND: Add icon + description endpoints

src/routes/
└── api.py                    # EXTEND: Add /api/icon, /api/occupation-description

src/services/
└── llm_service.py            # EXTEND: Add icon selection + description generation
```

### Pattern 1: ARIA Tab Panel with Automatic Activation

**What:** Horizontal tabs with arrow key navigation and automatic panel switching
**When to use:** Profile page tabs where content is pre-loaded and switching is instant

**Example:**
```javascript
// Source: W3C ARIA Authoring Practices Guide
class TabController {
    constructor(tablistEl) {
        this.tablist = tablistEl;
        this.tabs = Array.from(tablistEl.querySelectorAll('[role="tab"]'));
        this.panels = this.tabs.map(tab =>
            document.getElementById(tab.getAttribute('aria-controls'))
        );

        // Bind keyboard handlers
        this.tablist.addEventListener('keydown', this.onKeydown.bind(this));
        this.tabs.forEach((tab, i) => {
            tab.addEventListener('click', () => this.activateTab(i));
        });

        // Set initial state
        this.activateTab(0);
    }

    onKeydown(event) {
        const currentIndex = this.tabs.indexOf(document.activeElement);
        let targetIndex = currentIndex;

        switch(event.key) {
            case 'ArrowRight':
                targetIndex = (currentIndex + 1) % this.tabs.length;
                break;
            case 'ArrowLeft':
                targetIndex = currentIndex === 0 ?
                    this.tabs.length - 1 : currentIndex - 1;
                break;
            case 'Home':
                targetIndex = 0;
                break;
            case 'End':
                targetIndex = this.tabs.length - 1;
                break;
            default:
                return;
        }

        event.preventDefault();
        this.activateTab(targetIndex);
        this.tabs[targetIndex].focus();
    }

    activateTab(index) {
        // Update aria-selected
        this.tabs.forEach((tab, i) => {
            tab.setAttribute('aria-selected', i === index);
            tab.setAttribute('tabindex', i === index ? '0' : '-1');
        });

        // Show/hide panels
        this.panels.forEach((panel, i) => {
            panel.hidden = i !== index;
        });
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    const tablist = document.querySelector('[role="tablist"]');
    if (tablist) new TabController(tablist);
});
```

### Pattern 2: LLM Structured Output for Icon Selection

**What:** Prompt LLM to select best-matching icon from predefined list based on occupation description
**When to use:** Icon selection needs semantic matching beyond keyword lookup

**Example:**
```python
# Source: OpenAI Best Practices for Prompt Engineering
def select_icon_for_occupation(minor_group_description: str) -> str:
    """Select Font Awesome icon class based on minor group description."""

    # Curated icon mapping for NOC broad categories
    ICON_OPTIONS = {
        "legislative": "fa-landmark",
        "management": "fa-users-cog",
        "business": "fa-briefcase",
        "finance": "fa-chart-line",
        "sciences": "fa-atom",
        "health": "fa-heartbeat",
        "education": "fa-graduation-cap",
        "law": "fa-balance-scale",
        "arts": "fa-palette",
        "sports": "fa-running",
        "sales": "fa-handshake",
        "transport": "fa-truck",
        "agriculture": "fa-tractor",
        "manufacturing": "fa-industry",
        "default": "fa-briefcase"
    }

    system_prompt = """You are an icon selection expert. Given an occupation description,
select the SINGLE most appropriate Font Awesome icon class from the provided list.

Return ONLY the icon class name (e.g., "fa-atom"). No explanation."""

    user_prompt = f"""Occupation: {minor_group_description}

Available icons:
{chr(10).join(f'- {name}: {icon}' for name, icon in ICON_OPTIONS.items())}

Select the most semantically appropriate icon class:"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0,  # Deterministic selection
        max_tokens=20
    )

    icon_class = response.choices[0].message.content.strip()

    # Validate response is in allowed set
    if icon_class not in ICON_OPTIONS.values():
        return ICON_OPTIONS["default"]

    return icon_class
```

### Pattern 3: Server-Side Tab Content Mapping

**What:** Map OaSIS categories to JD element tabs server-side before rendering
**When to use:** Tab content structure is deterministic based on phase requirements

**Example:**
```python
# Source: Flask/Jinja2 template patterns
def build_tab_structure(profile_data: dict) -> dict:
    """Map OaSIS categories to tab structure."""

    return {
        "overview": {
            "label": "Overview",
            "sections": [
                {"title": "Also Known As", "content": profile_data['also_known_as']},
                {"title": "Core Competencies", "content": profile_data['core_competencies']},
                {"title": "Main Duties", "content": profile_data['main_duties']},
                {"title": "NOC Hierarchy", "content": profile_data['noc_hierarchy']}
            ]
        },
        "key_activities": {
            "label": "Key Activities",
            "sections": [
                {"title": "Main Duties", "content": profile_data['main_duties']},
                {"title": "Work Activities", "content": profile_data['work_activities']}
            ]
        },
        "skills": {
            "label": "Skills",
            "sections": [
                {"title": "Skills", "content": profile_data['skills']},
                {"title": "Abilities", "content": profile_data['abilities']},
                {"title": "Knowledge", "content": profile_data['knowledge']}
            ]
        },
        "effort": {
            "label": "Effort",
            "sections": [
                {"title": "Work Context - Effort",
                 "content": filter_work_context(profile_data['work_context'], 'effort')}
            ]
        },
        "responsibility": {
            "label": "Responsibility",
            "sections": [
                {"title": "Work Context - Responsibility",
                 "content": filter_work_context(profile_data['work_context'],
                                                ['responsib', 'decision'])}
            ]
        },
        "career": {
            "label": "Feeder Group Mobility & Career Progression",
            "sections": [
                {"title": "Career Progression",
                 "content": profile_data['additional_info']}
            ]
        }
    }

def filter_work_context(work_context: list, keywords: str | list) -> list:
    """Filter work context items by keyword match."""
    if isinstance(keywords, str):
        keywords = [keywords]

    return [
        item for item in work_context
        if any(kw.lower() in item['text'].lower() for kw in keywords)
    ]
```

### Anti-Patterns to Avoid

- **Accordion converted to tabs without ARIA updates:** Don't reuse `<details>` elements; tabs require explicit `role="tab"` and `role="tabpanel"`
- **Tab activation without focus management:** Arrow keys must move focus, not just visual selection
- **Inline onclick handlers:** Use event delegation and proper event listeners for accessibility
- **Hard-coded icon classes:** Icon should be data-driven from backend, not static in template

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| ARIA tab keyboard navigation | Custom arrow key handler | W3C APG pattern implementation | Handles edge cases (Home/End, wrapping, focus trap) |
| Icon selection logic | Rule-based keyword matching | LLM structured output | Handles semantic similarity, new occupation types |
| Tab content visibility | Manual CSS classes | `hidden` attribute + ARIA | Screen readers respect `hidden`, CSS can be overridden |
| Tab state persistence | Custom localStorage wrapper | Existing state.js pattern | App already has state management for selections |

**Key insight:** ARIA patterns are deceptively complex. Focus management, announcement timing, and keyboard traps require exact implementation of W3C patterns. Don't improvise.

## Common Pitfalls

### Pitfall 1: Tab Content Not Pre-Loaded

**What goes wrong:** User switches tabs, sees loading spinner or empty panel
**Why it happens:** Assuming lazy-loading is needed when all data is already fetched in profile API call
**How to avoid:** Render all tab panels in initial HTML with `hidden` attribute. Profile data is already complete from `/api/profile` endpoint.
**Warning signs:** JavaScript fetches data on tab click; panels show skeleton screens

### Pitfall 2: Incorrect tabindex Management

**What goes wrong:** Tab key skips tabs, or gets stuck in tab list
**Why it happens:** All tabs set to `tabindex="0"` instead of roving tabindex pattern
**How to avoid:**
- Active tab: `tabindex="0"`
- Inactive tabs: `tabindex="-1"`
- Update on arrow key navigation
**Warning signs:** Keyboard users can't reach content after tabs; Tab key cycles through all tab buttons

### Pitfall 3: LLM Icon Hallucination

**What goes wrong:** LLM returns invalid icon class like "fa-data-scientist" (doesn't exist)
**Why it happens:** LLM generates plausible-sounding but non-existent icon names
**How to avoid:**
- Provide explicit allowed list in prompt
- Validate response against allowed set
- Fallback to default icon (fa-briefcase) on invalid response
**Warning signs:** Console errors "icon not found"; blank icon space in header

### Pitfall 4: Mixing Accordion and Tab Semantics

**What goes wrong:** Existing accordion JavaScript interferes with tab behavior
**Why it happens:** Both use keyboard interaction and expand/collapse patterns
**How to avoid:**
- Use separate JavaScript modules (accordion.js for Step 10 sections, profile_tabs.js for Step 9)
- Don't apply accordion event listeners to tab elements
- Use different HTML structure (tabs use `<ul>` with `role="tablist"`, not `<details>`)
**Warning signs:** Tabs expand/collapse instead of switching; exclusive accordion behavior on tabs

### Pitfall 5: Missing Leading Statement

**What goes wrong:** Profile shows title and description but not the leading statement from OaSIS
**Why it happens:** Confusing LLM-generated description with scraped leading statement
**How to avoid:**
- Leading statement = short sentence from OaSIS (already scraped)
- LLM description = generated paragraph describing occupation
- Display BOTH in header (leading statement first, then LLM paragraph)
**Warning signs:** User sees only AI-generated text, no authoritative OaSIS statement

## Code Examples

Verified patterns from official sources:

### ARIA Tab HTML Structure

```html
<!-- Source: W3C ARIA Authoring Practices Guide -->
<div class="profile-header blueBG">
    <div class="container">
        <div class="row">
            <div class="col-md-8">
                <h2 class="profile-title">{{ title }}</h2>
                <span class="oasis-code-badge">{{ noc_code }}</span>
                <p class="leading-statement">{{ leading_statement }}</p>
                <p class="occupation-description">{{ llm_description }}</p>
            </div>
            <div class="col-md-4 text-center">
                <i class="fa-9x fas {{ icon_class }}" aria-hidden="true"></i>
            </div>
        </div>
    </div>
</div>

<div class="tabs-container">
    <ul class="tabs-bar-lg" role="tablist" aria-label="Job description sections">
        <li role="presentation">
            <button role="tab"
                    id="tab-overview"
                    aria-selected="true"
                    aria-controls="panel-overview"
                    tabindex="0">
                Overview
            </button>
        </li>
        <li role="presentation">
            <button role="tab"
                    id="tab-activities"
                    aria-selected="false"
                    aria-controls="panel-activities"
                    tabindex="-1">
                Key Activities
            </button>
        </li>
        <!-- More tabs... -->
    </ul>

    <div id="panel-overview" role="tabpanel" aria-labelledby="tab-overview" tabindex="0">
        <!-- Overview content sections -->
    </div>
    <div id="panel-activities" role="tabpanel" aria-labelledby="tab-activities" hidden tabindex="0">
        <!-- Key Activities content -->
    </div>
    <!-- More panels... -->
</div>
```

### LLM Occupation Description Prompt

```python
# Source: Existing llm_service.py pattern, adapted for description generation
def generate_occupation_description(
    occupation_title: str,
    minor_group_description: str,
    main_duties: list[str]
) -> str:
    """Generate contextual occupation description for profile header."""

    system_prompt = """You are an expert HR consultant specializing in Canadian occupations.
Generate a concise, professional paragraph (3-4 sentences, ~100 words) describing what
this occupation involves based on NOC data.

Guidelines:
- Write in third person present tense
- Focus on what workers in this occupation DO
- Synthesize minor group context with specific duties
- Use professional, accessible language
- Do NOT copy NOC text verbatim - contextualize and synthesize"""

    user_prompt = f"""Occupation: {occupation_title}

Context: {minor_group_description}

Key duties:
{chr(10).join(f'- {duty}' for duty in main_duties[:5])}

Generate a professional description paragraph:"""

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3,  # Slight creativity while staying factual
        max_tokens=150
    )

    return response.choices[0].message.content.strip()
```

### Tab Content Filtering (Work Context)

```python
# Source: Phase requirements for Effort/Responsibility tab filtering
def filter_work_context_by_dimension(work_context: list, dimension_filter: str | list) -> list:
    """Filter work context items for Effort or Responsibility tabs.

    Args:
        work_context: List of work context items with 'text' and optional 'dimension_type'
        dimension_filter: Single keyword or list of keywords to match

    Returns:
        Filtered list of work context items
    """
    if isinstance(dimension_filter, str):
        dimension_filter = [dimension_filter]

    filtered = []
    for item in work_context:
        # Check if text contains any of the filter keywords (case-insensitive)
        text_lower = item.get('text', '').lower()
        dimension_lower = item.get('dimension_type', '').lower()

        if any(
            keyword.lower() in text_lower or keyword.lower() in dimension_lower
            for keyword in dimension_filter
        ):
            filtered.append(item)

    return filtered

# Usage in route:
effort_items = filter_work_context_by_dimension(profile['work_context'], 'effort')
responsibility_items = filter_work_context_by_dimension(
    profile['work_context'],
    ['responsib', 'decision']
)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `<details>` accordion | ARIA tabs with `role="tablist"` | W3C ARIA 1.2 (2021) | Better tab semantics, keyboard nav |
| Rule-based icon mapping | LLM semantic selection | GPT-4 availability (2023) | Handles new occupations without code changes |
| CSS `display:none` | `hidden` attribute | HTML5 / ARIA best practices | Screen reader compatibility |
| Inline icon classes | Server-rendered data attributes | Progressive enhancement | SEO, no-JS fallback |

**Deprecated/outdated:**
- jQuery UI Tabs: Heavy dependency for simple pattern; vanilla JS is sufficient and current
- Manual aria-live announcements on tab switch: Not needed if using proper `hidden` + focus management
- CSS-only tabs with `:checked` pseudo-class: Doesn't provide proper keyboard navigation or ARIA semantics

## Open Questions

Things that couldn't be fully resolved:

1. **Minor Group Description Source**
   - What we know: NOC hierarchy includes minor group code (e.g., "726"), parser extracts it
   - What's unclear: Where to get human-readable minor group description text for LLM icon prompt
   - Recommendation:
     - Option A: Scrape from OaSIS hierarchy page when fetching profile (requires additional HTTP call)
     - Option B: Use broad category name + occupation title as proxy (simpler, may be sufficient)
     - Option C: Maintain static mapping of 162 minor groups to descriptions (accurate but requires maintenance)

2. **Tab Content Duplication Between Overview and Job Headers**
   - What we know: Main Duties appears in both Overview tab and Key Activities tab
   - What's unclear: Should content be duplicated or should Overview link to other tabs
   - Recommendation: Duplicate content per requirements. Overview is summary, other tabs are detailed selection interface.

3. **Icon Fallback Strategy**
   - What we know: LLM may fail or return invalid icon
   - What's unclear: Fallback to broad category mapping vs. generic briefcase icon
   - Recommendation: Two-tier fallback:
     1. Try LLM selection
     2. Fall back to broad category static mapping (legislative→landmark, sciences→atom, etc.)
     3. Final fallback to fa-briefcase

## Sources

### Primary (HIGH confidence)

- [W3C ARIA Authoring Practices Guide - Tabs Pattern](https://www.w3.org/WAI/ARIA/apg/patterns/tabs/) - ARIA attributes, keyboard interaction
- [OpenAI API Documentation - Prompt Engineering](https://platform.openai.com/docs/guides/prompt-engineering) - Best practices for structured output
- Existing codebase:
  - `src/services/llm_service.py` - LLM integration pattern
  - `static/js/accordion.js` - Statement rendering patterns
  - `src/services/parser.py` - NOC hierarchy extraction
  - `src/models/noc.py` - NOC data structure

### Secondary (MEDIUM confidence)

- [Building accessible user interface tabs in JavaScript - LogRocket](https://blog.logrocket.com/build-accessible-user-interface-tabs-javascript/) - Implementation examples
- [Font Awesome Icons Categories](https://fontawesome.com/icons/categories) - Available icon set
- [National Occupational Classification Structure](https://noc.esdc.gc.ca/) - 162 minor groups confirmed
- [Flask Jinja2 Templates - ArjanCodes](https://arjancodes.com/blog/rendering-templates-with-jinja2-in-flask/) - Template patterns

### Tertiary (LOW confidence)

- WebSearch results on LLM icon selection - No authoritative sources found; pattern derived from general prompt engineering principles

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All libraries already in use, no new dependencies
- Architecture (ARIA tabs): HIGH - W3C official pattern, widely implemented
- Architecture (LLM integration): HIGH - Extends existing working pattern
- Pitfalls: MEDIUM - Based on common ARIA mistakes documented in accessibility resources
- Icon selection approach: MEDIUM - Novel application of LLM structured output, requires validation

**Research date:** 2026-01-24
**Valid until:** 60 days (stack is stable; ARIA patterns don't change frequently)

**Key implementation risks:**
- **LOW RISK:** Tab HTML structure and ARIA attributes (well-documented pattern)
- **LOW RISK:** LLM occupation description (similar to existing overview generation)
- **MEDIUM RISK:** LLM icon selection (novel approach, needs validation fallback)
- **MEDIUM RISK:** Work Context filtering logic (requires understanding dimension_type field)
- **LOW RISK:** Tab content mapping (deterministic based on requirements)

**What to validate during planning:**
- Confirm minor group description source (scrape vs. static mapping vs. proxy)
- Verify Work Context dimension_type field exists and is populated
- Test LLM icon selection with sample minor group descriptions
- Confirm Font Awesome version available in application (5.x or 6.x)
