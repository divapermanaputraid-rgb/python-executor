"""
Tests for filesystem isolation (TASK 16).
SECURITY_SPEC.md §6-7, §39
"""
from __future__ import annotations
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from engine.runner import run_code
from engine.normalizer import normalize

SID = "test_fs"


def test_safe_local_file_write_and_read():
    code = textwrap_dedent("""\
        with open("hello.txt", "w") as f:
            f.write("sandbox test")

        with open("hello.txt", "r") as f:
            content = f.read()

        print(content)
    """)
    r = run_code(code)
    evts = normalize(r.events, SID)
    outs = [e for e in evts if e["type"] == "output"]

    assert len(outs) == 1
    assert outs[0]["value"] == "sandbox test\n"


def test_forbidden_host_file_access_blocked():
    code = textwrap_dedent("""\
        open("/etc/passwd")
    """)
    r = run_code(code)
    evts = normalize(r.events, SID)
    types = [e["type"] for e in evts]

    assert "security_violation" in types, types
    sec_evt = next(e for e in evts if e["type"] == "security_violation")
    assert "filesystem_access_blocked" in sec_evt["reason"]

    assert "exception" in types
    exc_evt = next(e for e in evts if e["type"] == "exception")
    assert exc_evt["exception"]["type"] == "PermissionError"


def textwrap_dedent(s: str) -> str:
    import textwrap
    return textwrap.dedent(s)


if __name__ == "__main__":
    test_safe_local_file_write_and_read()
    test_forbidden_host_file_access_blocked()
    print("All filesystem isolation tests passed.")
