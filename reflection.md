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

I defined priorities as 1 = high, 2 = medium, and 3 = low, with equal priorities keeping their original order. I also updated the UML to show that DailyPlan uses Owner rather than being stored by Owner. 

I renamed CareTask to Task and DailyPlan to Scheduler to match the implementation requirements. I added frequency and completion status to Task and get_all_tasks() to Owner. Scheduler uses this method to plan tasks across all pets, prioritizes unfinished tasks, and records reasons for skipped tasks.
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?
My scheduler considers available minutes, task priority, completion status, and due date. It checks unfinished tasks due today or earlier, with high-priority tasks first. If a task does not fit, it skips that task and keeps checking smaller tasks. Equal-priority tasks keep their original order.

I treated available time as a firm limit and priority as the main selection rule because pet owners need a manageable plan that puts important care first. Scheduled start times support sorting and conflict warnings, but the daily plan does not automatically resolve those conflicts.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?
My scheduler detects conflicts only when unfinished tasks have the same date and start time. This keeps the algorithm simple, but it misses overlapping tasks with different start times, such as a 30-minute walk at 08:00 and feeding at 08:15.

AI suggested using defaultdict instead of setdefault for readability. I kept the existing dictionary approach because it works correctly and the change would not meaningfully improve performance. I kept warnings sorted by date and time so they are easier to read.
---

## 3. AI Collaboration

**a. How you used AI**

I used Claude in VS Code to brainstorm classes, generate UML, create class skeletons, implement scheduling methods, connect the Streamlit interface, draft tests, and improve documentation. Agent mode was useful because it could read related files and make coordinated changes.

The most helpful prompts named the files, described the expected behavior, and limited which files Claude could change. Asking for a plan before implementation helped me review the approach. Separate chats for design, algorithms, and testing kept each phase focused.

I checked the results by running main.py, running all 27 pytest tests, and manually checking sorting, completion-status filtering, conflict warnings, and daily recurrence in the app.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?
Claude suggested replacing setdefault with defaultdict in conflict detection. I kept the existing approach because it already worked and the suggestion offered little performance improvement. I evaluated the explanation and checked that the CLI demo produced the expected warning and the automated conflict tests passed.
---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?
I tested task completion and addition, chronological sorting, time normalization, filtering by pet and status, daily and weekly recurrence, duplicate prevention, conflict detection, time-budget limits, and empty task lists. These tests check both normal use and edge cases that could produce an incorrect care plan. All 27 automated tests passed.

I also manually checked sorting, completion-status filtering, conflict warnings, and daily recurrence in the Streamlit app.
**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?
My confidence is 4 out of 5 because the automated tests pass and the main UI features worked during manual checks. More tests are still needed for overlapping task durations, invalid inputs through the UI, and longer sequences of user actions. I would also test date transitions such as the end of a month or year.
---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
I am most satisfied that the backend and Streamlit interface work together across multiple pets. I can add tasks, view them in time order, filter them, see conflict warnings, and complete recurring tasks. Building the CLI demo before connecting the UI helped me check the logic separately which was really helpful and i appreciate that.
**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
I would add detection of overlapping durations instead of only matching start times. I would also save data permanently, keep the generated schedule visible after other actions, and add more automated UI tests.
**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
I learned that being the lead architect means deciding what each class should do, giving AI clear requirements, and checking its work. AI can generate code quickly, but I still need to review suggestions, choose tradeoffs, and verify that the implementation, UML, and documentation agree.