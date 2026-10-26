"""PawPal+ core classes: Owner, Pet, Task, and Scheduler."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

VALID_PRIORITIES = (1, 2, 3)
PRIORITY_LABELS = {1: "high", 2: "medium", 3: "low"}


def _check_duration(duration: int) -> None:
    """Raise an error if the duration is not a positive number of minutes."""
    if duration <= 0:
        raise ValueError(f"Duration must be positive, got {duration}.")


def _check_priority(priority: int) -> None:
    """Raise an error if the priority is not 1, 2, or 3."""
    if priority not in VALID_PRIORITIES:
        raise ValueError(f"Priority must be 1 (high), 2 (medium), or 3 (low), got {priority}.")


def _check_minutes(minutes: int) -> None:
    """Raise an error if the available time is negative."""
    if minutes < 0:
        raise ValueError(f"Available minutes cannot be negative, got {minutes}.")


@dataclass
class Task:
    """A single care task for one pet.

    Priority: 1 = high, 2 = medium, 3 = low.
    Tasks with equal priority keep their original order when scheduled.
    Frequency (for example "daily" or "weekly") is stored as information only.
    """

    description: str
    duration: int  # minutes
    priority: int  # 1 (high) to 3 (low)
    pet_name: str
    frequency: str = "daily"
    completed: bool = False

    def __post_init__(self) -> None:
        """Check the starting values when a task is created."""
        _check_duration(self.duration)
        _check_priority(self.priority)

    def update_details(
        self,
        description: Optional[str] = None,
        duration: Optional[int] = None,
        priority: Optional[int] = None,
        frequency: Optional[str] = None,
    ) -> None:
        """Update any of the task's details. Details left as None are not changed."""
        if duration is not None:
            _check_duration(duration)
        if priority is not None:
            _check_priority(priority)

        if description is not None:
            self.description = description
        if duration is not None:
            self.duration = duration
        if priority is not None:
            self.priority = priority
        if frequency is not None:
            self.frequency = frequency

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True


@dataclass
class Pet:
    name: str
    species: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet. The task's pet_name must match this pet."""
        if task.pet_name != self.name:
            raise ValueError(
                f"Task '{task.description}' is for '{task.pet_name}', not '{self.name}'."
            )
        self.tasks.append(task)

    def edit_task(self, description: str, new_details: Dict[str, Any]) -> None:
        """Find the first task with this description and update it.

        new_details uses the same names as Task.update_details,
        for example {"duration": 20, "priority": 1}.
        """
        for task in self.tasks:
            if task.description == description:
                task.update_details(**new_details)
                return
        raise ValueError(f"{self.name} has no task called '{description}'.")


@dataclass
class Owner:
    name: str
    available_minutes: int
    pets: List[Pet] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Check the starting available time when an owner is created."""
        _check_minutes(self.available_minutes)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner. Pet names must be unique so tasks can find their pet."""
        for existing in self.pets:
            if existing.name == pet.name:
                raise ValueError(f"{self.name} already has a pet named '{pet.name}'.")
        self.pets.append(pet)

    def update_available_time(self, minutes: int) -> None:
        """Set how many minutes the owner has for pet care today."""
        _check_minutes(minutes)
        self.available_minutes = minutes

    def get_all_tasks(self) -> List[Task]:
        """Return the tasks of all this owner's pets, in pet order then task order."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks


@dataclass
class Scheduler:
    selected_tasks: List[Task] = field(default_factory=list)
    skipped_tasks: List[Tuple[Task, str]] = field(default_factory=list)  # (task, reason)
    total_duration: int = 0
    available_minutes: int = 0

    def generate_plan(self, owner: Owner) -> List[Task]:
        """Pick tasks from the owner's pets by priority to fit their available time.

        Completed tasks are skipped. Tasks are checked from high to low priority;
        a task that does not fit is skipped and the next task is still checked.
        Returns the selected tasks.
        """
        # Start fresh so running the plan twice does not repeat tasks.
        self.selected_tasks = []
        self.skipped_tasks = []
        self.total_duration = 0
        self.available_minutes = owner.available_minutes

        # sorted() keeps the original order for tasks with equal priority.
        tasks = sorted(owner.get_all_tasks(), key=lambda task: task.priority)

        for task in tasks:
            if task.completed:
                self.skipped_tasks.append((task, "already completed"))
                continue

            minutes_left = self.available_minutes - self.total_duration
            if task.duration <= minutes_left:
                self.selected_tasks.append(task)
                self.total_duration += task.duration
            else:
                reason = f"needs {task.duration} min but only {minutes_left} min left"
                self.skipped_tasks.append((task, reason))

        return self.selected_tasks

    def explain_choices(self) -> str:
        """Explain which tasks were selected and why the others were skipped."""
        lines = [
            f"Time used: {self.total_duration} of {self.available_minutes} minutes."
        ]

        lines.append("Selected tasks:")
        if self.selected_tasks:
            for task in self.selected_tasks:
                lines.append(
                    f"  - {task.description} for {task.pet_name} "
                    f"({task.duration} min, {PRIORITY_LABELS[task.priority]} priority)"
                )
        else:
            lines.append("  (none)")

        lines.append("Skipped tasks:")
        if self.skipped_tasks:
            for task, reason in self.skipped_tasks:
                lines.append(f"  - {task.description} for {task.pet_name}: {reason}")
        else:
            lines.append("  (none)")

        return "\n".join(lines)
