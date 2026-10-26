# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

I chose four classes:

- Owner stores the owner's name, available time, and pets. It handles adding pets and updating available time.
- Pet stores the pet's name, species, and care tasks. It handles adding and editing tasks.
- CareTask stores a task's name, duration, and priority. It handles updating task details.
- DailyPlan selects tasks from the owner's pets based on available time and priorities. It stores the selected tasks and total duration and explains its choices.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.
After reviewing AI feedback, I added pet_name to CareTask so the daily plan can identify which pet each task belongs to. I added skipped_tasks with reasons and available_minutes to DailyPlan so it can explain skipped tasks and report time usage.

I defined priorities as 1 = high, 2 = medium, and 3 = low, with equal priorities keeping their original order. I also updated the UML to show that DailyPlan uses Owner rather than being stored by Owner. All methods remain empty stubs.

I renamed CareTask to Task and DailyPlan to Scheduler to match the implementation requirements. I added frequency and completion status to Task and get_all_tasks() to Owner. Scheduler uses this method to plan tasks across all pets, prioritizes unfinished tasks, and records reasons for skipped tasks.
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?
My scheduler detects conflicts only when unfinished tasks have the same date and start time. This keeps the algorithm simple, but it misses overlapping tasks with different start times, such as a 30-minute walk at 08:00 and feeding at 08:15.

AI suggested using defaultdict instead of setdefault for readability. I kept the existing dictionary approach because it works correctly and the change would not meaningfully improve performance. I kept warnings sorted by date and time so they are easier to read.
---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?

AI helped me turn my UML into class skeletons, implement the methods, and draft tests. It suggested identifying each task's pet, storing skipped tasks with reasons, remembering the time budget, and defining clear priority rules. I accepted these suggestions because they made scheduling and explanations clearer.

I kept the design simple by passing Owner into Scheduler rather than adding a daily_plan attribute to Owner. I also left frequency as stored information without implementing recurring schedules.

I verified the result by running main.py with two pets and three tasks and checking the selected tasks, skipped task, and time used. I ran python -m pytest, and both tests passed.
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
