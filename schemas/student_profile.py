"""
Student Profile Schemas
Pydantic models for student data, IEP goals, trial data, and sensory profiles.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator


class SensoryProfile(BaseModel):
    """
    Sensory profile for an ASD student.
    Captures sensory sensitivities and preferences.
    """

    auditory_sensitivity: str = Field(
        default="typical",
        description="Level of auditory sensitivity (typical, sensitive, seeking)",
    )
    visual_sensitivity: str = Field(
        default="typical",
        description="Level of visual sensitivity (typical, sensitive, seeking)",
    )
    tactile_sensitivity: str = Field(
        default="typical",
        description="Level of tactile sensitivity (typical, sensitive, seeking)",
    )
    proprioceptive_preference: str = Field(
        default="typical",
        description="Proprioceptive feedback preference (typical, seeking, avoiding)",
    )
    vestibular_preference: str = Field(
        default="typical",
        description="Vestibular feedback preference (typical, seeking, avoiding)",
    )
    preferred_textures: List[str] = Field(
        default_factory=list,
        description="List of preferred tactile textures",
    )
    avoided_textures: List[str] = Field(
        default_factory=list,
        description="List of avoided tactile textures",
    )
    calming_strategies: List[str] = Field(
        default_factory=list,
        description="Known sensory calming strategies that work for this student",
    )

    @validator("auditory_sensitivity", "visual_sensitivity", "tactile_sensitivity")
    def validate_sensitivity(cls, v):
        """Validate sensitivity levels."""
        valid_values = ["typical", "sensitive", "seeking"]
        if v not in valid_values:
            raise ValueError(
                f"Must be one of {valid_values}, got {v}"
            )
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "auditory_sensitivity": "sensitive",
                "visual_sensitivity": "typical",
                "tactile_sensitivity": "seeking",
                "proprioceptive_preference": "seeking",
                "vestibular_preference": "avoiding",
                "preferred_textures": ["soft", "smooth"],
                "avoided_textures": ["rough", "scratchy"],
                "calming_strategies": ["deep pressure", "quiet space"],
            }
        }


class IEPGoal(BaseModel):
    """
    Individualized Education Plan (IEP) Goal.
    Represents a single target behavior or skill for the student.
    """

    goal_id: str = Field(
        ...,
        description="Unique identifier for the goal",
    )
    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Goal title or target behavior",
    )
    description: str = Field(
        default="",
        description="Detailed description of the goal",
    )
    domain: str = Field(
        default="academic",
        description="Goal domain (academic, social, communication, motor, sensory)",
    )
    target_percentage: float = Field(
        default=80.0,
        ge=0.0,
        le=100.0,
        description="Target success percentage for goal mastery",
    )
    created_date: datetime = Field(
        default_factory=datetime.utcnow,
        description="Date the goal was created",
    )
    start_date: datetime = Field(
        default_factory=datetime.utcnow,
        description="Date goal intervention began",
    )
    end_date: Optional[datetime] = Field(
        default=None,
        description="Expected end date for goal achievement",
    )
    is_active: bool = Field(
        default=True,
        description="Whether this goal is currently active",
    )
    measurement_method: str = Field(
        default="frequency",
        description="How success is measured (frequency, percentage, duration, quality)",
    )
    notes: str = Field(
        default="",
        description="Additional notes about the goal",
    )

    @validator("domain")
    def validate_domain(cls, v):
        """Validate goal domain."""
        valid_domains = ["academic", "social", "communication", "motor", "sensory"]
        if v not in valid_domains:
            raise ValueError(
                f"Domain must be one of {valid_domains}, got {v}"
            )
        return v

    @validator("measurement_method")
    def validate_measurement_method(cls, v):
        """Validate measurement method."""
        valid_methods = ["frequency", "percentage", "duration", "quality"]
        if v not in valid_methods:
            raise ValueError(
                f"Measurement method must be one of {valid_methods}, got {v}"
            )
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "goal_id": "GOAL_001",
                "title": "Increase eye contact during peer interactions",
                "description": "Student will maintain eye contact for at least 3 seconds during conversations",
                "domain": "social",
                "target_percentage": 80.0,
                "created_date": "2026-01-15T10:00:00",
                "start_date": "2026-01-15T10:00:00",
                "end_date": "2026-05-15T10:00:00",
                "is_active": True,
                "measurement_method": "frequency",
                "notes": "Focus on natural, peer-initiated interactions",
            }
        }


class TrialData(BaseModel):
    """
    Trial data for tracking goal progress.
    Records individual trial results for a specific goal.
    """

    trial_id: str = Field(
        ...,
        description="Unique identifier for the trial",
    )
    goal_id: str = Field(
        ...,
        description="Reference to the IEP goal being measured",
    )
    student_id: str = Field(
        ...,
        description="Reference to the student",
    )
    trial_date: datetime = Field(
        default_factory=datetime.utcnow,
        description="Date the trial was conducted",
    )
    total_trials: int = Field(
        default=1,
        ge=1,
        description="Total number of trials conducted",
    )
    successes: int = Field(
        default=0,
        ge=0,
        description="Number of successful trials",
    )
    success_percentage: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Calculated success percentage",
    )
    context: str = Field(
        default="classroom",
        description="Context where trial occurred (classroom, home, community, therapy)",
    )
    instructor: Optional[str] = Field(
        default=None,
        description="Name of instructor who conducted trial",
    )
    prompting_level: str = Field(
        default="independent",
        description="Level of prompting used (independent, spatial, verbal, model, physical)",
    )
    notes: str = Field(
        default="",
        description="Observational notes about the trial",
    )
    behavior_observations: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional behavioral observations (JSON structure)",
    )

    @validator("successes")
    def validate_successes(cls, v, values):
        """Ensure successes does not exceed total trials."""
        if "total_trials" in values and v > values["total_trials"]:
            raise ValueError("Successes cannot exceed total trials")
        return v

    @validator("success_percentage", always=True)
    def calculate_success_percentage(cls, v, values):
        """Auto-calculate success percentage from successes and total_trials."""
        if "total_trials" in values and "successes" in values:
            return round(
                (values["successes"] / values["total_trials"]) * 100, 2
            )
        return v

    @validator("context")
    def validate_context(cls, v):
        """Validate trial context."""
        valid_contexts = ["classroom", "home", "community", "therapy"]
        if v not in valid_contexts:
            raise ValueError(
                f"Context must be one of {valid_contexts}, got {v}"
            )
        return v

    @validator("prompting_level")
    def validate_prompting_level(cls, v):
        """Validate prompting level."""
        valid_levels = ["independent", "spatial", "verbal", "model", "physical"]
        if v not in valid_levels:
            raise ValueError(
                f"Prompting level must be one of {valid_levels}, got {v}"
            )
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "trial_id": "TRIAL_001",
                "goal_id": "GOAL_001",
                "student_id": "STU_001",
                "trial_date": "2026-02-10T14:30:00",
                "total_trials": 10,
                "successes": 8,
                "success_percentage": 80.0,
                "context": "classroom",
                "instructor": "Ms. Smith",
                "prompting_level": "verbal",
                "notes": "Student was responsive and engaged throughout session",
                "behavior_observations": {
                    "off_task_moments": 2,
                    "emotional_state": "calm",
                    "peer_interaction": "positive",
                },
            }
        }


class StudentProfile(BaseModel):
    """
    Complete student profile with demographic, clinical, and educational information.
    """

    student_id: str = Field(
        ...,
        min_length=1,
        description="Unique student identifier",
    )
    first_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Student first name",
    )
    last_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Student last name",
    )
    date_of_birth: datetime = Field(
        ...,
        description="Student date of birth",
    )
    grade_level: int = Field(
        default=1,
        ge=0,
        le=12,
        description="Current grade level (0 for preschool)",
    )
    school: str = Field(
        default="",
        description="School name",
    )
    teacher: str = Field(
        default="",
        description="Primary classroom teacher name",
    )
    autism_level: str = Field(
        default="level_1",
        description="Autism support level (level_1, level_2, level_3)",
    )
    asd_diagnosis_date: Optional[datetime] = Field(
        default=None,
        description="Date of ASD diagnosis",
    )
    primary_interests: List[str] = Field(
        default_factory=list,
        description="Primary areas of interest for the student",
    )
    strengths: List[str] = Field(
        default_factory=list,
        description="Academic and behavioral strengths",
    )
    challenges: List[str] = Field(
        default_factory=list,
        description="Known challenges and areas for support",
    )
    communication_style: str = Field(
        default="verbal",
        description="Primary communication style (verbal, AAC, sign, mixed)",
    )
    iep_goals: List[IEPGoal] = Field(
        default_factory=list,
        description="List of active IEP goals",
    )
    trial_history: List[TrialData] = Field(
        default_factory=list,
        description="Historical trial data for tracking progress",
    )
    sensory_profile: SensoryProfile = Field(
        default_factory=SensoryProfile,
        description="Sensory profile and preferences",
    )
    last_updated: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp of last profile update",
    )
    notes: str = Field(
        default="",
        description="General notes about the student",
    )

    @validator("autism_level")
    def validate_autism_level(cls, v):
        """Validate autism support level."""
        valid_levels = ["level_1", "level_2", "level_3"]
        if v not in valid_levels:
            raise ValueError(
                f"Autism level must be one of {valid_levels}, got {v}"
            )
        return v

    @validator("communication_style")
    def validate_communication_style(cls, v):
        """Validate communication style."""
        valid_styles = ["verbal", "AAC", "sign", "mixed"]
        if v not in valid_styles:
            raise ValueError(
                f"Communication style must be one of {valid_styles}, got {v}"
            )
        return v

    @property
    def full_name(self) -> str:
        """Return student full name."""
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self) -> int:
        """Calculate student age."""
        today = datetime.utcnow()
        age = today.year - self.date_of_birth.year
        if (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day):
            age -= 1
        return age

    @property
    def active_goals(self) -> List[IEPGoal]:
        """Return list of active IEP goals."""
        return [goal for goal in self.iep_goals if goal.is_active]

    @property
    def goal_count(self) -> int:
        """Return count of active IEP goals."""
        return len(self.active_goals)

    def get_goal_by_id(self, goal_id: str) -> Optional[IEPGoal]:
        """Retrieve a specific goal by ID."""
        for goal in self.iep_goals:
            if goal.goal_id == goal_id:
                return goal
        return None

    def get_recent_trials(self, goal_id: str, limit: int = 10) -> List[TrialData]:
        """Get recent trial data for a specific goal."""
        goal_trials = [
            trial for trial in self.trial_history
            if trial.goal_id == goal_id
        ]
        return sorted(
            goal_trials,
            key=lambda t: t.trial_date,
            reverse=True
        )[:limit]

    def calculate_goal_progress(self, goal_id: str) -> Dict[str, Any]:
        """Calculate progress metrics for a specific goal."""
        recent_trials = self.get_recent_trials(goal_id, limit=10)
        if not recent_trials:
            return {
                "goal_id": goal_id,
                "trials_count": 0,
                "average_percentage": 0.0,
                "trend": "no_data",
                "recent_trials": [],
            }

        percentages = [trial.success_percentage for trial in recent_trials]
        average = sum(percentages) / len(percentages)

        # Simple trend detection
        if len(percentages) >= 2:
            recent_avg = sum(percentages[:5]) / min(5, len(percentages))
            older_avg = sum(percentages[5:]) / max(1, len(percentages) - 5)
            if recent_avg > older_avg + 5:
                trend = "improving"
            elif recent_avg < older_avg - 5:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"

        return {
            "goal_id": goal_id,
            "trials_count": len(recent_trials),
            "average_percentage": round(average, 2),
            "trend": trend,
            "recent_trials": recent_trials,
        }

    class Config:
        json_schema_extra = {
            "example": {
                "student_id": "STU_001",
                "first_name": "Emma",
                "last_name": "Johnson",
                "date_of_birth": "2015-06-15",
                "grade_level": 5,
                "school": "Lincoln Elementary",
                "teacher": "Ms. Sarah Smith",
                "autism_level": "level_2",
                "asd_diagnosis_date": "2018-03-20",
                "primary_interests": ["animals", "reading", "art"],
                "strengths": ["memory skills", "visual processing", "artistic ability"],
                "challenges": ["social interaction", "sensory sensitivity", "anxiety"],
                "communication_style": "verbal",
                "notes": "Thrives with structure and visual supports",
            }
        }
