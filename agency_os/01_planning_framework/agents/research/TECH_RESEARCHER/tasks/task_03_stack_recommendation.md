# Task 03: Stack Recommendation

**Task ID:** task_03_stack_recommendation
**Dependencies:** task_01, task_02
**Output:** stack_recommendation.json

---

## Objective

Recommend full technology stack based on project type, scale, and requirements.

---

## Instructions

### Step 1: Analyze Project Requirements
- Project type (CLI, Web App, Mobile App, API Service)
- Scale (Solo, Small Team, Production)
- Performance requirements
- Deployment target (serverless, containers, VPS)

### Step 2: Recommend Stack Components
- **Frontend:** Framework, build tool, styling
- **Backend:** Framework, language, runtime
- **Database:** Type (SQL/NoSQL), specific DB
- **Infrastructure:** Hosting, CDN, storage
- **DevOps:** CI/CD, monitoring, logging

### Step 3: Justify Recommendations
For each recommendation, explain:
- Why this choice for this project type
- Alignment with scale requirements
- Trade-offs made

---

## Output Format

```json
{
  "stack_recommendation": {
    "frontend": {
      "framework": "React + TypeScript",
      "build_tool": "Vite",
      "styling": "Tailwind CSS",
      "rationale": "React for large ecosystem, TypeScript for type safety, Vite for fast dev experience"
    },
    "backend": {
      "language": "TypeScript",
      "framework": "Express",
      "runtime": "Node.js 20 LTS",
      "rationale": "Single language stack (TS), mature ecosystem, good for API services"
    },
    "database": {
      "type": "SQL",
      "engine": "PostgreSQL 15",
      "orm": "Prisma",
      "rationale": "Relational data model, ACID compliance needed, Prisma for type-safe queries"
    },
    "infrastructure": {
      "hosting": "Vercel (frontend) + Railway (backend)",
      "storage": "AWS S3",
      "cdn": "Cloudflare",
      "rationale": "Vercel for easy Next.js deployment, Railway for Postgres + API, S3 for file storage"
    }
  },
  "alternatives_considered": [
    {
      "alternative": "Next.js full-stack",
      "why_not_chosen": "Serverless limitations for WebSocket features"
    }
  ]
}
```

---

## Next Task

Proceed to **Task 04: Constraint Identification**
