from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from app.scheduler import scheduler, add_backup_job, remove_backup_job
from app.backup import perform_backup
from app.models import VPSConfig, BackupStatus

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Serve frontend (index.html) for / and any path
@app.get("/")
def serve_frontend():
    return FileResponse(STATIC_DIR / "index.html")

@app.get("/{full_path:path}")
def serve_routes(full_path: str):
    return FileResponse(STATIC_DIR / "index.html")

# Scheduler
@app.on_event("startup")
def start_scheduler():
    scheduler.start()

@app.post("/backup")
def manual_backup(config: VPSConfig):
    try:
        result = perform_backup(config)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/schedule")
def schedule_backup(config: VPSConfig):
    try:
        add_backup_job(config)
        return {"message": "Backup scheduled"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/schedule/{name}")
def delete_schedule(name: str):
    try:
        remove_backup_job(name)
        return {"message": f"Schedule for '{name}' removed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status")
def get_status():
    return BackupStatus.load_all()
