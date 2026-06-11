class TransactionManager:

    def __init__(self, ssh_manager, backup_manager):
        self.ssh = ssh_manager
        self.backup = backup_manager
        self.snapshot_path = None
        self.backup_path = None

    def begin(self):
        """
        Start transaction → create safety snapshot
        """

        self.snapshot_path = self._create_snapshot()
        return self.snapshot_path

    def _create_snapshot(self):

        output, error, exit_code = self.ssh.execute_sudo(
            "date +%F_%H-%M-%S"
        )

        if exit_code != 0:
            raise RuntimeError("Failed creating snapshot timestamp")

        snapshot_path = f"/opt/server-hardener/pre-restore/{output.strip()}"

        self.ssh.execute_sudo(f"mkdir -p {snapshot_path}")

        # backup critical state before restore
        self.ssh.execute_sudo(
            f"tar -czf {snapshot_path}/system.tar.gz /etc /home /root"
        )

        return snapshot_path

    def commit(self):
        """
        Transaction successful → cleanup snapshot
        """

        if self.snapshot_path:
            self.ssh.execute_sudo(
                f"rm -rf {self.snapshot_path}"
            )

        return True

    def rollback(self):
        """
        Restore system from snapshot
        """

        if not self.snapshot_path:
            raise RuntimeError("No snapshot to rollback")

        self.ssh.execute_sudo(
            f"tar -xzf {self.snapshot_path}/system.tar.gz -C /"
        )

        return True