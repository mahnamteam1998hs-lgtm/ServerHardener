import questionary


def ask_backup_selection(backups):

    return questionary.select(
        "Select Backup",
        choices=backups,
    ).ask()


def ask_restore_components():

    selected = questionary.checkbox(
        "Restore Components",
        choices=[
            "SSH",
            "Users",
            "Sudoers",
        ],
    ).ask()

    if not selected:
        raise ValueError(
            "At least one component must be selected."
        )

    return {
        "ssh": "SSH" in selected,
        "users": "Users" in selected,
        "sudoers": "Sudoers" in selected,
    }

import questionary


def confirm_restore(
        backup_name,
        components,
):

    selected = []

    if components["ssh"]:
        selected.append("SSH")

    if components["users"]:
        selected.append("Users")

    if components["sudoers"]:
        selected.append("Sudoers")

    return questionary.confirm(
        f"\nBackup: {backup_name}\n"
        f"Components: {', '.join(selected)}\n\n"
        f"Continue restore?"
    ).ask()