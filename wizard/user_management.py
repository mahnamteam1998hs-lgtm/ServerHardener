import questionary
import re


def ask_user_management(
    server_info,
):

    if (
        server_info.current_user
        != "root"
    ):
        return {
            "action": "skip"
        }

    return {
        "action": questionary.select(
            (
                "Root account detected.\n"
                "Recommended: create a dedicated admin user."
            ),
            choices=[
                "Create Admin User",
                "Continue Using Root",
            ],
        ).ask()
    }


def ask_new_admin_username():

    while True:

        username = questionary.text(
            "New admin username:"
        ).ask()

        if not username:
            continue

        username = username.strip()

        if not re.match(
            r"^[a-z_][a-z0-9_-]{2,31}$",
            username,
        ):
            print(
                "Invalid username format."
            )
            continue

        return username


def ask_new_admin_password():

    while True:

        password = (
            questionary.password(
                "Password:"
            ).ask()
        )

        confirm = (
            questionary.password(
                "Confirm Password:"
            ).ask()
        )

        if password != confirm:

            print(
                "Passwords do not match."
            )

            continue

        return password