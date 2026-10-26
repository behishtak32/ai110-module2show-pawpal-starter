from datetime import date

import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

PRIORITY_VALUES = {"high": 1, "medium": 2, "low": 3}
PRIORITY_NAMES = {1: "high", 2: "medium", 3: "low"}

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("Plan your pets' daily care based on your available time and task priorities.")

# Keep one Owner across reruns so pets and tasks are not lost.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", available_minutes=60)

owner = st.session_state.owner
scheduler = Scheduler()

# --- Owner ---
st.divider()
st.subheader("Owner")

with st.form("owner_form"):
    new_name = st.text_input("Owner name", value=owner.name)
    new_minutes = st.number_input(
        "Available minutes today", min_value=0, max_value=1440, value=owner.available_minutes
    )
    save_owner = st.form_submit_button("Save owner")

if save_owner:
    if not new_name.strip():
        st.error("Owner name cannot be empty.")
    else:
        try:
            owner.update_available_time(int(new_minutes))
            owner.name = new_name.strip()
            st.success(f"Saved: {owner.name} has {owner.available_minutes} minutes today.")
        except ValueError as error:
            st.error(str(error))

# --- Add pet ---
st.divider()
st.subheader("Add pet")

with st.form("pet_form", clear_on_submit=True):
    pet_name = st.text_input("Pet name")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    add_pet = st.form_submit_button("Add pet")

if add_pet:
    if not pet_name.strip():
        st.error("Pet name cannot be empty.")
    else:
        try:
            owner.add_pet(Pet(name=pet_name.strip(), species=species))
            st.success(f"Added {pet_name.strip()}.")
        except ValueError as error:
            st.error(str(error))

# --- Add task ---
st.divider()
st.subheader("Add task")

if not owner.pets:
    st.info("Add a pet first, then you can give it tasks.")
else:
    with st.form("task_form", clear_on_submit=True):
        chosen_pet_name = st.selectbox("Pet", [pet.name for pet in owner.pets])
        description = st.text_input("Task description", value="Morning walk")
        col1, col2, col3 = st.columns(3)
        with col1:
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        with col2:
            priority_label = st.selectbox("Priority", ["high", "medium", "low"])
        with col3:
            frequency = st.selectbox("Frequency", ["daily", "weekly", "as needed"])
        col4, col5 = st.columns(2)
        with col4:
            start_time = st.text_input("Start time (HH:MM, optional)", placeholder="08:00")
        with col5:
            due_date = st.date_input("Due date", value=date.today())
        add_task = st.form_submit_button("Add task")

    if add_task:
        if not description.strip():
            st.error("Task description cannot be empty.")
        else:
            chosen_pet = next(pet for pet in owner.pets if pet.name == chosen_pet_name)
            try:
                task = Task(
                    description=description.strip(),
                    duration=int(duration),
                    priority=PRIORITY_VALUES[priority_label],
                    pet_name=chosen_pet.name,
                    frequency=frequency,
                    scheduled_time=start_time.strip() or None,
                    due_date=due_date,
                )
                chosen_pet.add_task(task)
                st.success(f"Added '{task.description}' for {chosen_pet.name}.")
            except ValueError as error:
                st.error(str(error))

# --- Tasks ---
st.divider()
st.subheader(f"{owner.name}'s tasks")

if not owner.pets:
    st.info("No pets yet.")
else:
    st.caption("Pets: " + ", ".join(f"{pet.name} ({pet.species})" for pet in owner.pets))

    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        pet_choice = st.selectbox("Show pet", ["All pets"] + [pet.name for pet in owner.pets])
    with filter_col2:
        status_choice = st.selectbox("Show status", ["All", "Pending", "Completed"])

    pet_filter = None if pet_choice == "All pets" else pet_choice
    status_filter = {"All": None, "Pending": False, "Completed": True}[status_choice]
    shown_tasks = scheduler.sort_by_time(
        scheduler.filter_tasks(owner, pet_name=pet_filter, completed=status_filter)
    )

    if shown_tasks:
        st.table(
            [
                {
                    "Pet": task.pet_name,
                    "Task": task.description,
                    "Date": task.due_date.isoformat(),
                    "Time": task.scheduled_time or "-",
                    "Minutes": task.duration,
                    "Priority": PRIORITY_NAMES[task.priority],
                    "Frequency": task.frequency,
                    "Done": "yes" if task.completed else "no",
                }
                for task in shown_tasks
            ]
        )
    else:
        st.caption("No tasks match these filters.")

    # --- Complete a task ---
    # Show the result of a completion from the previous run.
    if "completion_message" in st.session_state:
        kind, message = st.session_state.pop("completion_message")
        if kind == "success":
            st.success(message)
        else:
            st.info(message)

    pending_tasks = scheduler.sort_by_time(scheduler.filter_tasks(owner, completed=False))
    if pending_tasks:
        # Options are list positions, so tasks with the same description stay distinct.
        chosen_index = st.selectbox(
            "Mark a task complete",
            range(len(pending_tasks)),
            format_func=lambda i: (
                f"{pending_tasks[i].pet_name}: {pending_tasks[i].description} "
                f"({pending_tasks[i].due_date}, {pending_tasks[i].scheduled_time or 'no time'})"
            ),
        )
        if st.button("Complete task"):
            task = pending_tasks[chosen_index]
            next_task = scheduler.complete_task(owner, task)
            if next_task is not None:
                st.session_state.completion_message = (
                    "success",
                    f"Completed '{task.description}' for {task.pet_name}. "
                    f"Next {task.frequency} occurrence added for {next_task.due_date}.",
                )
            else:
                st.session_state.completion_message = (
                    "info",
                    f"Completed '{task.description}' for {task.pet_name}.",
                )
            # Rerun so the table, conflicts, and schedule reflect the change.
            st.rerun()

    # --- Conflicts ---
    for warning in scheduler.find_conflicts(owner):
        st.warning(warning)

# --- Schedule ---
st.divider()
st.subheader("Build schedule")
st.caption(f"Time budget: {owner.available_minutes} minutes.")

if st.button("Generate schedule"):
    if not owner.pets:
        st.warning("Add at least one pet before generating a schedule.")
    elif not owner.get_all_tasks():
        st.warning("Add at least one task before generating a schedule.")
    else:
        selected = scheduler.generate_plan(owner)
        if selected:
            st.success(f"Scheduled {len(selected)} task(s).")
        else:
            st.warning("No tasks fit into today's available time.")
        st.text(scheduler.explain_choices())
