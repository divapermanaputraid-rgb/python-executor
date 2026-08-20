"""
Tests for function call and return tracking (TASK 12).
EVENT_SCHEMA.md §13-14, execution_flow.md §16-17
"""
from __future__ import annotations
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from engine.runner import run_code
from engine.normalizer import normalize

SID = "test_functions"


def test_simple_function_call():
    code = textwrap_dedent("""\
        def add(a, b):
            return a + b

        result = add(2, 3)
    """)
    r = run_code(code)
    evts = normalize(r.events, SID)

    calls = [e for e in evts if e["type"] == "function_call"]
    returns = [e for e in evts if e["type"] == "function_return"]

    assert len(calls) == 1, calls
    assert len(returns) == 1, returns

    call = calls[0]
    assert call["function"] == "add"
    assert call["arguments"] == {
        "a": {"type": "int", "repr": "2"},
        "b": {"type": "int", "repr": "3"},
    }

    ret = returns[0]
    assert ret["function"] == "add"
    assert ret["value"] == {"type": "int", "repr": "5"}
    assert ret["frame_id"] == call["frame_id"]


def test_nested_function_calls():
    code = textwrap_dedent("""\
        def square(x):
            return x * x

        def sum_of_squares(a, b):
            return square(a) + square(b)

        total = sum_of_squares(3, 4)
    """)
    r = run_code(code)
    evts = normalize(r.events, SID)

    calls = [e for e in evts if e["type"] == "function_call"]
    returns = [e for e in evts if e["type"] == "function_return"]

    call_names = [c["function"] for c in calls]
    assert call_names == ["sum_of_squares", "square", "square"], call_names

    return_values = [r["value"]["repr"] for r in returns]
    assert return_values == ["9", "16", "25"], return_values


def textwrap_dedent(s: str) -> str:
    import textwrap
    return textwrap.dedent(s)


if __name__ == "__main__":
    test_simple_function_call()
    test_nested_function_calls()
    print("All function tracking tests passed.")
