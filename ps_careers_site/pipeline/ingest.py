"""
TBS Ingest: Read Job_Architecture_TBS.xlsx → careers.sqlite

Usage (from ps_careers_site/ directory):
    python pipeline/ingest.py
    python pipeline/ingest.py --xlsx "Job Architecture_TBS.xlsx" --db careers.sqlite
"""

import argparse
import re
import sqlite3
from collections import Counter
from pathlib import Path

import openpyxl

# ---------------------------------------------------------------------------
# Paths (relative to ps_careers_site/ which is the script's parent dir)
# ---------------------------------------------------------------------------
_HERE = Path(__file__).parent.parent  # ps_careers_site/
DEFAULT_XLSX = _HERE / "Job Architecture_TBS.xlsx"
DEFAULT_DB = _HERE / "careers.sqlite"

# ---------------------------------------------------------------------------
# Card image mapping — 12 MVP job families
# ---------------------------------------------------------------------------
CARD_IMAGE_MAP = {
    "Administrative Support": "administrative support.webp",
    "Artificial Intelligence (AI) Strategy & Integration": "Artificial Intelligence Strategy & Integration.webp",
    "Organization and Classification": "Organizational Design and Classification.jpg",
    "Information and Data Architecture": "Information and Data Architecture.jpg",
    "Data Management": "data management.webp",
    "Enterprise Architecture": "enterprise architecture.png",
    "Innovation and Change Management": "innovation and change management.jpg",
    "Project Management": "project management.jpg",
    "Database and Database Administration": "database administration.png",
    "Electrical": "electronic engineering.jpg",
    "Food Services": "food services.jpg",
    "Nursing": "nursing.jpg",
}

# ---------------------------------------------------------------------------
# Schema DDL
# ---------------------------------------------------------------------------
DDL = """
CREATE TABLE IF NOT EXISTS careers (
    jt_id            INTEGER PRIMARY KEY,
    job_title        TEXT NOT NULL,
    titre_de_poste   TEXT,
    job_function     TEXT NOT NULL,
    job_family       TEXT NOT NULL,
    managerial_level TEXT,
    noc_2021_uid     TEXT,
    noc_2021_title   TEXT,
    digital          TEXT,
    digital_category TEXT,
    job_title_slug   TEXT,
    job_family_slug  TEXT,
    card_image_key   TEXT,
    overview         TEXT,
    training         TEXT,
    entry_plans      TEXT,
    part_time        TEXT,
    related_careers  TEXT,
    caf_related      TEXT,
    content_status   TEXT DEFAULT 'empty',
    enriched_at      TIMESTAMP
);
"""

UPSERT_SQL = """
INSERT INTO careers (
    jt_id, job_title, titre_de_poste, job_function, job_family,
    managerial_level, noc_2021_uid, noc_2021_title, digital, digital_category,
    job_title_slug, job_family_slug, card_image_key, content_status
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'empty')
ON CONFLICT(jt_id) DO UPDATE SET
    job_title        = excluded.job_title,
    titre_de_poste   = excluded.titre_de_poste,
    job_function     = excluded.job_function,
    job_family       = excluded.job_family,
    managerial_level = excluded.managerial_level,
    noc_2021_uid     = excluded.noc_2021_uid,
    noc_2021_title   = excluded.noc_2021_title,
    digital          = excluded.digital,
    digital_category = excluded.digital_category,
    job_title_slug   = excluded.job_title_slug,
    job_family_slug  = excluded.job_family_slug,
    card_image_key   = excluded.card_image_key
    -- overview, training, entry_plans, part_time, caf_related,
    -- content_status, enriched_at intentionally NOT updated
"""


# ---------------------------------------------------------------------------
# Slug utility
# ---------------------------------------------------------------------------
def make_slug(text: str, suffix: str = "") -> str:
    s = text.lower()
    s = s.replace("&", "and")
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"[\s]+", "-", s.strip())
    s = s.strip("-")
    if suffix:
        s = f"{s}-{suffix}"
    return s


# ---------------------------------------------------------------------------
# Schema creation
# ---------------------------------------------------------------------------
def create_schema(conn: sqlite3.Connection) -> None:
    conn.execute(DDL)
    conn.commit()


# ---------------------------------------------------------------------------
# Ingest
# ---------------------------------------------------------------------------
def ingest(xlsx_path: Path, db_path: Path) -> None:
    # Require SQLite UPSERT support (3.24+)
    sqlite_version = tuple(int(x) for x in sqlite3.sqlite_version.split("."))
    if sqlite_version < (3, 24):
        raise RuntimeError(
            f"SQLite >= 3.24 required for UPSERT; found {sqlite3.sqlite_version}"
        )

    print(f"Source : {xlsx_path}")
    print(f"Output : {db_path}")

    # Open workbook
    wb = openpyxl.load_workbook(xlsx_path, read_only=True, data_only=True)
    ws = wb["DRAFT_JA_EN-FR"]

    rows = list(ws.iter_rows(values_only=True))
    wb.close()

    # Build header index (normalize keys)
    raw_header = rows[0]
    header = {}
    for i, h in enumerate(raw_header):
        if h is not None:
            normalized = str(h).strip().lower().replace(" ", "_")
            header[normalized] = i

    def col(row, name):
        idx = header.get(name)
        if idx is None:
            return None
        v = row[idx]
        return str(v).strip() if v is not None else None

    # First pass: collect (jt_id, job_title, job_family) for slug collision detection
    data_rows = rows[1:]
    records = []
    for row in data_rows:
        raw_id = col(row, "jt_id")
        if raw_id is None:
            continue
        try:
            jt_id = int(float(raw_id))
        except (ValueError, TypeError):
            print(f"  WARNING: Skipping row with non-integer JT_ID: {raw_id!r}")
            continue
        job_title = col(row, "job_title") or ""
        job_family = col(row, "job_family") or ""
        records.append((jt_id, job_title, job_family, row))

    # Build slug collision map per family
    # family -> base_slug -> list of jt_ids
    family_slug_index: dict[str, dict[str, list[int]]] = {}
    for jt_id, job_title, job_family, _ in records:
        base = make_slug(job_title)
        fam_map = family_slug_index.setdefault(job_family, {})
        fam_map.setdefault(base, []).append(jt_id)

    collision_count = 0

    conn = sqlite3.connect(db_path)
    try:
        create_schema(conn)

        inserted = 0
        for jt_id, job_title, job_family, row in records:
            titre_de_poste = col(row, "titre_de_poste")
            job_function = col(row, "job_function") or ""
            managerial_level = col(row, "managerial_level")

            # NOC UID — keep as string (may be "12345" or None)
            raw_noc = col(row, "2021_noc_uid")
            noc_2021_uid = str(int(float(raw_noc))) if raw_noc else None

            noc_2021_title = col(row, "2021_noc_title")
            digital = col(row, "digital")
            digital_category = col(row, "digital_category")

            # Slug with collision handling
            base_slug = make_slug(job_title)
            fam_map = family_slug_index.get(job_family, {})
            if len(fam_map.get(base_slug, [])) > 1:
                job_title_slug = make_slug(job_title, suffix=str(jt_id))
                print(
                    f'  COLLISION: "{job_title}" -> "{job_title_slug}" (jt_id={jt_id})'
                )
                collision_count += 1
            else:
                job_title_slug = base_slug

            job_family_slug = make_slug(job_family)
            card_image_key = CARD_IMAGE_MAP.get(job_family)

            conn.execute(
                UPSERT_SQL,
                (
                    jt_id,
                    job_title,
                    titre_de_poste,
                    job_function,
                    job_family,
                    managerial_level,
                    noc_2021_uid,
                    noc_2021_title,
                    digital,
                    digital_category,
                    job_title_slug,
                    job_family_slug,
                    card_image_key,
                ),
            )
            inserted += 1

        conn.commit()

        row_count = conn.execute("SELECT COUNT(*) FROM careers").fetchone()[0]
        unique_families = conn.execute(
            "SELECT COUNT(DISTINCT job_family) FROM careers"
        ).fetchone()[0]
        unique_functions = conn.execute(
            "SELECT COUNT(DISTINCT job_function) FROM careers"
        ).fetchone()[0]

        print("\nIngest complete")
        print(f"Rows inserted/updated : {inserted}")
        print(f"Unique job families   : {unique_families}")
        print(f"Unique job functions  : {unique_functions}")
        print(f"Slug collisions fixed : {collision_count}")

        if row_count != 1989:
            print(f"WARNING: Expected 1989 rows, got {row_count}")
        else:
            print(f"Row count {row_count} matches expected 1989")

    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest TBS Job Architecture xlsx")
    parser.add_argument("--xlsx", type=Path, default=DEFAULT_XLSX)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    args = parser.parse_args()

    ingest(args.xlsx, args.db)
