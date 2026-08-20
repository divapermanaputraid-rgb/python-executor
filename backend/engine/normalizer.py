"""
Event normalizer: converts raw tracer output into clean user-facing events.

execution_flow.md §6: "Layer 2 — Normalized Execution Events"
Frontend and AI should consume normalized events, not raw tracer output.

Normalization rules:
- function_return for <module> is dropped (not meaningful to learner)
- output events with only whitespace newlines are merged into preceding output
- sequence is re-assigned from 1 to preserve ordering after filtering
- session_id and event_id are injected here
"""
from __future__ import annotations
import time
import uuid
from typing import Any


def normalize(
    raw_events: list[dict[str, Any]],
    session_id: str,
) -> list[dict[str, Any]]:
    """
    Filter and enrich raw tracer events into normalized execution events.
    Returns a new list; does not mutate input.
    """
    result: list[dict[str, Any]] = []
    seq = 0

    for evt in raw_events:
        t = evt.get("type")

        # Drop <module> return — not useful for learner
        if t == "function_return" and evt.get("function") == "<module>":
            continue

        # Merge bare newline output into previous output event
        if t == "output" and evt.get("value") == "\n" and result:
            last = result[-1]
            if last.get("type") == "output" and last.get("stream") == evt.get("stream"):
                result[-1] = {**last, "value": last["value"] + "\n"}
                continue

        seq += 1
        result.append({
            **evt,
            "event_id": f"evt_{uuid.uuid4().hex[:8]}",
            "session_id": session_id,
            "sequence": seq,
        })

    return result


# ---------------------------------------------------------------------------
# Self-check
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    from engine.runner import run_code

    SID = "exec_test"

    # --- Normal program ---
    r = run_code("x = 10\nprint(x)")
    events = normalize(r.events, SID)
    types = [e["type"] for e in events]

    assert events[0]["type"] == "program_start", types
    assert events[-1]["type"] == "program_end", types
    assert events[-1].get("status") == "completed", events[-1]

    # All events have session_id and event_id
    for e in events:
        assert e["session_id"] == SID
        assert e["event_id"].startswith("evt_")

    # Sequence is 1-based and contiguous
    seqs = [e["sequence"] for e in events]
    assert seqs == list(range(1, len(events) + 1)), seqs

    # No <module> function_return
    assert not any(
        e["type"] == "function_return" and e.get("function") == "<module>"
        for e in events
    ), "module return leaked"

    # Output merged: print(x) emits "10\n" as single event
    out_events = [e for e in events if e["type"] == "output"]
    assert len(out_events) == 1, f"expected 1 output event, got {out_events}"
    assert out_events[0]["value"] == "10\n", out_events[0]

    # --- Runtime exception ---
    r2 = run_code("x = 10\ny = '5'\nprint(x + y)")
    events2 = normalize(r2.events, SID)
    types2 = [e["type"] for e in events2]

    assert "exception" in types2, types2
    exc = next(e for e in events2 if e["type"] == "exception")
    assert exc["exception"]["type"] == "TypeError"
    assert exc["line"] == 3

    end2 = events2[-1]
    assert end2["type"] == "program_end"
    assert end2["status"] == "error"

    # --- SyntaxError ---
    r3 = run_code("def foo(\n    pass")
    events3 = normalize(r3.events, SID)
    types3 = [e["type"] for e in events3]
    assert "exception" in types3, types3
    exc3 = next(e for e in events3 if e["type"] == "exception")
    assert exc3["exception"]["type"] == "SyntaxError"
    assert events3[-1]["type"] == "program_end"
    assert events3[-1]["status"] == "error"

    print("All normalizer assertions passed.")
    print(f"Normal program events: {[e['type'] for e in events]}")
    print(f"Exception events: {[e['type'] for e in events2]}")
