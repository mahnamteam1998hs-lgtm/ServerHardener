from core.ssh_manager import SSHManager
from core.backup_manager import BackupManager

ssh = SSHManager(
    host="192.168.1.101",
    port=45891,
    username="tester",
    password="123456789"
)

ssh.connect()

backup = BackupManager(ssh)

backup_path = backup.create_backup()

print("BACKUP PATH:", repr(backup_path))

print(
    backup.verify_backup(backup_path)
)

ssh.disconnect()