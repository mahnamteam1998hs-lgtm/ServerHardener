import questionary


def ask_disable_password_login():

    return questionary.confirm(
        (
            "Disable SSH password login?\n\n"
            "Highly Recommended: Yes"
        ),
        default=True,
    ).ask()