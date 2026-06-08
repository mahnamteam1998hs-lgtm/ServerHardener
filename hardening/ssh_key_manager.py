from pathlib import Path
import subprocess

from core.ssh_manager import SSHManager


class SSHKeyManager:

    def __init__(
        self,
        ssh_manager: SSHManager,
    ):
        self.ssh = ssh_manager

    def local_key_exists(
        self,
        private_key_path: Path,
    ) -> bool:

        return (
            private_key_path.exists()
            and private_key_path.is_file()
        )

    def generate_local_key(
        self,
        private_key_path: Path,
        comment: str = "server-hardener-key",
        passphrase: str = "",
    ) -> None:

        private_key_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        cmd = [
            "ssh-keygen",
            "-t",
            "ed25519",
            "-f",
            str(private_key_path),
            "-C",
            comment,
            "-N",
            passphrase,
        ]

        subprocess.run(
            cmd,
            check=True,
        )

    def get_user_home(
        self,
        username: str,
    ) -> str:

        output, _, exit_code = self.ssh.execute(
            f"getent passwd {username} | cut -d: -f6"
        )

        if exit_code != 0:

            raise RuntimeError(
                f"Could not determine home directory for {username}"
            )

        return output.strip()

    def remove_public_key_from_server(
        self,
        private_key_path: Path,
        remote_user: str,
    ) -> None:

        pub_key_path = (
            private_key_path.with_suffix(
                ".pub"
            )
        )

        if not pub_key_path.exists():
            return

        with open(
            pub_key_path,
            "r",
            encoding="utf-8",
        ) as f:

            public_key = (
                f.read().strip()
            )

        remote_home = (
            self.get_user_home(
                remote_user
            )
        )

        authorized_keys = (
            f"{remote_home}/.ssh/authorized_keys"
        )

        escaped_key = (
            public_key.replace(
                "'",
                "'\"'\"'"
            )
        )

        self.ssh.execute(
            (
                f"if [ -f {authorized_keys} ]; then "
                f"grep -Fvx '{escaped_key}' "
                f"{authorized_keys} > {authorized_keys}.tmp; "
                f"mv {authorized_keys}.tmp {authorized_keys}; "
                f"chmod 600 {authorized_keys}; "
                f"fi"
            )
        )

    def upload_public_key_to_server(
        self,
        private_key_path: Path,
        remote_user: str,
    ) -> None:

        pub_key_path = (
            private_key_path.with_suffix(
                ".pub"
            )
        )

        if not pub_key_path.exists():
            raise FileNotFoundError(
                f"Public key not found: {pub_key_path}"
            )

        remote_home = (
            self.get_user_home(
                remote_user
            )
        )

        ssh_dir = (
            f"{remote_home}/.ssh"
        )

        authorized_keys = (
            f"{ssh_dir}/authorized_keys"
        )

        self.ssh.execute(
            f"mkdir -p {ssh_dir}"
        )

        self.ssh.execute(
            f"chmod 700 {ssh_dir}"
        )

        with open(
            pub_key_path,
            "r",
            encoding="utf-8",
        ) as f:

            public_key = (
                f.read().strip()
            )

        escaped_key = (
            public_key.replace(
                "'",
                "'\"'\"'"
            )
        )

        self.ssh.execute(
            (
                f"touch {authorized_keys}; "
                f"if ! grep -Fxq '{escaped_key}' {authorized_keys}; then "
                f"echo '{escaped_key}' >> {authorized_keys}; "
                f"fi"
            )
        )

        self.ssh.execute(
            f"chmod 600 {authorized_keys}"
        )

    def verify_key_login(
        self,
        private_key_path: Path,
    ) -> bool:

        try:

            test_ssh = SSHManager(
                host=self.ssh.host,
                port=self.ssh.port,
                username=self.ssh.username,
                private_key_path=private_key_path,
            )

            test_ssh.connect()

            output, _, exit_code = (
                test_ssh.execute(
                    "whoami"
                )
            )

            test_ssh.disconnect()

            if exit_code != 0:
                return False

            return (
                output.strip()
                == self.ssh.username
            )

        except Exception:
            return False