"""PawPal+ core classes: Owner, Pet, Task, and Scheduler."""

from dataclasses import dataclass, field, replace
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

VALID_PRIORITIES = (1, 2, 3)
PRIORITY_LABELS = {1: "high", 2: "medium", 3: "low"}
RECURRENCE_DAYS = {"daily": 1, "weekly": 7}  # other frequencies do not repeat


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


def _normalize_time(time_text: str) -> str:
    """Return a valid time as zero-padded HH:MM, or raise an error if it is invalid."""
    try:
        parsed = datetime.strptime(time_text.strip(), "%H:%M")
    except ValueError:
        raise ValueError(
            f"Time must be in HH:MM format (00:00 to 23:59), got '{time_text}'."
        ) from None
    return parsed.strftime("%H:%M")


@dataclass
class Task:
    """A single care task for one pet.

    Priority: 1 = high, 2 = medium, 3 = low.
    Tasks with equal priority keep their original order when scheduled.
    Daily and weekly tasks repeat when completed through Scheduler.complete_task().
    Duration is how long the task takes; scheduled_time is when it starts.
    """

    description: str
    duration: int  # minutes
    priority: int  # 1 (high) to 3 (low)
    pet_name: str
    frequency: str = "daily"
    completed: bool = False
    scheduled_time: Optional[str] = None  # start time as "HH:MM", or None if not set
    due_date: date = field(default_factory=date.today)

    def __post_init__(self) -> None:
        """Check the starting values when a task is created."""
        _check_duration(self.duration)
        _check_priority(self.priority)
        if self.scheduled_time is not None:
            self.scheduled_time = _normalize_time(self.scheduled_time)

    def update_details(
        self,
        description: Optional[str] = None,
        duration: Optional[int] = None,
        priority: Optional[int] = None,
        frequency: Optional[str] = None,
        scheduled_time: Optional[str] = None,
    ) -> None:
        """Update any of the task's details. Details left as None are not changed."""
        if duration is not None:
            _check_duration(duration)
        if priority is not None:
            _check_priority(priority)
        if scheduled_time is not None:
            scheduled_time = _normalize_time(scheduled_time)

        if description is not None:
            self.description = description
        if duration is not None:
            self.duration = duration
        if priority is not None:
            self.priority = priority
        if frequency is not None:
            self.frequency = frequency
        if scheduled_time is not None:
            self.scheduled_time = scheduled_time

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
        """Update the first task with this description using update_details() keyword names."""
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
        """Select incomplete tasks due by today, by priority, that fit the owner's time."""
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
            if task.due_date > date.today():
                self.skipped_tasks.append((task, f"not due until {task.due_date}"))
                continue

            minutes_left = self.available_minutes - self.total_duration
            if task.duration <= minutes_left:
                self.selected_tasks.append(task)
                self.total_duration += task.duration
            else:
                reason = f"needs {task.duration} min but only {minutes_left} min left"
                self.skipped_tasks.append((task, reason))

        return self.selected_tasks

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """Return a new list sorted by scheduled time, with untimed tasks last."""
        # False sorts before True, so tasks with a time come first.
        return sorted(tasks, key=lambda task: (task.scheduled_time is None, task.scheduled_time or ""))

    def filter_tasks(
        self, owner: Owner, pet_name: Optional[str] = None, completed: Optional[bool] = None
    ) -> List[Task]:
        """Return the owner's tasks matching a pet name and/or completion status (None means any)."""
        tasks = owner.get_all_tasks()
        if pet_name is not None:
            tasks = [task for task in tasks if task.pet_name == pet_name]
        if completed is not None:
            tasks = [task for task in tasks if task.completed == completed]
        return tasks

    def complete_task(self, owner: Owner, task: Task) -> Optional[Task]:
        """Mark a task complete and add its next daily/weekly occurrence; return it or None."""
        # Use "is" so only this exact task object counts, not an equal-looking copy.
        task_pet = None
        for pet in owner.pets:
            if any(existing is task for existing in pet.tasks):
                task_pet = pet
                break
        if task_pet is None:
            raise ValueError(f"Task '{task.description}' does not belong to any of {owner.name}'s pets.")

        # Completing a task twice must not create a second occurrence.
        if task.completed:
            return None
        task.mark_complete()

        days = RECURRENCE_DAYS.get(task.frequency.strip().lower())
        if days is None:
            return None

        # Count from the task's own due date if it is later than today.
        start_date = max(date.today(), task.due_date)
        next_task = replace(task, due_date=start_date + timedelta(days=days), completed=False)

        for existing in task_pet.tasks:
            if (
                existing.description == next_task.description
                and existing.due_date == next_task.due_date
                and existing.scheduled_time == next_task.scheduled_time
            ):
                return None

        task_pet.add_task(next_task)
        return next_task

    def find_conflicts(self, owner: Owner) -> List[str]:
        """Return a warning for each date and start time shared by two or more unfinished tasks."""
        groups: Dict[Tuple[date, str], List[Task]] = {}
        for task in owner.get_all_tasks():
            if task.completed or task.scheduled_time is None:
                continue
            key = (task.due_date, task.scheduled_time)
            groups.setdefault(key, []).append(task)

        warnings = []
        for (due_date, start_time), tasks in sorted(groups.items()):
            if len(tasks) >= 2:
                names = ", ".join(f"{task.description} ({task.pet_name})" for task in tasks)
                warnings.append(f"Conflict on {due_date} at {start_time}: {names}")
        return warnings

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
