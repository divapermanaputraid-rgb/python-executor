"""
Tests for resource limits protection (TASK 15).
SECURITY_SPEC.md §11-16, §27, §35
"""
from __future__ import annotations
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from engine.runner import run_code, MAX_SOURCE_BYTES
from engine.normalizer import normalize

SID = "test_limits"


def test_infinite_loop_timeout():
    code = "while True:\n    pass"
    r = run_code(code, timeout=1.0)
    assert r.timed_out is True
    assert len(r.events) == 1
    assert r.events[0]["type"] == "timeout"
    assert r.events[0]["limit_ms"] == 1000


def test_source_code_size_limit():
    huge_code = "x = 1\n" * (MAX_SOURCE_BYTES // 5)
    try:
        run_code(huge_code)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "exceeds limit" in str(e)


def test_deep_recursion_handling():
    code = textwrap_dedent("""\
        def recurse():
            return recurse()
        recurse()
    """)
    r = run_code(code)
    evts = normalize(r.events, SID)
    types = [e["type"] for e in evts]
    assert "exception" in types
    exc = next(e for e in evts if e["type"] == "exception")
    assert exc["exception"]["type"] == "RecursionError"


def textwrap_dedent(s: str) -> str:
    import textwrap
    return textwrap.dedent(s)


if __name__ == "__main__":
    test_infinite_loop_timeout()
    test_source_code_size_limit()
    test_deep_recursion_handling()
    print("All resource limits tests passed.")
