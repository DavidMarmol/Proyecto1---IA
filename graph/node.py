from enum import Enum


class NodeState(Enum):
    LOCKED = "locked"
    AVAILABLE = "available"
    SOLVED = "solved"


class Node:
    def __init__(
        self, node_id: str, label: str = "", locked: bool = False, puzzle_id: str = None
    ):
        self.node_id = node_id
        self.label = label if label else node_id
        self.puzzle_id = puzzle_id
        self.state = NodeState.LOCKED if locked else NodeState.AVAILABLE

    @property
    def is_locked(self) -> bool:
        return self.state == NodeState.LOCKED

    @property
    def is_available(self) -> bool:
        return self.state == NodeState.AVAILABLE

    @property
    def is_solved(self) -> bool:
        return self.state == NodeState.SOLVED

    def unlock(self):
        if self.state == NodeState.LOCKED:
            self.state = NodeState.AVAILABLE

    def mark_solved(self):
        self.state = NodeState.SOLVED

    def __repr__(self) -> str:
        return f"Node({self.node_id!r}, state={self.state.value})"

    def __eq__(self, other) -> bool:
        if isinstance(other, Node):
            return self.node_id == other.node_id
        return False

    def __hash__(self) -> int:
        return hash(self.node_id)
