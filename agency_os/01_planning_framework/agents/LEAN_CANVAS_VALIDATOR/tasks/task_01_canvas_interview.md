# === TASK: Lean Canvas Interview ===

## TASK IDENTITY
- **Task ID**: 01_canvas_interview
- **Phase**: 1 of 3
- **Purpose**: Systematically collect Lean Canvas data through interview OR research

## VERSION 1.1 UPDATE: Adaptive Mode Selection

**NEW:** Framework now adapts to project context!

### Mode Selection Logic

```yaml
if project_type in ["commercial"]:
  mode: FULL_INTERVIEW (9 fields, user-driven)
elif project_type in ["portfolio", "demo", "nonprofit", "personal"]:
  mode: QUICK_RESEARCH (3 core fields, research-driven)
else:
  mode: FULL_INTERVIEW (default, backward-compatible)
```

---

## MODE 1: FULL INTERVIEW (Commercial Projects)

**When:** project_type = "commercial"
**Duration:** 15-20 minutes
**Data Source:** User answers

### Opening Statement

```
Welcome! You're building a commercial product. Before we dive into technical planning,
I'll guide you through the "Lean Canvas" - a 9-field framework that helps us identify
the riskiest assumptions in your business model BEFORE we invest in building.

This will take about 15-20 minutes. Ready to begin?
```

### Interview Sequence (9 Fields)

[... Full 9-field interview as defined in original version ...]

(Content remains same as original task_01_canvas_interview.md for commercial projects)

---

## MODE 2: QUICK RESEARCH (Portfolio/Demo/Nonprofit/Personal)

**When:** project_type in ["portfolio", "demo", "nonprofit", "personal"]
**Duration:** 5-8 minutes
**Data Source:** WebSearch + User confirmation

### Opening Statement

```
Welcome! I see this is a {project_type} project.

For {portfolio/demo/nonprofit/personal} projects, I'll use a streamlined approach:
I'll research typical pain points and validate assumptions with you, rather than
conducting a full 9-field business interview.

This will take about 5-8 minutes. Ready?
```

### Quick Research Process (3 Core Fields)

#### Step 1: Problem Research (Auto-WebSearch)

**Agent Action:**
```
1. Execute WebSearch for problem domain
   Query: "{user_description} pain points challenges 2024"

2. Synthesize findings into Problem Statement:
   - Top 3 pain points (evidence-based)
   - Current alternatives being used
   - Why alternatives are insufficient

3. Present to user for confirmation:
   "Based on market research, I found these pain points for [domain]:
    1. [Pain Point 1] - Evidence: [Source]
    2. [Pain Point 2] - Evidence: [Source]
    3. [Pain Point 3] - Evidence: [Source]

   Does this match your understanding, or should I adjust?"
```

**User Response:** Confirms or corrects

---

#### Step 2: Customer Segments (Inferred + Confirmed)

**Agent Action:**
```
Based on your project description ("{user_description}"), I infer:

**Primary User Segment:** [Derived from description]
**Characteristics:** [Based on problem research]

For a {project_type}, the key question is:
"Who would use this as a demo/portfolio piece or benefit from it?"

Correct?
```

**User Response:** Confirms or corrects

---

#### Step 3: Riskiest Assumptions (LLM-Generated)

**Agent Action:**
```
Based on the problem and solution you described, here are the riskiest
assumptions your {project_type} should validate:

1. **[Assumption Category]**: [Specific assumption]
   - Why risky: [Rationale]
   - How to validate: [Approach]

2. **[Assumption Category]**: [Specific assumption]
   - Why risky: [Rationale]
   - How to validate: [Approach]

Does this align with your goals for this project?
```

**User Response:** Confirms or adds

---

### Quick Research Fields Summary

| Field | Full Interview | Quick Research |
|-------|----------------|----------------|
| **Problem** | User answers 3 questions | Auto-WebSearch + User confirms |
| **Customer Segments** | User describes early adopters | Inferred from description + User confirms |
| **UVP** | User defines | *(Skipped - derived in VIBE_ALIGNER)* |
| **Solution** | User describes MVP | *(Skipped - defined in Requirements)* |
| **Channels** | User lists | *(Skipped - not relevant for portfolio)* |
| **Revenue** | User defines pricing | *(Skipped - or set to "Free/Open-Source")* |
| **Costs** | User estimates | *(Skipped - or set to "Time-Investment")* |
| **Key Metrics** | User defines | *(Skipped - or set to "GitHub Stars, Feedback")* |
| **Unfair Advantage** | User defines | *(Skipped - usually none for portfolio)* |
| **Riskiest Assumptions** | Derived from 9 fields | LLM-generated from Problem + Solution |

---

## AUTO-WEBSEARCH TRIGGER (Both Modes)

**NEW v1.1 Feature:** Auto-detect vague responses and trigger WebSearch

### Confidence Detection

```python
def detect_confidence(user_response):
    vague_indicators = [
        "I don't know", "not sure", "maybe", "I think",
        "probably", "might be", "unsure", "unclear"
    ]

    if any(indicator in user_response.lower() for indicator in vague_indicators):
        return "LOW"
    elif len(user_response.split()) < 10:
        return "MEDIUM"
    else:
        return "HIGH"
```

### Auto-Research Flow

```
if confidence_level == "LOW":
    agent: "No problem! Let me research this for you."
    execute: WebSearch(query=construct_query(field, user_context))
    present: "Based on research, here's what I found: [...]
             Does this match what you had in mind?"
```

---

## OUTPUTS (Both Modes)

### canvas_responses (Structured)

```json
{
  "mode": "full_interview" | "quick_research",
  "canvas_type": "complete" | "simplified",
  "fields": {
    "problem": "...",
    "customer_segments": "...",
    "riskiest_assumptions": ["...", "..."]
  },
  "data_sources": {
    "problem": "user" | "websearch",
    "customer_segments": "user" | "inferred",
    "assumptions": "derived" | "llm_generated"
  }
}
```

---

## TRANSITION TO NEXT TASK

Pass canvas responses to task 02_risk_analysis

**Note for Quick Research Mode:**
Risk analysis will use simplified canvas but still identify 2-3 critical assumptions.

---

## BACKWARD COMPATIBILITY

**Legacy Behavior (no project_type set):**
- Defaults to FULL_INTERVIEW mode
- 100% backward compatible with existing workflows

**Migration Path:**
- Add `project_type` field to project_manifest.json
- Framework auto-adapts on next run

---

# === END TASK ===
