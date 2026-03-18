"""Careers site routes — DND Civilian Careers browser (employee surface)."""

import os
import json
import sqlite3
import logging

from flask import Blueprint, render_template, abort

logger = logging.getLogger(__name__)

careers_bp = Blueprint('careers', __name__, url_prefix='/careers')

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'ps_careers_site', 'careers.sqlite')

CARD_IMAGE_STATIC = {
    "Artificial Intelligence Strategy & Integration.webp": "ai-strategy-integration.webp",
    "Information and Data Architecture.jpg": "information-data-architecture.jpg",
    "Organizational Design and Classification.jpg": "organizational-design-classification.jpg",
    "administrative support.webp": "administrative-support.webp",
    "data management.webp": "data-management.webp",
    "database administration.png": "database-administration.png",
    "electronic engineering.jpg": "electronic-engineering.jpg",
    "enterprise architecture.png": "enterprise-architecture.png",
    "food services.jpg": "food-services.jpg",
    "innovation and change management.jpg": "innovation-change-management.jpg",
    "nursing.jpg": "nursing.jpg",
    "project management.jpg": "project-management.jpg",
}


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@careers_bp.route('/')
def browse_careers():
    conn = get_db()
    try:
        rows = conn.execute(
            """
            SELECT DISTINCT job_family, job_family_slug, job_function, card_image_key
            FROM careers
            WHERE card_image_key IS NOT NULL AND card_image_key != ''
            ORDER BY job_family ASC
            """
        ).fetchall()
        jf_rows = conn.execute(
            "SELECT DISTINCT job_function FROM careers WHERE job_function != '' ORDER BY job_function ASC"
        ).fetchall()
        title_rows = conn.execute(
            """
            SELECT job_family_slug, GROUP_CONCAT(lower(job_title), '|||') as titles
            FROM careers
            GROUP BY job_family_slug
            """
        ).fetchall()
    finally:
        conn.close()

    job_functions = [r["job_function"] for r in jf_rows]
    titles_by_slug = {
        r["job_family_slug"]: r["titles"].split("|||")
        for r in title_rows
        if r["titles"]
    }

    families = []
    for row in rows:
        families.append({
            "name": row["job_family"],
            "slug": row["job_family_slug"],
            "function": row["job_function"],
            "image_file": CARD_IMAGE_STATIC.get(row["card_image_key"]),
            "titles_json": json.dumps(titles_by_slug.get(row["job_family_slug"], [])),
        })

    return render_template(
        'careers/careers.html',
        families=families,
        job_functions=job_functions
    )


@careers_bp.route('/<family_slug>')
def job_family(family_slug):
    conn = get_db()
    try:
        rows = conn.execute(
            """
            SELECT jt_id, job_title, job_title_slug, job_family,
                   noc_2021_uid, noc_2021_title, managerial_level, digital, overview
            FROM careers
            WHERE job_family_slug = ?
            ORDER BY job_title ASC
            """,
            (family_slug,)
        ).fetchall()
    finally:
        conn.close()

    if not rows:
        abort(404)

    family_name = rows[0]["job_family"]
    jobs = []
    for row in rows:
        jobs.append({
            "title": row["job_title"],
            "slug": row["job_title_slug"],
            "noc_uid": row["noc_2021_uid"],
            "noc_title": row["noc_2021_title"],
            "managerial_level": row["managerial_level"],
            "digital": row["digital"],
            "excerpt": (row["overview"] or "")[:150],
        })

    return render_template(
        'family.html',
        family=family_name,
        family_slug=family_slug,
        jobs=jobs
    )


@careers_bp.route('/career/<title_slug>')
def career_detail(title_slug):
    conn = get_db()
    try:
        row = conn.execute(
            """
            SELECT jt_id, job_title, job_title_slug, job_family, job_family_slug,
                   job_function, managerial_level, noc_2021_uid, noc_2021_title, digital,
                   overview, training, entry_plans, part_time, related_careers, caf_related
            FROM careers
            WHERE job_title_slug = ?
            """,
            (title_slug,)
        ).fetchone()
    finally:
        conn.close()

    if not row:
        abort(404)

    try:
        caf_slugs = json.loads(row["caf_related"] or "[]")
    except (json.JSONDecodeError, TypeError):
        caf_slugs = []

    try:
        related_raw = json.loads(row["related_careers"] or "[]")
    except (json.JSONDecodeError, TypeError):
        related_raw = []

    job = {
        "title":            row["job_title"],
        "slug":             row["job_title_slug"],
        "family":           row["job_family"],
        "family_slug":      row["job_family_slug"],
        "function":         row["job_function"],
        "managerial_level": row["managerial_level"],
        "noc_uid":          row["noc_2021_uid"],
        "noc_title":        row["noc_2021_title"],
        "digital":          row["digital"],
        "overview":         row["overview"] or "",
        "training":         row["training"] or "",
        "entry_plans":      row["entry_plans"] or "",
        "part_time":        row["part_time"] or "",
        "caf_slugs":        caf_slugs,
        "related_raw":      related_raw,
    }

    return render_template('careers/career_detail.html', job=job)
