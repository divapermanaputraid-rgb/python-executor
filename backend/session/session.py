"""
Execution session lifecycle management.
execution_flow.md §4-5, SECURITY_SPEC.md §21-23
"""
from __future__ import annotations
import uuid
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Iterator

from engine.types import (
    ExecutionStatus,
    ExecutionState,
    ValueRepr,
    FrameState,
)


def _empty_state() -> ExecutionState:
    return ExecutionState(
        status=ExecutionStatus.CREATED,
        current_line=None,
        current_frame_id=None,
        variables={},
        call_stack=[],
        stdout="",
        stderr="",
        exception=None,
    )


@dataclass
class Session:
    session_id: str
    source_code: str
    created_at: float
    status: ExecutionStatus = ExecutionStatus.CREATED
    state: ExecutionState = field(default_factory=_empty_state)
    events: list[dict] = field(default_factory=list)
    _sequence: int = field(default=0, repr=False)

    # ------------------------------------------------------------------
    # Sequence counter (EVENT_SCHEMA.md §4)
    # ------------------------------------------------------------------

    def next_sequence(self) -> int:
        self._sequence += 1
        return self._sequence

    # ------------------------------------------------------------------
    # Lifecycle transitions
    # ------------------------------------------------------------------

    def transition(self, new_status: ExecutionStatus) -> None:
        self.status = new_status
        self.state = ExecutionState(
            status=new_status,
            current_line=self.state.current_line,
            current_frame_id=self.state.current_frame_id,
            variables=self.state.variables,
            call_stack=self.state.call_stack,
            stdout=self.state.stdout,
            stderr=self.state.stderr,
            exception=self.state.exception,
        )

    # ------------------------------------------------------------------
    # Cleanup (SECURITY_SPEC.md §23)
    # ------------------------------------------------------------------

    def cleanup(self) -> None:
        """Release session resources. Called on all termination paths."""
        self.events.clear()
        # ponytail: no temp files/processes to clean yet — TASK 15-16 adds sandbox cleanup


def create_session(source_code: str) -> Session:
    return Session(
        session_id=f"exec_{uuid.uuid4().hex[:8]}",
        source_code=source_code,
        created_at=time.time(),
    )


# ---------------------------------------------------------------------------
# In-memory session registry (ponytail: global dict, per-process only)
# ---------------------------------------------------------------------------

_sessions: dict[str, Session] = {}


def register(session: Session) -> None:
    _sessions[session.session_id] = session


def get(session_id: str) -> Session | None:
    return _sessions.get(session_id)


def remove(session_id: str) -> None:
    session = _sessions.pop(session_id, None)
    if session:
        session.cleanup()


@contextmanager
def managed_session(source_code: str) -> Iterator[Session]:
    """Create, register, yield, then cleanup a session automatically."""
    session = create_session(source_code)
    register(session)
    try:
        yield session
    finally:
        remove(session.session_id)


# ---------------------------------------------------------------------------
# Self-check
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Create and register
    s = create_session("x = 1")
    assert s.status == ExecutionStatus.CREATED
    assert s.session_id.startswith("exec_")
    register(s)
    assert get(s.session_id) is s

    # Lifecycle transitions
    s.transition(ExecutionStatus.RUNNING)
    assert s.status == ExecutionStatus.RUNNING
    assert s.state.status == ExecutionStatus.RUNNING

    s.transition(ExecutionStatus.WAITING_FOR_INPUT)
    assert s.status == ExecutionStatus.WAITING_FOR_INPUT

    s.transition(ExecutionStatus.COMPLETED)
    assert s.status == ExecutionStatus.COMPLETED

    # Sequence counter
    assert s.next_sequence() == 1
    assert s.next_sequence() == 2

    # Cleanup
    sid = s.session_id
    remove(sid)
    assert get(sid) is None

    # Context manager (auto cleanup)
    with managed_session("print('hi')") as ms:
        ms.transition(ExecutionStatus.RUNNING)
        mid = ms.session_id
        assert get(mid) is ms
    assert get(mid) is None

    print("All session assertions passed.")
