# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

The first plan printed by `python main.py` (the full run is in the Demo Walkthrough below):

```text
Today's Schedule
Time used: 35 of 40 minutes.
Selected tasks:
  - Walk for Rex (25 min, high priority)
  - Feed for Luna (10 min, high priority)
Skipped tasks:
  - Brush for Luna: needs 15 min but only 5 min left
```

## 🧪 Testing PawPal+

Run the tests with:

```bash
python -m pytest
```

The tests cover task completion, task addition, sorting, filtering, recurring tasks, duplicate prevention, conflicts, time limits, and empty task lists.

### Test Results

```text
============================= test session starts =============================
platform win32 -- Python 3.11.4, pytest-9.1.1, pluggy-1.7.0
rootdir: C:\Users\behis\OneDrive - George Mason University - O365 Production\Desktop\ai110-module2show-pawpal-starter
plugins: anyio-4.15.1
collected 27 items

tests\test_pawpal.py ...........................                         [100%]

============================= 27 passed in 0.03s ==============================
```

### Confidence Level

**★★★★☆ (4/5)**

All 27 tests pass. Conflict detection checks matching start times but does not detect overlapping durations. The tests do not cover every Streamlit interaction.

## ✨ Features

- **Streamlit UI** (`app.py`): edit the owner's name and available minutes, add pets, and add tasks with a description, duration, priority, frequency, optional start time (HH:MM), and due date. Duration (how long a task takes) is separate from start time (when it begins).
- **Sorting**: the task table is sorted by start time with `Scheduler.sort_by_time()`; tasks without a start time appear last.
- **Filtering**: the task table can be filtered by pet and by status (All, Pending, Completed) with `Scheduler.filter_tasks()`.
- **Daily/weekly recurrence**: completing a task through `Scheduler.complete_task()` marks it done and, for daily or weekly tasks, adds the next occurrence 1 or 7 days later. "As needed" tasks do not repeat, and completing the same task twice does not create a duplicate.
- **Conflict warnings**: `Scheduler.find_conflicts()` warns when two or more unfinished tasks share the same due date and start time, listing the date, time, task names, and pets.
- **Daily planning**: `Scheduler.generate_plan()` picks unfinished tasks due today or earlier, highest priority first, until the owner's available minutes run out. `Scheduler.explain_choices()` lists the selected tasks and the reason each other task was skipped.

### Limitations

- **Conflicts only detect matching start times, not overlapping durations.** A 30-minute task at 08:00 and another task at 08:15 are not flagged.
- **Session data is not permanently saved.** The owner, pets, and tasks live in Streamlit's `st.session_state` and are lost when the browser session ends or the app restarts.

## 📐 Smarter Scheduling

| Feature | Method | Behavior |
|---|---|---|
| Sorting | Scheduler.sort_by_time() | Sorts by HH:MM start time; untimed tasks appear last. |
| Filtering | Scheduler.filter_tasks() | Filters tasks by pet name, completion status, or both. |
| Recurring tasks | Scheduler.complete_task() | Creates the next daily or weekly occurrence and prevents duplicates. |
| Conflict detection | Scheduler.find_conflicts() | Warns when unfinished tasks share a date and start time across any pets. |
| Daily planning | Scheduler.generate_plan() | Selects unfinished tasks by priority within the time budget and skips future tasks. |

## 📐 Architecture

The final class diagram is in [diagrams/uml_final.mmd](diagrams/uml_final.mmd). It shows that an Owner has Pets, each Pet has Tasks, and the Scheduler reaches tasks across all pets through `Owner.get_all_tasks()`.

## 📸 Demo Walkthrough

Start the app with:

```bash
streamlit run app.py
```

1. **Set up the owner.** The app starts with an owner named Jordan who has 60 available minutes. Change the name or minutes in the Owner form and click **Save owner**.
2. **Add pets.** Enter a pet name, choose a species (dog, cat, or other), and click **Add pet**. Pet names must be unique.
3. **Add tasks.** Choose a pet and enter a description, duration in minutes, priority (high, medium, low), and frequency (daily, weekly, as needed). Optionally enter a start time such as `08:00` and pick a due date (today by default), then click **Add task**.
4. **Filter and sort the table.** The task table shows each task's pet, description, date, time, duration, priority, frequency, and completion status, sorted by start time with untimed tasks last. Use **Show pet** and **Show status** to narrow it down.
5. **Complete a recurring task.** Choose a pending task in **Mark a task complete** (each option shows its pet, date, and time, so tasks with the same name can be told apart) and click **Complete task**. For a daily or weekly task, a success message shows the due date of the next occurrence, which then appears in the table.
6. **View conflict warnings.** If two unfinished tasks share the same date and start time, a warning such as `Conflict on 2026-10-25 at 07:30: Give medicine (Rex), Feed (Luna)` appears below the task controls.
7. **Generate today's plan.** Click **Generate schedule** to see how many tasks fit, the time used, the selected tasks, and why each other task was skipped (already completed, not due yet, or not enough time left).

### CLI demo

`main.py` runs the same backend without the UI. Output of `python main.py` (dates depend on the day it is run):

```text
Today's Schedule
Time used: 35 of 40 minutes.
Selected tasks:
  - Walk for Rex (25 min, high priority)
  - Feed for Luna (10 min, high priority)
Skipped tasks:
  - Brush for Luna: needs 15 min but only 5 min left

All Tasks by Time
    07:30  Feed (Luna)
    12:15  Brush (Luna)
    18:00  Walk (Rex)
  no time  Clean litter box (Luna)

Luna's Unfinished Tasks
  - Feed
  - Clean litter box

Recurring Tasks
  Completed Walk (due 2026-10-25); next due 2026-10-26
  Completed Bath (due 2026-10-25); next due 2026-11-01
  Completing Walk again returned None; Rex's task count: 4 before, 4 after

Today's Schedule After Completing Tasks
Time used: 20 of 40 minutes.
Selected tasks:
  - Feed for Luna (10 min, high priority)
  - Clean litter box for Luna (10 min, medium priority)
Skipped tasks:
  - Walk for Rex: already completed
  - Walk for Rex: not due until 2026-10-26
  - Bath for Rex: already completed
  - Bath for Rex: not due until 2026-11-01
  - Brush for Luna: already completed

Schedule Conflicts
  WARNING: Conflict on 2026-10-25 at 07:30: Give medicine (Rex), Feed (Luna)
```

## Implementation Summary

PawPal+ creates a daily pet care plan based on the owner's available time and task priorities. Task stores an activity's description, duration, priority, frequency, pet name, completion status, scheduled_time (an optional HH:MM start time), and due_date. Pet manages its tasks, and Owner manages multiple pets and combines their tasks through get_all_tasks(). Scheduler uses this combined list to select unfinished tasks that fit the time budget and explain why other tasks were skipped.

The main.py script demonstrates scheduling across two pets. 27 pytest tests verify task completion, task addition, sorting, filtering, recurring tasks, duplicate prevention, conflicts, time limits, and empty task lists.
