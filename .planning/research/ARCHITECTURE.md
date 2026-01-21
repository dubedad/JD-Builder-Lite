# Architecture Patterns

**Domain:** Web scraping app with data transformation and LLM integration
**Project:** JD Builder Lite
**Researched:** 2026-01-21
**Confidence:** HIGH (standard patterns, well-documented)

## Recommended Architecture

```
+------------------+         +------------------+         +------------------+
|                  |  HTTP   |                  |  HTTP   |                  |
|  Browser         |-------->|  Node.js/Express |-------->|  OASIS Site      |
|  (Vanilla JS)    |<--------|  Backend Server  |<--------|  (noc.esdc.gc.ca)|
|                  |         |                  |         |                  |
+------------------+         +--------+---------+         +------------------+
                                      |
                                      | HTTPS
                                      v
                             +------------------+
                             |                  |
                             |  OpenAI API      |
                             |                  |
                             +------------------+
```

This is a **3-tier architecture** with the backend acting as a proxy/orchestration layer:

1. **Frontend (Browser)**: Vanilla HTML/CSS/JS - handles UI, user input, display
2. **Backend (Node.js)**: Express server - proxies OASIS requests, calls OpenAI, serves static files
3. **External Services**: OASIS (scrape target), OpenAI (LLM API)

### Why This Pattern

**CORS bypass is mandatory.** Browsers block cross-origin requests to OASIS. The backend proxy pattern is the standard solution - the browser talks to your backend, your backend talks to OASIS. This is not a workaround; it's the correct architectural approach.

**API key protection.** OpenAI API keys cannot be exposed in frontend code. The backend holds the key and proxies LLM requests.

**Data transformation hub.** The backend is the natural place to parse HTML, extract structured data, and prepare it for the frontend or LLM.

## Component Boundaries

| Component | Responsibility | Communicates With | Technology |
|-----------|---------------|-------------------|------------|
| **Frontend UI** | User interaction, display, form handling | Backend API only | HTML, CSS, Vanilla JS |
| **Static Server** | Serve HTML/CSS/JS files | Browser | Express.static |
| **Scrape Proxy** | Fetch OASIS pages, bypass CORS | OASIS site | node-fetch or axios |
| **HTML Parser** | Extract NOC data from HTML | Internal | cheerio |
| **Data Mapper** | Transform NOC data to JD elements | Internal | Pure JS |
| **LLM Proxy** | Call OpenAI API securely | OpenAI API | openai SDK |
| **PDF Generator** | Create downloadable PDF | Internal | Browser print or jsPDF |

### Boundary Rules

1. **Frontend never calls external services directly** - all external requests go through backend
2. **Backend is stateless** - no database, no sessions, each request is independent
3. **Parsing logic lives in backend** - HTML parsing is server-side, frontend receives clean JSON
4. **LLM prompts are backend-controlled** - frontend sends user selections, backend constructs prompts

## Data Flow

### Complete Request Flow

```
User Action                Frontend                     Backend                      External
-----------                --------                     -------                      --------

1. Search for job title
   [Type "Analyst"]  --->  fetch('/api/search?q=...')
                                                   ---> GET OASIS search page
                                                   <--- HTML response
                                                        Parse HTML, extract results
                           <--- JSON: [{title, url}]
   [Show results list]

2. Select a profile
   [Click profile]   --->  fetch('/api/profile?url=...')
                                                   ---> GET OASIS profile page
                                                        (multiple tabs)
                                                   <--- HTML responses
                                                        Parse all tabs
                                                        Extract NOC attributes
                                                        Map to JD elements
                           <--- JSON: {
                                  keyActivities: [...],
                                  skills: [...],
                                  effort: [...],
                                  ...
                                }
   [Display selection UI]

3. Generate overview
   [Click generate]  --->  POST /api/generate
                           body: {selections: {...}}
                                                   ---> POST OpenAI API
                                                        (constructed prompt)
                                                   <--- Generated text
                           <--- JSON: {overview: "..."}
   [Display overview]

4. Export PDF
   [Click export]    --->  (handled in browser)
                           window.print() or jsPDF
```

### Data Transformation Pipeline

```
OASIS HTML (raw)
      |
      v
+---------------------+
| Backend: Scraper    | <-- Fetches multiple tab pages
+---------------------+
      |
      v
OASIS HTML (multiple pages)
      |
      v
+---------------------+
| Backend: Parser     | <-- cheerio extracts tables, lists, text
+---------------------+
      |
      v
Raw NOC Data (structured but unmapped)
{
  mainDuties: [...],
  workActivities: [...],
  skills: [...],
  abilities: [...],
  knowledge: [...],
  workContext: [...],
  ...
}
      |
      v
+---------------------+
| Backend: Mapper     | <-- Applies NOC -> JD element mapping from PROJECT.md
+---------------------+
      |
      v
JD-Ready Data (frontend-friendly)
{
  keyActivities: [...],    // from mainDuties + workActivities
  skills: [...],           // from skills + abilities + knowledge
  effort: [...],           // from workContext filtered
  responsibility: [...],   // from workContext filtered
  workingConditions: [...],// from workContext
  annex: {...}             // other attributes
}
      |
      v
+---------------------+
| Frontend: Selector  | <-- User picks items under each header
+---------------------+
      |
      v
User Selections
{
  keyActivities: [selected items],
  skills: [selected items],
  ...
}
      |
      v
+---------------------+
| Backend: LLM Proxy  | <-- Constructs prompt from selections
+---------------------+
      |
      v
OpenAI API
      |
      v
Generated Overview
      |
      v
+---------------------+
| Frontend: Assembler | <-- Combines selections + overview + metadata
+---------------------+
      |
      v
Final Job Description (with compliance metadata)
      |
      v
+---------------------+
| Frontend/Browser:   | <-- Print dialog or jsPDF
| PDF Export          |
+---------------------+
```

## File Structure

Recommended project structure for this architecture:

```
jd-builder-lite/
|
+-- server.js              # Express entry point
+-- package.json           # Dependencies
|
+-- public/                # Static files served to browser
|   +-- index.html         # Main (only) HTML page
|   +-- css/
|   |   +-- styles.css     # All styles
|   +-- js/
|       +-- app.js         # Main application logic
|       +-- api.js         # Fetch calls to backend
|       +-- ui.js          # DOM manipulation
|       +-- pdf.js         # PDF generation
|
+-- src/                   # Backend modules
|   +-- scraper.js         # OASIS fetching
|   +-- parser.js          # HTML parsing with cheerio
|   +-- mapper.js          # NOC -> JD element mapping
|   +-- llm.js             # OpenAI API calls
|   +-- routes.js          # Express route definitions
|
+-- .env                   # OPENAI_API_KEY (gitignored)
+-- .gitignore
```

### Why This Structure

- **public/**: Everything the browser needs, served statically
- **src/**: Backend logic, never exposed to browser
- **Single HTML page**: No routing needed, single-page app flow
- **Separated JS files**: Maintainable but no build step required

## Patterns to Follow

### Pattern 1: Backend-for-Frontend (BFF) Proxy

**What:** Backend shapes data specifically for this frontend's needs.
**When:** Frontend needs curated data, not raw API/scrape responses.
**Why:** Reduces frontend complexity, keeps parsing/mapping logic server-side.

```javascript
// Backend: routes.js
app.get('/api/profile', async (req, res) => {
  const { url } = req.query;

  // Fetch raw HTML
  const html = await scraper.fetchProfile(url);

  // Parse to structured data
  const nocData = parser.extractNocData(html);

  // Map to JD elements (shaped for this frontend)
  const jdData = mapper.toJdElements(nocData);

  // Return clean, ready-to-use JSON
  res.json(jdData);
});
```

### Pattern 2: Clean HTML Before LLM

**What:** Strip HTML to essential text before sending to LLM.
**When:** Using scraped content as LLM input.
**Why:** Reduces tokens, improves LLM comprehension, lowers cost.

```javascript
// Backend: llm.js
function buildPrompt(selections) {
  // selections is already clean text, not HTML
  const context = Object.entries(selections)
    .map(([category, items]) => `${category}:\n${items.join('\n')}`)
    .join('\n\n');

  return `Generate a professional job overview based on:\n${context}`;
}
```

### Pattern 3: Stateless Request Handling

**What:** Each request is independent, no server-side session.
**When:** Demo apps, single-user scenarios.
**Why:** Simplicity - no session management, no state bugs.

```javascript
// Each request carries all needed context
// No: req.session.selections
// Yes: req.body.selections (sent each time)

app.post('/api/generate', async (req, res) => {
  const { selections } = req.body;  // Client sends selections each time
  const overview = await llm.generateOverview(selections);
  res.json({ overview });
});
```

### Pattern 4: Browser-Native PDF

**What:** Use window.print() with print-specific CSS.
**When:** Simple PDF needs, demo quality acceptable.
**Why:** Zero dependencies, works everywhere, good enough for demo.

```javascript
// Frontend: pdf.js
function exportPdf() {
  window.print();  // Browser handles PDF generation
}
```

```css
/* styles.css */
@media print {
  .no-print { display: none; }
  .print-only { display: block; }
  body { font-size: 12pt; }
}
```

## Anti-Patterns to Avoid

### Anti-Pattern 1: Frontend Direct to External APIs

**What:** Calling OASIS or OpenAI directly from browser JavaScript.
**Why bad:** CORS blocks OASIS calls. OpenAI key exposed in browser.
**Instead:** Always proxy through backend.

### Anti-Pattern 2: Parsing HTML in Frontend

**What:** Sending raw HTML to frontend, parsing with DOMParser.
**Why bad:** Large payloads, duplicated parsing logic, harder to maintain.
**Instead:** Parse on backend, send clean JSON.

### Anti-Pattern 3: Storing State in Backend

**What:** Keeping user selections in server memory between requests.
**Why bad:** Complexity for no benefit in single-user demo.
**Instead:** Frontend holds all state, sends to backend as needed.

### Anti-Pattern 4: Build Step for Frontend

**What:** Using webpack/Vite/etc. for vanilla JS demo.
**Why bad:** Unnecessary complexity for simple app.
**Instead:** Plain JS files, script tags in HTML. Works in browser directly.

### Anti-Pattern 5: Over-Engineering the Proxy

**What:** Building a general-purpose CORS proxy for any URL.
**Why bad:** Security risk, not needed for specific use case.
**Instead:** Purpose-built routes for OASIS search and profile only.

## Suggested Build Order

Build order follows data flow dependencies and testability:

### Phase 1: Backend Foundation (Build First)

**Components:** Express server, static file serving, basic route structure

**Why first:**
- Frontend can't function without backend endpoints
- Can test with curl/Postman before frontend exists
- Establishes project structure

**Deliverable:** Server that serves static files and has placeholder routes returning mock JSON.

### Phase 2: Scraping Pipeline (Build Second)

**Components:** OASIS fetcher, HTML parser, data mapper

**Why second:**
- Core functionality - everything depends on getting NOC data
- Can test independently with hardcoded URLs
- Most likely to have issues (external site structure)

**Deliverable:** Endpoint that returns parsed, mapped JD data for a profile URL.

### Phase 3: Frontend UI (Build Third)

**Components:** HTML structure, CSS styling, JS for search/selection

**Why third:**
- Now has real data to display (from Phase 2)
- Can iterate on UI with working data
- User can see actual NOC content

**Deliverable:** Working search, profile display, and selection interface.

### Phase 4: LLM Integration (Build Fourth)

**Components:** OpenAI proxy, prompt construction, overview generation

**Why fourth:**
- Needs selections from UI (Phase 3)
- Most expensive to test (API calls)
- Can use mock data while developing prompt

**Deliverable:** Generate button produces real LLM overview.

### Phase 5: PDF Export and Polish (Build Last)

**Components:** Print CSS, final assembly, compliance metadata

**Why last:**
- Needs complete flow working (all previous phases)
- Finishing touches, not core functionality
- Easy to iterate on styling

**Deliverable:** Complete demo with PDF export.

### Dependency Graph

```
Phase 1: Backend Foundation
    |
    v
Phase 2: Scraping Pipeline
    |
    v
Phase 3: Frontend UI
    |
    v
Phase 4: LLM Integration
    |
    v
Phase 5: PDF Export & Polish
```

Each phase builds on the previous. Phase 2 requires Phase 1's routes. Phase 3 requires Phase 2's data. Phase 4 requires Phase 3's selections. Phase 5 requires everything.

## Scalability Considerations

| Concern | At 1 user (Demo) | At 100 users | At 10K users |
|---------|------------------|--------------|--------------|
| OASIS load | Negligible | Rate limit risk | Need caching layer |
| OpenAI cost | Minimal | Moderate | Need usage limits |
| Server resources | Single process fine | Still fine | Need horizontal scaling |
| State management | In-browser only | Still fine | Consider session store |

**For this demo:** All concerns are "demo" level. No scaling needed.

## Technology Recommendations

Based on this architecture:

| Component | Recommended | Why |
|-----------|-------------|-----|
| Web server | Express.js | Standard, simple, well-documented |
| HTTP client | node-fetch or axios | Either works, axios slightly nicer |
| HTML parser | cheerio | jQuery-like API, fast, well-maintained |
| OpenAI client | openai (official SDK) | Best maintained, handles auth |
| PDF | window.print() | Zero deps, good enough for demo |
| Frontend | Vanilla JS | No build step, explicit requirement |

## Sources

Architecture patterns and CORS proxy approaches:
- [WebScraping.AI - CORS and API-based scraping](https://webscraping.ai/faq/apis/what-is-cors-and-how-does-it-affect-api-based-web-scraping)
- [Bump.sh - Open-source CORS proxy solution](https://bump.sh/blog/releasing-cors-proxy-opensource/)
- [SerpAPI - Building reverse proxy for frontend](https://serpapi.com/blog/adding-a-node-js-backend-to-handle-api-interactions-for-a-frontend-application/)
- [HeyNode - Express API proxy server](https://heynode.com/tutorial/use-express-create-api-proxy-server-nodejs/)
- [http-proxy-middleware on GitHub](https://github.com/chimurai/http-proxy-middleware)

HTML parsing and LLM integration:
- [DZone - Enhancing web scraping with LLMs](https://dzone.com/articles/enhancing-web-scraping-with-large-language-models)
- [LLM Scraper on GitHub](https://github.com/mishushakov/llm-scraper)
- [GroupBWT - Web scraping infrastructure](https://groupbwt.com/blog/infrastructure-of-web-scraping/)

Vanilla JS frontend patterns:
- [The New Stack - Developers returning to Vanilla JavaScript](https://thenewstack.io/why-developers-are-ditching-frameworks-for-vanilla-javascript/)
- [Frontend integration with APIs guide](https://kapucuonur.medium.com/integrating-frontend-and-backend-with-apis-a-comprehensive-guide-9d296eef2e33)
