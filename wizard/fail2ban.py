import questionary


def ask_fail2ban_options(server_info):

    installed = (
        server_info.fail2ban_installed
    )

    active = (
        server_info.fail2ban_active
    )

    if not installed:

        action = questionary.select(
            (
                "Fail2Ban "
                "[Installed: No] "
                "[Active: No]"
            ),
            choices=[
                "Install Only",
                "Install and Enable",
                "Skip",
            ],
        ).ask()

    elif active:

        action = questionary.select(
            (
                "Fail2Ban "
                "[Installed: Yes] "
                "[Active: Yes]"
            ),
            choices=[
                "Keep Enabled",
                "Disable Only",
                "Uninstall (Keep Config)",
                "Uninstall Completely",
            ],
        ).ask()

    else:

        action = questionary.select(
            (
                "Fail2Ban "
                "[Installed: Yes] "
                "[Active: No]"
            ),
            choices=[
                "Enable",
                "Keep Disabled",
                "Uninstall (Keep Config)",
                "Uninstall Completely",
            ],
        ).ask()

    return {
        "action": action,
    }