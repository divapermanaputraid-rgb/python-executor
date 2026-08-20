"""
Execution event schema — EVENT_SCHEMA.md
Schema version: 1.0

All events are immutable after creation (frozen Pydantic models).
Invalid events raise ValidationError at construction time.
"""
from __future__ import annotations
from typing import Annotated, Any, Literal
from pydantic import BaseModel, Field, field_validator

SCHEMA_VERSION = "1.0"


# ---------------------------------------------------------------------------
# Shared value representation (EVENT_SCHEMA.md §19-21)
# ---------------------------------------------------------------------------

class ValueRepr(BaseModel, frozen=True):
    type: str
    repr: str
    length: int | None = None
    inspectable: bool = False


# ---------------------------------------------------------------------------
# Base event (EVENT_SCHEMA.md §3)
# ---------------------------------------------------------------------------

class BaseEvent(BaseModel, frozen=True):
    schema_version: str = SCHEMA_VERSION
    event_id: str
    session_id: str
    sequence: Annotated[int, Field(ge=1)]
    timestamp: float
    line: int | None = None

    @field_validator("event_id", "session_id")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("must not be empty")
        return v


# ---------------------------------------------------------------------------
# Concrete event types (EVENT_SCHEMA.md §6-18)
# ---------------------------------------------------------------------------

class ProgramStartEvent(BaseEvent):
    type: Literal["program_start"] = "program_start"


class LineEvent(BaseEvent):
    type: Literal["line"] = "line"
    line: int  # required for line events
    frame_id: str


class VariableCreatedEvent(BaseEvent):
    type: Literal["variable_created"] = "variable_created"
    frame_id: str
    variable: str
    value: ValueRepr


class VariableUpdatedEvent(BaseEvent):
    type: Literal["variable_updated"] = "variable_updated"
    frame_id: str
    variable: str
    previous_value: ValueRepr
    new_value: ValueRepr


class InputRequestedEvent(BaseEvent):
    type: Literal["input_requested"] = "input_requested"
    prompt: str = ""


class InputReceivedEvent(BaseEvent):
    type: Literal["input_received"] = "input_received"
    value: str


class OutputEvent(BaseEvent):
    type: Literal["output"] = "output"
    stream: Literal["stdout", "stderr"]
    value: str


class FunctionCallEvent(BaseEvent):
    type: Literal["function_call"] = "function_call"
    function: str
    frame_id: str
    arguments: dict[str, ValueRepr] = Field(default_factory=dict)


class FunctionReturnEvent(BaseEvent):
    type: Literal["function_return"] = "function_return"
    function: str
    frame_id: str
    value: ValueRepr


class ExceptionEvent(BaseEvent):
    type: Literal["exception"] = "exception"
    frame_id: str
    exception: dict[str, str]  # {"type": "TypeError", "message": "..."}


class ProgramEndEvent(BaseEvent):
    type: Literal["program_end"] = "program_end"
    status: Literal["completed"] = "completed"


class TimeoutEvent(BaseEvent):
    type: Literal["timeout"] = "timeout"
    limit_ms: int


class SecurityViolationEvent(BaseEvent):
    type: Literal["security_violation"] = "security_violation"
    reason: str


# ---------------------------------------------------------------------------
# Union for deserialization
# ---------------------------------------------------------------------------

AnyEvent = (
    ProgramStartEvent
    | LineEvent
    | VariableCreatedEvent
    | VariableUpdatedEvent
    | InputRequestedEvent
    | InputReceivedEvent
    | OutputEvent
    | FunctionCallEvent
    | FunctionReturnEvent
    | ExceptionEvent
    | ProgramEndEvent
    | TimeoutEvent
    | SecurityViolationEvent
)


# ---------------------------------------------------------------------------
# Self-check
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from pydantic import ValidationError
    import time

    base = dict(event_id="evt_001", session_id="exec_001", sequence=1, timestamp=time.time())

    def evt(**kw: Any) -> dict[str, Any]:  # noqa: F811 — local helper
        return {**base, **kw}

    # Valid events
    ps = ProgramStartEvent(**base)
    assert ps.type == "program_start"
    assert ps.schema_version == "1.0"

    def evt(**kw: Any) -> dict[str, Any]:
        return {**base, **kw}

    le = LineEvent(**evt(sequence=2, line=3, frame_id="f1"))
    assert le.line == 3

    v = ValueRepr(type="int", repr="10")
    vc = VariableCreatedEvent(**evt(sequence=3, line=1, frame_id="f1", variable="x", value=v))
    assert vc.variable == "x"

    vu = VariableUpdatedEvent(
        **evt(sequence=4, line=2, frame_id="f1", variable="x",
              previous_value=ValueRepr(type="int", repr="10"),
              new_value=ValueRepr(type="int", repr="20"))
    )
    assert vu.new_value.repr == "20"

    out = OutputEvent(**evt(sequence=5, line=3, stream="stdout", value="hello\n"))
    assert out.stream == "stdout"

    pe = ProgramEndEvent(**evt(sequence=6))
    assert pe.status == "completed"

    # Immutability
    try:
        ps.event_id = "changed"  # type: ignore
        assert False, "should be frozen"
    except Exception:
        pass

    # Invalid: sequence < 1
    try:
        ProgramStartEvent(**evt(sequence=0))
        assert False, "should fail"
    except ValidationError:
        pass

    # Invalid: empty session_id
    try:
        ProgramStartEvent(**evt(session_id="  "))
        assert False, "should fail"
    except ValidationError:
        pass

    # Serialisation round-trip
    data = le.model_dump()
    assert data["schema_version"] == "1.0"
    assert data["type"] == "line"

    print("All event schema assertions passed.")
