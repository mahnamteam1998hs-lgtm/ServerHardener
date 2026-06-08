class Fail2BanManager:

    def __init__(self, ssh_manager):
        self.ssh = ssh_manager

    def is_installed(self) -> bool:
        output, error, exit_code = self.ssh.execute("command -v fail2ban-client")
        return exit_code == 0

    def is_active(self) -> bool:
        output, error, exit_code = self.ssh.execute("systemctl is-active fail2ban")
        return output.strip() == "active"

    def install(self) -> bool:
        output, error, exit_code = self.ssh.execute_sudo("apt-get update")
        if exit_code != 0:
            raise RuntimeError(f"Fail2Ban update failed: {error}")

        output, error, exit_code = self.ssh.execute_sudo("apt-get install -y fail2ban")
        if exit_code != 0:
            raise RuntimeError(f"Fail2Ban installation failed: {error}")
        return True

    def enable(self) -> bool:
        output, error, exit_code = self.ssh.execute_sudo("systemctl enable fail2ban")
        if exit_code != 0:
            raise RuntimeError(f"Failed enabling Fail2Ban: {error}")
        return True

    def disable(self) -> bool:
        output, error, exit_code = self.ssh.execute_sudo("systemctl disable fail2ban")
        if exit_code != 0:
            raise RuntimeError(f"Failed disabling Fail2Ban: {error}")
        return True

    def start(self) -> bool:
        output, error, exit_code = self.ssh.execute_sudo("systemctl start fail2ban")
        if exit_code != 0:
            raise RuntimeError(f"Failed starting Fail2Ban: {error}")
        return True

    def stop(self) -> bool:
        output, error, exit_code = self.ssh.execute_sudo("systemctl stop fail2ban")
        if exit_code != 0:
            raise RuntimeError(f"Failed stopping Fail2Ban: {error}")
        return True

    def uninstall(self) -> bool:
        output, error, exit_code = self.ssh.execute_sudo("apt-get remove -y fail2ban")
        if exit_code != 0:
            raise RuntimeError(f"Failed uninstalling Fail2Ban: {error}")
        return True

    def status(self) -> str:
        output, error, exit_code = self.ssh.execute_sudo("systemctl status fail2ban")
        if exit_code != 0:
            raise RuntimeError(f"Failed checking Fail2Ban status: {error}")
        return output.strip()