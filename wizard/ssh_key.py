import questionary

from pathlib import Path

from core.ssh_manager import SSHManager

from hardening.ssh_key_manager import (
    SSHKeyManager,
)


def ask_ssh_key_action(
    verified_key_path: Path | None,
):

    if verified_key_path:

        action = questionary.select(
            (
                "A verified SSH key was "
                f"found:\n{verified_key_path}"
            ),
            choices=[
                "Reuse Existing Key",
                "Replace Existing Key",
                "Skip SSH Key Authentication",
            ],
        ).ask()

        if action == "Reuse Existing Key":

            return {
                "action": "reuse",
                "key_path": verified_key_path,
            }

        if action == "Replace Existing Key":

            key_path = ask_key_path(
                default_path=verified_key_path
            )

            return {
                "action": "replace",
                "key_path": key_path,
            }

        return {
            "action": "skip",
            "key_path": None,
        }

    enable = questionary.confirm(
        "Do you want to enable SSH key authentication?",
        default=True,
    ).ask()

    if not enable:

        return {
            "action": "skip",
            "key_path": None,
        }

    key_path = ask_key_path()

    return {
        "action": "generate",
        "key_path": key_path,
    }


def ask_key_path(
    default_path: Path | None = None,
) -> Path:

    if default_path is None:

        default_path = (
            Path.home()
            / ".ssh"
            / "server_hardener_ed25519"
        )

    use_default = questionary.select(
        (
            "Default SSH key location:\n"
            f"{default_path}"
        ),
        choices=[
            "Use This Location",
            "Choose Another Location",
        ],
    ).ask()

    if use_default == "Use This Location":
        return default_path

    custom_path = questionary.text(
        "Enter SSH key path:",
    ).ask()

    key_path = (
        Path(custom_path)
        .expanduser()
        .resolve()
    )

    if key_path.exists():

        if key_path.is_dir():

            raise RuntimeError(
                "SSH key path must be a file path, not a directory."
            )

    return key_path


def setup_ssh_key(
    ssh: SSHManager,
    key_path: Path,
    force_regenerate: bool = False,
):

    manager = SSHKeyManager(
        ssh
    )

    if force_regenerate:

        if key_path.exists():
            key_path.unlink()

        pub_key_path = (
            key_path.with_suffix(
                ".pub"
            )
        )

        if pub_key_path.exists():
            pub_key_path.unlink()

    if not manager.local_key_exists(
        key_path
    ):

        manager.generate_local_key(
            key_path
        )

    manager.upload_public_key_to_server(
        key_path,
        ssh.username,
    )

    verified = (
        manager.verify_key_login(
            key_path
        )
    )

    if not verified:

        raise RuntimeError(
            "SSH key verification failed."
        )

    return True
