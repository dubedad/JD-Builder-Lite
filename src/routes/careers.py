"""Careers site routes — DND Civilian Careers browser (employee surface).

L1/L2: driven by JobForge gold parquet files via CareersParquetReader.
L3:    parquet for structure + careers.sqlite for enriched content
       (overview, training, entry_plans) until those fields are promoted
       into the JobForge gold layer (Step 5).
"""

import json
import logging
import os
import sqlite3

from flask import Blueprint, render_template, abort

from src.services.careers_parquet_reader import careers_parquet_reader

logger = logging.getLogger(__name__)

careers_bp = Blueprint('careers', __name__, url_prefix='/careers')

# careers.sqlite is kept for L3 enriched content only.
_DB_PATH = os.path.join(
    os.path.dirname(__file__), '..', '..', 'ps_careers_site', 'careers.sqlite'
)


def _get_db():
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _enrichment_for_slug(title_slug: str) -> dict:
    """Fetch LLM-enriched fields from careers.sqlite by title slug."""
    try:
        conn = _get_db()
        row = conn.execute(
            """
            SELECT overview, training, entry_plans, part_time,
                   related_careers, digital
            FROM careers
            WHERE job_title_slug = ?
            """,
            (title_slug,)
        ).fetchone()
        conn.close()
    except Exception as e:
        logger.warning("careers.sqlite lookup failed for %s: %s", title_slug, e)
        return {}

    if not row:
        return {}

    try:
        related_raw = json.loads(row["related_careers"] or "[]")
    except (json.JSONDecodeError, TypeError):
        related_raw = []

    return {
        "overview":    row["overview"] or "",
        "training":    row["training"] or "",
        "entry_plans": row["entry_plans"] or "",
        "part_time":   row["part_time"] or "",
        "digital":     row["digital"],
        "related_raw": related_raw,
    }


@careers_bp.route('/')
def browse_careers():
    try:
        families = careers_parquet_reader.get_families()
        job_functions = careers_parquet_reader.get_job_functions()
        titles_by_slug = careers_parquet_reader.get_titles_by_family_slug()

        for fam in families:
            fam["titles_json"] = json.dumps(titles_by_slug.get(fam["slug"], []))

        return render_template(
            'careers/careers.html',
            families=families,
            job_functions=job_functions
        )
    except Exception as e:
        import traceback
        logger.error("browse_careers error: %s\n%s", e, traceback.format_exc())
        raise


@careers_bp.route('/<family_slug>')
def job_family(family_slug):
    family_name, jobs = careers_parquet_reader.get_jobs_for_family(family_slug)

    if not family_name:
        abort(404)

    return render_template(
        'careers/family.html',
        family=family_name,
        family_slug=family_slug,
        jobs=jobs
    )


@careers_bp.route('/career/<title_slug>')
def career_detail(title_slug):
    job = careers_parquet_reader.get_job_by_title_slug(title_slug)

    if not job:
        abort(404)

    # Overlay enriched content from careers.sqlite
    enrichment = _enrichment_for_slug(title_slug)
    job.update(enrichment)

    return render_template('careers/career_detail.html', job=job)
