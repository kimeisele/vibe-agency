# Task 04: Positioning Analysis

**Task ID:** task_04_positioning_analysis
**Dependencies:** task_01, task_02, task_03
**Output:** positioning_map.json

---

## Objective

Identify positioning opportunities and white space in the market based on competitor analysis.

---

## Instructions

### Step 1: Map Competitor Positioning
Using data from previous tasks, map how competitors position themselves:
- What do they emphasize? (ease of use, power features, price, integrations)
- Who do they target? (enterprise, SMB, individuals)
- What's their primary differentiation?

### Step 2: Identify White Space
Look for gaps in:
- **Underserved segments:** Customer types no one targets well
- **Feature gaps:** Capabilities competitors lack
- **Pricing gaps:** Price points with few options
- **UX gaps:** Opportunities for simpler or more powerful UX

### Step 3: Analyze Differentiation Opportunities
Reference `RESEARCH_competitor_analysis_templates.yaml` for strategies:
- Niche focus
- Pricing innovation
- User experience excellence
- Integration depth
- Open source alternative

### Step 4: Create Positioning Recommendations
Based on analysis, suggest 3-5 positioning opportunities

---

## Output Format

```json
{
  "positioning_map": {
    "axes": {
      "x_axis": "Price (Low to High)",
      "y_axis": "Features (Simple to Complex)"
    },
    "competitors": [
      {
        "name": "Asana",
        "position": {"x": 3, "y": 4},
        "quadrant": "High price, feature-rich"
      }
    ]
  },
  "positioning_opportunities": [
    {
      "strategy": "Niche focus",
      "description": "Target creative agencies specifically (none of the major players focus on this vertical)",
      "differentiation": "Pre-built templates for agency workflows, creative feedback tools",
      "estimated_segment_size": "$50M SAM"
    },
    {
      "strategy": "Pricing innovation",
      "description": "Flat-rate pricing vs per-user (Basecamp model)",
      "differentiation": "Predictable costs for growing teams",
      "estimated_segment_size": "10-15% of SMB market"
    }
  ],
  "white_space_analysis": {
    "underserved_segments": ["Creative agencies", "Remote-first teams"],
    "feature_gaps": ["Built-in time tracking", "Client portal"],
    "pricing_gaps": ["$50-100/month flat rate (between freemium and per-user enterprise)"]
  }
}
```

---

## Quality Checklist

- [ ] At least 3 positioning opportunities identified
- [ ] Each opportunity has clear differentiation
- [ ] Opportunities are specific (not "better UX")
- [ ] White space analysis grounded in competitor research
- [ ] Realistic assessment of opportunity size

---

## Next Task

Proceed to **Task 05: Risk Identification**
