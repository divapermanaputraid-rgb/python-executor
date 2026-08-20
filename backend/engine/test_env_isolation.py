"""
Tests for environment isolation (TASK 17).
SECURITY_SPEC.md §9, §39
"""
from __future__ import annotations
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from engine.runner import run_code
from engine.normalizer import normalize

SID = "test_env"


def test_host_environment_variables_not_leaked():
    # Set fake host secret in parent process
    os.environ["DATABASE_URL"] = "postgresql://user:secret@localhost/db"
    os.environ["API_KEY"] = "super_secret_key_123"

    code = textwrap_dedent("""\
        import os
        has_db = "DATABASE_URL" in os.environ
        has_key = "API_KEY" in os.environ
        sandbox_id = os.environ.get("SANDBOX_ID")
        print(f"has_db={has_db}, has_key={has_key}, sandbox_id={sandbox_id}")
    """)

    r = run_code(code)
    evts = normalize(r.events, SID)
    outs = [e for e in evts if e["type"] == "output"]

    assert len(outs) == 1
    assert outs[0]["value"] == "has_db=False, has_key=False, sandbox_id=isolated_exec\n"


def textwrap_dedent(s: str) -> str:
    import textwrap
    return textwrap.dedent(s)


if __name__ == "__main__":
    test_host_environment_variables_not_leaked()
    print("All environment isolation tests passed.")
