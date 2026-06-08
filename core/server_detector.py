from models.server_info import ServerInfo


class ServerDetector:

    def __init__(self, ssh_manager):
        self.ssh = ssh_manager

    def detect(self) -> ServerInfo:

        info = ServerInfo()

        # Hostname

        hostname, _, _ = self.ssh.execute(
            "hostname"
        )

        info.hostname = hostname.strip()

        # Ubuntu version

        ubuntu_version, _, _ = self.ssh.execute(
            "lsb_release -ds 2>/dev/null || cat /etc/os-release | grep PRETTY_NAME"
        )

        info.ubuntu_version = (
            ubuntu_version.strip()
        )

        # Current user

        current_user, _, _ = self.ssh.execute(
            "whoami"
        )

        info.current_user = (
            current_user.strip()
        )

        # SSH port

        ssh_port, _, _ = (
            self.ssh.execute_sudo(
                r"sshd -T 2>/dev/null | grep '^port ' | awk '{print $2}'"
            )
        )

        if ssh_port.isdigit():

            info.ssh_port = int(
                ssh_port
            )

        # SSH service

        ssh_service, _, _ = (
            self.ssh.execute(
                "systemctl is-active ssh"
            )
        )

        info.ssh_service_active = (
            ssh_service.strip()
            == "active"
        )

        # Root login

        root_login, _, _ = (
            self.ssh.execute_sudo(
                "sshd -T | grep '^permitrootlogin'"
            )
        )

        password_login, _, _ = (
            self.ssh.execute_sudo(
                "sshd -T | grep '^passwordauthentication'"
            )
        )

        info.root_login_enabled = (
            "yes"
            in root_login.lower()
        )

        info.password_login_enabled = (
            "yes"
            in password_login.lower()
        )

        # Firewall

        ufw_status, _, _ = (
            self.ssh.execute_sudo(
                "ufw status | head -1"
            )
        )

        info.firewall_enabled = (
            ufw_status.strip().lower()
            == "status: active"
        )

        info.firewall_configured = False

        info.firewall_status = ""

        # Fail2Ban

        fail2ban_active, _, _ = (
            self.ssh.execute(
                "systemctl is-active fail2ban"
            )
        )

        _, _, exit_code = (
            self.ssh.execute(
                "systemctl status fail2ban --no-pager"
            )
        )

        info.fail2ban_installed = (
                exit_code == 0
        )

        info.fail2ban_active = (
                fail2ban_active.strip()
                == "active"
        )

        # SSH Key

        info.ssh_key_enabled = False

        info.ssh_key_verified = False

        # Backup

        info.backup_path = ""

        info.backup_created = False

        info.backup_verified = False

        return info