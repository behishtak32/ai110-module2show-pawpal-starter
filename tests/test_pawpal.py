from datetime import date, timedelta

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task


def test_mark_complete_sets_completed_to_true():
    task = Task("Walk", 30, 1, "Rex")
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_add_task_adds_task_to_pet():
    pet = Pet("Rex", "dog")
    task = Task("Walk", 30, 1, "Rex")
    count_before = len(pet.tasks)

    pet.add_task(task)

    assert len(pet.tasks) == count_before + 1
    assert task in pet.tasks


def make_owner_with_task(task):
    """Return an owner and a pet named Rex that already has the given task."""
    owner = Owner("Sam", 60)
    pet = Pet("Rex", "dog")
    owner.add_pet(pet)
    pet.add_task(task)
    return owner, pet


def test_daily_task_creates_next_occurrence_tomorrow():
    """Completing a daily task adds a separate unfinished copy due tomorrow."""
    task = Task("Walk", 30, 1, "Rex", frequency="daily", scheduled_time="08:00")
    owner, pet = make_owner_with_task(task)

    next_task = Scheduler().complete_task(owner, task)

    assert task.completed is True
    assert next_task is not task
    assert next_task.completed is False
    assert next_task.due_date == date.today() + timedelta(days=1)
    assert (next_task.description, next_task.duration, next_task.priority, next_task.scheduled_time) == (
        "Walk", 30, 1, "08:00"
    )
    assert pet.tasks == [task, next_task]


def test_weekly_task_creates_next_occurrence_in_seven_days():
    """Completing a weekly task adds a copy due one week from today."""
    task = Task("Bath", 20, 2, "Rex", frequency="weekly")
    owner, _ = make_owner_with_task(task)

    next_task = Scheduler().complete_task(owner, task)

    assert next_task.due_date == date.today() + timedelta(days=7)


def test_future_due_date_is_used_as_starting_point():
    """A task already due later than today repeats from its own due date."""
    later = date.today() + timedelta(days=3)
    task = Task("Walk", 30, 1, "Rex", frequency="daily", due_date=later)
    owner, _ = make_owner_with_task(task)

    next_task = Scheduler().complete_task(owner, task)

    assert next_task.due_date == later + timedelta(days=1)


def test_completing_twice_creates_no_duplicate():
    """A second completion of the same task returns None and adds nothing."""
    task = Task("Walk", 30, 1, "Rex", frequency="daily")
    owner, pet = make_owner_with_task(task)
    scheduler = Scheduler()

    scheduler.complete_task(owner, task)
    second = scheduler.complete_task(owner, task)

    assert second is None
    assert len(pet.tasks) == 2


def test_matching_occurrence_is_not_added_twice():
    """No new task is added if one with the same description, date, and time exists."""
    first = Task("Walk", 30, 1, "Rex", frequency="daily", scheduled_time="08:00")
    second = Task("Walk", 30, 1, "Rex", frequency="daily", scheduled_time="08:00")
    owner, pet = make_owner_with_task(first)
    pet.add_task(second)
    scheduler = Scheduler()

    scheduler.complete_task(owner, first)
    result = scheduler.complete_task(owner, second)

    assert result is None
    assert second.completed is True
    assert len(pet.tasks) == 3


def test_nonrecurring_task_creates_no_occurrence():
    """Tasks that are not daily or weekly are completed without repeating."""
    task = Task("Vet visit", 60, 1, "Rex", frequency="as needed")
    owner, pet = make_owner_with_task(task)

    result = Scheduler().complete_task(owner, task)

    assert result is None
    assert task.completed is True
    assert pet.tasks == [task]


def test_task_from_another_owner_is_rejected_unchanged():
    """An equal-looking task that is not the owner's own object raises and stays unfinished."""
    owner, _ = make_owner_with_task(Task("Walk", 30, 1, "Rex"))
    outside_task = Task("Walk", 30, 1, "Rex")

    with pytest.raises(ValueError):
        Scheduler().complete_task(owner, outside_task)

    assert outside_task.completed is False


def test_generate_plan_skips_future_tasks_with_reason():
    """Tasks due after today are skipped with the date in the reason."""
    tomorrow = date.today() + timedelta(days=1)
    task = Task("Walk", 30, 1, "Rex", due_date=tomorrow)
    owner, _ = make_owner_with_task(task)
    scheduler = Scheduler()

    scheduler.generate_plan(owner)

    assert scheduler.selected_tasks == []
    assert scheduler.skipped_tasks == [(task, f"not due until {tomorrow}")]


def test_same_time_tasks_across_pets_conflict():
    """Unfinished tasks for different pets at the same date and time produce one warning."""
    owner = Owner("Sam", 60)
    rex, luna = Pet("Rex", "dog"), Pet("Luna", "cat")
    owner.add_pet(rex)
    owner.add_pet(luna)
    rex.add_task(Task("Walk", 30, 1, "Rex", scheduled_time="08:00"))
    luna.add_task(Task("Feed", 10, 1, "Luna", scheduled_time="8:00"))

    warnings = Scheduler().find_conflicts(owner)

    assert warnings == [f"Conflict on {date.today()} at 08:00: Walk (Rex), Feed (Luna)"]


def test_same_time_on_different_dates_does_not_conflict():
    """Tasks at the same time on different dates are not conflicts."""
    owner = Owner("Sam", 60)
    rex, luna = Pet("Rex", "dog"), Pet("Luna", "cat")
    owner.add_pet(rex)
    owner.add_pet(luna)
    rex.add_task(Task("Walk", 30, 1, "Rex", scheduled_time="08:00"))
    luna.add_task(
        Task("Feed", 10, 1, "Luna", scheduled_time="08:00", due_date=date.today() + timedelta(days=1))
    )

    assert Scheduler().find_conflicts(owner) == []
