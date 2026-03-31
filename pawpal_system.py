from typing import Any


class Task:
    def __init__(self, description: str, time: int, frequency: str, priority: str = "medium"):
        if not isinstance(time, int) or time < 0 or time >= 1440:
            raise ValueError("time must be an integer between 0 and 1439 (minutes since midnight)")
        if priority not in ("low", "medium", "high"):
            raise ValueError(f"priority must be 'low', 'medium', or 'high', got '{priority}'")
        if not description:
            raise ValueError("description cannot be empty")
        if not frequency:
            raise ValueError("frequency cannot be empty")

        self.description = description  # e.g. "Morning walk"
        self.time = time                # minutes since midnight, e.g. 480 = 8:00am
        self.frequency = frequency      # e.g. "daily", "twice_daily", "weekly"
        self.priority = priority        # "low", "medium", "high"
        self.completed = False

    def mark_complete(self) -> None:
        """Mark this task as completed, raising an error if it's already done."""
        if self.completed:
            raise RuntimeError(f"Task '{self.description}' is already marked complete")
        self.completed = True

    def format_time(self) -> str:
        """Convert minutes since midnight to a 12-hour time string with am/pm."""
        hour, minute = divmod(self.time, 60)
        period = "am" if hour < 12 else "pm"
        hour = hour % 12 or 12
        return f"{hour}:{minute:02d}{period}"

    def __repr__(self) -> str:
        """Return a readable string showing task status, time, and priority."""
        status = "done" if self.completed else "pending"
        return f"[{status}] {self.description} at {self.format_time()} ({self.priority})"


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

    def build_schedule(self) -> list[Task]:
        """
        Pull all pending tasks from the owner's pets, filter by owner availability,
        then sort by priority (high first) and scheduled time.
        """
        if not self.owner.pets:
            raise ValueError("Owner has no pets — add a pet before building a schedule")

        constraints = self.owner.get_constraints()
        available = constraints["available_hours"]
        preferences = constraints["preferences"]

        pending = []
        for pet in self.owner.pets:
            pending.extend(pet.get_pending_tasks())

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

    def get_tasks_by_priority(self, priority: str) -> list[Task]:
        """Return all scheduled tasks matching the given priority level."""
        if priority not in ("low", "medium", "high"):
            raise ValueError(f"priority must be 'low', 'medium', or 'high', got '{priority}'")
        if not self.schedule:
            raise RuntimeError("Schedule is empty — run build_schedule() first")
        return [t for t in self.schedule if t.priority == priority]

    def mark_complete(self, task: Task) -> None:
        """Mark a scheduled task as complete."""
        if not isinstance(task, Task):
            raise TypeError("task must be an instance of Task")
        if task not in self.schedule:
            raise ValueError(f"Task '{task.description}' is not in the current schedule")
        task.mark_complete()

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
