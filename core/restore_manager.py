from core.state.restore_state import (
    RestoreState,
    RestoreStateMachine,
)
from core.validation_engine import (
    ValidationEngine
)
from core.restore_engine import (
    RestoreEngine
)

from core.transaction_engine import (
    TransactionEngine
)

class RestoreManager:

    def __init__(self, ssh_manager, backup_manager):
        self.ssh = ssh_manager
        self.backup_manager = backup_manager
        self.state_machine = (
            RestoreStateMachine()
        )

        self.validator = ValidationEngine(
            ssh_manager
        )

        self.restore_engine = RestoreEngine(
            ssh_manager
        )

        self.transaction_engine = (
            TransactionEngine(
                backup_manager=self.backup_manager,
                restore_engine=self.restore_engine,
                validator=self.validator,
                state_machine=self.state_machine,
            )
        )

    def create_safety_snapshot(self):
        return self.backup_manager.create_backup()


    def full_restore(
            self,
            backup_path: str,
            ssh=True,
            users=True,
            sudoers=True,
    ):
        self.state_machine.set_state(
            RestoreState.IDLE
        )

        print(
            "[STATE]",
            self.state_machine.get_state().name
        )

        return self.transaction_engine.execute_restore(
            backup_path=backup_path,
            ssh=ssh,
            users=users,
            sudoers=sudoers,
        )