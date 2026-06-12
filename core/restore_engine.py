class RestoreEngine:

    def __init__(self, ssh_manager):

        self.ssh = ssh_manager

    def restore_ssh(self, backup_path: str):

        output, error, exit_code = (
            self.ssh.execute_sudo(
                f"tar -xzf {backup_path}/ssh.tar.gz -C /"
            )
        )

        if exit_code != 0:
            raise RuntimeError(
                f"SSH restore failed: {error}"
            )

    def restore_users(self, backup_path: str):

        output, error, exit_code = (
            self.ssh.execute_sudo(
                f"tar -xzf {backup_path}/users.tar.gz -C /"
            )
        )

        if exit_code != 0:
            raise RuntimeError(
                f"Users restore failed: {error}"
            )

    def restore_sudoers(self, backup_path: str):

        output, error, exit_code = (
            self.ssh.execute_sudo(
                f"tar -xzf {backup_path}/sudoers.tar.gz -C /"
            )
        )

        if exit_code != 0:
            raise RuntimeError(
                f"Sudoers restore failed: {error}"
            )

    def restore_selected(
            self,
            backup_path: str,
            ssh=False,
            users=False,
            sudoers=False,
    ):

        if ssh:
            self.restore_ssh(
                backup_path
            )

        if users:
            self.restore_users(
                backup_path
            )

        if sudoers:
            self.restore_sudoers(
                backup_path
            )

        return True