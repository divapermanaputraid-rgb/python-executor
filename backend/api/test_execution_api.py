"""
Tests for Execution Service API (TASK 19).
POST /api/execute
"""
from __future__ import annotations
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_execute_success():
    res = client.post("/api/execute", json={"code": "x = 5\nprint(x)"})
    assert res.status_code == 200, res.text
    data = res.json()

    assert data["session_id"].startswith("exec_")
    assert data["status"] == "completed"
    assert len(data["events"]) > 0
    assert len(data["snapshots"]) > 0
    assert data["stdout"] == "5\n"


def test_execute_with_inputs():
    res = client.post("/api/execute", json={"code": "name = input()\nprint(f'Hello {name}')", "inputs": ["Alice"]})
    assert res.status_code == 200, res.text
    data = res.json()

    assert data["status"] == "completed"
    assert "Hello Alice\n" in data["stdout"]


def test_execute_with_exception():
    res = client.post("/api/execute", json={"code": "1 / 0"})
    assert res.status_code == 200, res.text
    data = res.json()

    assert data["status"] == "error"
    assert any(e["type"] == "exception" for e in data["events"])


if __name__ == "__main__":
    test_execute_success()
    test_execute_with_inputs()
    test_execute_with_exception()
    print("All Execution API tests passed.")
