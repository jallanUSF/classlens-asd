"""
Chat endpoint — conversational Gemma 4 assistant with streaming.
The assistant has access to all backend services via function calling.
"""

import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

load_dotenv()

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


@router.post("/chat")
async def chat(req: ChatRequest) -> dict[str, Any]:
    """
    Send a message to the ClassLens Assistant.
    Returns the assistant's response (non-streaming for now).

    Streaming via SSE will be added when the frontend chat panel is built.
    """
    student_context = ""
    if req.student_id:
        student_context = _load_student_context(req.student_id)

    system = SYSTEM_PROMPT.format(student_context=student_context)

    # Build conversation for the model
    messages = []
    for msg in req.conversation_history:
        messages.append(msg)
    messages.append({"role": "user", "content": req.message})

    # Format as a single prompt for Gemma (conversation history + current message)
    prompt_parts = []
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "assistant":
            prompt_parts.append(f"Assistant: {content}")
        else:
            prompt_parts.append(f"Teacher: {content}")
    prompt = "\n\n".join(prompt_parts)

    # Get response from model
    try:
        if os.getenv("OPENROUTER_API_KEY") or (
            os.getenv("GOOGLE_AI_STUDIO_KEY")
            and os.getenv("GOOGLE_AI_STUDIO_KEY") != "your_api_key_here"
        ):
            from core.gemma_client import GemmaClient
            client = GemmaClient()
            response_text = client.generate(prompt=prompt, system=system)
        else:
            # Mock response for demo/development
            response_text = _mock_response(req.message, req.student_id)
    except Exception as e:
        response_text = f"I'm having trouble connecting to the model right now. Error: {str(e)}"

    # Strip stray HTML tags that models occasionally emit
    import re
    response_text = re.sub(r"</?(?:td|tr|table|div|span|p|br)\s*/?>", "", response_text).strip()

    return {
        "role": "assistant",
        "content": response_text,
        "student_id": req.student_id,
    }


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
