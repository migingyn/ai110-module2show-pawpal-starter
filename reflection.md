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

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
