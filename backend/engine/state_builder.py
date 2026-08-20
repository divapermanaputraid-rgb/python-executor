"""
Call stack & execution state reconstructor.
EVENT_SCHEMA.md §22-24, execution_flow.md §20, §27

Reconstructs the active call stack and ExecutionState snapshot
from a sequence of normalized execution events.
"""
from __future__ import annotations
from typing import Any
from engine.types import ExecutionState, ExecutionStatus, FrameState, ValueRepr


def _to_value_repr(val: dict[str, Any] | None) -> ValueRepr | None:
    if val is None:
        return None
    return ValueRepr(
        type=val.get("type", "unknown"),
        repr=val.get("repr", "None"),
        length=val.get("length"),
        inspectable=val.get("inspectable", False),
    )


class StateReconstructor:
    """
    Reconstructs ExecutionState snapshot by processing normalized events sequentially.
    Source of truth: EVENT_SCHEMA.md §22-24
    """

    def __init__(self) -> None:
        self.status = ExecutionStatus.CREATED
        self.current_line: int | None = None
        self.current_frame_id: str | None = None
        self.call_stack: list[FrameState] = []
        self.stdout = ""
        self.stderr = ""
        self.exception: dict[str, str] | None = None

    def process_event(self, event: dict[str, Any]) -> ExecutionState:
        t = event.get("type")

        if t == "program_start":
            self.status = ExecutionStatus.RUNNING
            # Initialize global frame
            global_frame = FrameState(
                frame_id="frame_global",
                function="<module>",
                scope="global",
                line=1,
                variables={},
            )
            self.call_stack = [global_frame]
            self.current_frame_id = "frame_global"

        elif t == "line":
            self.current_line = event.get("line")
            frame_id = event.get("frame_id")
            if frame_id:
                self.current_frame_id = frame_id
                # If global frame still has placeholder ID, set it to real frame_id
                if len(self.call_stack) == 1 and self.call_stack[0].frame_id == "frame_global":
                    self.call_stack[0].frame_id = frame_id
                # Update line in active frame
                for frame in reversed(self.call_stack):
                    if frame.frame_id == frame_id:
                        frame.line = self.current_line or frame.line
                        break

        elif t == "variable_created" or t == "variable_updated":
            frame_id = event.get("frame_id") or self.current_frame_id
            var_name = event.get("variable")
            raw_val = event.get("value") or event.get("new_value")

            if var_name and raw_val:
                val_repr = _to_value_repr(raw_val)
                if val_repr:
                    # Match by frame_id, or default to matching single global frame
                    target_frame = None
                    for frame in reversed(self.call_stack):
                        if frame.frame_id == frame_id:
                            target_frame = frame
                            break
                    if target_frame is None and len(self.call_stack) == 1:
                        target_frame = self.call_stack[0]

                    if target_frame:
                        target_frame.variables[var_name] = val_repr

        elif t == "function_call":
            frame_id = event.get("frame_id", f"frame_{len(self.call_stack)}")
            fn_name = event.get("function", "function")
            line = event.get("line", 1)
            raw_args = event.get("arguments", {})

            args_repr = {
                k: _to_value_repr(v) for k, v in raw_args.items() if _to_value_repr(v) is not None
            }

            new_frame = FrameState(
                frame_id=frame_id,
                function=fn_name,
                scope="local",
                line=line,
                variables=args_repr,
            )
            self.call_stack.append(new_frame)
            self.current_frame_id = frame_id
            self.current_line = line

        elif t == "function_return":
            frame_id = event.get("frame_id")
            if len(self.call_stack) > 1:
                # Pop matching frame or top frame
                if frame_id and self.call_stack[-1].frame_id == frame_id:
                    self.call_stack.pop()
                elif not frame_id:
                    self.call_stack.pop()
                else:
                    # Find and remove matching frame
                    self.call_stack = [f for f in self.call_stack if f.frame_id != frame_id]

                if self.call_stack:
                    self.current_frame_id = self.call_stack[-1].frame_id
                    self.current_line = self.call_stack[-1].line

        elif t == "output":
            stream = event.get("stream", "stdout")
            val = event.get("value", "")
            if stream == "stdout":
                self.stdout += val
            elif stream == "stderr":
                self.stderr += val

        elif t == "exception":
            self.status = ExecutionStatus.ERROR
            self.exception = event.get("exception")
            line = event.get("line")
            if line:
                self.current_line = line

        elif t == "program_end":
            st = event.get("status")
            if st == "completed":
                self.status = ExecutionStatus.COMPLETED
            elif st == "error":
                self.status = ExecutionStatus.ERROR

        elif t == "timeout":
            self.status = ExecutionStatus.TIMEOUT

        elif t == "security_violation":
            self.status = ExecutionStatus.SECURITY_VIOLATION

        # Compute flat variable map for top frame
        active_vars = self.call_stack[-1].variables if self.call_stack else {}

        return ExecutionState(
            status=self.status,
            current_line=self.current_line,
            current_frame_id=self.current_frame_id,
            variables=active_vars,
            call_stack=list(self.call_stack),
            stdout=self.stdout,
            stderr=self.stderr,
            exception=self.exception,
        )


def build_snapshots(events: list[dict[str, Any]]) -> list[ExecutionState]:
    """Reconstruct ExecutionState snapshot for every event in the stream."""
    reconstructor = StateReconstructor()
    return [reconstructor.process_event(evt) for evt in events]


# ---------------------------------------------------------------------------
# Self-check / Test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    from engine.runner import run_code
    from engine.normalizer import normalize

    code = """\
def multiply(x, y):
    res = x * y
    return res

a = 5
b = 10
total = multiply(a, b)
"""
    r = run_code(code)
    evts = normalize(r.events, "test_stack")
    snapshots = build_snapshots(evts)

    # Find snapshot inside multiply() call
    in_fn_snapshots = [
        s for s in snapshots
        if s.current_frame_id and len(s.call_stack) == 2 and s.call_stack[-1].function == "multiply"
    ]
    assert len(in_fn_snapshots) > 0, "No inside-function snapshot found"

    fn_state = in_fn_snapshots[-1]
    assert len(fn_state.call_stack) == 2
    assert fn_state.call_stack[0].scope == "global"
    assert fn_state.call_stack[1].scope == "local"
    assert fn_state.call_stack[1].function == "multiply"
    assert fn_state.call_stack[1].variables["x"].repr == "5"
    assert fn_state.call_stack[1].variables["y"].repr == "10"
    assert fn_state.call_stack[1].variables["res"].repr == "50"

    # Final snapshot
    final_state = snapshots[-1]
    assert final_state.status == ExecutionStatus.COMPLETED
    assert len(final_state.call_stack) == 1
    assert final_state.call_stack[0].variables["total"].repr == "50"

    print("All CallStack state reconstruction tests passed.")
