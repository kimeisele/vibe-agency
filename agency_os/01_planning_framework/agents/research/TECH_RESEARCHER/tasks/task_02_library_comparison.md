# Task 02: Library Comparison

**Task ID:** task_02_library_comparison
**Dependencies:** task_01_api_evaluation
**Output:** library_comparison.json

---

## Objective

Compare libraries and frameworks needed for core functionality. Verify maintenance status, licensing, and ecosystem fit.

---

## Instructions

### Step 1: Identify Required Libraries
Based on features and tech stack:
- Frontend framework (React, Vue, Svelte, etc.)
- Backend framework (Express, FastAPI, Rails, etc.)
- Database ORM (Prisma, TypeORM, SQLAlchemy, etc.)
- Testing libraries
- Utility libraries

### Step 2: Research Each Library
For each library, gather:
- **GitHub URL**
- **License** (MIT, Apache, GPL, proprietary)
- **Maintenance status** (last commit date, active issues, release cadence)
- **GitHub stars** (popularity indicator)
- **npm/PyPI downloads** (usage indicator)
- **Documentation quality**
- **Breaking changes history** (stability indicator)

### Step 3: Compare Alternatives
For each category, compare 2-3 alternatives on:
- Maintenance status
- Learning curve
- Performance
- Community support
- Bundle size (for frontend)

---

## Output Format

```json
{
  "libraries_by_category": {
    "frontend_framework": [
      {
        "name": "React",
        "purpose": "UI framework",
        "license": "MIT",
        "maintenance_status": "Active - last commit 2025-11-10, weekly releases",
        "github_stars": 220000,
        "github_url": "https://github.com/facebook/react",
        "npm_downloads_monthly": 20000000,
        "documentation_quality": "excellent",
        "pros": ["Large ecosystem", "Wide adoption", "Strong typing with TypeScript"],
        "cons": ["Larger bundle size", "Steeper learning curve"]
      }
    ]
  },
  "recommended_libraries": [
    {
      "name": "React",
      "purpose": "Frontend UI framework",
      "license": "MIT",
      "maintenance_status": "Active - last commit 2025-11-10",
      "github_stars": 220000,
      "source": "https://github.com/facebook/react",
      "selection_rationale": "Most popular, excellent TypeScript support, large ecosystem"
    }
  ]
}
```

---

## Maintenance Status Check

✅ **Active:** Last commit < 30 days, regular releases
⚠️ **Moderate:** Last commit 30-90 days, occasional releases
❌ **Inactive:** Last commit > 90 days, no recent releases

---

## Next Task

Proceed to **Task 03: Stack Recommendation**
