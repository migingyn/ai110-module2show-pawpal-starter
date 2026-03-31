from pawpal_system import Owner, Pet, Task, Scheduler

owner = Owner("John Doe", [(360, 540), (1080, 1260)], {"prefers_morning": True})
pet1 = Pet("Buddy", "Dog")
pet2 = Pet("Mittens", "Cat")
owner.add_pet(pet1)
owner.add_pet(pet2)

pet1.add_task(Task("Morning walk", 420, "daily", "high"))
pet1.add_task(Task("Evening play", 1140, "daily", "medium"))
pet2.add_task(Task("Feed", 480, "daily", "high"))
pet2.add_task(Task("Medication", 480, "twice_daily", "high"))

scheduler = Scheduler(owner)
scheduler.build_schedule()

# --- 1. Sort by time (chronological view) ---
print("=== Schedule Sorted by Time ===")
for task in scheduler.sort_by_time():
    print(f"  {task}")

# --- 2. Filter by pet ---
print("\n=== Buddy's Tasks ===")
for task in scheduler.get_tasks_for_pet("Buddy"):
    print(f"  {task}")

print("\n=== Mittens's Tasks ===")
for task in scheduler.get_tasks_for_pet("Mittens"):
    print(f"  {task}")

# --- 3. Filter by status ---
print("\n=== Pending Tasks (before any completions) ===")
for task in scheduler.get_tasks_by_status(completed=False):
    print(f"  {task}")

# --- 4. Conflict detection ---
print("\n=== Conflict Detection ===")
conflicts = scheduler.detect_conflicts()
if conflicts:
    for t1, t2 in conflicts:
        print(f"  CONFLICT: '{t1.description}' and '{t2.description}' both at {t1.format_time()}")
else:
    print("  No conflicts detected.")

# --- 5. Auto-rescheduling via timedelta ---
print("\n=== Auto-Rescheduling Demo ===")
morning_walk = scheduler.get_tasks_for_pet("Buddy")[0]
print(f"  Completing: {morning_walk}")
next_walk = scheduler.mark_complete(morning_walk)
if next_walk:
    print(f"  Auto-scheduled next: {next_walk}")

feed_task = scheduler.get_tasks_for_pet("Mittens")[0]
print(f"  Completing: {feed_task}")
next_feed = scheduler.mark_complete(feed_task)
if next_feed:
    print(f"  Auto-scheduled next: {next_feed}")

print("\n=== Updated Schedule (Completed + Rescheduled) ===")
for task in scheduler.sort_by_time():
    print(f"  {task}")
