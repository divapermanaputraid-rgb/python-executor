"""
AI Tutor API Endpoint (TASK 28).
POST /api/tutor/explain
"""
from __future__ import annotations
from typing import Any
from fastapi import APIRouter
from pydantic import BaseModel, Field

from ai.tutor import generate_tutor_response

router = APIRouter(prefix="/api/tutor", tags=["tutor"])


class TutorExplainRequest(BaseModel):
    source_code: str = Field(..., description="Python source code")
    events: list[dict[str, Any]] = Field(default_factory=list, description="Trace events")
    current_snapshot: dict[str, Any] | None = Field(default=None, description="ExecutionState snapshot")
    user_query: str | None = Field(default=None, description="Student question or answer")


class TutorExplainResponse(BaseModel):
    tutor_response: str
    suggested_question: str


@router.post("/explain", response_model=TutorExplainResponse)
def explain_step(req: TutorExplainRequest) -> TutorExplainResponse:
    res = generate_tutor_response(
        source_code=req.source_code,
        events=req.events,
        current_snapshot_dict=req.current_snapshot,
        user_query=req.user_query,
    )
    return TutorExplainResponse(**res)
