from models.server_info import ServerInfo


class DashboardEngine:

    def __init__(self, server_info: ServerInfo):
        self.info = server_info

    # =====================================
    # PUBLIC
    # =====================================

    def build(self) -> ServerInfo:

        self._calculate_authentication_method()

        self._calculate_port_security()

        self._generate_findings()

        self._calculate_security_grade()

        self._calculate_recovery_grade()

        self._calculate_overall_health()

        self.info.dashboard_initialized = True

        return self.info

    # =====================================
    # AUTHENTICATION
    # =====================================

    def _calculate_authentication_method(self):

        if (
            self.info.ssh_key_enabled
            and not self.info.password_login_enabled
        ):
            self.info.authentication_method = (
                "SSH Key Only"
            )

        elif (
            self.info.ssh_key_enabled
            and self.info.password_login_enabled
        ):
            self.info.authentication_method = (
                "Password + SSH Key"
            )

        elif (
            not self.info.ssh_key_enabled
            and self.info.password_login_enabled
        ):
            self.info.authentication_method = (
                "Password Only"
            )

        else:
            self.info.authentication_method = (
                "Unknown"
            )

    # =====================================
    # PORT SECURITY
    # =====================================

    def _calculate_port_security(self):

        if self.info.ssh_port == 22:
            self.info.port_security_status = (
                "Default Port"
            )

        else:
            self.info.port_security_status = (
                "Non-Default Port"
            )

    # =====================================
    # FINDINGS
    # =====================================

    def _generate_findings(self):

        findings = []

        if self.info.root_login_enabled:
            findings.append(
                "Root login is enabled"
            )

        if self.info.password_login_enabled:
            findings.append(
                "Password authentication is enabled"
            )

        if self.info.ssh_port == 22:
            findings.append(
                "SSH is running on default port 22"
            )

        if not self.info.firewall_enabled:
            findings.append(
                "Firewall is disabled"
            )

        if not self.info.fail2ban_active:
            findings.append(
                "Fail2Ban is not active"
            )

        self.info.findings = findings

    # =====================================
    # SECURITY GRADE
    # =====================================

    def _calculate_security_grade(self):

        score = 0

        if not self.info.root_login_enabled:
            score += 25

        if not self.info.password_login_enabled:
            score += 25

        if self.info.firewall_enabled:
            score += 25

        if self.info.fail2ban_active:
            score += 25

        self.info.overall_security_score = score

        if score >= 95:
            grade = "A+"

        elif score >= 85:
            grade = "A"

        elif score >= 70:
            grade = "B"

        elif score >= 50:
            grade = "C"

        else:
            grade = "F"

        self.info.security_grade = grade

    # =====================================
    # RECOVERY GRADE
    # =====================================

    def _calculate_recovery_grade(self):

        score = 0

        if self.info.backup_created:
            score += 25

        if self.info.backup_verified:
            score += 25

        if self.info.rollback_available:
            score += 25

        if self.info.verification_enabled:
            score += 25

        self.info.overall_recovery_score = score

        if score >= 95:
            grade = "A+"

        elif score >= 85:
            grade = "A"

        elif score >= 70:
            grade = "B"

        elif score >= 50:
            grade = "C"

        else:
            grade = "F"

        self.info.recovery_grade = grade

    # =====================================
    # OVERALL HEALTH
    # =====================================

    def _calculate_overall_health(self):

        average = (
            self.info.overall_security_score
            +
            self.info.overall_recovery_score
        ) / 2

        if average >= 90:
            health = "Excellent"

        elif average >= 75:
            health = "Good"

        elif average >= 60:
            health = "Warning"

        else:
            health = "Critical"

        self.info.overall_health = health