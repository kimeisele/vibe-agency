# Quick Start - Your First Project in 15 Minutes

**Version:** 1.0
**Goal:** Complete your first Vibe Agency planning session
**Time:** 15-20 minutes
**Project:** Simple Todo App (perfect for learning!)

---

## 🎯 What You'll Learn

By the end of this guide, you'll:
- ✅ Understand how Vibe Agency sessions work
- ✅ Complete all 6 planning phases
- ✅ Get a validated feature specification
- ✅ See scope negotiation in action
- ✅ Be ready to plan your own projects

---

## 📝 Prerequisites

### What You Need

1. **Access to Claude Code** (or Claude.ai)
2. **15-20 minutes** of focused time
3. **The vibe-agency repository** (you're already here!)

### Quick Setup

```bash
# Make sure you're in the vibe-agency directory
cd /path/to/vibe-agency

# Test that vibe_helper.py works
python3 -c "from vibe_helper import list_agents; print(list_agents())"

# Should output: dict of agents
```

---

## 🚀 Let's Start!

### Step 1: Tell Claude You Want to Plan a Project

**Say to Claude:**
```
I want to plan a software project using Vibe Agency.
Let's build a simple todo app to learn the system.
```

**Claude will load VIBE_ALIGNER and start Phase 1.**

---

### Step 2: Phase 1 - Choose Your Scope

**Claude will ask:**
```
Are we building:
📦 PROTOTYPE (days)
🚀 MVP (4-8 weeks)
✅ v1.0 (8-16 weeks)
```

**Your Answer:**
```
MVP - I want something minimal but functional
```

**Why MVP?**
- For learning, MVP scope is perfect
- Small enough to complete quickly (~15 min planning)
- Large enough to see all phases in action

---

### Step 3: Phase 2 - Describe Your Project

**Claude will ask about your project.**

**Your Answer:**
```
I want a simple todo app where users can:
- Add new tasks
- Mark tasks as complete
- Delete tasks
- See all their tasks in a list

It should be a web app, nothing fancy.
```

**What Happens:**
Claude will:
- Match to "simple_crud_learning" template
- Extract 4 core features
- Ask a few clarifying questions

---

### Step 4: Answer Claude's Questions

**Claude might ask:**

**Q1: "User accounts or guest mode?"**
```
Your Answer: Guest mode for MVP (no accounts needed)
```

**Q2: "Persist data or session-only?"**
```
Your Answer: Persist to browser localStorage (simple for MVP)
```

**Q3: "Any filtering/sorting?"**
```
Your Answer: Not for MVP. Just show all tasks.
```

**What's Happening:**
Claude is using **smart questioning rules** - only asking what can't be inferred.

Claude **won't ask:**
- "Should it handle errors?" (Yes, always)
- "Should tasks have text?" (Obviously yes)
- "Need a database?" (Inferred from "persist" answer)

---

### Step 5: Phase 3 - Feasibility Check

**Claude will validate:**
```
✅ Add task - FEASIBLE (simple CRUD)
✅ Complete task - FEASIBLE (state update)
✅ Delete task - FEASIBLE (array remove)
✅ List tasks - FEASIBLE (render array)
✅ localStorage - FEASIBLE (browser API)

All features feasible for MVP ✓
```

**No action needed - Claude just validating.**

---

### Step 6: Phase 4 - Gap Detection

**Claude will check dependencies:**
```
Feature: "Add task"
→ Depends on: "Task data structure" ✅
→ Depends on: "Form validation" ⚠️ Should we add?

Feature: "Persist data"
→ Depends on: "Browser localStorage API" ✅

Missing: Basic form validation (prevent empty tasks)
Should I add this? [Yes / No]
```

**Your Answer:**
```
Yes, add form validation
```

---

### Step 7: Phase 5 - Scope Negotiation

**Claude will calculate complexity:**
```
Feature Breakdown:
- Add task (with validation): 8 points
- Complete task: 5 points
- Delete task: 5 points
- List tasks: 5 points
- localStorage persistence: 8 points

Total: 31 points

Timeline Estimate:
- 1 developer: 2-3 days
- Learning project (you): 1 week (with tutorial)

Cost Estimate:
- Self-build: €0
- Freelancer: €400-600
- Agency: €1,500-2,000

Since this is a learning project, I assume you're building it yourself?
```

**Your Answer:**
```
Yes, I'll build it myself as a learning project
```

**Claude:**
```
Perfect! This is an excellent learning project.

Complexity: 31 points (low)
Timeline: 3-5 days (part-time)
Difficulty: Beginner-friendly

Status: ✅ GREEN (Perfect for learning!)
```

---

### Step 8: Phase 6 - Get Your Specification

**Claude will generate:**
```json
{
  "project_id": "todo_app_mvp",
  "scope": "MVP",
  "type": "Learning Project",
  "timeline": "3-5 days",
  "complexity": 31,
  "status": "GREEN",

  "features": [
    {
      "id": "add_task",
      "name": "Add New Task",
      "description": "User enters task text, clicks Add, task appears in list",
      "complexity": 8,
      "input": "Text input field",
      "output": "Task added to list",
      "validation": "Prevent empty tasks"
    },
    {
      "id": "complete_task",
      "name": "Mark Task Complete",
      "description": "User clicks checkbox, task marked as done (strikethrough)",
      "complexity": 5
    },
    {
      "id": "delete_task",
      "name": "Delete Task",
      "description": "User clicks delete icon, task removed from list",
      "complexity": 5
    },
    {
      "id": "list_tasks",
      "name": "Display All Tasks",
      "description": "Show all tasks with complete/delete actions",
      "complexity": 5
    },
    {
      "id": "persist_tasks",
      "name": "Persist to localStorage",
      "description": "Save tasks to browser, load on page refresh",
      "complexity": 8
    }
  ],

  "tech_stack": {
    "framework": "React (or Vanilla JS)",
    "styling": "CSS (or Tailwind)",
    "storage": "localStorage",
    "hosting": "GitHub Pages (free)"
  },

  "learning_path": [
    "Week 1: Build core features (add/complete/delete)",
    "Week 2: Add localStorage persistence",
    "Week 3: Polish UI, deploy to GitHub Pages",
    "Future: Add user accounts (v1.1)"
  ]
}
```

**Claude will save this as `feature_spec.json`**

---

## ✅ Congratulations!

**You just completed your first Vibe Agency planning session!**

### What You Achieved

✅ **Learned the 6-phase process**
✅ **Saw smart questioning** (only 3 questions asked)
✅ **Witnessed validation** (feasibility check)
✅ **Experienced scope negotiation** (complexity → timeline)
✅ **Got a structured specification**

### Time Taken

- **Phase 1 (Education):** 2 minutes
- **Phase 2 (Feature Extraction):** 5 minutes
- **Phase 3 (Validation):** 1 minute
- **Phase 4 (Gap Detection):** 3 minutes
- **Phase 5 (Scope Negotiation):** 3 minutes
- **Phase 6 (Output):** 1 minute

**Total:** ~15 minutes

---

## 🎓 What You Learned

### Key Concepts

1. **Education Phase Sets Expectations**
   - MVP vs v1.0 matters
   - Scope must match reality
   - Tradeoffs are inevitable

2. **Smart Questioning Saves Time**
   - Claude asked ~3 questions
   - Generic AI would ask 10-15
   - Templates + inference rules = efficiency

3. **Validation Catches Issues Early**
   - "Add ML recommendations" → Too complex
   - Better to know upfront than mid-project

4. **Dependencies Matter**
   - "Persist data" → Need storage mechanism
   - Better Claude detects than you forget

5. **Complexity Drives Timeline**
   - 31 points = 2-3 days
   - Not guesswork - calculated from 1,303 rules

---

## 🚀 Next Steps

### Option 1: Build This Todo App

**Use the spec you just created!**

Follow the learning path:
1. Set up React (or Vanilla JS)
2. Build add/complete/delete
3. Add localStorage
4. Deploy to GitHub Pages

**Resources:**
- React: https://react.dev/learn
- localStorage: https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage
- GitHub Pages: https://pages.github.com/

---

### Option 2: Plan Your Real Project

**Now that you've learned the process, plan something real!**

**Say to Claude:**
```
I want to plan a project using Vibe Agency.

It's a [describe your project]...
```

**Claude will:**
- Start Phase 1 (Education)
- Guide you through all phases
- Apply the same process to your project

**Example Projects to Try:**
- Booking system for your business
- Portfolio website with CMS
- Internal tool for your team
- Chrome extension for productivity
- API for your mobile app

---

### Option 3: Continue to Architecture Design

**Want to see the next phase?**

**Say to Claude:**
```
Continue from the todo app spec.
Let's do architecture design with GENESIS_BLUEPRINT.
```

**Claude will:**
- Switch to GENESIS_BLUEPRINT agent
- Design technical architecture
- Select core modules
- Generate directory structure
- Output architecture.json

**This shows the complete Planning → Architecture workflow.**

---

## 📚 Dive Deeper

### Read the Full Guides

Now that you've done it once, read the detailed guides:

1. **USER_EXPERIENCE_GUIDE.md** - What happens in each phase
2. **SESSION_EXAMPLES.md** - Real project transcripts
3. **CLAUDE_SESSION_GUIDE.md** - Technical details (for Claude)
4. **HOW_CLAUDE_USES_VIBE.md** - System architecture

### Try Different Project Types

**Vibe Agency has 18 project templates:**

**Simple (Good for Learning):**
- Todo app (what you just did!)
- Portfolio website
- Blog with CMS
- URL shortener

**Medium:**
- Booking system
- E-commerce store
- SaaS dashboard
- REST API

**Complex:**
- Marketplace
- Real-time chat
- AI-powered tool
- Multi-tenant SaaS

Try planning each - see how complexity changes!

---

## 💡 Pro Tips

### For Your Next Session

**✅ DO:**
- Be specific about your core problem
- Have timeline/budget in mind
- Trust the complexity estimates
- Ask "why" if you don't understand
- Accept scope negotiation

**❌ DON'T:**
- List 50 features upfront
- Say "I want everything"
- Ignore feasibility warnings
- Skip education phase
- Refuse to cut scope

### Common Mistakes (and How to Avoid)

**Mistake #1: "I want it like [Big Company Product]"**
→ Be specific: Which features exactly?

**Mistake #2: "Can we do it in 2 weeks?"**
→ Let Claude calculate first, then negotiate

**Mistake #3: "This is too expensive"**
→ Ask: "What can we cut to hit [budget]?"

**Mistake #4: "Let's add [feature] later"**
→ Add now or plan for v1.1 - don't assume "easy"

---

## 🎯 Success Metrics

### You're Ready When...

✅ You can complete a planning session in 20-30 minutes
✅ You understand scope vs timeline tradeoffs
✅ You trust complexity estimates (not just gut feeling)
✅ You can identify must-have vs nice-to-have features
✅ You accept that some features should wait for v1.1

---

## 🆘 Troubleshooting

### "Claude isn't following the phases"

**Make sure you say:**
```
"Plan a project using Vibe Agency"
```

This triggers Claude to load the VIBE_ALIGNER framework.

---

### "Too many questions being asked"

**This shouldn't happen!** Vibe Agency uses smart questioning.

If Claude asks obvious things, say:
```
"Use inference rules - only ask what's genuinely ambiguous"
```

---

### "I want to skip Phase X"

**Don't skip phases!** Each builds on the previous:
- Phase 1 → Sets scope expectations
- Phase 2 → Extracts features (needs scope from Phase 1)
- Phase 3 → Validates features (needs list from Phase 2)
- etc.

Skipping = incomplete spec

---

### "Complexity estimate seems high/low"

**Ask Claude for breakdown:**
```
"Can you show me which features are most complex?"
```

Claude will break down points per feature.

---

## 🎉 You're Ready!

**You've completed the quick start!**

You now know:
- ✅ How Vibe Agency sessions work
- ✅ The 6-phase planning process
- ✅ How to get a validated specification
- ✅ How to use it for real projects

**Go plan something awesome! 🚀**

---

## 📞 Need Help?

- **Documentation:** See README.md
- **Examples:** See SESSION_EXAMPLES.md
- **Details:** See USER_EXPERIENCE_GUIDE.md
- **Issues:** File at GitHub Issues
- **Community:** GitHub Discussions

---

**Version:** 1.0
**Status:** Complete
**Next:** Plan your own project or explore SESSION_EXAMPLES.md
