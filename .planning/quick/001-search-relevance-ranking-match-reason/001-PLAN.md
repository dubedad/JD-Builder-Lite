---
phase: quick
plan: 001
type: execute
wave: 1
depends_on: []
files_modified:
  - src/models/noc.py
  - src/routes/api.py
  - static/js/main.js
  - static/css/results-cards.css
  - .planning/PROJECT.md
autonomous: true

must_haves:
  truths:
    - "Search results are sorted by relevance: title matches first, then lead statement matches, then alternate job title matches"
    - "Each result card shows a match-reason indicator explaining why this result appeared"
    - "Existing sort dropdown 'Matching search criteria' option uses relevance scoring"
  artifacts:
    - path: "src/models/noc.py"
      provides: "relevance_score and match_reason fields on EnrichedSearchResult"
      contains: "relevance_score"
    - path: "src/routes/api.py"
      provides: "Relevance scoring logic and sorted results"
      contains: "relevance_score"
    - path: "static/js/main.js"
      provides: "Match reason display on cards and relevance-aware sorting"
      contains: "match_reason"
    - path: "static/css/results-cards.css"
      provides: "Styling for match-reason indicator"
      contains: "match-reason"
  key_links:
    - from: "src/routes/api.py"
      to: "src/models/noc.py"
      via: "Sets relevance_score and match_reason on each EnrichedSearchResult"
      pattern: "relevance_score"
    - from: "static/js/main.js"
      to: "result.match_reason"
      via: "Reads match_reason from API response to render indicator"
      pattern: "match_reason"
---

<objective>
Add search relevance scoring and match-reason display to search results.

Purpose: OASIS returns results matched on hidden alternate job titles, causing confusing results (e.g., "Printer" returning "Athletes" because "Sprinter" contains "printer"). Scoring and sorting by where the search term actually matched — title, lead statement, or alternate title — surfaces the most relevant results first and explains why each result appeared.

Output: Modified backend scoring in the API route, new fields on EnrichedSearchResult, sorted API response, match-reason indicators on result cards, updated PROJECT.md.
</objective>

<execution_context>
@C:\Users\Administrator\.claude/get-shit-done/workflows/execute-plan.md
@C:\Users\Administrator\.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@src/models/noc.py
@src/routes/api.py
@src/services/parser.py
@static/js/main.js
@static/css/results-cards.css
</context>

<tasks>

<task type="auto">
  <name>Task 1: Add relevance scoring fields and backend sorting logic</name>
  <files>
    src/models/noc.py
    src/routes/api.py
  </files>
  <action>
    1. In `src/models/noc.py`, add two new Optional fields to `EnrichedSearchResult`:
       - `relevance_score: Optional[int] = None` — integer score (3 = title match, 2 = lead statement match, 1 = alternate job title match)
       - `match_reason: Optional[str] = None` — human-readable label: "Title match", "Description match", or "Alternate job title"

    2. In `src/routes/api.py`, in the `search()` function, AFTER `results = parser.parse_search_results_enhanced(html)` and BEFORE creating the SearchResponse:

       Add a scoring loop that iterates over each result and computes relevance:
       ```python
       # Score results by where the search term matches
       query_lower = query.lower()
       for result in results:
           if query_lower in result.title.lower():
               result.relevance_score = 3
               result.match_reason = "Title match"
           elif result.lead_statement and query_lower in result.lead_statement.lower():
               result.relevance_score = 2
               result.match_reason = "Description match"
           else:
               result.relevance_score = 1
               result.match_reason = "Alternate job title"

       # Sort by relevance score descending (best matches first)
       results.sort(key=lambda r: r.relevance_score or 0, reverse=True)
       ```

       This goes between line 89 (`results = parser.parse_search_results_enhanced(html)`) and line 92 (`response = SearchResponse(...)`).

       IMPORTANT: Do NOT modify parser.py. The scoring belongs in the route because it needs the original search query, which the parser does not have access to.
  </action>
  <verify>
    Run `python -c "from src.models.noc import EnrichedSearchResult; r = EnrichedSearchResult(noc_code='12345', title='Test', url='/test', relevance_score=3, match_reason='Title match'); print(r.relevance_score, r.match_reason)"` — should print "3 Title match".

    Run the Flask app and search for "Printer" via browser or curl: `curl "http://localhost:5000/api/search?q=Printer"` — verify response JSON includes `relevance_score` and `match_reason` fields on each result, and results are sorted with title matches first.
  </verify>
  <done>
    Every search result in the API response includes `relevance_score` (1-3) and `match_reason` (string). Results are sorted by relevance_score descending. The EnrichedSearchResult model accepts both new fields.
  </done>
</task>

<task type="auto">
  <name>Task 2: Display match reason on result cards and wire up relevance sort</name>
  <files>
    static/js/main.js
    static/css/results-cards.css
  </files>
  <action>
    1. In `static/js/main.js`, in the `renderCardView()` function, add a match-reason indicator inside the `.card-footer` div. Replace the existing card-footer block (the last section of the card HTML template, around lines 344-351) with:

       ```javascript
       <div class="card-footer">
           ${result.match_reason ? `
           <span class="match-reason match-reason--${result.relevance_score === 3 ? 'high' : result.relevance_score === 2 ? 'medium' : 'low'}">
               ${escapeHtml(result.match_reason)}
           </span>
           ` : ''}
           <i class="fa fa-search card-icon" aria-hidden="true"></i>
           <span class="card-text">
               <span class="matching-label">Matching search criteria</span>
               ${result.matching_criteria ? `<br><span class="matching-value">${escapeHtml(result.matching_criteria)}</span>` : ''}
           </span>
       </div>
       ```

    2. In the sort dropdown handler (`sortSelect.addEventListener('change', ...)`), update the `'match'` case (around line 690-692) to sort by relevance_score instead of preserving original order:

       ```javascript
       case 'match':
       default:
           // Sort by relevance score (highest first)
           sorted.sort((a, b) => (b.relevance_score || 0) - (a.relevance_score || 0));
           break;
       ```

       This ensures that after filtering (which may reorder results), selecting "Matching search criteria" re-sorts by relevance.

    3. In `static/css/results-cards.css`, add styles for the match-reason indicator at the end of the file:

       ```css
       /* Match Reason Indicator */
       .match-reason {
           display: inline-block;
           font-size: 0.7rem;
           font-weight: 600;
           text-transform: uppercase;
           letter-spacing: 0.03em;
           padding: 0.15rem 0.5rem;
           border-radius: 3px;
           margin-bottom: 0.4rem;
           float: right;
       }

       .match-reason--high {
           background-color: #d4edda;
           color: #155724;
       }

       .match-reason--medium {
           background-color: #fff3cd;
           color: #856404;
       }

       .match-reason--low {
           background-color: #f8d7da;
           color: #721c24;
       }
       ```

       Color semantics: green = title match (most relevant), amber = description match, red-ish = alternate job title (least relevant, likely the confusing result).
  </action>
  <verify>
    Run the Flask app, search for "Printer" in the browser. Verify:
    1. Each result card shows a colored match-reason badge in the card footer
    2. Results with "Title match" (green) appear before "Description match" (amber) before "Alternate job title" (pinkish)
    3. The sort dropdown "Matching search criteria" option sorts by relevance score
    4. No console errors in browser dev tools
  </verify>
  <done>
    Result cards display a colored match-reason indicator. Title matches are visually distinct (green) from alternate job title matches (red-ish). Sort-by-match uses the new relevance_score field.
  </done>
</task>

<task type="auto">
  <name>Task 3: Update PROJECT.md with new requirement and key decision</name>
  <files>
    .planning/PROJECT.md
  </files>
  <action>
    1. In the `### Validated` section, under the `**v2.0 UI Redesign:**` block (after `DISP-34`), add a new requirement:
       - `- SRCH-13: Search results scored by relevance (title > description > alternate title) and sorted best-first with match-reason indicator -- v2.0`

       Use the checkmark format consistent with the other entries: `- ✓ SRCH-13: ...`

    2. In the `## Key Decisions` table, add a new row:
       ```
       | Relevance scoring in API route (not parser) | Parser lacks query context; route has both query and results for scoring | ✓ Good |
       ```

    3. Update the `*Last updated:` line at the bottom to today's date and note.
  </action>
  <verify>
    Read `.planning/PROJECT.md` and confirm:
    - SRCH-13 requirement is present in Validated section under v2.0
    - New key decision row exists in the table
    - Last updated line reflects current date
  </verify>
  <done>
    PROJECT.md documents the search relevance scoring feature as a validated requirement (SRCH-13) and records the architectural decision to score in the route rather than the parser.
  </done>
</task>

</tasks>

<verification>
1. Start Flask app: `python app.py` (or however the app starts)
2. Search for "Printer" — verify results sorted with direct title matches first, alternate title matches last
3. Each card shows a match-reason badge with appropriate color
4. Sort dropdown "Matching search criteria" option works correctly
5. Search for a common term like "Engineer" — verify title matches (e.g., "Software Engineers") appear before description/alternate matches
6. API response at `/api/search?q=Printer` includes `relevance_score` and `match_reason` in JSON
</verification>

<success_criteria>
- API returns `relevance_score` (1-3) and `match_reason` (string) on every search result
- Results are sorted by relevance_score descending by default
- Result cards display a color-coded match-reason indicator
- PROJECT.md updated with SRCH-13 requirement and scoring decision
- No regressions in existing search, filter, or card/grid view functionality
</success_criteria>

<output>
After completion, create `.planning/quick/001-search-relevance-ranking-match-reason/001-SUMMARY.md`
</output>
