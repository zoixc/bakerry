from pydantic import BaseModel
from typing import List, Optional
from pathlib import Path
import json
import os

BACKUP_STATUS_FILE = "/data/backup_status.json"

class VPSConfig(BaseModel):
    name: str
    host: str
    port: int = 22
    username: str
    password: Optional[str] = None
    private_key: Optional[str] = None  # путь к приватному ключу
    schedule: str  # cron-выражение
    max_backups: int = 2

class BackupStatus(BaseModel):
    name: str
    last_backup: Optional[str] = None
    status: str = "pending"

    @staticmethod
    def load_all() -> List["BackupStatus"]:
        if not Path(BACKUP_STATUS_FILE).exists():
            return []
        with open(BACKUP_STATUS_FILE, "r") as f:
            data = json.load(f)
        return [BackupStatus(**item) for item in data]

    @staticmethod
    def save_all(statuses: List["BackupStatus"]):
        os.makedirs(Path(BACKUP_STATUS_FILE).parent, exist_ok=True)
        with open(BACKUP_STATUS_FILE, "w") as f:
            json.dump([s.dict() for s in statuses], f, indent=2)

    @staticmethod
    def update(name: str, last_backup: str, status: str):
        statuses = BackupStatus.load_all()
        found = False
        for s in statuses:
            if s.name == name:
                s.last_backup = last_backup
                s.status = status
                found = True
        if not found:
            statuses.append(BackupStatus(name=name, last_backup=last_backup, status=status))
        BackupStatus.save_all(statuses)
