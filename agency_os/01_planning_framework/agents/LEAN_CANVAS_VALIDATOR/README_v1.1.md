# LEAN_CANVAS_VALIDATOR v1.1 - Project Context Modes

## Adaptive Workflow Selection

### Mode Matrix

| project_type | Canvas Mode | Duration | Data Source | Use Case |
|--------------|-------------|----------|-------------|----------|
| **commercial** | Full Interview (9 fields) | 15-20 min | User-driven | Startups, Business Ideas |
| **portfolio** | Quick Research (3 fields) | 5-8 min | WebSearch + User confirm | Job Applications, Showcases |
| **demo** | Quick Research (3 fields) | 5-8 min | WebSearch + User confirm | Proof-of-Concepts, Prototypes |
| **nonprofit** | Quick Research (3 fields) | 5-8 min | WebSearch + User confirm | Charitable Projects, NGOs |
| **personal** | Quick Research (3 fields) | 5-8 min | WebSearch + User confirm | Side Projects, Learning |
| *(not set)* | Full Interview (default) | 15-20 min | User-driven | Backward Compatibility |

---

## Quick Research Mode Details

### Core Principle
**"Research-First, User-Validates"** instead of "User-Answers-Everything"

### Process Flow

```
1. User provides vague description
   ↓
2. Agent executes WebSearch (market research)
   ↓
3. Agent synthesizes findings
   ↓
4. User confirms/corrects (fast validation)
   ↓
5. Agent generates riskiest assumptions
   ↓
6. Output: Simplified Canvas (3 fields) + Assumptions
```

### What Gets Skipped (Quick Mode)

- UVP (derived later in VIBE_ALIGNER)
- Channels (not relevant for portfolio/demo)
- Revenue/Costs (set to defaults like "Free/Open-Source" or "Time-Investment")
- Key Metrics (set to defaults like "GitHub Stars, User Feedback")
- Unfair Advantage (usually none for portfolio)

### What Remains (Quick Mode)

- ✅ Problem (WebSearch-validated)
- ✅ Customer Segments (inferred + confirmed)
- ✅ Riskiest Assumptions (LLM-generated)

This is sufficient for VIBE_ALIGNER to proceed with feature extraction!

---

## Auto-WebSearch Integration

### Trigger Conditions

1. **Explicit Request:** User says "I don't know" or "research this"
2. **Low Confidence:** Vague indicators detected ("maybe", "not sure", "I think")
3. **Short Response:** <10 words for complex question
4. **Quick Research Mode:** Always active for non-commercial projects

### WebSearch Query Construction

```python
def construct_query(field, user_context):
    templates = {
        "problem": f"{user_context['domain']} pain points challenges {current_year}",
        "customer_segments": f"{user_context['domain']} target users early adopters",
        "market_size": f"{user_context['domain']} market size TAM {current_year}"
    }
    return templates[field]
```

---

## Benefits of Quick Research Mode

### For Portfolio/Demo Projects

✅ **Time-Efficient:** 5-8 min instead of 15-20 min
✅ **Less Friction:** User doesn't need to answer business questions they can't answer
✅ **Evidence-Based:** Research provides actual market data (not guesses)
✅ **Sufficient for Planning:** VIBE_ALIGNER gets what it needs

### For Commercial Projects

✅ **Deep Validation:** Full 9-field interview forces critical thinking
✅ **Risk Identification:** More comprehensive assumption mapping
✅ **Investor-Ready:** Canvas can be shared with stakeholders

---

## Implementation Notes

### SOP_001 Integration

```yaml
# Pseudo-code for SOP_001
project_type = read_from_manifest("project_type", default="commercial")

if project_type == "commercial":
  invoke: LEAN_CANVAS_VALIDATOR (mode=full_interview)
  duration: 15-20 min
else:
  invoke: LEAN_CANVAS_VALIDATOR (mode=quick_research)
  duration: 5-8 min

# Both modes output same schema → VIBE_ALIGNER compatibility
```

### Backward Compatibility

- If `project_type` is missing → defaults to "commercial" (full mode)
- Existing project_manifest.json files work without changes
- Users can opt-in to quick mode by adding `project_type` field

---

## User Experience Example

### Before v1.1 (Frustrating for Portfolio)

```
Agent: "What are the Top 3 problems your target customers have?"
User: "Um... I don't really know. This is just a portfolio project."
Agent: "Please answer the question to proceed."
User: *frustrated* "Can you just skip this?"
```

### After v1.1 (Smooth for Portfolio)

```
Agent: "I see this is a portfolio project. Let me research typical
       pain points in [your domain] and you can confirm if it matches
       your vision. This will take 5 minutes instead of 20."
User: "Perfect!"
Agent: *executes WebSearch* "Based on 2024 research, I found:
       1. [Pain Point with Source]
       Does this align with your project goals?"
User: "Yes, exactly!"
```

---

## v1.1 Summary

**What Changed:**
- ✅ Added `project_type` enum to schema
- ✅ Added Quick Research Mode (5-8 min vs 15-20 min)
- ✅ Added Auto-WebSearch trigger logic
- ✅ Updated LEAN_CANVAS_VALIDATOR prompts

**What Stayed Same:**
- ✅ Output schema (backward compatible)
- ✅ VIBE_ALIGNER integration (no changes needed)
- ✅ Default behavior (commercial projects unchanged)

**Impact:**
- 🎯 Portfolio/Demo projects: 60% faster workflow
- 🎯 Commercial projects: Same high-quality process
- 🎯 All projects: Auto-research for vague answers

---

**Version:** 1.1.0
**Date:** 2025-11-13
**Status:** Production-Ready
