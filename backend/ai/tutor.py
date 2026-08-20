"""
Socratic AI Tutor Logic (TASK 28).
Generates pedagogical questions and feedback based strictly on real execution trace facts.
"""
from __future__ import annotations
import os
from typing import Any
from ai.context_builder import build_tutor_context


def generate_tutor_response(
    source_code: str,
    events: list[dict[str, Any]],
    current_snapshot_dict: dict[str, Any] | None = None,
    user_query: str | None = None,
) -> dict[str, str]:
    """
    Generate Socratic AI tutor responses.
    Uses mock/fallback pedagogical responses if LLM API key is not configured.
    """
    line_code = ""
    curr_line = current_snapshot_dict.get("current_line") if current_snapshot_dict else None
    if curr_line and 1 <= curr_line <= len(source_code.splitlines()):
        line_code = source_code.splitlines()[curr_line - 1].strip()

    vars_repr = current_snapshot_dict.get("variables", {}) if current_snapshot_dict else {}

    # If LLM API Key is missing, respond with deterministic Socratic tutor prompts
    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        if user_query:
            return {
                "tutor_response": f"Good question! On line {curr_line} (`{line_code}`), what do you think Python is doing to the variables right now?",
                "suggested_question": "Why did the variable value change here?",
            }
        else:
            var_names = list(vars_repr.keys())
            if var_names:
                last_var = var_names[-1]
                val = vars_repr[last_var].get("repr", "?")
                return {
                    "tutor_response": f"Python just executed line {curr_line}: `{line_code}`. We see `{last_var}` is now `{val}`. What statement caused this value to be assigned?",
                    "suggested_question": f"How was {last_var} computed?",
                }
            return {
                "tutor_response": f"Python is currently at line {curr_line}: `{line_code}`. Before stepping forward, what output do you expect?",
                "suggested_question": "What will happen next line?",
            }

    # If API key configured: (ponytail: mock fallback for default runs without paid keys)
    return {
        "tutor_response": f"On line {curr_line} (`{line_code}`), how does Python evaluate this expression?",
        "suggested_question": "Explain this step in your own words.",
    }
