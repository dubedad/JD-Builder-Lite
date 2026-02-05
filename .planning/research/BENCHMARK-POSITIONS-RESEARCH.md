# Benchmark Positions Research

**Researched:** 2026-02-04
**Purpose:** Identify sources for pre-scored benchmark positions to support v5.0 job evaluation automation

---

## Key Finding: Benchmarks ARE Publicly Available

Benchmark positions are **embedded within the Job Evaluation Standard documents** on canada.ca. They are not separate files - they're appendices or integrated sections within each standard.

---

## What a Benchmark Position Contains

| Field | Description | Example |
|-------|-------------|---------|
| **Position Title** | Descriptive title | "Senior Policy Manager" |
| **Level Classification** | Target level | EC-05 |
| **Total Points** | Sum of all factor scores | 420 points |
| **Organization Context** | Department/unit setting | "Reports to DG in policy branch..." |
| **Principal Duties** | Key responsibilities list | 5-8 bullet points |
| **Factor Ratings** | Degree per factor | "DM: 5, LO: 3, CO: 4..." |
| **Points per Factor** | Score breakdown | "DM: 90, LO: 50, CO: 75..." |
| **Evaluation Rationale** | Why each rating was assigned | Narrative explanation |

---

## Benchmark Availability by Standard

### EC - Economics and Social Science Services `[JES-EC]`

**Source:** [EC Job Evaluation Standard](https://www.canada.ca/en/treasury-board-secretariat/services/collective-agreements/job-evaluation/economics-social-science-services-job-evaluation-standard.html)

- **19 benchmark positions** (BM 1-19)
- Covers EC-01 through EC-08
- Scored across all 9 factors
- Example: BM at 220 points → EC-03

**Status:** ✓ Publicly available, scrapeable

---

### EX - Executive Group `[JES-EX]`

**Source:** [Executive Group Position Evaluation Plan 2022](https://www.canada.ca/en/treasury-board-secretariat/services/collective-agreements/job-evaluation/executive-group-position-evaluation-plan-2022.html)

**Benchmark Pages:**
- [EX-01 Benchmarks (1-26)](https://www.canada.ca/en/treasury-board-secretariat/services/collective-agreements/job-evaluation/executive-group-position-evaluation-plan-2022/app-c-benchmark-positions-ex-01.html)
- [EX-02 Benchmarks (27-40)](https://www.canada.ca/en/treasury-board-secretariat/services/collective-agreements/job-evaluation/executive-group-position-evaluation-plan-2022/app-c-benchmark-positions-ex-02.html)
- [EX-03 Benchmarks (41-48)](https://www.canada.ca/en/treasury-board-secretariat/services/collective-agreements/job-evaluation/executive-group-position-evaluation-plan-2022/app-c-benchmark-positions-ex-03.html)
- [EX-04 Benchmarks (49-60)](https://www.canada.ca/en/treasury-board-secretariat/services/collective-agreements/job-evaluation/executive-group-position-evaluation-plan-2022/app-c-benchmark-positions-ex-04.html)
- [EX-05 Benchmarks (61-72)](https://www.canada.ca/en/treasury-board-secretariat/services/collective-agreements/job-evaluation/executive-group-position-evaluation-plan-2022/app-c-benchmark-positions-ex-05.html)

- **72 benchmark positions** total
- Uses Hay methodology (Know-How, Problem Solving, Accountability)
- Point totals + profile designations

**Status:** ✓ Publicly available, scrapeable

---

### IT - Information Technology `[JES-IT]`

**Source:** [IT Job Evaluation Standard](https://www.canada.ca/en/treasury-board-secretariat/services/collective-agreements/job-evaluation/information-technology-job-evaluation-standard.html)

- Benchmarks integrated with factor descriptions
- 5 levels (IT-01 through IT-05)
- References within degree descriptors

**Status:** ✓ Publicly available, embedded in standard

---

### ED - Education `[JES-ED]`

**Source:** [Education Job Evaluation Standard](https://www.canada.ca/en/treasury-board-secretariat/services/collective-agreements/job-evaluation/education-job-evaluation-standard.html)

- Point rating plan with benchmark position descriptions
- Covers ED-EDS sub-group

**Status:** ✓ Publicly available

---

### Other Standards

| Standard | Benchmark Availability | Notes |
|----------|----------------------|-------|
| CT - Comptrollership | Likely embedded | 2023 standard |
| FB - Border Services | Likely embedded | 2005 standard |
| FS - Foreign Service | Likely embedded | 2005 standard |
| LC - Law Management | Likely embedded | 2017 standard |
| LP - Law Practitioner | Likely embedded | 2017 standard |
| NU - Nursing | Likely embedded | 2017 standard |
| PS - Psychology | Likely embedded | 2017 standard |
| SW - Social Work | Likely embedded | 2017 standard |

**Note:** Some detailed benchmarks may be on GCpedia (internal) rather than public canada.ca

---

## Benchmark Scoring Methodologies

### Point-Rating Method (EC, ED, most groups)

```
Total Points = Σ (Factor Degree Points)

Example (EC):
- Decision Making (Degree 5): 90 points
- Leadership (Degree 3): 50 points
- Communication (Degree 4): 75 points
- ... (6 more factors)
- Total: 420 points → EC-05
```

### Hay Method (EX group)

```
Total Points = Know-How + Problem Solving + Accountability

Example (EX):
- Know-How: F.III.2 = 460 points
- Problem Solving: E+.4 (50%) = 230 points
- Accountability: E+.2P = 230 points
- Total: 920 points → EX-01
```

---

## Data Extraction Strategy

### For v5.0 Implementation

**Option A: Scrape from canada.ca** (Recommended for public standards)
- Parse HTML tables from standard documents
- Extract benchmark position data
- Store in `dim_benchmark_position` table

**Option B: Request from TBS** (For internal/GCpedia benchmarks)
- Some detailed benchmarks may not be publicly posted
- Client may have access via GCpedia/GCxchange

**Option C: Manual data entry** (Fallback)
- If parsing is complex, manual entry of key benchmarks
- Focus on most common groups (EC, CS/IT, PM)

---

## Recommended Scrape Targets

| Priority | Standard | URL | Benchmark Count |
|----------|----------|-----|-----------------|
| 1 | EC | economics-social-science-services-job-evaluation-standard.html | 19 |
| 2 | EX | executive-group-position-evaluation-plan-2022/app-c-* | 72 |
| 3 | IT | information-technology-job-evaluation-standard.html | ~15 |
| 4 | ED | education-job-evaluation-standard.html | TBD |

---

## Schema for Benchmark Storage

```sql
CREATE TABLE dim_benchmark_position (
    id INTEGER PRIMARY KEY,
    standard_code TEXT NOT NULL,        -- 'EC', 'EX', 'IT'
    benchmark_number INTEGER NOT NULL,  -- BM 1, BM 2, etc.
    position_title TEXT NOT NULL,
    level_code TEXT NOT NULL,           -- 'EC-03', 'EX-01'
    total_points INTEGER NOT NULL,
    factor_scores TEXT NOT NULL,        -- JSON: {"DM": 5, "LO": 3, ...}
    point_breakdown TEXT NOT NULL,      -- JSON: {"DM": 90, "LO": 50, ...}
    principal_duties TEXT,              -- Summary of duties
    organization_context TEXT,          -- Org setting description
    evaluation_rationale TEXT,          -- Why ratings assigned
    source_url TEXT NOT NULL,
    scraped_at TEXT NOT NULL,
    FOREIGN KEY (standard_code) REFERENCES dim_job_eval_standard(standard_code)
);
```

---

## Conclusion

**Benchmarks are available** - they're embedded in the public Job Evaluation Standards on canada.ca. No need to wait for client data for this item.

**Recommendation:** Add a scraping phase to v5.0 that extracts benchmark positions from the public standards, starting with EC and EX which have the most comprehensive public documentation.

---

## Sources

- [Job Evaluation Standards Overview](https://www.canada.ca/en/treasury-board-secretariat/services/collective-agreements/job-evaluation/job-evaluation-standards-public-service-employees.html)
- [EC Group Standard](https://www.canada.ca/en/treasury-board-secretariat/services/collective-agreements/job-evaluation/economics-social-science-services-job-evaluation-standard.html)
- [EX Group Standard 2022](https://www.canada.ca/en/treasury-board-secretariat/services/collective-agreements/job-evaluation/executive-group-position-evaluation-plan-2022.html)
- [IT Group Standard](https://www.canada.ca/en/treasury-board-secretariat/services/collective-agreements/job-evaluation/information-technology-job-evaluation-standard.html)

---

*Research completed: 2026-02-04*
*Policy provenance: `[JES]`, `[GUIDE-S2.P3]`*
