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
        comment: str = "server-hardener-managed",
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

        output, _, exit_code = (
            self.ssh.execute(
                f"getent passwd {username} | cut -d: -f6"
            )
        )

        if exit_code != 0:

            raise RuntimeError(
                (
                    "Could not determine home "
                    f"directory for {username}"
                )
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

        public_key_parts = (
            public_key.split()
        )

        if len(public_key_parts) < 2:
            return

        public_key_data = (
            public_key_parts[1]
        )

        remote_home = (
            self.get_user_home(
                remote_user
            )
        )

        authorized_keys = (
            f"{remote_home}/.ssh/authorized_keys"
        )

        try:

            content = (
                self.ssh.read_remote_file(
                    authorized_keys
                )
            )

        except FileNotFoundError:
            return

        lines = []

        for line in content.splitlines():

            line_parts = (
                line.strip().split()
            )

            if (
                len(line_parts) >= 2
                and line_parts[1]
                == public_key_data
            ):
                continue

            lines.append(line)

        new_content = "\n".join(lines)

        if new_content:
            new_content += "\n"

        self.ssh.write_remote_file(
            authorized_keys,
            new_content,
        )

        self.ssh.execute(
            f"chmod 600 {authorized_keys}"
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
                (
                    "Public key not found: "
                    f"{pub_key_path}"
                )
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

        try:

            content = (
                self.ssh.read_remote_file(
                    authorized_keys
                )
            )

        except FileNotFoundError:

            content = ""

        lines = [
            line.strip()
            for line in content.splitlines()
            if line.strip()
        ]

        if public_key not in lines:
            lines.append(public_key)

        new_content = (
            "\n".join(lines)
        )

        if new_content:
            new_content += "\n"

        self.ssh.write_remote_file(
            authorized_keys,
            new_content,
        )

        self.ssh.execute(
            f"chmod 600 {authorized_keys}"
        )

        self.ssh.execute_sudo(
            (
                f"chown -R "
                f"{remote_user}:{remote_user} "
                f"{ssh_dir}"
            )
        )

    def verify_key_login(
            self,
            private_key_path: Path,
            username: str | None = None,
    ) -> bool:

        test_username = (
                username
                or self.ssh.username
        )

        try:

            test_ssh = SSHManager(
                host=self.ssh.host,
                port=self.ssh.port,
                username=test_username,
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
                    == test_username
            )

        except Exception:
            return False