import json
import os

from pathlib import Path


class UserSettings:

    def __init__(self):

        self.settings_path = (
            self._get_settings_path()
        )

        self.settings_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    def _get_settings_path(
        self,
    ) -> Path:

        if os.name == "nt":

            appdata = os.getenv(
                "APPDATA"
            )

            if appdata:

                return (
                    Path(appdata)
                    / "ServerHardener"
                    / "user_settings.json"
                )

        return (
            Path.home()
            / ".config"
            / "server-hardener"
            / "user_settings.json"
        )

    def load_settings(
        self,
    ) -> dict:

        if not self.settings_path.exists():

            return {
                "connections": {}
            }

        try:

            with open(
                self.settings_path,
                "r",
                encoding="utf-8",
            ) as f:

                data = json.load(f)

            if not isinstance(
                data,
                dict,
            ):
                raise ValueError

            data.setdefault(
                "connections",
                {},
            )

            return data

        except Exception:

            return {
                "connections": {}
            }

    def save_settings(
        self,
        data: dict,
    ) -> None:

        with open(
            self.settings_path,
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(
                data,
                f,
                indent=4,
            )

    def _connection_key(
        self,
        host: str,
        port: int,
        username: str,
    ) -> str:

        return (
            f"{username}@{host}:{port}"
        )

    def save_key_path(
        self,
        host: str,
        port: int,
        username: str,
        key_path: str,
    ) -> None:

        data = self.load_settings()

        connection_key = (
            self._connection_key(
                host,
                port,
                username,
            )
        )

        data["connections"][
            connection_key
        ] = {
            "key_path": key_path,
            "last_verified": True,
        }

        self.save_settings(
            data
        )

    def get_connection(
        self,
        host: str,
        port: int,
        username: str,
    ) -> dict | None:

        data = self.load_settings()

        connection_key = (
            self._connection_key(
                host,
                port,
                username,
            )
        )

        return data[
            "connections"
        ].get(
            connection_key
        )

    def get_key_path(
        self,
        host: str,
        port: int,
        username: str,
    ) -> Path | None:

        connection = (
            self.get_connection(
                host,
                port,
                username,
            )
        )

        if not connection:
            return None

        key_path = connection.get(
            "key_path"
        )

        if not key_path:
            return None

        return Path(
            key_path
        )

    def remove_connection(
        self,
        host: str,
        port: int,
        username: str,
    ) -> None:

        data = self.load_settings()

        connection_key = (
            self._connection_key(
                host,
                port,
                username,
            )
        )

        if (
            connection_key
            in data["connections"]
        ):

            del data[
                "connections"
            ][
                connection_key
            ]

            self.save_settings(
                data
            )