from models.server_info import ServerInfo


class ServerDetector:

    def __init__(self, ssh_manager):
        self.ssh = ssh_manager

    def detect(self) -> ServerInfo:

        info = ServerInfo()

        try:

            # Hostname
            hostname, _, _ = self.ssh.execute(
                "hostname"
            )
            info.hostname = hostname.strip()

            # Ubuntu version
            ubuntu_version, _, _ = self.ssh.execute(
                "lsb_release -ds 2>/dev/null || cat /etc/os-release | grep PRETTY_NAME"
            )
            info.ubuntu_version = ubuntu_version.strip()

            # Current user
            current_user, _, _ = self.ssh.execute(
                "whoami"
            )
            info.current_user = current_user.strip()

            # SSH port (safe fallback)
            ssh_port, _, exit_code = self.ssh.execute_sudo(
                r"sshd -T 2>/dev/null | grep '^port ' | awk '{print $2}'"
            )

            if exit_code == 0 and ssh_port.strip().isdigit():
                info.ssh_port = int(ssh_port.strip())

            # SSH service
            ssh_service, _, _ = self.ssh.execute(
                "systemctl is-active ssh"
            )

            info.ssh_service_active = (
                    ssh_service.strip() == "active"
            )

            # Root login
            root_login, _, exit_code = self.ssh.execute_sudo(
                "sshd -T | grep '^permitrootlogin'"
            )

            if exit_code == 0:
                info.root_login_enabled = "yes" in root_login.lower()
            else:
                info.root_login_enabled = False

            # Password login
            password_login, _, exit_code = self.ssh.execute_sudo(
                "sshd -T | grep '^passwordauthentication'"
            )

            if exit_code == 0:
                info.password_login_enabled = "yes" in password_login.lower()
            else:
                info.password_login_enabled = False

            # Firewall
            ufw_status, _, _ = self.ssh.execute_sudo(
                "ufw status | head -1"
            )

            info.firewall_enabled = (
                    ufw_status.strip().lower() == "status: active"
            )

            info.firewall_configured = False
            info.firewall_status = ""

            # Fail2Ban
            _, _, exit_code = self.ssh.execute(
                "command -v fail2ban-client"
            )

            info.fail2ban_installed = (exit_code == 0)

            fail2ban_active, _, _ = self.ssh.execute(
                "systemctl is-active fail2ban"
            )

            info.fail2ban_active = (
                    fail2ban_active.strip() == "active"
            )

            # SSH Key
            info.ssh_key_enabled = False
            info.ssh_key_verified = False

            # Backup
            info.backup_path = ""
            info.backup_created = False
            info.backup_verified = False

            # Users
            users_output, _, _ = self.ssh.execute(
                r"getent passwd | awk -F: '$7 !~ /(nologin|false)$/ {print $1}'"
            )

            info.users = [
                user.strip()
                for user in users_output.splitlines()
                if user.strip()
            ]

            admin_users_output, _, _ = self.ssh.execute(
                "getent group sudo | cut -d: -f4"
            )

            info.admin_users = [
                user.strip()
                for user in admin_users_output.split(",")
                if user.strip()
            ]

            return info

        except RuntimeError as e:

            # مهم‌ترین تغییر اینجاست
            raise RuntimeError(
                f"Server detection failed: {e}"
            )