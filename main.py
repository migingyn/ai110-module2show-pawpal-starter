from pawpal_system import Owner, Pet, Task, Scheduler

owner = Owner("John Doe", [(360, 540), (1080, 1260)], {"prefers_morning": True})
pet1 = Pet("Buddy", "Dog")
pet2 = Pet("Mittens", "Cat")
owner.add_pet(pet1)
owner.add_pet(pet2)

pet1.add_task(Task("Morning walk", 420, "daily", "high"))
pet1.add_task(Task("Evening play", 1140, "daily", "medium"))
pet2.add_task(Task("Feed", 480, "daily", "high"))

scheduler = Scheduler(owner)
scheduler.build_schedule()

print("=== Today's Schedule ===")
print(scheduler.explain())
