"""
Tests for stdout and stderr output capture (TASK 11).
EVENT_SCHEMA.md §12, execution_flow.md §15
"""
from __future__ import annotations
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from engine.runner import run_code
from engine.normalizer import normalize

SID = "test_output"


def test_stdout_capture():
    code = "print('line 1')\nprint('line 2')"
    r = run_code(code)
    evts = normalize(r.events, SID)
    outs = [e for e in evts if e["type"] == "output"]

    assert len(outs) == 2, outs
    assert outs[0]["stream"] == "stdout"
    assert outs[0]["value"] == "line 1\n"
    assert outs[1]["stream"] == "stdout"
    assert outs[1]["value"] == "line 2\n"


def test_stderr_capture():
    code = textwrap_dedent("""\
        import sys
        sys.stderr.write("warning msg\\n")
        print("normal msg")
    """)
    r = run_code(code)
    evts = normalize(r.events, SID)
    outs = [e for e in evts if e["type"] == "output"]

    assert len(outs) == 2, outs
    stderr_evt = next(e for e in outs if e["stream"] == "stderr")
    stdout_evt = next(e for e in outs if e["stream"] == "stdout")

    assert stderr_evt["value"] == "warning msg\n"
    assert stdout_evt["value"] == "normal msg\n"


def textwrap_dedent(s: str) -> str:
    import textwrap
    return textwrap.dedent(s)


if __name__ == "__main__":
    test_stdout_capture()
    test_stderr_capture()
    print("All output capture tests passed.")
