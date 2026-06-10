import paramiko
from typing import Optional, Union
from pathlib import Path


class SSHManager:

    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: Optional[str] = None,
        private_key_path: Optional[Union[str, Path]] = None,
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.private_key_path = (
            Path(private_key_path)
            if private_key_path
            else None
        )

        self.client: Optional[
            paramiko.SSHClient
        ] = None

    def connect(self):

        self.client = (
            paramiko.SSHClient()
        )

        self.client.set_missing_host_key_policy(
            paramiko.AutoAddPolicy()
        )

        if (
            self.private_key_path
            and self.private_key_path.exists()
        ):

            key = (
                paramiko.Ed25519Key.from_private_key_file(
                    str(
                        self.private_key_path
                    )
                )
            )

            self.client.connect(
                hostname=self.host,
                port=self.port,
                username=self.username,
                pkey=key,
                timeout=10,
            )

        elif self.password:

            self.client.connect(
                hostname=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                timeout=10,
            )

        else:

            raise RuntimeError(
                (
                    "No valid authentication method "
                    "provided (password or SSH key)."
                )
            )

    def execute(
        self,
        command: str,
    ):

        if not self.client:

            raise RuntimeError(
                "SSH client not connected."
            )

        stdin, stdout, stderr = (
            self.client.exec_command(
                command
            )
        )

        output = (
            stdout.read()
            .decode()
            .strip()
        )

        error = (
            stderr.read()
            .decode()
            .strip()
        )

        exit_code = (
            stdout.channel.recv_exit_status()
        )

        return (
            output,
            error,
            exit_code,
        )

    def execute_sudo(
        self,
        command: str,
    ):

        return self.execute(
            f"sudo {command}"
        )

    def read_remote_file(
        self,
        remote_path: str,
    ) -> str:

        if not self.client:

            raise RuntimeError(
                "SSH client not connected."
            )

        sftp = (
            self.client.open_sftp()
        )

        try:

            with sftp.open(
                remote_path,
                "r",
            ) as remote_file:

                return (
                    remote_file.read()
                    .decode(
                        "utf-8"
                    )
                )

        finally:

            sftp.close()

    def write_remote_file(
        self,
        remote_path: str,
        content: str,
    ) -> None:

        if not self.client:

            raise RuntimeError(
                "SSH client not connected."
            )

        sftp = (
            self.client.open_sftp()
        )

        try:

            with sftp.open(
                remote_path,
                "w",
            ) as remote_file:

                remote_file.write(
                    content
                )

        finally:

            sftp.close()

    def disconnect(self):

        if self.client:

            self.client.close()

            self.client = None