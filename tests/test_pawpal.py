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


def make_owner_with_two_pets(available_minutes=60):
    """Return an owner with two empty pets, Rex the dog and Luna the cat."""
    owner = Owner("Sam", available_minutes)
    rex, luna = Pet("Rex", "dog"), Pet("Luna", "cat")
    owner.add_pet(rex)
    owner.add_pet(luna)
    return owner, rex, luna


# --- Sorting ---


def test_sort_by_time_returns_chronological_order():
    """Tasks come back from earliest to latest start time."""
    afternoon = Task("Play", 20, 2, "Rex", scheduled_time="14:00")
    morning = Task("Walk", 30, 1, "Rex", scheduled_time="08:00")
    midday = Task("Feed", 10, 1, "Rex", scheduled_time="11:30")

    result = Scheduler().sort_by_time([afternoon, morning, midday])

    assert result == [morning, midday, afternoon]


def test_sort_by_time_puts_9_00_before_10_00():
    """A short time like "9:00" is stored as "09:00", so it sorts before "10:00"."""
    ten = Task("Feed", 10, 1, "Rex", scheduled_time="10:00")
    nine = Task("Walk", 30, 1, "Rex", scheduled_time="9:00")

    result = Scheduler().sort_by_time([ten, nine])

    assert nine.scheduled_time == "09:00"
    assert result == [nine, ten]


def test_sort_by_time_puts_untimed_tasks_last():
    """Tasks without a start time go after every timed task."""
    untimed = Task("Brush", 5, 3, "Rex")
    late = Task("Play", 20, 2, "Rex", scheduled_time="23:00")

    result = Scheduler().sort_by_time([untimed, late])

    assert result == [late, untimed]


def test_sort_by_time_leaves_original_list_unchanged():
    """Sorting returns a new list instead of reordering the one passed in."""
    late = Task("Play", 20, 2, "Rex", scheduled_time="14:00")
    early = Task("Walk", 30, 1, "Rex", scheduled_time="08:00")
    tasks = [late, early]

    Scheduler().sort_by_time(tasks)

    assert tasks == [late, early]


# --- Filtering ---


def make_owner_for_filtering():
    """Return an owner whose pets have a mix of finished and unfinished tasks."""
    owner, rex, luna = make_owner_with_two_pets()
    walk = Task("Walk", 30, 1, "Rex", completed=True)
    feed_rex = Task("Feed", 10, 1, "Rex")
    feed_luna = Task("Feed", 10, 1, "Luna")
    rex.add_task(walk)
    rex.add_task(feed_rex)
    luna.add_task(feed_luna)
    return owner, walk, feed_rex, feed_luna


def test_filter_by_pet_returns_only_that_pets_tasks():
    owner, walk, feed_rex, _ = make_owner_for_filtering()

    assert Scheduler().filter_tasks(owner, pet_name="Rex") == [walk, feed_rex]


def test_filter_by_completion_status():
    owner, walk, feed_rex, feed_luna = make_owner_for_filtering()
    scheduler = Scheduler()

    assert scheduler.filter_tasks(owner, completed=True) == [walk]
    assert scheduler.filter_tasks(owner, completed=False) == [feed_rex, feed_luna]


def test_filter_by_pet_and_status_together():
    owner, _, feed_rex, _ = make_owner_for_filtering()

    result = Scheduler().filter_tasks(owner, pet_name="Rex", completed=False)

    assert result == [feed_rex]


def test_filter_by_unknown_pet_returns_empty_list():
    owner, _, _, _ = make_owner_for_filtering()

    assert Scheduler().filter_tasks(owner, pet_name="Milo") == []


# --- Time budget ---


def test_task_that_exactly_fits_is_selected():
    """A task needing exactly the minutes available is still selected."""
    owner = Owner("Sam", 30)
    pet = Pet("Rex", "dog")
    owner.add_pet(pet)
    walk = Task("Walk", 30, 1, "Rex")
    pet.add_task(walk)
    scheduler = Scheduler()

    scheduler.generate_plan(owner)

    assert scheduler.selected_tasks == [walk]
    assert scheduler.total_duration == 30


def test_oversized_task_is_skipped_but_smaller_task_still_fits():
    """A task that is too long is skipped, and a later shorter task is still selected."""
    owner = Owner("Sam", 40)
    pet = Pet("Rex", "dog")
    owner.add_pet(pet)
    grooming = Task("Grooming", 50, 1, "Rex")
    feed = Task("Feed", 10, 2, "Rex")
    pet.add_task(grooming)
    pet.add_task(feed)
    scheduler = Scheduler()

    scheduler.generate_plan(owner)

    assert scheduler.selected_tasks == [feed]
    assert scheduler.skipped_tasks == [(grooming, "needs 50 min but only 40 min left")]


def test_zero_minutes_selects_nothing():
    owner = Owner("Sam", 0)
    pet = Pet("Rex", "dog")
    owner.add_pet(pet)
    pet.add_task(Task("Feed", 10, 1, "Rex"))
    scheduler = Scheduler()

    scheduler.generate_plan(owner)

    assert scheduler.selected_tasks == []
    assert len(scheduler.skipped_tasks) == 1


# --- Empty cases ---


def test_owner_with_no_pets_gives_empty_results():
    owner = Owner("Sam", 60)
    scheduler = Scheduler()

    assert scheduler.generate_plan(owner) == []
    assert scheduler.filter_tasks(owner) == []
    assert scheduler.find_conflicts(owner) == []
    assert "(none)" in scheduler.explain_choices()


def test_pet_with_no_tasks_gives_empty_results():
    owner = Owner("Sam", 60)
    owner.add_pet(Pet("Rex", "dog"))
    scheduler = Scheduler()

    assert scheduler.generate_plan(owner) == []
    assert scheduler.filter_tasks(owner, pet_name="Rex") == []
    assert scheduler.find_conflicts(owner) == []
    assert scheduler.sort_by_time([]) == []


# --- Conflicts ---


def test_completed_tasks_do_not_conflict():
    """A finished task at the same time as an unfinished one is not a conflict."""
    owner, rex, luna = make_owner_with_two_pets()
    rex.add_task(Task("Walk", 30, 1, "Rex", scheduled_time="08:00", completed=True))
    luna.add_task(Task("Feed", 10, 1, "Luna", scheduled_time="08:00"))

    assert Scheduler().find_conflicts(owner) == []


def test_untimed_tasks_do_not_conflict():
    """Tasks with no start time are never reported as conflicts."""
    owner, rex, luna = make_owner_with_two_pets()
    rex.add_task(Task("Walk", 30, 1, "Rex"))
    luna.add_task(Task("Feed", 10, 1, "Luna"))

    assert Scheduler().find_conflicts(owner) == []
