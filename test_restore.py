from core.ssh_manager import SSHManager
from core.backup_manager import BackupManager
from core.restore_manager import RestoreManager

# -----------------------------
# SSH Connection Config
# -----------------------------
ssh = SSHManager(
    host="192.168.1.101",
    port=45891,
    username="mahnam4",
    password="987654321",  # فقط برای sudo (در صورت نیاز)
    private_key_path=r"C:\Users\NITRO\.ssh\server_hardener_ed25519",
)

# -----------------------------
# Connect to Server
# -----------------------------
ssh.connect()

# -----------------------------
# Managers
# -----------------------------
backup_manager = BackupManager(ssh)
restore_manager = RestoreManager(ssh, backup_manager)

try:

    # -------------------------
    # 1. Create Backup
    # -------------------------
    backup_path = backup_manager.create_backup()
    print("\nBACKUP CREATED:")
    print(backup_path)

    # -------------------------
    # 2. Transactional Restore
    # -------------------------
    print("\nSTARTING RESTORE...")
    result = restore_manager.full_restore(
        backup_path,
        ssh=True,
        users=False,
        sudoers=False,
    )

    print("\nRESTORE RESULT:")
    print(result)

    # -------------------------
    # 3. Verify Restore
    # -------------------------
    print("\nVERIFYING RESTORE...")
    verify_result = restore_manager.verify_restore()

    print("VERIFY RESULT:", verify_result)

finally:

    # همیشه اتصال بسته شود حتی اگر خطا رخ دهد
    ssh.disconnect()