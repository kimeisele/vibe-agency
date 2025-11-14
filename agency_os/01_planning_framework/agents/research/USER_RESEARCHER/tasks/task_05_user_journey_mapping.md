# Task 05: User Journey Mapping

**Task ID:** task_05_user_journey_mapping
**Dependencies:** task_01, task_02
**Input:** personas.json, pain_points.json
**Output:** user_journeys.json

---

## Objective

Generate 5-stage user journey map template for each primary persona.

---

## Instructions

### Step 1: Define Journey Stages
Standard 5-stage journey:

1. **Awareness:** User realizes they have a problem
2. **Consideration:** User researches solutions
3. **Decision:** User evaluates and selects product
4. **Onboarding:** User starts using product
5. **Retention:** User continues using product (or churns)

### Step 2: For Each Stage, Document:
- **Touchpoints:** Where user interacts with product/brand
- **Actions:** What user does
- **Emotions:** How user feels (frustrated, curious, confident, etc.)
- **Pain points:** What goes wrong
- **Opportunities:** Where to improve experience

### Step 3: Customize for Each Persona
- Journey varies by persona (B2B vs consumer, etc.)
- B2B journeys longer, involve multiple stakeholders
- Consumer journeys faster, more emotional

---

## Output Format

```json
{
  "user_journeys": [
    {
      "persona": "Marketing Mary",
      "journey": [
        {
          "stage": "Awareness",
          "touchpoints": ["Google search", "LinkedIn ads", "Peer recommendations"],
          "actions": [
            "Searches for 'marketing automation tools'",
            "Reads comparison articles",
            "Asks colleagues for recommendations"
          ],
          "emotions": "Frustrated with current tools, curious about alternatives",
          "pain_points": [
            "Too many options, overwhelming",
            "Hard to tell which tools are credible"
          ],
          "opportunities": [
            "Clear positioning/differentiation",
            "Educational content (not just sales pitch)",
            "Comparison charts with honest pros/cons"
          ]
        },
        {
          "stage": "Consideration",
          "touchpoints": ["Product website", "Demo videos", "Reviews (G2, Capterra)"],
          "actions": [
            "Watches demo video",
            "Reads reviews",
            "Compares pricing",
            "Signs up for free trial"
          ],
          "emotions": "Cautiously optimistic, skeptical of marketing claims",
          "pain_points": [
            "Hard to evaluate without trying",
            "Unclear which plan to choose",
            "Worried about integration complexity"
          ],
          "opportunities": [
            "Easy trial signup (no credit card)",
            "Clear pricing with calculator",
            "Integration documentation upfront"
          ]
        },
        {
          "stage": "Decision",
          "touchpoints": ["Free trial", "Customer support chat", "Pricing page"],
          "actions": [
            "Tests key features",
            "Evaluates integration with existing tools",
            "Calculates ROI",
            "Gets approval from manager"
          ],
          "emotions": "Excited if trial goes well, anxious about making wrong choice",
          "pain_points": [
            "Need to justify purchase to manager",
            "Unclear if trial data will migrate",
            "Worried about lock-in"
          ],
          "opportunities": [
            "ROI calculator",
            "Case studies with similar companies",
            "Easy migration path from trial to paid"
          ]
        },
        {
          "stage": "Onboarding",
          "touchpoints": ["Setup wizard", "Onboarding emails", "Help documentation"],
          "actions": [
            "Connects integrations",
            "Imports data",
            "Configures workflows",
            "Invites team members"
          ],
          "emotions": "Hopeful but impatient, wants quick wins",
          "pain_points": [
            "Overwhelming number of settings",
            "Data import issues",
            "Team members don't adopt"
          ],
          "opportunities": [
            "Guided setup wizard",
            "Quick win campaigns (template library)",
            "Team training resources"
          ]
        },
        {
          "stage": "Retention",
          "touchpoints": ["Daily product usage", "Email notifications", "Customer success check-ins"],
          "actions": [
            "Uses product for daily workflows",
            "Monitors analytics",
            "Troubleshoots issues",
            "Considers upgrading plan"
          ],
          "emotions": "Satisfied if product works well, frustrated if bugs/issues",
          "pain_points": [
            "Feature requests not prioritized",
            "Bugs slow down work",
            "Outgrows current plan but upgrade expensive"
          ],
          "opportunities": [
            "Proactive customer success outreach",
            "Feature roadmap transparency",
            "Flexible upgrade paths"
          ]
        }
      ]
    }
  ]
}
```

---

## Next Task

Proceed to **Task 06: Output Generation**
