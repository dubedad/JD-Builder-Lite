---
phase: 08-C-profile-page-tabs
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - src/services/llm_service.py
  - src/routes/api.py
  - src/config.py
autonomous: true

must_haves:
  truths:
    - "LLM can select an appropriate icon class from a predefined list based on occupation description"
    - "LLM can generate a 3-4 sentence occupation description from title and main duties"
    - "Invalid icon responses fallback to default icon"
    - "API endpoints return icon class and description text"
  artifacts:
    - path: "src/services/llm_service.py"
      provides: "select_occupation_icon() and generate_occupation_description() functions"
      contains: "ICON_OPTIONS"
    - path: "src/routes/api.py"
      provides: "POST /api/occupation-icon and POST /api/occupation-description endpoints"
      exports: ["occupation_icon", "occupation_description"]
  key_links:
    - from: "src/routes/api.py"
      to: "src/services/llm_service.py"
      via: "function imports"
      pattern: "from src.services.llm_service import.*select_occupation_icon"
---

<objective>
Add LLM-powered icon selection and occupation description generation endpoints to support the profile header redesign.

Purpose: Enable the profile page to display a contextually appropriate icon and a synthesized occupation description, both driven by LLM based on NOC data.

Output: Two new API endpoints (`/api/occupation-icon`, `/api/occupation-description`) backed by LLM service functions with proper fallback handling.
</objective>

<execution_context>
@C:\Users\Administrator\.claude/get-shit-done/workflows/execute-plan.md
@C:\Users\Administrator\.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/08-C-profile-page-tabs/08-C-RESEARCH.md
@src/services/llm_service.py
@src/routes/api.py
@src/config.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Add icon selection and description generation to LLM service</name>
  <files>src/services/llm_service.py, src/config.py</files>
  <action>
    Add two new functions to llm_service.py:

    1. **ICON_OPTIONS constant** - Dictionary mapping semantic categories to Font Awesome icon classes:
       ```python
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
           "trades": "fa-tools",
           "agriculture": "fa-tractor",
           "manufacturing": "fa-industry",
           "default": "fa-briefcase"
       }
       ```

    2. **select_occupation_icon(occupation_title: str, lead_statement: str) -> str**
       - System prompt: "You are an icon selection expert. Select ONE icon class from the list that best represents this occupation. Return ONLY the icon class name."
       - User prompt: Include occupation title and lead statement
       - List all available icon classes in prompt
       - Temperature: 0 (deterministic)
       - Max tokens: 30
       - Validate response is in ICON_OPTIONS.values()
       - Fallback to "fa-briefcase" if invalid

    3. **generate_occupation_description(occupation_title: str, lead_statement: str, main_duties: list[str]) -> str**
       - System prompt: "You are an expert HR consultant. Generate a concise 3-4 sentence paragraph (~100 words) describing what workers in this occupation do. Write in third person present tense. Synthesize the information - do not copy verbatim."
       - User prompt: Include title, lead statement, and first 5 main duties
       - Temperature: 0.3 (slight creativity)
       - Max tokens: 200
       - Return the generated text stripped of whitespace

    Both functions should use the existing OpenAI client and catch exceptions gracefully.
  </action>
  <verify>
    Run Python REPL to test:
    ```python
    from src.services.llm_service import select_occupation_icon, generate_occupation_description, ICON_OPTIONS

    # Test icon selection
    icon = select_occupation_icon("Data scientists", "Data scientists use advanced analytics...")
    print(f"Icon: {icon}")
    assert icon in ICON_OPTIONS.values()

    # Test description generation
    desc = generate_occupation_description("Data scientists", "...", ["analyze data", "build models"])
    print(f"Description: {desc}")
    assert len(desc) > 50
    ```
  </verify>
  <done>
    Both LLM functions exist, return valid outputs, and handle errors gracefully with fallbacks.
  </done>
</task>

<task type="auto">
  <name>Task 2: Add API endpoints for icon and description</name>
  <files>src/routes/api.py</files>
  <action>
    Add two new POST endpoints to api.py:

    1. **POST /api/occupation-icon**
       - Import `select_occupation_icon` from llm_service
       - Expects JSON body: `{"occupation_title": str, "lead_statement": str}`
       - Validates both fields are non-empty strings
       - Calls `select_occupation_icon()`
       - Returns: `{"icon_class": "fa-atom"}` or error response
       - Handle exceptions, return 500 on failure

    2. **POST /api/occupation-description**
       - Import `generate_occupation_description` from llm_service
       - Expects JSON body: `{"occupation_title": str, "lead_statement": str, "main_duties": list[str]}`
       - Validates fields (main_duties can be empty list)
       - Calls `generate_occupation_description()`
       - Returns: `{"description": "...text..."}` or error response
       - Handle exceptions, return 500 on failure

    Update the import at top of file to include both new functions.
  </action>
  <verify>
    Test endpoints with curl:
    ```bash
    # Test icon endpoint
    curl -X POST http://localhost:5000/api/occupation-icon \
      -H "Content-Type: application/json" \
      -d '{"occupation_title": "Data scientists", "lead_statement": "Data scientists use advanced analytics technologies..."}'

    # Should return: {"icon_class": "fa-atom"} or similar

    # Test description endpoint
    curl -X POST http://localhost:5000/api/occupation-description \
      -H "Content-Type: application/json" \
      -d '{"occupation_title": "Data scientists", "lead_statement": "Data scientists use...", "main_duties": ["analyze data", "build models"]}'

    # Should return: {"description": "...paragraph..."}
    ```
  </verify>
  <done>
    Both endpoints return valid JSON responses, handle validation errors with 400, and handle LLM errors with 500.
  </done>
</task>

</tasks>

<verification>
1. Flask app starts without import errors: `python -c "from src.app import app; print('OK')"`
2. Icon selection works and validates against allowed list
3. Description generation returns coherent paragraph
4. Both endpoints accessible via POST with JSON body
5. Error handling returns appropriate status codes
</verification>

<success_criteria>
- [ ] ICON_OPTIONS constant defined with 16 icon mappings
- [ ] select_occupation_icon() returns valid Font Awesome class
- [ ] generate_occupation_description() returns 3-4 sentence paragraph
- [ ] Invalid icon responses fallback to "fa-briefcase"
- [ ] POST /api/occupation-icon endpoint works
- [ ] POST /api/occupation-description endpoint works
- [ ] Error responses use proper HTTP status codes
</success_criteria>

<output>
After completion, create `.planning/phases/08-C-profile-page-tabs/08-C-01-SUMMARY.md`
</output>
