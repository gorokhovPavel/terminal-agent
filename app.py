from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from bot_flow import process as bot_process
from db import init_db
from agent_runtime import run_agent

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent

# In-memory сессии: session_id -> state dict
sessions: dict[str, dict] = {}

# In-memory история агента: session_id -> list of messages
ai_histories: dict[str, list] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    log.info("DB initialised")
    yield


app = FastAPI(title="GuitarSpace", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


# ── Схемы ────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    session_id: str
    text: str


class ChatResponse(BaseModel):
    text: str
    buttons: list[str] = []
    mode: str = "bot_flow"


# ── Роуты ────────────────────────────────────────────────────

@app.get("/")
async def index():
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    session = sessions.setdefault(req.session_id, {"session_id": req.session_id})
    result = bot_process(session, req.text)
    log.info("bot_flow | session=%s text=%r state=%s", req.session_id, req.text, session.get("state"))
    return ChatResponse(
        text=result["text"],
        buttons=result.get("buttons", []),
        mode=result.get("mode", "bot_flow"),
    )


@app.post("/api/ai", response_model=ChatResponse)
async def ai_consultant(req: ChatRequest):
    log.info("ai_consultant | session=%s text=%r", req.session_id, req.text[:80])

    # Сброс истории при возврате в меню
    if req.text in ("В главное меню", "/start"):
        ai_histories.pop(req.session_id, None)
        sessions.pop(req.session_id, None)
        session = sessions.setdefault(req.session_id, {"session_id": req.session_id})
        result = bot_process(session, "/start")
        return ChatResponse(text=result["text"], buttons=result.get("buttons", []), mode="bot_flow")

    history = ai_histories.setdefault(req.session_id, [])
    result = run_agent(req.text, session_id=req.session_id, conversation_history=history)
    return ChatResponse(
        text=result["text"],
        buttons=result.get("buttons", ["В главное меню"]),
        mode=result.get("mode", "ai_consultant"),
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
