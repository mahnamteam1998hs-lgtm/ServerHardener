import questionary


def ask_fail2ban_options(server_info):

    if (
        server_info.fail2ban_installed
        and server_info.fail2ban_active
    ):
        status = "ACTIVE"

    elif server_info.fail2ban_installed:
        status = "INSTALLED"

    else:
        status = "NOT INSTALLED"

    action = questionary.select(
        f"Fail2Ban Status: {status}",
        choices=[
            "Install / Enable",
            "Uninstall",
        ]
    ).ask()

    return {
        "action": action
    }