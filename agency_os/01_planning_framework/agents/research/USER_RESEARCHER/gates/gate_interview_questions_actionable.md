# Validation Gate: Interview Questions Actionable

**Gate ID:** gate_interview_questions_actionable
**Purpose:** Ensure interview questions are open-ended and will elicit useful answers
**Enforcement:** WARNING ONLY - does not block progression

---

## Validation Criteria

This gate passes ONLY if:

1. **Questions are open-ended**
   - Start with "Tell me...", "Walk me through...", "Describe..."
   - NOT yes/no questions
   - NOT leading questions

2. **Questions are specific**
   - Not vague ("What do you think about X?")
   - Focus on past behavior, not hypothetical

3. **Questions will elicit useful answers**
   - Ask about problems, not solutions
   - Avoid "Would you use this?" (everyone says yes)

---

## Validation Logic

```python
import re

def validate_interview_questions_actionable(interview_script):
    issues = []
    warnings = []

    all_questions = []

    # Collect all questions
    for phase in ["background_questions", "problem_exploration_questions", "future_state_questions", "wrap_up_questions"]:
        questions = interview_script.get(phase, [])
        all_questions.extend(questions)

    for i, question in enumerate(all_questions):
        question_lower = question.lower()

        # Check for yes/no questions
        yes_no_starters = ["do you", "are you", "have you", "will you", "can you", "is it", "does it"]
        if any(question_lower.startswith(starter) for starter in yes_no_starters):
            warnings.append(f"Question #{i+1}: Appears to be yes/no question: '{question}'")

        # Check for leading questions
        leading_phrases = ["wouldn't you agree", "don't you think", "isn't it true"]
        if any(phrase in question_lower for phrase in leading_phrases):
            warnings.append(f"Question #{i+1}: Leading question detected: '{question}'")

        # Check for hypothetical questions
        if "would you" in question_lower or "if you could" in question_lower:
            warnings.append(f"Question #{i+1}: Hypothetical question (focus on past behavior): '{question}'")

        # Check for "Would you use" anti-pattern
        if "would you use" in question_lower:
            issues.append(f"Question #{i+1}: Avoid 'Would you use this?' (everyone says yes): '{question}'")

        # Check question starts with open-ended prompt
        good_starters = ["tell me", "walk me through", "describe", "what", "how", "why", "explain"]
        if not any(question_lower.startswith(starter) for starter in good_starters):
            warnings.append(f"Question #{i+1}: Doesn't start with open-ended prompt: '{question}'")

    # WARNING ONLY gate
    passed = True

    return {
        "passed": passed,
        "issues": issues,
        "warnings": warnings,
        "questions_checked": len(all_questions),
        "gate_type": "WARNING_ONLY"
    }
```

---

## Example: Pass vs. Fail

### ✅ PASS - Open-ended questions
```json
{
  "interview_script": {
    "problem_exploration_questions": [
      "Tell me about the last time you had to manage a marketing campaign.",
      "Walk me through your workflow for tracking ROI.",
      "What's the most frustrating part of using multiple tools?"
    ]
  }
}
```

### ⚠️ WARNING - Yes/no questions
```json
{
  "interview_script": {
    "problem_exploration_questions": [
      "Do you find your current tools frustrating?",
      "Would you use a new tool if it solved this problem?"
    ]
  }
}
```

---

## Success Message

```
✅ Gate Passed: Interview Questions Actionable
- Checked: 15 questions
- All open-ended
- Focus on past behavior
- No leading questions
- Ready for next task
```

---

## Warning Message

```
⚠️ Gate Warning: Interview Questions Actionable (WARNING ONLY)
Warnings found:
- Question #3: Appears to be yes/no question: 'Do you use HubSpot?'
- Question #7: Hypothetical question (focus on past behavior): 'What would you do if...'

Issues found:
- Question #10: Avoid 'Would you use this?' (everyone says yes)

Recommendation: Rewrite questions to be more open-ended.
Proceeding to next task (warning only).
```

---

## Notes

This gate is **WARNING ONLY** because:
- Interview scripts can be refined during actual research
- Some yes/no questions acceptable for screeners
- Research team can adapt questions in real-time
