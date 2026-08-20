"""
Minimal Python execution in an isolated subprocess.

Security: user code runs in a child process, never in main backend process.
ponytail: no full sandbox yet — filesystem/network/env isolation in TASK 15-18.
"""
from __future__ import annotations
import subprocess
import sys
import textwrap
from dataclasses import dataclass


MAX_SOURCE_BYTES = 64 * 1024   # 64 KB — SECURITY_SPEC.md §27
MAX_OUTPUT_BYTES = 256 * 1024  # 256 KB — SECURITY_SPEC.md §15
DEFAULT_TIMEOUT_S = 5          # SECURITY_SPEC.md §12


@dataclass
class RunResult:
    stdout: str
    stderr: str
    exit_code: int
    timed_out: bool


def run_code(source: str, timeout: float = DEFAULT_TIMEOUT_S) -> RunResult:
    """Execute Python source in an isolated subprocess and return stdout/stderr."""
    if len(source.encode()) > MAX_SOURCE_BYTES:
        raise ValueError(f"Source code exceeds {MAX_SOURCE_BYTES} bytes")

    try:
        result = subprocess.run(
            [sys.executable, "-c", source],
            capture_output=True,
            timeout=timeout,
            text=True,
        )
    except subprocess.TimeoutExpired:
        return RunResult(stdout="", stderr="", exit_code=-1, timed_out=True)

    stdout = result.stdout
    if len(stdout.encode()) > MAX_OUTPUT_BYTES:
        stdout = stdout.encode()[:MAX_OUTPUT_BYTES].decode(errors="replace") + "\n[output truncated]"

    return RunResult(
        stdout=stdout,
        stderr=result.stderr,
        exit_code=result.returncode,
        timed_out=False,
    )


# ---------------------------------------------------------------------------
# Self-check
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Basic stdout
    r = run_code('print("hello")')
    assert r.stdout.strip() == "hello", repr(r.stdout)
    assert r.timed_out is False
    assert r.exit_code == 0

    # Stderr / exception
    r2 = run_code("x = 1 + 'oops'")
    assert r2.exit_code != 0
    assert "TypeError" in r2.stderr

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
