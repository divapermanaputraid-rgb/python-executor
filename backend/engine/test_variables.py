"""
Tests for variable state tracking (TASK 09).
EVENT_SCHEMA.md §8-9, execution_flow.md §11-12
"""
from __future__ import annotations
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from engine.runner import run_code
from engine.normalizer import normalize

SID = "test_vars"


def test_primitive_types():
    code = "a = 42\nb = 3.14\nc = 'hello'\nd = True\ne = None"
    r = run_code(code)
    evts = normalize(r.events, SID)
    vars_created = {e["variable"]: e["value"] for e in evts if e["type"] == "variable_created"}

    assert vars_created["a"] == {"type": "int", "repr": "42"}
    assert vars_created["b"] == {"type": "float", "repr": "3.14"}
    assert vars_created["c"] == {"type": "str", "repr": "'hello'"}
    assert vars_created["d"] == {"type": "bool", "repr": "True"}
    assert vars_created["e"] == {"type": "NoneType", "repr": "None"}


def test_type_mutation():
    code = "x = 10\nx = 'ten'\nx = [1, 2]"
    r = run_code(code)
    evts = normalize(r.events, SID)
    updates = [e for e in evts if e["type"] == "variable_updated" and e["variable"] == "x"]

    assert len(updates) == 2, updates
    # int → str
    assert updates[0]["previous_value"]["type"] == "int"
    assert updates[0]["new_value"]["type"] == "str"
    # str → list
    assert updates[1]["previous_value"]["type"] == "str"
    assert updates[1]["new_value"]["type"] == "list"


def test_scope_isolation():
    code = textwrap_dedent("""\
        x = 'global'
        def foo():
            x = 'local'
            return x
        foo()
    """)
    r = run_code(code)
    evts = normalize(r.events, SID)
    frame_ids = {e["frame_id"] for e in evts if "frame_id" in e}
    assert len(frame_ids) >= 2, f"expected at least 2 frames (global + foo), got {frame_ids}"


def textwrap_dedent(s: str) -> str:
    import textwrap
    return textwrap.dedent(s)


def test_exception_context_preserves_vars():
    code = "x = 100\ny = '50'\nz = x + y"
    r = run_code(code)
    evts = normalize(r.events, SID)
    created_names = [e["variable"] for e in evts if e["type"] == "variable_created"]

    assert "x" in created_names
    assert "y" in created_names
    assert "z" not in created_names  # failed before z was assigned
    assert any(e["type"] == "exception" for e in evts)


if __name__ == "__main__":
    test_primitive_types()
    test_type_mutation()
    test_scope_isolation()
    test_exception_context_preserves_vars()
    print("All variable state tracking tests passed.")
