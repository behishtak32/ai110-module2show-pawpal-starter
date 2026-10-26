from pawpal_system import Owner, Pet, Task, Scheduler
owner = Owner(name="Marwa", available_minutes=40)

# Create two pets.
dog = Pet(name="Rex", species="Dog")
cat = Pet(name="Luna", species="Cat")

owner.add_pet(dog)
owner.add_pet(cat)

# Add three tasks with different durations, deliberately out of time order.
dog.add_task(Task("Walk", 25, 1, "Rex", scheduled_time="18:00"))
cat.add_task(Task("Feed", 10, 1, "Luna", scheduled_time="7:30"))
cat.add_task(Task("Brush", 15, 3, "Luna", scheduled_time="12:15"))

# Generate and print a plan covering both pets.
scheduler = Scheduler()
scheduler.generate_plan(owner)

print("Today's Schedule")
print(scheduler.explain_choices())

# Add a task with no time; it should appear last when sorting.
cat.add_task(Task("Clean litter box", 10, 2, "Luna"))

print()
print("All Tasks by Time")
for task in scheduler.sort_by_time(owner.get_all_tasks()):
    time_text = task.scheduled_time or "no time"
    print(f"  {time_text:>7}  {task.description} ({task.pet_name})")

# Finish one of Luna's tasks, then show only her unfinished ones.
cat.tasks[1].mark_complete()

print()
print("Luna's Unfinished Tasks")
for task in scheduler.filter_tasks(owner, pet_name="Luna", completed=False):
    print(f"  - {task.description}")

# Recurring tasks: completing a daily or weekly task adds its next occurrence.
dog.add_task(Task("Bath", 20, 2, "Rex", frequency="weekly", scheduled_time="10:00"))
walk = dog.tasks[0]  # daily
bath = dog.tasks[1]  # weekly

print()
print("Recurring Tasks")
next_walk = scheduler.complete_task(owner, walk)
print(f"  Completed {walk.description} (due {walk.due_date}); next due {next_walk.due_date}")
next_bath = scheduler.complete_task(owner, bath)
print(f"  Completed {bath.description} (due {bath.due_date}); next due {next_bath.due_date}")

count_before = len(dog.tasks)
again = scheduler.complete_task(owner, walk)
print(f"  Completing {walk.description} again returned {again}; "
      f"Rex's task count: {count_before} before, {len(dog.tasks)} after")

# The new occurrences are dated in the future, so today's plan skips them.
scheduler.generate_plan(owner)
print()
print("Today's Schedule After Completing Tasks")
print(scheduler.explain_choices())

# Conflicts: two unfinished tasks for different pets at the same date and time.
dog.add_task(Task("Give medicine", 5, 1, "Rex", scheduled_time="07:30"))

print()
print("Schedule Conflicts")
conflicts = scheduler.find_conflicts(owner)
if conflicts:
    for warning in conflicts:
        print(f"  WARNING: {warning}")
else:
    print("  No conflicts found.")
