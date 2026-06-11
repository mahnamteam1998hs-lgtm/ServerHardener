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

        archives = {
            "ssh.tar.gz": [
                "etc/ssh",
            ],
            "users.tar.gz": [
                "etc/passwd",
                "etc/group",
                "etc/shadow",
            ],
            "sudoers.tar.gz": [
                "etc/sudoers",
                "etc/sudoers.d",
            ],
        }

        for archive_name, required_entries in (
            archives.items()
        ):

            archive_path = (
                f"{backup_path}/{archive_name}"
            )

            # فایل وجود داشته باشد
            output, error, exit_code = (
                self.ssh.execute_sudo(
                    f"test -f {archive_path}"
                )
            )

            if exit_code != 0:
                return False

            # آرشیو سالم باشد
            output, error, exit_code = (
                self.ssh.execute_sudo(
                    f"tar -tzf {archive_path}"
                )
            )

            if exit_code != 0:
                return False

            archive_contents = output.splitlines()

            # محتویات ضروری وجود داشته باشند
            for entry in required_entries:

                found = any(
                    item == entry
                    or item == f"./{entry}"
                    or item.startswith(f"{entry}/")
                    or item.startswith(f"./{entry}/")
                    for item in archive_contents
                )

                if not found:
                    return False

        return True

    def list_backups(self):

        output, error, exit_code = (
            self.ssh.execute_sudo(
                f"ls -1 {BACKUP_BASE_PATH}"
            )
        )

        if exit_code != 0:
            raise RuntimeError(
                f"Failed listing backups: {error}"
            )

        backups = [
            item.strip()
            for item in output.splitlines()
            if item.strip()
        ]

        backups.sort(reverse=True)

        return backups