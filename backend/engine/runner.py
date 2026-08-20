"""
Execute user Python code in an isolated subprocess with sys.settrace tracing.

Architecture:
  backend process
      ↓ subprocess
  child process
      ├── tracer.trace_exec(source)
      ├── emits JSON events → stderr
      └── program stdout → stdout
  backend process
      └── parse JSON events from stderr

Security: user code never runs in main backend process. (SECURITY_SPEC.md §20)
ponytail: no full sandbox yet — filesystem/network/env isolation in TASK 15-18.
"""
from __future__ import annotations
import json
import subprocess
import sys
import textwrap
from dataclasses import dataclass, field
from pathlib import Path

MAX_SOURCE_BYTES = 64 * 1024    # SECURITY_SPEC.md §27
MAX_OUTPUT_BYTES = 256 * 1024   # SECURITY_SPEC.md §15
DEFAULT_TIMEOUT_S = 5           # SECURITY_SPEC.md §12

# Path to tracer module so child can import it
_ENGINE_DIR = Path(__file__).parent


@dataclass
class RunResult:
    events: list[dict] = field(default_factory=list)
    stdout: str = ""
    stderr_raw: str = ""   # non-JSON stderr lines (Python tracebacks, etc.)
    timed_out: bool = False
    exit_code: int = 0


def run_code(source: str, timeout: float = DEFAULT_TIMEOUT_S) -> RunResult:
    """Execute source in isolated child process; return parsed execution events."""
    if len(source.encode()) > MAX_SOURCE_BYTES:
        raise ValueError(f"Source code exceeds {MAX_SOURCE_BYTES} bytes")

    # Child bootstrap: import tracer from engine dir, then trace_exec(source)
    escaped = source.replace("\\", "\\\\").replace('"""', '\\"\\"\\"')
    bootstrap = textwrap.dedent(f"""\
        import sys
        sys.path.insert(0, {str(_ENGINE_DIR.parent)!r})
        from engine.tracer import trace_exec
        trace_exec({source!r})
    """)

    try:
        result = subprocess.run(
            [sys.executable, "-c", bootstrap],
            capture_output=True,
            timeout=timeout,
            text=True,
        )
    except subprocess.TimeoutExpired:
        return RunResult(
            timed_out=True,
            events=[{"type": "timeout", "sequence": 1, "timestamp": 0, "limit_ms": int(timeout * 1000)}],
        )

    # Parse events from stderr (one JSON per line)
    events: list[dict] = []
    raw_lines: list[str] = []
    for line in result.stderr.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            raw_lines.append(line)

    stdout = result.stdout
    if len(stdout.encode()) > MAX_OUTPUT_BYTES:
        stdout = stdout.encode()[:MAX_OUTPUT_BYTES].decode(errors="replace") + "\n[output truncated]"

    return RunResult(
        events=events,
        stdout=stdout,
        stderr_raw="\n".join(raw_lines),
        timed_out=False,
        exit_code=result.returncode,
    )


# ---------------------------------------------------------------------------
# Self-check
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Basic: line events + variable tracking
    r = run_code("x = 10\ny = x + 5\nprint(y)")
    types = [e["type"] for e in r.events]

    assert "program_start" in types, types
    assert "program_end" in types, types
    assert "line" in types, types
    assert "variable_created" in types, types
    assert "output" in types, types

    # Variable created with correct value
    vc = next(e for e in r.events if e["type"] == "variable_created" and e["variable"] == "x")
    assert vc["value"]["repr"] == "10", vc

    # Variable created y = 15
    vy = next(e for e in r.events if e["type"] == "variable_created" and e["variable"] == "y")
    assert vy["value"]["repr"] == "15", vy

    # Output event
    out_evt = next(e for e in r.events if e["type"] == "output")
    assert "15" in out_evt["value"], out_evt

    # Sequence ordering
    seqs = [e["sequence"] for e in r.events]
    assert seqs == sorted(seqs), "Events out of order"

    # Exception
    r2 = run_code("x = 10\ny = '5'\nprint(x + y)")
    exc = next(e for e in r2.events if e["type"] == "exception")
    assert exc["exception"]["type"] == "TypeError", exc

    # Timeout
    r3 = run_code("while True: pass", timeout=1)
    assert r3.timed_out is True

    # Source size limit
    try:
        run_code("x = 1\n" * 100_000)
        assert False, "should raise"
    except ValueError:
        pass

    print("All runner assertions passed.")
    print(f"Events for 'x=10; y=x+5; print(y)': {[e['type'] for e in r.events]}")
