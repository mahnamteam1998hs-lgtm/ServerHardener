from hardening.ufw_manager import UFWManager
from hardening.fail2ban_manager import Fail2BanManager


class HardeningManager:

    def __init__(self, ssh_manager, server_info):

        self.ssh = ssh_manager
        self.server_info = server_info

        self.ufw = UFWManager(ssh_manager)

        self.fail2ban = Fail2BanManager(
            ssh_manager
        )

    # -------------------------
    # Firewall
    # -------------------------

    def enable_firewall(
        self,
        extra_ports=None,
    ):

        if extra_ports is None:
            extra_ports = []

        if not self.ufw.is_installed():
            self.ufw.install()

        # Always keep SSH accessible
        self.ufw.allow_ssh(
            self.server_info.ssh_port
        )

        for port in extra_ports:

            self.ufw.allow_port(
                int(port)
            )

        self.ufw.enable()

        self.server_info.firewall_enabled = True

        self.server_info.firewall_configured = True

        status = self.ufw.status()

        self.server_info.firewall_status = (
            status
        )

        return status

    def disable_firewall(
        self,
        remove_rules: bool = False,
    ):

        self.ufw.disable()

        if remove_rules:

            self.ufw.reset()

        self.server_info.firewall_enabled = False

        self.server_info.firewall_configured = True

        self.server_info.firewall_status = (
            "Disabled"
        )

        return "Firewall disabled"

    # -------------------------
    # Fail2Ban
    # -------------------------

    def install_fail2ban(self):

        if not self.fail2ban.is_installed():

            self.fail2ban.install()

        self.server_info.fail2ban_installed = True

        self.server_info.fail2ban_active = False

        return "Fail2Ban installed"

    def enable_fail2ban(self):

        if not self.fail2ban.is_installed():

            self.fail2ban.install()

        self.fail2ban.enable()

        self.fail2ban.start()

        self.server_info.fail2ban_installed = True

        self.server_info.fail2ban_active = True

        return "Fail2Ban enabled"

    def disable_fail2ban(self):

        if self.fail2ban.is_installed():

            self.fail2ban.stop()

            self.fail2ban.disable()

        self.server_info.fail2ban_installed = True

        self.server_info.fail2ban_active = False

        return "Fail2Ban disabled"

    def uninstall_fail2ban(self):

        if self.fail2ban.is_installed():

            self.fail2ban.stop()

            self.fail2ban.disable()

            self.fail2ban.uninstall()

        self.server_info.fail2ban_installed = False

        self.server_info.fail2ban_active = False

        return "Fail2Ban removed"

    def purge_fail2ban(self):

        if self.fail2ban.is_installed():

            self.fail2ban.stop()

            self.fail2ban.disable()

            self.fail2ban.purge()

        self.server_info.fail2ban_installed = False

        self.server_info.fail2ban_active = False

        return "Fail2Ban purged"

    def disable_root_login(self):

        self.ssh.execute_sudo(
            (
                r"sed -i "
                r"'s/^#\?PermitRootLogin.*/PermitRootLogin no/' "
                r"/etc/ssh/sshd_config"
            )
        )

        self.ssh.execute_sudo(
            "sshd -t"
        )

        self.ssh.execute_sudo(
            "systemctl restart ssh"
        )

        output, _, _ = (
            self.ssh.execute_sudo(
                "sshd -T | grep '^permitrootlogin'"
            )
        )

        self.server_info.root_login_enabled = (
            False
        )

        return (
                "permitrootlogin no"
                in output.lower()
        )

    def disable_password_login(self):

        # Main sshd_config
        self.ssh.execute_sudo(
            (
                r"sed -i "
                r"'s/^#\?PasswordAuthentication.*/PasswordAuthentication no/' "
                r"/etc/ssh/sshd_config"
            )
        )

        # Override files (Ubuntu 24 cloud-init etc.)
        self.ssh.execute_sudo(
            (
                r"find /etc/ssh/sshd_config.d "
                r"-type f "
                r"-exec sed -i "
                r"'s/^#\?PasswordAuthentication.*/PasswordAuthentication no/' "
                r"{} \;"
            )
        )

        output, error, exit_code = (
            self.ssh.execute_sudo(
                "sshd -t"
            )
        )

        if exit_code != 0:
            return False

        self.ssh.execute_sudo(
            "systemctl restart ssh"
        )

        output, _, _ = (
            self.ssh.execute_sudo(
                "sshd -T | grep '^passwordauthentication'"
            )
        )

        success = (
                "passwordauthentication no"
                in output.lower()
        )

        if success:
            self.server_info.password_login_enabled = (
                False
            )

        return success