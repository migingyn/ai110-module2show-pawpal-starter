from tabulate import tabulate
from pawpal_system import Owner, Pet, Task, Scheduler

owner = Owner("John Doe", [(360, 540), (1080, 1260)], {"prefers_morning": True})
pet1 = Pet("Buddy", "Dog")
pet2 = Pet("Mittens", "Cat")
owner.add_pet(pet1)
owner.add_pet(pet2)

pet1.add_task(Task("Morning walk", 420, "daily", "high"))
pet1.add_task(Task("Vet check-in", 480, "weekly", "high"))   # cross-pet conflict with Feed/Medication
pet1.add_task(Task("Evening play", 1140, "daily", "medium"))
pet2.add_task(Task("Feed", 480, "daily", "high"))            # same-pet conflict with Medication
pet2.add_task(Task("Medication", 480, "twice_daily", "high"))

scheduler = Scheduler(owner)
scheduler.build_schedule()


def _task_rows(tasks):
    return [
        [t.description, t.format_time(), t.priority, t.frequency, "done" if t.completed else "pending"]
        for t in tasks
    ]

HEADERS = ["Task", "Time", "Priority", "Frequency", "Status"]

# --- 1. Sort by time ---
print("\n=== Schedule Sorted by Time ===")
print(tabulate(_task_rows(scheduler.sort_by_time()), headers=HEADERS, tablefmt="rounded_outline"))

# --- 2. Filter by pet ---
print("\n=== Buddy's Tasks ===")
print(tabulate(_task_rows(scheduler.get_tasks_for_pet("Buddy")), headers=HEADERS, tablefmt="rounded_outline"))

print("\n=== Mittens's Tasks ===")
print(tabulate(_task_rows(scheduler.get_tasks_for_pet("Mittens")), headers=HEADERS, tablefmt="rounded_outline"))

# --- 3. Filter by status ---
print("\n=== Pending Tasks ===")
print(tabulate(_task_rows(scheduler.get_tasks_by_status(completed=False)), headers=HEADERS, tablefmt="rounded_outline"))

# --- 4. Conflict warnings ---
print("\n=== Conflict Warnings ===")
warnings = scheduler.get_conflict_warnings()
if warnings:
    for w in warnings:
        print(f"  {w}")
else:
    print("  No conflicts detected.")

# --- 5. Find next available slot ---
print("\n=== Next Available Slot ===")
next_slot_minutes = scheduler.find_next_slot(preferred_time=480)
hour, minute = divmod(next_slot_minutes, 60)
period = "am" if hour < 12 else "pm"
hour = hour % 12 or 12
print(f"  Next free slot after 8:00am -> {hour}:{minute:02d}{period} ({next_slot_minutes} min)")

# --- 6. Auto-rescheduling ---
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

print("\n=== Updated Schedule (after completions) ===")
print(tabulate(_task_rows(scheduler.sort_by_time()), headers=HEADERS, tablefmt="rounded_outline"))
