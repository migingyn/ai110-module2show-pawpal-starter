from datetime import date, timedelta

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def owner():
    return Owner("Alice", [(0, 1440)], {})


@pytest.fixture
def pet(owner):
    p = Pet("Buddy", "Dog")
    owner.add_pet(p)
    return p


@pytest.fixture
def scheduler(owner):
    return Scheduler(owner)


# ---------------------------------------------------------------------------
# 1. Existing baseline tests
# ---------------------------------------------------------------------------

def test_mark_complete_changes_status():
    task = Task("Morning walk", 420, "daily", "high")
    assert not task.completed
    task.mark_complete()
    assert task.completed


def test_add_task_increases_pet_task_count():
    pet = Pet("Buddy", "Dog")
    assert len(pet.get_tasks()) == 0
    pet.add_task(Task("Morning walk", 420, "daily", "high"))
    assert len(pet.get_tasks()) == 1


# ---------------------------------------------------------------------------
# 2. Sorting correctness
# ---------------------------------------------------------------------------

def test_build_schedule_priority_order(owner, pet, scheduler):
    """High-priority tasks come before lower-priority ones."""
    pet.add_task(Task("Low task", 480, "daily", "low"))
    pet.add_task(Task("High task", 600, "daily", "high"))
    pet.add_task(Task("Medium task", 540, "daily", "medium"))

    schedule = scheduler.build_schedule()

    assert schedule[0].priority == "high"
    assert schedule[1].priority == "medium"
    assert schedule[2].priority == "low"


def test_sort_by_time_chronological(owner, pet, scheduler):
    """sort_by_time() returns tasks in ascending time order."""
    pet.add_task(Task("Evening walk", 1080, "daily", "low"))
    pet.add_task(Task("Morning walk", 420, "daily", "low"))
    pet.add_task(Task("Midday meal", 720, "daily", "low"))

    scheduler.build_schedule()
    by_time = scheduler.sort_by_time()

    assert by_time[0].time == 420
    assert by_time[1].time == 720
    assert by_time[2].time == 1080


def test_same_priority_sorted_by_time(owner, pet, scheduler):
    """When priorities are equal, earlier time comes first."""
    pet.add_task(Task("Late high", 900, "daily", "high"))
    pet.add_task(Task("Early high", 300, "daily", "high"))

    schedule = scheduler.build_schedule()

    assert schedule[0].time == 300
    assert schedule[1].time == 900


# ---------------------------------------------------------------------------
# 3. Recurrence logic
# ---------------------------------------------------------------------------

def test_daily_task_reschedules_next_day():
    """mark_complete() on a daily task returns a new task due tomorrow."""
    today = date.today()
    task = Task("Walk", 480, "daily", "high", today)
    new_task = task.mark_complete()

    assert new_task is not None
    assert new_task.due_date == today + timedelta(days=1)
    assert new_task.completed is False


def test_weekly_task_reschedules_next_week():
    today = date.today()
    task = Task("Bath", 600, "weekly", "medium", today)
    new_task = task.mark_complete()

    assert new_task is not None
    assert new_task.due_date == today + timedelta(weeks=1)


def test_one_off_task_does_not_reschedule():
    """A task with frequency 'once' returns None on completion."""
    task = Task("Vet visit", 480, "once", "high")
    result = task.mark_complete()
    assert result is None


def test_scheduler_mark_complete_adds_next_task_to_pet(owner, pet, scheduler):
    """Completing a daily task via Scheduler adds the rescheduled task to the pet."""
    today = date.today()
    t = Task("Walk", 480, "daily", "high", today)
    pet.add_task(t)
    scheduler.build_schedule()

    next_task = scheduler.mark_complete(t)

    assert next_task is not None
    assert next_task in pet.get_tasks()
    assert next_task.due_date == today + timedelta(days=1)


def test_scheduler_mark_complete_inserts_into_schedule(owner, pet, scheduler):
    """The rescheduled task appears in the live schedule."""
    t = Task("Walk", 480, "daily", "high")
    pet.add_task(t)
    scheduler.build_schedule()

    next_task = scheduler.mark_complete(t)

    assert next_task in scheduler.schedule


# ---------------------------------------------------------------------------
# 4. Twice-daily expansion
# ---------------------------------------------------------------------------

def test_twice_daily_expands_to_two_slots(owner, pet, scheduler):
    """A twice_daily task produces two entries in the schedule."""
    pet.add_task(Task("Feed", 480, "twice_daily", "medium"))
    schedule = scheduler.build_schedule()

    feed_tasks = [t for t in schedule if "Feed" in t.description]
    assert len(feed_tasks) == 2


def test_twice_daily_second_slot_12_hours_later(owner, pet, scheduler):
    """The second slot is exactly 720 minutes after the first."""
    pet.add_task(Task("Feed", 480, "twice_daily", "medium"))
    scheduler.build_schedule()

    by_time = scheduler.sort_by_time()
    feed_tasks = [t for t in by_time if "Feed" in t.description]

    assert feed_tasks[1].time == (feed_tasks[0].time + 720) % 1440


def test_twice_daily_second_slot_is_synthetic(owner, pet, scheduler):
    """The expanded (2nd) copy is marked synthetic and won't auto-reschedule."""
    pet.add_task(Task("Feed", 480, "twice_daily", "medium"))
    scheduler.build_schedule()

    second_slot = next(t for t in scheduler.schedule if "(2nd)" in t.description)
    assert second_slot._synthetic is True
    assert second_slot.mark_complete() is None


def test_twice_daily_midnight_wraparound(owner, pet, scheduler):
    """A twice_daily task starting at 840 (2pm) wraps its second slot to 0 (2am)."""
    pet.add_task(Task("Late feed", 840, "twice_daily", "low"))
    scheduler.build_schedule()

    second_slot = next(t for t in scheduler.schedule if "(2nd)" in t.description)
    assert second_slot.time == (840 + 720) % 1440


# ---------------------------------------------------------------------------
# 5. Conflict detection
# ---------------------------------------------------------------------------

def test_detect_conflicts_same_time(owner, pet, scheduler):
    """Two tasks at the same minute are flagged as a conflict."""
    pet.add_task(Task("Walk", 480, "daily", "high"))
    pet.add_task(Task("Feed", 480, "daily", "medium"))
    scheduler.build_schedule()

    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) == 1
    assert conflicts[0][0].time == conflicts[0][1].time


def test_detect_conflicts_three_tasks_same_time(owner, pet, scheduler):
    """Three tasks at the same minute produce 3 conflicting pairs (C(3,2))."""
    pet.add_task(Task("A", 480, "daily", "high"))
    pet.add_task(Task("B", 480, "daily", "medium"))
    pet.add_task(Task("C", 480, "daily", "low"))
    scheduler.build_schedule()

    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) == 3


def test_detect_conflicts_no_conflicts(owner, pet, scheduler):
    """Distinct times produce no conflicts."""
    pet.add_task(Task("Walk", 480, "daily", "high"))
    pet.add_task(Task("Feed", 540, "daily", "medium"))
    scheduler.build_schedule()

    assert scheduler.detect_conflicts() == []


def test_get_conflict_warnings_returns_strings(owner, pet, scheduler):
    """get_conflict_warnings() returns human-readable strings for each conflict."""
    pet.add_task(Task("Walk", 480, "daily", "high"))
    pet.add_task(Task("Feed", 480, "daily", "medium"))
    scheduler.build_schedule()

    warnings = scheduler.get_conflict_warnings()
    assert len(warnings) == 1
    assert "WARNING" in warnings[0]
    assert "8:00am" in warnings[0]


# ---------------------------------------------------------------------------
# 6. Error / edge-case paths
# ---------------------------------------------------------------------------

def test_double_mark_complete_raises():
    """Calling mark_complete() twice on the same task raises RuntimeError."""
    task = Task("Walk", 480, "daily", "high")
    task.mark_complete()
    with pytest.raises(RuntimeError):
        task.mark_complete()


def test_scheduler_mark_complete_task_not_in_schedule_raises(owner, pet, scheduler):
    """Passing a task that isn't scheduled raises ValueError."""
    pet.add_task(Task("Walk", 480, "daily", "high"))
    scheduler.build_schedule()
    orphan = Task("Ghost task", 300, "daily", "low")
    with pytest.raises(ValueError):
        scheduler.mark_complete(orphan)


def test_build_schedule_no_pets_raises():
    """An owner with no pets raises ValueError."""
    owner = Owner("Bob", [(0, 1440)], {})
    scheduler = Scheduler(owner)
    with pytest.raises(ValueError):
        scheduler.build_schedule()


def test_build_schedule_no_pending_tasks_raises(owner, pet, scheduler):
    """All tasks already completed → ValueError."""
    t = Task("Walk", 480, "daily", "high")
    t.mark_complete()
    pet.add_task(t)
    with pytest.raises(ValueError):
        scheduler.build_schedule()


def test_build_schedule_all_tasks_outside_window():
    """Tasks outside the owner's available window are filtered, raising ValueError."""
    owner = Owner("Carol", [(900, 1200)], {})   # available 3pm–8pm only
    pet = Pet("Max", "Cat")
    pet.add_task(Task("Morning feed", 420, "daily", "high"))  # 7am — outside window
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    with pytest.raises(ValueError):
        scheduler.build_schedule()


def test_pet_with_no_tasks_skipped(owner, scheduler):
    """A pet with no tasks doesn't crash the schedule; other pets' tasks are used."""
    empty_pet = Pet("Ghost", "Cat")
    owner.add_pet(empty_pet)
    active_pet = Pet("Rex", "Dog")
    active_pet.add_task(Task("Walk", 480, "daily", "high"))
    owner.add_pet(active_pet)

    schedule = scheduler.build_schedule()
    assert len(schedule) >= 1


def test_sort_by_time_before_build_raises(scheduler):
    """sort_by_time() before build_schedule() raises RuntimeError."""
    with pytest.raises(RuntimeError):
        scheduler.sort_by_time()


def test_detect_conflicts_before_build_raises(scheduler):
    """detect_conflicts() before build_schedule() raises RuntimeError."""
    with pytest.raises(RuntimeError):
        scheduler.detect_conflicts()
