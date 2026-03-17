import os
import json
import logging
import sqlite3

import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI(title="DND Civilian Careers")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

DB_PATH = os.path.join(os.path.dirname(__file__), "pipeline", "careers.sqlite")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.on_event("startup")
async def startup_event():
    if not os.path.exists(DB_PATH):
        logger.warning("careers.sqlite not found at %s — static-only mode", DB_PATH)
    else:
        logger.info("careers.sqlite found at %s", DB_PATH)


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})


@app.get("/careers")
async def browse_careers(request: Request):
    conn = get_db()
    try:
        rows = conn.execute(
            """
            SELECT DISTINCT job_family, job_family_slug, job_function, card_image_key
            FROM careers
            WHERE job_family != ''
            ORDER BY job_family ASC
            """
        ).fetchall()
        jf_rows = conn.execute(
            "SELECT DISTINCT job_function FROM careers ORDER BY job_function ASC"
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
            "image_file": row["card_image_key"] or None,
            "titles_json": json.dumps(titles_by_slug.get(row["job_family_slug"], [])),
        })

    return templates.TemplateResponse(
        "careers.html",
        {"request": request, "families": families, "job_functions": job_functions}
    )


@app.get("/careers/{family_slug}")
async def job_family(request: Request, family_slug: str):
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
        raise HTTPException(status_code=404, detail="Job family not found")

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

    return templates.TemplateResponse(
        "family.html",
        {
            "request": request,
            "family": family_name,
            "family_slug": family_slug,
            "jobs": jobs,
        }
    )


@app.get("/career/{title_slug}")
async def career_detail(request: Request, title_slug: str):
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
        raise HTTPException(status_code=404, detail="Career not found")

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

    return templates.TemplateResponse(
        "career_detail.html",
        {"request": request, "job": job}
    )


port = int(os.getenv("PORT", "8000"))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
