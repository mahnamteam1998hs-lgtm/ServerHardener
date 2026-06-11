class UserManager:

    RESERVED_USERNAMES = {
        "root",
        "ubuntu",
        "debian",
        "admin",
        "administrator",
        "ec2-user",
        "centos",
        "rocky",
        "test",
        "user",
        "guest",
        "support",
        "backup",
    }

    def __init__(self, ssh_manager):
        self.ssh = ssh_manager

    def is_reserved_username(
        self,
        username: str,
    ):
        return (
            username.lower()
            in self.RESERVED_USERNAMES
        )

    def user_exists(
        self,
        username: str,
    ):
        _, _, exit_code = (
            self.ssh.execute(
                f"id {username}"
            )
        )

        return exit_code == 0

    def create_admin_user(
        self,
        username: str,
        password: str,
    ):

        self.ssh.execute_sudo(
            (
                f"adduser "
                f"--disabled-password "
                f"--gecos '' "
                f"{username}"
            )
        )

        self.ssh.execute(
            (
                f"echo '{username}:{password}' "
                f"| sudo chpasswd"
            )
        )

        self.ssh.execute_sudo(
            (
                f"usermod -aG sudo {username}"
            )
        )

        return self.user_exists(
            username
        )