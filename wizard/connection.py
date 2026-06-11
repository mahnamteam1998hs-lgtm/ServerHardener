import questionary

from config.settings import DEFAULT_SSH_PORT


def ask_connection():

    host = questionary.text(
        "Server IP:"
    ).ask()

    port = questionary.text(
        "SSH Port:",
        default=str(DEFAULT_SSH_PORT)
    ).ask()

    username = questionary.text(
        "Username:"
    ).ask()

    return {
        "host": host.strip(),
        "port": int(port.strip()),
        "username": username.strip(),
    }