"""PawPal+ core classes: Owner, Pet, CareTask, and DailyPlan."""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class CareTask:
    name: str
    duration: int  # minutes
    priority: int

    def update_details(self, name: str, duration: int, priority: int) -> None:
        """Update this task's name, duration, and priority."""
        pass


@dataclass
class Pet:
    name: str
    species: str
    care_tasks: List[CareTask] = field(default_factory=list)

    def add_task(self, task: CareTask) -> None:
        """Add a care task to this pet."""
        pass

    def edit_task(self, task_name: str, new_details: Dict[str, Any]) -> None:
        """Find a task by name and apply the new details to it."""
        pass


@dataclass
class Owner:
    name: str
    available_minutes: int
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        pass

    def update_available_time(self, minutes: int) -> None:
        """Set how many minutes the owner has for pet care today."""
        pass


@dataclass
class DailyPlan:
    selected_tasks: List[CareTask] = field(default_factory=list)
    total_duration: int = 0

    def generate_plan(self, owner: Owner) -> None:
        """Pick tasks from the owner's pets by priority to fit their available time."""
        pass

    def explain_choices(self) -> str:
        """Explain why each task was or wasn't included in the plan."""
        pass
