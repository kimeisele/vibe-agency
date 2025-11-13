# Validation Gate: Tech Stack Coherence

## Rule
All chosen technologies must work well together, without known conflicts or antipatterns.

---

## Coherence Rules

### 1. Language Consistency
- ✅ Frontend and backend in same language (e.g., Next.js + Node.js)
- ✅ OR clear separation with API boundary (e.g., React + Django via REST)
- ❌ Mixing languages unnecessarily (e.g., Node.js backend + random Go microservice for no reason)

### 2. Database-ORM Compatibility
- ✅ ORM officially supports chosen database (e.g., Prisma + PostgreSQL)
- ❌ Using SQL ORM with MongoDB (use ODM like Mongoose instead)
- ❌ Using old ORM version incompatible with DB version

### 3. Framework-Hosting Compatibility
- ✅ Vercel + Next.js (optimized)
- ✅ Railway + Django/FastAPI/Express (standard)
- ❌ Vercel Serverless + WebSocket (doesn't work, need persistent connections)
- ❌ Next.js Server Components on AWS Lambda (cold start issues)

### 4. Authentication-Framework Compatibility
- ✅ NextAuth.js + Next.js (native integration)
- ✅ Django Auth + Django (built-in)
- ❌ Using Passport.js with Next.js (better options exist)

### 5. Real-Time Stack Compatibility
- ✅ Socket.io + Redis + Sticky Sessions (for horizontal scaling)
- ❌ Socket.io without Redis on multiple servers (breaks)
- ❌ WebSocket on serverless (doesn't work)

---

## Common Antipatterns

### ❌ Antipattern 1: Over-Engineering
```
BAD: Using Kubernetes + Microservices for a 3-feature MVP
GOOD: Single Next.js app on Vercel
```

### ❌ Antipattern 2: Mixing Too Many Languages
```
BAD: Node.js backend + Python ML service + Go API gateway (for no reason)
GOOD: Python for everything (FastAPI + ML libraries)
```

### ❌ Antipattern 3: Deprecated/Unmaintained Libraries
```
BAD: Using Meteor.js in 2025 (dead ecosystem)
GOOD: Using Next.js or Remix (active, modern)
```

### ❌ Antipattern 4: Wrong Database Type
```
BAD: Using MongoDB for highly relational data (users, orders, products)
GOOD: Using PostgreSQL (supports JSON if needed)
```

### ❌ Antipattern 5: Wrong Hosting for Workload
```
BAD: Using Vercel Serverless for long-running background jobs
GOOD: Using Railway or Fly.io (persistent servers)
```

---

## Validation Process

1. Check framework + hosting compatibility
2. Check ORM + database compatibility
3. Check language consistency (frontend vs. backend)
4. Check for deprecated/unmaintained libraries
5. Check for known conflicts (e.g., WebSocket + Serverless)
6. Check team expertise matches chosen stack

---

## Pass Criteria

- ✅ All components officially support each other
- ✅ No deprecated/unmaintained libraries
- ✅ Hosting supports chosen framework's features
- ✅ ORM compatible with database
- ✅ Tech stack matches team expertise
- ✅ No over-engineering for project size

---

## Failure Conditions

- ❌ Critical incompatibility (e.g., Vercel + WebSocket server)
- ❌ Using deprecated framework (e.g., Meteor, Backbone.js)
- ❌ ORM doesn't support chosen database
- ❌ Hosting can't run chosen runtime (e.g., Deno on Heroku)
- ❌ Over-engineering (Kubernetes for simple CRUD app)
- ❌ Team has no expertise in chosen stack (and no time to learn)

---

## Compatibility Matrix

### ✅ Well-Known Good Combinations

**Web Full-Stack:**
- Next.js + Prisma + PostgreSQL + Vercel ✅
- Django + PostgreSQL + Railway ✅
- Rails + PostgreSQL + Heroku ✅
- FastAPI + SQLAlchemy + PostgreSQL + Railway ✅
- Express + Prisma + PostgreSQL + Fly.io ✅

**Mobile:**
- React Native + Expo + Firebase ✅
- React Native + Expo + REST API (any backend) ✅
- Flutter + Firebase ✅
- Flutter + Supabase ✅

**Real-Time:**
- Next.js + Socket.io + Redis + Railway ✅
- Next.js + Yjs + WebSocket + Railway ✅
- Express + Socket.io + Redis + Fly.io ✅

**API Only:**
- FastAPI + PostgreSQL + Docker + Railway ✅
- Express + TypeScript + Prisma + Fly.io ✅
- NestJS + TypeORM + PostgreSQL + AWS ✅

### ❌ Known Bad Combinations

- Next.js Server Components + Vercel Serverless + Long-running tasks ❌
- Socket.io + Multiple servers + No Redis ❌
- Prisma + MongoDB + Complex relational queries ❌
- Vercel Serverless + WebSocket server ❌
- Django + Vercel ❌ (use Railway/Fly.io instead)
- React Native + bare React Native + complex native modules + no Mac ❌

---

## Error Message Template

```
GATE FAILED: Tech Stack Incompatibility

Incompatibility detected: {incompatibility_description}

Your chosen stack:
- Frontend: {frontend}
- Backend: {backend}
- Database: {database}
- ORM: {orm}
- Hosting: {hosting}
- Auth: {auth}

Issue: {specific_issue}

Why this doesn't work:
{explanation}

Recommended alternatives:
1. {option_1}
2. {option_2}
3. {option_3}

Action: Choose a compatible tech stack
```

**Example:**
```
GATE FAILED: Tech Stack Incompatibility

Incompatibility detected: Vercel Serverless + Socket.io WebSocket Server

Your chosen stack:
- Frontend: Next.js
- Backend: Next.js API Routes
- Real-time: Socket.io
- Hosting: Vercel

Issue: Vercel Serverless functions cannot maintain persistent WebSocket connections

Why this doesn't work:
Serverless functions are stateless and short-lived (max 10s on Vercel).
WebSocket connections need persistent, long-running servers.
Socket.io requires a server that stays alive to maintain client connections.

Recommended alternatives:
1. Use Vercel + Pusher/Ably (managed WebSocket service) ✅
2. Deploy Socket.io server separately on Railway/Fly.io ✅
3. Switch hosting to Railway (supports WebSocket) ✅
4. Use Vercel + Server-Sent Events (SSE) instead of WebSocket

Action: Choose a compatible hosting + real-time solution
```

---

## Purpose

Prevents project failure from incompatible technologies. Ensures smooth integration and deployment.

---

## Exemptions

- User has proven experience making "unusual" combinations work
- User explicitly accepts risk of non-standard stack
- There's a documented, working example of this combination
