# Phase 3: LLM Integration - Research

**Researched:** 2026-01-21
**Domain:** OpenAI API integration with Flask, streaming responses, prompt engineering
**Confidence:** HIGH

## Summary

This phase integrates OpenAI's GPT-4o model to generate job description overviews based on manager selections. The standard approach uses the official OpenAI Python library with Server-Sent Events (SSE) for streaming responses to the frontend, Flask generators for SSE implementation, and structured prompt engineering for consistent output quality.

The locked decisions (GPT-4o, streaming display, full provenance tracking) align well with current best practices. GPT-4o is OpenAI's latest flagship model with excellent text generation capabilities, streaming provides immediate user feedback, and the OpenAI Python SDK makes both trivially simple to implement.

Key implementation considerations: Flask's built-in development server cannot handle SSE (requires Gunicorn with async workers for production), error handling must cover both pre-stream and mid-stream failures, and provenance tracking should capture model name, timestamp, input statement IDs, and prompt template version.

**Primary recommendation:** Use the official OpenAI Python SDK with native streaming support, implement SSE via Flask Response generators (no Redis dependency needed for single-user sessions), structure prompts with system instructions and formatted user context, and implement exponential backoff retry logic for rate limit handling.

## Standard Stack

The established libraries/tools for OpenAI integration with Flask:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| openai | 1.x+ | Official OpenAI Python SDK | Official library with native streaming, type hints, async support |
| flask | 3.1.2 | Web framework | Already in project, native generator support for SSE |
| gunicorn | 22.0+ | WSGI server | Required for SSE in production (Flask dev server doesn't support concurrent connections) |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| gevent | 24.0+ | Async worker class | Use with Gunicorn for async SSE handling (`--worker-class gevent`) |
| python-dotenv | 1.2.1 | API key management | Already in project, use for OPENAI_API_KEY |
| tenacity | 9.0+ | Retry logic | Optional but recommended for robust error handling with exponential backoff |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| OpenAI SDK | Direct HTTP requests | SDK handles streaming, retries, types automatically - no reason to roll your own |
| Flask generators | Flask-SSE (Redis) | Flask-SSE requires Redis pub/sub infrastructure; overkill for single-user session state |
| Gunicorn+gevent | eventlet workers | gevent is more commonly used, better maintained, simpler to configure |

**Installation:**
```bash
pip install openai==1.59.0
pip install gunicorn==23.0.0
pip install gevent==24.11.1
pip install tenacity==9.0.0  # Optional but recommended
```

## Architecture Patterns

### Recommended Project Structure
```
src/
├── services/
│   ├── llm_service.py      # OpenAI API integration, prompt templates
│   └── session_store.py    # In-memory session state for provenance
├── routes/
│   └── api.py              # SSE endpoint for streaming generation
├── models/
│   └── ai.py               # Pydantic models for AI metadata, generation requests
└── config.py               # OpenAI API key, model configuration
```

### Pattern 1: OpenAI Streaming with Flask SSE

**What:** Stream GPT-4o responses token-by-token using Flask Response generators
**When to use:** Any time you want real-time feedback during LLM generation (which you do)

**Example:**
```python
# Source: OpenAI Python SDK + Flask SSE patterns
from openai import OpenAI
from flask import Response, stream_with_context

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route('/api/generate', methods=['POST'])
def generate_overview():
    data = request.json
    statements = data.get('statements', [])
    job_context = data.get('context', {})

    def generate():
        try:
            stream = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": build_system_prompt()},
                    {"role": "user", "content": build_user_prompt(statements, job_context)}
                ],
                temperature=0.7,  # Some creativity, not too much
                max_tokens=300,   # ~4-6 sentences
                stream=True
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    text = chunk.choices[0].delta.content
                    # SSE format: "data: <content>\n\n"
                    yield f"data: {text}\n\n"

            # Signal completion
            yield "data: [DONE]\n\n"

        except Exception as e:
            yield f"data: [ERROR] {str(e)}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'  # Disable nginx buffering
        }
    )
```

### Pattern 2: Structured Prompt Engineering

**What:** Organize prompts with system instructions, formatted context, and clear output constraints
**When to use:** Always - GPT-4o responds best to well-structured, explicit instructions

**Example:**
```python
# Source: OpenAI prompt engineering best practices
def build_system_prompt():
    return """You are an expert HR consultant specializing in Canadian job descriptions.
You create concise, professional General Overview sections that accurately reflect the role based on NOC (National Occupational Classification) data.

Guidelines:
- Write 4-6 sentences (approximately 150-200 words)
- Focus on the role's purpose and key responsibilities
- Use professional, clear language
- Synthesize information from all provided NOC elements
- Do NOT copy NOC statements verbatim - synthesize and contextualize"""

def build_user_prompt(statements, job_context):
    # Group statements by JD Element
    grouped = group_statements_by_element(statements)

    prompt_parts = [
        f"Job Title: {job_context['job_title']}",
        f"NOC Code: {job_context['noc_code']} - {job_context['noc_title']}",
        f"Occupation Code: {job_context['occupation_code']}",
        "",
        "Selected NOC Statements:",
        ""
    ]

    for element_name, element_statements in grouped.items():
        prompt_parts.append(f"{element_name}:")
        for stmt in element_statements:
            prompt_parts.append(f"  - {stmt['text']}")
        prompt_parts.append("")

    prompt_parts.append("Generate a professional General Overview section (4-6 sentences) for this job description:")

    return "\n".join(prompt_parts)
```

### Pattern 3: Provenance Tracking with Session State

**What:** Store AI generation metadata in Flask session for later PDF export
**When to use:** When you need to track what the AI did without persisting to database

**Example:**
```python
# Source: Flask session management best practices
from flask import session
from datetime import datetime
import json

def record_generation_metadata(statements, model_name, prompt_version):
    """Store provenance data in session until PDF export"""
    session['ai_generation'] = {
        'model': model_name,
        'timestamp': datetime.utcnow().isoformat(),
        'input_statement_ids': [s['id'] for s in statements],
        'prompt_version': prompt_version,
        'modified': False  # Track if manager edited the output
    }
    session.modified = True  # Ensure Flask saves the session

def mark_as_modified():
    """Call when manager edits the generated text"""
    if 'ai_generation' in session:
        session['ai_generation']['modified'] = True
        session.modified = True
```

### Pattern 4: Error Handling with Retry Logic

**What:** Implement exponential backoff for transient API failures
**When to use:** Always - OpenAI API has rate limits and occasional timeouts

**Example:**
```python
# Source: OpenAI error handling cookbook
from openai import OpenAI, RateLimitError, APIConnectionError, APITimeoutError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

client = OpenAI()

@retry(
    retry=retry_if_exception_type((RateLimitError, APIConnectionError, APITimeoutError)),
    wait=wait_exponential(multiplier=1, min=1, max=60),
    stop=stop_after_attempt(3)
)
def generate_with_retry(messages, **kwargs):
    """Generate with automatic retry on transient errors"""
    return client.chat.completions.create(
        messages=messages,
        **kwargs
    )
```

### Anti-Patterns to Avoid

- **Building prompt templates in frontend JavaScript:** Prompt logic should live server-side where you can version it and track what was used
- **Using Flask dev server for SSE in testing:** It will appear to work but hang on concurrent requests - use Gunicorn even in dev
- **Ignoring mid-stream errors:** Errors can occur after streaming starts; frontend must handle `[ERROR]` messages
- **Storing full generated text in session:** Only store metadata and final accepted version; let frontend manage the textarea state
- **Hardcoding the model name in code:** Use config so you can easily test with different models or fallback to gpt-4o-mini

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| OpenAI API client | Custom requests + JSON parsing | OpenAI Python SDK | Handles streaming chunks, authentication, retries, type hints automatically |
| Retry logic for rate limits | Custom sleep/loop | tenacity library | Proper exponential backoff, jitter, exception filtering built-in |
| SSE message formatting | Manual string building | Flask Response generators | Flask natively supports generators for streaming; just yield strings |
| API key security | Inline strings | python-dotenv + environment variables | Already in project; never commit API keys to git |
| Token counting | Character-based estimation | tiktoken library | OpenAI's official tokenizer for accurate prompt/response counting (optional but useful) |

**Key insight:** OpenAI integration is mature enough that the official SDK handles 90% of complexity. The hard parts are prompt engineering (which requires domain knowledge) and error handling (which requires understanding failure modes). Don't reinvent HTTP clients or streaming parsers.

## Common Pitfalls

### Pitfall 1: Using Flask Dev Server for SSE
**What goes wrong:** Flask's built-in development server (`flask run`) handles requests synchronously, one at a time. When a client connects to an SSE endpoint, the connection stays open, blocking all other requests.
**Why it happens:** Flask dev server is designed for simple request/response, not long-lived connections.
**How to avoid:** Use Gunicorn with gevent workers even during development: `gunicorn --worker-class gevent --bind 127.0.0.1:5000 src.app:app`
**Warning signs:** Frontend hangs waiting for SSE connection; other API endpoints become unresponsive

### Pitfall 2: Mid-Stream Error Handling
**What goes wrong:** Errors that occur after streaming starts cannot change the HTTP status code (it's already 200). Frontend assumes success but receives incomplete output.
**Why it happens:** SSE streams commit the response headers immediately, before you know if the full generation will succeed.
**How to avoid:** Send error messages as SSE data events (e.g., `data: [ERROR] <message>\n\n`) and teach frontend to watch for these. Include a `[DONE]` message on success so frontend knows the stream completed normally.
**Warning signs:** Frontend shows partial text with no indication of failure; user thinks generation is complete when it isn't

### Pitfall 3: Content Moderation on Streamed Output
**What goes wrong:** You can't moderate content before sending it to users when streaming. By the time you detect a policy violation, the user has already seen it.
**Why it happens:** Streaming sends tokens as soon as they're generated; no chance to review full output first.
**How to avoid:** For job descriptions, this is low-risk (unlikely to generate harmful content from NOC statements). If moderation becomes necessary, switch to non-streaming generation, moderate the full response, then return it. For your use case, streaming is fine.
**Warning signs:** Compliance concerns about AI output reaching users without review

### Pitfall 4: Prompt Version Tracking
**What goes wrong:** You improve the prompt over time, but can't tell which version generated a specific output. User reports an issue and you can't reproduce it because the prompt has changed.
**Why it happens:** Prompt templates evolve iteratively; without explicit versioning, you lose track.
**How to avoid:** Include a `PROMPT_VERSION` constant in your prompt building code and store it in provenance metadata. When debugging, you can reconstruct the exact prompt that was used.
**Warning signs:** "It worked yesterday but now the output is different" bug reports you can't reproduce

### Pitfall 5: Session Secret Key in Development
**What goes wrong:** Flask sessions require `app.secret_key` to be set. If missing, Flask will crash with cryptic errors when you try to use `session`.
**Why it happens:** Flask encrypts session cookies and needs a secret key to do so.
**How to avoid:** Set `app.secret_key` from environment variable in `config.py`: `SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-change-in-production')`
**Warning signs:** `RuntimeError: The session is unavailable because no secret key was set`

### Pitfall 6: Temperature and Determinism
**What goes wrong:** User regenerates and gets wildly different output each time, or output is too repetitive and boring.
**Why it happens:** `temperature` parameter controls randomness (0.0 = deterministic, 2.0 = very random). Wrong setting for use case.
**How to avoid:** For job descriptions, use `temperature=0.7` - enough creativity for natural language but consistent enough for professional output. For factual extraction, use 0.0. For creative writing, use 1.0+.
**Warning signs:** Users complain output is "robotic and repetitive" (too low) or "inconsistent and weird" (too high)

## Code Examples

Verified patterns from official sources and best practices:

### Complete Generation Endpoint
```python
# Source: OpenAI SDK docs + Flask SSE patterns
from flask import Flask, request, Response, session, stream_with_context
from openai import OpenAI
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-change-in-production')

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

PROMPT_VERSION = "v1.0"
MODEL_NAME = "gpt-4o"

@app.route('/api/generate', methods=['POST'])
def generate_overview():
    data = request.json
    statements = data['statements']  # List of selected statement objects
    job_context = data['context']    # Job title, NOC code, etc.

    def generate():
        try:
            # Build prompt
            system_msg = build_system_prompt()
            user_msg = build_user_prompt(statements, job_context)

            # Store provenance before generation
            record_generation_metadata(
                statements=statements,
                model_name=MODEL_NAME,
                prompt_version=PROMPT_VERSION
            )

            # Stream from OpenAI
            stream = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg}
                ],
                temperature=0.7,
                max_tokens=300,
                stream=True
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    text = chunk.choices[0].delta.content
                    yield f"data: {text}\n\n"

            yield "data: [DONE]\n\n"

        except Exception as e:
            yield f"data: [ERROR] {str(e)}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        }
    )

def record_generation_metadata(statements, model_name, prompt_version):
    session['ai_generation'] = {
        'model': model_name,
        'timestamp': datetime.utcnow().isoformat(),
        'input_statement_ids': [s['id'] for s in statements],
        'prompt_version': prompt_version,
        'modified': False
    }
    session.modified = True
```

### Frontend EventSource Consumer
```javascript
// Source: MDN EventSource API + Flask SSE integration patterns
function generateOverview(statements, context) {
  const textarea = document.getElementById('overview-textarea');
  const badge = document.getElementById('ai-badge');
  let fullText = '';

  // Clear previous
  textarea.value = '';
  badge.textContent = 'AI Generated';

  // Send POST to trigger generation
  fetch('/api/generate', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({statements, context})
  }).then(response => {
    if (!response.ok) throw new Error('Generation failed');

    // Open SSE connection
    const eventSource = new EventSource('/api/generate');

    eventSource.onmessage = (event) => {
      if (event.data === '[DONE]') {
        eventSource.close();
        return;
      }

      if (event.data.startsWith('[ERROR]')) {
        eventSource.close();
        alert('Generation failed: ' + event.data.substring(8));
        return;
      }

      // Append token to textarea
      fullText += event.data;
      textarea.value = fullText;

      // Auto-scroll to bottom
      textarea.scrollTop = textarea.scrollHeight;
    };

    eventSource.onerror = (error) => {
      eventSource.close();
      alert('Connection error during generation');
    };
  });
}

// Track manual edits
document.getElementById('overview-textarea').addEventListener('input', () => {
  fetch('/api/mark-modified', {method: 'POST'});
  document.getElementById('ai-badge').textContent = 'AI-Generated (Modified)';
});
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Completions API | Chat Completions API | 2023 | Use `chat.completions.create()` not `completions.create()` |
| Manual SSE parsing | OpenAI SDK streaming | 2023+ | SDK handles chunk parsing, just iterate the stream |
| GPT-3.5-turbo | GPT-4o | May 2024 | Better at following instructions, multimodal, faster, same price tier for text |
| Flask-SocketIO for real-time | SSE with Flask generators | Current | SSE is simpler for one-way streaming; no WebSocket needed |
| Chat Completions API | Responses API | 2025/2026 | OpenAI now recommends Responses API for new projects, but Chat Completions still fully supported |

**Deprecated/outdated:**
- **Completions API (`text-davinci-003`)**: Legacy API, superseded by Chat Completions - don't use
- **Flask dev server for SSE**: Never worked properly for concurrent connections - always use Gunicorn
- **Storing API keys in code**: Use environment variables; this was always bad but enforcement is stricter now

**Note on Responses API:** OpenAI introduced a newer Responses API in 2025-2026 that they recommend over Chat Completions for new projects. However, Chat Completions is still fully supported and more widely documented. For this phase, **stick with Chat Completions** unless specific Responses API features are needed (they're not for this use case).

## Open Questions

Things that couldn't be fully resolved:

1. **Frontend framework for SSE**
   - What we know: EventSource API is built into browsers, works with vanilla JS
   - What's unclear: Phase 2 frontend stack - React/Vue/etc may have preferred patterns for SSE
   - Recommendation: Vanilla EventSource example provided; adapt to Phase 2 framework during implementation

2. **Production deployment requirements**
   - What we know: Gunicorn with gevent workers needed for SSE
   - What's unclear: Actual deployment target (cloud provider, container setup)
   - Recommendation: Document Gunicorn command in README; deployment config is out of scope for this phase

3. **Token usage monitoring**
   - What we know: OpenAI bills per token; typical job overview is ~300 output tokens
   - What's unclear: Whether to implement token tracking/budgeting
   - Recommendation: Not required for v1; OpenAI dashboard provides usage monitoring

4. **Prompt template storage**
   - What we know: Prompt should be versioned and tracked
   - What's unclear: Whether to store templates in database vs. code constants
   - Recommendation: Start with code constants (easier to iterate); move to database if non-technical users need to edit prompts

## Sources

### Primary (HIGH confidence)
- [OpenAI Python SDK GitHub](https://github.com/openai/openai-python) - Installation, streaming patterns, API usage
- [OpenAI Chat Completions API Reference](https://platform.openai.com/docs/api-reference/chat) - Message structure, parameters
- [OpenAI GPT-4o Model Page](https://platform.openai.com/docs/models/gpt-4o) - Specifications and capabilities
- [OpenAI Rate Limits Guide](https://platform.openai.com/docs/guides/rate-limits) - Error codes and retry strategies
- [OpenAI Error Codes](https://platform.openai.com/docs/guides/error-codes) - Exception types

### Secondary (MEDIUM confidence)
- [Flask SSE without dependencies](https://maxhalford.github.io/blog/flask-sse-no-deps/) - Generator pattern for SSE
- [OpenAI Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering) - Best practices (verified via multiple sources)
- [Flask Session Management](https://testdriven.io/blog/flask-sessions/) - Session patterns and security
- [OpenAI Rate Limit Handling Cookbook](https://cookbook.openai.com/examples/how_to_handle_rate_limits) - Retry logic patterns

### Tertiary (LOW confidence - WebSearch only)
- Various blog posts on Flask SSE integration - general patterns confirmed but specific code not verified
- Community discussions on OpenAI streaming bugs - known issues documented
- Prompt engineering guides from Palantir, Google Cloud - high-level concepts applicable but not OpenAI-specific

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Official OpenAI SDK is the only reasonable choice; Flask already in project
- Architecture: HIGH - Patterns verified from official docs and widely used in production
- Pitfalls: HIGH - Common issues documented in official guides and experienced by many developers
- Prompt engineering: MEDIUM - Best practices are established but job description generation is domain-specific

**Research date:** 2026-01-21
**Valid until:** ~30 days (stable technologies; OpenAI API is mature)

**Notes:**
- OpenAI's Responses API is newly recommended but Chat Completions is still standard and better documented - use Chat Completions
- SSE with Flask generators requires no additional dependencies (no Redis needed)
- Gunicorn+gevent is essential even in development if testing SSE
- Provenance tracking via Flask session is appropriate for temporary state until PDF export
