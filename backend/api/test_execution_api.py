"""
Tests for Execution Service API & Streaming (TASK 19 & TASK 20).
POST /api/execute
POST /api/execute/stream
"""
from __future__ import annotations
import json
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


def test_execute_stream_sse():
    res = client.post("/api/execute/stream", json={"code": "a = 10\nprint(a)"})
    assert res.status_code == 200, res.text
    assert "text/event-stream" in res.headers["content-type"]

    lines = res.text.strip().split("\n\n")
    data_lines = [l.replace("data: ", "") for l in lines if l.startswith("data: ")]

    assert len(data_lines) >= 2
    assert data_lines[-1] == "[DONE]"

    first_item = json.loads(data_lines[0])
    assert "event" in first_item
    assert "snapshot" in first_item
    assert first_item["event"]["type"] == "program_start"


if __name__ == "__main__":
    test_execute_success()
    test_execute_with_inputs()
    test_execute_with_exception()
    test_execute_stream_sse()
    print("All Execution & Streaming API tests passed.")
