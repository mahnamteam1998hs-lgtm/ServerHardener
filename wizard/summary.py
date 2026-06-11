from rich.console import Console
from rich.table import Table


def show_summary(server_info):

    console = Console()

    table = Table(
        title="Server Information"
    )

    table.add_column(
        "Setting",
        no_wrap=True,
    )

    table.add_column(
        "Value"
    )

    table.add_row(
        "Hostname",
        server_info.hostname,
    )

    table.add_row(
        "Ubuntu Version",
        server_info.ubuntu_version,
    )

    table.add_row(
        "Current User",
        server_info.current_user,
    )

    table.add_row(
        "SSH Port",
        str(server_info.ssh_port),
    )

    table.add_row(
        "SSH Service",
        (
            "Active"
            if server_info.ssh_service_active
            else "Inactive"
        ),
    )

    table.add_row(
        "Firewall",
        (
            "Enabled"
            if server_info.firewall_enabled
            else "Disabled"
        ),
    )

    table.add_row(
        "Firewall Configured",
        (
            "Yes"
            if server_info.firewall_configured
            else "-"
        ),
    )

    table.add_row(
        "Firewall Status",
        server_info.firewall_status,
    )

    table.add_row(
        "Fail2Ban Installed",
        (
            "Yes"
            if server_info.fail2ban_installed
            else "No"
        ),
    )

    table.add_row(
        "Fail2Ban Active",
        (
            "Yes"
            if server_info.fail2ban_active
            else "No"
        ),
    )

    table.add_row(
        "Root Login",
        (
            "Enabled"
            if server_info.root_login_enabled
            else "Disabled"
        ),
    )

    table.add_row(
        "Password Login",
        (
            "Enabled"
            if server_info.password_login_enabled
            else "Disabled"
        ),
    )

    table.add_row(
        "Backup Path",
        server_info.backup_path,
    )

    table.add_row(
        "Backup Created",
        (
            "Yes"
            if server_info.backup_created
            else "-"
        ),
    )

    table.add_row(
        "Backup Verified",
        (
            "Yes"
            if server_info.backup_verified
            else "-"
        ),
    )

    console.print(
        table
    )