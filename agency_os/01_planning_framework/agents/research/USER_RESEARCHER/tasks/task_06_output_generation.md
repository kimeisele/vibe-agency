# Task 06: Output Generation

**Task ID:** task_06_output_generation
**Dependencies:** All previous tasks
**Output:** user_insights (for research_brief.json)

---

## Objective

Compile all user research into the final `user_insights` section of `research_brief.json`.

---

## Instructions

### Step 1: Aggregate Data
- personas.json (Task 1)
- pain_points.json (Task 2)
- interview_script.json (Task 3)
- survey_template.json (Task 4)
- user_journeys.json (Task 5)

### Step 2: Format for Data Contract
Transform to match `research_brief.schema.json` format.

### Step 3: Run Validation Gates
- gate_personas_industry_standard
- gate_interview_questions_actionable

---

## Output Format

```json
{
  "user_insights": {
    "personas": [
      {
        "name": "Marketing Mary",
        "age_range": "28-35",
        "job_title": "Marketing Manager",
        "goals": ["Increase lead gen by 30%", "Reduce manual work"],
        "pain_points": ["Too many tools", "Can't track attribution"],
        "tools_used": ["HubSpot", "Google Analytics"],
        "quote": "I need tools that help me work smarter."
      }
    ],
    "pain_points": [
      "Managing multiple disconnected tools wastes time",
      "Can't track marketing attribution accurately"
    ],
    "interview_script": {
      "intro": "Thanks for taking time...",
      "questions": [
        "Tell me about the last time you managed a marketing campaign.",
        "What's the hardest part about tracking ROI?"
      ]
    },
    "user_journeys": [
      {
        "stage": "Awareness",
        "touchpoints": ["Google search", "LinkedIn"],
        "emotions": "Frustrated, curious"
      }
    ]
  }
}
```

---

## Quality Checklist

- [ ] Personas follow industry-standard format
- [ ] Interview questions are open-ended and actionable
- [ ] Pain points are specific (not vague)
- [ ] User journeys document all 5 stages
- [ ] Conforms to research_brief.schema.json

---

## Handoff

This `user_insights` section will be:
1. Included in `research_brief.json`
2. Passed to **LEAN_CANVAS_VALIDATOR** to inform customer segments
3. Used to validate product-market fit assumptions
