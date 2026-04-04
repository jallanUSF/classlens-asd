"""
Function calling tool definitions for all four agents.
Gemma 4 native function calling — JSON schema format.

These are passed to GemmaClient.generate_with_tools() as the tools parameter.
"""

TRANSCRIBE_STUDENT_WORK = {
    "name": "transcribe_student_work",
    "description": "Transcribes student work from an image into structured data",
    "parameters": {
        "type": "object",
        "properties": {
            "work_type": {
                "type": "string",
                "enum": [
                    "worksheet", "tally_sheet", "checklist",
                    "visual_schedule", "free_response",
                ],
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
                        "notes": {"type": "string"},
                    },
                },
            },
            "total_items": {"type": "integer"},
            "completed_items": {"type": "integer"},
            "correct_items": {"type": "integer"},
            "accuracy_percentage": {"type": "number"},
            "observations": {"type": "string"},
        },
        "required": [
            "work_type", "items", "total_items",
            "completed_items", "correct_items",
            "accuracy_percentage",
        ],
    },
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
                        "relevance": {
                            "type": "string",
                            "enum": ["primary", "secondary"],
                        },
                        "trials": {"type": "integer"},
                        "successes": {"type": "integer"},
                        "percentage": {"type": "number"},
                        "reasoning": {"type": "string"},
                    },
                },
            },
        },
        "required": ["student_id", "matched_goals"],
    },
}

ANALYZE_PROGRESS = {
    "name": "analyze_goal_progress",
    "description": "Analyzes trend data for an IEP goal and generates alerts",
    "parameters": {
        "type": "object",
        "properties": {
            "student_id": {"type": "string"},
            "goal_id": {"type": "string"},
            "trend": {
                "type": "string",
                "enum": ["improving", "on_track", "plateaued", "regressing"],
            },
            "current_average": {"type": "number"},
            "sessions_analyzed": {"type": "integer"},
            "confidence": {
                "type": "string",
                "enum": ["high", "medium", "low"],
            },
            "alert": {"type": "boolean"},
            "alert_message": {"type": "string"},
            "progress_note": {"type": "string"},
            "recommendation": {"type": "string"},
        },
        "required": [
            "student_id", "goal_id", "trend",
            "current_average", "sessions_analyzed",
        ],
    },
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
                "items": {"type": "string"},
            },
            "warm_up": {"type": "string"},
            "main_activity": {"type": "string"},
            "guided_practice": {"type": "string"},
            "independent_practice": {"type": "string"},
            "assessment_check": {"type": "string"},
            "interest_integration": {"type": "string"},
            "scaffolding_notes": {"type": "string"},
            "estimated_duration_minutes": {"type": "integer"},
        },
        "required": [
            "student_id", "goal_id", "lesson_title",
            "objective", "main_activity",
        ],
    },
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
                "enum": [
                    "trial_percentage", "frequency_count",
                    "duration", "interval", "task_analysis",
                ],
            },
            "columns": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "header": {"type": "string"},
                        "width": {"type": "string"},
                    },
                },
            },
            "rows_per_page": {"type": "integer"},
            "instructions": {"type": "string"},
            "goal_text": {"type": "string"},
            "target_criterion": {"type": "string"},
        },
        "required": [
            "student_id", "goal_id", "sheet_title",
            "measurement_type", "columns",
        ],
    },
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
                            "enum": [
                                "descriptive", "perspective",
                                "directive", "control",
                                "affirmative", "cooperative",
                            ],
                        },
                    },
                },
            },
            "interest_used": {"type": "string"},
            "vocabulary_level": {"type": "string"},
        },
        "required": ["student_id", "title", "scenario", "sentences"],
    },
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
            "tone": {"type": "string"},
        },
        "required": [
            "student_id", "date", "highlight",
            "data_summary", "home_activity",
        ],
    },
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
                        "recommendation": {"type": "string"},
                    },
                },
            },
            "overall_assessment": {"type": "string"},
            "next_steps": {"type": "string"},
        },
        "required": [
            "student_id", "report_period",
            "executive_summary", "goal_summaries",
        ],
    },
}
