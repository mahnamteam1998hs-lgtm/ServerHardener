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

            # Firewall installed

            _, _, exit_code = self.ssh.execute(
                "command -v ufw"
            )

            info.firewall_installed = (
                    exit_code == 0
            )

            # Firewall version

            if info.firewall_installed:
                version_output, _, _ = (
                    self.ssh.execute(
                        "ufw version | head -1"
                    )
                )

                info.firewall_version = (
                    version_output.strip()
                )

            # Firewall rules count

            rules_output, _, _ = (
                self.ssh.execute_sudo(
                    "ufw status numbered"
                )
            )

            info.firewall_rules_count = len(
                [
                    line
                    for line in rules_output.splitlines()
                    if line.strip().startswith("[")
                ]
            )

            info.firewall_configured = (
                    info.firewall_rules_count > 0
            )
            if info.firewall_enabled:
                info.firewall_status = "Active"
            else:
                info.firewall_status = "Inactive"

            # Fail2Ban
            _, _, exit_code = self.ssh.execute(
                "command -v fail2ban-client"
            )

            info.fail2ban_installed = (exit_code == 0)

            if info.fail2ban_installed:
                version_output, _, _ = (
                    self.ssh.execute(
                        "fail2ban-client --version"
                    )
                )

                info.fail2ban_version = (
                    version_output.strip()
                )

                fail2ban_active, _, _ = self.ssh.execute(
                    "systemctl is-active fail2ban"
                )

                info.fail2ban_active = (
                        fail2ban_active.strip() == "active"
                )

                if info.fail2ban_active:

                    jail_output, _, _ = (
                        self.ssh.execute(
                            "fail2ban-client status"
                        )
                    )

                    for line in jail_output.splitlines():

                        if "Jail list:" in line:
                            jail_text = (
                                line.split(
                                    "Jail list:"
                                )[-1]
                            )

                            info.fail2ban_jails = [
                                jail.strip()
                                for jail in jail_text.split(",")
                                if jail.strip()
                            ]

                            break



            # SSH Key
            pubkey_output, _, exit_code = (
                self.ssh.execute_sudo(
                    "sshd -T | grep '^pubkeyauthentication'"
                )
            )

            if exit_code == 0:
                info.ssh_key_enabled = (
                        "yes"
                        in pubkey_output.lower()
                )
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