from datetime import date, timedelta
from typing import Any, Optional


# How many days to advance for each auto-reschedulable frequency
_RESCHEDULE_DELTA: dict[str, timedelta] = {
    "daily": timedelta(days=1),
    "twice_daily": timedelta(days=1),
    "weekly": timedelta(weeks=1),
}


class Task:
    def __init__(
        self,
        description: str,
        time: int,
        frequency: str,
        priority: str = "medium",
        due_date: Optional[date] = None,
    ):
        if not isinstance(time, int) or time < 0 or time >= 1440:
            raise ValueError("time must be an integer between 0 and 1439 (minutes since midnight)")
        if priority not in ("low", "medium", "high"):
            raise ValueError(f"priority must be 'low', 'medium', or 'high', got '{priority}'")
        if not description:
            raise ValueError("description cannot be empty")
        if not frequency:
            raise ValueError("frequency cannot be empty")
        if due_date is not None and not isinstance(due_date, date):
            raise TypeError("due_date must be a datetime.date instance or None")

        self.description = description  # e.g. "Morning walk"
        self.time = time                # minutes since midnight, e.g. 480 = 8:00am
        self.frequency = frequency      # e.g. "daily", "twice_daily", "weekly"
        self.priority = priority        # "low", "medium", "high"
        self.due_date: date = due_date if due_date is not None else date.today()
        self.completed = False
        # True for synthetic copies created by _expand_recurring; they never auto-reschedule
        self._synthetic: bool = False

    def mark_complete(self) -> Optional["Task"]:
        """
        Mark this task as completed.

        Returns a new Task scheduled for the next occurrence if the frequency
        is auto-reschedulable (daily, twice_daily, weekly); otherwise returns None.
        Uses timedelta to advance the due_date by the correct interval.
        """
        if self.completed:
            raise RuntimeError(f"Task '{self.description}' is already marked complete")
        self.completed = True

        if self._synthetic or self.frequency not in _RESCHEDULE_DELTA:
            return None

        next_date = self.due_date + _RESCHEDULE_DELTA[self.frequency]
        return Task(self.description, self.time, self.frequency, self.priority, next_date)

    def format_time(self) -> str:
        """Convert minutes since midnight to a 12-hour time string with am/pm."""
        hour, minute = divmod(self.time, 60)
        period = "am" if hour < 12 else "pm"
        hour = hour % 12 or 12
        return f"{hour}:{minute:02d}{period}"

    def __repr__(self) -> str:
        """Return a readable string showing task status, due date, time, and priority."""
        status = "done" if self.completed else "pending"
        return (
            f"[{status}] {self.description} on {self.due_date} "
            f"at {self.format_time()} ({self.priority})"
        )


class Pet:
    def __init__(self, name: str, species: str):
        if not name:
            raise ValueError("Pet name cannot be empty")
        if not species:
            raise ValueError("Pet species cannot be empty")

        self.name = name
        self.species = species
        self.tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        """Add a Task to this pet's task list."""
        if not isinstance(task, Task):
            raise TypeError("task must be an instance of Task")
        self.tasks.append(task)

    def get_tasks(self) -> list[Task]:
        """Return all tasks assigned to this pet."""
        return self.tasks

    def get_pending_tasks(self) -> list[Task]:
        """Return only tasks that have not been completed yet."""
        return [t for t in self.tasks if not t.completed]


class Owner:
    def __init__(self, name: str, available_hours: list[tuple[int, int]], preferences: dict[str, Any]):
        if not name:
            raise ValueError("Owner name cannot be empty")
        if not isinstance(available_hours, list):
            raise TypeError("available_hours must be a list of (start, end) tuples")
        for window in available_hours:
            if not (isinstance(window, tuple) and len(window) == 2):
                raise TypeError("each entry in available_hours must be a (start, end) tuple")
            start, end = window
            if not (0 <= start < end <= 1440):
                raise ValueError(f"invalid time window {window}: start and end must be between 0-1440 with start < end")

        self.name = name
        self.available_hours = available_hours  # list of (start, end) minutes since midnight, e.g. (480, 600) = 8am-10am
        self.preferences = preferences          # e.g. {"prefers_morning": True}
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a Pet to this owner's list of pets."""
        if not isinstance(pet, Pet):
            raise TypeError("pet must be an instance of Pet")
        self.pets.append(pet)

    def get_all_tasks(self) -> list[Task]:
        """Return all tasks across every pet the owner has."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.get_tasks())
        return all_tasks

    def get_constraints(self) -> dict[str, Any]:
        """Return the owner's available hours and preferences as a dict."""
        return {
            "available_hours": self.available_hours,
            "preferences": self.preferences,
        }


class Scheduler:
    def __init__(self, owner: Owner):
        if not isinstance(owner, Owner):
            raise TypeError("owner must be an instance of Owner")

        self.owner = owner
        self.schedule: list[Task] = []  # finalized ordered task list for the day
        # Maps each scheduled Task back to the Pet that owns it
        self._task_pet_map: dict[int, Pet] = {}

    def _expand_recurring(self, pet: Pet, tasks: list[Task]) -> list[Task]:
        """
        Expand twice_daily tasks into two instances 12 hours apart.
        The second instance is marked synthetic so it never auto-reschedules
        (the original task handles rescheduling for the whole pair).
        """
        expanded = []
        for task in tasks:
            expanded.append(task)
            if task.frequency == "twice_daily":
                second_time = (task.time + 720) % 1440
                extra = Task(
                    f"{task.description} (2nd)",
                    second_time,
                    task.frequency,
                    task.priority,
                    task.due_date,
                )
                extra._synthetic = True
                expanded.append(extra)
                self._task_pet_map[id(extra)] = pet
        return expanded

    def build_schedule(self) -> list[Task]:
        """
        Pull all pending tasks from the owner's pets, expand recurring tasks,
        filter by owner availability, then sort by priority (high first) and time.
        """
        if not self.owner.pets:
            raise ValueError("Owner has no pets — add a pet before building a schedule")

        constraints = self.owner.get_constraints()
        available = constraints["available_hours"]
        preferences = constraints["preferences"]

        self._task_pet_map.clear()
        pending: list[Task] = []
        for pet in self.owner.pets:
            pet_tasks = pet.get_pending_tasks()
            for t in pet_tasks:
                self._task_pet_map[id(t)] = pet
            pending.extend(self._expand_recurring(pet, pet_tasks))

        if not pending:
            raise ValueError("No pending tasks found across any of the owner's pets")

        def is_available(task: Task) -> bool:
            for start, end in available:
                if start <= task.time < end:
                    return True
            return False

        filtered = [t for t in pending if is_available(t)]

        if not filtered:
            raise ValueError("No tasks fall within the owner's available time windows")

        priority_order = {"high": 0, "medium": 1, "low": 2}
        filtered.sort(key=lambda t: (
            priority_order.get(t.priority, 1),
            t.time if not preferences.get("prefers_morning") else t.time
        ))

        self.schedule = filtered
        return self.schedule

    def sort_by_time(self) -> list[Task]:
        """Return a copy of the schedule sorted chronologically by time."""
        if not self.schedule:
            raise RuntimeError("Schedule is empty — run build_schedule() first")
        return sorted(self.schedule, key=lambda t: t.time)

    def get_tasks_for_pet(self, pet_name: str) -> list[Task]:
        """Return scheduled tasks that belong to the named pet."""
        if not self.schedule:
            raise RuntimeError("Schedule is empty — run build_schedule() first")
        known = [p.name for p in self.owner.pets]
        if pet_name not in known:
            raise ValueError(f"No pet named '{pet_name}' found; known pets: {known}")
        return [t for t in self.schedule
                if self._task_pet_map.get(id(t)) is not None
                and self._task_pet_map[id(t)].name == pet_name]

    def get_tasks_by_status(self, completed: bool) -> list[Task]:
        """Return scheduled tasks filtered by completion status."""
        if not self.schedule:
            raise RuntimeError("Schedule is empty — run build_schedule() first")
        return [t for t in self.schedule if t.completed == completed]

    def detect_conflicts(self) -> list[tuple[Task, Task]]:
        """
        Return pairs of tasks scheduled at the exact same minute.
        Uses a single pass with a time-keyed dict for O(n) detection.
        """
        if not self.schedule:
            raise RuntimeError("Schedule is empty — run build_schedule() first")
        seen: dict[int, Task] = {}
        conflicts: list[tuple[Task, Task]] = []
        for task in self.schedule:
            if task.time in seen:
                conflicts.append((seen[task.time], task))
            else:
                seen[task.time] = task
        return conflicts

    def get_tasks_by_priority(self, priority: str) -> list[Task]:
        """Return all scheduled tasks matching the given priority level."""
        if priority not in ("low", "medium", "high"):
            raise ValueError(f"priority must be 'low', 'medium', or 'high', got '{priority}'")
        if not self.schedule:
            raise RuntimeError("Schedule is empty — run build_schedule() first")
        return [t for t in self.schedule if t.priority == priority]

    def mark_complete(self, task: Task) -> Optional[Task]:
        """
        Mark a scheduled task as complete.

        If the task's frequency is auto-reschedulable (daily, twice_daily, weekly),
        the next occurrence is automatically added to the owning pet's task list
        and inserted into the live schedule.  Returns the new Task, or None.
        """
        if not isinstance(task, Task):
            raise TypeError("task must be an instance of Task")
        if task not in self.schedule:
            raise ValueError(f"Task '{task.description}' is not in the current schedule")

        next_task: Optional[Task] = task.mark_complete()

        if next_task is not None:
            pet = self._task_pet_map.get(id(task))
            if pet is None:
                raise RuntimeError(
                    f"Cannot reschedule '{task.description}': owning pet not found in map"
                )
            pet.add_task(next_task)
            self._task_pet_map[id(next_task)] = pet

            priority_order = {"high": 0, "medium": 1, "low": 2}
            self.schedule.append(next_task)
            self.schedule.sort(key=lambda t: (priority_order.get(t.priority, 1), t.time))

        return next_task

    def explain(self) -> str:
        """Return a human-readable summary of the day's scheduled tasks."""
        if not self.schedule:
            raise RuntimeError("Schedule is empty — run build_schedule() first")

        lines = [f"Schedule for {self.owner.name}:\n"]
        for task in self.schedule:
            lines.append(
                f"  - {task.description} at {task.format_time()} "
                f"[{task.priority} priority, {task.frequency}]"
            )
        return "\n".join(lines)
