import questionary


def ask_firewall_options(server_info):

    current_status = (
        "ENABLED"
        if server_info.firewall_enabled
        else "DISABLED"
    )

    if server_info.firewall_enabled:

        choices = [
            "Keep Current Configuration",
            "Disable Firewall",
        ]

    else:

        choices = [
            "Keep Current Configuration",
            "Enable Firewall",
        ]

    action = questionary.select(
        f"Firewall Status: {current_status}",
        choices=choices,
    ).ask()

    extra_ports = []

    remove_rules = False

    if action == "Enable Firewall":

        ports = questionary.text(
            (
                "Additional ports "
                "(comma separated, blank = none)"
            )
        ).ask()

        if ports:

            extra_ports = [
                p.strip()
                for p in ports.split(",")
                if p.strip()
            ]

    elif action == "Disable Firewall":

        rule_action = questionary.select(
            "Firewall Rules",
            choices=[
                "Keep Existing Rules",
                "Remove All Rules",
            ],
        ).ask()

        remove_rules = (
            rule_action
            == "Remove All Rules"
        )

    return {
        "action": action,
        "extra_ports": extra_ports,
        "remove_rules": remove_rules,
    }