from enum import Enum, auto


class RestoreState(Enum):

    IDLE = auto()

    SNAPSHOT_CREATED = auto()

    RESTORE_RUNNING = auto()

    VERIFY_RUNNING = auto()

    SUCCESS = auto()

    VERIFY_FAILED = auto()

    ROLLBACK_RUNNING = auto()

    ROLLED_BACK = auto()

class RestoreStateMachine:

    def __init__(self):

        self.state = RestoreState.IDLE

    def set_state(self, state):

        self.state = state

    def get_state(self):

        return self.state

    def __str__(self):

        return self.state.name