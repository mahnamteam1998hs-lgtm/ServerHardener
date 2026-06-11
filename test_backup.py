from core.ssh_manager import SSHManager
from core.backup_manager import BackupManager
from core.restore_manager import RestoreManager

ssh = SSHManager(
    host="192.168.1.101",
    port=45891,
    username="mahnam4",
    password="987654321",
    private_key_path=r"C:\Users\NITRO\.ssh\server_hardener_ed25519",
)

ssh.connect()

backup = BackupManager(ssh)
restore = RestoreManager(ssh)

backup_path = backup.create_backup()

print("BACKUP:", backup_path)

# تست restore
restore.full_restore(backup_path)

ssh.disconnect()