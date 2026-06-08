from pathlib import Path

from rich.console import Console

from core.progress_manager import ProgressManager
from core.backup_manager import BackupManager
from core.ssh_manager import SSHManager
from core.server_detector import ServerDetector
from core.user_settings import UserSettings

from hardening.hardening_manager import HardeningManager
from hardening.ssh_key_manager import SSHKeyManager

from wizard.connection import ask_connection
from wizard.summary import show_summary
from wizard.firewall import ask_firewall_options
from wizard.fail2ban import ask_fail2ban_options
from wizard.ssh_key import (
    ask_ssh_key_action,
    setup_ssh_key,
)


progress = ProgressManager()

console = Console()

console.print(
    "[bold green]Ubuntu Server Hardening Wizard[/bold green]"
)

connection = ask_connection()

ssh = SSHManager(
    connection["host"],
    connection["port"],
    connection["username"],
    connection["password"],
)

try:

    progress.start(
        "Connecting"
    )

    ssh.connect()

    progress.stop(
        "Connected"
    )

    output, error, exit_code = ssh.execute(
        "sudo -n true"
    )

    if exit_code != 0:
        raise RuntimeError(
            "Passwordless sudo is required."
        )

    settings = UserSettings()

    verified_key_path = None

    saved_key_path = settings.get_key_path(
        connection["host"],
        connection["port"],
        connection["username"],
    )

    key_manager = SSHKeyManager(
        ssh
    )

    if saved_key_path:

        if (
            saved_key_path.exists()
            and key_manager.verify_key_login(
                saved_key_path
            )
        ):

            verified_key_path = (
                saved_key_path
            )

        else:

            settings.remove_connection(
                connection["host"],
                connection["port"],
                connection["username"],
            )

            saved_key_path = None

    ssh_key_action = ask_ssh_key_action(
        verified_key_path
    )

    ssh_key_enabled = False

    ssh_key_verified = False

    if (
        ssh_key_action["action"]
        == "reuse"
    ):

        ssh_key_enabled = True

        ssh_key_verified = True

    elif (
        ssh_key_action["action"]
        == "replace"
    ):

        progress.start(
            "Replacing SSH Key"
        )

        if saved_key_path:

            key_manager.remove_public_key_from_server(
                saved_key_path,
                ssh.username,
            )

        setup_ssh_key(
            ssh,
            ssh_key_action["key_path"],
            force_regenerate=True,
        )

        settings.save_key_path(
            connection["host"],
            connection["port"],
            connection["username"],
            str(
                ssh_key_action[
                    "key_path"
                ]
            ),
        )

        ssh_key_enabled = True

        ssh_key_verified = True

        progress.stop(
            "SSH Key Replaced"
        )

    elif (
        ssh_key_action["action"]
        == "generate"
    ):

        progress.start(
            "Configuring SSH Key"
        )

        setup_ssh_key(
            ssh,
            ssh_key_action["key_path"],
        )

        settings.save_key_path(
            connection["host"],
            connection["port"],
            connection["username"],
            str(
                ssh_key_action[
                    "key_path"
                ]
            ),
        )

        ssh_key_enabled = True

        ssh_key_verified = True

        progress.stop(
            "SSH Key Configured"
        )

    progress.start(
        "Detecting Server"
    )

    detector = ServerDetector(
        ssh
    )

    server_info = detector.detect()

    server_info.ssh_key_enabled = (
        ssh_key_enabled
    )

    server_info.ssh_key_verified = (
        ssh_key_verified
    )

    progress.stop(
        "Server Detected"
    )

    progress.start(
        "Creating Backup"
    )

    backup_manager = BackupManager(
        ssh
    )

    backup_path = (
        backup_manager.create_backup()
    )

    server_info.backup_path = (
        backup_path
    )

    server_info.backup_created = True

    backup_verified = (
        backup_manager.verify_backup(
            backup_path
        )
    )

    server_info.backup_verified = (
        backup_verified
    )

    progress.stop(
        "Backup Created"
    )

    console.print(
        f"[green]Backup Path:[/green] {backup_path}"
    )

    console.print(
        f"[green]Backup Verified:[/green] {backup_verified}"
    )

    hardening = HardeningManager(
        ssh,
        server_info,
    )

    firewall_options = (
        ask_firewall_options(
            server_info
        )
    )

    firewall_status = ""

    if (
        firewall_options["action"]
        == "Enable Firewall"
    ):

        progress.start(
            "Configuring Firewall"
        )

        hardening.enable_firewall(
            extra_ports=firewall_options[
                "extra_ports"
            ]
        )

        firewall_status = (
            hardening.ufw.status()
        )

        progress.stop(
            "Firewall Configured"
        )

    elif (
        firewall_options["action"]
        == "Disable Firewall"
    ):

        progress.start(
            "Disabling Firewall"
        )

        hardening.disable_firewall()

        firewall_status = (
            hardening.ufw.status()
        )

        progress.stop(
            "Firewall Disabled"
        )

    fail2ban_options = (
        ask_fail2ban_options(
            server_info
        )
    )

    if (
        fail2ban_options["action"]
        == "Install / Enable"
    ):

        progress.start(
            "Configuring Fail2Ban"
        )

        hardening.enable_fail2ban()

        progress.stop(
            "Fail2Ban Enabled"
        )

    else:

        if (
            server_info.fail2ban_installed
        ):

            progress.start(
                "Removing Fail2Ban"
            )

            hardening.uninstall_fail2ban()

            progress.stop(
                "Fail2Ban Removed"
            )

    progress.start(
        "Generating Summary"
    )

    progress.stop(
        "Completed"
    )

    console.print(
        "\n[bold cyan]Final Summary[/bold cyan]\n"
    )

    show_summary(
        server_info
    )

    if firewall_status:

        console.print(
            f"\n{firewall_status}"
        )

finally:

    ssh.disconnect()