# Task 01: Persona Generation

**Task ID:** task_01_persona_generation
**Dependencies:** None (first task)
**Input:** user_vision, market_analysis
**Output:** personas.json

---

## Objective

Generate 2-3 industry-standard user personas based on market analysis and user vision.

---

## Instructions

### Step 1: Review Market Analysis
From market_analysis:
- Who are competitors targeting?
- What customer segments exist?
- What problems are users trying to solve?

### Step 2: Apply Persona Template
Use template from `RESEARCH_persona_templates.yaml`:
- Demographics (age, job title, company size)
- Psychographics (goals, pain points, motivations)
- Behavioral (tools used, decision criteria, tech savviness)
- Quote (representative statement)

### Step 3: Avoid Anti-Patterns
From `RESEARCH_persona_templates.yaml`:
- ❌ Too generic ("anyone who wants to be productive")
- ❌ Unrealistic combinations ("Tech-savvy C-level who codes daily")
- ❌ All positive traits ("smart, motivated, well-funded")
- ❌ Demographic-only (no behavioral data)

### Step 4: Generate 2-3 Personas
- Primary persona (main target)
- Secondary persona (secondary target)
- Tertiary persona (optional, edge case)

---

## Output Format

```json
{
  "personas": [
    {
      "name": "Marketing Mary",
      "persona_type": "primary",
      "age_range": "28-35",
      "job_title": "Marketing Manager",
      "company_size": "50-200 employees",
      "industry": "B2B SaaS",
      "goals": [
        "Increase lead generation by 30%",
        "Reduce manual work in campaign management",
        "Prove ROI to leadership"
      ],
      "pain_points": [
        "Too many disconnected tools",
        "Can't track attribution accurately",
        "Limited budget, need to justify spend"
      ],
      "motivations": [
        "Career advancement",
        "Learning new skills",
        "Data-driven decision making"
      ],
      "tools_used": ["HubSpot", "Google Analytics", "Mailchimp"],
      "information_sources": ["Marketing blogs", "LinkedIn", "Industry conferences"],
      "decision_criteria": [
        "Ease of use",
        "Integration with existing tools",
        "Price",
        "Customer support quality"
      ],
      "tech_savviness": "medium",
      "quote": "I need tools that help me work smarter, not add more complexity to my day."
    }
  ]
}
```

---

## Next Task

Proceed to **Task 02: Pain Point Identification**
