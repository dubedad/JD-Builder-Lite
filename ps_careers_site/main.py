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

DB_PATH = os.path.join(os.path.dirname(__file__), "careers.sqlite")

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


@app.on_event("startup")
async def startup_event():
    if not os.path.exists(DB_PATH):
        logger.warning("careers.sqlite not found at %s — static-only mode", DB_PATH)
    else:
        logger.info("careers.sqlite found at %s", DB_PATH)


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})


# L1: Function browse — shows 22 Job Function cards
@app.get("/careers")
async def careers_functions(request: Request):
    """Show 22 Job Function cards."""
    conn = get_db()
    try:
        functions = conn.execute("""
            SELECT job_function_slug, job_function, job_function_description, image_path
            FROM job_functions
            ORDER BY job_function
        """).fetchall()
    finally:
        conn.close()
    return templates.TemplateResponse("careers_functions.html", {
        "request": request,
        "functions": functions,
    })


# L2: Family browse within a function
@app.get("/careers/{function_slug}/{family_slug}")
async def careers_titles(request: Request, function_slug: str, family_slug: str):
    """Show Title cards for a specific family."""
    conn = get_db()
    try:
        function = conn.execute(
            "SELECT * FROM job_functions WHERE job_function_slug = ?", (function_slug,)
        ).fetchone()
        if not function:
            raise HTTPException(status_code=404, detail="Job function not found")
        family = conn.execute(
            "SELECT * FROM job_families WHERE job_family_slug = ? AND job_function_slug = ?",
            (family_slug, function_slug)
        ).fetchone()
        if not family:
            raise HTTPException(status_code=404, detail="Job family not found")
        titles = conn.execute("""
            SELECT jt_id, job_title, job_title_slug, job_title_description, image_path
            FROM careers
            WHERE job_family_slug = ?
            ORDER BY job_title
        """, (family_slug,)).fetchall()
    finally:
        conn.close()
    return templates.TemplateResponse("careers_titles.html", {
        "request": request,
        "function": function,
        "family": family,
        "titles": titles,
    })


# L2 (must be declared AFTER /{function_slug}/{family_slug} to avoid shadowing)
@app.get("/careers/{function_slug}")
async def careers_families(request: Request, function_slug: str):
    """Show Family cards for a specific function."""
    conn = get_db()
    try:
        function = conn.execute(
            "SELECT * FROM job_functions WHERE job_function_slug = ?", (function_slug,)
        ).fetchone()
        if not function:
            raise HTTPException(status_code=404, detail="Job function not found")
        families = conn.execute("""
            SELECT job_family_slug, job_family, job_function_slug,
                   job_family_description, image_path
            FROM job_families
            WHERE job_function_slug = ?
            ORDER BY job_family
        """, (function_slug,)).fetchall()
    finally:
        conn.close()
    return templates.TemplateResponse("careers_families.html", {
        "request": request,
        "function": function,
        "families": families,
    })


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
