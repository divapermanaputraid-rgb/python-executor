"""
Tests for network and process restrictions (TASK 18).
SECURITY_SPEC.md §8, §10, §39
"""
from __future__ import annotations
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from engine.runner import run_code
from engine.normalizer import normalize

SID = "test_sec"


def test_socket_creation_blocked():
    code = textwrap_dedent("""\
        import socket
        s = socket.socket()
    """)
    r = run_code(code)
    evts = normalize(r.events, SID)
    types = [e["type"] for e in evts]

    assert "security_violation" in types, types
    sec = next(e for e in evts if e["type"] == "security_violation")
    assert sec["reason"] == "network_access_blocked"

    assert "exception" in types
    exc = next(e for e in evts if e["type"] == "exception")
    assert exc["exception"]["type"] == "PermissionError"


def test_subprocess_creation_blocked():
    code = textwrap_dedent("""\
        import subprocess
        subprocess.run(["echo", "hi"])
    """)
    r = run_code(code)
    evts = normalize(r.events, SID)
    types = [e["type"] for e in evts]

    assert "security_violation" in types, types
    sec = next(e for e in evts if e["type"] == "security_violation")
    assert sec["reason"] == "process_creation_blocked"


def test_os_system_blocked():
    code = textwrap_dedent("""\
        import os
        os.system("echo hacked")
    """)
    r = run_code(code)
    evts = normalize(r.events, SID)
    types = [e["type"] for e in evts]

    assert "security_violation" in types, types
    sec = next(e for e in evts if e["type"] == "security_violation")
    assert sec["reason"] == "process_creation_blocked"


def textwrap_dedent(s: str) -> str:
    import textwrap
    return textwrap.dedent(s)


if __name__ == "__main__":
    test_socket_creation_blocked()
    test_subprocess_creation_blocked()
    test_os_system_blocked()
    print("All network and process restriction tests passed.")
