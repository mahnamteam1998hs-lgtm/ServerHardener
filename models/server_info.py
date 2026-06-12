from pydantic import BaseModel


class ServerInfo(BaseModel):

    # =====================================
    # SYSTEM
    # =====================================

    hostname: str = ""

    ubuntu_version: str = ""

    current_user: str = ""

    users: list[str] = []

    admin_users: list[str] = []

    ssh_port: int = 22

    ssh_service_active: bool = False

    # =====================================
    # SSH SECURITY
    # =====================================

    root_login_enabled: bool = False

    password_login_enabled: bool = False

    ssh_key_enabled: bool = False

    ssh_key_verified: bool = False

    authentication_method: str = ""

    port_security_status: str = ""

    # =====================================
    # FIREWALL
    # =====================================

    firewall_installed: bool = False

    firewall_enabled: bool = False

    firewall_configured: bool = False

    firewall_status: str = ""

    firewall_version: str = ""

    firewall_rules_count: int = 0

    # =====================================
    # FAIL2BAN
    # =====================================

    fail2ban_installed: bool = False

    fail2ban_active: bool = False

    fail2ban_version: str = ""

    fail2ban_jails: list[str] = []

    # =====================================
    # BACKUP
    # =====================================

    backup_path: str = ""

    backup_created: bool = False

    backup_verified: bool = False

    backup_timestamp: str = ""

    backup_age: str = ""

    backup_integrity: bool = False

    backup_coverage: str = ""

    # =====================================
    # ROLLBACK
    # =====================================

    rollback_available: bool = False

    rollback_snapshot_exists: bool = False

    # =====================================
    # VALIDATION
    # =====================================

    verification_enabled: bool = True

    verification_status: str = ""

    verification_coverage: str = ""

    # =====================================
    # TRANSACTION
    # =====================================

    transaction_engine_enabled: bool = True

    transaction_state: str = "IDLE"

    last_transaction_status: str = ""

    last_rollback_status: str = ""

    # =====================================
    # DASHBOARD / ANALYTICS
    # =====================================

    security_grade: str = ""

    recovery_grade: str = ""

    overall_security_score: int = 0

    overall_recovery_score: int = 0

    overall_health: str = ""

    findings: list[str] = []

    dashboard_initialized: bool = False