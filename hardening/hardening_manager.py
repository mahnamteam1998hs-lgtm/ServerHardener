from hardening.ufw_manager import UFWManager
from hardening.fail2ban_manager import Fail2BanManager
from core.restore_manager import RestoreManager
from core.backup_manager import BackupManager
from core.hardening_engine import (
    HardeningEngine
)


class HardeningManager:

    def __init__(self, ssh_manager, server_info):

        self.ssh = ssh_manager
        self.server_info = server_info

        self.ufw = UFWManager(ssh_manager)

        self.fail2ban = Fail2BanManager(
            ssh_manager
        )

        self.engine = HardeningEngine(
            ssh_manager=ssh_manager,
            server_info=server_info,
            ufw_manager=self.ufw,
            fail2ban_manager=self.fail2ban,
        )

        self.backup_manager = BackupManager(ssh_manager)

        self.restore = RestoreManager(
            ssh_manager,
            self.backup_manager
        )

    # -------------------------
    # Firewall
    # -------------------------

    def enable_firewall(
            self,
            extra_ports=None,
    ):

        return self.engine.enable_firewall(
            extra_ports=extra_ports
        )

    def disable_firewall(
            self,
            remove_rules: bool = False,
    ):

        return self.engine.disable_firewall(
            remove_rules=remove_rules
        )

    # -------------------------
    # Fail2Ban
    # -------------------------

    def install_fail2ban(self):

        return self.engine.install_fail2ban()

    def enable_fail2ban(self):

        return self.engine.enable_fail2ban()

    def disable_fail2ban(self):

        return self.engine.disable_fail2ban()

    def uninstall_fail2ban(self):

        return self.engine.uninstall_fail2ban()

    def purge_fail2ban(self):

        return self.engine.purge_fail2ban()

    def disable_root_login(self):
        return self.engine.disable_root_login()

    def disable_password_login(self):
        return self.engine.disable_password_login()

    # -------------------------
    # Restore System
    # -------------------------

    def restore_system(self, backup_path: str):

        result = self.restore.full_restore(backup_path)

        return "System restored successfully"