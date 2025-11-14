# Task 03: Interview Script Creation

**Task ID:** task_03_interview_script_creation
**Dependencies:** task_01, task_02
**Input:** personas.json, pain_points.json
**Output:** interview_script.json

---

## Objective

Generate actionable interview script following frameworks from `RESEARCH_interview_question_bank.yaml`.

---

## Instructions

### Step 1: Structure Interview (5 Phases)
From `RESEARCH_interview_question_bank.yaml`:

1. **Introduction (5 min)**
   - Build rapport, set expectations

2. **Background (5-10 min)**
   - Understand context and current state

3. **Problem Exploration (15-20 min)**
   - Deep dive into pain points

4. **Future State (5-10 min)**
   - Understand ideal solutions

5. **Wrap-up (5 min)**
   - Final questions, thank you

### Step 2: Write Open-Ended Questions
Best practices from knowledge base:
- ✅ "Tell me about..." not "Do you...?"
- ✅ "Walk me through..." not "Would you...?"
- ✅ Focus on past behavior, not hypothetical
- ✅ Follow up with "Why?" or "Tell me more"
- ❌ Avoid leading questions
- ❌ Avoid yes/no questions

### Step 3: Customize for Personas
- Questions specific to each persona's context
- Reference their tools, workflows, pain points

---

## Output Format

```json
{
  "interview_script": {
    "intro": "Thanks for taking the time to speak with me today. I'm researching how [persona role] currently handle [problem area] to understand the challenges you face. There are no right or wrong answers—I'm just trying to learn from your experience. This conversation will take about 30 minutes. Do you have any questions before we start?",
    "background_questions": [
      "Tell me about your role and what a typical day looks like.",
      "What tools do you currently use for [task/problem]?",
      "Walk me through the last time you had to [perform task]."
    ],
    "problem_exploration_questions": [
      "What's the most frustrating part of [task/workflow]?",
      "Tell me about a time when [task] went wrong. What happened?",
      "What mistakes or errors commonly happen in this process?",
      "Have you tried solving this problem before? What happened?"
    ],
    "future_state_questions": [
      "If you had a magic wand, what would you change about [task]?",
      "What would make [task] easier or faster?",
      "How would you prioritize these improvements?"
    ],
    "wrap_up_questions": [
      "Is there anything I should have asked but didn't?",
      "Would you be interested in testing an early version of a solution?",
      "Can I follow up if I have more questions?"
    ]
  },
  "interview_duration": "30-45 minutes",
  "personas_targeted": ["Marketing Mary", "Sales Sam"]
}
```

---

## Next Task

Proceed to **Task 04: Survey Design**
