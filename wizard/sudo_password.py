import questionary


def ask_sudo_password():

    return questionary.password(
        "User Password (used for sudo):"
    ).ask()