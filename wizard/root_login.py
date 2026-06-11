import questionary


def ask_disable_root_login():

    return questionary.confirm(
        (
            "Disable SSH root login?\n\n"
            "Recommended: Yes"
        ),
        default=True,
    ).ask()