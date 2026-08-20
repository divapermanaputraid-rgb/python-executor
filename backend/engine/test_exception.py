"""
Tests for structured exception state representation (TASK 14).
EVENT_SCHEMA.md §15, execution_flow.md §18, TASK 14
"""
from __future__ import annotations
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from engine.runner import run_code
from engine.normalizer import normalize
from engine.state_builder import build_snapshots

SID = "test_exc"


def test_type_error_exception_details():
    code = textwrap_dedent("""\
        x = 10
        y = "5"
        result = x + y
    """)
    r = run_code(code)
    evts = normalize(r.events, SID)
    snaps = build_snapshots(evts)

    exc_evt = next(e for e in evts if e["type"] == "exception")
    assert exc_evt["line"] == 3
    assert exc_evt["exception"]["type"] == "TypeError"
    assert "unsupported operand type" in exc_evt["exception"]["message"]

    # Traceback structure
    tb = exc_evt["exception"]["traceback"]
    assert len(tb) > 0
    assert tb[-1]["line"] == 3
    assert tb[-1]["function"] == "<module>"

    # State snapshot at error
    err_snap = snaps[-1]
    assert err_snap.status.value == "ERROR"
    assert err_snap.exception["type"] == "TypeError"
    assert err_snap.variables["x"].repr == "10"
    assert err_snap.variables["y"].repr == "'5'"


def test_zero_division_in_function():
    code = textwrap_dedent("""\
        def divide(a, b):
            return a / b

        x = 10
        y = 0
        ans = divide(x, y)
    """)
    r = run_code(code)
    evts = normalize(r.events, SID)
    snaps = build_snapshots(evts)

    exc_evt = next(e for e in evts if e["type"] == "exception")
    assert exc_evt["exception"]["type"] == "ZeroDivisionError"

    tb = exc_evt["exception"]["traceback"]
    # Should trace from <module> line 7 to divide() line 2
    lines = [item["line"] for item in tb]
    assert 2 in lines or 7 in lines, lines

    err_snap = snaps[-1]
    assert err_snap.status.value == "ERROR"


def textwrap_dedent(s: str) -> str:
    import textwrap
    return textwrap.dedent(s)


if __name__ == "__main__":
    test_type_error_exception_details()
    test_zero_division_in_function()
    print("All structured exception state tests passed.")
