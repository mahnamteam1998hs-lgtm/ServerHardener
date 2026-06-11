from pathlib import Path
from wizard.root_login import (
    ask_disable_root_login,
)
from wizard.password_login import (
    ask_disable_password_login,
)

from rich.console import Console
from core.progress_manager import ProgressManager
from core.backup_manager import BackupManager
from core.ssh_manager import SSHManager
from core.server_detector import ServerDetector
from core.sudo_validator import (
    validate_sudo,
)
from core.user_settings import UserSettings
from hardening.hardening_manager import HardeningManager
from hardening.ssh_key_manager import SSHKeyManager
from wizard.connection import ask_connection
from wizard.sudo_password import (
    ask_sudo_password,
)
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

sudo_password = (
    ask_sudo_password()
)

settings = UserSettings()

saved_key_path = settings.get_key_path(
    connection["host"],
    connection["port"],
    connection["username"],
)

ssh = SSHManager(
    connection["host"],
    connection["port"],
    connection["username"],
    password=sudo_password,
    private_key_path=saved_key_path,
)

try:

    progress.start(
        "Connecting"
    )

    ssh.connect()

    progress.stop(
        "Connected"
    )

    sudo_valid = False

    for attempt in range(3):

        try:

            validate_sudo(ssh)

            sudo_valid = True

            break

        except RuntimeError:

            if attempt == 2:
                raise RuntimeError(
                    "Invalid sudo password."
                )

            console.print(
                (
                    f"[yellow]Invalid sudo password "
                    f"({attempt + 1}/3)[/yellow]"
                )
            )

            sudo_password = (
                ask_sudo_password()
            )

            ssh.password = (
                sudo_password
            )

    if not sudo_valid:
        raise RuntimeError(
            "Invalid sudo password."
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

        generated_key_path = setup_ssh_key(
            ssh,
            ssh_key_action["key_path"],
            force_regenerate=True,
        )

        settings.save_key_path(
            connection["host"],
            connection["port"],
            connection["username"],
            str(generated_key_path),
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

        generated_key_path = setup_ssh_key(
            ssh,
            ssh_key_action["key_path"],
        )

        settings.save_key_path(
            connection["host"],
            connection["port"],
            connection["username"],
            str(generated_key_path),
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

    try:

        server_info = detector.detect()

        progress.stop(
            "Server Detected"
        )

    except RuntimeError as e:

        progress.stop(
            "Detection Failed"
        )

        console.print(
            f"[red]Error during detection:[/red] {e}"
        )

        ssh.disconnect()

        exit(1)

    hardening = HardeningManager(
        ssh,
        server_info,
    )

    from core.user_manager import UserManager
    from wizard.user_management import (
        ask_user_management,
        ask_new_admin_username,
        ask_new_admin_password,
    )

    server_info.ssh_key_enabled = (
        ssh_key_enabled
    )

    server_info.ssh_key_verified = (
        ssh_key_verified
    )

    user_options = (
        ask_user_management(
            server_info
        )
    )

    if (
            user_options["action"]
            == "Create Admin User"
    ):

        user_manager = UserManager(
            ssh
        )

        username = (
            ask_new_admin_username()
        )

        while (
                user_manager.is_reserved_username(
                    username
                )
        ):
            console.print(
                (
                    "[red]Reserved username.[/red]"
                )
            )

            username = (
                ask_new_admin_username()
            )

        password = (
            ask_new_admin_password()
        )

        progress.start(
            "Creating Admin User"
        )

        success = (
            user_manager.create_admin_user(
                username,
                password,
            )
        )

        progress.stop(
            "Admin User Created"
        )

        from wizard.new_user_ssh_key import (
            ask_new_user_ssh_key,
        )

        ssh_key_result = (
            ask_new_user_ssh_key(
                ssh,
                username,
            )
        )

        if ssh_key_result["configured"]:
            console.print(
                (
                    f"[green]SSH key verified "
                    f"for '{username}'.[/green]"
                )
            )

    if ssh_key_verified:

        console.print(
            "\n[bold cyan]SSH Hardening[/bold cyan]\n"
        )

        disable_root = (
            ask_disable_root_login()
        )

        if disable_root:

            progress.start(
                "Disabling Root Login"
            )

            success = (
                hardening.disable_root_login()
            )

            progress.stop(
                (
                    "Root Login Disabled"
                    if success
                    else "Failed"
                )
            )

            if success:
                console.print(
                    (
                        "[green]Root login "
                        "disabled successfully."
                        "[/green]"
                    )
                )

        disable_password = (
            ask_disable_password_login()
        )

        if disable_password:

            progress.start(
                "Disabling Password Login"
            )

            success = (
                hardening.disable_password_login()
            )

            progress.stop(
                (
                    "Password Login Disabled"
                    if success
                    else "Failed"
                )
            )

            if success:
                console.print(
                    (
                        "[green]Password login "
                        "disabled successfully."
                        "[/green]"
                    )
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

    firewall_options = (
        ask_firewall_options(
            server_info
        )
    )

    firewall_status = ""
    if (
            firewall_options["action"]
            == "Keep Current Configuration"
    ):

        firewall_status = (
            hardening.ufw.status()
        )

        server_info.firewall_status = (
            firewall_status
        )

    elif (
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

        server_info.firewall_status = (
            firewall_status
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

        hardening.disable_firewall(
            remove_rules=firewall_options[
                "remove_rules"
            ]
        )

        firewall_status = (
            hardening.ufw.status()
        )

        server_info.firewall_status = (
            firewall_status
        )

        progress.stop(
            "Firewall Disabled"
        )

    fail2ban_options = (
        ask_fail2ban_options(
            server_info
        )
    )

    action = (
        fail2ban_options["action"]
    )

    if action == "Install Only":

        progress.start(
            "Installing Fail2Ban"
        )

        hardening.install_fail2ban()

        progress.stop(
            "Fail2Ban Installed"
        )

    elif action == "Install and Enable":

        progress.start(
            "Configuring Fail2Ban"
        )

        hardening.enable_fail2ban()

        progress.stop(
            "Fail2Ban Enabled"
        )

    elif action == "Enable":

        progress.start(
            "Enabling Fail2Ban"
        )

        hardening.enable_fail2ban()

        progress.stop(
            "Fail2Ban Enabled"
        )

    elif action == "Disable Only":

        progress.start(
            "Disabling Fail2Ban"
        )

        hardening.disable_fail2ban()

        progress.stop(
            "Fail2Ban Disabled"
        )

    elif action == "Uninstall (Keep Config)":

        progress.start(
            "Removing Fail2Ban"
        )

        hardening.uninstall_fail2ban()

        progress.stop(
            "Fail2Ban Removed"
        )

    elif action == "Uninstall Completely":

        progress.start(
            "Purging Fail2Ban"
        )

        hardening.purge_fail2ban()

        progress.stop(
            "Fail2Ban Purged"
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

except RuntimeError as e:

    try:
        progress.stop(
            "Failed"
        )
    except Exception:
        pass

    console.print()

    console.print(
        f"[red]Error:[/red] {e}"
    )

finally:

    ssh.disconnect()