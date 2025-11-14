# Validation Gate: Adaptive Quality Threshold

**Gate ID:** gate_quality_threshold
**Purpose:** Validate research quality with adaptive thresholds based on project type
**Enforcement:** CONDITIONAL BLOCKING - can block or warn depending on project type

---

## Context

Different project types have different research requirements:
- **Commercial/SaaS:** Requires full market validation (high threshold)
- **Internal/Portfolio:** Self-contained projects (low threshold)
- **Startups:** Mixed requirements (medium threshold)

This gate implements **adaptive thresholds** instead of a single rigid rule.

---

## Validation Criteria

This gate checks research quality RELATIVE to the project type:

1. **Detect project type** from research_brief or user input
   - Keywords: "internal", "portfolio", "commercial", "SaaS", "startup"
   - Default: "commercial"

2. **Apply adaptive threshold**
   ```
   ✅ internal/portfolio:    quality_score >= 30  (Lenient)
   ✅ startup:               quality_score >= 40  (Moderate)
   ✅ commercial/SaaS:       quality_score >= 50  (Strict)
   ```

3. **Explain threshold rationale** to user
   - Why this threshold was chosen
   - What it means for the project

4. **Interactive failure handling**
   - If quality < threshold: WARN user
   - Ask: "Continue anyway? (y/n)"
   - If yes: ALLOW with reduced confidence
   - If no: BLOCK workflow

---

## Validation Logic

```python
def detect_project_type(research_brief_or_input):
    """
    Detect project type from research_brief or user keywords.

    Returns:
    - "commercial": SaaS, B2B, startup with revenue model
    - "internal": Internal tool, employee-focused
    - "portfolio": Hobby project, portfolio piece, learning
    - "nonprofit": Nonprofit mission
    - "enterprise": Large enterprise tool
    """

    # Check if project_type already in research_brief
    if "project_type" in research_brief_or_input:
        return research_brief_or_input["project_type"]

    # Extract keywords from description/vision
    description = research_brief_or_input.get("project_vision", "").lower()

    if any(keyword in description for keyword in ["internal", "internal-only", "employee", "team tool"]):
        return "internal"

    if any(keyword in description for keyword in ["portfolio", "portfolio piece", "learning", "exercise", "hobby"]):
        return "portfolio"

    if any(keyword in description for keyword in ["nonprofit", "open source", "public good"]):
        return "nonprofit"

    if any(keyword in description for keyword in ["enterprise", "corporate", "large team"]):
        return "enterprise"

    if any(keyword in description for keyword in ["SaaS", "startup", "B2B", "B2C", "revenue"]):
        return "commercial"

    # Default to commercial (safest assumption)
    return "commercial"


def calculate_quality_threshold(research_brief):
    """
    Calculate quality threshold based on project type.

    Returns:
    {
        "project_type": "internal",
        "threshold": 30,
        "min_quality_score": 30,
        "rationale": "Internal projects don't require market validation..."
    }
    """

    project_type = detect_project_type(research_brief)

    thresholds = {
        "internal": {
            "threshold": 30,
            "rationale": "Internal projects are self-contained and don't need competitors/market data. Low threshold acceptable."
        },
        "portfolio": {
            "threshold": 35,
            "rationale": "Portfolio projects are demonstration pieces. Market research is optional for learning purposes."
        },
        "nonprofit": {
            "threshold": 40,
            "rationale": "Nonprofit projects may have limited market data. Quality threshold adjusted for mission-driven work."
        },
        "startup": {
            "threshold": 45,
            "rationale": "Startups need good market understanding but may have limited resources for extensive research."
        },
        "enterprise": {
            "threshold": 55,
            "rationale": "Enterprise projects must meet high standards. Full market validation and compliance required."
        },
        "commercial": {
            "threshold": 50,
            "rationale": "Commercial projects require full market validation, competitor analysis, and pricing research."
        }
    }

    config = thresholds.get(project_type, thresholds["commercial"])

    return {
        "project_type": project_type,
        "threshold": config["threshold"],
        "rationale": config["rationale"]
    }


def validate_quality_threshold(research_brief, fact_validation, user_interaction=None):
    """
    Validate research quality with adaptive threshold.

    Args:
        research_brief: Contains project info and project_type
        fact_validation: Contains quality_score and issues
        user_interaction: Optional user response to "continue anyway?" prompt

    Returns:
    {
        "passed": bool,
        "blocking": bool,
        "quality_score": int,
        "threshold": int,
        "project_type": str,
        "messages": [str],
        "user_override": bool
    }
    """

    # Get quality score
    quality_score_str = fact_validation.get("quality_score", "0/100")
    quality_score = int(quality_score_str.split("/")[0])

    # Calculate adaptive threshold
    threshold_config = calculate_quality_threshold(research_brief)
    threshold = threshold_config["threshold"]
    project_type = threshold_config["project_type"]
    rationale = threshold_config["rationale"]

    messages = []
    user_override = False

    # Check if quality meets threshold
    if quality_score >= threshold:
        messages.append(f"✅ Quality score {quality_score}/100 meets threshold ({threshold}) for {project_type} project")
        messages.append(f"   Rationale: {rationale}")
        return {
            "passed": True,
            "blocking": False,
            "quality_score": quality_score,
            "threshold": threshold,
            "project_type": project_type,
            "messages": messages,
            "user_override": False
        }

    # Quality below threshold
    messages.append(f"⚠️  Quality score {quality_score}/100 is below threshold ({threshold}) for {project_type} project")
    messages.append(f"   Rationale: {rationale}")

    # Check for user override
    if user_interaction == "continue_anyway":
        messages.append(f"⚠️  User chose to continue despite low quality score")
        messages.append(f"   Confidence level: LOW")
        user_override = True

        return {
            "passed": True,
            "blocking": False,
            "quality_score": quality_score,
            "threshold": threshold,
            "project_type": project_type,
            "messages": messages,
            "user_override": True
        }

    # No override - BLOCK
    messages.append(f"❌ Research quality insufficient. Workflow blocked.")
    messages.append(f"   ACTION: Improve research quality to {threshold}+ and re-run FACT_VALIDATOR")

    return {
        "passed": False,
        "blocking": True,
        "quality_score": quality_score,
        "threshold": threshold,
        "project_type": project_type,
        "messages": messages,
        "user_override": False
    }
```

---

## Example Scenarios

### ✅ PASS: Internal Project (Low Threshold)
```json
{
  "research_brief": {
    "project_type": "internal",
    "project_vision": "Build an internal tool for our team"
  },
  "fact_validation": {
    "quality_score": "32/100",
    "issues_found": 5,
    "issues_critical": 0,
    "flagged_hallucinations": []
  }
}
```

**Result:**
```
✅ PASS - Quality Threshold Met
- Project type: internal
- Quality score: 32/100
- Required threshold: 30
- Status: PASS (internal projects don't require market validation)
```

### ✅ PASS: Commercial Project (High Quality)
```json
{
  "research_brief": {
    "project_type": "commercial",
    "project_vision": "Build a SaaS tool to compete in the market"
  },
  "fact_validation": {
    "quality_score": "75/100",
    "issues_found": 2,
    "issues_critical": 0,
    "flagged_hallucinations": []
  }
}
```

**Result:**
```
✅ PASS - Quality Threshold Met
- Project type: commercial
- Quality score: 75/100
- Required threshold: 50
- Status: PASS (exceeds commercial project requirements)
```

### ⚠️  USER PROMPT: Commercial Project (Low Quality)
```json
{
  "research_brief": {
    "project_type": "commercial",
    "project_vision": "Build a SaaS tool but limited research time"
  },
  "fact_validation": {
    "quality_score": "38/100",
    "issues_found": 15,
    "issues_critical": 0,
    "flagged_hallucinations": ["competitor_data_incomplete"]
  }
}
```

**Result:**
```
⚠️  QUALITY THRESHOLD NOT MET

Project type: commercial
Quality score: 38/100
Required threshold: 50

Rationale: Commercial projects require full market validation, competitor analysis, and pricing research.

Missing elements:
- Incomplete competitor data
- Limited market size analysis
- Insufficient pricing research

ACTION REQUIRED:
Continue anyway? (y/n)

If YES: Research will proceed with LOW CONFIDENCE ⚠️
If NO:  Workflow BLOCKED - return to MARKET_RESEARCHER or TECH_RESEARCHER to improve research
```

### ❌ FAIL: Critical Issues (Always Blocks)
```json
{
  "research_brief": {
    "project_type": "portfolio",
    "project_vision": "Portfolio project"
  },
  "fact_validation": {
    "quality_score": "15/100",
    "issues_critical": 3,
    "issues_found": 12,
    "flagged_hallucinations": [
      {
        "claim": "Company has no competitors",
        "severity": "critical"
      }
    ]
  }
}
```

**Result:**
```
🛑 GATE BLOCKED - Critical Issues Detected

Project type: portfolio
Quality score: 15/100
Required threshold: 35

Blocker: 3 CRITICAL ISSUES FOUND
- Even with low threshold for portfolio projects, critical hallucinations must be resolved

Critical hallucination:
- "Company has no competitors" (has no source)

ACTION REQUIRED:
1. Fix critical hallucinations in FACT_VALIDATOR
2. Verify all major claims have sources
3. Re-run research if necessary
4. Re-run FACT_VALIDATOR

WORKFLOW BLOCKED - Cannot proceed
```

---

## Blocking Behavior

When this gate fails (no user override):
1. **STOP** workflow progression
2. **RETURN** to MARKET_RESEARCHER or TECH_RESEARCHER
3. **SHOW** quality report with specific gaps
4. **BLOCK** handoff to LEAN_CANVAS_VALIDATOR

When user chooses "continue anyway":
1. **PROCEED** with LOW confidence flag
2. **LOG** that threshold was overridden
3. **WARN** in subsequent steps that research quality is below standard
4. **ALLOW** progression to next step (non-blocking)

---

## Success Message

```
✅ Gate Passed: Quality Threshold Met

Project type: internal
Quality score: 32/100
Required threshold: 30
Confidence level: HIGH

Rationale: Internal projects are self-contained and don't require extensive market validation.
Research quality is acceptable for this project type.

Ready to proceed to USER_RESEARCHER or finalize research_brief.
```

---

## Failure Message (BLOCKING)

```
🛑 GATE BLOCKED: Quality Below Threshold

Project type: commercial
Quality score: 38/100
Required threshold: 50

Rationale: Commercial projects require full market validation, competitor analysis, and pricing research.

Research gaps:
- Competitor data: INCOMPLETE (only 2 of 5 competitors found)
- Market size: UNVERIFIED (no sources)
- Pricing analysis: MISSING (not researched)

ACTION REQUIRED:
1. Return to MARKET_RESEARCHER to complete competitor research
2. Return to TECH_RESEARCHER to verify market size
3. Add pricing analysis to MARKET_RESEARCHER tasks
4. Re-run FACT_VALIDATOR after improvements

Continue anyway? (y/n)
- If YES: Proceed with LOW confidence ⚠️
- If NO: Workflow BLOCKED

Contact research team if you need help improving research quality.
```

---

## YAML Schema Addition

This gate requires adding `project_type` to the research_brief schema:

```yaml
- name: "research_brief.schema.json"
  version: "1.1.0"
  fields:
    - name: "project_type"
      type: "string"
      enum: ["commercial", "internal", "portfolio", "nonprofit", "enterprise"]
      default: "commercial"
      description: "Project context type - determines quality threshold strictness"
      required: false
```

---

## Integration Notes

1. **When to run:** After FACT_VALIDATOR completes quality assessment
2. **Input:** research_brief + fact_validation output
3. **Output:** Quality assessment with adaptive threshold results
4. **Non-blocking:** Can be overridden by user (with warning)
5. **Backward compatible:** If no project_type specified, defaults to "commercial"
