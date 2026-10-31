"""Minimal authenticated FastAPI proxy; Gemini key stays on the server."""
import os
import secrets
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
from rosa_core.gemini import GeminiClient, GeminiError

app = FastAPI(title="ROSA AI Gateway", version="3.0.0")

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=6000)
    language: str = Field(default="auto", pattern="^(auto|en|te|hi)$")
    history: list[dict[str, str]] = Field(default_factory=list, max_length=12)

class ChatResponse(BaseModel):
    reply: str

@app.get("/health")
def health():
    return {"status": "ok", "ai_configured": bool(os.getenv("GEMINI_API_KEY"))}

@app.post("/v1/chat", response_model=ChatResponse)
def chat(body: ChatRequest, authorization: str | None = Header(default=None)):
    expected = os.getenv("ROSA_PROXY_TOKEN", "")
    supplied = (authorization or "").removeprefix("Bearer ").strip()
    if not expected or not supplied or not secrets.compare_digest(expected, supplied):
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        reply = GeminiClient().generate(body.message, body.language, body.history)
        return ChatResponse(reply=reply)
    except GeminiError as exc:
        code = 503 if exc.retryable else 502
        raise HTTPException(status_code=code, detail=exc.message) from exc
