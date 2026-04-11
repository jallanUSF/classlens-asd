"""
Chat endpoints — conversational Gemma 4 assistant.

Exposes two routes:
  - POST /api/chat          Non-streaming. Returns the full assistant reply
                            in a single JSON payload. Kept for backwards
                            compatibility and simple integrations.
  - POST /api/chat/stream   Streaming via Server-Sent Events. Yields
                            incremental text deltas as the model generates
                            them. Used by the frontend chat panel so the
                            user sees characters appear live.

Both endpoints share the same ChatRequest model, student-context loading,
system prompt, conversation-history flattening, and output sanitization.
"""

import json
import os
import re
from pathlib import Path
from typing import Any, Iterator

from dotenv import load_dotenv
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

load_dotenv()

# Strip any HTML/XML-like tags the model emits. Gemma occasionally leaks
# table fragments (<td>, <tr>) and structural tags from training data.
# We also drop <script>/<style> *blocks* with their contents, since leaving
# their bodies as plain text would leak raw CSS/JS into the chat UI.
_SCRIPT_STYLE_BLOCK_RE = re.compile(
    r"<(script|style)\b[^>]*>.*?</\1\s*>", re.IGNORECASE | re.DOTALL
)
_ANY_TAG_RE = re.compile(r"<[^>]+>")


def _sanitize_model_text(text: str) -> str:
    """Remove HTML tags and dangerous script/style blocks from model output."""
    if not text:
        return text
    text = _SCRIPT_STYLE_BLOCK_RE.sub("", text)
    text = _ANY_TAG_RE.sub("", text)
    return text.strip()

router = APIRouter(tags=["chat"])

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


class ChatRequest(BaseModel):
    message: str
    student_id: str | None = None
    conversation_history: list[dict[str, str]] = []


def _load_student_context(student_id: str) -> str:
    """Build context string from student profile for the system prompt."""
    student_path = DATA_DIR / "students" / f"{student_id}.json"
    if not student_path.exists():
        return ""
    with open(student_path, "r") as f:
        data = json.load(f)

    goals_text = ""
    for g in data.get("iep_goals", []):
        history = g.get("trial_history", [])
        recent_pct = [h.get("pct", 0) for h in history[-3:]] if history else []
        trend = f"Recent: {', '.join(f'{p:.0f}%' for p in recent_pct)}" if recent_pct else "No data yet"
        goals_text += f"  - {g.get('goal_id')}: {g.get('domain', '').replace('_', ' ').title()} — {g.get('description', g.get('title', ''))} | {trend}\n"

    sensory = data.get("sensory_profile", {})
    calming = sensory.get("calming_strategies", [])

    return f"""Current student: {data.get('name', student_id)}
Grade: {data.get('grade', '?')} | ASD Level: {data.get('asd_level', '?')}
Communication: {data.get('communication_level', 'verbal')}
Interests: {', '.join(data.get('interests', []))}
Calming strategies: {', '.join(calming) if calming else 'Not specified'}
IEP Goals:
{goals_text}"""


SYSTEM_PROMPT = """You are the ClassLens Assistant — an expert IEP co-teacher powered by Gemma 4.

PERSONALITY:
- Speak like an experienced special education colleague, warm but professional
- Use teacher vocabulary: "trial data," "prompting level," "present levels," "IEP goal"
- NEVER use AI/ML jargon: no "tokens," "inference," "confidence scores," "model"
- Be proactive — surface insights and suggest next steps
- Always defer to teacher judgment: "Here's what I see — what do you think?"

CAPABILITIES:
- Analyze student work from uploaded photos
- Map work to IEP goals and record trial data
- Detect progress trends, plateaus, and regressions
- Generate lesson plans, social stories, tracking sheets, visual schedules, parent letters, admin reports
- Help onboard new students by extracting goals from IEP documents
- Prepare IEP meeting summaries and talking points

RULES:
- Always personalize materials using the student's interests and communication style
- Reference specific data points when discussing progress (e.g., "7/10 on last 3 sessions")
- When generating materials, ask which goal to target if not obvious
- After generating content, always offer: "Want me to adjust anything?"
- Keep responses concise — teachers are busy

{student_context}"""


def _build_prompt_and_system(req: ChatRequest) -> tuple[str, str]:
    """Shared helper: build (prompt, system) pair from a ChatRequest.

    Used by both the streaming and non-streaming endpoints so they stay in
    lockstep on context, history flattening, and system prompt.
    """
    student_context = ""
    if req.student_id:
        student_context = _load_student_context(req.student_id)

    system = SYSTEM_PROMPT.format(student_context=student_context)

    messages = list(req.conversation_history)
    messages.append({"role": "user", "content": req.message})

    prompt_parts = []
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "assistant":
            prompt_parts.append(f"Assistant: {content}")
        else:
            prompt_parts.append(f"Teacher: {content}")
    return "\n\n".join(prompt_parts), system


def _has_live_api_key() -> bool:
    """True if any live-model provider API key is configured."""
    return bool(
        os.getenv("OPENROUTER_API_KEY")
        or (
            os.getenv("GOOGLE_AI_STUDIO_KEY")
            and os.getenv("GOOGLE_AI_STUDIO_KEY") != "your_api_key_here"
        )
    )


@router.post("/chat")
async def chat(req: ChatRequest) -> dict[str, Any]:
    """
    Send a message to the ClassLens Assistant (non-streaming).

    Returns the full assistant response in one JSON payload. Prefer
    ``/api/chat/stream`` for interactive UIs — this endpoint is kept for
    simple clients, scripts, and the existing test suite.
    """
    prompt, system = _build_prompt_and_system(req)

    try:
        if _has_live_api_key():
            from core.gemma_client import GemmaClient
            client = GemmaClient()
            response_text = client.generate(prompt=prompt, system=system)
        else:
            # Mock response for demo/development
            response_text = _mock_response(req.message, req.student_id)
    except Exception as e:
        response_text = f"I'm having trouble connecting to the model right now. Error: {str(e)}"

    response_text = _sanitize_model_text(response_text)

    return {
        "role": "assistant",
        "content": response_text,
        "student_id": req.student_id,
    }


@router.post("/chat/stream")
async def chat_stream(req: ChatRequest) -> StreamingResponse:
    """
    Send a message to the ClassLens Assistant with Server-Sent Events streaming.

    Yields SSE frames of the form ``data: {"delta": "..."}\\n\\n`` as the
    model produces tokens, a terminal ``data: {"done": true}\\n\\n`` frame,
    and an error frame if something fails mid-stream. The frontend chat
    panel consumes this via ``fetch`` + ``ReadableStream`` so typed text
    appears live rather than in one blob.
    """
    prompt, system = _build_prompt_and_system(req)

    def event_source() -> Iterator[str]:
        try:
            if _has_live_api_key():
                from core.gemma_client import GemmaClient
                client = GemmaClient()
                for chunk in client.generate_stream(prompt=prompt, system=system):
                    cleaned = _sanitize_model_text(chunk)
                    if not cleaned:
                        continue
                    yield f"data: {json.dumps({'delta': cleaned})}\n\n"
            else:
                # No API key — emit the mock response as a single delta so
                # the no-key dev path still looks like a real stream.
                mock = _sanitize_model_text(_mock_response(req.message, req.student_id))
                yield f"data: {json.dumps({'delta': mock})}\n\n"
        except Exception as e:  # pragma: no cover — network/provider errors
            err = f"I'm having trouble connecting to the model right now. Error: {str(e)}"
            yield f"data: {json.dumps({'error': err})}\n\n"
        yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(
        event_source(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


def _mock_response(message: str, student_id: str | None) -> str:
    """Generate a helpful mock response for development without API keys."""
    msg_lower = message.lower()

    if student_id:
        student_path = DATA_DIR / "students" / f"{student_id}.json"
        if student_path.exists():
            with open(student_path, "r") as f:
                data = json.load(f)
            name = data.get("name", student_id)
            goals = data.get("iep_goals", [])
            interests = data.get("interests", [])

            if "lesson plan" in msg_lower or "generate" in msg_lower:
                interest = interests[0] if interests else "their interests"
                return (
                    f"I'd love to generate a lesson plan for {name}! "
                    f"They have {len(goals)} active goals. Which goal should I focus on? "
                    f"I'll incorporate {interest} to keep them engaged."
                )

            if "progress" in msg_lower or "how" in msg_lower:
                goal_summaries = []
                for g in goals[:3]:
                    history = g.get("trial_history", [])
                    if history:
                        recent = history[-1].get("pct", 0)
                        goal_summaries.append(
                            f"**{g.get('goal_id')}** ({g.get('domain', '').replace('_', ' ').title()}): "
                            f"Last session {recent:.0f}%"
                        )
                if goal_summaries:
                    return f"Here's where {name} stands:\n\n" + "\n".join(goal_summaries) + "\n\nWant me to dig deeper into any goal?"
                return f"{name} doesn't have any session data yet. Want to scan some recent work?"

            return f"I'm looking at {name}'s profile — Grade {data.get('grade')}, {len(goals)} active IEP goals. What would you like to work on?"

    if "add" in msg_lower and "student" in msg_lower:
        return "Let's set up a new student! What's their first name and grade?"

    return "I'm here to help! You can ask me about a student's progress, generate materials, scan work, or set up a new student profile."
