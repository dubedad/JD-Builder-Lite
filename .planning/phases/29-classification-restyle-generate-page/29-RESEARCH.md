# Phase 29: Classification Restyle + Generate Page - Research

**Researched:** 2026-03-12
**Domain:** Frontend UI restyle (HTML/CSS/JS) + backend data model gaps for Classification and Generate pages
**Confidence:** HIGH (all findings are from direct codebase inspection; screenshots are the v5.1 authoritative spec)

---

## Summary

Phase 29 requires two parallel work streams: (1) restyling the existing `#classify-section` to match the v5.1 chrome — adding an occupation header card with DADM/Full Provenance badges, a TBS dark-navy 3-step card, a post-analysis result card with a Statement Alignment Comparison two-column layout, Key Evidence bullets, Caveats bullets, Alternative Groups Considered text, and a Next Step box; (2) replacing the existing `#overview-section` with a fully redesigned Generate page that has a "Generate AI Overview" card, DADM Level 2 / Human Review Required badges, a yellow DADM Compliance Notice, an optional Additional Context textarea, a "Generate with AI" button, and AI-generated prose below with an "AI Generated" badge and Regenerate button.

The **classification backend** (the `/api/allocate` route and the `GroupRecommendation` model) is missing three fields the v5.1 UI needs: `alignment_comparison`, `caveats`, and `next_step_guidance`. The model already carries `evidence_spans` (which maps to Key Evidence), `confidence` (which maps to the green progress bar and 95% score), `definition_fit_rationale` (summary sentence), and via the provenance_map the TBS Definition link. The missing fields must be added to the allocator LLM prompt output and surfaced through the API response.

The **generate page** can reuse `generate.js` with a light wrapper — the SSE streaming infrastructure, `startGeneration()`, `consumeStream()`, `handleSSEMessage()`, and `resetGeneratingState()` are all solid. The HTML must be completely replaced (the current `#overview-section` structure does not match the v5.1 spec), and the existing `generate-btn` DOM ID convention must be preserved or `generate.js` updated in parallel.

**Primary recommendation:** Complete the classify restyle as 29-01 (HTML/CSS in `#classify-section` + two new JS helper functions in `classify.js` + minimal backend additions to the allocator prompt + `GroupRecommendation` model), and the generate page redesign as 29-02 (HTML replacement in `#overview-section` + CSS additions in `overview.css` + minor DOM-ID wiring update in `generate.js`).

---

## Standard Stack

### Core (already in use — no new installs)
| Library/Pattern | Version | Purpose | Why Used |
|---|---|---|---|
| Vanilla JS IIFE modules | n/a | Page logic (`classify.js`, `generate.js`) | All existing JS follows this pattern |
| Flask SSE streaming | current | `/api/generate` token streaming | Already wired; `generate.js` consumes it |
| OpenAI via `llm_service.py` | current | Text generation | Confirmed in `api.py` line 14, `generate_stream()` |
| Pydantic `BaseModel` | v2 | API request/response models | All models use this |
| CSS custom properties | n/a | Design tokens in `:root` | `main.css` has the full set |
| Font Awesome | 6.x (CDN) | Icons throughout the app | Used in every module |

### Supporting (design tokens already defined)
| Token | Value | Purpose |
|---|---|---|
| `--app-bar-bg` | `#26374a` | TBS dark navy card background |
| `--badge-green-bg` / `--badge-green-text` | `#d4edda` / `#155724` | DADM Compliant badge |
| `--pill-oasis-bg` | `#6f42c1` | Full Provenance purple badge |
| `--gc-red` | `#af3c43` | Not used for the CTA; orange `#f5a623` is what screenshots show |

**No new npm/pip packages required for this phase.**

---

## Architecture Patterns

### Recommended File Changes
```
templates/index.html         — Replace #classify-section and #overview-section HTML
static/css/classify.css      — Add new post-analysis sections CSS
static/css/overview.css      — Replace with v5.1 Generate page CSS
static/js/classify.js        — Add renderTopResultCard(), renderPostAnalysis() functions
static/js/generate.js        — Update DOM element IDs to match new HTML
src/matching/models.py       — Add caveats, alignment_comparison, next_step_guidance fields to GroupRecommendation
src/matching/classifier.py   — Update LLM prompt to return new fields (or populate in allocator.py)
```

### Pattern 1: Classification Page — Two Rendering Phases

The v5.1 Classification page has two distinct rendering phases:

**Pre-analysis (step 3 entry, before "Analyze" button clicked):**
- Occupation header card with icon, title "Occupational Group Allocation", subtitle "Classification Step 1 — Per TBS Directive on Classification"
- DADM Compliant badge (green) + Full Provenance badge (purple/link icon) — top-right of header card
- Dark-navy TBS Prescribed Allocation Method card with three equally-wide sub-boxes (§4.1.1, §4.1.2, §4.1.3)
- Large full-width orange "Analyze & Recommend Occupational Group" button

The current HTML wires to `triggerClassification()` automatically when navigating to step 3. The new design needs a button the user can see and click. The current flow auto-fires on step entry. **Decision for planner:** the auto-trigger on step entry should be preserved (same as today) but the button should still be visible as a "re-analyze" affordance.

**Post-analysis (after API returns):**
- Same occupation header card + badges + TBS card
- Same orange Analyze button (still visible)
- New result card below: `{confidence}% {group_code} – {group_name}` heading + "Recommended Occupational Group" subtitle + TBS Definition link top-right + green progress bar
- Summary sentence (from `definition_fit_rationale`)
- Statement Alignment Comparison (CLASS-02): two-column layout
- Key Evidence (CLASS-03): green check bullets from `evidence_spans`
- Caveats (CLASS-03): amber warning bullets (NEW API FIELD)
- Alternative Groups Considered (CLASS-03): `EL – Electronics (25%)` — from other `recommendations[]` entries
- Next Step box (CLASS-04): blue-tinted box with bold link text (NEW API FIELD or static per group_code)
- Back to Edit | Continue to Generate nav buttons at the bottom

### Pattern 2: Generate Page — Card-Wrapper Layout

From screenshot 4.0, the Generate page is a single white card:
- Card header row: "Generate AI Overview" (title) + "DADM Level 2" orange badge + "Human Review Required" red/danger badge
- Subtitle: "AI-generated content is logged per TBS Directive on Automated Decision-Making."
- Yellow warning box: "DADM Compliance Notice" — "This AI-generated content has **moderate impact**. Human review is required before use."
- "Additional Context (optional)" label + textarea (placeholder: "Department-specific requirements, organizational context...")
- Dark-navy full-width "Generate with AI" button (pencil icon)
- "Generated Overview" section header + "AI Generated" blue badge (appears after generation)
- Multi-paragraph prose display (either readonly textarea or div)
- "Regenerate" | "Continue" nav buttons at the bottom

The existing `generate.js` uses `#generate-btn` — the new HTML must use that same ID OR `generate.js` must be updated. Looking at the code: `generate.js` references `#generate-btn`, `#regenerate-btn`, `#overview-textarea`, `#ai-badge`, `#overview-error`. The new HTML will need to either preserve these IDs or update `generate.js.elements` to match new IDs.

### Pattern 3: New API Fields for Classification

The v5.1 post-analysis spec requires:
1. **`caveats`**: List of strings (amber warning bullets). Not in current `GroupRecommendation`. Must be added.
2. **`alignment_comparison`**: Object with `selected_statements: List[str]` and `og_definition_statements: List[str]` and `alignment_score: int`. Not in current model. The "Your Selected Statements" column comes from the frontend (known: `jdData.key_activities`). The "OG Definition Statements" column comes from the TBS group definition (available in `allocator.py` Step 1 from the database). The score is the count of aligned statements.
3. **`next_step_guidance`**: Object with `instructions: str` and `links: List[{text: str, url: str}]`. Can be computed statically per `group_code` (a lookup table in the allocator or a static JS object) OR returned from the LLM.

**Simplest approach for `alignment_comparison`:** The frontend already has `jdData.key_activities` (user's selected statements). The OG definition statements are the inclusions/definition text already stored in the database for each group. The allocator already loads these to run matching. The planner should add a field to `GroupRecommendation` that carries both sides.

**Simplest approach for `next_step_guidance`:** Static lookup table in `classify.js` keyed by `group_code`, linking to the appropriate TBS Job Evaluation Standard URL. The content in screenshot 3.1 reads: "Apply the **Information Technology Job Evaluation Standard** to determine the level within IT." — this is a static template per group. No LLM call needed.

**Simplest approach for `caveats`:** The LLM classifier (`classifier.py`) already generates rationale and evidence; adding a `caveats: List[str]` field to the structured output prompt is minimal work.

### Anti-Patterns to Avoid

- **Do not put the orange CTA button inside the results-only `#classify-results` div.** The button must always be visible (pre- and post-analysis). It should be rendered outside the hidden/shown results block.
- **Do not replace generate.js wholesale.** The SSE streaming logic is solid. Only update the DOM element IDs in `generation.elements` init block and add the new Additional Context textarea value to the POST body.
- **Do not create a new API route for classification.** The existing `/api/allocate` route is sufficient; just add new fields to the response model.
- **Do not hard-code alignment score as 0.** The score should reflect actual matched statements (even if simplistically computed by the allocator or frontend).

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---|---|---|---|
| SSE token streaming | Custom EventSource | Existing `consumeStream()` in `generate.js` | Already works perfectly |
| Badge styling | New badge CSS | Existing `--badge-green-bg`, `--badge-green-text`, `--pill-oasis-bg` tokens | Tokens already defined and used across the app |
| TBS definition links | Scraping or LLM | Static lookup table per group_code | These URLs are stable government pages; a 40-line JS object is better than any dynamic approach |
| Statement list for left column | New API field | Read from `window.currentJdData` already assembled in `classify.js` | `buildJdDataFromProfile()` returns `key_activities` — already available |

---

## Common Pitfalls

### Pitfall 1: The "Analyze" Button vs. Auto-trigger

**What goes wrong:** The current flow auto-fires classification when entering step 3. The new UI shows an "Analyze & Recommend Occupational Group" orange button — if you just add the button but keep auto-fire, classification runs twice.

**Why it happens:** `navigateToStep(3)` in `main.js` calls `triggerClassification()` unconditionally (except on cache hit). Adding a button that also calls it creates a double-fire.

**How to avoid:** Keep the auto-fire on step entry (for UX consistency), but show the button as a "Re-analyze" affordance. OR keep the button as the only trigger and remove the auto-fire. The phase-29 planner must make this call explicitly.

**Warning signs:** Two API calls in network tab when navigating to step 3.

### Pitfall 2: generate.js DOM Element ID Mismatch

**What goes wrong:** Renaming HTML element IDs in the new Generate page without updating `generate.js` breaks the generation button.

**Why it happens:** `generate.js` init() caches DOM elements by ID: `#generate-btn`, `#regenerate-btn`, `#overview-textarea`, `#ai-badge`, `#overview-error`.

**How to avoid:** Either (a) preserve these exact IDs in the new HTML, or (b) update `generate.js` init() to use the new IDs. Option (a) is simpler.

**Warning signs:** "Generate with AI" button click does nothing; console error "Cannot read properties of null".

### Pitfall 3: Caveats and Alignment Comparison Are New Model Fields

**What goes wrong:** Planner assumes these can be derived purely on the frontend and skips the backend model change. The OG Definition Statements column requires data from the database (group definition sentences), which the frontend cannot compute.

**Why it happens:** Some fields look derivable from existing data but actually require new backend output.

**How to avoid:** Add `caveats: List[str]` and `og_definition_statements: List[str]` to `GroupRecommendation` in `src/matching/models.py`, update the LLM prompt in `classifier.py` to populate them, and add `alignment_comparison` as a computed field in the allocator.

**Warning signs:** Column "IT Definition Statements" is empty or shows placeholder text.

### Pitfall 4: CSS Specificity Conflicts in classify.css

**What goes wrong:** Adding new CSS classes for the post-analysis result card conflicts with existing `.recommendation-card` styles.

**Why it happens:** `classify.css` already has `.recommendation-card` as the primary card style; the new top-result display card is visually different (larger, shows confidence %, green bar).

**How to avoid:** Use distinct class names for the new result card (`classify-result-card`, `classify-result-card__confidence`, etc.) rather than overriding existing `.recommendation-card`.

### Pitfall 5: Two-Column Layout Alignment Score Computation

**What goes wrong:** `Overall Alignment Score: 0/8 statements aligned` is shown in the screenshot even though some evidence spans exist — it appears the score is computed as a specific matching step, not just counting evidence_spans.

**Why it happens:** The alignment comparison is between the user's selected *labeled* statements and the OG's textual definition sentences — they don't literally match as substrings, the comparison is semantic.

**How to avoid:** For v5.1, compute alignment score as `evidence_spans.length` / `selected_statements.length` (evidence spans are already the matched portions). If no semantic match is available, default to 0. Document that this is an approximation.

---

## Code Examples

### Occupation Header Card (verified from screenshot 3.1 inspection)

```html
<!-- Source: screenshot 3.1 Classified.png analysis -->
<div class="classify-occupation-header">
    <div class="classify-occupation-icon">
        <i class="fas fa-sitemap"></i>
    </div>
    <div class="classify-occupation-info">
        <h2 class="classify-occupation-title">Occupational Group Allocation</h2>
        <p class="classify-occupation-subtitle">Classification Step 1 — Per TBS Directive on Classification</p>
    </div>
    <div class="classify-occupation-badges">
        <span class="badge badge--dadm-compliant">
            <i class="fas fa-check-circle"></i> DADM Compliant
        </span>
        <a href="#" class="badge badge--full-provenance">
            <i class="fas fa-link"></i> Full Provenance
        </a>
    </div>
</div>
```

### TBS Dark Card (verified from screenshots 3.0 and 3.1)

```html
<!-- Source: screenshots 3.0 and 3.1 inspection -->
<div class="classify-tbs-method-card">
    <div class="classify-tbs-method-header">
        <i class="fas fa-th-list"></i> TBS Prescribed Allocation Method
    </div>
    <div class="classify-tbs-method-steps">
        <div class="classify-tbs-step">
            <strong>§4.1.1 Primary Purpose</strong>
            <p>Determine why the position exists</p>
        </div>
        <div class="classify-tbs-step">
            <strong>§4.1.2 Definition Fit</strong>
            <p>Match work to OG definitions</p>
        </div>
        <div class="classify-tbs-step">
            <strong>§4.1.3 Inclusions/Exclusions</strong>
            <p>Verify alignment and conflicts</p>
        </div>
    </div>
</div>
```

```css
/* Source: design tokens in main.css + screenshot color inspection */
.classify-tbs-method-card {
    background: var(--app-bar-bg); /* #26374a dark navy */
    border-radius: 8px;
    padding: 1.5rem;
    margin: 1.5rem 0;
    color: white;
}
.classify-tbs-method-header {
    font-weight: 600;
    font-size: 1rem;
    margin-bottom: 1rem;
}
.classify-tbs-method-steps {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.75rem;
}
.classify-tbs-step {
    background: rgba(255,255,255,0.08);
    border-radius: 6px;
    padding: 1rem;
}
.classify-tbs-step strong {
    display: block;
    margin-bottom: 0.25rem;
    font-size: 0.9375rem;
}
.classify-tbs-step p {
    font-size: 0.875rem;
    color: rgba(255,255,255,0.75);
    margin: 0;
}
```

### Badge Patterns (verified from main.css token inspection)

```css
/* Source: main.css design tokens, confirmed by screenshot badge colors */
.badge--dadm-compliant {
    display: inline-flex;
    align-items: center;
    gap: 0.375rem;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.8125rem;
    font-weight: 500;
    background: var(--badge-green-bg);   /* #d4edda */
    color: var(--badge-green-text);       /* #155724 */
    border: 1px solid #b1dfbb;
}
.badge--full-provenance {
    display: inline-flex;
    align-items: center;
    gap: 0.375rem;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.8125rem;
    font-weight: 500;
    background: #ede7f6;
    color: var(--pill-oasis-bg);          /* #6f42c1 purple */
    border: 1px solid #d1c4e9;
    text-decoration: none;
}
```

### Statement Alignment Comparison (two-column, from screenshot 3.1)

```html
<!-- Source: screenshot 3.1 Classified.png — two-column layout -->
<div class="classify-alignment-section">
    <h3 class="classify-section-heading">
        <i class="fas fa-columns"></i> Statement Alignment Comparison
    </h3>
    <div class="classify-alignment-columns">
        <div class="classify-alignment-col classify-alignment-col--left">
            <div class="classify-alignment-col-header">
                <i class="fas fa-user"></i> Your Selected Statements
            </div>
            <ul class="classify-alignment-list" id="alignment-selected"></ul>
        </div>
        <div class="classify-alignment-col classify-alignment-col--right">
            <div class="classify-alignment-col-header classify-alignment-col-header--og">
                <i class="fas fa-book"></i> IT Definition Statements
            </div>
            <ul class="classify-alignment-list classify-alignment-list--og" id="alignment-og"></ul>
        </div>
    </div>
    <div class="classify-alignment-score">
        <span>Overall Alignment Score</span>
        <span class="classify-alignment-score-value" id="alignment-score">0/8 statements aligned</span>
    </div>
</div>
```

### Key Evidence + Caveats (from screenshot 3.1)

```html
<!-- Source: screenshot 3.1 — green check bullets for Evidence, amber for Caveats -->
<div class="classify-key-evidence">
    <h3 class="classify-section-heading">Key Evidence</h3>
    <ul class="classify-evidence-list" id="key-evidence-list">
        <!-- JS renders: <li><i class="fas fa-check-circle classify-evidence-icon--green"></i> text</li> -->
    </ul>
</div>
<div class="classify-caveats">
    <div class="classify-caveats-box">
        <div class="classify-caveats-header">
            <i class="fas fa-exclamation-triangle classify-caveats-icon"></i>
            <strong>Caveats</strong>
        </div>
        <ul class="classify-caveats-list" id="caveats-list">
            <!-- JS renders: <li>caveat text</li> -->
        </ul>
    </div>
</div>
```

### Generate Page — New HTML Structure (verified from screenshot 4.0)

```html
<!-- Source: screenshot 4.0 Generate.png — full card structure -->
<section id="overview-section" class="overview-section hidden">
    <div class="generate-card">
        <!-- Card Header -->
        <div class="generate-card-header">
            <h2 class="generate-card-title">Generate AI Overview</h2>
            <div class="generate-card-badges">
                <span class="badge badge--dadm-level2">DADM Level 2</span>
                <span class="badge badge--human-review">Human Review Required</span>
            </div>
        </div>
        <p class="generate-card-subtitle">
            AI-generated content is logged per TBS Directive on Automated Decision-Making.
        </p>

        <!-- DADM Compliance Notice -->
        <div class="generate-dadm-notice">
            <div class="generate-dadm-notice-header">
                <i class="fas fa-exclamation-triangle"></i>
                <strong>DADM Compliance Notice</strong>
            </div>
            <p>This AI-generated content has <strong>moderate impact</strong>. Human review is required before use.</p>
        </div>

        <!-- Additional Context -->
        <div class="generate-context-field">
            <label class="generate-context-label" for="additional-context">Additional Context (optional)</label>
            <textarea
                id="additional-context"
                class="generate-context-textarea"
                placeholder="Department-specific requirements, organizational context..."
                rows="4"
            ></textarea>
        </div>

        <!-- Generate button -->
        <button id="generate-btn" class="generate-btn" type="button">
            <i class="fas fa-pencil-alt"></i> Generate with AI
        </button>

        <!-- Generated Output (hidden until generation completes) -->
        <div id="generate-output" class="generate-output hidden">
            <div class="generate-output-header">
                <span class="generate-output-title">Generated Overview</span>
                <span id="ai-badge" class="ai-badge">AI Generated</span>
            </div>
            <div id="overview-textarea" class="generate-output-prose"></div>
        </div>

        <div id="overview-error" class="overview-error hidden" role="alert"></div>

        <!-- Nav buttons -->
        <div class="generate-nav-actions">
            <button class="btn btn--secondary" id="generate-regenerate" id="regenerate-btn" type="button">
                <i class="fas fa-redo"></i> Regenerate
            </button>
            <button class="btn btn--primary" id="generate-continue" type="button">
                Continue <i class="fas fa-arrow-right"></i>
            </button>
        </div>
    </div>
</section>
```

**IMPORTANT NOTE:** The existing `generate.js` appends tokens to `elements.textarea.value` (a `<textarea>`). The new design shows prose as a `<div>`. Two options:
- Keep `#overview-textarea` as a hidden `<textarea>` for JS compatibility, display a parallel `<div>` styled as prose — sync them.
- Change `generate.js` to append to `innerHTML` of a `<div>` — simpler but requires updating `generate.js` method.

The planner should pick: **update `generate.js` to use `textContent +=` on a `<div>` element** — this is cleaner than maintaining two parallel elements. The `textarea` was used for user editing; in v5.1 the design shows prose output that is not explicitly shown as editable in the screenshot.

### generate.js DOM IDs to Preserve or Update

Current `generate.js` init() references:
```javascript
// Source: static/js/generate.js lines 24-31
section: document.getElementById('overview-section'),    // PRESERVE
textarea: document.getElementById('overview-textarea'),  // Can change to div
badge: document.getElementById('ai-badge'),              // PRESERVE
generateBtn: document.getElementById('generate-btn'),    // PRESERVE
regenerateBtn: document.getElementById('regenerate-btn'), // PRESERVE (note: HTML has both 'regenerate-btn' and 'generate-regenerate')
errorDiv: document.getElementById('overview-error')      // PRESERVE
```

Current HTML has TWO regenerate buttons (`#regenerate-btn` and `#generate-regenerate`). `generate.js` binds to `#regenerate-btn`. `main.js` binds `#generate-regenerate` to `window.generation.startGeneration()`. In the new HTML, one button should serve both: use `id="regenerate-btn"` as the primary and also add the `generate-regenerate` handler in `main.js`.

---

## State of the Art

| Old Approach | Current Approach | Notes |
|---|---|---|
| `#classify-section` plain header + status badge | v5.1 occupation header card with icon + dual badges | Phase 29 adds the new header card |
| `#overview-section` minimal textarea + Regenerate | v5.1 Generate page card with compliance notices | Full replace in Phase 29 |
| No Statement Alignment Comparison | Two-column layout with OG definition sentences | Requires new API field `og_definition_statements` |
| No Caveats section | Amber warning bullets from LLM | Requires new `caveats` field in `GroupRecommendation` |
| No Next Step box | Blue-tinted instructional box per group_code | Can be static lookup table in `classify.js` |

---

## Open Questions

1. **Auto-trigger vs. button-only for classification**
   - What we know: current flow auto-fires on step 3 entry; v5.1 shows an "Analyze" button
   - What's unclear: should auto-fire be preserved (button = re-analyze) or removed (button = only trigger)?
   - Recommendation: preserve auto-fire, label the button "Re-analyze" when results exist; first analysis fires automatically as before

2. **OG Definition Statements data source**
   - What we know: screenshot shows 7-8 sentences in the IT Definition Statements column (e.g. "Designs, develops, and maintains IT systems")
   - What's unclear: are these the TBS definition sentences already stored in `dim_occupational_group`, or are they LLM-generated?
   - Recommendation: inspect `src/storage/repository.py` and the database schema to verify the definition text is stored; if yes, pass it through as a new `og_definition_statements: List[str]` field in `GroupRecommendation`

3. **`overview-textarea` vs. `<div>` for generated prose**
   - What we know: current `generate.js` treats it as a textarea (`.value +=`); v5.1 screenshot shows prose paragraphs
   - What's unclear: should the user be able to edit the generated text?
   - Recommendation: change the element to a `<div contenteditable="true">` and update `generate.js` to use `.textContent +=` during streaming and `handleEdit()` to fire on `input` event

---

## Sources

### Primary (HIGH confidence)
- Direct codebase inspection: `static/js/classify.js` (954 lines), `static/js/generate.js` (307 lines), `static/js/main.js` (~891 lines)
- `src/routes/api.py` — full route definitions, confirmed `/api/allocate` and `/api/generate` routes
- `src/models/allocation.py` + `src/matching/models.py` — full data model inspection
- `static/css/classify.css` (902 lines), `static/css/overview.css` (145 lines), `static/css/main.css` (design tokens section)
- `templates/index.html` lines 291-498 — current classify and overview section HTML

### Secondary (HIGH confidence from screenshots)
- `.planning/ui-walkthrough-v5.1/screenshots/3.0 Classification.png` — pre-analysis state visual spec
- `.planning/ui-walkthrough-v5.1/screenshots/3.1 Classified.png` — post-analysis state visual spec (authoritative for all CLASS-01 through CLASS-04)
- `.planning/ui-walkthrough-v5.1/screenshots/4.0 Generate.png` — generate page visual spec (authoritative for GEN-01 through GEN-04)

---

## Metadata

**Confidence breakdown:**
- Classification HTML/CSS structure: HIGH — screenshots are authoritative, no guesswork
- Generate page HTML/CSS structure: HIGH — screenshot 4.0 is clear
- API backend gaps (caveats, og_definition_statements): HIGH — confirmed by model inspection; fields are absent
- Next Step guidance approach (static lookup vs LLM): MEDIUM — static is feasible; content for each group_code needs to be authored
- `generate.js` compatibility: HIGH — all ID references confirmed by code inspection
- OG Definition Statements data source: MEDIUM — needs `repository.py` inspection to confirm definition text is stored in DB

**Research date:** 2026-03-12
**Valid until:** 2026-04-12 (stable codebase)
