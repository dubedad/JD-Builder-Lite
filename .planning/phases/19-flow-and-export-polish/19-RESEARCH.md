# Phase 19: Flow and Export Polish - Research

**Researched:** 2026-02-07
**Domain:** Navigation UX, State Preservation, Coaching UI, Export Enhancement, Technical Documentation
**Confidence:** HIGH

## Summary

Phase 19 focuses on four interconnected domains: navigation flow between screens with state preservation, coaching-style UX for multi-group classification results, classification data export in PDF/DOCX formats, and README documentation for dual audiences. The research reveals established patterns for each domain that align well with user decisions in CONTEXT.md.

Navigation requires split-layout buttons (top-left return vs bottom action bar), breadcrumb/step indicators for progress tracking, and client-side state caching using localStorage or sessionStorage. The coaching UX reframes "invalid combination" as ranked recommendations with informational styling (blue/amber tones), emphasizing transparency and decision support. Export enhancement builds on existing WeasyPrint (PDF) and python-docx (DOCX) infrastructure, which both support hyperlinks natively. README best practices recommend dual-audience structure with executive summary first, then technical deep-dive.

The existing codebase provides strong foundations: Flask routes handle preview/export, allocation API returns structured recommendations with provenance, and the frontend uses vanilla JavaScript with modular files. Key gaps include navigation wiring, state restoration logic, coaching UI styling, and classification export templates.

**Primary recommendation:** Implement navigation as client-side state management using History API and localStorage, style multi-group coaching as ranked decision support (not errors), extend existing export templates with classification sections including clickable provenance hyperlinks, and structure README with compliance value proposition before technical architecture.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Navigation flow:**
- Split layout: "Return to Builder" at top-left, "Classify" and "Export" in a bottom/footer action bar
- Step indicator / breadcrumb showing Builder > Preview > Classify with current step highlighted
- Rename existing "Back to Edit" to "Return to Builder" and reposition to match new nav layout
- Classification results cached until JD changes — user doesn't have to re-classify after navigating away
- When JD is edited after classifying, show stale warning: "JD changed — re-classify for updated results"
- Export available from both Preview and Classification screens
- When exporting from Classification, user can choose what to include (checkboxes: Include JD, Include Classification)

**Multi-group coaching (replaces "Invalid Combination"):**
- Reframe from "invalid" to "Your JD spans multiple groups — here's how we ranked them by confidence"
- Show both duty alignment percentages AND key duties driving each ranking
- Offer both paths: "Accept the top recommendation" or "Return to Builder to adjust your JD"
- No red styling — coaching tone, not error tone

**Classification in export:**
- Full detail: recommendations, confidence scores, rationale, evidence quotes, and provenance chain
- Provenance entries hyperlinked to actual TBS directive URLs (clickable in both PDF and DOCX)
- Full audit footer: tool name, version, date generated, data sources used

**README:**
- Dual audience: quick overview + value proposition for reviewers, then technical details for developers
- Screenshots of key screens (Builder, Preview, Classification, Export)
- Detailed architecture: component diagram, data pipeline, file structure, classification algorithm overview

### Claude's Discretion

- Return-to-Builder state handling (preserve selections, scroll position decisions)
- Button hierarchy (Classify primary vs equal weight with Export)
- Whether step indicator steps are clickable or visual-only
- Whether Export appears as a step in the breadcrumb or stays a side action
- Color scheme for multi-group coaching (replacing red — likely blue/amber informational tones)
- Classification placement in export document (after JD vs separate page)
- How to position compliance context in README

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within phase scope
</user_constraints>

## Standard Stack

The existing codebase uses a proven stack that requires no additions for Phase 19.

### Core (Already in Use)
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Flask | 3.x | Backend web framework | Python web standard, handles routing/templates |
| WeasyPrint | Latest | PDF generation from HTML | Best Python PDF generator, supports CSS3 and hyperlinks |
| python-docx | 1.1.x | DOCX generation | Standard Python library for Word documents, supports hyperlinks |
| Vanilla JavaScript | ES6+ | Frontend interactions | No framework needed for state management in this scope |

### Supporting (Already in Use)
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Jinja2 | 3.x | HTML templating | Rendering preview and export templates |
| localStorage API | Browser native | Client-side state caching | Preserve navigation state between screens |
| History API | Browser native | Browser navigation control | Handle back button and state restoration |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| localStorage | sessionStorage | sessionStorage clears on tab close; localStorage persists across sessions (better for classification cache) |
| History API | Manual URL hash | History API is modern standard with better semantics; hash is legacy fallback |
| Vanilla JS | React/Vue | No need for framework complexity; state scope is limited to navigation flow |

**Installation:**
No new dependencies required. Phase 19 works within existing stack.

## Architecture Patterns

### Recommended Navigation State Pattern

**What:** Client-side navigation with state preservation using localStorage and History API
**When to use:** SPA-like navigation without full page reloads, preserving user selections and classification results

**Pattern structure:**
```javascript
// State management module
const navState = {
  // Save current state before navigation
  saveState: function(screenId, data) {
    const state = {
      screen: screenId,
      timestamp: Date.now(),
      data: data,
      jdHash: this.hashJd(data.selections) // For cache invalidation
    };
    localStorage.setItem('jd_builder_state', JSON.stringify(state));
    history.pushState(state, '', `#${screenId}`);
  },

  // Restore state on back button or direct navigation
  restoreState: function() {
    const stored = localStorage.getItem('jd_builder_state');
    if (stored) {
      const state = JSON.parse(stored);
      // Check if JD has changed since classification
      if (state.classificationResult && this.jdHasChanged(state)) {
        state.stale = true; // Flag for warning
      }
      return state;
    }
    return null;
  },

  // Hash JD content for change detection
  hashJd: function(selections) {
    return JSON.stringify(selections).hashCode(); // Simple hash
  }
};

// Listen for back button
window.addEventListener('popstate', (event) => {
  if (event.state) {
    restoreScreen(event.state.screen, event.state.data);
  }
});
```

**Benefits:**
- Preserves user work across navigation
- Handles browser back button naturally
- Enables cache invalidation when JD changes
- No server-side session complexity

### Split Navigation Layout Pattern

**What:** Dual button placement — return/back actions at top-left, primary actions in bottom action bar
**When to use:** Multi-screen workflows where users need both "escape hatch" and forward progress options

**Structure:**
```html
<!-- Top navigation bar -->
<nav class="preview-header">
  <button class="btn-return-to-builder">
    <i class="fa fa-arrow-left"></i> Return to Builder
  </button>
  <!-- Center: breadcrumb/step indicator -->
  <div class="step-indicator">
    Builder > Preview > Classify
  </div>
</nav>

<!-- Content area -->
<main>
  <!-- Preview or Classification results -->
</main>

<!-- Bottom action bar (sticky footer) -->
<footer class="action-bar">
  <button class="btn btn--primary">Classify</button>
  <button class="btn btn--secondary">Export</button>
</footer>
```

**Benefits:**
- Clear visual hierarchy: escape vs progress
- Common pattern in web apps (Gmail, Jira, Figma)
- Mobile-friendly: action bar accessible at thumb zone
- Breadcrumb provides context without taking action space

### Coaching UI Pattern for Ranked Results

**What:** Present multiple classification results as ranked recommendations with explanatory content, not error messages
**When to use:** When system produces multiple valid options requiring user decision, especially in compliance/advisory contexts

**Visual structure:**
```html
<div class="coaching-panel coaching-panel--info">
  <div class="coaching-icon">
    <i class="fa fa-lightbulb"></i> <!-- Informational icon, not warning -->
  </div>
  <h3 class="coaching-title">Your JD spans multiple occupational groups</h3>
  <p class="coaching-explanation">
    Based on your duties, we identified [N] potential groups.
    Here's how we ranked them by alignment:
  </p>

  <div class="ranked-recommendations">
    <!-- Card 1: Highest confidence -->
    <div class="recommendation-card recommendation-card--primary">
      <div class="confidence-badge">85%</div>
      <h4>CS: Computer Systems</h4>
      <p class="alignment-summary">
        Strong match on [X] key duties: [duty excerpts]
      </p>
    </div>

    <!-- Card 2: Second -->
    <div class="recommendation-card">
      <div class="confidence-badge">72%</div>
      <h4>IT: Information Technology</h4>
      <p class="alignment-summary">
        Moderate match on [Y] key duties: [duty excerpts]
      </p>
    </div>
  </div>

  <div class="coaching-actions">
    <button class="btn btn--primary">Accept Top Recommendation</button>
    <button class="btn btn--text">Return to Builder to Refine</button>
  </div>
</div>
```

**Styling approach:**
- Background: Blue (#e3f2fd) or amber (#fff3e0) for informational tone
- Border: Subtle blue (#1565c0) or amber (#e65100) — NOT red
- Icon: Lightbulb, info circle, or chart — conveys "insight" not "error"
- Typography: Conversational, coaching tone ("Here's what we found...")
- Card hierarchy: Visual weight on top recommendation (larger, highlighted)

**Anti-pattern to avoid:**
- Red error styling (implies mistake/failure)
- "Invalid" or "Error" language (use "Multiple matches found")
- Single result without explanation (defeats coaching purpose)
- Technical jargon without context

### Export Template Extension Pattern

**What:** Extend existing Jinja2 templates to include optional classification section with provenance hyperlinks
**When to use:** Adding new content blocks to established export templates

**Template structure:**
```jinja2
{# templates/export/jd_pdf.html #}

<!-- Existing JD content -->
{% for element in jd_elements %}
  <!-- ... existing statements ... -->
{% endfor %}

<!-- NEW: Classification section (conditional) -->
{% if include_classification and classification_result %}
<section class="classification-section">
  <h1>Classification Step 1: Occupational Group Allocation</h1>

  <div class="classification-metadata">
    <p><strong>Analyzed:</strong> {{ classification_result.analyzed_at }}</p>
    <p><strong>Status:</strong> {{ classification_result.status }}</p>
  </div>

  <h2>Recommendations</h2>
  {% for rec in classification_result.recommendations %}
  <div class="recommendation-item">
    <h3>{{ rec.group_code }}: {{ rec.group_name }}</h3>
    <p class="confidence">Confidence: {{ rec.confidence }}%</p>
    <p class="rationale">{{ rec.rationale }}</p>

    <!-- Evidence with character offsets -->
    <div class="evidence">
      <h4>Supporting Evidence</h4>
      {% for ev in rec.evidence %}
      <blockquote>
        "{{ ev.quote }}"
        <cite>{{ ev.source_field }}</cite>
      </blockquote>
      {% endfor %}
    </div>

    <!-- Provenance with hyperlinks -->
    <div class="provenance">
      <h4>Authoritative Source</h4>
      <p>
        <a href="{{ rec.provenance.url }}" target="_blank">
          TBS Occupational Group {{ rec.group_code }} Definition
        </a>
      </p>
      <p><small>Retrieved: {{ rec.provenance.scraped_at }}</small></p>
    </div>
  </div>
  {% endfor %}

  <!-- Audit footer -->
  <footer class="classification-footer">
    <p><strong>Tool:</strong> JobForge Classification Engine v{{ version }}</p>
    <p><strong>Generated:</strong> {{ generated_at }}</p>
    <p><strong>Data Sources:</strong> TBS Occupational Group Definitions</p>
    <p><strong>Compliance:</strong> TBS Directive 32592</p>
  </footer>
</section>
{% endif %}
```

**Hyperlink implementation:**
- **PDF (WeasyPrint):** Standard HTML `<a href="...">` tags become clickable links automatically
- **DOCX (python-docx):** Use `add_hyperlink()` helper function (see Code Examples section)

**Benefits:**
- Conditional inclusion (export with/without classification)
- Maintains existing export structure
- Hyperlinks work in both formats
- Full audit trail for compliance

### README Dual-Audience Pattern

**What:** Structure README with executive summary for reviewers, followed by technical deep-dive for developers
**When to use:** Open source projects, compliance tools, or any project with non-technical stakeholders

**Structure:**
```markdown
# JobForge - Job Description Builder

[Hero screenshot showing main UI]

## Quick Start (for Reviewers)

**What it does:** Helps GC managers build TBS-compliant job descriptions...

**Why it matters:** Demonstrates Directive 32592 compliance with full provenance...

**Key features:**
- [Bullet list of value propositions]
- Screenshots showing key flows

## Installation (for Developers)

[Technical setup instructions]

## Architecture

[Component diagram]
[Data flow diagram]

### Directory Structure
```

**Benefits:**
- Non-technical readers get value without scrolling past setup commands
- Developers find technical details quickly
- Screenshots provide visual proof of features
- Clear compliance messaging for audit purposes

### Anti-Patterns to Avoid

**Navigation:**
- **Don't:** Use full page reloads for navigation between builder/preview/classify
  - **Do:** Use History API and DOM manipulation for instant transitions
- **Don't:** Store sensitive data in localStorage (personal info, credentials)
  - **Do:** Only cache non-sensitive UI state (selections IDs, timestamps)

**Coaching UI:**
- **Don't:** Present ranked results as "errors" or "failures" with red styling
  - **Do:** Frame as "decision support" or "multiple matches" with blue/amber informational tones
- **Don't:** Hide rationale behind "learn more" links requiring clicks
  - **Do:** Show key evidence inline; offer expansion for full details

**Export:**
- **Don't:** Generate classification report as separate file from JD
  - **Do:** Include classification as section within main export (single source of truth)
- **Don't:** Use plain text URLs in exports
  - **Do:** Use proper hyperlinks that are clickable in PDF/DOCX viewers

## Don't Hand-Roll

Phase 19 has several areas where custom solutions are tempting but existing solutions are better.

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| State caching between screens | Custom state sync to server | localStorage + History API | Browser APIs handle edge cases (back button, tab close, crash recovery) better than custom solutions |
| Hyperlinks in PDF | Text URLs with "Visit: ..." | WeasyPrint's native `<a>` tag support | WeasyPrint automatically converts HTML links to PDF annotations; custom solutions miss PDF viewer integration |
| Hyperlinks in DOCX | Plain text URLs | python-docx `add_hyperlink()` | python-docx creates proper Word hyperlink objects; plain text lacks clickability |
| Multi-option decision UI | Custom dropdown or radio buttons | Ranked card layout with confidence badges | Decision support research shows cards with visual hierarchy outperform flat lists for confidence-weighted options |
| Cache invalidation | Manual "refresh" buttons | Hash-based change detection | Content hashing detects JD changes automatically; manual refresh puts burden on user to remember |
| README diagrams | ASCII art or text descriptions | Embedded images or mermaid.js | Visual diagrams communicate architecture 10x faster; ASCII art is legacy pattern |

**Key insight:** Navigation, export, and documentation are solved problems with mature browser/library support. Don't reinvent these wheels — focus implementation effort on domain-specific coaching UX and compliance messaging where custom solutions add unique value.

## Common Pitfalls

### Pitfall 1: localStorage Quota Exceeded

**What goes wrong:** Storing large classification results directly in localStorage can exceed 5-10MB browser quota, causing silent failures or exceptions.

**Why it happens:** localStorage has per-origin limits (typically 5MB); storing full JD text + classification results + provenance can exceed this.

**How to avoid:**
- Store only essential state: selection IDs, timestamps, classification result ID (not full text)
- Store full classification results in memory during session
- Use IndexedDB if quota becomes issue (future enhancement, not Phase 19 scope)

**Warning signs:**
- QuotaExceededError exceptions in console
- State not restoring after navigation
- Classification cache not working

### Pitfall 2: Back Button Breaking State

**What goes wrong:** Browser back button navigates away from app entirely, or loads stale screen without restoring selections.

**Why it happens:** Failing to properly register state with History API; using `location.hash` without `pushState()`.

**How to avoid:**
- Always call `history.pushState()` when changing screens
- Register `popstate` event listener on page load
- Store screen identifier in state object
- Test back button explicitly in all navigation flows

**Warning signs:**
- Back button exits app to external referrer
- Back button shows blank screen
- Selections disappear after back navigation

### Pitfall 3: Coaching UI Perceived as Error

**What goes wrong:** Users see multi-group results as "something went wrong" and abandon the flow.

**Why it happens:** Using error styling (red, warning icons) for what is actually a valid result requiring user decision.

**How to avoid:**
- Use blue/amber informational colors (not red)
- Lead with positive framing: "We found multiple matches" not "Unable to classify"
- Show confidence percentages to reinforce legitimacy
- Include "Accept top recommendation" as primary action (not just "go back")

**Warning signs:**
- User testing reveals confusion or frustration with multi-group results
- Users don't understand they can proceed with top recommendation
- Abandonment rate increases on multi-group classifications

### Pitfall 4: Hyperlinks Not Clickable in Exports

**What goes wrong:** URLs appear as plain text in PDF/DOCX; users must manually copy-paste to browser.

**Why it happens:**
- PDF: Using text rendering instead of proper HTML `<a>` tags before WeasyPrint conversion
- DOCX: Using `add_paragraph(url_string)` instead of `add_hyperlink()` function

**How to avoid:**
- **PDF:** Ensure Jinja2 templates use `<a href="{{ url }}">{{ link_text }}</a>` syntax
- **DOCX:** Use python-docx hyperlink helper (see Code Examples section)
- Test exports by clicking links in Adobe Reader (PDF) and Microsoft Word (DOCX)

**Warning signs:**
- Links appear blue/underlined but don't respond to clicks
- Right-click context menu doesn't show "Open Link" option
- Accessibility scanners flag missing hyperlink semantics

### Pitfall 5: JD Changes Not Detected

**What goes wrong:** User modifies JD after classifying; old classification results still shown without staleness warning.

**Why it happens:** Not hashing JD content when caching classification results; no comparison on restore.

**How to avoid:**
- Hash selection IDs + key activity text when saving classification cache
- Re-hash current state on "Return to Builder"
- Compare hashes; if different, set `stale: true` flag
- Display warning banner: "JD changed — re-classify for updated results"

**Warning signs:**
- Users export JD with mismatched classification (JD doesn't match classified duties)
- No staleness indicator appears after editing
- Cache persists indefinitely without invalidation

### Pitfall 6: README Overwhelms Non-Technical Readers

**What goes wrong:** Technical setup commands appear first; reviewers/auditors bounce without understanding value proposition.

**Why it happens:** Following traditional README template (installation → usage → architecture).

**How to avoid:**
- Lead with "What it does" and "Why it matters" (2-3 sentences)
- Add hero screenshot showing finished UI before any code
- Defer technical setup to "Installation" section after overview
- Use table of contents so developers can skip to setup

**Warning signs:**
- Stakeholder questions reveal they didn't read README
- Audit reviewers ask "What does this do?" despite README existing
- Developers complain about lack of setup instructions (didn't scroll past overview)

## Code Examples

Verified patterns from existing codebase and official documentation.

### Navigation State Management (Client-side)

```javascript
// Source: Existing static/js/state.js + History API patterns
// Add to static/js/navigation.js (new file)

const navigationState = {
  /**
   * Save current screen state before navigation
   * @param {string} screenId - 'builder' | 'preview' | 'classify'
   * @param {object} data - State data to preserve
   */
  saveState: function(screenId, data) {
    const state = {
      screen: screenId,
      timestamp: Date.now(),
      data: data,
      jdHash: this.hashJd(store.getState().selections)
    };

    // Save to localStorage for persistence
    localStorage.setItem('jd_builder_nav_state', JSON.stringify(state));

    // Register with History API for back button support
    history.pushState(state, '', `#${screenId}`);
  },

  /**
   * Restore state from localStorage + History API
   * @returns {object|null} Restored state or null if none exists
   */
  restoreState: function() {
    const stored = localStorage.getItem('jd_builder_nav_state');
    if (!stored) return null;

    const state = JSON.parse(stored);

    // Check if classification is stale
    if (state.classificationResult) {
      const currentHash = this.hashJd(store.getState().selections);
      if (currentHash !== state.jdHash) {
        state.stale = true; // Flag for warning display
      }
    }

    return state;
  },

  /**
   * Simple hash for JD content comparison
   * @param {object} selections - Store selections object
   * @returns {string} Hash string
   */
  hashJd: function(selections) {
    // Simple hash: concatenate sorted selection IDs
    const allIds = Object.values(selections)
      .flat()
      .sort()
      .join(',');
    return btoa(allIds); // Base64 encode for compact storage
  },

  /**
   * Clear cached state (when user starts new JD)
   */
  clearState: function() {
    localStorage.removeItem('jd_builder_nav_state');
    localStorage.removeItem('classification_cache');
  }
};

// Listen for browser back button
window.addEventListener('popstate', (event) => {
  if (event.state && event.state.screen) {
    // Restore screen based on state
    restoreScreen(event.state.screen, event.state.data);
  }
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = navigationState;
}
```

### Classification Cache with Invalidation

```javascript
// Source: Pattern from existing classify.js + cache invalidation logic
// Add to static/js/classify.js

const classificationCache = {
  /**
   * Save classification result with JD hash for invalidation
   * @param {object} result - Full allocation response
   */
  saveResult: function(result) {
    const cache = {
      result: result,
      jdHash: navigationState.hashJd(store.getState().selections),
      timestamp: Date.now()
    };
    localStorage.setItem('classification_cache', JSON.stringify(cache));
  },

  /**
   * Get cached classification if still valid
   * @returns {object|null} Cached result or null if stale/missing
   */
  getResult: function() {
    const stored = localStorage.getItem('classification_cache');
    if (!stored) return null;

    const cache = JSON.parse(stored);
    const currentHash = navigationState.hashJd(store.getState().selections);

    // Check if JD has changed
    if (cache.jdHash !== currentHash) {
      console.log('[classify] Cache invalid: JD changed');
      return null;
    }

    // Check if cache is too old (24 hours)
    const age = Date.now() - cache.timestamp;
    if (age > 24 * 60 * 60 * 1000) {
      console.log('[classify] Cache expired');
      return null;
    }

    return cache.result;
  },

  /**
   * Clear classification cache
   */
  clear: function() {
    localStorage.removeItem('classification_cache');
  },

  /**
   * Check if cache exists and is valid
   * @returns {boolean} True if valid cache exists
   */
  isValid: function() {
    return this.getResult() !== null;
  }
};
```

### Coaching UI Component (HTML + CSS)

```html
<!-- Source: Pattern adapted from existing classify-section + coaching UX research -->
<!-- Add to templates/index.html (modify existing classify-section) -->

<div class="coaching-panel coaching-panel--info">
  <div class="coaching-icon">
    <i class="fas fa-lightbulb"></i>
  </div>
  <div class="coaching-content">
    <h3 class="coaching-title">Your JD spans multiple occupational groups</h3>
    <p class="coaching-explanation">
      Based on your key activities, we identified {{ recommendations|length }}
      potential groups. Here's how we ranked them by confidence and duty alignment:
    </p>

    <!-- Ranked recommendation cards -->
    <div class="ranked-recommendations">
      {% for rec in recommendations %}
      <div class="recommendation-card {% if loop.first %}recommendation-card--primary{% endif %}">
        <div class="recommendation-header">
          <div class="confidence-badge confidence-badge--{{ rec.confidence_tier }}">
            {{ rec.confidence }}%
          </div>
          <h4 class="recommendation-title">
            {{ rec.group_code }}: {{ rec.group_name }}
          </h4>
        </div>

        <div class="duty-alignment">
          <p><strong>Alignment Summary:</strong></p>
          <ul class="duty-list">
            {% for duty in rec.key_duties[:3] %}
            <li>{{ duty }}</li>
            {% endfor %}
          </ul>
        </div>

        <button class="btn-expand-details" data-group="{{ rec.group_code }}">
          View Full Rationale
        </button>
      </div>
      {% endfor %}
    </div>

    <div class="coaching-actions">
      <button class="btn btn--primary" onclick="acceptTopRecommendation()">
        <i class="fas fa-check"></i> Accept Top Recommendation
      </button>
      <button class="btn btn--text" onclick="returnToBuilder()">
        <i class="fas fa-arrow-left"></i> Return to Builder to Refine
      </button>
    </div>
  </div>
</div>
```

```css
/* Source: Coaching UI research + existing classify.css patterns */
/* Add to static/css/classify.css */

.coaching-panel {
  background: #e3f2fd; /* Light blue for informational tone */
  border: 2px solid #1565c0; /* Medium blue border */
  border-radius: 8px;
  padding: 2rem;
  margin: 2rem 0;
  display: flex;
  gap: 1.5rem;
}

.coaching-panel--info {
  background: #e3f2fd;
  border-color: #1565c0;
}

.coaching-panel--warning {
  background: #fff3e0; /* Amber for moderate alerts */
  border-color: #e65100;
}

.coaching-icon {
  flex-shrink: 0;
  font-size: 2.5rem;
  color: #1565c0;
}

.coaching-title {
  margin: 0 0 0.5rem 0;
  font-size: 1.25rem;
  color: #1565c0;
}

.coaching-explanation {
  margin: 0 0 1.5rem 0;
  line-height: 1.6;
  color: #424242;
}

.ranked-recommendations {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.recommendation-card {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  padding: 1.25rem;
}

.recommendation-card--primary {
  border: 2px solid #1565c0; /* Emphasize top choice */
  box-shadow: 0 2px 8px rgba(21, 101, 192, 0.15);
}

.recommendation-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.confidence-badge {
  padding: 0.375rem 0.75rem;
  border-radius: 4px;
  font-weight: 600;
  font-size: 0.875rem;
}

.confidence-badge--high {
  background: #e8f5e9;
  color: #2e7d32;
}

.confidence-badge--medium {
  background: #fff3e0;
  color: #e65100;
}

.duty-alignment {
  margin-bottom: 1rem;
}

.duty-list {
  margin: 0.5rem 0 0 1.5rem;
  color: #616161;
}

.coaching-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}
```

### Export Classification Section (Jinja2 Template)

```jinja2
{# Source: Existing templates/export/jd_pdf.html pattern extended #}
{# Add to templates/export/jd_pdf.html after JD elements section #}

{% if include_classification and classification_result %}
<section class="classification-section">
  <h1 class="classification-heading">Classification Step 1: Occupational Group Allocation</h1>

  <div class="classification-metadata">
    <table class="metadata-table">
      <tr>
        <th>Analyzed:</th>
        <td>{{ classification_result.analyzed_at.strftime('%Y-%m-%d %H:%M UTC') }}</td>
      </tr>
      <tr>
        <th>Status:</th>
        <td>{{ classification_result.status }}</td>
      </tr>
      <tr>
        <th>Match Context:</th>
        <td>{{ classification_result.match_context }}</td>
      </tr>
    </table>
  </div>

  <h2>Recommendations (Ranked by Confidence)</h2>

  {% for rec in classification_result.recommendations %}
  <div class="recommendation-item">
    <div class="recommendation-header">
      <h3>{{ rec.group_code }}: {{ rec.group_name }}</h3>
      <span class="confidence-badge confidence-{{ rec.confidence_tier }}">
        {{ rec.confidence }}% confidence
      </span>
    </div>

    <div class="rationale-section">
      <h4>Rationale</h4>
      <p>{{ rec.rationale }}</p>
    </div>

    <div class="evidence-section">
      <h4>Supporting Evidence from Job Description</h4>
      {% for ev in rec.evidence %}
      <blockquote class="evidence-quote">
        <p>"{{ ev.quote }}"</p>
        <cite>Source: {{ ev.source_field }}</cite>
      </blockquote>
      {% endfor %}
    </div>

    <div class="provenance-section">
      <h4>Authoritative Source</h4>
      <p>
        <strong>Source Type:</strong> {{ rec.provenance.source_type }}<br>
        <strong>Document:</strong>
        <a href="{{ rec.provenance.url }}" target="_blank" class="provenance-link">
          TBS Occupational Group {{ rec.group_code }} Definition
        </a><br>
        <strong>Definition Paragraph:</strong> {{ rec.provenance.definition_paragraph }}<br>
        <strong>Inclusions Referenced:</strong>
        {% if rec.provenance.inclusions_referenced %}
          {{ rec.provenance.inclusions_referenced|join(', ') }}
        {% else %}
          None
        {% endif %}<br>
        <strong>Exclusions Checked:</strong>
        {% if rec.provenance.exclusions_checked %}
          {{ rec.provenance.exclusions_checked|join(', ') }}
        {% else %}
          None
        {% endif %}
      </p>
      <p class="provenance-meta">
        <small>Retrieved: {{ rec.provenance.scraped_at }} |
        Archive: {{ rec.provenance.archive_path or 'Not archived' }}</small>
      </p>
    </div>
  </div>
  {% endfor %}

  <!-- Classification audit footer -->
  <footer class="classification-footer">
    <h3>Classification Audit Trail</h3>
    <table class="audit-table">
      <tr>
        <th>Tool:</th>
        <td>JobForge Classification Engine</td>
      </tr>
      <tr>
        <th>Version:</th>
        <td>{{ app_version }}</td>
      </tr>
      <tr>
        <th>Generated:</th>
        <td>{{ classification_result.analyzed_at.strftime('%Y-%m-%d %H:%M UTC') }}</td>
      </tr>
      <tr>
        <th>Data Sources:</th>
        <td>TBS Occupational Group Definitions ({{ tbs_data_version }})</td>
      </tr>
      <tr>
        <th>Compliance:</th>
        <td>TBS Directive 32592 (Automated Decision Making)</td>
      </tr>
      <tr>
        <th>Constraints Verified:</th>
        <td>{{ classification_result.constraints_compliance }}</td>
      </tr>
    </table>
  </footer>
</section>
{% endif %}
```

### DOCX Hyperlink Helper (Python)

```python
# Source: python-docx documentation + community patterns
# Add to src/services/docx_generator.py

from docx import Document
from docx.oxml.shared import OxmlElement
from docx.oxml.ns import qn

def add_hyperlink(paragraph, url, text, color='0000FF', underline=True):
    """
    Add a hyperlink to a paragraph.

    Args:
        paragraph: docx.text.paragraph.Paragraph object
        url: Target URL (string)
        text: Display text for the link
        color: Hex color code (default: blue)
        underline: Whether to underline (default: True)

    Returns:
        Run object containing the hyperlink

    Source: python-docx documentation pattern
    https://github.com/python-openxml/python-docx/issues/384
    """
    # Create hyperlink element
    hyperlink = OxmlElement('w:hyperlink')
    hyperlink.set(qn('r:id'), paragraph.part.relate_to(
        url,
        'http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink',
        is_external=True
    ))

    # Create run with text
    run = OxmlElement('w:r')
    rPr = OxmlElement('w:rPr')

    # Apply hyperlink styling
    if color:
        c = OxmlElement('w:color')
        c.set(qn('w:val'), color)
        rPr.append(c)

    if underline:
        u = OxmlElement('w:u')
        u.set(qn('w:val'), 'single')
        rPr.append(u)

    run.append(rPr)
    text_elem = OxmlElement('w:t')
    text_elem.text = text
    run.append(text_elem)
    hyperlink.append(run)

    paragraph._p.append(hyperlink)
    return run

# Usage in export generation:
def add_classification_section(doc, classification_result):
    """Add classification section to DOCX with hyperlinked provenance."""
    doc.add_heading('Classification Step 1: Occupational Group Allocation', 1)

    for rec in classification_result['recommendations']:
        doc.add_heading(f"{rec['group_code']}: {rec['group_name']}", 2)

        # Rationale
        doc.add_paragraph(rec['rationale'])

        # Provenance with hyperlink
        prov_para = doc.add_paragraph('Authoritative Source: ')
        add_hyperlink(
            prov_para,
            rec['provenance']['url'],
            f"TBS Occupational Group {rec['group_code']} Definition",
            color='1565C0',  # GC blue
            underline=True
        )
```

### README Dual-Audience Template

```markdown
<!-- Source: GitHub README best practices + dual-audience research -->
<!-- Create as README.md in project root -->

# JobForge - Job Description Builder

![JobForge Main Screen](docs/screenshots/builder-screen.png)

## Overview

**JobForge** is a compliance-focused job description builder that helps Government of Canada managers create TBS-compliant job descriptions with full provenance tracking. Built to demonstrate compliance with TBS Directive 32592 (Automated Decision Making), JobForge traces every statement to authoritative sources (ESDC NOC 2025, O*NET) and provides occupational group classification guidance.

### Key Features

- **Authoritative Sources:** All content sourced from ESDC NOC 2025 v1.0 and O*NET 27.2
- **Classification Guidance:** AI-assisted occupational group allocation (Classification Step 1)
- **Full Provenance:** Every selection linked to data steward, publication date, and source URL
- **Export Options:** Generate PDF or Word documents with embedded compliance metadata
- **Medallion Architecture:** Bronze (raw), Silver (validated), Gold (enriched) data layers

### For Reviewers

JobForge demonstrates:
- ✅ Compliance with TBS Directive 32592 (DADM) Section 6.2.3 (data sources)
- ✅ Compliance with Section 6.2.7 (manager decisions with provenance)
- ✅ Compliance with Section 6.3.5 (data quality: relevant, accurate, up-to-date)
- ✅ Full audit trail: tool version, data sources, timestamps, hyperlinked provenance

See [Compliance Architecture](docs/COMPLIANCE.md) for detailed mapping.

### Screenshots

| Builder Screen | Classification Results | Export Preview |
|---------------|----------------------|----------------|
| ![Builder](docs/screenshots/builder.png) | ![Classification](docs/screenshots/classification.png) | ![Export](docs/screenshots/export.png) |

---

## Installation (for Developers)

### Prerequisites

- Python 3.11+
- pip package manager
- (Optional) Virtual environment tool

### Setup

1. Clone repository:
   ```bash
   git clone https://github.com/yourorg/jobforge.git
   cd jobforge
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your settings (OpenAI API key for classification)
   ```

4. Initialize database:
   ```bash
   python -m src.cli.refresh_occupational
   ```

5. Run development server:
   ```bash
   python -m src.app
   ```

6. Open browser: http://localhost:5000

### Project Structure

```
jobforge/
├── src/
│   ├── services/       # Core services (scraping, PDF, LLM)
│   ├── matching/       # Classification engine
│   ├── storage/        # Database and repository layer
│   ├── routes/         # Flask API routes
│   └── models/         # Pydantic models
├── static/
│   ├── js/            # Frontend modules (state, classify, export)
│   └── css/           # Styling (GC design system)
├── templates/
│   ├── index.html     # Main SPA
│   └── export/        # PDF/DOCX templates
├── data/
│   └── jobforge.db    # SQLite database
└── tests/             # Test suite
```

## Architecture

### Data Pipeline

```
[ESDC NOC] → [Scraper] → [Parser] → [Bronze DB]
                                          ↓
[O*NET] → [Enrichment] → [Silver DB] → [Gold DB]
                                          ↓
                                    [API Layer]
                                          ↓
                                   [Frontend SPA]
```

### Classification Algorithm

1. **Shortlisting:** Semantic similarity (sentence-transformers) + NOC label matching
2. **LLM Classification:** GPT-4 with structured outputs analyzing JD against group definitions
3. **Confidence Scoring:** Multi-factor (semantic similarity, LLM confidence, label boost)
4. **Evidence Extraction:** Character-offset quotes from JD mapped to recommendations
5. **Provenance Linking:** TBS source URLs with inclusion/exclusion paragraph references

See [Classification Algorithm](docs/CLASSIFICATION.md) for detailed flow.

## Compliance & Data Governance

JobForge implements medallion architecture for data quality:

- **Bronze Layer:** Raw HTML from ESDC NOC (archived with timestamps)
- **Silver Layer:** Validated, parsed profiles with data quality checks
- **Gold Layer:** Enriched with O*NET, ready for production use

Every export includes:
- Data steward (ESDC)
- Authoritative source URL
- Retrieval timestamp
- Manager selection timestamps (UTC)
- Tool version and model used

## Testing

Run test suite:
```bash
pytest tests/
```

Run specific test file:
```bash
pytest tests/test_classification.py -v
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## License

[Your License]

---

**Contact:** [Your Contact Info]
**Documentation:** [Link to full docs]
```

## State of the Art

Phase 19 builds on mature patterns; key evolution is UX framing of multi-option results.

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Full page reloads for navigation | History API + DOM manipulation | ~2015 (HTML5 History API adoption) | Instant transitions, better UX |
| Server-side sessions for state | localStorage + client-side caching | ~2018 (SPA maturity) | Reduced server load, offline capability |
| Error messaging for multi-option results | Coaching/decision support UI | 2020+ (AI UX research) | Users understand results are valid, not failures |
| Plain text URLs in exports | Hyperlinked provenance | 2010+ (PDF/DOCX standard support) | Clickable links improve auditing workflow |
| Developer-first README | Dual-audience structure | 2022+ (open source best practices) | Non-technical stakeholders understand value |

**Deprecated/outdated:**
- **URL hash navigation (`#page`):** Replaced by History API with `pushState()` for cleaner URLs and better semantics
- **Synchronous AJAX with XMLHttpRequest:** Replaced by `fetch()` API with async/await for cleaner async code
- **Red "error" styling for valid multi-option results:** Replaced by blue/amber "informational" coaching UI based on decision support UX research

## Open Questions

Things that couldn't be fully resolved in research:

1. **Button Hierarchy: Classify vs Export**
   - What we know: Both actions available from Preview and Classification screens
   - What's unclear: Should "Classify" be primary button (green) and "Export" secondary (gray), or equal weight?
   - Recommendation: Make "Classify" primary when no classification exists; make "Export" primary after classification complete (progressive disclosure). User can always re-classify if needed.

2. **Breadcrumb Clickability**
   - What we know: Breadcrumb shows Builder > Preview > Classify progression
   - What's unclear: Should steps be clickable for direct navigation, or visual-only progress indicator?
   - Recommendation: Make completed steps clickable (e.g., click "Preview" to return to preview from Classify), but disable future steps. This matches common pattern in checkout flows.

3. **Scroll Position Restoration**
   - What we know: "Return to Builder" should preserve selections
   - What's unclear: Should scroll position also be preserved (e.g., user was scrolled to "Skills" section)?
   - Recommendation: Don't preserve scroll position — let user scroll naturally. Preserving selections is sufficient; forced scroll feels jarring. If needed, add "Jump to [section]" links in sidebar.

4. **Classification Section Placement in Export**
   - What we know: Classification appears in PDF/DOCX export
   - What's unclear: Should it be main section after JD elements, or separate appendix page?
   - Recommendation: Place as final main section before Compliance Appendix. This makes classification feel like "part of the JD" not "attached audit report." Use page break before classification section for visual separation.

5. **Export Checkboxes: Default State**
   - What we know: When exporting from Classification screen, user chooses "Include JD" and "Include Classification" via checkboxes
   - What's unclear: Should both be checked by default, or only "Include Classification" since JD is already visible?
   - Recommendation: Check both by default. Most users want complete document; unchecking requires conscious choice. Show preview of what's included.

## Sources

### Primary (HIGH confidence)

- **WeasyPrint Documentation:** https://doc.courtbouillon.org/weasyprint/v62.0/api_reference.html - Confirmed native hyperlink support in PDF generation
- **python-docx Issues:** https://github.com/python-openxml/python-docx/issues/384 - Community-verified hyperlink implementation pattern
- **MDN History API:** https://developer.mozilla.org/en-US/docs/Web/API/History_API/Working_with_the_History_API - Authoritative browser API documentation
- **Existing Codebase:** src/services/pdf_generator.py, src/services/docx_generator.py, static/js/classify.js, src/models/allocation.py - Current implementation patterns

### Secondary (MEDIUM confidence)

- [Breadcrumb Pattern - W3C](https://www.w3.org/WAI/ARIA/apg/patterns/breadcrumb/) - ARIA accessibility patterns for breadcrumbs
- [Breadcrumbs: 11 Design Guidelines - Nielsen Norman Group](https://www.nngroup.com/articles/breadcrumbs/) - UX best practices for navigation
- [Error Message UX - Pencil & Paper](https://www.pencilandpaper.io/articles/ux-pattern-analysis-error-feedback) - Error vs informational messaging patterns
- [README Best Practices - GitHub](https://github.com/jehna/readme-best-practices) - Dual-audience documentation structure
- [Design Guidelines for Better Notifications UX - Smashing Magazine](https://www.smashingmagazine.com/2025/07/design-guidelines-better-notifications-ux/) - Informational vs error tone in UX
- [Top UX Design Principles 2026 - UX Design Institute](https://www.uxdesigninstitute.com/blog/ux-design-principles-2026/) - Modern UX patterns and trust-building
- [Decision Support User Interfaces - Springer](https://link.springer.com/article/10.1007/s10796-021-10234-5) - AI-based decision support interface design principles
- [Working with the History API - MDN](https://developer.mozilla.org/en-US/docs/Web/API/History_API/Working_with_the_History_API) - Browser navigation and state management

### Tertiary (LOW confidence)

- Various blog posts and Medium articles on SPA navigation patterns (useful for general patterns but not authoritative for specific implementation)
- Community discussions on Flask state management (patterns noted but require verification against official Flask docs)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All libraries already in use, no new dependencies, verified in existing codebase
- Architecture patterns: HIGH - Navigation, state management, and export patterns well-documented with official sources and existing code examples
- Coaching UX: MEDIUM - Strong research on informational vs error messaging, but specific multi-group coaching UI is custom design requiring user testing
- Hyperlinks in exports: HIGH - Both WeasyPrint and python-docx have documented hyperlink support with verified implementation patterns
- README structure: HIGH - Dual-audience pattern well-established in open source best practices

**Research date:** 2026-02-07
**Valid until:** 2026-03-07 (30 days - stable domain, mature patterns, minimal churn expected)
