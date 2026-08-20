"""
Domain types for the Python Execution Flow Tutor.
Source of truth: EVENT_SCHEMA.md, execution_flow.md
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# ---------------------------------------------------------------------------
# Execution status
# ---------------------------------------------------------------------------

class ExecutionStatus(str, Enum):
    CREATED = "CREATED"
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    WAITING_FOR_INPUT = "WAITING_FOR_INPUT"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"
    TIMEOUT = "TIMEOUT"
    SECURITY_VIOLATION = "SECURITY_VIOLATION"


# ---------------------------------------------------------------------------
# Safe value representation (EVENT_SCHEMA.md §19-21)
# ---------------------------------------------------------------------------

@dataclass
class ValueRepr:
    type: str        # e.g. "int", "str", "list"
    repr: str        # str(value) or repr(value)
    length: int | None = None        # for collections
    inspectable: bool = False        # for complex objects


# ---------------------------------------------------------------------------
# Execution frame / call stack (EVENT_SCHEMA.md §22-23)
# ---------------------------------------------------------------------------

@dataclass
class FrameState:
    frame_id: str
    function: str
    scope: str       # "global" | "local"
    line: int
    variables: dict[str, ValueRepr] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Execution state snapshot (EVENT_SCHEMA.md §24)
# ---------------------------------------------------------------------------

@dataclass
class ExecutionState:
    status: ExecutionStatus
    current_line: int | None
    current_frame_id: str | None
    variables: dict[str, ValueRepr]   # flat view of current frame vars
    call_stack: list[FrameState]
    stdout: str
    stderr: str
    exception: dict[str, str] | None  # {"type": ..., "message": ...}


# ---------------------------------------------------------------------------
# Execution session
# ---------------------------------------------------------------------------

@dataclass
class ExecutionSession:
    session_id: str
    source_code: str
    status: ExecutionStatus = ExecutionStatus.CREATED
    state: ExecutionState = field(default_factory=lambda: ExecutionState(
        status=ExecutionStatus.CREATED,
        current_line=None,
        current_frame_id=None,
        variables={},
        call_stack=[],
        stdout="",
        stderr="",
        exception=None,
    ))
    events: list[dict[str, Any]] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Event types (EVENT_SCHEMA.md §5)
# ---------------------------------------------------------------------------

class EventType(str, Enum):
    PROGRAM_START = "program_start"
    LINE = "line"
    VARIABLE_CREATED = "variable_created"
    VARIABLE_UPDATED = "variable_updated"
    INPUT_REQUESTED = "input_requested"
    INPUT_RECEIVED = "input_received"
    OUTPUT = "output"
    FUNCTION_CALL = "function_call"
    FUNCTION_RETURN = "function_return"
    EXCEPTION = "exception"
    PROGRAM_END = "program_end"
    TIMEOUT = "timeout"
    SECURITY_VIOLATION = "security_violation"


# ---------------------------------------------------------------------------
# Self-check
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    v = ValueRepr(type="int", repr="42")
    assert v.type == "int"

    f = FrameState(frame_id="f1", function="<module>", scope="global", line=1)
    assert f.scope == "global"

    state = ExecutionState(
        status=ExecutionStatus.RUNNING,
        current_line=1,
        current_frame_id="f1",
        variables={"x": v},
        call_stack=[f],
        stdout="",
        stderr="",
        exception=None,
    )
    assert state.status == ExecutionStatus.RUNNING

    session = ExecutionSession(session_id="exec_001", source_code="x = 1")
    assert session.status == ExecutionStatus.CREATED

    assert EventType.LINE == "line"
    print("All domain type assertions passed.")
