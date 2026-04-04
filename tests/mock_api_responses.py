"""
Mock API responses for offline development.

Drop-in replacement for GemmaClient when MOCK_MODE=true in .env

This module provides realistic mock responses for all Gemma 4 API operations,
allowing offline development and testing without consuming API rate limits.

Usage:
    from tests.mock_api_responses import MockGemmaClient
    client = MockGemmaClient()  # Same interface as GemmaClient
    response = client.generate(prompt="Analyze this...")
"""

from typing import Dict, List, Optional, Any
import json
import os
from pathlib import Path


class MockGemmaClient:
    """
    Drop-in replacement for GemmaClient that returns pre-built responses.

    Provides realistic mock data for all vision reading, function calling,
    thinking, and text generation operations used in the ClassLens pipeline.
    """

    def __init__(self):
        """Initialize the mock client with realistic response data."""
        self.mock_data = self._load_mock_data()

    def _load_mock_data(self) -> Dict[str, Any]:
        """Load all mock response data."""
        return {
            "vision_responses": {
                "maya_math_worksheet": self._mock_maya_math_worksheet(),
                "maya_behavior_tally": self._mock_maya_behavior_tally(),
                "jaylen_task_checklist": self._mock_jaylen_task_checklist(),
                "sofia_writing_sample": self._mock_sofia_writing_sample(),
            },
            "function_calls": {
                "iep_mapper": self._mock_iep_mapper_functions(),
                "progress_analyst": self._mock_progress_analyst_functions(),
                "material_forge": self._mock_material_forge_functions(),
            },
            "thinking_responses": {
                "trend_analysis": self._mock_trend_analysis(),
                "intervention_planning": self._mock_intervention_planning(),
            },
        }

    def generate(self, prompt: str, system: Optional[str] = None) -> str:
        """
        Generate a text response to a prompt.

        Args:
            prompt: The user prompt
            system: Optional system prompt

        Returns:
            A realistic mock text response
        """
        # Route based on prompt content for context-aware responses
        if "analyze" in prompt.lower() and "trial" in prompt.lower():
            return (
                "Based on the trial data provided, Maya shows steady progress toward her "
                "communication goal. Her peer interaction rates have improved from 30% to 80% over "
                "4 weeks. Key success factors include the peer buddy program and consistent "
                "reinforcement with dinosaur stickers. Recommend continuing current interventions "
                "and exploring group small-peer interactions for generalization."
            )
        elif "recommend" in prompt.lower():
            return (
                "Recommended interventions for Maya's next period:\n"
                "1. Expand peer buddy program to include lunch table participation\n"
                "2. Create dinosaur-themed social stories for group transitions\n"
                "3. Use iPad counting app as transition reward\n"
                "4. Schedule sensory breaks before transitions\n"
                "5. Continue behavior tracking with weighted lap pad integration"
            )
        else:
            return "Mock text generation response for: " + prompt[:100]

    def generate_multimodal(
        self, image_path: str, prompt: str, system: Optional[str] = None
    ) -> str:
        """
        Process an image and return transcribed/analyzed content.

        Detects which sample image is being processed by filename and returns
        the matching gold-standard response.

        Args:
            image_path: Path to the image file
            prompt: Text prompt to accompany the image
            system: Optional system prompt

        Returns:
            Transcription/analysis of the image content
        """
        filename = Path(image_path).stem.lower()

        if "maya_math" in filename:
            return self._mock_maya_math_worksheet()
        elif "maya_behavior" in filename or "tally" in filename:
            return self._mock_maya_behavior_tally()
        elif "jaylen" in filename or "task" in filename or "checklist" in filename:
            return self._mock_jaylen_task_checklist()
        elif "sofia" in filename or "writing" in filename or "sample" in filename:
            return self._mock_sofia_writing_sample()
        else:
            return f"Mock OCR transcription of image: {Path(image_path).name}"

    def generate_with_tools(
        self,
        prompt: str,
        tools: List[Dict[str, Any]],
        system: Optional[str] = None,
        image_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate a response with function calling capability.

        Returns properly structured function call results matching the tool definitions.

        Args:
            prompt: The user prompt
            tools: List of tool/function definitions
            system: Optional system prompt

        Returns:
            Response dict with "function" and "args" keys
        """
        # Detect which tool/function is being called based on prompt context or tool names
        prompt_lower = prompt.lower()
        tool_names = [t.get("name", "").lower() for t in tools] if tools else []

        # Vision Reader: image_path provided means OCR/transcription
        if image_path:
            return self._mock_vision_reader_call(image_path, prompt)
        elif "map" in prompt_lower and "goal" in prompt_lower:
            return self._mock_iep_mapper_call(prompt)
        elif "analyze" in prompt_lower and "progress" in prompt_lower:
            return self._mock_progress_analyst_call(prompt)
        elif ("generate" in prompt_lower and "lesson" in prompt_lower) or \
             any("generate_lesson" in t for t in tool_names) or \
             any("generate_social" in t for t in tool_names):
            return self._mock_material_forge_call(prompt)
        else:
            return {
                "function": "analyze_content",
                "args": {"content": prompt, "confidence": 0.85},
            }

    def generate_with_thinking(
        self, prompt: str, system: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generate a response with extended thinking capability.

        Returns thinking process + final output dict.

        Args:
            prompt: The user prompt
            system: Optional system prompt

        Returns:
            Dict with "thinking" and "output" keys
        """
        if "trend" in prompt.lower():
            return self._mock_trend_analysis()
        elif "intervention" in prompt.lower():
            return self._mock_intervention_planning()
        else:
            return {
                "thinking": "Analyzing the provided information step by step...",
                "output": "Detailed analysis of the provided context.",
            }

    # ==================== Mock Response Builders ====================

    def _mock_maya_math_worksheet(self) -> str:
        """Mock transcription of Maya's math worksheet with counting problems."""
        return (
            "Maya's Math Worksheet - Date: 2026-04-03\n"
            "Name: MAYA\n"
            "---\n"
            "Problem 1: Count the dinosaurs. 🦖🦖🦖🦖🦖\n"
            "Answer: 5 dinosaurs\n"
            "---\n"
            "Problem 2: Count and write the number.\n"
            "⭐⭐⭐⭐⭐⭐⭐\n"
            "Answer: 7\n"
            "---\n"
            "Problem 3: 2 + 3 = ?\n"
            "Answer: 5 (with 5 dinosaur stickers drawn)\n"
            "---\n"
            "Teacher notes: Excellent focus today. Maya stayed engaged for 15 minutes. "
            "Counted accurately and used dinosaur imagery as engagement tool. "
            "Baseline math skills: accurate to 10."
        )

    def _mock_maya_behavior_tally(self) -> str:
        """Mock transcription of Maya's behavior tally sheet for peer interactions."""
        return (
            "Maya - Peer Interaction Behavior Tally - Week of 2026-03-29 to 2026-04-03\n"
            "---\n"
            "Monday (03/29): III (3/10 greetings) - Fire drill disrupted; recovered well\n"
            "Tuesday (03/30): IIII (4/10) - Morning routine establishing pattern\n"
            "Wednesday (03/31): IIII I (6/10) - Better with familiar peers\n"
            "Thursday (04/01): IIII II (7/10) - Consistent responses in greeting time\n"
            "Friday (04/02): IIII III (8/10) - **GOAL MET** Peer buddy reinforcement working\n"
            "---\n"
            "Reinforcer used: Dinosaur stickers (5 per successful greeting)\n"
            "Context: Classroom arrivals, lunch, specials, free play\n"
            "Teacher observations: Maya shows clear preference for familiar peers. "
            "Sticker reinforcer highly motivating. Recommendation: Expand to new peer contexts."
        )

    def _mock_jaylen_task_checklist(self) -> str:
        """Mock transcription of Jaylen's visual schedule compliance checklist."""
        return (
            "Jaylen - Visual Schedule Independence Checklist - Date: 2026-04-03\n"
            "---\n"
            "Transition 1 (Arrival to Mat Time): ✓ unprompted\n"
            "Transition 2 (Mat Time to Work Station): ✓ with verbal cue + point\n"
            "Transition 3 (Work Station to Lunch): ✓ unprompted\n"
            "Transition 4 (Lunch to Fine Motor): ✓ with verbal cue only\n"
            "Transition 5 (Fine Motor to Sensory): ✓ unprompted\n"
            "---\n"
            "Score: 5/5 transitions completed\n"
            "Independence rating: 4/5 (mostly unprompted, minimal cues needed)\n"
            "Reinforcer: 2 minutes with Thomas train toys\n"
            "Notes: Jaylen's visual schedule now includes photos of him engaged in activities. "
            "Using Thomas sticker chart for motivation. Self-initiating transitions most of the time. "
            "**GOAL MET: 90% independence achieved**"
        )

    def _mock_sofia_writing_sample(self) -> str:
        """Mock transcription of Sofia's reflective writing sample."""
        return (
            "Sofia - Reflective Essay: 'The Most Important Presidents'\n"
            "Date: 2026-04-03 | Grade Level: 5 | Reading Level: 7\n"
            "---\n"
            "I think George Washington was important because he started our country. "
            "But I also think Lincoln was important because he cared about people being free. "
            "He was worried that slavery was wrong. I think Washington maybe felt worried too "
            "because he had to make hard decisions.\n"
            "\n"
            "Some presidents were good at making peace, and some were good at making laws. "
            "I organized all 47 presidents by what they did best. I noticed that presidents "
            "who listened to other people were more successful. Maybe that is why they felt happy "
            "in their job.\n"
            "\n"
            "When I write about presidents, I feel interested and excited. I like organizing things "
            "in categories. I think that is why this assignment felt easy for me.\n"
            "---\n"
            "Writing Rubric Assessment: 4/4\n"
            "- Voice & Opinion: Strong personal perspective; abstract reasoning present\n"
            "- Emotional Expression: Includes inferences about president feelings\n"
            "- Organization: Well-structured with supporting examples\n"
            "**GOAL MET: Creative expression with emotional/abstract thinking demonstrated**"
        )

    def _mock_iep_mapper_functions(self) -> Dict[str, Any]:
        """Mock function definitions for IEP mapping."""
        return {
            "functions": [
                {
                    "name": "map_transcription_to_goals",
                    "description": "Map transcribed student work to specific IEP goals",
                    "parameters": {
                        "transcription": "The transcribed work content",
                        "student_id": "Student identifier",
                        "goal_ids": "List of relevant goal IDs",
                        "success_indicators": "List of indicators of goal progress",
                    },
                },
                {
                    "name": "extract_trial_data",
                    "description": "Extract trial data from worksheets or tally sheets",
                    "parameters": {
                        "transcription": "The transcribed content",
                        "goal_id": "The relevant goal ID",
                        "total_trials": "Total number of trials recorded",
                        "successes": "Number of successful trials",
                    },
                },
            ]
        }

    def _mock_progress_analyst_functions(self) -> Dict[str, Any]:
        """Mock function definitions for progress analysis."""
        return {
            "functions": [
                {
                    "name": "analyze_goal_progress",
                    "description": "Analyze progress toward an IEP goal",
                    "parameters": {
                        "goal_id": "The goal to analyze",
                        "recent_trials": "List of recent trial data",
                        "trend": "Identified trend (improving/stable/declining)",
                        "days_to_target": "Estimated days to reach 80% target",
                    },
                },
                {
                    "name": "flag_regression",
                    "description": "Flag potential regressions or concerns",
                    "parameters": {
                        "goal_id": "Goal with potential issue",
                        "regression_type": "Type of regression detected",
                        "severity": "Severity level (low/medium/high)",
                    },
                },
            ]
        }

    def _mock_material_forge_functions(self) -> Dict[str, Any]:
        """Mock function definitions for material generation."""
        return {
            "functions": [
                {
                    "name": "generate_lesson_plan",
                    "description": "Generate personalized lesson plan themed to student interests",
                    "parameters": {
                        "goal_id": "Target IEP goal",
                        "student_interests": "Student's interests for theming",
                        "grade_level": "Student's grade level",
                        "format": "Lesson plan with activities, materials, reinforcers",
                    },
                },
                {
                    "name": "generate_social_story",
                    "description": "Generate a social story for a specific scenario",
                    "parameters": {
                        "scenario": "The social scenario to address",
                        "student_interests": "Interests to incorporate",
                        "story": "Social story with visual descriptions",
                    },
                },
            ]
        }

    def _mock_vision_reader_call(self, image_path: str, prompt: str) -> Dict[str, Any]:
        """Mock Vision Reader function call response (transcription via tool use)."""
        filename = Path(image_path).stem.lower()

        if "maya_math" in filename:
            return {
                "function": "transcribe_student_work",
                "args": {
                    "student_name": "Maya",
                    "work_type": "worksheet",
                    "subject": "math",
                    "raw_text": self._mock_maya_math_worksheet(),
                    "task_items": [
                        {"item": "Count the dinosaurs", "response": "5", "correct": True},
                        {"item": "Count and write the number", "response": "7", "correct": True},
                        {"item": "2 + 3 = ?", "response": "5", "correct": True},
                    ],
                    "total_items": 3,
                    "correct_items": 3,
                    "accuracy_pct": 100,
                    "teacher_notes": "Excellent focus today. Stayed engaged for 15 minutes.",
                    "engagement_indicators": ["sustained focus", "dinosaur imagery as engagement tool"],
                },
            }
        elif "maya_behavior" in filename or "tally" in filename:
            return {
                "function": "transcribe_student_work",
                "args": {
                    "student_name": "Maya",
                    "work_type": "tally_sheet",
                    "subject": "communication",
                    "raw_text": self._mock_maya_behavior_tally(),
                    "task_items": [
                        {"item": "Monday greetings", "response": "3/10", "correct": False},
                        {"item": "Tuesday greetings", "response": "4/10", "correct": False},
                        {"item": "Wednesday greetings", "response": "6/10", "correct": False},
                        {"item": "Thursday greetings", "response": "7/10", "correct": False},
                        {"item": "Friday greetings", "response": "8/10", "correct": True},
                    ],
                    "total_items": 5,
                    "correct_items": 1,
                    "accuracy_pct": 80,
                    "teacher_notes": "Peer buddy reinforcement working. Goal met Friday.",
                    "engagement_indicators": ["consistent daily improvement", "sticker reinforcer effective"],
                },
            }
        elif "jaylen" in filename or "checklist" in filename:
            return {
                "function": "transcribe_student_work",
                "args": {
                    "student_name": "Jaylen",
                    "work_type": "checklist",
                    "subject": "daily_living",
                    "raw_text": self._mock_jaylen_task_checklist(),
                    "task_items": [
                        {"item": "Arrival to Mat Time", "response": "unprompted", "correct": True},
                        {"item": "Mat Time to Work Station", "response": "verbal cue + point", "correct": True},
                        {"item": "Work Station to Lunch", "response": "unprompted", "correct": True},
                        {"item": "Lunch to Fine Motor", "response": "verbal cue only", "correct": True},
                        {"item": "Fine Motor to Sensory", "response": "unprompted", "correct": True},
                    ],
                    "total_items": 5,
                    "correct_items": 5,
                    "accuracy_pct": 100,
                    "teacher_notes": "90% independence achieved. Visual schedule with photos working.",
                    "engagement_indicators": ["self-initiating transitions", "Thomas train motivation"],
                },
            }
        elif "sofia" in filename or "writing" in filename:
            return {
                "function": "transcribe_student_work",
                "args": {
                    "student_name": "Sofia",
                    "work_type": "free_response",
                    "subject": "writing",
                    "raw_text": self._mock_sofia_writing_sample(),
                    "task_items": [
                        {"item": "Voice & Opinion", "response": "4/4", "correct": True},
                        {"item": "Emotional Expression", "response": "4/4", "correct": True},
                        {"item": "Organization", "response": "4/4", "correct": True},
                    ],
                    "total_items": 3,
                    "correct_items": 3,
                    "accuracy_pct": 100,
                    "teacher_notes": "Creative expression with emotional/abstract thinking demonstrated.",
                    "engagement_indicators": ["strong personal perspective", "abstract reasoning", "organizing by categories"],
                },
            }
        else:
            return {
                "function": "transcribe_student_work",
                "args": {
                    "student_name": "Unknown",
                    "work_type": "worksheet",
                    "subject": "general",
                    "raw_text": f"Mock transcription of {Path(image_path).name}",
                    "task_items": [],
                    "total_items": 0,
                    "correct_items": 0,
                    "accuracy_pct": 0,
                    "teacher_notes": "",
                    "engagement_indicators": [],
                },
            }

    def _mock_iep_mapper_call(self, prompt: str) -> Dict[str, Any]:
        """Mock IEP mapper function call response."""
        prompt_lower = prompt.lower()

        if "jaylen" in prompt_lower:
            return {
                "function": "map_work_to_goals",
                "args": {
                    "matched_goals": [
                        {
                            "goal_id": "G1",
                            "reasoning": "Visual schedule independence directly measures G1 target",
                            "trials": 5,
                            "successes": 5,
                            "percentage": 100,
                        }
                    ],
                    "overall_summary": "Jaylen met 90% independence target on visual schedule transitions.",
                },
            }
        elif "sofia" in prompt_lower:
            return {
                "function": "map_work_to_goals",
                "args": {
                    "matched_goals": [
                        {
                            "goal_id": "G1",
                            "reasoning": "Writing sample demonstrates abstract reasoning and emotional expression",
                            "trials": 3,
                            "successes": 3,
                            "percentage": 100,
                        }
                    ],
                    "overall_summary": "Sofia's writing demonstrates goal mastery in creative expression.",
                },
            }
        else:
            # Default to Maya
            return {
                "function": "map_work_to_goals",
                "args": {
                    "matched_goals": [
                        {
                            "goal_id": "G1",
                            "reasoning": "Peer greeting tally directly measures communication goal",
                            "trials": 10,
                            "successes": 8,
                            "percentage": 80,
                        },
                        {
                            "goal_id": "G2",
                            "reasoning": "Math accuracy and engagement indicate direction-following progress",
                            "trials": 8,
                            "successes": 6,
                            "percentage": 75,
                        },
                    ],
                    "overall_summary": "Maya shows strong progress on both communication and direction-following goals.",
                },
            }

    def _mock_progress_analyst_call(self, prompt: str) -> Dict[str, Any]:
        """Mock progress analyst function call response."""
        return {
            "function": "analyze_goal_progress",
            "args": {
                "goal_id": "G1",
                "recent_trials": [
                    {"date": "2026-03-29", "success_pct": 60},
                    {"date": "2026-04-01", "success_pct": 70},
                    {"date": "2026-04-03", "success_pct": 80},
                ],
                "trend": "improving",
                "days_to_target": 0,
                "target_reached_date": "2026-04-03",
                "confidence": 0.95,
            },
        }

    def _mock_material_forge_call(self, prompt: str) -> Dict[str, Any]:
        """Mock material forge function call response."""
        prompt_lower = prompt.lower()

        if "tracking" in prompt_lower or "sheet" in prompt_lower:
            return {
                "function": "generate_tracking_sheet",
                "args": {
                    "title": "Communication Goal G1 — Tracking Sheet",
                    "student_name": "Maya",
                    "goal_description": "Initiate/respond to peer greetings with 80% accuracy",
                    "columns": ["Date", "Setting", "Trials", "Successes", "Pct", "Prompting", "Notes"],
                    "measurement_method": "teacher observation tally",
                    "target": 80,
                    "baseline": 20,
                },
            }
        elif "social story" in prompt_lower or "scenario" in prompt_lower:
            return {
                "function": "generate_social_story",
                "args": {
                    "title": "When My Friends Say Hello",
                    "pages": [
                        "Sometimes my friends say 'Hi Maya!' when I get to school. This is called a greeting.",
                        "When someone says hi, I can wave, say 'hi' back, or smile. All of these are good!",
                        "My friend Blue the raptor always greets his pack. I can greet my friends too.",
                        "If I feel nervous, I can squeeze my fidget cube. Then I can try to say hi.",
                        "When I greet my friends, they feel happy. And I might get a dinosaur sticker!",
                    ],
                    "skill_targeted": "Responding to peer greetings",
                    "interest_integration": "Jurassic World raptors (Blue)",
                },
            }
        elif "parent" in prompt_lower:
            return {
                "function": "generate_parent_comm",
                "args": {
                    "subject": "Maya's Weekly Progress Update",
                    "greeting": "Dear Maya's family,",
                    "progress_summary": "Maya had a great week! She's been greeting her friends more and more each day.",
                    "highlights": [
                        "Met her peer greeting goal (8 out of 10 greetings!)",
                        "Stayed focused for 15 minutes during math",
                        "Used her calming strategies well after the fire drill",
                    ],
                    "home_tips": [
                        "Practice greetings with family members at dinner",
                        "Use dinosaur stickers as rewards for saying hi to neighbors",
                    ],
                    "closing": "Maya is making wonderful progress. Thank you for your support at home!",
                },
            }
        elif "admin" in prompt_lower or "report" in prompt_lower:
            return {
                "function": "generate_admin_report",
                "args": {
                    "student_name": "Maya",
                    "period": "Monthly",
                    "executive_summary": "Maya demonstrates strong upward trend across all IEP goals.",
                    "goal_summaries": [
                        {"goal_id": "G1", "status": "Met", "trend": "improving", "current_pct": 80},
                        {"goal_id": "G2", "status": "Met", "trend": "improving", "current_pct": 75},
                        {"goal_id": "G3", "status": "Approaching", "trend": "improving", "current_pct": 80},
                    ],
                    "recommendations": "Continue current interventions; consider expanding peer contexts.",
                },
            }
        else:
            # Default: lesson plan
            return {
                "function": "generate_lesson_plan",
                "args": {
                    "title": "Blue Raptor Peer Greeting Game",
                    "duration": "15-20 minutes",
                    "goal_id": "G1",
                    "objective": "Practice peer greetings in a dinosaur-themed game context",
                    "materials": [
                        "Blue raptor figurines",
                        "Dinosaur stickers",
                        "Picture cards of peers",
                        "Purple paper",
                    ],
                    "activities": [
                        {"step": 1, "description": "Greeting practice with raptor character voices", "duration": "5 min"},
                        {"step": 2, "description": "Count successful peer greetings on purple tally", "duration": "5 min"},
                        {"step": 3, "description": "Earn dinosaur sticker rewards for each greeting", "duration": "5 min"},
                    ],
                    "reinforcers": ["Dinosaur stickers", "5 min water table time"],
                    "sensory_supports": ["Weighted lap pad available", "Noise-canceling headphones nearby"],
                    "data_collection": "Tally greetings on tracking sheet; note prompting level",
                },
            }

    def _mock_trend_analysis(self) -> Dict[str, str]:
        """Mock trend analysis with thinking process."""
        return {
            "thinking": (
                "Let me analyze Maya's trial data step by step:\n"
                "1. Initial baseline (March 15): 3/10 successes (30%)\n"
                "2. Second observation (March 22): 4/10 (40%) - slight improvement\n"
                "3. Third observation (March 29): 6/10 (60%) - clear upward trend, despite fire drill disruption\n"
                "4. Fourth observation (April 1): 7/10 (70%) - consistent improvement\n"
                "5. Fifth observation (April 3): 8/10 (80%) - TARGET REACHED\n"
                "\n"
                "Pattern analysis:\n"
                "- Steady increase of approximately 10% per week\n"
                "- Only minor setback during fire drill (expected given sensory sensitivity)\n"
                "- Peer buddy program appears highly effective\n"
                "- Dinosaur sticker reinforcer strongly motivating\n"
                "- Goal reached in 4 weeks, well ahead of initial IEP timeline\n"
                "\n"
                "Confidence in trend: Very high (95%+). This is a clear, linear improvement "
                "with consistent intervention application."
            ),
            "output": (
                "Maya demonstrates strong positive trend toward Communication Goal G1. "
                "She has reached the 80% target in 4 weeks through consistent peer buddy "
                "engagement, reinforcement with dinosaur stickers, and morning routine establishment. "
                "The trend is stable and sustainable, with only minor disruption during the fire drill. "
                "Recommend maintaining current interventions and considering generalization to "
                "larger peer group contexts."
            ),
        }

    def _mock_intervention_planning(self) -> Dict[str, str]:
        """Mock intervention planning with thinking process."""
        return {
            "thinking": (
                "Given Maya's strong progress on G1 (communication/peer interaction), "
                "I should plan interventions that:\n"
                "1. Consolidate current gains in familiar contexts\n"
                "2. Generalize to new contexts (larger groups, new peers)\n"
                "3. Address G2 (following directions) where she's at 75% (near target)\n"
                "4. Maintain sensory supports that are clearly working\n"
                "\n"
                "Intervention options:\n"
                "- Expand peer buddy program to different lunch tables\n"
                "- Create dinosaur-themed social stories for group transitions\n"
                "- Use water table as transition reward (aligns with interests)\n"
                "- Combine G1 and G2: give two-step directions in peer contexts\n"
                "- Maintain sensory breaks; they're preventing escalation\n"
                "\n"
                "Feasibility: High (teacher already using effective strategies)\n"
                "Cost: Minimal (dinosaur stickers, social story creation time)\n"
                "Estimated success rate: 85%+"
            ),
            "output": (
                "Recommended next interventions for Maya (next 4 weeks):\n"
                "1. Expand peer interaction to new peer dyads using dinosaur game context\n"
                "2. Create 3 dinosaur-themed social stories for transition/lunch contexts\n"
                "3. Integrate water table time as G2 (direction-following) reward\n"
                "4. Continue weighted lap pad and noise-canceling headphone supports\n"
                "5. Track generalization to 2-3 new peers and 2-3 new settings\n"
                "6. Schedule review in 3 weeks to assess G2 progress (currently 75%)"
            ),
        }
