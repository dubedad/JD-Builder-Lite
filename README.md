# JobForge - Job Description Builder

> Compliance-focused job description builder demonstrating TBS Directive 32592 compliance with full provenance tracking.

## Overview

**JobForge** helps Government of Canada managers build TBS-compliant job descriptions with full provenance tracking from authoritative data sources. Every statement in a generated job description is traceable to its source (ESDC NOC 2025 v1.0 or O*NET 27.2), with publication dates, source URLs, and automated decision-making transparency.

### Key Features

- **Authoritative Sources**: ESDC National Occupational Classification (NOC) 2025 v1.0 and O*NET 27.2 data
- **Classification Guidance**: Occupational group allocation (Classification Step 1) with confidence scoring and evidence extraction
- **Full Provenance**: Every selection linked to data steward, publication date, and source URL
- **Export Formats**: PDF and Word with embedded compliance metadata and classification results
- **Medallion Architecture**: Bronze → Silver → Gold data layers for audit transparency
- **AI Transparency**: All AI-generated content clearly labeled with model, timestamp, and modification tracking

### For Reviewers / Auditors

**Compliance Mapping to TBS Directive 32592 (Automated Decision Making):**

| Requirement | How Met | Evidence Location |
|-------------|---------|-------------------|
| **6.2.3** - Document input data, source, method of collection | ESDC NOC and O*NET data with retrieval timestamps and URLs | Compliance Appendix → Data Sources |
| **6.2.7** - Document decisions made/assisted by automated systems | Manager selections tracked with timestamps and provenance | Compliance Appendix → Documented Decisions |
| **6.3.5** - Data must be relevant, accurate, up-to-date | NOC version tracking, scrape timestamps, direct OASIS retrieval | Compliance Appendix → Data Quality Validation |
| **AI Disclosure** - Transparency for AI-generated content | LLM model, prompt version, input IDs, modification flags | Compliance Appendix → AI-Generated Content Disclosure |
| **Classification Audit Trail** - Automated classification transparency | Tool version, data sources, constraints, provenance URLs | Classification Section → Audit Trail |

**Classification Algorithm (Step 1 - Occupational Group Allocation):**

The classification engine uses a 5-step process:
1. **Shortlisting**: Match job description to NOC Broad Occupational Categories
2. **LLM Classification**: OpenAI GPT-4o analyzes JD against TBS occupational group definitions
3. **Confidence Scoring**: 0.0-1.0 scale based on definition fit
4. **Evidence Extraction**: Identifies supporting quotes from job description
5. **Provenance Linking**: Each recommendation linked to authoritative TBS directive URL

### Screenshots

<!-- TODO: Add screenshots -->
See `docs/screenshots/` directory for visual walkthroughs:
- Search and NOC profile selection
- Job description building with proficiency levels
- Classification results with evidence highlighting
- Export preview with compliance metadata
- PDF/DOCX output samples

---

## Quick Start

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Internet connection (for ESDC NOC and O*NET data retrieval)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd jd-builder-lite
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**:

   Create a `.env` file in the project root:
   ```env
   FLASK_ENV=development
   SECRET_KEY=your-secret-key-here
   OPENAI_API_KEY=your-openai-api-key-here

   # Optional: Classification engine settings
   CLASSIFICATION_CACHE_TTL=3600
   CLASSIFICATION_MODEL=gpt-4o
   ```

4. **Initialize database**:
   ```bash
   python scripts/init_db.py
   ```

5. **Run the development server**:
   ```bash
   python app.py
   ```

6. **Open in browser**:
   ```
   http://localhost:5000
   ```

---

## Architecture

### Data Pipeline

```
ESDC NOC 2025    O*NET 27.2
      |              |
      v              v
  Scraper -----> Parser -----> Mapper
                                 |
                                 v
                   Bronze Layer (Raw HTML/JSON)
                                 |
                                 v
                   Silver Layer (Parsed Structured Data)
                                 |
                                 v
                   Gold Layer (JD Elements + Provenance)
                                 |
                                 v
                   API -----> Frontend (Builder UI)
                                 |
                                 v
                   Export (PDF/DOCX with Compliance Metadata)
```

### Classification Algorithm

**5-Step Process:**

1. **Shortlisting**:
   - Extract NOC Broad Occupational Category from job title
   - Retrieve relevant occupational groups from TBS definitions
   - Filter to ~5-10 candidate groups

2. **LLM Classification**:
   - Provide job description + TBS group definitions to GPT-4o
   - Request ranked recommendations with rationale
   - Extract confidence scores (0.0-1.0)

3. **Confidence Scoring**:
   - High: ≥80% (Strong definition fit)
   - Medium: 50-79% (Partial fit)
   - Low: <50% (Weak fit or exclusion match)

4. **Evidence Extraction**:
   - Identify job description quotes supporting each recommendation
   - Track evidence spans (text + source field)
   - Link evidence to definition paragraphs

5. **Provenance Linking**:
   - Map each group to TBS directive URL
   - Record scraped date, inclusions/exclusions referenced
   - Store in provenance_map for export

### Directory Structure

```
jd-builder-lite/
├── src/
│   ├── models/           # Pydantic models (requests, responses, domain objects)
│   ├── services/         # Business logic (scraper, parser, mapper, LLM, export)
│   ├── routes/           # Flask API routes
│   ├── storage/          # Database and cache layer
│   ├── matching/         # Classification engine (allocator, provenance builder)
│   └── utils/            # Helpers (OaSIS provenance, NOC parsing)
├── static/
│   ├── js/              # Frontend modules (main, export, classify, generation)
│   └── css/             # Styles (main, export screen/print, classify)
├── templates/
│   ├── index.html       # Single-page application shell
│   └── export/          # PDF and preview templates (jd_pdf.html, jd_preview.html)
├── data/
│   ├── noc/             # NOC bronze/silver/gold layers
│   ├── onet/            # O*NET bronze/silver/gold layers
│   └── classification/  # TBS group definitions and provenance cache
├── tests/               # Unit and integration tests
└── .planning/           # Project documentation (plans, roadmap, state)
```

---

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_mapper.py
```

### Code Style

- **Python**: PEP 8 compliance (enforced by flake8)
- **JavaScript**: ES6+ with JSDoc comments
- **HTML/CSS**: Follows GC Web Experience Toolkit patterns where applicable

### Key Design Patterns

1. **Medallion Architecture** (Bronze → Silver → Gold):
   - Bronze: Raw scraped HTML/JSON
   - Silver: Parsed structured data
   - Gold: Domain-specific mapped data with provenance

2. **Provenance-First Design**:
   - Every data point tracks: source, publication date, URL, scrape timestamp
   - Stored alongside content for compliance export

3. **Separation of Concerns**:
   - `scraper`: HTTP retrieval
   - `parser`: HTML/JSON extraction
   - `mapper`: Domain transformation
   - `export_service`: Compliance metadata builder

---

## Deployment

### Production Checklist

- [ ] Set `FLASK_ENV=production` in `.env`
- [ ] Generate secure `SECRET_KEY` (32+ random bytes)
- [ ] Configure OpenAI API key with rate limiting
- [ ] Set up HTTPS (TLS certificate)
- [ ] Enable CORS only for trusted origins
- [ ] Configure logging to file/service
- [ ] Set up monitoring (Sentry, CloudWatch, etc.)
- [ ] Review CSP headers for XSS protection

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `FLASK_ENV` | Yes | `development` or `production` |
| `SECRET_KEY` | Yes | Flask session encryption key (32+ bytes) |
| `OPENAI_API_KEY` | Yes | OpenAI API key for LLM services |
| `CLASSIFICATION_MODEL` | No | Default: `gpt-4o` |
| `CLASSIFICATION_CACHE_TTL` | No | Cache lifetime in seconds (default: 3600) |

---

## License

Internal Government of Canada tool. Not licensed for external distribution.

## Contact

For questions or issues, contact: [Your Team/Department]

---

**Version**: 4.1
**Last Updated**: 2026-02-07
**TBS Compliance**: Directive 32592 (Automated Decision Making)
