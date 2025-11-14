# Task 05: Risk Identification

**Task ID:** task_05_risk_identification
**Dependencies:** task_01, task_02, task_03, task_04
**Output:** risk_assessment.json

---

## Objective

Identify and assess market risks that could impact success.

---

## Instructions

### Step 1: Assess Market Saturation
- How many competitors exist?
- How mature is the market?
- Are there dominant players (>30% market share)?

### Step 2: Identify Entry Barriers
- How easy is it to replicate the product?
- Are there strong network effects?
- How much capital is required?
- What's the sales cycle length?

### Step 3: Analyze Competitive Threats
- Are competitors well-funded?
- Any recent large funding rounds in the space?
- Are major tech companies entering this market?

### Step 4: Evaluate Technology Risks
- Is the underlying technology changing rapidly?
- Are there platform dependencies?
- Regulatory risks?

### Step 5: Document All Risks
Use risk categories from `RESEARCH_competitor_analysis_templates.yaml`:
- Market saturation
- Dominant player
- Low barriers to entry
- Technology shift
- Funding requirements

---

## Output Format

```json
{
  "risk_assessment": {
    "risks": [
      {
        "category": "market_saturation",
        "severity": "high",
        "description": "10+ established competitors including well-funded startups (Monday.com, Asana, ClickUp)",
        "indicators": [
          "Multiple Series B-C funded competitors",
          "Market leaders with strong brand recognition"
        ],
        "mitigation_strategies": [
          "Focus on underserved niche (creative agencies)",
          "Differentiate through vertical-specific features"
        ]
      },
      {
        "category": "dominant_player",
        "severity": "medium",
        "description": "Microsoft Project has significant enterprise presence but weak in SMB segment",
        "indicators": [
          "Strong brand in enterprise",
          "Limited cloud/collaboration features"
        ],
        "mitigation_strategies": [
          "Target cloud-first SMBs",
          "Focus on collaboration over planning"
        ]
      }
    ],
    "overall_risk_level": "medium-high",
    "proceed_recommendation": "PROCEED_WITH_CAUTION",
    "key_success_factors": [
      "Strong differentiation in target niche",
      "Capital efficiency (avoid competing on marketing spend)",
      "Fast product iteration"
    ]
  }
}
```

---

## Risk Severity Guidelines

- **Critical:** Major blockers (e.g., dominant player with 80% market share, dying market)
- **High:** Significant challenges (e.g., 10+ funded competitors, high barriers to entry)
- **Medium:** Manageable challenges (e.g., some competition, moderate funding needed)
- **Low:** Minor concerns

---

## Quality Checklist

- [ ] At least 3 risks identified
- [ ] Each risk has severity level
- [ ] Specific indicators provided (not vague)
- [ ] Mitigation strategies suggested
- [ ] Overall recommendation provided

---

## Next Task

Proceed to **Task 06: Output Generation**
