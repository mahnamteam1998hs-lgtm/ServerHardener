class RestoreManager:

    def __init__(self, ssh_manager, backup_manager):
        self.ssh = ssh_manager
        self.backup_manager = backup_manager

    def create_safety_snapshot(self):
        return self.backup_manager.create_backup()

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

    def restore_backup(self, backup_path: str):

        self.restore_selected(
            backup_path,
            ssh=True,
            users=True,
            sudoers=True,
        )

        return True

    def full_restore(
            self,
            backup_path: str,
            ssh=True,
            users=True,
            sudoers=True,
    ):

        snapshot = self.backup_manager.create_backup()

        try:

            self.restore_selected(
                backup_path,
                ssh=ssh,
                users=users,
                sudoers=sudoers,
            )

            verify = self.verify_selected(
                ssh=ssh,
                users=users,
                sudoers=sudoers,
            )

            if not all(verify.values()):
                raise RuntimeError(
                    f"Verify failed: {verify}"
                )

            return {
                "status": "success",
                "verify": verify,
                "snapshot": snapshot,
            }

        except Exception as e:

            self.restore_selected(
                snapshot,
                ssh=ssh,
                users=users,
                sudoers=sudoers,
            )

            return {
                "status": "rolled_back",
                "error": str(e),
                "snapshot": snapshot,
            }

    def verify_restore(self) -> dict:

        results = {
            "ssh_config": False,
            "users": False,
            "sudoers": False,
            "ssh_service": False,
        }

        print("\n===== VERIFY RESTORE =====")

        # -------------------------------------------------
        # 1. SSH CONFIG
        # -------------------------------------------------

        output, error, exit_code = self.ssh.execute_sudo(
            "sshd -t"
        )

        print("\n[SSH CONFIG]")
        print("exit_code =", exit_code)
        print("output =", repr(output))
        print("error =", repr(error))

        results["ssh_config"] = (
            exit_code == 0
        )

        # -------------------------------------------------
        # 2. USERS
        # -------------------------------------------------

        output, error, exit_code = self.ssh.execute(
            "cat /etc/passwd"
        )

        print("\n[USERS]")
        print("exit_code =", exit_code)

        results["users"] = (
            "root:" in output
        )

        # -------------------------------------------------
        # 3. SUDOERS
        # -------------------------------------------------

        output, error, exit_code = self.ssh.execute_sudo(
            "visudo -c"
        )

        print("\n[SUDOERS]")
        print("exit_code =", exit_code)
        print("output =", repr(output))
        print("error =", repr(error))

        results["sudoers"] = (
            exit_code == 0
        )

        # -------------------------------------------------
        # 4. SSH SERVICE
        # -------------------------------------------------

        output, error, exit_code = self.ssh.execute_sudo(
            "systemctl is-active ssh"
        )

        print("\n[SSH SERVICE]")
        print("exit_code =", exit_code)
        print("output =", repr(output))
        print("error =", repr(error))

        results["ssh_service"] = (
                output.lower().splitlines()[-1].strip() == "active"
        )

        print("\n[VERIFY RESULTS]")
        print(results)

        return results

    def verify_selected(
            self,
            ssh=False,
            users=False,
            sudoers=False,
    ):

        full_results = self.verify_restore()

        selected_results = {}

        if ssh:
            selected_results["ssh_config"] = (
                full_results["ssh_config"]
            )

            selected_results["ssh_service"] = (
                full_results["ssh_service"]
            )

        if users:
            selected_results["users"] = (
                full_results["users"]
            )

        if sudoers:
            selected_results["sudoers"] = (
                full_results["sudoers"]
            )

        return selected_results

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