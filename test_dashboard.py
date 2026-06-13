from models.server_info import ServerInfo

from wizard.dashboard import (
    DashboardRenderer
)


info = ServerInfo()

info.root_login_enabled = True

info.password_login_enabled = True

info.ssh_key_enabled = True

info.ssh_port = 45891

info.firewall_installed = True

info.firewall_enabled = True

info.firewall_rules_count = 4

info.fail2ban_installed = True

info.fail2ban_active = True

info.fail2ban_jails = [
    "sshd"
]

info.backup_created = True

info.backup_verified = True

info.backup_integrity = True

info.rollback_available = True

info.rollback_snapshot_exists = True

info.verification_enabled = True

info.verification_status = "Verified"

info.verification_coverage = "Full"

DashboardRenderer(
    info
).render()