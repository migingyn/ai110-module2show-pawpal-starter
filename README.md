# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

Phase 3 adds four scheduling algorithms that make the app more useful for a real pet owner.

**Sort by time** — `sort_by_time()` returns the day's tasks in chronological order, separate from the priority sort that `build_schedule()` uses internally. Useful when you just want to see what's coming up next rather than what's most important.

**Filter by pet or status** — `get_tasks_for_pet(name)` narrows the schedule down to one pet's tasks, and `get_tasks_by_status(completed)` splits pending vs done. Both work off the live schedule so they stay accurate after tasks are marked complete.

**Recurring task expansion** — Tasks with `frequency="twice_daily"` automatically get a second slot 12 hours later. When you mark a `daily` or `weekly` task complete, the next occurrence is created and added to the schedule using Python's `timedelta` — no manual re-adding needed.

**Conflict detection** — `get_conflict_warnings()` scans for tasks booked at the exact same minute and returns a warning that identifies which pets are involved and whether it's a same-pet or cross-pet clash. It doesn't crash — it just flags the problem so you can decide what to do.

## Testing PawPal+

### Run the test suite

```bash
python -m pytest tests/test_pawpal.py -v
```

### What the tests cover

| Area | Tests | Description |
|---|---|---|
| **Sorting correctness** | 3 | Verifies high → medium → low priority order and time as a tiebreaker within the same priority |
| **Recurrence logic** | 5 | Confirms daily tasks reschedule +1 day, weekly tasks +7 days, one-off tasks return `None`, and the new task lands in both the pet's list and the live schedule |
| **Twice-daily expansion** | 4 | Checks that a `twice_daily` task expands to two slots 720 minutes apart, that the second copy is flagged synthetic (no re-rescheduling), and that midnight wraparound is handled correctly |
| **Conflict detection** | 4 | Validates that two tasks at the same minute produce one pair, three tasks produce three pairs (C(3,2)), no-conflict cases return an empty list, and warning strings are human-readable |
| **Error / edge cases** | 8 | Guards against double-completion, orphan tasks, no pets, no pending tasks, all tasks outside the availability window, and calling sort/detect before `build_schedule()` |

**Total: 26 tests — all passing.**

### Confidence Level

**4 / 5 stars**

The core scheduling behaviors (priority sort, recurrence, conflict detection, twice-daily expansion, and availability filtering) are fully covered with both happy-path and error-path tests. One star is withheld because the `prefers_morning` preference branch in `build_schedule()` has no effect on the sort key as currently written, and cross-pet conflict scenarios with more than two pets are not yet tested.

---

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
