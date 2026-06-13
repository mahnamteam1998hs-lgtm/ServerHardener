from models.server_info import ServerInfo

from core.dashboard_rule_engine import DashboardRuleEngine


info = ServerInfo()

# SSH

info.root_login_enabled = True
info.password_login_enabled = True

info.ssh_key_enabled = True

info.ssh_port = 45891

# Firewall

info.firewall_installed = True
info.firewall_enabled = True

info.firewall_rules_count = 4

# Fail2Ban

info.fail2ban_installed = True
info.fail2ban_active = True

info.fail2ban_jails = ["sshd"]

rules = DashboardRuleEngine(
    info
).build()

print("\n=== SECURITY RULES ===\n")

for rule in rules.security_rules:

    print(
        f"{rule.name:25}"
        f"{rule.current:15}"
        f" -> "
        f"{rule.recommended:15}"
        f"{rule.status}"
    )