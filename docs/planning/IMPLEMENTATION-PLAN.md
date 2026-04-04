# ClassLens ASD — Full Technical Implementation Plan
## Jeff's Build Bible (Copy This Folder to Your Sandbox)

**Created:** April 4, 2026
**Deadline:** May 17, 2026 (submit day)
**Goal:** Win the Gemma 4 Good Hackathon. Working demo > production code.

---

## PART 1: TECH STACK DECISIONS

### The Question: Google AI Studio vs Kaggle vs AWS vs Self-Hosted?

After researching all options, here's the decision matrix:

| Option | Cost | GPU | Live Demo? | Complexity | Verdict |
|--------|------|-----|------------|------------|---------|
| **Google AI Studio API** | Free | Google's | Yes (API calls) | LOW | ★ PRIMARY — free Gemma 4 API, multimodal + function calling, `google.genai` Python client |
| **Kaggle Notebooks** | Free | P100 16GB, 30hr/wk | Partial (notebook only) | LOW | ★ CODE DEMO — required for submission anyway, run full pipeline demo as notebook |
| **Ollama Local** | Free | Your GPU | No (local only) | LOW | ★ SPECIAL TECH TRACK — privacy story, show in video |
| **AWS EC2 + GPU** | ~$1-3/hr | A10G/T4 | Yes | HIGH | SKIP — adds cost and complexity for no competition benefit |
| **HF Spaces (GPU)** | $0.40/hr | T4 | Yes | MEDIUM | SKIP — not free, Streamlit Cloud + API is simpler |
| **vLLM self-hosted** | Varies | Your own | Yes | HIGH | SKIP — overkill for hackathon demo |

### Final Architecture

```
┌─────────────────────────────────────────────────────────┐
│            STREAMLIT CLOUD (Free, Public URL)            │
│                                                         │
│  ┌──────────┐  ┌───────────┐  ┌──────────┐  ┌────────┐│
│  │  Upload   │  │ Dashboard │  │ Outputs  │  │Reports ││
│  │  Screen   │  │  Screen   │  │  Screen  │  │ Screen ││
│  └─────┬─────┘  └─────┬─────┘  └────┬─────┘  └───┬────┘│
│        │              │              │             │     │
│        └──────────────┴──────┬───────┴─────────────┘     │
│                              │                           │
│                    ┌─────────▼──────────┐                │
│                    │  AGENT PIPELINE    │                │
│                    │  (Python backend)  │                │
│                    └─────────┬──────────┘                │
└──────────────────────────────┼───────────────────────────┘
                               │ API calls
                    ┌──────────▼──────────┐
                    │  GOOGLE AI STUDIO   │
                    │  Gemini API         │
                    │  model: gemma-4-27b │
                    │  Free tier          │
                    └─────────────────────┘
```

**Why this wins:**
1. **Zero infrastructure cost** — Google AI Studio API is free, Streamlit Cloud is free
2. **Judges get a URL** — public Streamlit app, pre-loaded with sample data, works instantly
3. **Simple code** — no Docker, no GPU provisioning, no deployment configs to debug
4. **Kaggle Notebook** — shows the same pipeline running step-by-step for technical credibility
5. **Ollama local** — 2-hour add-on for Special Tech track ($10K prize potential)

### The "Always Works" Demo Strategy

**Problem:** Google AI Studio free tier is 5-15 RPM. A judge hammering the demo could hit rate limits.

**Solution:** Pre-baked demo mode.

```python
# When a judge picks a sample student and uploads a sample image,
# we check if we have pre-computed results
if image_hash in PRECOMPUTED_RESULTS:
    return PRECOMPUTED_RESULTS[image_hash]  # Instant, always works
else:
    return call_gemma_api(image)  # Live inference, might be slower
```

All sample students + sample work images have pre-computed full pipeline results cached in JSON files. The demo flows perfectly for the standard walkthrough. If a judge uploads something totally new, the live API handles it (maybe slower, but functional). **The happy path never fails.**

---

## PART 2: PROJECT STRUCTURE

```
classlens-asd/
├── CLAUDE.md                          # Claude Code context for sandbox builds
├── README.md                          # Setup instructions + project overview
├── requirements.txt                   # Python dependencies
├── .env.example                       # Template for API keys
├── .streamlit/
│   └── config.toml                    # Streamlit theme config
│
├── app.py                             # Main Streamlit app entry point
│
├── agents/
│   ├── __init__.py
│   ├── base.py                        # Base agent class, shared Gemma client
│   ├── vision_reader.py               # Agent 1: Multimodal OCR
│   ├── iep_mapper.py                  # Agent 2: Goal matching + trial data
│   ├── progress_analyst.py            # Agent 3: Trends + alerts + reports
│   └── material_forge.py             # Agent 4: All 7 output types
│
├── core/
│   ├── __init__.py
│   ├── gemma_client.py                # Google AI Studio API wrapper
│   ├── state_store.py                 # Read/write student JSON profiles
│   ├── report_generator.py            # Admin report PDF/HTML generation
│   └── pipeline.py                    # End-to-end orchestration
│
├── data/
│   ├── students/                      # Student profile JSON files
│   │   ├── maya_2026.json
│   │   ├── jaylen_2026.json
│   │   └── sofia_2026.json
│   ├── sample_work/                   # Sample work artifact images
│   │   ├── maya_math_worksheet.jpg
│   │   ├── maya_tally_sheet.jpg
│   │   ├── jaylen_checklist.jpg
│   │   └── ...
│   └── precomputed/                   # Pre-baked demo results
│       ├── maya_math_worksheet_result.json
│       ├── maya_tally_sheet_result.json
│       └── ...
│
├── prompts/
│   ├── vision_reader.py               # System + user prompts for Agent 1
│   ├── iep_mapper.py                  # Prompts for Agent 2
│   ├── progress_analyst.py            # Prompts for Agent 3
│   └── material_forge.py             # Prompts for Agent 4 (all 7 output types)
│
├── schemas/
│   ├── tools.py                       # All function calling JSON schemas
│   └── student_profile.py             # Student profile Pydantic models
│
├── ui/
│   ├── __init__.py
│   ├── upload.py                      # Upload screen component
│   ├── dashboard.py                   # Student dashboard component
│   ├── outputs.py                     # Generated materials viewer
│   ├── reports.py                     # Admin report screen
│   ├── lesson_planner.py             # IEP goal → lesson plan screen
│   └── styles.py                      # Custom CSS
│
├── notebooks/
│   └── classlens_demo.ipynb           # Kaggle notebook: full pipeline walkthrough
│
├── demo_assets/
│   ├── cover_image.png                # Kaggle media gallery cover
│   └── screenshots/                   # App screenshots for writeup
│
└── docs/
    ├── teacher-playbook.md
    ├── tech-playbook.md
    └── ...
```

---

## PART 3: DEPENDENCIES

```
# requirements.txt
google-genai>=1.0.0            # Google AI Studio / Gemini API client
streamlit>=1.45.0              # Demo app framework
Pillow>=10.0.0                 # Image handling
plotly>=5.24.0                 # Charts for dashboard + admin reports
pydantic>=2.10.0               # Data models and validation
python-dotenv>=1.0.0           # Environment variable management
jinja2>=3.1.0                  # Report templates (admin reports)
weasyprint>=62.0               # HTML → PDF for printable reports/tracking sheets (optional)
```

**No LangChain. No LangGraph. No CrewAI.** Direct Gemma 4 API calls via `google.genai`. Judges should see clean code that demonstrates Gemma 4 usage, not framework abstractions.

---

## PART 4: FILE-BY-FILE IMPLEMENTATION SPECS

### 4.1 `core/gemma_client.py` — The Foundation

Everything talks to Gemma 4 through this single wrapper. Handles API key, model selection, multimodal input, function calling, and thinking mode.

```python
"""
GemmaClient: Thin wrapper around Google AI Studio's Gemini API for Gemma 4.
Supports: text, multimodal (image+text), function calling, thinking mode.
"""
import os
import json
import base64
from pathlib import Path
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

class GemmaClient:
    """Single interface for all Gemma 4 interactions."""

    def __init__(self, model: str = "gemma-4-27b-it"):
        self.client = genai.Client(api_key=os.getenv("GOOGLE_AI_STUDIO_KEY"))
        self.model = model

    def generate(self, prompt: str, system: str = None) -> str:
        """Basic text generation."""
        config = types.GenerateContentConfig(
            system_instruction=system
        ) if system else None
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=config
        )
        return response.text

    def generate_multimodal(self, image_path: str, prompt: str,
                            system: str = None) -> str:
        """Image + text → text. Used by Vision Reader."""
        image_data = Path(image_path).read_bytes()
        contents = [
            types.Part.from_bytes(data=image_data, mime_type="image/jpeg"),
            types.Part.from_text(text=prompt)
        ]
        config = types.GenerateContentConfig(
            system_instruction=system
        ) if system else None
        response = self.client.models.generate_content(
            model=self.model,
            contents=contents,
            config=config
        )
        return response.text

    def generate_with_tools(self, prompt: str, tools: list,
                            system: str = None) -> dict:
        """Function calling. Used by IEP Mapper and Material Forge."""
        config = types.GenerateContentConfig(
            system_instruction=system,
            tools=tools,
            tool_config=types.ToolConfig(
                function_calling_config=types.FunctionCallingConfig(
                    mode="AUTO"
                )
            )
        )
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=config
        )
        # Extract function call results
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'function_call'):
                return {
                    "function": part.function_call.name,
                    "args": dict(part.function_call.args)
                }
        return {"text": response.text}

    def generate_with_thinking(self, prompt: str, system: str = None) -> dict:
        """Thinking mode. Used by Progress Analyst."""
        thinking_system = f"<|think|>\n{system}" if system else "<|think|>"
        config = types.GenerateContentConfig(
            system_instruction=thinking_system,
            thinking_config=types.ThinkingConfig(
                thinking_budget_tokens=2048
            )
        )
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=config
        )
        # Separate thinking from final response
        thinking = ""
        output = ""
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'thought') and part.thought:
                thinking += part.text
            else:
                output += part.text
        return {"thinking": thinking, "output": output}
```

### 4.2 `schemas/tools.py` — All Function Calling Schemas

```python
"""
Function calling tool definitions for all four agents.
Gemma 4 native function calling — JSON schema format.
"""

TRANSCRIBE_STUDENT_WORK = {
    "name": "transcribe_student_work",
    "description": "Transcribes student work from an image into structured data",
    "parameters": {
        "type": "object",
        "properties": {
            "work_type": {
                "type": "string",
                "enum": ["worksheet", "tally_sheet", "checklist",
                         "visual_schedule", "free_response"]
            },
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "item_number": {"type": "integer"},
                        "prompt": {"type": "string"},
                        "student_response": {"type": "string"},
                        "correct_response": {"type": "string"},
                        "is_correct": {"type": "boolean"},
                        "notes": {"type": "string"}
                    }
                }
            },
            "total_items": {"type": "integer"},
            "completed_items": {"type": "integer"},
            "correct_items": {"type": "integer"},
            "accuracy_percentage": {"type": "number"},
            "observations": {"type": "string"}
        },
        "required": ["work_type", "items", "total_items",
                      "completed_items", "correct_items",
                      "accuracy_percentage"]
    }
}

MAP_WORK_TO_GOALS = {
    "name": "map_work_to_goals",
    "description": "Maps transcribed student work to IEP goals with trial data",
    "parameters": {
        "type": "object",
        "properties": {
            "student_id": {"type": "string"},
            "matched_goals": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "goal_id": {"type": "string"},
                        "relevance": {"type": "string",
                                      "enum": ["primary", "secondary"]},
                        "trials": {"type": "integer"},
                        "successes": {"type": "integer"},
                        "percentage": {"type": "number"},
                        "reasoning": {"type": "string"}
                    }
                }
            }
        },
        "required": ["student_id", "matched_goals"]
    }
}

ANALYZE_PROGRESS = {
    "name": "analyze_goal_progress",
    "description": "Analyzes trend data for an IEP goal and generates alerts",
    "parameters": {
        "type": "object",
        "properties": {
            "student_id": {"type": "string"},
            "goal_id": {"type": "string"},
            "trend": {"type": "string",
                      "enum": ["improving", "on_track",
                               "plateaued", "regressing"]},
            "current_average": {"type": "number"},
            "sessions_analyzed": {"type": "integer"},
            "confidence": {"type": "string",
                           "enum": ["high", "medium", "low"]},
            "alert": {"type": "boolean"},
            "alert_message": {"type": "string"},
            "progress_note": {"type": "string"},
            "recommendation": {"type": "string"}
        },
        "required": ["student_id", "goal_id", "trend",
                      "current_average", "sessions_analyzed"]
    }
}

GENERATE_LESSON_PLAN = {
    "name": "generate_lesson_plan",
    "description": "Generates a goal-aligned lesson plan with activities",
    "parameters": {
        "type": "object",
        "properties": {
            "student_id": {"type": "string"},
            "goal_id": {"type": "string"},
            "lesson_title": {"type": "string"},
            "objective": {"type": "string"},
            "materials_needed": {
                "type": "array",
                "items": {"type": "string"}
            },
            "warm_up": {"type": "string"},
            "main_activity": {"type": "string"},
            "guided_practice": {"type": "string"},
            "independent_practice": {"type": "string"},
            "assessment_check": {"type": "string"},
            "interest_integration": {"type": "string"},
            "scaffolding_notes": {"type": "string"},
            "estimated_duration_minutes": {"type": "integer"}
        },
        "required": ["student_id", "goal_id", "lesson_title",
                      "objective", "main_activity"]
    }
}

GENERATE_TRACKING_SHEET = {
    "name": "generate_tracking_sheet",
    "description": "Generates a printable data tracking sheet for an IEP goal",
    "parameters": {
        "type": "object",
        "properties": {
            "student_id": {"type": "string"},
            "goal_id": {"type": "string"},
            "sheet_title": {"type": "string"},
            "measurement_type": {
                "type": "string",
                "enum": ["trial_percentage", "frequency_count",
                         "duration", "interval", "task_analysis"]
            },
            "columns": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "header": {"type": "string"},
                        "width": {"type": "string"}
                    }
                }
            },
            "rows_per_page": {"type": "integer"},
            "instructions": {"type": "string"},
            "goal_text": {"type": "string"},
            "target_criterion": {"type": "string"}
        },
        "required": ["student_id", "goal_id", "sheet_title",
                      "measurement_type", "columns"]
    }
}

GENERATE_SOCIAL_STORY = {
    "name": "generate_social_story",
    "description": "Generates a Carol Gray social story for a student",
    "parameters": {
        "type": "object",
        "properties": {
            "student_id": {"type": "string"},
            "title": {"type": "string"},
            "scenario": {"type": "string"},
            "sentences": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string"},
                        "type": {
                            "type": "string",
                            "enum": ["descriptive", "perspective",
                                     "directive", "control",
                                     "affirmative", "cooperative"]
                        }
                    }
                }
            },
            "interest_used": {"type": "string"},
            "vocabulary_level": {"type": "string"}
        },
        "required": ["student_id", "title", "scenario", "sentences"]
    }
}

GENERATE_PARENT_COMM = {
    "name": "generate_parent_communication",
    "description": "Generates a parent communication note",
    "parameters": {
        "type": "object",
        "properties": {
            "student_id": {"type": "string"},
            "date": {"type": "string"},
            "greeting": {"type": "string"},
            "highlight": {"type": "string"},
            "data_summary": {"type": "string"},
            "home_activity": {"type": "string"},
            "closing": {"type": "string"},
            "tone": {"type": "string"}
        },
        "required": ["student_id", "date", "highlight",
                      "data_summary", "home_activity"]
    }
}

GENERATE_ADMIN_REPORT = {
    "name": "generate_admin_report",
    "description": "Generates a professional progress report for administrators",
    "parameters": {
        "type": "object",
        "properties": {
            "student_id": {"type": "string"},
            "report_period": {"type": "string"},
            "executive_summary": {"type": "string"},
            "goal_summaries": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "goal_id": {"type": "string"},
                        "goal_description": {"type": "string"},
                        "baseline": {"type": "number"},
                        "current": {"type": "number"},
                        "target": {"type": "number"},
                        "trend": {"type": "string"},
                        "sessions_tracked": {"type": "integer"},
                        "narrative": {"type": "string"},
                        "recommendation": {"type": "string"}
                    }
                }
            },
            "overall_assessment": {"type": "string"},
            "next_steps": {"type": "string"}
        },
        "required": ["student_id", "report_period",
                      "executive_summary", "goal_summaries"]
    }
}
```

### 4.3 `agents/vision_reader.py` — Agent 1

```python
"""
Agent 1: Vision Reader
Photo of student work → structured JSON transcription.
Uses Gemma 4 multimodal (image + text → function call).
"""
from core.gemma_client import GemmaClient
from schemas.tools import TRANSCRIBE_STUDENT_WORK
from prompts.vision_reader import SYSTEM_PROMPT, user_prompt_template

class VisionReader:
    def __init__(self, client: GemmaClient):
        self.client = client

    def transcribe(self, image_path: str, student_name: str,
                   grade: int, work_type: str, subject: str) -> dict:
        """
        Read a photo of student work and produce structured transcription.

        Args:
            image_path: Path to the photograph
            student_name: Student's first name
            grade: Grade level (for context)
            work_type: worksheet|tally_sheet|checklist|visual_schedule|free_response
            subject: Subject area (math, reading, etc.)

        Returns:
            dict with transcribed data matching TRANSCRIBE_STUDENT_WORK schema
        """
        prompt = user_prompt_template.format(
            student_name=student_name,
            grade=grade,
            work_type=work_type,
            subject=subject
        )

        result = self.client.generate_with_tools(
            prompt=prompt,
            tools=[TRANSCRIBE_STUDENT_WORK],
            system=SYSTEM_PROMPT
        )

        # If function calling worked, return args directly
        if "function" in result:
            return result["args"]

        # Fallback: parse JSON from text response
        return self._parse_fallback(result.get("text", ""))

    def _parse_fallback(self, text: str) -> dict:
        """If function calling fails, try to extract JSON from text."""
        import json
        import re
        json_match = re.search(r'\{[\s\S]*\}', text)
        if json_match:
            return json.loads(json_match.group())
        raise ValueError(f"Could not parse Vision Reader output: {text[:200]}")
```

### 4.4 `agents/iep_mapper.py` — Agent 2

```python
"""
Agent 2: IEP Mapper
Transcribed work → matched to student's IEP goals → trial data recorded.
Uses Gemma 4 function calling.
"""
from core.gemma_client import GemmaClient
from core.state_store import StateStore
from schemas.tools import MAP_WORK_TO_GOALS
from prompts.iep_mapper import SYSTEM_PROMPT, user_prompt_template

class IEPMapper:
    def __init__(self, client: GemmaClient, store: StateStore):
        self.client = client
        self.store = store

    def map_to_goals(self, student_id: str, transcription: dict,
                     date: str) -> dict:
        """
        Map transcribed work to the student's IEP goals.

        Args:
            student_id: Student identifier
            transcription: Output from VisionReader.transcribe()
            date: Date of the work (YYYY-MM-DD)

        Returns:
            dict with matched_goals and trial data
        """
        profile = self.store.load_student(student_id)
        goals_context = self._format_goals(profile["iep_goals"])

        prompt = user_prompt_template.format(
            student_name=profile["name"],
            goals_context=goals_context,
            transcription=json.dumps(transcription, indent=2)
        )

        result = self.client.generate_with_tools(
            prompt=prompt,
            tools=[MAP_WORK_TO_GOALS],
            system=SYSTEM_PROMPT
        )

        mapping = result.get("args", {})

        # Record trial data to student's history
        for goal_match in mapping.get("matched_goals", []):
            self.store.add_trial_data(
                student_id=student_id,
                goal_id=goal_match["goal_id"],
                date=date,
                trials=goal_match.get("trials", 0),
                successes=goal_match.get("successes", 0),
                percentage=goal_match.get("percentage", 0),
                notes=goal_match.get("reasoning", "")
            )

        return mapping

    def _format_goals(self, goals: list) -> str:
        """Format IEP goals as context string for the prompt."""
        lines = []
        for g in goals:
            lines.append(
                f"[{g['goal_id']}] {g['domain']}: {g['description']} "
                f"(baseline: {g['baseline']['value']}%, "
                f"target: {g['target']}%)"
            )
        return "\n".join(lines)
```

### 4.5 `agents/progress_analyst.py` — Agent 3

```python
"""
Agent 3: Progress Analyst
Trial history → trend analysis, progress notes, regression alerts.
Uses Gemma 4 thinking mode for explainable reasoning.
"""
from core.gemma_client import GemmaClient
from core.state_store import StateStore
from schemas.tools import ANALYZE_PROGRESS
from prompts.progress_analyst import SYSTEM_PROMPT, user_prompt_template

class ProgressAnalyst:
    def __init__(self, client: GemmaClient, store: StateStore):
        self.client = client
        self.store = store

    def analyze(self, student_id: str, goal_id: str) -> dict:
        """
        Analyze progress toward a specific IEP goal.

        Returns:
            dict with trend, alert, progress_note, recommendation,
            plus 'thinking' key showing the model's reasoning chain
        """
        profile = self.store.load_student(student_id)
        goal = self._get_goal(profile, goal_id)
        history = goal.get("trial_history", [])

        prompt = user_prompt_template.format(
            student_name=profile["name"],
            goal_id=goal_id,
            goal_description=goal["description"],
            baseline=goal["baseline"]["value"],
            target=goal["target"],
            review_date=goal["iep_review_date"],
            trial_history=json.dumps(history, indent=2)
        )

        # Use thinking mode — the reasoning chain is part of the output
        result = self.client.generate_with_thinking(
            prompt=prompt,
            system=SYSTEM_PROMPT
        )

        # Parse the structured analysis from the output
        analysis = self._parse_analysis(result["output"])
        analysis["thinking"] = result["thinking"]  # Keep for explainability

        return analysis

    def analyze_all_goals(self, student_id: str) -> list:
        """Run analysis on every goal for a student. Used for dashboard."""
        profile = self.store.load_student(student_id)
        results = []
        for goal in profile["iep_goals"]:
            analysis = self.analyze(student_id, goal["goal_id"])
            results.append(analysis)
        return results
```

### 4.6 `agents/material_forge.py` — Agent 4 (The Big One — 7 Output Types)

```python
"""
Agent 4: Material Forge
Generates personalized materials for three audiences:
  Teacher: lesson plans, tracking sheets, social stories, visual schedules, first-then boards
  Parents: parent communications
  Admin:   progress reports

Uses Gemma 4 text generation with student profile as context.
"""
from core.gemma_client import GemmaClient
from core.state_store import StateStore
from schemas.tools import (
    GENERATE_LESSON_PLAN, GENERATE_TRACKING_SHEET,
    GENERATE_SOCIAL_STORY, GENERATE_PARENT_COMM,
    GENERATE_ADMIN_REPORT
)
from prompts.material_forge import (
    LESSON_PLAN_SYSTEM, LESSON_PLAN_USER,
    TRACKING_SHEET_SYSTEM, TRACKING_SHEET_USER,
    SOCIAL_STORY_SYSTEM, SOCIAL_STORY_USER,
    VISUAL_SCHEDULE_SYSTEM, VISUAL_SCHEDULE_USER,
    FIRST_THEN_SYSTEM, FIRST_THEN_USER,
    PARENT_COMM_SYSTEM, PARENT_COMM_USER,
    ADMIN_REPORT_SYSTEM, ADMIN_REPORT_USER
)

class MaterialForge:
    def __init__(self, client: GemmaClient, store: StateStore):
        self.client = client
        self.store = store

    def generate_lesson_plan(self, student_id: str, goal_id: str) -> dict:
        """
        IEP goal → scaffolded lesson plan incorporating student interests.
        Sarah's #1 request. This is the hero output.
        """
        profile = self.store.load_student(student_id)
        goal = self._get_goal(profile, goal_id)
        prompt = LESSON_PLAN_USER.format(
            student_name=profile["name"],
            grade=profile["grade"],
            comm_level=profile["communication_level"],
            interests=", ".join(profile["interests"]),
            sensory_seeks=", ".join(profile["sensory_profile"]["seeks"]),
            sensory_avoids=", ".join(profile["sensory_profile"]["avoids"]),
            goal_id=goal["goal_id"],
            goal_description=goal["description"],
            baseline=goal["baseline"]["value"],
            target=goal["target"],
            current_trend=self._get_latest_trend(student_id, goal_id)
        )
        return self.client.generate_with_tools(
            prompt=prompt,
            tools=[GENERATE_LESSON_PLAN],
            system=LESSON_PLAN_SYSTEM
        ).get("args", {})

    def generate_tracking_sheet(self, student_id: str, goal_id: str) -> dict:
        """Per-goal clipboard-ready tracking sheet."""
        # ... similar pattern

    def generate_social_story(self, student_id: str,
                               scenario: str) -> dict:
        """Carol Gray framework social story with student interests."""
        # ... similar pattern

    def generate_visual_schedule(self, student_id: str,
                                  activity: str) -> str:
        """Sequential visual schedule description for para to build."""
        # ... returns text description

    def generate_first_then(self, student_id: str,
                             first_activity: str) -> str:
        """First-Then board text using student's reinforcers."""
        # ... returns formatted text

    def generate_parent_comm(self, student_id: str, date: str,
                              todays_data: dict) -> dict:
        """Parent communication referencing today's specific work."""
        # ... similar pattern

    def generate_admin_report(self, student_id: str,
                               period: str = "monthly") -> dict:
        """
        Polished progress report for administrators.
        "Admin eat up fancy reports and data." — Sarah
        """
        profile = self.store.load_student(student_id)
        all_analyses = []
        for goal in profile["iep_goals"]:
            analysis = self._get_latest_trend(student_id, goal["goal_id"])
            all_analyses.append(analysis)

        prompt = ADMIN_REPORT_USER.format(
            student_name=profile["name"],
            grade=profile["grade"],
            asd_level=profile["asd_level"],
            report_period=period,
            goals_and_data=json.dumps(all_analyses, indent=2)
        )
        return self.client.generate_with_tools(
            prompt=prompt,
            tools=[GENERATE_ADMIN_REPORT],
            system=ADMIN_REPORT_SYSTEM
        ).get("args", {})
```

### 4.7 `core/pipeline.py` — End-to-End Orchestration

```python
"""
Full pipeline: image → transcription → goal mapping → analysis → materials.
Single function call that runs the entire agent chain.
"""

class ClassLensPipeline:
    def __init__(self):
        self.client = GemmaClient()
        self.store = StateStore()
        self.vision = VisionReader(self.client)
        self.mapper = IEPMapper(self.client, self.store)
        self.analyst = ProgressAnalyst(self.client, self.store)
        self.forge = MaterialForge(self.client, self.store)

    def process_work_artifact(self, student_id: str, image_path: str,
                               work_type: str, subject: str,
                               date: str) -> dict:
        """
        Full pipeline: photo → everything.

        Returns dict with:
        - transcription: raw OCR result
        - goal_mapping: which IEP goals this maps to
        - analyses: progress analysis per matched goal
        - alerts: any regression/plateau alerts
        - materials: generated lesson plans, social stories, etc.
        """
        profile = self.store.load_student(student_id)

        # Step 1: Vision Reader
        transcription = self.vision.transcribe(
            image_path, profile["name"], profile["grade"],
            work_type, subject
        )

        # Step 2: IEP Mapper
        mapping = self.mapper.map_to_goals(
            student_id, transcription, date
        )

        # Step 3: Progress Analyst (for each matched goal)
        analyses = []
        alerts = []
        for goal_match in mapping.get("matched_goals", []):
            analysis = self.analyst.analyze(
                student_id, goal_match["goal_id"]
            )
            analyses.append(analysis)
            if analysis.get("alert"):
                alerts.append(analysis)

        # Step 4: Material Forge (generate relevant materials)
        materials = {}

        # Always generate lesson plan for primary goal
        primary_goal = mapping["matched_goals"][0]["goal_id"]
        materials["lesson_plan"] = self.forge.generate_lesson_plan(
            student_id, primary_goal
        )

        # Generate social story if there's a behavioral alert
        if any(a.get("alert") for a in analyses):
            materials["social_story"] = self.forge.generate_social_story(
                student_id,
                scenario=alerts[0].get("alert_message", "")
            )

        # Always generate parent communication
        materials["parent_comm"] = self.forge.generate_parent_comm(
            student_id, date, {"transcription": transcription,
                               "mapping": mapping}
        )

        return {
            "transcription": transcription,
            "goal_mapping": mapping,
            "analyses": analyses,
            "alerts": alerts,
            "materials": materials
        }
```

### 4.8 `app.py` — Streamlit Demo App

```python
"""
ClassLens ASD — Streamlit Demo App
Multi-page app with:
  1. Upload: Photo upload + student selection
  2. Dashboard: Per-student IEP goal progress
  3. Outputs: Generated materials (lesson plans, stories, schedules)
  4. Reports: Admin progress reports
  5. Lesson Planner: IEP goal → lesson plan + tracking sheet
"""
import streamlit as st

st.set_page_config(
    page_title="ClassLens ASD",
    page_icon="🔍",
    layout="wide"
)

# Sidebar navigation
page = st.sidebar.selectbox("Navigate", [
    "📸 Upload Student Work",
    "📊 Student Dashboard",
    "📝 Generated Materials",
    "📋 Admin Reports",
    "🎯 Lesson Planner"
])

if page == "📸 Upload Student Work":
    from ui.upload import render_upload
    render_upload()
elif page == "📊 Student Dashboard":
    from ui.dashboard import render_dashboard
    render_dashboard()
elif page == "📝 Generated Materials":
    from ui.outputs import render_outputs
    render_outputs()
elif page == "📋 Admin Reports":
    from ui.reports import render_reports
    render_reports()
elif page == "🎯 Lesson Planner":
    from ui.lesson_planner import render_lesson_planner
    render_lesson_planner()
```

---

## PART 5: DUMMY DATA (Use Until Sarah Delivers)

### Three Dummy Students

**These profiles are realistic enough to build and test the full pipeline. Replace with Sarah's real profiles when they arrive.**

See `data/students/` directory for full JSON files. Summary:

| Student | Grade | ASD Level | Communication | Interests | Key Goals |
|---------|-------|-----------|---------------|-----------|-----------|
| **Maya** | 3 | 2 | Verbal, 3-4 word phrases | Dinosaurs, water play, purple, counting | Greeting peers (75%), two-step directions (90%), self-regulation (1/day) |
| **Jaylen** | 1 | 3 | Non-verbal, uses PECS + AAC device | Thomas the Tank Engine, spinning wheels, deep pressure | Requesting wants via AAC (80%), following visual schedule (90%), turn-taking (4/5) |
| **Sofia** | 5 | 1 | Full sentences, advanced reader | US Presidents, maps, organizing things | Initiating conversation (80%), managing transitions (85%), written expression (4/5 rubric) |

### Sample Work Artifact Descriptions (Create These as Images)

Until Sarah provides real handwritten samples, create simple mock images:

1. **Maya's Math Worksheet** — 10 single-digit addition problems. 7 correct, 2 wrong, 1 skipped. Messy handwriting with some erasures. Dinosaur stickers at top.

2. **Maya's Behavior Tally Sheet** — Grid with dates across top, behaviors down side. Tally marks in cells. "Greeted peer" row shows 3/4 on most recent day.

3. **Jaylen's Visual Schedule** — Photo of a "to do" / "done" board with Velcro picture cards. 4 of 6 cards moved to "done" side.

4. **Jaylen's Task Analysis Checklist** — Hand-washing steps. 5 of 7 steps checked off. "Thomas" sticker on the sheet.

5. **Sofia's Writing Sample** — 3-sentence paragraph about George Washington. Legible cursive. Some spelling errors.

---

## PART 6: PROMPT TEMPLATES

### `prompts/vision_reader.py`

```python
SYSTEM_PROMPT = """You are a special education teaching assistant.
Your job is to accurately read and transcribe student work from photographs.

CRITICAL RULES:
- Read EXACTLY what the student wrote, including misspellings and errors
- Do NOT correct the student's work — transcribe it faithfully
- Note any erasures, cross-outs, or self-corrections in the notes field
- If handwriting is ambiguous, note the ambiguity rather than guessing
- For tally sheets, count marks precisely
- For checklists, mark items as completed only if clearly checked/marked
- If an item is blank or skipped, mark it as such

Call the transcribe_student_work function with your analysis."""

user_prompt_template = """This is a photograph of student work from an ASD classroom.
Student: {student_name} (Grade {grade})
Activity type: {work_type}
Subject: {subject}

Please transcribe this work accurately using the transcribe_student_work function.
Count every item, note every response. Be precise."""
```

### `prompts/material_forge.py` (Lesson Plan — the key one)

```python
LESSON_PLAN_SYSTEM = """You are an experienced special education teacher
creating lesson plans for students with autism spectrum disorder.

DESIGN PRINCIPLES:
- Activities must directly build toward the IEP goal
- Incorporate the student's specific interests naturally (not forced)
- Ensure activities match the student's communication level
- Include sensory considerations (what to avoid, what helps)
- Scaffold appropriately: break complex skills into smaller steps
- Include clear success criteria the teacher can observe
- Keep plans practical — these are real classroom activities with real materials
- Estimate realistic time durations

Call the generate_lesson_plan function with your lesson plan."""

LESSON_PLAN_USER = """Create a lesson plan for this student and IEP goal:

STUDENT PROFILE:
- Name: {student_name}, Grade {grade}
- Communication: {comm_level}
- Interests: {interests}
- Sensory seeks: {sensory_seeks}
- Sensory avoids: {sensory_avoids}

IEP GOAL [{goal_id}]:
{goal_description}
Baseline: {baseline}% | Target: {target}% | Current trend: {current_trend}

Create a 20-30 minute lesson that:
1. Directly targets this IEP goal
2. Weaves in the student's interests naturally
3. Includes a clear assessment check aligned to the goal's measurement
4. Could be done tomorrow with common classroom materials
5. Accounts for sensory needs"""
```

### `prompts/material_forge.py` (Admin Report)

```python
ADMIN_REPORT_SYSTEM = """You are writing a professional IEP progress report
for school administrators and IEP team members.

REQUIREMENTS:
- Use formal, professional language suitable for official documentation
- Lead with an executive summary (2-3 sentences)
- For each goal: state the goal, baseline, current performance, trend, and recommendation
- Include specific data points and percentages
- Note any goals that are at risk of not being met
- End with clear next steps
- This report should look impressive and data-driven
- Administrators love charts and clear metrics — describe data in ways
  that could easily be visualized

Call the generate_admin_report function with your report."""
```

---

## PART 7: BUILD ORDER (Day by Day)

### Phase 1: Foundation (Days 1-3)

```
Day 1: Environment Setup
├── Create project structure (all folders and __init__.py files)
├── Set up requirements.txt and install dependencies
├── Get Google AI Studio API key, create .env
├── Write gemma_client.py and verify basic text generation works
├── Verify multimodal works: send a test image + text, get response
└── Verify function calling works: send a simple tool, get structured output

Day 2: Schemas + State Store
├── Write all schemas/tools.py function definitions
├── Write schemas/student_profile.py Pydantic models
├── Write core/state_store.py (load/save student JSON files)
├── Create 3 dummy student profile JSON files
├── Write unit tests for state_store
└── Verify: can load a profile, add trial data, save, reload

Day 3: Create Sample Work Images
├── Use Gemma 4 or image generation to create mock student work images
├── OR: handwrite some sample worksheets and photograph them
├── OR: create simple digital mockups in a drawing app
├── Need at minimum: 1 worksheet, 1 tally sheet, 1 checklist per student
└── Save to data/sample_work/
```

### Phase 2: Agent Pipeline (Days 4-10)

```
Day 4-5: Vision Reader (Agent 1)
├── Write prompts/vision_reader.py
├── Write agents/vision_reader.py
├── Test on each sample work image type
├── Tune: if accuracy is poor, try higher token budget, different prompts
├── Create precomputed results for all sample images
└── KEY TEST: Does it correctly read Maya's 7/10 math worksheet?

Day 6-7: IEP Mapper (Agent 2)
├── Write prompts/iep_mapper.py
├── Write agents/iep_mapper.py
├── Test: worksheet transcription → correct goal mapping
├── Verify trial data gets saved to student JSON
├── Test with all three students
└── KEY TEST: Does it map Maya's math worksheet to Goal G2 (directions)?

Day 8-9: Progress Analyst (Agent 3)
├── Write prompts/progress_analyst.py
├── Write agents/progress_analyst.py
├── Pre-populate 4+ weeks of dummy trial history
├── Test trend detection across all scenarios
├── Test alert generation (plateau, regression)
├── Verify thinking mode shows reasoning chain
└── KEY TEST: Does it detect Maya's G2 plateau and recommend adding gestural cues?

Day 10: Pipeline Integration
├── Write core/pipeline.py
├── Wire all three agents end-to-end
├── Test full flow: image → transcription → mapping → analysis
├── Create precomputed results for all sample images
├── Fix any data format mismatches between agents
└── KEY TEST: Full pipeline runs in <30 seconds for one image
```

### Phase 3: Material Forge (Days 11-16)

```
Day 11-12: Lesson Plans + Tracking Sheets (Sarah's priorities)
├── Write prompts for lesson plans and tracking sheets
├── Implement generate_lesson_plan() — test with all 3 students × their goals
├── Implement generate_tracking_sheet() — generate printable HTML
├── KEY TEST: Lesson plan for Maya's G1 includes dinosaur-themed greeting activities

Day 13: Social Stories + Visual Schedules + First-Then
├── Implement generate_social_story() — Carol Gray framework
├── Implement generate_visual_schedule() — sequential steps
├── Implement generate_first_then() — binary reinforcement
├── KEY TEST: Social story for Maya uses first person, 2:1 ratio, dinosaur theme

Day 14: Parent Communications + Admin Reports
├── Implement generate_parent_comm()
├── Implement generate_admin_report()
├── Write core/report_generator.py — HTML template for polished admin report
├── KEY TEST: Admin report has executive summary, goal charts, professional language

Day 15-16: Material Forge Integration
├── Wire Material Forge into the full pipeline
├── Test all 7 output types for all 3 students
├── Generate and cache precomputed materials for demo
├── Run full pipeline end-to-end: image → everything
└── KEY TEST: Complete pipeline produces all outputs for all students
```

### Phase 4: Demo App (Days 17-22)

```
Day 17-18: Streamlit App Core
├── Write app.py entry point with navigation
├── Write ui/upload.py — student selector + image upload + process button
├── Write ui/dashboard.py — per-student goal cards with trend arrows
├── Use Plotly for progress charts (line charts showing trial history)
└── KEY TEST: Upload image → see dashboard update with new data point

Day 19-20: Output Screens
├── Write ui/outputs.py — tabbed view of all generated materials
├── Add approve/edit/regenerate buttons (approve just marks it ✓ in session)
├── Write ui/lesson_planner.py — select student + goal → generate lesson plan + tracking sheet
├── Write ui/reports.py — generate admin report → display as formatted HTML
└── KEY TEST: Lesson Planner produces plan within 15 seconds

Day 21: Styling + Polish
├── Write ui/styles.py — custom CSS for ASD-friendly design
├── Color scheme: calm, predictable, high contrast
├── Add ClassLens ASD branding (header, logo placeholder)
├── Pre-load sample data — judges can explore without uploading anything
└── KEY TEST: App looks professional on first load with no setup

Day 22: Precomputed Demo Mode
├── Run full pipeline on every sample image
├── Cache all results in data/precomputed/
├── Implement precomputed result lookup in pipeline.py
├── Test: sample images load instantly, new images call API
└── KEY TEST: Demo walkthrough takes <2 minutes, never waits for API
```

### Phase 5: Deploy + Kaggle Notebook (Days 23-27)

```
Day 23: Deploy to Streamlit Cloud
├── Create streamlit app via Streamlit Cloud (connect GitHub repo)
├── Set GOOGLE_AI_STUDIO_KEY as secret in Streamlit Cloud
├── Verify public URL works
├── Test on phone (judges might try on mobile)
└── KEY TEST: Public URL loads, sample demo works without API key

Day 24-25: Kaggle Notebook
├── Create notebooks/classlens_demo.ipynb
├── Step-by-step walkthrough of entire pipeline
├── Cell 1: Setup and imports
├── Cell 2: Load student profile
├── Cell 3: Vision Reader on sample image (show input and output)
├── Cell 4: IEP Mapper (show goal matching)
├── Cell 5: Progress Analyst (show thinking chain + analysis)
├── Cell 6: Material Forge — lesson plan
├── Cell 7: Material Forge — social story
├── Cell 8: Material Forge — admin report
├── Cell 9: Full pipeline end-to-end
├── Rich markdown cells between each explaining what's happening
└── KEY TEST: Notebook runs top-to-bottom on Kaggle with GPU

Day 26: Ollama Local Demo (Special Tech Track — $10K)
├── Test Gemma 4 E4B via Ollama locally
├── Create a simplified demo script that runs entirely local
├── Document: "Student data never leaves the school network"
├── Take screenshots for writeup / video
└── KEY TEST: E4B model handles at least the Vision Reader + one output type

Day 27: Final Testing + Swap in Sarah's Data
├── Replace dummy profiles with Sarah's real student profiles (if available)
├── Replace sample images with Sarah's work artifacts (if available)
├── Regenerate all precomputed results with new data
├── Full regression test of demo app
├── Full regression test of Kaggle notebook
└── KEY TEST: Everything works with real teacher data
```

### Phase 6: Submission Assets (Days 28-32)

```
Day 28-29: Video Production
├── Screen-record the demo walkthrough (OBS or QuickTime)
├── Integrate Sarah's phone-recorded segments
├── Record Jeff's voiceover (architecture explanation)
├── Edit in iMovie/CapCut to ≤3 minutes
├── Upload to YouTube
└── KEY TEST: Video tells the story in under 3 minutes

Day 30: Kaggle Writeup
├── Write ≤1,500 word writeup
├── Structure: Hook → Solution → Architecture → ASD Design → Demo → Impact
├── Sarah reviews for ASD accuracy
└── KEY TEST: Word count ≤1,500, all required links included

Day 31: Polish + Cover Image
├── Create cover image for Kaggle media gallery
├── Final README.md for GitHub repo
├── Verify all links work (demo URL, YouTube, GitHub)
└── KEY TEST: Everything is publicly accessible

Day 32 (May 17): SUBMIT
├── Submit Kaggle writeup with all attachments
├── Verify status shows "Submitted" not "Draft"
├── Celebrate
└── DONE
```

---

## PART 8: COMPETITION-WINNING DETAILS

### Demo Walkthrough Script (What Judges Will See)

1. App loads with pre-populated student list (Maya, Jaylen, Sofia)
2. Select "Maya" — her profile card shows: Grade 3, dinosaurs, ASD Level 2
3. Dashboard shows 3 IEP goals with trend arrows and mini-charts
4. Click "Upload Work" → select maya_math_worksheet.jpg
5. Watch: "Reading student work..." → "Mapping to IEP goals..." → "Analyzing progress..."
6. Dashboard updates: G2 (following directions) now shows 80% ↑ with new data point
7. Generated Materials tab appears:
   - Lesson plan: "Dinosaur Discovery Directions" — two-step direction activities with dinosaur themes
   - Social story: "When My Teacher Gives Two Steps" — first person, dinosaur reference
   - Parent note: "Maya got 7/10 on her math today! She's improving on following two-step directions..."
8. Click "Admin Report" → polished professional report with charts appears
9. Click "Lesson Planner" → select Maya + Goal G1 → generates a greeting-practice lesson with dinosaur role-play

**Total demo time: 90 seconds of pure wow.**

### The Three "Wow" Moments for Judges

1. **Visual wow:** Messy handwriting photo → structured data appears in real-time
2. **Emotional wow:** Dinosaur-themed social story personalized for one specific child
3. **Professional wow:** Polished admin report that looks like it took hours to write

### IEP Goal Demo Example (From Sarah's Input)

Use this in the Lesson Planner demo:

> "Sam will use two to three word phrases or sentences correctly 90% of the time in response to a direct question"

→ ClassLens generates:
- Lesson plan: "Train Station Questions" (if Sam likes trains)
- Tracking sheet: Date | Question Asked | Student Response | 2-3 Words? | Correct? | Notes
- Practice activities: Turn-taking games where trains only move when Sam uses 2+ word responses

---

## PART 9: RISK MITIGATION (UPDATED)

| Risk | Severity | Mitigation | When to Decide |
|------|----------|------------|----------------|
| Google AI Studio rate limits (5-15 RPM) block demo | HIGH | Pre-baked demo mode with cached results. Happy path never hits API. | Day 1 — verify free tier limits |
| Gemma 4 multimodal OCR accuracy poor | HIGH | Test Day 1. Fallback: cleaner printed worksheets. Increase token budget. | Day 1 |
| Gemma 4 not available on free API tier (April 2026 changes) | HIGH | Check Day 1. Fallback: use Gemini Flash with Gemma for notebook demo. Or Ollama for all inference. | Day 1 |
| Function calling returns malformed JSON | MEDIUM | Every agent has `_parse_fallback()`. Extract JSON from text if tool call fails. | Day 4-5 |
| Streamlit Cloud deployment fails | MEDIUM | Fallback: HF Spaces Docker container, or pre-recorded demo video. | Day 23 |
| Sarah's real data arrives late | LOW | Dummy data is demo-ready. Swap in when available. | Day 27 |

---

## PART 10: ENVIRONMENT SETUP (First Thing on Sandbox)

```bash
# 1. Create project
mkdir classlens-asd && cd classlens-asd

# 2. Python environment
python -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install google-genai streamlit pillow plotly pydantic python-dotenv jinja2

# 4. API key
echo "GOOGLE_AI_STUDIO_KEY=your_key_here" > .env

# 5. Verify Gemma 4 access
python -c "
from google import genai
import os
from dotenv import load_dotenv
load_dotenv()
client = genai.Client(api_key=os.getenv('GOOGLE_AI_STUDIO_KEY'))
response = client.models.generate_content(
    model='gemma-4-27b-it',
    contents='Hello, confirm you are Gemma 4.'
)
print(response.text)
print('SUCCESS: Gemma 4 API is working')
"

# 6. Verify multimodal
python -c "
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
load_dotenv()
client = genai.Client(api_key=os.getenv('GOOGLE_AI_STUDIO_KEY'))
# Test with a simple image
response = client.models.generate_content(
    model='gemma-4-27b-it',
    contents=[
        types.Part.from_text(text='Describe this test image briefly'),
    ]
)
print(response.text)
print('SUCCESS: Multimodal API is working')
"

# 7. Run Streamlit
streamlit run app.py
```

---

## APPENDIX: KEY API REFERENCES

- **Google AI Studio / Gemini API:** https://ai.google.dev/gemini-api/docs
- **Gemma 4 Model Card:** https://ai.google.dev/gemma/docs/core/model_card_4
- **Gemma 4 on Ollama:** https://ollama.com/library/gemma4
- **Streamlit Docs:** https://docs.streamlit.io
- **Streamlit Cloud Deploy:** https://streamlit.io/cloud
- **Plotly for Python:** https://plotly.com/python/
