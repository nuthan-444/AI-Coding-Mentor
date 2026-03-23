"""
main.py — Python AI Engine (FastAPI)
AI Coding Practice Mentor
Uses local JSON file for memory storage instead of Hindsight
"""

import os
import json
import httpx
from pathlib import Path
from dotenv import load_dotenv

# Force load .env
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="AI Coding Mentor — Python Engine", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Config ─────────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_URL     = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL   = "llama-3.3-70b-versatile"

# ── Memory file path ───────────────────────────────────────────
MEMORY_FILE = Path(__file__).parent / "memory.json"

print(f"🔑 GROQ_API_KEY loaded: {'✅ YES' if GROQ_API_KEY else '❌ NOT FOUND'}")
print(f"📁 Memory file: {MEMORY_FILE}")


# ══════════════════════════════════════════════════════════════
# REQUEST MODELS
# ══════════════════════════════════════════════════════════════

class AnalyzeRequest(BaseModel):
    code: str
    language: str = "python"
    userId: str

class TestRequest(BaseModel):
    userId: str

class EvaluateRequest(BaseModel):
    userId: str
    question: str
    answer: str
    questionIndex: Optional[int] = 0


# ══════════════════════════════════════════════════════════════
# LOCAL MEMORY SYSTEM (replaces Hindsight)
# Stores data in memory.json file
# ══════════════════════════════════════════════════════════════

def load_all_memories() -> dict:
    """Load all memories from JSON file."""
    if not MEMORY_FILE.exists():
        return {}
    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Memory] Load error: {e}")
        return {}


def save_all_memories(data: dict):
    """Save all memories to JSON file."""
    try:
        with open(MEMORY_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"[Memory] Save error: {e}")


def get_user_memories(user_id: str) -> list:
    """Get all memories for a specific user."""
    all_memories = load_all_memories()
    return all_memories.get(user_id, [])


def store_memory(user_id: str, topic: str, mistake: str, language: str, score: int = 1):
    """
    Store or update a mistake memory for a user.
    If same topic+language exists, increment score.
    """
    all_memories = load_all_memories()

    if user_id not in all_memories:
        all_memories[user_id] = []

    user_memories = all_memories[user_id]

    # Check if this topic+language already exists
    found = False
    for m in user_memories:
        if m.get("topic", "").lower() == topic.lower() and \
           m.get("language", "").lower() == language.lower():
            m["score"] = m.get("score", 1) + 1
            m["mistake"] = mistake  # update with latest mistake
            found = True
            print(f"[Memory] Updated: {topic} ({language}) score={m['score']}")
            break

    if not found:
        user_memories.append({
            "userId":   user_id,
            "topic":    topic,
            "mistake":  mistake,
            "language": language,
            "score":    score
        })
        print(f"[Memory] Stored new: {topic} ({language}) score={score}")

    all_memories[user_id] = user_memories
    save_all_memories(all_memories)


def update_memory_score(user_id: str, topic: str, delta: int):
    """
    Update score of a memory by delta.
    Remove memory if score reaches 0 or below.
    """
    all_memories = load_all_memories()

    if user_id not in all_memories:
        return

    user_memories = all_memories[user_id]
    updated = []

    for m in user_memories:
        if m.get("topic", "").lower() == topic.lower():
            new_score = m.get("score", 1) + delta
            if new_score <= 0:
                print(f"[Memory] Removed (score=0): {topic}")
                continue  # Remove this memory
            m["score"] = new_score
            print(f"[Memory] Score updated: {topic} score={new_score}")
        updated.append(m)

    all_memories[user_id] = updated
    save_all_memories(all_memories)


def format_memories_for_prompt(memories: list) -> str:
    """Format memories as readable string for LLM prompt."""
    if not memories:
        return "No past mistakes on record."
    lines = []
    for m in memories:
        lines.append(
            f"- [{m.get('language','?')}] Topic: {m.get('topic','?')} | "
            f"Mistake: {m.get('mistake','?')} | "
            f"Frequency: {m.get('score', 1)}"
        )
    return "\n".join(lines)


def parse_json_from_llm(text: str) -> dict:
    """Extract JSON from LLM response, handles markdown fences."""
    text = text.strip()
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()
    try:
        return json.loads(text)
    except Exception:
        return {}


# ══════════════════════════════════════════════════════════════
# GROQ LLM HELPER
# ══════════════════════════════════════════════════════════════

async def call_groq(system_prompt: str, user_message: str) -> str:
    """Call Groq LLM and return response text."""
    if not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not configured in .env")

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_message}
        ],
        "max_tokens": 1024,
        "temperature": 0.3
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            res = await client.post(GROQ_URL, json=payload, headers=headers)
            if res.status_code != 200:
                print(f"❌ Groq error {res.status_code}: {res.text}")
                raise HTTPException(status_code=500, detail=f"Groq API error: {res.text}")
            return res.json()["choices"][0]["message"]["content"]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Groq API error: {str(e)}")


# ══════════════════════════════════════════════════════════════
# ENDPOINT: POST /analyze
# ══════════════════════════════════════════════════════════════

@app.post("/analyze")
async def analyze_code(req: AnalyzeRequest):
    """Analyze code, store mistakes in local memory."""

    # 1. Get past mistakes
    memories = get_user_memories(req.userId)
    memory_context = format_memories_for_prompt(memories)

    # 2. Call Groq
    system_prompt = """You are an expert coding mentor.
Analyze the provided code and return ONLY a JSON object with this exact structure:
{
  "errors": ["list of specific errors found"],
  "explanation": "clear explanation of what went wrong and why",
  "mistakes": ["mistake category labels like ZeroDivisionError, OffByOne, SyntaxError"],
  "suggestions": ["list of actionable improvement suggestions"],
  "topic": "main topic of the mistake e.g. Error Handling, Loops, Variables",
  "language": "programming language"
}
Return ONLY valid JSON. No extra text."""

    user_message = f"""Code to analyze ({req.language}):
```
{req.code}
```
Student's past mistakes:
{memory_context}

Analyze this code and return JSON only."""

    raw = await call_groq(system_prompt, user_message)
    parsed = parse_json_from_llm(raw)

    # 3. Store mistakes in local memory
    if parsed.get("topic") and parsed.get("mistakes"):
        for mistake_label in parsed["mistakes"]:
            store_memory(
                user_id=req.userId,
                topic=parsed.get("topic", mistake_label),
                mistake=mistake_label,
                language=parsed.get("language", req.language),
                score=1
            )
    elif parsed.get("topic"):
        # Store even if no specific mistake labels
        store_memory(
            user_id=req.userId,
            topic=parsed.get("topic", "General"),
            mistake=parsed.get("explanation", "Code issue")[:100],
            language=parsed.get("language", req.language),
            score=1
        )

    return {
        "feedback": {
            "errors":      parsed.get("errors", []),
            "explanation": parsed.get("explanation", raw),
            "mistakes":    parsed.get("mistakes", []),
            "suggestions": parsed.get("suggestions", [])
        },
        "memoriesUsed": len(memories)
    }


# ══════════════════════════════════════════════════════════════
# ENDPOINT: POST /generate-test
# ══════════════════════════════════════════════════════════════

@app.post("/generate-test")
async def generate_test(req: TestRequest):
    """Generate practice questions based on user weaknesses."""

    memories = get_user_memories(req.userId)

    if not memories:
        raise HTTPException(
            status_code=400,
            detail="No weakness data found. Please analyze some code first!"
        )

    memory_context = format_memories_for_prompt(memories)

    system_prompt = """You are a coding instructor creating targeted practice questions.
Return ONLY a JSON object:
{
  "questions": [
    "Question 1 text here",
    "Question 2 text here",
    "Question 3 text here",
    "Question 4 text here"
  ]
}
Make questions practical and specific to the weak areas. Return ONLY valid JSON."""

    user_message = f"""Student weakness profile:
{memory_context}

Generate 4 targeted practice questions to help this student improve."""

    raw = await call_groq(system_prompt, user_message)
    parsed = parse_json_from_llm(raw)
    questions = parsed.get("questions", [])

    # Fallback if JSON parsing failed
    if not questions:
        questions = [
            line.strip("- 0123456789.)").strip()
            for line in raw.split("\n")
            if line.strip() and len(line.strip()) > 20
        ][:4]

    return {
        "questions": questions,
        "weaknessCount": len(memories)
    }


# ══════════════════════════════════════════════════════════════
# ENDPOINT: POST /evaluate-test
# ══════════════════════════════════════════════════════════════

@app.post("/evaluate-test")
async def evaluate_test(req: EvaluateRequest):
    """Evaluate student answer and update memory scores."""

    system_prompt = """You are a coding instructor evaluating a student's answer.
Return ONLY a JSON object:
{
  "correct": true or false,
  "explanation": "detailed explanation of the correct answer",
  "topic": "topic being tested"
}
Be educational and encouraging. Return ONLY valid JSON."""

    user_message = f"""Question: {req.question}

Student Answer:
{req.answer if req.answer.strip() else "(no answer provided)"}

Evaluate this answer."""

    raw = await call_groq(system_prompt, user_message)
    parsed = parse_json_from_llm(raw)

    is_correct = parsed.get("correct", False)
    explanation = parsed.get("explanation", raw)
    topic = parsed.get("topic", "general")

    # Update memory score
    if is_correct:
        update_memory_score(req.userId, topic, delta=-1)
    else:
        update_memory_score(req.userId, topic, delta=+1)

    return {
        "correct":     is_correct,
        "explanation": explanation,
        "topic":       topic
    }


# ══════════════════════════════════════════════════════════════
# ENDPOINT: GET /weaknesses
# ══════════════════════════════════════════════════════════════

@app.get("/weaknesses")
async def get_weaknesses(userId: str):
    """Get user weaknesses sorted by score."""
    memories = get_user_memories(userId)
    memories_sorted = sorted(
        memories,
        key=lambda m: m.get("score", 1),
        reverse=True
    )
    return {"weaknesses": memories_sorted}


# ── Health check ───────────────────────────────────────────────
@app.get("/health")
async def health():
    return {
        "status": "ok",
        "groq_configured": bool(GROQ_API_KEY),
        "memory_file": str(MEMORY_FILE),
        "memory_exists": MEMORY_FILE.exists()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)