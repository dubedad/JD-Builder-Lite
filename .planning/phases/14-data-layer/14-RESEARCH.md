# Phase 14: Data Layer - Research

**Researched:** 2026-02-03
**Domain:** Web scraping, ETL data pipelines, SQLite reference data management
**Confidence:** HIGH

## Summary

Phase 14 involves scraping TBS occupational group definitions from Canada.ca government websites and building a SQLite reference data lookup table with full provenance tracking. The user has decided on SQLite for storage, append-only design with effective dates, and comprehensive HTTP-level provenance for DADM/TBS compliance.

The standard Python web scraping stack (requests + BeautifulSoup4 with lxml parser) is well-established and current as of 2026. SQLite is appropriate for reference data with normalized schema design (master groups + child inclusions/exclusions). The ETL pattern requires validation at extraction, transformation, and load stages to ensure completeness, accuracy, and consistency per DAMA-DMBOK 2.0.

Key challenges include handling HTML parsing fragility (government sites may change structure), implementing polite rate limiting (1 req/sec as user decided), managing retry logic with exponential backoff, and ensuring atomic transactions so partial data never persists.

**Primary recommendation:** Use requests.Session with HTTPAdapter for retry logic, BeautifulSoup4 with lxml parser for speed and robustness, direct SQLite inserts with parameterized queries (not pandas for this scale), WAL mode for concurrency, and comprehensive validation before any database writes.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| requests | 2.32.5 | HTTP client for web scraping | Industry standard, 30M downloads/week, excellent session management |
| beautifulsoup4 | 4.14.3 | HTML parsing and extraction | Most popular Python HTML parser, handles malformed HTML gracefully |
| lxml | latest | Parser backend for BeautifulSoup | 11x faster than html.parser, written in C, best balance of speed/robustness |
| sqlite3 | stdlib | Relational database for reference data | Python stdlib, perfect for local reference data, ACID transactions |
| hashlib | stdlib | SHA-256 content hashing | Python stdlib, FIPS-compliant secure hashing |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| urllib3 | latest (via requests) | HTTP connection pooling, retry logic | Automatic via requests, configure HTTPAdapter for retries |
| backoff | latest | Exponential backoff decorators | Optional, can implement manually or use urllib3.Retry |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| lxml parser | html.parser (stdlib) | html.parser is 1.5x slower but has no external dependencies |
| lxml parser | html5lib | html5lib is most lenient but significantly slower, only if lxml fails |
| SQLite | PostgreSQL | Overkill for reference data, adds deployment complexity |
| requests | httpx | httpx adds async support but unnecessary for 1 req/sec rate limit |

**Installation:**
```bash
pip install requests beautifulsoup4 lxml
# sqlite3 and hashlib are Python stdlib
```

## Architecture Patterns

### Recommended Project Structure
```
src/
├── scrapers/           # Web scraping logic
│   ├── tbs_scraper.py  # Main scraper orchestrator
│   ├── html_parser.py  # BeautifulSoup extraction logic
│   └── http_client.py  # Requests session with retry/rate-limit
├── storage/            # Database layer
│   ├── schema.sql      # DDL for all tables
│   ├── db_manager.py   # Connection management, WAL mode
│   └── repository.py   # Insert/update operations with validation
├── models/             # Data models
│   ├── occupational_group.py
│   ├── inclusion.py
│   └── provenance.py
└── validation/         # Data quality checks
    ├── completeness.py # All required fields present
    ├── consistency.py  # Foreign keys valid, dates logical
    └── accuracy.py     # Format validation, duplicate detection
data/
├── occupational.db     # SQLite database
└── html_archive/       # Raw HTML files with timestamps
    ├── occupational-groups-YYYY-MM-DD-HHMMSS.html
    └── definitions-YYYY-MM-DD-HHMMSS.html
```

### Pattern 1: ETL Pipeline with Validation Gates
**What:** Extract → Validate → Transform → Validate → Load → Validate pattern ensures no corrupt data enters database.
**When to use:** All ETL operations, especially for reference data requiring high integrity.
**Example:**
```python
# Pattern: Validate at each stage, fail fast, never insert partial data
def scrape_and_load():
    # EXTRACT
    raw_html = extract_from_url(url)
    validate_http_response(raw_html)  # 200 status, content-type, size > 0

    # TRANSFORM
    parsed_data = transform_html_to_models(raw_html)
    validate_completeness(parsed_data)  # All required fields present
    validate_consistency(parsed_data)   # Foreign keys resolve, no orphans
    validate_accuracy(parsed_data)      # Formats correct, no duplicates

    # LOAD (atomic transaction)
    with db.transaction():
        load_to_database(parsed_data)
        validate_database_state()  # Row counts match, constraints hold
```

### Pattern 2: Append-Only Temporal Design
**What:** Never UPDATE or DELETE, only INSERT with effective_from/effective_to dates to maintain full history.
**When to use:** Reference data that changes rarely, audit requirements, provenance tracking.
**Example:**
```python
# Schema pattern: temporal validity tracking
CREATE TABLE dim_occupational_group (
    id INTEGER PRIMARY KEY,
    group_code TEXT NOT NULL,
    subgroup TEXT,
    definition TEXT NOT NULL,
    effective_from TEXT NOT NULL,  -- ISO 8601 timestamp
    effective_to TEXT,              -- NULL means currently valid
    source_url TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    scraped_at TEXT NOT NULL,
    UNIQUE(group_code, subgroup, effective_from)
);

# Query current data: WHERE effective_to IS NULL
# Query historical: WHERE effective_from <= date AND (effective_to IS NULL OR effective_to > date)
```

### Pattern 3: Session-Based HTTP with Retry Logic
**What:** Reuse requests.Session with configured HTTPAdapter for automatic retries with exponential backoff.
**When to use:** All HTTP operations in scrapers.
**Example:**
```python
# Source: Verified with requests 2.32.5 docs + 2026 best practices
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import requests

def create_scraping_session():
    session = requests.Session()

    # Retry on 429 (rate limit), 500, 502, 503, 504 (server errors)
    retry_strategy = Retry(
        total=3,                          # Max 3 retries
        backoff_factor=2,                 # Wait 2, 4, 8 seconds
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "HEAD"]   # Only retry safe methods
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    # Set User-Agent for transparency (IETF best practice)
    session.headers.update({
        'User-Agent': 'JD-Builder/1.0 (TBS Occupational Data Scraper; Contact: your-email@example.com)'
    })

    return session

# Usage with rate limiting (user decided: 1 req/sec)
import time

session = create_scraping_session()
for url in urls:
    response = session.get(url, timeout=30)  # Always set timeout
    # Process response
    time.sleep(1.0)  # Polite 1-second delay between requests
```

### Pattern 4: Content-Addressed HTML Archiving
**What:** Save raw HTML with SHA-256 hash as filename, compare hashes to detect changes.
**When to use:** Provenance tracking, change detection, ability to re-parse without re-scraping.
**Example:**
```python
# Source: Python hashlib stdlib + 2026 integrity verification best practices
import hashlib
from pathlib import Path

def archive_html(content: bytes, url: str, timestamp: str) -> str:
    """Archive raw HTML and return content hash."""
    # Calculate SHA-256 hash
    content_hash = hashlib.sha256(content).hexdigest()

    # Save with descriptive name + hash
    filename = f"{url.split('/')[-1]}-{timestamp}-{content_hash[:8]}.html"
    archive_path = Path("data/html_archive") / filename

    archive_path.parent.mkdir(parents=True, exist_ok=True)
    archive_path.write_bytes(content)

    return content_hash

def content_changed(url: str, new_content: bytes, db) -> bool:
    """Check if content has changed since last scrape."""
    new_hash = hashlib.sha256(new_content).hexdigest()
    last_hash = db.get_last_content_hash(url)
    return new_hash != last_hash
```

### Pattern 5: Provenance Chain Tracking
**What:** Capture HTTP-level metadata (URL, timestamp, headers, status, hash) and link parsed data to source location.
**When to use:** DADM compliance, TBS audit requirements, traceable data lineage.
**Example:**
```python
# Provenance data model
class Provenance:
    url: str                    # Source URL
    scraped_at: datetime        # ISO 8601 timestamp
    http_status: int            # 200, 404, etc.
    http_headers: dict          # Response headers (JSON)
    content_hash: str           # SHA-256 of response body
    archive_path: str           # Path to saved HTML file
    parser_version: str         # Code version that parsed this

class Inclusion:
    id: int
    group_id: int               # FK to occupational_group
    statement: str
    order: int                  # Position in original list
    source_provenance_id: int   # FK to provenance
    paragraph_label: str        # e.g., "P3" for allocation guide

# Database captures full chain: Inclusion → Provenance → Archive → HTTP Response
```

### Anti-Patterns to Avoid
- **Scraping without User-Agent:** Government sites may block or log anonymous scrapers. Always identify your scraper with contact info (IETF recommendation).
- **No retry logic:** Network is unreliable. Use HTTPAdapter with Retry, not manual try/except loops.
- **String interpolation in SQL:** SQL injection risk. Always use parameterized queries: `cursor.execute("INSERT INTO x VALUES (?)", (value,))`
- **Pandas for small ETL:** Pandas adds memory overhead. For <100k rows, direct SQLite inserts with executemany() are faster and simpler.
- **UPDATE/DELETE in append-only design:** Breaks temporal history. Always INSERT new rows with effective dates.
- **Parsing without error handling:** HTML structure changes. Wrap all BeautifulSoup selectors in try/except, validate extracted data.

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| HTTP retries with backoff | Manual time.sleep() + retry loop | urllib3.Retry + HTTPAdapter | Handles edge cases: jitter, which methods to retry, backoff calculation, max retries. Battle-tested. |
| Content hashing | Custom hash function | hashlib.sha256() | FIPS-compliant, optimized C implementation, handles large files with streaming. |
| SQL injection prevention | Manual string escaping | Parameterized queries (? placeholders) | sqlite3 handles all escaping, type conversion, edge cases. String escaping always has bugs. |
| HTML parsing | Manual regex | BeautifulSoup + lxml | Regex cannot parse HTML (famous Stack Overflow post). BeautifulSoup handles malformed HTML, nested tags, character encoding. |
| Database transactions | Manual COMMIT/ROLLBACK | Context manager (with conn:) | Ensures ROLLBACK on exception, handles nested transactions correctly. |
| Temporal validity queries | Manual date comparison logic | SQL: WHERE effective_to IS NULL | Database indexes temporal queries, handles NULL semantics correctly, prevents logic bugs. |

**Key insight:** Web scraping and ETL have 15+ years of battle-tested patterns in Python. Don't reinvent HTTP clients, HTML parsers, or retry logic. Focus implementation effort on domain-specific validation rules and data quality checks.

## Common Pitfalls

### Pitfall 1: Rate Limiting Violations Leading to IP Bans
**What goes wrong:** Scraper makes requests too quickly, government server detects bot behavior, blocks IP address.
**Why it happens:** Default requests behavior has no delays. Developers forget to add sleep() between requests.
**How to avoid:**
- Implement explicit rate limiting (user decided: 1 req/sec)
- Use time.sleep(1.0) after each request
- Consider token bucket pattern for more sophisticated rate limiting
- Monitor 429 status codes (Too Many Requests)
**Warning signs:**
- 429 HTTP status codes
- Connection timeouts
- CAPTCHAs appearing
- Requests taking longer (server throttling)

### Pitfall 2: Parsing Fragility When HTML Structure Changes
**What goes wrong:** TBS updates website HTML structure, scraper's BeautifulSoup selectors break, extraction fails silently or returns empty data.
**Why it happens:** Hardcoded CSS selectors (e.g., "div.content > p:nth-child(3)") are brittle. Government sites change without notice.
**How to avoid:**
- Use semantic selectors when possible (h4 text="Inclusions" vs. div:nth-child)
- Validate extracted data immediately after parsing
- Test for None/empty results before using parsed data
- Log warnings when expected elements missing
- Keep raw HTML archive so you can debug failures post-mortem
**Warning signs:**
- Validation failures (missing required fields)
- Empty strings where data expected
- None values in parsed results
- Different number of inclusions/exclusions than expected

### Pitfall 3: Partial Data Insertion on Validation Failure
**What goes wrong:** Scraper inserts some rows, validation fails midway, database left in inconsistent state (some groups loaded, others missing).
**Why it happens:** Not using database transactions, or committing too frequently.
**How to avoid:**
- Wrap entire load operation in single transaction
- Validate ALL data before starting transaction
- Use SQLite transaction: `with conn:` (auto-rollback on exception)
- Never commit inside loops
- Implement "all or nothing" principle: if any group fails validation, rollback everything
**Warning signs:**
- Inconsistent row counts between tables (10 groups but 7 definitions)
- Foreign key constraint violations
- Orphaned child records (inclusions without parent group)
- Database state differs between runs despite same source data

### Pitfall 4: SQLite Locking in WAL Mode
**What goes wrong:** Multiple processes try to write to SQLite simultaneously, get "database is locked" errors.
**Why it happens:** SQLite allows multiple readers OR one writer. WAL mode helps but doesn't eliminate all locking.
**How to avoid:**
- Single writer pattern: only one process should run scraper
- Use WAL mode for better concurrency: PRAGMA journal_mode=WAL
- Keep transactions short (don't hold write lock during HTTP requests)
- Set busy_timeout: conn.execute("PRAGMA busy_timeout = 5000")
- For this use case: manual trigger only (user decided), so single process is guaranteed
**Warning signs:**
- sqlite3.OperationalError: database is locked
- Slow writes
- Timeout errors

### Pitfall 5: Character Encoding Issues from Government HTML
**What goes wrong:** French text with accented characters (é, à, ç) becomes mojibake or causes UnicodeDecodeError.
**Why it happens:** Assuming UTF-8 when server sends ISO-8859-1 or Windows-1252, or not handling BOM.
**How to avoid:**
- Use requests, not urllib (requests auto-detects encoding)
- Always use response.content (bytes) not response.text if encoding unclear
- Pass .content to BeautifulSoup, let lxml detect encoding
- Store as UTF-8 in database (SQLite default TEXT encoding)
- Test with French content from bilingual government sites
**Warning signs:**
- UnicodeDecodeError or UnicodeEncodeError
- Accented characters display as � or &#233;
- Database queries fail on French text

### Pitfall 6: Timestamp Inconsistency Across Scrape
**What goes wrong:** Use CURRENT_TIMESTAMP for each INSERT, get different timestamps for related records from same scrape run.
**Why it happens:** CURRENT_TIMESTAMP evaluated per statement in SQLite, not per transaction.
**How to avoid:**
- Capture timestamp once at start of scrape operation
- Pass same timestamp to all inserts: scraped_at = datetime.now(timezone.utc).isoformat()
- Store as TEXT in ISO 8601 format: YYYY-MM-DDTHH:MM:SS+00:00
- Use UTC to avoid timezone ambiguity
**Warning signs:**
- Provenance records have timestamps minutes apart despite 1-second rate limit
- Can't identify which records came from same scrape run
- Temporal queries return unexpected results

### Pitfall 7: Missing Validation for Required Fields
**What goes wrong:** Scraper inserts group with NULL definition or missing group_code, violates data quality requirements.
**Why it happens:** BeautifulSoup returns None when element not found, code doesn't check before inserting.
**How to avoid:**
- Validate completeness before any database operation
- Check: group_code, definition, source_url are all non-empty
- Check: inclusions list is not empty (per DAMA: validate completeness)
- Raise exception if validation fails, don't insert partial data
- Log detailed error: which field missing, which URL, what was extracted
**Warning signs:**
- NULL values in NOT NULL columns (caught by database constraint)
- Empty strings in definition field
- Groups with zero inclusions/exclusions
- Validation error logs

## Code Examples

Verified patterns from official sources:

### BeautifulSoup HTML Parsing with Error Handling
```python
# Source: BeautifulSoup 4.14.3 docs + 2026 scraping best practices
from bs4 import BeautifulSoup
from typing import Optional, List

def parse_occupational_group(html: bytes) -> dict:
    """Parse single occupational group definition section."""
    soup = BeautifulSoup(html, 'lxml')  # lxml parser for speed

    try:
        # Find group heading (h3 with group name)
        heading = soup.find('h3', id=lambda x: x and x.startswith('def-'))
        if not heading:
            raise ValueError("Group heading not found")

        group_code = heading.get('id').replace('def-', '').upper()

        # Definition statement (first p after h3)
        definition_p = heading.find_next_sibling('p')
        if not definition_p:
            raise ValueError(f"Definition not found for {group_code}")
        definition = definition_p.get_text(strip=True)

        # Inclusions section (h4 with text "Inclusions" → ol)
        inclusions_heading = soup.find('h4', string='Inclusions')
        inclusions = []
        if inclusions_heading:
            inclusions_list = inclusions_heading.find_next_sibling('ol')
            if inclusions_list:
                inclusions = [
                    li.get_text(strip=True)
                    for li in inclusions_list.find_all('li')
                ]

        # Exclusions section (h4 with text "Exclusions" → ol)
        exclusions_heading = soup.find('h4', string='Exclusions')
        exclusions = []
        if exclusions_heading:
            exclusions_list = exclusions_heading.find_next_sibling('ol')
            if exclusions_list:
                exclusions = [
                    li.get_text(strip=True)
                    for li in exclusions_list.find_all('li')
                ]

        return {
            'group_code': group_code,
            'definition': definition,
            'inclusions': inclusions,
            'exclusions': exclusions
        }

    except (AttributeError, ValueError) as e:
        # Log error with context, don't crash entire scrape
        print(f"Parse error: {e}")
        return None
```

### SQLite Transaction with Validation
```python
# Source: Python sqlite3 stdlib docs + 2026 ETL validation best practices
import sqlite3
from typing import List
from datetime import datetime, timezone

def load_groups_transactional(groups: List[dict], db_path: str):
    """Load groups with full validation in atomic transaction."""
    # Validate before opening transaction
    for group in groups:
        if not group.get('group_code'):
            raise ValueError(f"Missing group_code: {group}")
        if not group.get('definition'):
            raise ValueError(f"Missing definition for {group['group_code']}")
        if not group.get('source_url'):
            raise ValueError(f"Missing source_url for {group['group_code']}")

    scraped_at = datetime.now(timezone.utc).isoformat()

    # All validation passed, now open transaction
    conn = sqlite3.connect(db_path)
    try:
        with conn:  # Auto-commit on success, rollback on exception
            cursor = conn.cursor()

            # Insert groups (parameterized query prevents SQL injection)
            for group in groups:
                cursor.execute("""
                    INSERT INTO dim_occupational_group
                    (group_code, subgroup, definition, effective_from,
                     source_url, content_hash, scraped_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    group['group_code'],
                    group.get('subgroup'),
                    group['definition'],
                    scraped_at,  # Same timestamp for all
                    group['source_url'],
                    group['content_hash'],
                    scraped_at
                ))

                group_id = cursor.lastrowid

                # Insert inclusions (child records)
                for order, statement in enumerate(group.get('inclusions', []), 1):
                    cursor.execute("""
                        INSERT INTO dim_occupational_inclusion
                        (group_id, statement, order_num)
                        VALUES (?, ?, ?)
                    """, (group_id, statement, order))

            # Validate database state before commit
            cursor.execute("SELECT COUNT(*) FROM dim_occupational_group")
            group_count = cursor.fetchone()[0]
            if group_count != len(groups):
                raise ValueError(f"Expected {len(groups)} groups, got {group_count}")

        print(f"Successfully loaded {len(groups)} groups")

    except Exception as e:
        print(f"Transaction failed: {e}")
        raise
    finally:
        conn.close()
```

### SHA-256 Content Hashing for Change Detection
```python
# Source: Python hashlib stdlib docs (updated 2026-02-03)
import hashlib
from pathlib import Path

def calculate_content_hash(content: bytes) -> str:
    """Calculate SHA-256 hash of content."""
    return hashlib.sha256(content).hexdigest()

def calculate_file_hash(file_path: Path) -> str:
    """Calculate SHA-256 hash of large file efficiently (streaming)."""
    sha256_hash = hashlib.sha256()

    # Read in 64kb chunks to handle large files
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha256_hash.update(chunk)

    return sha256_hash.hexdigest()

# Usage in scraper
def should_reprocess(url: str, new_content: bytes, db) -> bool:
    """Check if content has changed since last scrape."""
    new_hash = calculate_content_hash(new_content)
    last_hash = db.get_last_content_hash_for_url(url)

    if last_hash is None:
        print(f"First scrape of {url}")
        return True

    if new_hash != last_hash:
        print(f"Content changed for {url}: {last_hash[:8]} → {new_hash[:8]}")
        return True

    print(f"Content unchanged for {url}, skipping reprocess")
    return False
```

### SQLite Schema with Temporal Design and Foreign Keys
```python
# Source: SQLite foreign key docs + temporal database patterns
schema_sql = """
-- Enable foreign keys (disabled by default in SQLite)
PRAGMA foreign_keys = ON;

-- Enable WAL mode for better concurrency
PRAGMA journal_mode = WAL;

-- Provenance tracking (HTTP-level metadata)
CREATE TABLE IF NOT EXISTS scrape_provenance (
    id INTEGER PRIMARY KEY,
    url TEXT NOT NULL,
    scraped_at TEXT NOT NULL,        -- ISO 8601 UTC
    http_status INTEGER NOT NULL,
    http_headers TEXT,                -- JSON
    content_hash TEXT NOT NULL,       -- SHA-256
    archive_path TEXT NOT NULL,       -- Path to saved HTML
    parser_version TEXT NOT NULL
);

-- Master table: occupational groups (append-only temporal)
CREATE TABLE IF NOT EXISTS dim_occupational_group (
    id INTEGER PRIMARY KEY,
    group_code TEXT NOT NULL,
    subgroup TEXT,
    definition TEXT NOT NULL,
    qualification_standard TEXT,
    rates_of_pay_represented TEXT,
    rates_of_pay_unrepresented TEXT,
    effective_from TEXT NOT NULL,     -- ISO 8601 UTC
    effective_to TEXT,                 -- NULL = currently valid
    source_provenance_id INTEGER NOT NULL,
    FOREIGN KEY (source_provenance_id) REFERENCES scrape_provenance(id),
    UNIQUE (group_code, subgroup, effective_from)
);

-- Child table: inclusions (normalized, links to provenance)
CREATE TABLE IF NOT EXISTS dim_occupational_inclusion (
    id INTEGER PRIMARY KEY,
    group_id INTEGER NOT NULL,
    statement TEXT NOT NULL,
    order_num INTEGER NOT NULL,       -- Original list position
    paragraph_label TEXT,              -- e.g., "P3" for allocation guide
    source_provenance_id INTEGER NOT NULL,
    FOREIGN KEY (group_id) REFERENCES dim_occupational_group(id),
    FOREIGN KEY (source_provenance_id) REFERENCES scrape_provenance(id)
);

-- Child table: exclusions (normalized, links to provenance)
CREATE TABLE IF NOT EXISTS dim_occupational_exclusion (
    id INTEGER PRIMARY KEY,
    group_id INTEGER NOT NULL,
    statement TEXT NOT NULL,
    order_num INTEGER NOT NULL,
    paragraph_label TEXT,
    source_provenance_id INTEGER NOT NULL,
    FOREIGN KEY (group_id) REFERENCES dim_occupational_group(id),
    FOREIGN KEY (source_provenance_id) REFERENCES scrape_provenance(id)
);

-- Human verification events (DADM human-in-loop compliance)
CREATE TABLE IF NOT EXISTS verification_event (
    id INTEGER PRIMARY KEY,
    group_id INTEGER NOT NULL,
    verified_at TEXT NOT NULL,        -- ISO 8601 UTC
    verified_by TEXT NOT NULL,        -- Username or email
    verification_notes TEXT,
    FOREIGN KEY (group_id) REFERENCES dim_occupational_group(id)
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_group_code ON dim_occupational_group(group_code);
CREATE INDEX IF NOT EXISTS idx_effective_dates ON dim_occupational_group(effective_from, effective_to);
CREATE INDEX IF NOT EXISTS idx_current_groups ON dim_occupational_group(effective_to) WHERE effective_to IS NULL;
CREATE INDEX IF NOT EXISTS idx_provenance_url ON scrape_provenance(url);
CREATE INDEX IF NOT EXISTS idx_provenance_hash ON scrape_provenance(content_hash);

-- View for current (active) occupational groups
CREATE VIEW IF NOT EXISTS v_current_occupational_groups AS
SELECT
    g.id,
    g.group_code,
    g.subgroup,
    g.definition,
    g.qualification_standard,
    g.rates_of_pay_represented,
    g.rates_of_pay_unrepresented,
    g.effective_from,
    p.url as source_url,
    p.scraped_at,
    p.content_hash
FROM dim_occupational_group g
JOIN scrape_provenance p ON g.source_provenance_id = p.id
WHERE g.effective_to IS NULL;
"""
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| html.parser (stdlib) | lxml via BeautifulSoup | lxml stable since 2010s | 11x faster parsing, handles malformed HTML better |
| Manual retry loops | urllib3.Retry + HTTPAdapter | urllib3 v1.0 (2013), refined 2020s | Exponential backoff, jitter, configurable status codes |
| SQLite default journal mode | WAL (write-ahead logging) | SQLite 3.7.0 (2010) | Readers don't block writers, 2-3x faster writes |
| Pandas for all ETL | Direct SQLite for small data | Community shift 2020s | Pandas adds memory overhead, slower for <100k rows |
| String concatenation SQL | Parameterized queries | Always best practice, emphasized post-2015 | Prevents SQL injection, handles escaping correctly |
| CURRENT_TIMESTAMP per row | Application-level timestamp | Temporal database patterns 2010s | Consistent timestamps across transaction |

**Deprecated/outdated:**
- **BeautifulSoup 3:** Deprecated, use BeautifulSoup4 (current: 4.14.3, Nov 2025)
- **Python 2 support:** Ended Jan 1, 2021. Use Python 3.9+ (requests requires 3.9+, BeautifulSoup requires 3.7+)
- **requests.get() without timeout:** Now considered bad practice (can hang indefinitely), always set timeout parameter
- **Ignoring robots.txt:** Was common 2000s-2010s, now considered unethical and may violate ToS (verify canada.ca allows scraping)

## Open Questions

Things that couldn't be fully resolved:

1. **Table of Concordance structure**
   - What we know: User wants to scrape Table of Concordance linking groups ↔ evaluation standards (DATA-05)
   - What's unclear: Exact URL and HTML structure of this table
   - Recommendation: During planning, fetch https://www.canada.ca/en/treasury-board-secretariat/services/collective-agreements/occupational-groups.html and identify "Concordance" table structure. WebFetch showed "Job evaluation standard" column with links, may be the concordance data.

2. **Allocation guide paragraph labeling convention**
   - What we know: User wants paragraphs labeled P1, P2, P3... for provenance map
   - What's unclear: How to identify paragraph boundaries (by <p> tag? by heading? by semantic sections?)
   - Recommendation: Fetch https://www.canada.ca/en/treasury-board-secretariat/services/classification/job-evaluation/guide-allocating-positions-using-occupational-group-definitions.html and define labeling rules. Likely each <p> or <li> gets sequential label.

3. **Subgroup representation in database**
   - What we know: Groups have subgroups (e.g., AI has "Non-Operational" subgroup)
   - What's unclear: Are subgroups separate rows (group_code + subgroup unique) or child table?
   - Recommendation: Single table with group_code + subgroup columns (user's "master + child" means groups are master, inclusions/exclusions are children). Subgroups share same group_code but different definition URL anchor.

4. **Handling of bilingual content**
   - What we know: Canada.ca is bilingual (EN/FR), URLs have /en/ prefix
   - What's unclear: Should scraper get both languages or English only?
   - Recommendation: Scrape English only for v4.0 (URLs provided are /en/). French could be separate phase or DATA-06. Confirm with user in planning.

5. **Retry strategy for permanent failures**
   - What we know: User decided "fail explicitly, keep existing data, alert operator"
   - What's unclear: What constitutes "permanent" vs "transient" failure? Retry 3 times then fail?
   - Recommendation: Retry transient errors (429, 5xx) with backoff. Fail immediately on client errors (404, 403). Log all failures with context. Don't update database on failure (keep last good data).

## Sources

### Primary (HIGH confidence)
- BeautifulSoup 4.14.3: https://pypi.org/project/beautifulsoup4/ (verified Nov 30, 2025 release)
- Requests 2.32.5: https://pypi.org/project/requests/ (verified Aug 18, 2025 release)
- Python hashlib stdlib: https://docs.python.org/3/library/hashlib.html (updated 2026-02-03)
- SQLite WAL mode: https://sqlite.org/wal.html (official docs)
- SQLite Foreign Keys: https://sqlite.org/foreignkeys.html (official docs)
- Canada.ca occupational groups: https://www.canada.ca/en/treasury-board-secretariat/services/collective-agreements/occupational-groups.html (fetched 2026-02-03)
- Canada.ca robots.txt: https://www.canada.ca/robots.txt (no crawl-delay directive, TBS paths not disallowed)

### Secondary (MEDIUM confidence)
- [Beautiful Soup: Build a Web Scraper With Python – Real Python](https://realpython.com/beautiful-soup-web-scraper-python/)
- [Scraping Best Practices | CodeSignal Learn](https://codesignal.com/learn/courses/implementing-scalable-web-scraping-with-python/lessons/scraping-best-practices)
- [Data Validation in ETL - 2026 Guide | Integrate.io](https://www.integrate.io/blog/data-validation-etl/)
- [Best Practices for Database Schema Design in SQLite | MoldStud](https://moldstud.com/articles/p-best-practices-for-database-schema-design-in-sqlite)
- [Retry Failed Python Requests in 2026 | Decodo](https://decodo.com/blog/python-requests-retry)
- [BeautifulSoup vs lxml: A Practical Performance Comparison - DEV Community](https://dev.to/dmitriiweb/beautifulsoup-vs-lxml-a-practical-performance-comparison-1l0a)
- [Data Pipeline Design Patterns - #2. Coding patterns in Python – Start Data Engineering](https://www.startdataengineering.com/post/code-patterns/)
- [Going Fast with SQLite and Python | Charles Leifer](https://charlesleifer.com/blog/going-fast-with-sqlite-and-python/)

### Tertiary (LOW confidence - community sources)
- [10 Tips on How to make Python's Beautiful Soup faster when scraping | ScrapingBee](https://www.scrapingbee.com/blog/how-to-make-pythons-beautiful-soup-faster-performance/) - Parser performance claims
- [Auditing and Versioning Data in SQLite | ByteFish](https://www.bytefish.de/blog/sqlite_logging_changes.html) - Temporal table patterns (not official)
- [Data Lineage Tracking: Complete Guide for 2026 | Atlan](https://atlan.com/know/data-lineage-tracking/) - Lineage concepts (not Python-specific implementation)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All libraries verified from PyPI with current versions (requests 2.32.5, beautifulsoup4 4.14.3)
- Architecture: HIGH - ETL patterns verified across multiple authoritative sources, SQLite temporal design is established pattern
- Pitfalls: HIGH - Common scraping and SQLite pitfalls documented in official docs + 2026 best practices articles
- Code examples: HIGH - All examples use stdlib (sqlite3, hashlib) or verified library versions, patterns confirmed in official docs

**Research date:** 2026-02-03
**Valid until:** 2026-03-03 (30 days, stable stack - requests/BeautifulSoup have mature APIs)

**Notes:**
- User decisions constrain implementation: SQLite (not alternatives), append-only design (not updates), 1 req/sec rate limit
- Claude's discretion areas: exact schema design, HTML parsing selectors, retry parameters
- Key risk: HTML structure changes on canada.ca break parsing (mitigate: validate extraction, keep archives, log errors)
- DAMA-DMBOK 2.0 compliance achieved via: normalized schema, provenance chain, validation gates, append-only history
