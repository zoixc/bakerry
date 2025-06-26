from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from .backup import perform_backup
from .models import VPSConfig
import json
from pathlib import Path

CONFIG_FILE = "/data/scheduled_backups.json"
scheduler = BackgroundScheduler()


def add_backup_job(config: VPSConfig):
    trigger = CronTrigger.from_crontab(config.schedule)
    scheduler.add_job(
        func=perform_backup,
        trigger=trigger,
        args=[config],
        id=config.name,
        replace_existing=True
    )
    _store_config(config)


def _store_config(config: VPSConfig):
    configs = load_all_configs()
    configs = [c for c in configs if c.name != config.name]
    configs.append(config)
    Path(CONFIG_FILE).parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump([c.dict() for c in configs], f, indent=2)


def load_all_configs() -> list[VPSConfig]:
    if not Path(CONFIG_FILE).exists():
        return []
    with open(CONFIG_FILE, "r") as f:
        data = json.load(f)
    return [VPSConfig(**d) for d in data]

def remove_backup_job(name: str):
    # Удаление задания из планировщика
    try:
        scheduler.remove_job(job_id=name)
    except Exception as e:
        print(f"[Scheduler] Could not remove job {name}: {e}")

    # Удаление конфигурации
    configs = load_all_configs()
    configs = [c for c in configs if c.name != name]
    with open(CONFIG_FILE, "w") as f:
        json.dump([c.dict() for c in configs], f, indent=2)

# Автоматически загружаем все конфиги и запускаем джобы при старте
for cfg in load_all_configs():
    try:
        add_backup_job(cfg)
    except Exception as e:
        print(f"[Scheduler] Failed to load job for {cfg.name}: {e}")
