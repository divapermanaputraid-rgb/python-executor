"""
Python runtime line tracer using sys.settrace.

This module is designed to run INSIDE the child process (not the backend).
It installs a trace function, executes user code, and emits JSON events
to stdout — one JSON object per line.

MASTER_CODING.md: "Do NOT simulate Python execution with regex/string parsing/LLM."
execution_flow.md §30: "Current line must come from execution trace."
"""
from __future__ import annotations
import builtins
from pathlib import Path
import sys
import json
import time
import traceback
import io
from types import FrameType
from typing import Any

# ---------------------------------------------------------------------------
# Safe value representation (execution_flow.md §26)
# ---------------------------------------------------------------------------

MAX_REPR_LEN = 200
MAX_COLLECTION_ITEMS = 20


def safe_repr(value: Any) -> dict[str, Any]:
    """Convert a Python value to a serialisable dict. No side effects."""
    t = type(value).__name__
    try:
        if isinstance(value, (int, float, bool, type(None))):
            return {"type": t, "repr": repr(value)}
        if isinstance(value, str):
            r = repr(value)
            return {"type": "str", "repr": r[:MAX_REPR_LEN] + ("…" if len(r) > MAX_REPR_LEN else "")}
        if isinstance(value, (list, tuple, set, frozenset)):
            items = list(value)[:MAX_COLLECTION_ITEMS]
            r = repr(type(value)(items))
            return {"type": t, "repr": r[:MAX_REPR_LEN], "length": len(value)}
        if isinstance(value, dict):
            items = dict(list(value.items())[:MAX_COLLECTION_ITEMS])
            r = repr(items)
            return {"type": "dict", "repr": r[:MAX_REPR_LEN], "length": len(value)}
        r = repr(value)
        return {"type": t, "repr": r[:MAX_REPR_LEN], "inspectable": True}
    except Exception:
        return {"type": t, "repr": "<repr error>"}


# ---------------------------------------------------------------------------
# Tracer
# ---------------------------------------------------------------------------

USER_CODE_FILE = "<string>"  # filename used when exec(compile(source, "<string>", "exec"))


class LineTracer:
    """
    sys.settrace-based tracer. Emits one JSON event per relevant trace call.
    Only traces frames from user code ("<string>") — ignores stdlib internals.
    Runs inside the child process.
    """

    def __init__(self, source_lines: list[str], out: io.TextIOBase) -> None:
        self._lines = source_lines
        self._out = out
        # per-frame locals snapshot: frame_id → {name: repr_dict}
        self._frame_locals: dict[str, dict[str, dict]] = {}
        self._seq = 0

    def _emit(self, event: dict[str, Any]) -> None:
        self._seq += 1
        event["sequence"] = self._seq
        event["timestamp"] = time.time()
        print(json.dumps(event), file=self._out, flush=True)

    def _snapshot_vars(self, frame: FrameType) -> dict[str, dict]:
        return {
            k: safe_repr(v)
            for k, v in frame.f_locals.items()
            if not k.startswith("__")
        }

    def _var_events(self, frame: FrameType, line: int, frame_id: str) -> None:
        """Diff locals for this frame and emit variable_created / variable_updated."""
        current = self._snapshot_vars(frame)
        prev = self._frame_locals.get(frame_id, {})
        for name, val in current.items():
            if name not in prev:
                self._emit({
                    "type": "variable_created",
                    "line": line,
                    "frame_id": frame_id,
                    "variable": name,
                    "value": val,
                })
            elif prev[name] != val:
                self._emit({
                    "type": "variable_updated",
                    "line": line,
                    "frame_id": frame_id,
                    "variable": name,
                    "previous_value": prev[name],
                    "new_value": val,
                })
        self._frame_locals[frame_id] = current

    # ------------------------------------------------------------------
    # sys.settrace protocol
    # ------------------------------------------------------------------

    def global_trace(self, frame: FrameType, event: str, arg: Any):
        # Only trace user code frames
        if frame.f_code.co_filename != USER_CODE_FILE:
            return None
        if event == "call":
            frame_id = f"frame_{id(frame)}"
            fn = frame.f_code.co_name
            if fn != "<module>":
                args = {
                    k: safe_repr(frame.f_locals.get(k))
                    for k in frame.f_code.co_varnames[: frame.f_code.co_argcount]
                }
                self._emit({
                    "type": "function_call",
                    "line": frame.f_lineno,
                    "frame_id": frame_id,
                    "function": fn,
                    "arguments": args,
                })
        return self.local_trace

    def local_trace(self, frame: FrameType, event: str, arg: Any):
        # Drop back to None for non-user frames (stdlib called from user code)
        if frame.f_code.co_filename != USER_CODE_FILE:
            return None
        frame_id = f"frame_{id(frame)}"
        line = frame.f_lineno

        if event == "line":
            self._emit({"type": "line", "line": line, "frame_id": frame_id})
            self._var_events(frame, line, frame_id)

        elif event == "return":
            # Emit var events before return so final locals are captured
            self._var_events(frame, line, frame_id)
            self._emit({
                "type": "function_return",
                "line": line,
                "frame_id": frame_id,
                "function": frame.f_code.co_name,
                "value": safe_repr(arg),
            })

        elif event == "exception":
            exc_type, exc_val, exc_tb = arg
            # Format clean user traceback lines
            tb_lines = []
            curr_tb = exc_tb
            while curr_tb:
                if curr_tb.tb_frame.f_code.co_filename == USER_CODE_FILE:
                    tb_lines.append({
                        "line": curr_tb.tb_lineno,
                        "function": curr_tb.tb_frame.f_code.co_name,
                    })
                curr_tb = curr_tb.tb_next

            # Capture current frame variables at exception point
            self._var_events(frame, line, frame_id)

            self._emit({
                "type": "exception",
                "line": line,
                "frame_id": frame_id,
                "exception": {
                    "type": exc_type.__name__,
                    "message": str(exc_val),
                    "traceback": tb_lines,
                },
            })

        return self.local_trace


# ---------------------------------------------------------------------------
# Entry point — called inside child process
# ---------------------------------------------------------------------------

def trace_exec(source: str, inputs: list[str] | None = None) -> None:
    """
    Install tracer, execute source, emit JSON events.
    stdout carries events; real program output is also emitted as 'output' events.
    inputs: pre-supplied inputs or interactive input values.
    """
    out = sys.stderr  # events go to stderr; stdout stays for program output
    lines = source.splitlines()

    tracer = LineTracer(source_lines=lines, out=out)

    # Input queue setup
    input_queue = list(inputs) if inputs is not None else []
    original_input = builtins.input
    original_open = builtins.open

    # Filesystem sandbox boundary check (SECURITY_SPEC.md §6)
    sandbox_root = Path.cwd().resolve()

    def custom_open(file, mode="r", *args, **kwargs):
        # Only enforce sandbox check when called from user code
        frame = sys._getframe(1)
        if frame.f_code.co_filename == USER_CODE_FILE:
            try:
                target_path = Path(file).resolve()
                if not (target_path == sandbox_root or sandbox_root in target_path.parents):
                    tracer._emit({
                        "type": "security_violation",
                        "line": frame.f_lineno,
                        "reason": f"filesystem_access_blocked: {file}",
                    })
                    raise PermissionError(f"Access to host path '{file}' is forbidden by sandbox")
            except (TypeError, ValueError):
                pass
        return original_open(file, mode, *args, **kwargs)

    builtins.open = custom_open

    def custom_input(prompt: str = "") -> str:
        # Get frame of user code calling input()
        frame = sys._getframe(1)
        line = frame.f_lineno if frame.f_code.co_filename == USER_CODE_FILE else 1

        tracer._emit({
            "type": "input_requested",
            "line": line,
            "prompt": str(prompt),
        })

        if input_queue:
            val = input_queue.pop(0)
        else:
            # Fallback to stdin line if available
            try:
                val = sys.__stdin__.readline().rstrip("\r\n")
            except Exception:
                val = ""

        tracer._emit({
            "type": "input_received",
            "line": line,
            "value": val,
        })
        return val

    builtins.input = custom_input

    # Capture program stdout and stderr
    real_stdout = sys.stdout
    real_stderr = sys.stderr
    event_out = real_stderr  # events go to real stderr

    class _CapturingStream(io.TextIOBase):
        def __init__(self, stream_name: str) -> None:
            self._stream_name = stream_name

        def write(self, s: str) -> int:
            if s:
                tracer._emit({"type": "output", "stream": self._stream_name, "value": s})
            return len(s)

        def flush(self) -> None:
            pass

    sys.stdout = _CapturingStream("stdout")  # type: ignore
    sys.stderr = _CapturingStream("stderr")  # type: ignore

    # Emit program_start
    tracer._emit({"type": "program_start"})

    try:
        sys.settrace(tracer.global_trace)
        exec(compile(source, "<string>", "exec"), {})  # noqa: S102
        sys.settrace(None)
        tracer._emit({"type": "program_end", "status": "completed"})
    except SyntaxError as e:
        sys.settrace(None)
        tracer._emit({
            "type": "exception",
            "line": e.lineno,
            "frame_id": "frame_global",
            "exception": {"type": "SyntaxError", "message": str(e)},
        })
        tracer._emit({"type": "program_end", "status": "error"})
    except Exception as e:
        sys.settrace(None)
        tracer._emit({
            "type": "exception",
            "line": getattr(e, "lineno", 1) or 1,
            "frame_id": "frame_global",
            "exception": {
                "type": type(e).__name__,
                "message": str(e),
            },
        })
        tracer._emit({"type": "program_end", "status": "error"})
    finally:
        sys.settrace(None)
        builtins.input = original_input
        builtins.open = original_open
        sys.stdout = real_stdout
        sys.stderr = real_stderr
