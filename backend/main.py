"""
FastAPI app — the full backend for the B.Tech AI & Programming FAQ Assistant.

Endpoints:
  GET  /api/health         -> liveness check
  GET  /api/faqs           -> all FAQs (id, category, question)
  GET  /api/categories     -> one sample question per category, for topic chips
  POST /api/ask            -> {question} -> AI-matched answer + updated stats
  GET  /api/stats          -> current asked count / avg score / memory

Run locally:
    pip install -r requirements.txt
    uvicorn main:app --reload --port 8000

No model download is needed — the AI engine (ai_engine.py) uses scikit-learn
TF-IDF + cosine similarity, fitted directly on the FAQ corpus at startup.
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import database
from ai_engine import AiEngine

engine = AiEngine()


@asynccontextmanager
async def lifespan(app: FastAPI):
    conn = database.get_connection()
    database.init_db(conn)
    database.seed_faqs_if_empty(conn)
    faqs = database.get_all_faqs(conn)
    engine.index_faqs(faqs)
    conn.close()
    print(f"[startup] Indexed {len(faqs)} FAQs with TF-IDF vectors (scikit-learn).")
    yield


app = FastAPI(title="B.Tech AI & Programming FAQ Assistant API", lifespan=lifespan)

# Allow the deployed frontend (Vercel) to call this API. Set ALLOWED_ORIGIN
# in your Render environment variables to your Vercel URL(s) once deployed.
# Vercel often serves the same project under more than one URL (e.g. a short
# alias and a longer deployment-specific one) — separate multiple origins
# with commas, e.g.:
#   ALLOWED_ORIGIN=https://circuitbot.vercel.app,https://circuitbot-abc123-team.vercel.app
# Defaults to "*" so local development works out of the box.
ALLOWED_ORIGIN = os.environ.get("ALLOWED_ORIGIN", "*")
if ALLOWED_ORIGIN == "*":
    allow_origins = ["*"]
else:
    allow_origins = [origin.strip() for origin in ALLOWED_ORIGIN.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=500)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/faqs")
def list_faqs():
    conn = database.get_connection()
    try:
        return database.get_all_faqs(conn)
    finally:
        conn.close()


@app.get("/api/categories")
def list_categories():
    conn = database.get_connection()
    try:
        return database.get_categories(conn)
    finally:
        conn.close()


@app.post("/api/ask")
def ask(payload: AskRequest):
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    conn = database.get_connection()
    try:
        faq_id, score = engine.match(question)
        matched = faq_id is not None and engine.is_confident(score)

        database.log_chat(conn, question, faq_id if matched else None, score, matched)
        stats = database.get_stats(conn)

        if matched:
            faq = database.get_faq_by_id(conn, faq_id)
            return {
                "matched": True,
                "answer": faq["answer"],
                "category": faq["category"],
                "score": round(score, 3),
                "stats": stats,
            }
        else:
            suggestions = database.get_random_faqs(conn, 3)
            return {
                "matched": False,
                "message": "I don't have a confident answer for that yet — I'm limited to the topics in my knowledge base. Try rephrasing, or pick one of these:",
                "score": round(score, 3),
                "suggestions": [{"id": s["id"], "question": s["question"]} for s in suggestions],
                "stats": stats,
            }
    finally:
        conn.close()


@app.get("/api/stats")
def stats():
    conn = database.get_connection()
    try:
        return database.get_stats(conn)
    finally:
        conn.close()
