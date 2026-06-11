import questionary

from wizard.ssh_key import (
    ask_key_path,
    setup_ssh_key,
)


def ask_new_user_ssh_key(
    ssh,
    username: str,
):

    configure = questionary.confirm(
        (
            f"Configure SSH key authentication "
            f"for '{username}'?"
        ),
        default=True,
    ).ask()

    if not configure:

        return {
            "configured": False,
        }

    key_path = ask_key_path()

    actual_key_path = setup_ssh_key(
        ssh=ssh,
        key_path=key_path,
        remote_user=username,
    )

    return {
        "configured": True,
        "key_path": actual_key_path,
    }