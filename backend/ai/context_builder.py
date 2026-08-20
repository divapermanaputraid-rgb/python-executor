"""
AI Context Builder (TASK 27).
Constructs minimal, fact-checked AI context payloads containing real execution facts.

MASTER_CODING.md: "The AI tutor MUST NEVER fabricate execution state."
PRD.md §18: "Construct prompt context from real execution trace."
"""
from __future__ import annotations
from typing import Any
from engine.types import ExecutionState


def build_tutor_context(
    source_code: str,
    events: list[dict[str, Any]],
    current_snapshot: ExecutionState | None = None,
    user_query: str | None = None,
) -> dict[str, Any]:
    """
    Build structured AI context strictly bound to runtime trace facts.
    """
    lines = source_code.splitlines()

    # Active line context
    curr_line_num = current_snapshot.current_line if current_snapshot else None
    curr_line_code = ""
    if curr_line_num and 1 <= curr_line_num <= len(lines):
        curr_line_code = lines[curr_line_num - 1]

    # Compact variables view
    var_summary = {}
    if current_snapshot and current_snapshot.variables:
        for k, v in current_snapshot.variables.items():
            var_summary[k] = {"type": v.type, "value": v.repr}

    # Compact call stack view
    stack_summary = []
    if current_snapshot and current_snapshot.call_stack:
        for frame in current_snapshot.call_stack:
            stack_summary.append({
                "function": frame.function,
                "line": frame.line,
                "scope": frame.scope,
            })

    context_payload = {
        "system_instruction": (
            "You are a Socratic Python Execution Tutor. "
            "Your goal is to guide the student to understand how Python executes line-by-line. "
            "RULES: "
            "1. NEVER fabricate or guess variable values or execution flow — rely ONLY on the provided runtime trace facts. "
            "2. Ask guiding Socratic questions before explaining answers outright. "
            "3. Keep responses concise, supportive, and focused on line-by-line execution logic."
        ),
        "execution_facts": {
            "source_code": source_code,
            "status": current_snapshot.status.value if current_snapshot else "UNKNOWN",
            "current_line": curr_line_num,
            "line_code": curr_line_code,
            "variables": var_summary,
            "call_stack": stack_summary,
            "stdout": current_snapshot.stdout if current_snapshot else "",
            "exception": current_snapshot.exception if current_snapshot else None,
            "total_trace_events": len(events),
        },
        "student_query": user_query or "",
    }

    return context_payload
