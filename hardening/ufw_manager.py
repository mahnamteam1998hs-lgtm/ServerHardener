class UFWManager:

    def __init__(self, ssh_manager):
        self.ssh = ssh_manager

    def is_installed(self) -> bool:

        output, error, exit_code = (
            self.ssh.execute(
                "command -v ufw"
            )
        )

        return exit_code == 0

    def is_enabled(self) -> bool:

        output, error, exit_code = (
            self.ssh.execute(
                "ufw status | head -1"
            )
        )

        if exit_code != 0:
            return False

        return (
            "active"
            in output.lower()
        )

    def install(self):

        output, error, exit_code = (
            self.ssh.execute_sudo(
                "apt-get update"
            )
        )

        if exit_code != 0:

            return (
                output,
                error,
                exit_code,
            )

        return self.ssh.execute_sudo(
            "apt-get install -y ufw"
        )

    def enable(self) -> bool:

        output, error, exit_code = (
            self.ssh.execute_sudo(
                "ufw --force enable"
            )
        )

        if exit_code != 0:

            raise RuntimeError(
                (
                    "Failed to enable UFW: "
                    f"{error}"
                )
            )

        return True

    def disable(self) -> bool:

        output, error, exit_code = (
            self.ssh.execute_sudo(
                "ufw --force disable"
            )
        )

        if exit_code != 0:

            raise RuntimeError(
                (
                    "Failed to disable UFW: "
                    f"{error}"
                )
            )

        return True

    def reset(self) -> bool:

        output, error, exit_code = (
            self.ssh.execute_sudo(
                "ufw --force reset"
            )
        )

        if exit_code != 0:

            raise RuntimeError(
                (
                    "Failed to reset UFW: "
                    f"{error}"
                )
            )

        return True

    def allow_ssh(
        self,
        port: int,
    ) -> bool:

        return self.allow_port(
            port
        )

    def allow_port(
        self,
        port: int,
    ) -> bool:

        output, error, exit_code = (
            self.ssh.execute_sudo(
                f"ufw allow {port}/tcp"
            )
        )

        if exit_code != 0:

            raise RuntimeError(
                (
                    f"Failed to allow port {port}: "
                    f"{error}"
                )
            )

        return True

    def status(self) -> str:

        output, error, exit_code = (
            self.ssh.execute_sudo(
                "ufw status verbose"
            )
        )

        if exit_code != 0:

            raise RuntimeError(
                (
                    "Failed to get UFW status: "
                    f"{error}"
                )
            )

        return output