"""
Tests for AI Tutor Endpoint & Socratic Logic (TASK 28).
"""
from __future__ import annotations
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_tutor_explain_endpoint():
    payload = {
        "source_code": "a = 5\nb = 10\nprint(a + b)",
        "events": [],
        "current_snapshot": {
            "status": "RUNNING",
            "current_line": 2,
            "variables": {"a": {"type": "int", "repr": "5"}},
        },
        "user_query": None,
    }

    res = client.post("/api/tutor/explain", json=payload)
    assert res.status_code == 200, res.text
    data = res.json()

    assert "tutor_response" in data
    assert "suggested_question" in data
    assert "line 2" in data["tutor_response"] or "Python" in data["tutor_response"]


if __name__ == "__main__":
    test_tutor_explain_endpoint()
    print("All AI Tutor endpoint tests passed.")
