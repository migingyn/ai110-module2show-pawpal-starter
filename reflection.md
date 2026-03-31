# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

The initial UML design should have at least an owner class, pet class, plan class, and a calendar class. The relationship between these classes are that the owner has a pet and constraints -> the pet has needs -> the plan builds tasks off of those needs and owner constraints -> plans are stored onto the calendar. The owner class should contain a string of their name, hour availability in a list, their preferences, and a getter method of their constraints and a method to add a pet to them. The pet class should contain a string of their name, type of pet, and a list of their needs stored as a dict with a getter method of their needs and a method to add needs to the pet. The plan class should contain a string of the owner, the pet, and a list of tasks with a method to build tasks off pet needs. Lastly, the calendar class should contain a dict of plans with a getter method of the plans given the date, a method to add plans to the calendar, and a method to view all the plans of the week.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes, a few things changed once I started actually writing the skeleton. First, I changed available_hours in the owner class from a list of strings like "8am-10am" to a list of tuples of integers representing minutes since midnight. The string version looked clean on paper but would've been a pain to work with in the scheduling logic since you'd have to parse the string every time you wanted to compare it against a task duration. Using integers makes the math way simpler. Second, I gave the plan class a date attribute and moved owner and pet into the constructor instead of having them as optional vars that also get passed into build(). Before, those were set in two different places which was confusing. Now the plan knows its date, its owner, and its pet from the start, and build() just does the scheduling work. Third, I kept needs and tasks as plain dicts instead of making them their own classes. It keeps the design to exactly 4 classes and is simpler since needs and tasks don't really need their own methods.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

Constraints that my scheduler considers are the owner's available time windows (stored as minute-based tuples), task priority (high, medium, low), and a morning preference flag. I decided priority mattered most because a missed high-priority task like medication is a bigger problem than missing a low-priority enrichment task. Time windows came second since there's no point scheduling something the owner can't actually do. The morning preference was last since it's more of a nice-to-have than a hard rule.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

One tradeoff my scheduler makes is only flagging conflicts when two tasks share the exact same start minute, rather than checking if their durations overlap. So two 30-minute tasks at 8:00am and 8:15am would slip through undetected even though you couldn't realistically do both. It's a reasonable limitation right now because `Task` doesn't have a duration field, and adding one just to support overlap detection felt like over-engineering for what this app actually needs. If durations get added later, the fix in `detect_conflicts()` is straightforward since you'd just swap the equality check for a range comparison.

I also reviewed `detect_conflicts()` with AI, which suggested swapping the manual nested `range` loops for `itertools.combinations(tasks, 2)`. I kept it because `combinations(tasks, 2)` says exactly what it does ("give me all pairs") so it's genuinely clearer, not just shorter.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

The most effective features were Copilot Chat with `#codebase` for test planning and Agent Mode for multi-file changes like adding JSON persistence across `pawpal_system.py` and `app.py` at the same time. Prompts that included context upfront worked best, like describing the full data model before asking a scheduling question instead of asking in isolation. Inline chat was useful for smaller focused tasks like formatting the time input widget.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

When Copilot helped implement the `prefers_morning` preference in `build_schedule()`, the sort lambda it wrote looked correct but both the morning and non-morning branches were doing the exact same thing, so the flag had no actual effect on the output. I caught it by tracing through the lambda manually and confirmed it with a test. I left the field in the data model but documented the limitation honestly in the README rather than shipping logic that looked functional but wasn't.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I tested priority sort order, twice-daily expansion including midnight wraparound, daily and weekly rescheduling after `mark_complete()`, conflict detection for two and three tasks at the same time, and a full set of error paths like no pets, all tasks outside the availability window, and double-completing a task. These mattered because the scheduling logic has a lot of interdependencies and a bug in one place like `_expand_recurring` would break filtering and conflict detection downstream too.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I'm confident in the core behaviors since all 26 tests pass and they cover both happy paths and error conditions. If I had more time I'd test the `prefers_morning` flag once it's actually wired up, multi-pet conflict scenarios with three or more pets, and the JSON round-trip to make sure tasks with different frequencies and dates serialize and reload correctly.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

The scheduling logic turned out cleaner than I expected. Having `Task` as its own class with `mark_complete()` returning the next occurrence kept the rescheduling self-contained, and `_task_pet_map` made it possible to track ownership through expansion and rescheduling without adding a back-reference to every task.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I'd add a duration field to `Task` so conflict detection could catch overlapping tasks instead of just exact-minute matches. That's the biggest real-world gap right now since two 30-minute tasks 10 minutes apart would slip through. I'd also make `prefers_morning` actually affect the sort key.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

AI is useful for generating options quickly but it doesn't know which option fits your design. The `itertools.combinations` suggestion for conflict detection was genuinely better than what I had, but the `prefers_morning` sort lambda looked correct and wasn't. The difference is that I had to read and reason about both of them myself to know which was which. Using separate chat sessions per phase helped with this because each session stayed focused and I wasn't carrying forward assumptions from earlier conversations that might not apply anymore.

---

## 6. Prompt Comparison (Stretch)

**Task tested:** Rescheduling logic for recurring tasks — specifically, how to generate the next `Task` after `mark_complete()` is called on a `daily` or `weekly` task.

**Prompt used (same for both models):**
> "In a Python pet scheduler, when a task is marked complete, I want to automatically create a copy of it scheduled for the next occurrence. The task has a `frequency` field that can be `daily`, `weekly`, or `twice_daily`. How should I implement this in `mark_complete()`?"

| | Model A: _[fill in model name]_ | Model B: _[fill in model name]_ |
|---|---|---|
| **Approach** | _[describe the approach it suggested]_ | _[describe the approach it suggested]_ |
| **Code style** | _[e.g., used if/elif chain, used a dict lookup, etc.]_ | _[e.g., used if/elif chain, used a dict lookup, etc.]_ |
| **What was useful** | _[what you kept or learned from it]_ | _[what you kept or learned from it]_ |
| **What was wrong or off** | _[anything incorrect, over-engineered, or that didn't fit]_ | _[anything incorrect, over-engineered, or that didn't fit]_ |

**Which suggestion did you use and why?**

_[Write 2–3 sentences. Which model gave the more Pythonic or modular answer? Did either one suggest the `_RESCHEDULE_DELTA` dict lookup pattern, or did you arrive at that yourself? What did you change before using it?]_
