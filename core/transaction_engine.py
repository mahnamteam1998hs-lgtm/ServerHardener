from core.state.restore_state import (
    RestoreState
)


class TransactionEngine:

    def __init__(
            self,
            backup_manager,
            restore_engine,
            validator,
            state_machine,
    ):

        self.backup_manager = backup_manager

        self.restore_engine = restore_engine

        self.validator = validator

        self.state_machine = state_machine

    def execute_restore(
            self,
            backup_path,
            ssh=True,
            users=True,
            sudoers=True,
    ):

        snapshot = self.backup_manager.create_backup()

        self.state_machine.set_state(
            RestoreState.SNAPSHOT_CREATED
        )

        print(
            "[STATE]",
            self.state_machine.get_state()
        )

        try:

            self.state_machine.set_state(
                RestoreState.RESTORE_RUNNING
            )

            print(
                "[STATE]",
                self.state_machine.get_state()
            )

            self.restore_engine.restore_selected(
                backup_path,
                ssh=ssh,
                users=users,
                sudoers=sudoers,
            )

            self.state_machine.set_state(
                RestoreState.VERIFY_RUNNING
            )

            print(
                "[STATE]",
                self.state_machine.get_state()
            )

            verify = self.validator.verify_selected(
                ssh=ssh,
                users=users,
                sudoers=sudoers,
            )

            if not all(verify.values()):
                raise RuntimeError(
                    f"Verify failed: {verify}"
                )

            self.state_machine.set_state(
                RestoreState.SUCCESS
            )

            print(
                "[STATE]",
                self.state_machine.get_state()
            )

            return {
                "status": "success",
                "verify": verify,
                "snapshot": snapshot,
            }

        except Exception as e:

            self.state_machine.set_state(
                RestoreState.VERIFY_FAILED
            )

            print(
                "[STATE]",
                self.state_machine.get_state()
            )

            self.state_machine.set_state(
                RestoreState.ROLLBACK_RUNNING
            )

            print(
                "[STATE]",
                self.state_machine.get_state()
            )

            self.restore_engine.restore_selected(
                snapshot,
                ssh=ssh,
                users=users,
                sudoers=sudoers,
            )

            self.state_machine.set_state(
                RestoreState.ROLLED_BACK
            )

            print(
                "[STATE]",
                self.state_machine.get_state()
            )

            return {
                "status": "rolled_back",
                "error": str(e),
                "snapshot": snapshot,
            }