import argparse
import json
import re
import sqlite3
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import anthropic

_HERE = Path(__file__).parent.parent  # ps_careers_site/
DEFAULT_DB = _HERE / "careers.sqlite"
DEFAULT_MODEL = "claude-haiku-4-5-20251001"
DEFAULT_WORKERS = 5
MAX_RETRIES = 3
RETRY_BASE_SECONDS = 2

ENRICHMENT_PROMPT = """\
You are a Government of Canada HR specialist writing career content \
for the DND Civilian Workforce careers website.

Given this job title from the TBS Job Architecture:
- Job Title: {job_title}
- Job Family: {job_family}
- Job Function: {job_function}
- NOC 2021: {noc_2021_title}
- Managerial Level: {managerial_level}

Generate content for each section following the exact structure used \
on the CAF Careers site (forces.ca). Write in plain, professional \
Government of Canada tone.

Return a JSON object (no markdown, no code fences) with exactly these keys:
- overview: 2-3 paragraphs covering role description, responsibilities, and work environment
- training: Education requirements, certifications, professional development opportunities
- entry_plans: How someone enters this career in the federal Public Service (competitions, pools, student programs, lateral moves)
- part_time: Part-time, flexible work, and remote options typical for this role
"""


def extract_json(text: str) -> dict:
    """Extract a JSON dict from a string, handling markdown-wrapped JSON."""
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    raise ValueError(f"Cannot extract JSON from response: {text[:200]}")


def enrich_one(client: anthropic.Anthropic, model: str, row: dict) -> dict | None:
    """Call the API for one row and return the 4-field dict, or None on failure."""
    jt_id = row["jt_id"]
    prompt = ENRICHMENT_PROMPT.format(
        job_title=row.get("job_title") or "",
        job_family=row.get("job_family") or "",
        job_function=row.get("job_function") or "",
        noc_2021_title=row.get("noc_2021_title") or "",
        managerial_level=row.get("managerial_level") or "",
    )

    for attempt in range(MAX_RETRIES):
        try:
            response = client.messages.create(
                model=model,
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}],
            )
            text = response.content[0].text
            result = extract_json(text)
            required = ("overview", "training", "entry_plans", "part_time")
            for key in required:
                if not result.get(key) or not str(result[key]).strip():
                    raise ValueError(f"Missing or empty key: {key}")
            return result
        except anthropic.RateLimitError:
            sleep_time = RETRY_BASE_SECONDS * (2 ** attempt)
            time.sleep(sleep_time)
        except (anthropic.APIError, ValueError):
            time.sleep(2)

    print(f"  ERROR: jt_id={jt_id} failed after {MAX_RETRIES} attempts — skipping")
    return None


def main(db_path: Path, model: str, workers: int, limit: int | None) -> None:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    query = (
        "SELECT jt_id, job_title, job_family, job_function, noc_2021_title, managerial_level "
        "FROM careers WHERE content_status = 'empty'"
    )
    if limit:
        query += f" LIMIT {limit}"
    rows = [dict(r) for r in conn.execute(query).fetchall()]
    conn.close()

    if not rows:
        print("Rows to enrich: 0 — nothing to do.")
        return

    print(
        f"Enrichment starting\n"
        f"Model         : {model}\n"
        f"Rows to enrich: {len(rows)}\n"
        f"Workers       : {workers}"
    )

    client = anthropic.Anthropic()
    done = 0
    errors = 0
    start = time.time()

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(enrich_one, client, model, row): row for row in rows}
        for future in as_completed(futures):
            row = futures[future]
            result = future.result()
            if result is None:
                errors += 1
            else:
                wconn = sqlite3.connect(str(db_path), timeout=30)
                wconn.execute(
                    "UPDATE careers SET overview=?, training=?, entry_plans=?, part_time=?, "
                    "content_status='draft', enriched_at=? WHERE jt_id=?",
                    (
                        result["overview"],
                        result["training"],
                        result["entry_plans"],
                        result["part_time"],
                        datetime.now(timezone.utc).isoformat(),
                        row["jt_id"],
                    ),
                )
                wconn.commit()
                wconn.close()
                done += 1
            total_processed = done + errors
            if total_processed % 50 == 0 or total_processed == len(rows):
                print(f"  Progress: {total_processed}/{len(rows)} ({errors} errors)")

    elapsed = time.time() - start

    # Final summary
    sconn = sqlite3.connect(str(db_path))
    total_draft = sconn.execute("SELECT COUNT(*) FROM careers WHERE content_status = 'draft'").fetchone()[0]
    total_empty = sconn.execute("SELECT COUNT(*) FROM careers WHERE content_status = 'empty'").fetchone()[0]
    sconn.close()

    print(
        f"\nEnrichment complete\n"
        f"Enriched       : {done}\n"
        f"Errors skipped : {errors}\n"
        f"Elapsed        : {elapsed:.1f}s\n"
        f"Total draft    : {total_draft}\n"
        f"Total empty    : {total_empty}"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LLM enrichment for careers.sqlite")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS)
    parser.add_argument("--limit", type=int, default=None, help="Enrich only N rows — for testing")
    args = parser.parse_args()
    main(args.db, args.model, args.workers, args.limit)
