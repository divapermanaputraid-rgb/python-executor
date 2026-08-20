"""
Execution Service API Endpoint (TASK 19 & TASK 20).
POST /api/execute
GET /api/stream/{session_id}
POST /api/execute/stream (SSE stream directly)
"""
from __future__ import annotations
import asyncio
import dataclasses
import json
from typing import Any, AsyncGenerator
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from engine.runner import run_code
from engine.normalizer import normalize
from engine.state_builder import StateReconstructor
from session.session import managed_session

router = APIRouter(prefix="/api", tags=["execution"])


class ExecuteRequest(BaseModel):
    code: str = Field(..., max_length=64 * 1024, description="User Python source code")
    inputs: list[str] | None = Field(default=None, description="Pre-supplied input lines")


class ExecuteResponse(BaseModel):
    session_id: str
    events: list[dict[str, Any]]
    snapshots: list[dict[str, Any]]
    status: str
    stdout: str
    exit_code: int


@router.post("/execute", response_model=ExecuteResponse)
def execute_code(req: ExecuteRequest) -> ExecuteResponse:
    with managed_session(req.code) as sess:
        run_res = run_code(req.code, inputs=req.inputs)
        norm_events = normalize(run_res.events, sess.session_id)
        sess.events = norm_events

        reconstructor = StateReconstructor()
        snapshots = [reconstructor.process_event(evt) for evt in norm_events]

        if run_res.timed_out:
            status_str = "timeout"
        elif any(e.get("type") == "exception" for e in norm_events):
            status_str = "error"
        else:
            status_str = "completed"

        captured_stdout = snapshots[-1].stdout if snapshots else run_res.stdout

        return ExecuteResponse(
            session_id=sess.session_id,
            events=norm_events,
            snapshots=[dataclasses.asdict(s) for s in snapshots],
            status=status_str,
            stdout=captured_stdout,
            exit_code=run_res.exit_code,
        )


@router.post("/execute/stream")
async def execute_stream(req: ExecuteRequest) -> StreamingResponse:
    """Stream normalized events step-by-step as SSE (TASK 20)."""
    async def event_generator() -> AsyncGenerator[str, None]:
        with managed_session(req.code) as sess:
            run_res = run_code(req.code, inputs=req.inputs)
            norm_events = normalize(run_res.events, sess.session_id)
            reconstructor = StateReconstructor()

            for evt in norm_events:
                state = reconstructor.process_event(evt)
                payload = {
                    "event": evt,
                    "snapshot": dataclasses.asdict(state),
                }
                yield f"data: {json.dumps(payload)}\n\n"
                await asyncio.sleep(0.01)

            yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
