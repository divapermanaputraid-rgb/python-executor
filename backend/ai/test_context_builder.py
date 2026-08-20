"""
Tests for AI Context Builder (TASK 27).
"""
from __future__ import annotations
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from engine.runner import run_code
from engine.normalizer import normalize
from engine.state_builder import build_snapshots
from ai.context_builder import build_tutor_context


def test_build_tutor_context_fact_accuracy():
    code = "x = 10\ny = 20\ntotal = x + y\nprint(total)"
    r = run_code(code)
    evts = normalize(r.events, "test_ctx")
    snapshots = build_snapshots(evts)

    # Context at line 3 (total = x + y)
    snap_line3 = next(s for s in snapshots if s.current_line == 3)
    ctx = build_tutor_context(code, evts, snap_line3, user_query="What value is total?")

    facts = ctx["execution_facts"]
    assert facts["current_line"] == 3
    assert facts["line_code"] == "total = x + y"
    assert facts["variables"]["x"]["value"] == "10"
    assert facts["variables"]["y"]["value"] == "20"

    assert "NEVER fabricate" in ctx["system_instruction"]


if __name__ == "__main__":
    test_build_tutor_context_fact_accuracy()
    print("All AI Context Builder tests passed.")
