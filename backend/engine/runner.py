"""
Execute user Python code in an isolated subprocess with sys.settrace tracing
and strict resource limits.

Security Limits (SECURITY_SPEC.md §11-15, §27):
  - Timeout: 3 seconds
  - Max source size: 64 KB
  - Max output size: 256 KB
  - Max memory: 256 MB (via resource.setrlimit)
  - Execution timeout / memory abuse terminates process safely.
"""
from __future__ import annotations
import json
import os
import resource
import subprocess
import sys
import tempfile
import textwrap
from dataclasses import dataclass, field
from pathlib import Path

MAX_SOURCE_BYTES = 64 * 1024      # SECURITY_SPEC.md §27 (64 KB)
MAX_OUTPUT_BYTES = 256 * 1024     # SECURITY_SPEC.md §15 (256 KB)
DEFAULT_TIMEOUT_S = 3.0           # SECURITY_SPEC.md §11-12 (3s)
MAX_MEMORY_BYTES = 256 * 1024 * 1024  # SECURITY_SPEC.md §13 (256 MB)

_ENGINE_DIR = Path(__file__).parent


@dataclass
class RunResult:
    events: list[dict] = field(default_factory=list)
    stdout: str = ""
    stderr_raw: str = ""
    timed_out: bool = False
    exit_code: int = 0


def _set_resource_limits() -> None:
    """Pre-exec fn in child process: sets memory rlimit."""
    try:
        resource.setrlimit(resource.RLIMIT_AS, (MAX_MEMORY_BYTES, MAX_MEMORY_BYTES))
    except (ValueError, OSError):
        pass


def _get_minimal_env() -> dict[str, str]:
    """
    Construct minimal environment for child execution process.
    SECURITY_SPEC.md §9: Host secrets must not leak to user code.
    """
    clean_env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "PYTHONPATH": str(_ENGINE_DIR.parent),
        "PYTHONUNBUFFERED": "1",
        "PYTHONIOENCODING": "utf-8",
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "SANDBOX_ID": "isolated_exec",
    }
    return clean_env


def run_code(
    source: str,
    inputs: list[str] | None = None,
    timeout: float = DEFAULT_TIMEOUT_S,
    work_dir: str | None = None,
) -> RunResult:
    """
    Execute source in isolated child process within a temporary working directory
    and minimal environment.
    SECURITY_SPEC.md §6-7, §9: Filesystem and Environment Isolation
    """
    if len(source.encode()) > MAX_SOURCE_BYTES:
        raise ValueError(f"Source code size exceeds limit of {MAX_SOURCE_BYTES} bytes")

    temp_dir_obj = None
    if work_dir is None:
        temp_dir_obj = tempfile.TemporaryDirectory(prefix="exec_sandbox_")
        target_dir = temp_dir_obj.name
    else:
        target_dir = work_dir

    try:
        inputs_repr = repr(inputs or [])
        bootstrap = textwrap.dedent(f"""\
            import sys
            sys.path.insert(0, {str(_ENGINE_DIR.parent)!r})
            from engine.tracer import trace_exec
            trace_exec({source!r}, {inputs_repr})
        """)

        try:
            result = subprocess.run(
                [sys.executable, "-c", bootstrap],
                capture_output=True,
                timeout=timeout,
                text=True,
                cwd=target_dir,
                env=_get_minimal_env(),
                preexec_fn=_set_resource_limits if os.name != "nt" else None,
            )
        except subprocess.TimeoutExpired:
            return RunResult(
                timed_out=True,
                events=[{
                    "type": "timeout",
                    "sequence": 1,
                    "timestamp": 0,
                    "limit_ms": int(timeout * 1000),
                }],
            )

        if result.returncode == -9 or "MemoryError" in result.stderr:
            return RunResult(
                events=[{
                    "type": "security_violation",
                    "sequence": 1,
                    "timestamp": 0,
                    "reason": "memory_limit_exceeded",
                }],
                exit_code=result.returncode,
            )

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
    finally:
        if temp_dir_obj is not None:
            temp_dir_obj.cleanup()


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
