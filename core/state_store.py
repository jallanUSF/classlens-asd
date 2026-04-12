"""
State Store Module
Manages persistent storage and retrieval of student data.
Handles JSON serialization with Pydantic models.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from core.json_io import read_json, write_json
from schemas.student_profile import StudentProfile, IEPGoal, TrialData


class StateStore:
    """
    Persistent state management for student data.
    Stores and retrieves student profiles, IEP goals, and trial data.
    Uses JSON files for persistence.
    """

    def __init__(self, data_dir: str = "data"):
        """
        Initialize the state store.

        Args:
            data_dir: Directory path for storing student data files.
                     Defaults to 'data' in the current working directory.
        """
        self.data_dir = Path(data_dir)
        self.students_dir = self.data_dir / "students"

        # Create directories if they don't exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.students_dir.mkdir(parents=True, exist_ok=True)

    def _get_student_path(self, student_id: str) -> Path:
        """
        Get the file path for a student's data file.

        Args:
            student_id: The student's unique identifier.

        Returns:
            Path object for the student's JSON file.
        """
        return self.students_dir / f"{student_id}.json"

    def load_student(self, student_id: str) -> Optional[StudentProfile]:
        """
        Load a complete student profile from disk.

        Args:
            student_id: The student's unique identifier.

        Returns:
            StudentProfile object if found, None if not found.

        Raises:
            ValueError: If the JSON file is corrupted or invalid.
        """
        student_path = self._get_student_path(student_id)

        if not student_path.exists():
            return None

        try:
            data = read_json(student_path)
            return StudentProfile(**data)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Corrupted JSON file for student {student_id}: {str(e)}"
            )
        except Exception as e:
            raise ValueError(
                f"Error loading student {student_id}: {str(e)}"
            )

    def save_student(self, student: StudentProfile) -> None:
        """
        Save a complete student profile to disk.

        Args:
            student: StudentProfile object to save.

        Raises:
            IOError: If the file cannot be written.
        """
        student_path = self._get_student_path(student.student_id)

        try:
            # Convert Pydantic model to JSON-serializable dict
            student_data = student.model_dump(
                mode="json",
                exclude_none=False,
            )
            write_json(student_path, student_data)
        except IOError as e:
            raise IOError(
                f"Failed to save student {student.student_id}: {str(e)}"
            )

    def add_trial_data(
        self,
        student_id: str,
        goal_id: str,
        trial_date: Optional[datetime] = None,
        total_trials: int = 10,
        successes: int = 0,
        context: str = "classroom",
        instructor: Optional[str] = None,
        prompting_level: str = "independent",
        notes: str = "",
        behavior_observations: Optional[Dict[str, Any]] = None,
    ) -> Optional[TrialData]:
        """
        Add trial data for a specific student goal.

        Args:
            student_id: The student's unique identifier.
            goal_id: The goal ID the trial is measuring.
            trial_date: Date the trial occurred. Defaults to now.
            total_trials: Total number of trials conducted.
            successes: Number of successful trials.
            context: Context where trial occurred.
            instructor: Name of instructor who conducted trial.
            prompting_level: Level of prompting used.
            notes: Observational notes.
            behavior_observations: Additional behavioral observations.

        Returns:
            TrialData object if successful, None if student or goal not found.

        Raises:
            ValueError: If trial data is invalid.
        """
        student = self.load_student(student_id)
        if student is None:
            raise ValueError(f"Student {student_id} not found")

        # Verify goal exists
        goal = student.get_goal_by_id(goal_id)
        if goal is None:
            raise ValueError(
                f"Goal {goal_id} not found for student {student_id}"
            )

        if trial_date is None:
            trial_date = datetime.utcnow()

        # Generate trial ID
        trial_count = len(student.trial_history) + 1
        trial_id = f"{student_id}_{goal_id}_TRIAL_{trial_count:04d}"

        # Create trial data
        trial_data = TrialData(
            trial_id=trial_id,
            goal_id=goal_id,
            student_id=student_id,
            trial_date=trial_date,
            total_trials=total_trials,
            successes=successes,
            context=context,
            instructor=instructor,
            prompting_level=prompting_level,
            notes=notes,
            behavior_observations=behavior_observations,
        )

        # Add to student's trial history
        student.trial_history.append(trial_data)
        student.last_updated = datetime.utcnow()

        # Persist changes
        self.save_student(student)

        return trial_data

    def get_all_students(self) -> List[str]:
        """
        Get a list of all student IDs in the store.

        Returns:
            List of student IDs.
        """
        if not self.students_dir.exists():
            return []

        student_ids = []
        for json_file in self.students_dir.glob("*.json"):
            student_id = json_file.stem
            student_ids.append(student_id)

        return sorted(student_ids)

    def get_student_summary(self, student_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a summary of student information.

        Args:
            student_id: The student's unique identifier.

        Returns:
            Dictionary with key student information, or None if not found.
        """
        student = self.load_student(student_id)
        if student is None:
            return None

        return {
            "student_id": student.student_id,
            "full_name": student.full_name,
            "grade_level": student.grade_level,
            "autism_level": student.autism_level,
            "age": student.age,
            "school": student.school,
            "teacher": student.teacher,
            "primary_interests": student.primary_interests,
            "communication_style": student.communication_style,
            "goal_count": student.goal_count,
            "active_goals": [
                {
                    "goal_id": goal.goal_id,
                    "title": goal.title,
                    "domain": goal.domain,
                    "target_percentage": goal.target_percentage,
                }
                for goal in student.active_goals
            ],
            "trial_count": len(student.trial_history),
            "last_updated": student.last_updated.isoformat(),
        }

    def create_student(
        self,
        student_id: str,
        first_name: str,
        last_name: str,
        date_of_birth: datetime,
        grade_level: int = 1,
        school: str = "",
        teacher: str = "",
        autism_level: str = "level_1",
        communication_style: str = "verbal",
    ) -> StudentProfile:
        """
        Create a new student profile.

        Args:
            student_id: Unique student identifier.
            first_name: Student's first name.
            last_name: Student's last name.
            date_of_birth: Student's date of birth.
            grade_level: Current grade level.
            school: School name.
            teacher: Primary classroom teacher name.
            autism_level: Autism support level.
            communication_style: Primary communication style.

        Returns:
            StudentProfile object.

        Raises:
            ValueError: If student already exists.
        """
        if self._get_student_path(student_id).exists():
            raise ValueError(f"Student {student_id} already exists")

        student = StudentProfile(
            student_id=student_id,
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date_of_birth,
            grade_level=grade_level,
            school=school,
            teacher=teacher,
            autism_level=autism_level,
            communication_style=communication_style,
        )

        self.save_student(student)
        return student

    def add_iep_goal(
        self,
        student_id: str,
        goal_id: str,
        title: str,
        domain: str = "academic",
        description: str = "",
        target_percentage: float = 80.0,
        measurement_method: str = "frequency",
        end_date: Optional[datetime] = None,
        notes: str = "",
    ) -> Optional[IEPGoal]:
        """
        Add an IEP goal to a student's profile.

        Args:
            student_id: The student's unique identifier.
            goal_id: Unique goal identifier.
            title: Goal title or target behavior.
            domain: Goal domain (academic, social, communication, motor, sensory).
            description: Detailed goal description.
            target_percentage: Target success percentage (0-100).
            measurement_method: How success is measured.
            end_date: Expected end date for goal achievement.
            notes: Additional notes about the goal.

        Returns:
            IEPGoal object if successful, None if student not found.

        Raises:
            ValueError: If student not found or goal data is invalid.
        """
        student = self.load_student(student_id)
        if student is None:
            raise ValueError(f"Student {student_id} not found")

        # Check if goal already exists
        if student.get_goal_by_id(goal_id) is not None:
            raise ValueError(
                f"Goal {goal_id} already exists for student {student_id}"
            )

        goal = IEPGoal(
            goal_id=goal_id,
            title=title,
            domain=domain,
            description=description,
            target_percentage=target_percentage,
            measurement_method=measurement_method,
            end_date=end_date,
            notes=notes,
        )

        student.iep_goals.append(goal)
        student.last_updated = datetime.utcnow()
        self.save_student(student)

        return goal

    def deactivate_goal(self, student_id: str, goal_id: str) -> bool:
        """
        Deactivate an IEP goal for a student.

        Args:
            student_id: The student's unique identifier.
            goal_id: The goal ID to deactivate.

        Returns:
            True if successful, False if goal not found.
        """
        student = self.load_student(student_id)
        if student is None:
            return False

        goal = student.get_goal_by_id(goal_id)
        if goal is None:
            return False

        goal.is_active = False
        student.last_updated = datetime.utcnow()
        self.save_student(student)

        return True

    def get_goal_progress(
        self,
        student_id: str,
        goal_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Get progress metrics for a specific goal.

        Args:
            student_id: The student's unique identifier.
            goal_id: The goal ID to analyze.

        Returns:
            Dictionary with progress metrics, or None if not found.
        """
        student = self.load_student(student_id)
        if student is None:
            return None

        return student.calculate_goal_progress(goal_id)

    def get_student_progress_summary(self, student_id: str) -> Optional[Dict[str, Any]]:
        """
        Get progress summary across all goals for a student.

        Args:
            student_id: The student's unique identifier.

        Returns:
            Dictionary with overall progress metrics, or None if not found.
        """
        student = self.load_student(student_id)
        if student is None:
            return None

        goal_progress = []
        for goal in student.active_goals:
            progress = student.calculate_goal_progress(goal.goal_id)
            goal_progress.append(progress)

        # Calculate overall statistics
        all_percentages = []
        for goal in student.active_goals:
            trials = student.get_recent_trials(goal.goal_id, limit=10)
            all_percentages.extend(
                [trial.success_percentage for trial in trials]
            )

        overall_average = (
            sum(all_percentages) / len(all_percentages)
            if all_percentages
            else 0.0
        )

        return {
            "student_id": student_id,
            "full_name": student.full_name,
            "goal_count": len(student.active_goals),
            "overall_average_percentage": round(overall_average, 2),
            "total_trials": len(student.trial_history),
            "goal_progress": goal_progress,
            "last_updated": student.last_updated.isoformat(),
        }

    def delete_student(self, student_id: str) -> bool:
        """
        Delete a student profile from storage.

        Args:
            student_id: The student's unique identifier.

        Returns:
            True if successful, False if student not found.
        """
        student_path = self._get_student_path(student_id)

        if not student_path.exists():
            return False

        try:
            student_path.unlink()
            return True
        except OSError as e:
            raise IOError(
                f"Failed to delete student {student_id}: {str(e)}"
            )

    def export_student_data(
        self,
        student_id: str,
        export_path: str,
    ) -> bool:
        """
        Export a student's data to a JSON file.

        Args:
            student_id: The student's unique identifier.
            export_path: Path where the file should be exported.

        Returns:
            True if successful, False if student not found.
        """
        student = self.load_student(student_id)
        if student is None:
            return False

        try:
            export_file = Path(export_path)
            export_file.parent.mkdir(parents=True, exist_ok=True)

            student_data = student.model_dump(
                mode="json",
                exclude_none=False,
            )
            write_json(export_file, student_data)
            return True
        except IOError as e:
            raise IOError(
                f"Failed to export student {student_id}: {str(e)}"
            )
