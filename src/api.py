"""FastAPI server for the RAG agent.

Run: uvicorn src.api:app --reload   (from rag_agent_demo/)
"""
from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.agent import RagAgent

app = FastAPI(title="RAG Agent Demo", version="0.1.0")
_agent = RagAgent()


class AskRequest(BaseModel):
    question: str


class ChatRequest(BaseModel):
    question: str
    session_id: str


class ResetRequest(BaseModel):
    session_id: str


class AnswerResponse(BaseModel):
    answer: str


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/ask", response_model=AnswerResponse)
def ask(req: AskRequest) -> AnswerResponse:
    """Stateless single-turn question."""
    try:
        answer = _agent.ask(req.question, session_id=None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return AnswerResponse(answer=answer)


@app.post("/api/chat", response_model=AnswerResponse)
def chat(req: ChatRequest) -> AnswerResponse:
    """Multi-turn chat keyed by session_id."""
    try:
        answer = _agent.ask(req.question, session_id=req.session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return AnswerResponse(answer=answer)


@app.post("/api/reset")
def reset(req: ResetRequest) -> dict:
    _agent.reset(req.session_id)
    return {"status": "ok", "session_id": req.session_id}
