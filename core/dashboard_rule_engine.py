from dataclasses import dataclass, field

ROW_RULE = "rule"
ROW_GROUP = "group"

@dataclass
class DashboardRule:
    name: str
    current: str
    recommended: str
    status: str
    category: str = ""
    row_type: str = ROW_RULE


@dataclass
class DashboardRules:
    security_rules: list[DashboardRule] = field(default_factory=list)

    recovery_rules: list[DashboardRule] = field(default_factory=list)

    validation_rules: list[DashboardRule] = field(default_factory=list)

    transaction_rules: list[DashboardRule] = field(default_factory=list)


class DashboardRuleEngine:

    def __init__(self, info):
        self.info = info

    def build(self):
        return DashboardRules(
            security_rules=self._build_security_rules(),
            recovery_rules=self._build_recovery_rules(),
            validation_rules=self._build_validation_rules(),
            transaction_rules=self._build_transaction_rules(),
        )

    def _rule(
        self,
        name,
        current,
        recommended,
        status,
        category="",
    ):
        return DashboardRule(
            name=name,
            current=str(current),
            recommended=str(recommended),
            status=status,
            category=category,
            row_type=ROW_RULE,
        )

    def _group_header(
            self,
            title,
    ):
        return DashboardRule(
            name=title,
            current="",
            recommended="",
            status="",
            row_type=ROW_GROUP,
        )

    def _build_security_rules(self):

        rules = []
        rules.append(
            self._group_header(
                "SSH Setting"
            )
        )

        # Root Login
        rules.append(
            self._rule(
                "Root Login",
                "Enabled" if self.info.root_login_enabled else "Disabled",
                "Disabled",
                "critical"
                if self.info.root_login_enabled
                else "ok",
                "SSH",
            )
        )

        # Password Authentication
        rules.append(
            self._rule(
                "Password Authentication",
                "Enabled" if self.info.password_login_enabled else "Disabled",
                "Disabled",
                "critical"
                if self.info.password_login_enabled
                else "ok",
                "SSH",
            )
        )

        # Public Key Authentication
        rules.append(
            self._rule(
                "Public Key Authentication",
                "Enabled" if self.info.ssh_key_enabled else "Disabled",
                "Enabled",
                "ok"
                if self.info.ssh_key_enabled
                else "critical",
                "SSH",
            )
        )

        # SSH Port
        rules.append(
            self._rule(
                "SSH Port",
                self.info.ssh_port,
                "Non-Default",
                "critical"
                if self.info.ssh_port == 22
                else "ok",
                "SSH",
            )
        )
        rules.append(
            self._group_header(
                "Firewall Setting"
            )
        )
        # Firewall Installed
        rules.append(
            self._rule(
                "Firewall Installed",
                "Yes" if self.info.firewall_installed else "No",
                "Yes",
                "critical"
                if not self.info.firewall_installed
                else "ok",
                "Firewall",
            )
        )

        # Firewall Status
        rules.append(
            self._rule(
                "Firewall Status",
                "Active" if self.info.firewall_enabled else "Inactive",
                "Active",
                "critical"
                if not self.info.firewall_enabled
                else "ok",
                "Firewall",
            )
        )

        # Firewall Rules
        rules.append(
            self._rule(
                "Firewall Rules",
                self.info.firewall_rules_count,
                "> 0",
                "warning"
                if self.info.firewall_rules_count == 0
                else "ok",
                "Firewall",
            )
        )
        rules.append(
            self._group_header(
                "Fail2Ban Setting"
            )
        )
        # Fail2Ban Installed
        rules.append(
            self._rule(
                "Fail2Ban Installed",
                "Yes" if self.info.fail2ban_installed else "No",
                "Yes",
                "critical"
                if not self.info.fail2ban_installed
                else "ok",
                "Fail2Ban",
            )
        )

        # Fail2Ban Active
        rules.append(
            self._rule(
                "Fail2Ban Active",
                "Yes" if self.info.fail2ban_active else "No",
                "Yes",
                "critical"
                if not self.info.fail2ban_active
                else "ok",
                "Fail2Ban",
            )
        )

        # Fail2Ban Jails
        rules.append(
            self._rule(
                "Fail2Ban Jails",
                ", ".join(self.info.fail2ban_jails)
                if self.info.fail2ban_jails
                else "None",
                "sshd+",
                "warning"
                if not self.info.fail2ban_jails
                else "ok",
                "Fail2Ban",
            )
        )

        return rules

    def _build_recovery_rules(self):
        rules = []
        rules.append(
            self._group_header(
                "Backup Setting"
            )
        )
        rules.append(
            self._rule(
                "Backup Exists",
                (
                    "Yes"
                    if self.info.backup_created
                    else "No"
                ),
                "Yes",
                (
                    "ok"
                    if self.info.backup_created
                    else "critical"
                ),
            )
        )

        rules.append(
            self._rule(
                "Backup Verified",
                (
                    "Yes"
                    if self.info.backup_verified
                    else "No"
                ),
                "Yes",
                (
                    "ok"
                    if self.info.backup_verified
                    else "warning"
                ),
            )
        )

        rules.append(
            self._rule(
                "Backup Integrity",
                (
                    "Valid"
                    if self.info.backup_integrity
                    else "Unknown"
                ),
                "Valid",
                (
                    "ok"
                    if self.info.backup_integrity
                    else "warning"
                ),
            )
        )

        rules.append(
            self._group_header(
                "Rollback Setting"
            )
        )

        rules.append(
            self._rule(
                "Rollback Available",
                (
                    "Yes"
                    if self.info.rollback_available
                    else "No"
                ),
                "Yes",
                (
                    "ok"
                    if self.info.rollback_available
                    else "critical"
                ),
            )
        )

        rules.append(
            self._rule(
                "Rollback Snapshot",
                (
                    "Exists"
                    if self.info.rollback_snapshot_exists
                    else "Missing"
                ),
                "Exists",
                (
                    "ok"
                    if self.info.rollback_snapshot_exists
                    else "warning"
                ),
            )
        )

        return rules

    def _build_validation_rules(self):
        rules = []
        rules.append(
            self._group_header(
                "Verification Setting"
            )
        )
        rules.append(
            self._rule(
                "Verification Enabled",
                (
                    "Yes"
                    if self.info.verification_enabled
                    else "No"
                ),
                "Yes",
                (
                    "ok"
                    if self.info.verification_enabled
                    else "critical"
                ),
            )
        )

        rules.append(
            self._rule(
                "Verification Status",
                (
                    self.info.verification_status
                    if self.info.verification_status
                    else "Unknown"
                ),
                "Verified",
                (
                    "ok"
                    if self.info.verification_status == "Verified"
                    else "warning"
                ),
            )
        )

        rules.append(
            self._rule(
                "Verification Coverage",
                (
                    self.info.verification_coverage
                    if self.info.verification_coverage
                    else "Unknown"
                ),
                "Full",
                (
                    "ok"
                    if self.info.verification_coverage == "Full"
                    else "warning"
                ),
            )
        )

        return rules

    def _build_transaction_rules(self):
        return []