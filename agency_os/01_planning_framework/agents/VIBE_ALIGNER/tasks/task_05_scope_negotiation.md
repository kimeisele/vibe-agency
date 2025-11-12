# Task: Scope Negotiation (APCE)

## Objective
Prevent scope creep by calculating complexity and negotiating v1.0 boundaries using the APCE (Complexity & Prioritization Engine).

---

## Goal
Ensure the feature set is realistic and shippable within the user's timeline and scope choice.

---

## Input Artifacts
- `features_with_dependencies.json` (from Task 04)
- `APCE_rules.yaml` (from knowledge base)
- Session state: `user_scope_choice`

---

## Complexity Scoring

For EACH feature, calculate complexity using `APCE_rules.yaml`:

```python
# Pseudo-code for complexity scoring
total_complexity = 0

for feature in features_with_dependencies:
    # Get base complexity from APCE
    base = APCE.get_base_complexity(feature.type)

    # Apply multipliers
    multipliers = APCE.get_multipliers(feature.enhancements)
    final_complexity = base * product(multipliers)

    total_complexity += final_complexity

# Check if total exceeds v1.0 threshold
if total_complexity > APCE.v1_threshold:
    trigger_scope_negotiation()
```

---

## Negotiation Trigger Conditions

Trigger negotiation if:
- Total complexity > 60 points
- More than 10 features requested
- Any single feature > 13 complexity points
- User added features after initial planning ("scope creep")

---

## Negotiation Dialog Templates

### Scenario 1: Too Many Features

```
📊 SCOPE ANALYSIS

Thank you for the detailed vision! I've analyzed your {total_count} feature requests.

**Complexity Assessment:**
- Total complexity: {total_complexity} points
- Recommended v1.0 max: 50-60 points
- Current overage: {overage} points

To ensure a successful v1.0 launch, I recommend focusing on the core features that directly enable your value proposition.

**MUST HAVE (v1.0 Core)** - {must_have_count} features:
{list_must_haves_with_complexity}

**SHOULD HAVE (v1.0 Goals)** - {should_have_count} features:
{list_should_haves_with_complexity}

**WON'T HAVE (Planned for v2.0)** - {wont_have_count} features:
{list_wont_haves_with_reason}

**Reasoning:**
The "Must Have" scope ensures a strong, focused v1.0 that solves your core problem completely. The v2.0 features can be prioritized based on user feedback after launch.

**Timeline Impact:**
- Current scope: ~{current_weeks} weeks
- Recommended scope: ~{recommended_weeks} weeks
- Time saved: {time_saved} weeks

Shall we proceed with this focused v1.0 scope?

Options:
A) Proceed with recommended scope (faster launch)
B) Keep all features (extend timeline to {extended_weeks} weeks)
C) Let me know which features are non-negotiable, and I'll re-prioritize
```

---

### Scenario 2: Impossible Feature Detected

```
⚠️ TECHNICAL FEASIBILITY CONCERN

I've analyzed "{impossible_feature}" and identified a significant implementation challenge.

**The Challenge:**
{technical_reason_from_fae}

**Requirements:**
- {requirement_1}
- {requirement_2}
- {requirement_3}

**Typical timeline:** {weeks} weeks
**Complexity impact:** +{complexity_points} points

**For v1.0, I recommend:**

Option A: **{alternative_1}**
  - Timeline: {alt1_weeks} weeks
  - Complexity: {alt1_complexity} points
  - Tradeoff: {alt1_tradeoff}

Option B: **{alternative_2}**
  - Timeline: {alt2_weeks} weeks
  - Complexity: {alt2_complexity} points
  - Tradeoff: {alt2_tradeoff}

Option C: **Include original feature**
  - Timeline: Extend to {extended_weeks} weeks total
  - Risk: May delay validation of core value proposition

Which approach aligns best with your goals?
```

---

### Scenario 3: Mid-Planning Scope Creep

```
🔄 SCOPE CHANGE DETECTED

I've noted your additional request for: {new_features}

**Impact Analysis:**
- Additional complexity: +{added_complexity} points
- Timeline impact: +{added_weeks} weeks
- New total timeline: {new_total_weeks} weeks

**Your options:**

A) **Keep v1.0 focused** (recommended)
   - Current v1.0 scope stays as-is
   - New features go to v2.0 roadmap
   - Timeline: {original_weeks} weeks

B) **Extend timeline**
   - Include new features in v1.0
   - Timeline: {extended_weeks} weeks

C) **Feature swap**
   - Replace {current_feature} with {new_feature}
   - Timeline: {original_weeks} weeks (unchanged)

What's your priority: Fast launch or broader feature set?
```

---

## Output

Negotiated feature list with priorities:

```json
{
  "negotiated_features": [
    {
      "id": "feature_1",
      "name": "...",
      "priority": "must_have",
      "complexity_score": 5,
      "estimated_effort": "1-2 weeks"
    },
    {
      "id": "feature_2",
      "name": "...",
      "priority": "should_have",
      "complexity_score": 8,
      "estimated_effort": "2-3 weeks"
    },
    {
      "id": "feature_3",
      "name": "...",
      "priority": "wont_have_v1",
      "complexity_score": 13,
      "estimated_effort": "4-6 weeks",
      "reason_excluded": "Too complex for v1.0 timeline"
    }
  ],
  "scope_negotiation": {
    "total_complexity": 45,
    "complexity_breakdown": {
      "must_have": 30,
      "should_have": 15,
      "wont_have_v1": 25
    },
    "timeline_estimate": "10-14 weeks",
    "v1_exclusions": [
      "Feature X (too complex - see FAE-005)",
      "Feature Y (nice-to-have - deprioritized)"
    ]
  }
}
```

---

## Success Criteria

- Complexity calculated for all features
- Scope negotiation completed if threshold exceeded
- User agrees on must/should/won't priorities
- Total complexity within acceptable range (50-60 points for v1.0)

---

## Validation Gates

- `gate_complexity_within_threshold.md` - Ensures total complexity doesn't exceed v1.0 limits
