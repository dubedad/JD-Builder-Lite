---
phase: 08-C-profile-page-tabs
plan: 02
type: execute
wave: 2
depends_on: ["08-C-01"]
files_modified:
  - templates/index.html
  - static/css/main.css
  - static/js/api.js
  - static/js/accordion.js
autonomous: true

must_haves:
  truths:
    - "Profile header displays blue banner with occupation title"
    - "OaSIS code appears as styled badge below title"
    - "LLM-generated icon displays on right side of header"
    - "LLM-generated description paragraph visible in header"
    - "Leading statement from NOC data displays below code badge"
  artifacts:
    - path: "templates/index.html"
      provides: "Profile header section with blueBG banner"
      contains: "profile-header"
    - path: "static/css/main.css"
      provides: "Blue banner styling, badge styles, icon display"
      contains: ".blueBG"
    - path: "static/js/accordion.js"
      provides: "Header rendering with LLM calls"
      contains: "fetchOccupationIcon"
  key_links:
    - from: "static/js/accordion.js"
      to: "/api/occupation-icon"
      via: "fetch API call"
      pattern: "fetch.*occupation-icon"
    - from: "static/js/accordion.js"
      to: "/api/occupation-description"
      via: "fetch API call"
      pattern: "fetch.*occupation-description"
---

<objective>
Create the profile header UI with blue banner, OaSIS code badge, LLM-driven icon, and LLM-generated occupation description.

Purpose: Replace the current plain profile info card with an OaSIS-style blue banner header that displays contextual icon and synthesized description.

Output: New profile header section with styling matching OaSIS design, fetching icon and description from LLM endpoints.
</objective>

<execution_context>
@C:\Users\Administrator\.claude/get-shit-done/workflows/execute-plan.md
@C:\Users\Administrator\.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/phases/08-C-profile-page-tabs/08-C-RESEARCH.md
@.planning/phases/08-C-profile-page-tabs/08-C-01-SUMMARY.md
@.planning/phases/06-enhanced-ui-display/OASIS-HTML-REFERENCE.md
@templates/index.html
@static/css/main.css
@static/js/accordion.js
@static/js/api.js
</context>

<tasks>

<task type="auto">
  <name>Task 1: Add profile header HTML and CSS</name>
  <files>templates/index.html, static/css/main.css</files>
  <action>
    **HTML Changes (templates/index.html):**

    Replace the existing `#profile-info` section with a new profile header structure:

    ```html
    <!-- Profile Header (blue banner, initially hidden) -->
    <section id="profile-header" class="profile-header blueBG hidden">
        <div class="profile-header__content">
            <div class="profile-header__text">
                <h2 id="profile-title" class="profile-header__title"></h2>
                <span id="profile-code-badge" class="oasis-code-badge"></span>
                <p id="profile-lead-statement" class="profile-header__lead"></p>
                <p id="profile-description" class="profile-header__description"></p>
            </div>
            <div class="profile-header__icon">
                <i id="profile-icon" class="fas fa-briefcase" aria-hidden="true"></i>
            </div>
        </div>
        <div class="profile-header__meta">
            <span class="profile-header__source">
                Source: <a id="profile-link" href="#" target="_blank" rel="noopener noreferrer">View on OASIS</a>
            </span>
            <span id="profile-timestamp" class="profile-header__timestamp"></span>
        </div>
    </section>
    ```

    Also add Font Awesome CDN link in `<head>` section:
    ```html
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    ```

    **CSS Changes (static/css/main.css):**

    Add blue banner and header styling:

    ```css
    /* Profile Header - Blue Banner */
    .profile-header {
        background: linear-gradient(135deg, #003366 0%, #004488 100%);
        color: #ffffff;
        padding: 2rem;
        margin-bottom: 1.5rem;
        border-radius: 8px;
    }

    .profile-header__content {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 2rem;
    }

    .profile-header__text {
        flex: 1;
    }

    .profile-header__title {
        font-size: 1.75rem;
        font-weight: 600;
        margin: 0 0 0.75rem 0;
        color: #ffffff;
    }

    .oasis-code-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.2);
        padding: 0.25rem 0.75rem;
        border-radius: 4px;
        font-size: 0.875rem;
        font-weight: 500;
        margin-bottom: 1rem;
    }

    .profile-header__lead {
        font-size: 1rem;
        line-height: 1.5;
        margin: 0.75rem 0;
        opacity: 0.95;
    }

    .profile-header__description {
        font-size: 0.9375rem;
        line-height: 1.6;
        margin: 1rem 0 0 0;
        opacity: 0.9;
        font-style: italic;
    }

    .profile-header__icon {
        flex-shrink: 0;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .profile-header__icon i {
        font-size: 5rem;
        color: #CADBF2;
    }

    .profile-header__meta {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 1.5rem;
        padding-top: 1rem;
        border-top: 1px solid rgba(255, 255, 255, 0.2);
        font-size: 0.8125rem;
        opacity: 0.8;
    }

    .profile-header__meta a {
        color: #CADBF2;
        text-decoration: underline;
    }

    /* Hide icon on mobile */
    @media (max-width: 768px) {
        .profile-header__icon {
            display: none;
        }

        .profile-header__content {
            flex-direction: column;
        }
    }
    ```
  </action>
  <verify>
    1. Flask app serves the updated index.html
    2. Font Awesome CDN loads (check browser dev tools Network tab)
    3. Profile header section exists in DOM (initially hidden)
    4. CSS renders correctly when element is made visible via dev tools
  </verify>
  <done>
    Profile header HTML structure in place with blue banner CSS styling matching OaSIS design.
  </done>
</task>

<task type="auto">
  <name>Task 2: Add API client methods and header rendering logic</name>
  <files>static/js/api.js, static/js/accordion.js</files>
  <action>
    **API Client (static/js/api.js):**

    Add two new methods to the api object:

    ```javascript
    async fetchOccupationIcon(occupationTitle, leadStatement) {
        const response = await fetch('/api/occupation-icon', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                occupation_title: occupationTitle,
                lead_statement: leadStatement
            })
        });
        if (!response.ok) return { icon_class: 'fa-briefcase' };
        return response.json();
    },

    async fetchOccupationDescription(occupationTitle, leadStatement, mainDuties) {
        const response = await fetch('/api/occupation-description', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                occupation_title: occupationTitle,
                lead_statement: leadStatement,
                main_duties: mainDuties || []
            })
        });
        if (!response.ok) return { description: '' };
        return response.json();
    }
    ```

    **Header Rendering (static/js/accordion.js):**

    Add a new function `renderProfileHeader(profile)`:

    ```javascript
    const renderProfileHeader = async (profile) => {
        const header = document.getElementById('profile-header');
        const titleEl = document.getElementById('profile-title');
        const badgeEl = document.getElementById('profile-code-badge');
        const leadEl = document.getElementById('profile-lead-statement');
        const descEl = document.getElementById('profile-description');
        const iconEl = document.getElementById('profile-icon');
        const linkEl = document.getElementById('profile-link');
        const timestampEl = document.getElementById('profile-timestamp');

        // Set static content immediately
        titleEl.textContent = profile.title;
        badgeEl.textContent = profile.noc_code;
        leadEl.textContent = profile.reference_attributes?.lead_statement || '';
        linkEl.href = profile.metadata?.profile_url || '#';
        timestampEl.textContent = new Date().toLocaleDateString();

        // Show header
        header.classList.remove('hidden');

        // Extract main duties for description generation
        const mainDuties = (profile.key_activities?.statements || [])
            .filter(s => s.source_attribute === 'Main Duties')
            .map(s => s.text)
            .slice(0, 5);

        const leadStatement = profile.reference_attributes?.lead_statement || profile.title;

        // Fetch icon and description in parallel (non-blocking)
        Promise.all([
            api.fetchOccupationIcon(profile.title, leadStatement),
            api.fetchOccupationDescription(profile.title, leadStatement, mainDuties)
        ]).then(([iconResult, descResult]) => {
            // Update icon
            const iconClass = iconResult.icon_class || 'fa-briefcase';
            iconEl.className = `fas ${iconClass}`;

            // Update description
            if (descResult.description) {
                descEl.textContent = descResult.description;
            }
        }).catch(err => {
            console.warn('LLM enrichment failed:', err);
            // Keep defaults - graceful degradation
        });
    };

    // Export for use by search.js
    window.renderProfileHeader = renderProfileHeader;
    ```

    Modify the existing `renderAccordions` function to call `renderProfileHeader` first:

    In the function body, add at the beginning:
    ```javascript
    // Render profile header with LLM enrichment
    renderProfileHeader(profile);
    ```
  </action>
  <verify>
    1. Search for an occupation (e.g., "pilot")
    2. Select a profile from results
    3. Blue banner header appears with:
       - Title (immediate)
       - Code badge (immediate)
       - Lead statement (immediate)
       - Icon updates after LLM response (~1-2 seconds)
       - Description appears after LLM response (~2-3 seconds)
    4. Check browser console for any errors
  </verify>
  <done>
    Profile header renders with static content immediately, then enriches with LLM-driven icon and description.
  </done>
</task>

</tasks>

<verification>
1. Search for "data scientist" and select a profile
2. Blue banner header displays immediately with title, code badge, lead statement
3. Icon updates from default briefcase to context-appropriate icon (e.g., atom for data scientist)
4. Description paragraph appears below lead statement
5. Responsive: icon hidden on mobile widths
6. Source link opens correct OASIS page in new tab
</verification>

<success_criteria>
- [ ] Blue banner header with correct styling (#003366 gradient)
- [ ] Occupation title displays large and white
- [ ] OaSIS code badge displays below title with translucent background
- [ ] Lead statement displays from NOC data
- [ ] LLM-generated description displays in italics
- [ ] Icon displays on right side with light blue color (#CADBF2)
- [ ] Icon updates dynamically after LLM response
- [ ] Description updates dynamically after LLM response
- [ ] Graceful degradation: header works even if LLM fails
- [ ] Responsive: icon hidden on mobile
</success_criteria>

<output>
After completion, create `.planning/phases/08-C-profile-page-tabs/08-C-02-SUMMARY.md`
</output>
