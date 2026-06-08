from pydantic import BaseModel


class ServerInfo(BaseModel):

    hostname: str = ""

    ubuntu_version: str = ""

    current_user: str = ""

    ssh_port: int = 22

    ssh_service_active: bool = False

    # Firewall

    firewall_enabled: bool = False

    firewall_configured: bool = False

    firewall_status: str = ""

    # Fail2Ban

    fail2ban_installed: bool = False

    fail2ban_active: bool = False

    # SSH

    root_login_enabled: bool = False

    password_login_enabled: bool = False

    ssh_key_enabled: bool = False

    ssh_key_verified: bool = False

    # Backup

    backup_path: str = ""

    backup_created: bool = False

    backup_verified: bool = False