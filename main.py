from pawpal_system import Owner, Pet, Task, Scheduler
owner = Owner(name="Marwa", available_minutes=40)

# Create two pets.
dog = Pet(name="Rex", species="Dog")
cat = Pet(name="Luna", species="Cat")

owner.add_pet(dog)
owner.add_pet(cat)

# Add three tasks with different durations.
dog.add_task(Task("Walk", 25, 1, "Rex"))
cat.add_task(Task("Feed", 10, 1, "Luna"))
cat.add_task(Task("Brush", 15, 3, "Luna"))

# Generate and print a plan covering both pets.
scheduler = Scheduler()
scheduler.generate_plan(owner)

print("Today's Schedule")
print(scheduler.explain_choices())