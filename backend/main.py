from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.execution import router as execution_router
from api.tutor import router as tutor_router

app = FastAPI(title="Python Execution Flow Tutor", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(execution_router)
app.include_router(tutor_router)


@app.get("/health")
def health():
    return {"status": "ok"}
