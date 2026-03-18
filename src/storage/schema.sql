-- SQLite schema for DIM_OCCUPATIONAL reference data
-- Append-only temporal design with full provenance tracking
-- DAMA-DMBOK 2.0 compliant validation

-- Enable foreign keys (disabled by default in SQLite)
PRAGMA foreign_keys = ON;

-- ============================================================================
-- Table 1: scrape_provenance - HTTP-level metadata for DADM compliance
-- ============================================================================
CREATE TABLE IF NOT EXISTS scrape_provenance (
    id INTEGER PRIMARY KEY,
    url TEXT NOT NULL,
    scraped_at TEXT NOT NULL,           -- ISO 8601 UTC
    http_status INTEGER NOT NULL,
    http_headers TEXT,                   -- JSON string
    content_hash TEXT NOT NULL,          -- SHA-256
    archive_path TEXT NOT NULL,          -- Path to saved HTML
    parser_version TEXT NOT NULL
);

-- ============================================================================
-- Table 2: dim_occupational_group - Master table with append-only temporal
-- ============================================================================
CREATE TABLE IF NOT EXISTS dim_occupational_group (
    id INTEGER PRIMARY KEY,
    group_code TEXT NOT NULL,            -- e.g., "AI", "CP"
    subgroup TEXT,                       -- e.g., "Non-Operational" for AI
    definition TEXT NOT NULL,
    qualification_standard_url TEXT,
    rates_of_pay_represented_url TEXT,
    rates_of_pay_unrepresented_url TEXT,
    effective_from TEXT NOT NULL,        -- ISO 8601 UTC
    effective_to TEXT,                   -- NULL = currently valid
    source_provenance_id INTEGER NOT NULL,
    UNIQUE(group_code, subgroup, effective_from),
    FOREIGN KEY (source_provenance_id) REFERENCES scrape_provenance(id)
);

-- ============================================================================
-- Table 3: dim_occupational_inclusion - Child table for inclusion statements
-- ============================================================================
CREATE TABLE IF NOT EXISTS dim_occupational_inclusion (
    id INTEGER PRIMARY KEY,
    group_id INTEGER NOT NULL,           -- FK to dim_occupational_group
    statement TEXT NOT NULL,
    order_num INTEGER NOT NULL,          -- Original list position
    paragraph_label TEXT,                -- e.g., "I1", "I2" for provenance
    source_provenance_id INTEGER NOT NULL,
    FOREIGN KEY (group_id) REFERENCES dim_occupational_group(id),
    FOREIGN KEY (source_provenance_id) REFERENCES scrape_provenance(id)
);

-- ============================================================================
-- Table 4: dim_occupational_exclusion - Child table for exclusion statements
-- ============================================================================
CREATE TABLE IF NOT EXISTS dim_occupational_exclusion (
    id INTEGER PRIMARY KEY,
    group_id INTEGER NOT NULL,           -- FK to dim_occupational_group
    statement TEXT NOT NULL,
    order_num INTEGER NOT NULL,          -- Original list position
    paragraph_label TEXT,                -- e.g., "E1", "E2" for provenance
    source_provenance_id INTEGER NOT NULL,
    FOREIGN KEY (group_id) REFERENCES dim_occupational_group(id),
    FOREIGN KEY (source_provenance_id) REFERENCES scrape_provenance(id)
);

-- ============================================================================
-- Table 5: verification_event - Human-in-loop tracking for DADM
-- ============================================================================
CREATE TABLE IF NOT EXISTS verification_event (
    id INTEGER PRIMARY KEY,
    group_id INTEGER NOT NULL,
    verified_at TEXT NOT NULL,           -- ISO 8601 UTC
    verified_by TEXT NOT NULL,           -- Username or email
    verification_notes TEXT,
    FOREIGN KEY (group_id) REFERENCES dim_occupational_group(id)
);

-- ============================================================================
-- Table 6: table_of_concordance - Links groups to evaluation standards (DATA-05)
-- ============================================================================
CREATE TABLE IF NOT EXISTS table_of_concordance (
    id INTEGER PRIMARY KEY,
    group_code TEXT NOT NULL,
    job_evaluation_standard_url TEXT,
    effective_from TEXT NOT NULL,        -- ISO 8601 UTC
    effective_to TEXT,                   -- NULL = currently valid
    source_provenance_id INTEGER NOT NULL,
    FOREIGN KEY (source_provenance_id) REFERENCES scrape_provenance(id)
);

-- ============================================================================
-- Indexes for common queries
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_group_code ON dim_occupational_group(group_code);
CREATE INDEX IF NOT EXISTS idx_effective_dates ON dim_occupational_group(effective_from, effective_to);
CREATE INDEX IF NOT EXISTS idx_current_groups ON dim_occupational_group(effective_to) WHERE effective_to IS NULL;
CREATE INDEX IF NOT EXISTS idx_provenance_url ON scrape_provenance(url);
CREATE INDEX IF NOT EXISTS idx_provenance_hash ON scrape_provenance(content_hash);

-- ============================================================================
-- View: v_current_occupational_groups - JOIN groups with provenance WHERE effective_to IS NULL
-- ============================================================================
CREATE VIEW IF NOT EXISTS v_current_occupational_groups AS
SELECT
    g.id,
    g.group_code,
    g.subgroup,
    g.definition,
    g.qualification_standard_url,
    g.rates_of_pay_represented_url,
    g.rates_of_pay_unrepresented_url,
    g.effective_from,
    p.url as source_url,
    p.scraped_at,
    p.content_hash
FROM dim_occupational_group g
JOIN scrape_provenance p ON g.source_provenance_id = p.id
WHERE g.effective_to IS NULL;
