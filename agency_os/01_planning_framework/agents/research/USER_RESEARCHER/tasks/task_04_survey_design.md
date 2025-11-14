# Task 04: Survey Design

**Task ID:** task_04_survey_design
**Dependencies:** task_01, task_02
**Input:** personas.json, pain_points.json
**Output:** survey_template.json

---

## Objective

Create survey template for quantitative validation (optional, complements interviews).

---

## Instructions

### Step 1: Structure Survey
From `RESEARCH_interview_question_bank.yaml`:

1. **Screener questions** (qualify respondents)
2. **Core questions** (main research objectives, 10-15 max)
3. **Demographics** (put at end to avoid drop-off)

### Step 2: Question Types
- **Multiple choice:** Quantifying preferences/behaviors
- **Rating scale (1-5):** Measuring satisfaction/agreement
- **Open-ended:** Collecting qualitative insights
- **Ranking:** Prioritizing features/pain points

### Step 3: Best Practices
- Keep short (5-10 minutes max)
- Simple, clear language
- Avoid double-barreled questions
- Randomize answer options (avoid bias)
- Offer incentive for completion

---

## Output Format

```json
{
  "survey_template": {
    "title": "Understanding [Problem Area] Challenges for [Persona Role]",
    "estimated_time": "7 minutes",
    "incentive": "$10 Amazon gift card",
    "screener_questions": [
      {
        "question": "What is your current role?",
        "type": "multiple_choice",
        "options": ["Marketing Manager", "Marketing Director", "CMO", "Other"],
        "disqualify_if": ["Other"]
      },
      {
        "question": "Do you currently use tools for [task]?",
        "type": "yes_no",
        "disqualify_if": "no"
      }
    ],
    "core_questions": [
      {
        "question": "How often do you [perform task]?",
        "type": "multiple_choice",
        "options": ["Daily", "Weekly", "Monthly", "Rarely", "Never"]
      },
      {
        "question": "How satisfied are you with your current tools for [task]?",
        "type": "rating_scale",
        "scale": "1-5",
        "labels": {"1": "Very Dissatisfied", "5": "Very Satisfied"}
      },
      {
        "question": "What's the biggest challenge you face with [task]?",
        "type": "open_ended",
        "max_length": 500
      },
      {
        "question": "Rank these pain points in order of importance:",
        "type": "ranking",
        "options": ["Pain point 1", "Pain point 2", "Pain point 3"]
      }
    ],
    "demographics": [
      {
        "question": "Company size?",
        "type": "multiple_choice",
        "options": ["1-10", "11-50", "51-200", "201-1000", "1000+"]
      },
      {
        "question": "Industry?",
        "type": "multiple_choice",
        "options": ["Technology", "Healthcare", "Finance", "Other"]
      }
    ]
  }
}
```

---

## Next Task

Proceed to **Task 05: User Journey Mapping**
