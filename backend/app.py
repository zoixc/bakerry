### backend/app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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
