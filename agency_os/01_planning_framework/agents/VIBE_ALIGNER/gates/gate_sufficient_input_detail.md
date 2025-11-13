# Validation Gate: Sufficient Input Detail

## Rule
User input must contain enough detail to extract concrete features. Too vague = need clarification.

---

## Minimum Required Information

To proceed with feature extraction, user input MUST contain at least:

### ✅ MUST Have (Minimum)
1. **Project Type** (explicit or inferable)
   - Examples: "booking system", "API", "mobile app", "dashboard"
   - Can be inferred from keywords: "users can book classes" → booking system

2. **Core User Action** (at least ONE)
   - Example: "users can book", "track workouts", "manage inventory"
   - Minimum 1 concrete action verb

3. **Target Scope Indicator** (explicit or inferable)
   - Explicit: "MVP", "v1.0", "prototype", "full app"
   - Inferable: Budget/timeline hints indicate scope

### 🟡 Should Have (Ideal)
4. **Technical Context** (nice to have)
   - Team expertise (JavaScript, Python, etc.)
   - Budget range ($5k, $50k, etc.)
   - Timeline (2 weeks, 3 months, etc.)

5. **Additional Features** (helps scoping)
   - "also needs authentication"
   - "with payment integration"

---

## Vagueness Levels

### 🟢 Green (Sufficient Detail - PASS)
```
Input: "I want a booking website for my yoga studio. Customers should
be able to see available classes, book a slot, and get email confirmation.
Budget is €25k, timeline 6 weeks."

Why sufficient:
✅ Project type: booking website
✅ Core actions: see classes, book slot, get confirmation
✅ Scope indicators: Budget + timeline suggest v1.0
✅ Technical context: Budget/timeline provided

Result: PROCEED to feature extraction
```

### 🟡 Yellow (Borderline - Ask 1-2 Clarifying Questions)
```
Input: "I need a fitness app for tracking workouts."

Why borderline:
✅ Project type: fitness app (clear)
✅ Core action: track workouts (clear)
⚠️ Missing: What KIND of tracking? (reps/sets? running distance? calories?)
⚠️ Missing: Mobile or web?
⚠️ Missing: Any other features? (social, analytics, etc.)

Action: Ask 2-3 focused questions:
1. "Mobile app (iOS/Android) or web application?"
2. "What workout data do users track? (e.g., exercises/reps, running distance, calories)"
3. "Any other must-have features for v1? (e.g., progress charts, workout history)"

Result: ASK then PROCEED
```

### 🔴 Red (Too Vague - Cannot Proceed)
```
Input: "I want to build something for my business."

Why too vague:
❌ No project type (what KIND of "something"?)
❌ No core action (what will users DO?)
❌ No scope indicators

Action: EDUCATE then ASK OPEN QUESTIONS:
"To help you, I need to understand your project better:
1. What problem are you solving? (e.g., 'customers can't book appointments online')
2. Who will use this? (e.g., 'my yoga studio customers')
3. What's the main thing users will do? (e.g., 'book classes, track orders, manage inventory')
4. What's your target timeline and budget? (helps scope v1.0)"

Result: CANNOT PROCEED until clarified
```

---

## Vagueness Indicators (Red Flags)

### ❌ Too Vague Phrases
- "I want a website" (what KIND of website?)
- "I need an app" (what does it DO?)
- "Something like Uber but for..." (need specifics, not just analogy)
- "Build me a platform" (too generic)
- "I have an idea for..." (what IS the idea?)

### ❌ Missing Core Elements
- No action verbs ("users can...")
- No user type mentioned (who is this for?)
- Only technology mentioned ("I want to use React") but no functionality

### ⚠️ Borderline Phrases (Ask 1-2 Questions)
- "Simple app" (how simple? which features?)
- "Just basics" (which basics exactly?)
- "Like [other app] but simpler" (which features do you want?)

---

## Clarification Strategy

### For 🔴 Red (Too Vague):
Use **open-ended questions** to get basic context:

```
"Let me understand your project better:

1. PROBLEM: What problem does this solve?
   Example: "Customers can't book appointments 24/7"

2. USERS: Who will use this?
   Example: "My yoga studio customers"

3. ACTION: What's the main thing users will do?
   Example: "Book classes and pay online"

4. CONTEXT: Rough budget and timeline?
   Example: "€20-30k, need it in 8 weeks"
```

### For 🟡 Yellow (Borderline):
Use **specific, focused questions** (max 3):

```
"I understand you want [project type]. A few quick questions:

1. [Specific technical question]
   Example: "Mobile app (iOS/Android) or web application?"

2. [Scope question]
   Example: "For v1.0, which features are must-have vs nice-to-have?"

3. [Context question]
   Example: "Do you have a team already, or are you solo?"
```

---

## Validation Process

**Step 1: Extract Keywords**
- Scan for project type keywords (booking, api, dashboard, etc.)
- Scan for action verbs (book, track, manage, etc.)
- Scan for scope indicators (MVP, budget, timeline)

**Step 2: Count Core Elements**
```python
has_project_type = detect_project_keywords(input)
has_core_action = detect_action_verbs(input)
has_scope_indicator = detect_scope_hints(input)

if not has_project_type or not has_core_action:
    return "RED - Too Vague"
elif has_project_type and has_core_action and has_scope_indicator:
    return "GREEN - Sufficient"
else:
    return "YELLOW - Borderline"
```

**Step 3: Decision**
- **Green:** Proceed to Feature Extraction (Task 02)
- **Yellow:** Ask 1-3 focused questions, THEN proceed
- **Red:** Educate + ask open questions, DO NOT proceed until clarified

---

## Pass Criteria

- ✅ **Green:** Project type + core action + scope indicator all present
- ✅ **Yellow:** Project type + core action present (ask for scope/details)

---

## Failure Conditions

- ❌ **Red:** Missing project type OR missing core action
- ❌ User says "just build something" with no specifics
- ❌ Only mentions technology ("I want to use React") without functionality

---

## Examples by Project Type

### Booking System
```
🟢 Sufficient: "Booking website for my yoga studio. Customers book classes, get email confirmation."
🟡 Borderline: "I need a booking system for my business." (what business? what gets booked?)
🔴 Too Vague: "I want appointment scheduling." (for what? who books? what features?)
```

### API Backend
```
🟢 Sufficient: "REST API for mobile app. Users authenticate, log workouts (exercises/reps), get weekly summary."
🟡 Borderline: "I need an API backend." (for what? which endpoints? which data?)
🔴 Too Vague: "Backend for my app." (what app? what functionality?)
```

### Mobile App
```
🟢 Sufficient: "Mobile app (iOS+Android) for tracking running. Users log distance/time, see progress charts."
🟡 Borderline: "Fitness tracking app." (mobile or web? track what exactly? other features?)
🔴 Too Vague: "Mobile app for health." (track what? who uses it? what's the core feature?)
```

---

## Error Message Template

```
GATE FAILED: Input Too Vague

Your input: "{user_input}"

Issue: Missing critical information to extract concrete features.

What's missing:
{missing_elements}

To proceed, please provide:
1. {question_1}
2. {question_2}
3. {question_3}

Example of sufficient input:
"{example_sufficient_input}"

Action: Please clarify the above, then we can proceed
```

**Example:**
```
GATE FAILED: Input Too Vague

Your input: "I want to build an app for my business."

Issue: Too generic - cannot determine project type or core functionality.

What's missing:
- ❌ What KIND of app? (booking, inventory, dashboard, etc.)
- ❌ What will users DO with it? (book appointments, track data, manage orders?)
- ❌ Who are the users? (customers, employees, yourself?)

To proceed, please provide:
1. What problem does this solve for your business?
2. What is the MAIN thing users will do?
3. Rough budget and timeline?

Example of sufficient input:
"Booking website for my yoga studio. Customers can see available classes,
book a slot, and get email confirmation. Budget €25k, need it in 6 weeks."

Action: Please clarify the above, then we can proceed
```

---

## Purpose

Prevents wasting time on inputs that are too vague to work with. Gets user to provide minimum viable context before starting feature extraction.

---

## Exemptions

- User explicitly in "brainstorming mode" (not ready for spec yet)
- User asks conceptual questions ("is this even possible?")
- User provides context incrementally through conversation (OK to ask follow-ups)
