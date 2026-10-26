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
                )
                chosen_pet.add_task(task)
                st.success(f"Added '{task.description}' for {chosen_pet.name}.")
            except ValueError as error:
                st.error(str(error))

# --- Current pets and tasks ---
st.divider()
st.subheader(f"{owner.name}'s pets")

if not owner.pets:
    st.info("No pets yet.")
else:
    for pet in owner.pets:
        st.markdown(f"**{pet.name}** ({pet.species})")
        if pet.tasks:
            st.table(
                [
                    {
                        "Task": task.description,
                        "Minutes": task.duration,
                        "Priority": PRIORITY_NAMES[task.priority],
                        "Frequency": task.frequency,
                        "Done": "yes" if task.completed else "no",
                    }
                    for task in pet.tasks
                ]
            )
        else:
            st.caption("No tasks yet.")

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
        scheduler = Scheduler()
        selected = scheduler.generate_plan(owner)
        if selected:
            st.success(f"Scheduled {len(selected)} task(s).")
        else:
            st.warning("No tasks fit into today's available time.")
        st.text(scheduler.explain_choices())
