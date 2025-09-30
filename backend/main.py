from fastapi import FastAPI, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
import os, aiofiles
from datetime import datetime
from typing import Literal
from uuid import uuid4

app = FastAPI()

# CORS so the frontend can call the API from localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", "http://127.0.0.1:5173",
        "http://localhost:3000", "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "/tmp/soccer-uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ---- very simple in-memory "DB" (resets when server restarts) ----
MOCK_DB = {
    "shooting": [],  # list of dicts {video_id, filename, competence, created_at}
    "passing":  []
}

@app.get("/")
def root():
    return {"message": "Soccer Evolved API is running"}

@app.get("/health")
def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat()}

@app.post("/upload")
async def upload(
    file: UploadFile = File(...),
    gesture: Literal["shooting", "passing"] = Query("shooting")
):
    """
    Save upload, return a FAKE score + stubbed errors/tips,
    and append a record to the in-memory DB for the dashboard.
    """
    # 1) save file (demo; later you’ll push to cloud storage)
    video_id = f"vid_{uuid4().hex[:8]}"
    save_path = os.path.join(
        UPLOAD_DIR, f"{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}-{file.filename}"
    )
    async with aiofiles.open(save_path, "wb") as f:
        content = await file.read()
        await f.write(content)

    # 2) fake analysis (placeholder)
    competence = 0.75  # keep it constant for now
    # gesture-specific stubbed feedback (Portuguese as per client)
    if gesture == "shooting":
        errors = ["lean_back"]
        tips = ["Inclina o tronco para a frente", "Segue o movimento do pé após o remate"]
    else:
        errors = ["weak_plant_foot"]
        tips = ["Coloca o pé de apoio ao lado da bola", "Passa com o interior do pé"]

    record = {
        "video_id": video_id,
        "filename": file.filename,
        "gesture": gesture,
        "competence": competence,
        "created_at": datetime.utcnow().isoformat(timespec="seconds"),
    }
    MOCK_DB[gesture].append(record)

    return {
        "video_id": video_id,
        "gesture": gesture,
        "competence": competence,
        "errors": errors,
        "tips": tips,
        "explainer_video_url": "",  # fill later
        "created_at": record["created_at"],
    }

@app.get("/videos")
def list_videos(
    gesture: Literal["shooting", "passing"],
    type: Literal["all", "top"] = "all"
):
    """
    Return recent uploads or Top 5 by competence (for now, all 0.75 so Top 5 ~ latest 5)
    """
    items = list(MOCK_DB.get(gesture, []))
    if type == "top":
        # sort by competence desc, then by created_at desc
        items = sorted(items, key=lambda r: (r.get("competence", 0), r["created_at"]), reverse=True)[:5]
    else:
        # newest first
        items = sorted(items, key=lambda r: r["created_at"], reverse=True)
    return items
