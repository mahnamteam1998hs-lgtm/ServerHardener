import questionary


def ask_firewall_options(server_info):

    current_status = (
        "ENABLED"
        if server_info.firewall_enabled
        else "DISABLED"
    )

    action = questionary.select(
        f"Firewall Status: {current_status}",
        choices=[
            "Enable Firewall",
            "Disable Firewall",
        ]
    ).ask()

    extra_ports = []

    if action == "Enable Firewall":

        ports = questionary.text(
            "Additional ports (comma separated, blank = none)"
        ).ask()

        if ports:

            extra_ports = [
                p.strip()
                for p in ports.split(",")
                if p.strip()
            ]

    return {
        "action": action,
        "extra_ports": extra_ports,
    }