import os
import datetime
import tarfile
import paramiko
from pathlib import Path
from .models import VPSConfig, BackupStatus

BACKUP_DIR = "/data/backups"

def perform_backup(config: VPSConfig):
    timestamp = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    backup_path = Path(BACKUP_DIR) / config.name / f"{timestamp}.tar.gz"
    os.makedirs(backup_path.parent, exist_ok=True)

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        if config.private_key:
            pkey = paramiko.RSAKey.from_private_key_file(config.private_key)
            ssh.connect(config.host, port=config.port, username=config.username, pkey=pkey)
        else:
            ssh.connect(config.host, port=config.port, username=config.username, password=config.password)

        sftp = ssh.open_sftp()
        remote_tmp = f"/tmp/{config.name}_backup.tar.gz"

        ssh.exec_command(f"tar czpf {remote_tmp} --exclude=/proc --exclude=/sys --exclude=/dev/pts --exclude=/tmp --exclude=/run /")

        with sftp.open(remote_tmp, "rb") as remote_file:
            with open(backup_path, "wb") as local_file:
                local_file.write(remote_file.read())

        ssh.exec_command(f"rm -f {remote_tmp}")
        sftp.close()
        ssh.close()

        _cleanup_old_backups(config)
        BackupStatus.update(config.name, timestamp, "success")
        return {"status": "success", "path": str(backup_path)}

    except Exception as e:
        BackupStatus.update(config.name, timestamp, "failed")
        raise e

def _cleanup_old_backups(config: VPSConfig):
    bdir = Path(BACKUP_DIR) / config.name
    backups = sorted(bdir.glob("*.tar.gz"), reverse=True)
    for old in backups[config.max_backups:]:
        old.unlink()
