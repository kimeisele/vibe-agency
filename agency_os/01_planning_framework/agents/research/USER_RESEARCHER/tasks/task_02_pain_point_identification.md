# Task 02: Pain Point Identification

**Task ID:** task_02_pain_point_identification
**Dependencies:** task_01
**Input:** personas.json, user_vision
**Output:** pain_points.json

---

## Objective

Extract and consolidate pain points from personas and user vision.

---

## Instructions

### Step 1: Extract from Personas
From personas.json:
- Collect all pain_points fields
- Identify common themes
- Prioritize by frequency

### Step 2: Extract from User Vision
From user_vision:
- What problem is being solved?
- What frustrations are mentioned?
- What inefficiencies exist?

### Step 3: Consolidate and Prioritize
- Group similar pain points
- Rank by severity/frequency
- Make specific (not vague)

---

## Output Format

```json
{
  "pain_points": [
    {
      "pain_point": "Managing multiple disconnected tools wastes time",
      "severity": "high",
      "frequency": "daily",
      "personas_affected": ["Marketing Mary", "Sales Sam"],
      "current_workarounds": [
        "Manual data entry between systems",
        "Spreadsheets as integration layer"
      ],
      "cost_of_pain": "5-10 hours/week per person"
    },
    {
      "pain_point": "Can't track marketing attribution accurately",
      "severity": "high",
      "frequency": "weekly",
      "personas_affected": ["Marketing Mary"],
      "current_workarounds": [
        "Rough estimates from Google Analytics",
        "UTM parameters (incomplete)"
      ],
      "cost_of_pain": "Unable to justify marketing spend, risk of budget cuts"
    }
  ],
  "summary": {
    "total_pain_points": 8,
    "high_severity": 3,
    "medium_severity": 4,
    "low_severity": 1
  }
}
```

---

## Next Task

Proceed to **Task 03: Interview Script Creation**
