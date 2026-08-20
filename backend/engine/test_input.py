"""
Tests for Python input() handling (TASK 10).
EVENT_SCHEMA.md §10-11, execution_flow.md §13-14
"""
from __future__ import annotations
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from engine.runner import run_code
from engine.normalizer import normalize

SID = "test_input"


def test_single_input():
    code = "name = input('Name: ')\nprint('Hello ' + name)"
    r = run_code(code, inputs=["Diva"])
    events = normalize(r.events, SID)
    types = [e["type"] for e in events]

    assert "input_requested" in types, types
    assert "input_received" in types, types

    req = next(e for e in events if e["type"] == "input_requested")
    assert req["prompt"] == "Name: "
    assert req["line"] == 1

    rec = next(e for e in events if e["type"] == "input_received")
    assert rec["value"] == "Diva"
    assert rec["line"] == 1

    var = next(e for e in events if e["type"] == "variable_created" and e["variable"] == "name")
    assert var["value"] == {"type": "str", "repr": "'Diva'"}

    out = next(e for e in events if e["type"] == "output")
    assert out["value"] == "Hello Diva\n"


def test_multiple_inputs_with_type_conversion():
    code = textwrap_dedent("""\
        name = input("Name: ")
        age = int(input("Age: "))
        print(f"{name} is {age}")
    """)
    r = run_code(code, inputs=["Alice", "25"])
    events = normalize(r.events, SID)

    reqs = [e for e in events if e["type"] == "input_requested"]
    recs = [e for e in events if e["type"] == "input_received"]

    assert len(reqs) == 2
    assert len(recs) == 2

    assert reqs[0]["prompt"] == "Name: "
    assert recs[0]["value"] == "Alice"

    assert reqs[1]["prompt"] == "Age: "
    assert recs[1]["value"] == "25"

    age_var = next(e for e in events if e["type"] == "variable_created" and e["variable"] == "age")
    assert age_var["value"] == {"type": "int", "repr": "25"}


def textwrap_dedent(s: str) -> str:
    import textwrap
    return textwrap.dedent(s)


if __name__ == "__main__":
    test_single_input()
    test_multiple_inputs_with_type_conversion()
    print("All input handling tests passed.")
