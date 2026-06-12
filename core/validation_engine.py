class ValidationEngine:
    def __init__(self, ssh_manager):

        self.ssh = ssh_manager
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