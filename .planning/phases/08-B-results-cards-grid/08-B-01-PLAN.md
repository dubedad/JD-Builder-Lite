---
phase: 08-B-results-cards-grid
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - src/models/noc.py
  - src/services/parser.py
  - src/routes/api.py
  - src/models/responses.py
autonomous: true

must_haves:
  truths:
    - "Search API returns enriched results with card data points"
    - "Each result includes lead statement extracted from OaSIS HTML"
    - "Each result includes TEER description from OaSIS HTML"
    - "Each result includes broad category from OaSIS HTML"
    - "Each result includes matching criteria from OaSIS HTML"
    - "Minor group code is derived from NOC code for filtering"
  artifacts:
    - path: "src/models/noc.py"
      provides: "EnrichedSearchResult model with all card/filter fields"
      contains: "class EnrichedSearchResult"
    - path: "src/services/parser.py"
      provides: "parse_search_results_enhanced() extracting card data"
      contains: "def parse_search_results_enhanced"
    - path: "src/routes/api.py"
      provides: "Updated /api/search returning EnrichedSearchResult"
      contains: "EnrichedSearchResult"
    - path: "src/models/responses.py"
      provides: "SearchResponse using EnrichedSearchResult"
      contains: "EnrichedSearchResult"
  key_links:
    - from: "src/routes/api.py"
      to: "src/services/parser.py"
      via: "parser.parse_search_results_enhanced()"
      pattern: "parse_search_results_enhanced"
    - from: "src/services/parser.py"
      to: "src/models/noc.py"
      via: "returns List[EnrichedSearchResult]"
      pattern: "EnrichedSearchResult"
    - from: "src/routes/api.py"
      to: "src/models/responses.py"
      via: "SearchResponse with enriched results"
      pattern: "SearchResponse"
---

<objective>
Create backend infrastructure for enriched search results with all 6 card data points.

Purpose: Enable frontend to render OaSIS-style cards without additional API calls. Extract lead statement, TEER, broad category, and matching criteria from OaSIS search HTML. Derive minor group from NOC code for filtering.

Output: EnrichedSearchResult model, enhanced parser method, updated API route returning enriched data.

**Scope note:** This plan extracts data available from search results HTML. Fields requiring profile fetch (example_titles, mobility_progression, source_table, publication_date, top_skills, top_abilities, top_knowledge) are defined in the model but populated as None. Profile data population is deferred to Phase 08-C or a future enhancement.

**Limitation:** minor_group_name is not available from search results HTML. The field exists in the model but remains None. Only minor_group (the 3-digit code) is derived from the NOC code.
</objective>

<execution_context>
@~/.claude/get-shit-done/workflows/execute-plan.md
@~/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/08-B-results-cards-grid/08-B-RESEARCH.md
@.planning/phases/06-enhanced-ui-display/OASIS-HTML-REFERENCE.md
@src/models/noc.py
@src/services/parser.py
@src/routes/api.py
@src/models/responses.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Create EnrichedSearchResult model</name>
  <files>src/models/noc.py</files>
  <action>
Add EnrichedSearchResult model to src/models/noc.py after the existing SearchResult class (around line 26):

```python
class EnrichedSearchResult(BaseModel):
    """Enhanced search result with card data for OaSIS-style display.

    Contains all 6 data points for card view (DISP-20):
    1. lead_statement - from OaSIS card
    2. example_titles - (requires profile fetch, optional)
    3. teer_description - from OaSIS card
    4. mobility_progression - (requires profile fetch, optional)
    5. source_table - (requires profile fetch, optional)
    6. publication_date - (requires profile fetch, optional)

    Plus fields for filtering (DISP-22) and grid view (DISP-21).

    Note: Fields marked "requires profile fetch" are populated as None in this phase.
    Profile data population deferred to Phase 08-C or future enhancement.
    """
    # Core fields (same as SearchResult)
    noc_code: str
    title: str
    url: str

    # Card View Data (from OaSIS search HTML)
    lead_statement: Optional[str] = None
    teer_description: Optional[str] = None
    broad_category_name: Optional[str] = None
    matching_criteria: Optional[str] = None

    # Card View Data (requires profile fetch - optional)
    example_titles: Optional[str] = None
    mobility_progression: Optional[str] = None
    source_table: Optional[str] = None
    publication_date: Optional[str] = None

    # For Filtering (DISP-22) - derived from NOC code
    broad_category: Optional[int] = None  # First digit of NOC code
    minor_group: Optional[str] = None     # First 3 digits
    minor_group_name: Optional[str] = None  # Not available from search HTML

    # For Grid View (DISP-21) - requires profile fetch
    top_skills: Optional[List[str]] = None
    top_abilities: Optional[List[str]] = None
    top_knowledge: Optional[List[str]] = None

    model_config = ConfigDict(from_attributes=True)
```

Note: Add `List` to the imports from typing at the top of the file if not already present.
  </action>
  <verify>
Run Python to check model imports correctly:
```bash
python -c "from src.models.noc import EnrichedSearchResult; print('EnrichedSearchResult model OK')"
```
  </verify>
  <done>
EnrichedSearchResult model exists with all card data, filter, and grid view fields.
  </done>
</task>

<task type="auto">
  <name>Task 2: Create enhanced search results parser</name>
  <files>src/services/parser.py</files>
  <action>
Add parse_search_results_enhanced method to OASISParser class in src/services/parser.py.

1. First, update the imports at the top of the file to include EnrichedSearchResult:
```python
from src.models.noc import (
    SearchResult, EnrichedSearchResult, NOCHierarchy, BROAD_CATEGORIES,
    ReferenceAttributes, CareerMobilityPath, Interest, JobRequirements
)
```

2. Add new method after parse_search_results (around line 77):

```python
def parse_search_results_enhanced(self, html: str) -> List[EnrichedSearchResult]:
    """Parse search results HTML into EnrichedSearchResult models.

    Extracts available card data from OaSIS search results HTML:
    - NOC code and title from link
    - Lead statement (fa-book icon cell)
    - TEER description (fa-bookmark icon cell)
    - Broad category (fa-truck/fa-pen-alt icon cell)
    - Matching criteria (fa-search icon cell)
    - Minor group (derived from NOC code)

    Note: example_titles, mobility_progression, source_table, publication_date,
    and skills/abilities/knowledge require profile fetch and are left as None.

    Args:
        html: Raw HTML from OASIS search page

    Returns:
        List of EnrichedSearchResult models with available card data
    """
    soup = BeautifulSoup(html, 'lxml')
    results = []

    # OaSIS uses table rows with class 'cardsTr' for each result
    # Each row contains: hidden cols, profile link, BOC, TEER, lead statement, matching
    rows = soup.select('tr.cardsTr, tr.eqht-trgt')

    for row in rows:
        # Skip header rows
        if row.find('th'):
            continue

        # Extract NOC code and title from card header link
        link = row.select_one('.cardsheader a, td a[href*="OccProfile"], td a[href*="code="]')
        if not link:
            continue

        href = link.get('href', '')
        text = link.get_text(strip=True)

        # Extract NOC code from text or URL
        code_match = self.NOC_CODE_PATTERN.search(text) or self.NOC_CODE_PATTERN.search(href)
        if not code_match:
            continue

        noc_code = code_match.group(0)
        # Title is text after code (format: "72600.01 - Air pilots")
        title = text.replace(noc_code, '').strip(' -–')

        # Extract lead statement (cell with fa-book icon)
        lead_statement = None
        book_cell = row.select_one('td:has(.fa-book) .OaSISCardTDTextStyle, td:has(.fa-book) p, td:has(.fa-book) div')
        if book_cell:
            lead_statement = book_cell.get_text(strip=True)
        else:
            # Fallback: try finding cell with "Lead" in class or text pattern
            for td in row.select('td'):
                td_text = td.get_text(strip=True)
                # Lead statements typically describe what the occupation does
                if len(td_text) > 50 and not td_text.startswith('Matching'):
                    if td.select_one('.fa-book'):
                        lead_statement = td_text
                        break

        # Extract TEER description (cell with fa-bookmark icon)
        teer_description = None
        bookmark_cell = row.select_one('td:has(.fa-bookmark) .OaSISCardTDTextStyle, td:has(.fa-bookmark) span.noFontStyle')
        if bookmark_cell:
            teer_description = bookmark_cell.get_text(strip=True)

        # Extract broad category (cell with fa-truck, fa-pen-alt, fa-handshake icons)
        broad_category_name = None
        for icon_class in ['fa-truck', 'fa-pen-alt', 'fa-handshake', 'fa-laptop', 'fa-stethoscope']:
            boc_cell = row.select_one(f'td:has(.{icon_class}) .OaSISCardTDTextStyle')
            if boc_cell:
                broad_category_name = boc_cell.get_text(strip=True)
                break

        # Extract matching criteria (cell with fa-search icon)
        matching_criteria = None
        search_cell = row.select_one('td:has(.fa-search) .OaSISCardTDTextStyle, td.topBorder .OaSISCardTDTextStyle')
        if search_cell:
            # Get full text including child spans
            matching_text = search_cell.get_text(separator=' ', strip=True)
            # Clean up "Matching search criteria Label, Job titles" format
            matching_criteria = matching_text.replace('Matching search criteria', '').strip()

        # Derive minor group and broad category from NOC code
        base_code = noc_code.split('.')[0]
        broad_category = int(base_code[0]) if base_code else None
        minor_group = base_code[:3] if len(base_code) >= 3 else None

        results.append(EnrichedSearchResult(
            noc_code=noc_code,
            title=title,
            url=href,
            lead_statement=lead_statement,
            teer_description=teer_description,
            broad_category_name=broad_category_name,
            matching_criteria=matching_criteria,
            broad_category=broad_category,
            minor_group=minor_group,
            minor_group_name=None,  # Not available from search HTML
            # These require profile fetch - left as None
            example_titles=None,
            mobility_progression=None,
            source_table=None,
            publication_date=None,
            top_skills=None,
            top_abilities=None,
            top_knowledge=None
        ))

    return results
```
  </action>
  <verify>
Test with sample search to verify parsing:
```bash
python -c "
from src.services.scraper import scraper
from src.services.parser import parser

html = scraper.search('pilot')
results = parser.parse_search_results_enhanced(html)
print(f'Found {len(results)} results')
if results:
    r = results[0]
    print(f'First result: {r.noc_code} - {r.title}')
    print(f'Lead: {r.lead_statement[:100] if r.lead_statement else \"None\"}...')
    print(f'TEER: {r.teer_description[:50] if r.teer_description else \"None\"}...')
    print(f'Minor group: {r.minor_group}')
"
```
  </verify>
  <done>
parse_search_results_enhanced method extracts card data from OaSIS HTML. Lead statement, TEER, broad category, matching criteria populated from HTML. Minor group derived from NOC code.
  </done>
</task>

<task type="auto">
  <name>Task 3: Update API and response model to use EnrichedSearchResult</name>
  <files>src/routes/api.py, src/models/responses.py</files>
  <action>
1. Update src/models/responses.py to use EnrichedSearchResult:

Find the SearchResponse class and update the results field type. First add import:
```python
from src.models.noc import SourceMetadata, EnrichedSearchResult
```

Then update the class:
```python
class SearchResponse(BaseModel):
    """Response for /api/search endpoint."""
    query: str
    results: List[EnrichedSearchResult]  # Changed from SearchResult
    count: int
    metadata: SourceMetadata

    model_config = ConfigDict(from_attributes=True)
```

2. Update src/routes/api.py to use enhanced parser:

In the search() function (around line 50-52), change:
```python
html = scraper.search(query, search_type=search_type)
results = parser.parse_search_results(html)
```

To:
```python
html = scraper.search(query, search_type=search_type)
results = parser.parse_search_results_enhanced(html)
```

No other changes needed - the SearchResponse model will serialize EnrichedSearchResult correctly.
  </action>
  <verify>
Test full API flow:
```bash
curl -s "http://localhost:5000/api/search?q=pilot" | python -c "
import sys, json
data = json.load(sys.stdin)
r = data['results'][0] if data['results'] else {}
print('Count:', data['count'])
print('First result noc_code:', r.get('noc_code'))
print('lead_statement present:', 'lead_statement' in r)
print('minor_group:', r.get('minor_group'))
"
```

Verify response includes enriched fields (lead_statement, teer_description, minor_group, etc.)
  </verify>
  <done>
API returns EnrichedSearchResult with all available card data. Frontend can now render cards without additional API calls.
  </done>
</task>

</tasks>

<verification>
After all tasks complete:

1. **Model verification:**
   ```bash
   python -c "from src.models.noc import EnrichedSearchResult; print('Model OK')"
   ```

2. **Parser verification:**
   ```bash
   python -c "
   from src.services.scraper import scraper
   from src.services.parser import parser
   html = scraper.search('software')
   results = parser.parse_search_results_enhanced(html)
   assert len(results) > 0, 'No results parsed'
   r = results[0]
   assert r.noc_code, 'Missing noc_code'
   assert r.minor_group, 'Missing minor_group'
   print(f'Parsed {len(results)} enriched results')
   print(f'Sample: {r.noc_code} - {r.title}')
   print(f'Has lead_statement: {r.lead_statement is not None}')
   "
   ```

3. **API verification:**
   ```bash
   curl -s "http://localhost:5000/api/search?q=pilot" | python -c "
   import sys, json
   data = json.load(sys.stdin)
   assert data['count'] > 0, 'No results'
   r = data['results'][0]
   assert 'lead_statement' in r, 'Missing lead_statement field'
   assert 'minor_group' in r, 'Missing minor_group field'
   print('API returns enriched results: OK')
   "
   ```

4. **Backward compatibility:**
   - Existing frontend should still work (displays title and noc_code)
   - Additional fields are optional and won't break rendering
</verification>

<success_criteria>
- [ ] EnrichedSearchResult model created with all card/filter/grid fields
- [ ] parse_search_results_enhanced method extracts available data from OaSIS HTML
- [ ] Lead statement extracted from fa-book cells
- [ ] TEER description extracted from fa-bookmark cells
- [ ] Broad category name extracted from BOC icon cells
- [ ] Matching criteria extracted from fa-search cells
- [ ] Minor group derived from NOC code (first 3 digits)
- [ ] API /search returns EnrichedSearchResult via SearchResponse
- [ ] Existing frontend continues to work (backward compatible)
- [ ] Profile-dependent fields (skills, abilities, knowledge, mobility) documented as None
</success_criteria>

<output>
After completion, create `.planning/phases/08-B-results-cards-grid/08-B-01-SUMMARY.md`
</output>
