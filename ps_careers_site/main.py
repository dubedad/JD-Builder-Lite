import os
import logging

import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="DND Civilian Careers")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.on_event("startup")
async def startup_event():
    db_path = "pipeline/careers.sqlite"
    if not os.path.exists(db_path):
        logger.warning("careers.sqlite not found at %s — static-only mode", db_path)
    else:
        logger.info("careers.sqlite found at %s", db_path)


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})


port = int(os.getenv("PORT", "8000"))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
