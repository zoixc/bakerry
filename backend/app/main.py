from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .scheduler import scheduler, add_backup_job
from .backup import perform_backup
from .models import VPSConfig, BackupStatus

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def serve_frontend():
    return FileResponse("static/index.html")

@app.get("/{full_path:path}")
def serve_vue_routes(full_path: str):
    return FileResponse("static/index.html")

@app.on_event("startup")
def start_scheduler():
    scheduler.start()

@app.post("/backup")
def manual_backup(config: VPSConfig):
    try:
        return perform_backup(config)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/schedule")
def schedule_backup(config: VPSConfig):
    try:
        add_backup_job(config)
        return {"message": "Backup scheduled"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status")
def get_status():
    return BackupStatus.load_all()
