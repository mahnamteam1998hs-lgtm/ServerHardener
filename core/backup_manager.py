from config.settings import BACKUP_BASE_PATH


class BackupManager:

    def __init__(self, ssh_manager):
        self.ssh = ssh_manager

    def create_backup(self):

        # ساخت پوشه اصلی بکاپ
        output, error, exit_code = self.ssh.execute_sudo(
            f"mkdir -p {BACKUP_BASE_PATH}"
        )

        if exit_code != 0:
            raise RuntimeError(
                f"Failed creating backup base path: {error}"
            )

        # تولید timestamp
        timestamp, error, exit_code = self.ssh.execute(
            "date +%F_%H-%M-%S"
        )

        if exit_code != 0:
            raise RuntimeError(
                f"Failed generating timestamp: {error}"
            )

        backup_path = (
            f"{BACKUP_BASE_PATH}/{timestamp.strip()}"
        )

        # ساخت پوشه بکاپ
        output, error, exit_code = self.ssh.execute_sudo(
            f"mkdir -p {backup_path}"
        )

        if exit_code != 0:
            raise RuntimeError(
                f"Failed creating backup directory: {error}"
            )

        # بکاپ SSH
        output, error, exit_code = self.ssh.execute_sudo(
            f"tar -czf {backup_path}/ssh.tar.gz /etc/ssh"
        )

        if exit_code != 0:
            raise RuntimeError(
                f"SSH backup failed: {error}"
            )

        # بکاپ کاربران
        output, error, exit_code = self.ssh.execute_sudo(
            f"tar -czf {backup_path}/users.tar.gz "
            f"/etc/passwd /etc/group /etc/shadow"
        )

        if exit_code != 0:
            raise RuntimeError(
                f"Users backup failed: {error}"
            )

        # بکاپ sudoers
        output, error, exit_code = self.ssh.execute_sudo(
            f"tar -czf {backup_path}/sudoers.tar.gz "
            f"/etc/sudoers /etc/sudoers.d"
        )

        if exit_code != 0:
            raise RuntimeError(
                f"Sudoers backup failed: {error}"
            )

        return backup_path

    def verify_backup(self, backup_path):

        required_files = [
            "ssh.tar.gz",
            "users.tar.gz",
            "sudoers.tar.gz",
        ]

        for file_name in required_files:

            output, error, exit_code = (
                self.ssh.execute_sudo(
                    f"test -f {backup_path}/{file_name}"
                )
            )

            if exit_code != 0:
                return False

        return True