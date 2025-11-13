# Validation Gate: Dependency Availability

## Rule
All required libraries, APIs, and services must be actively maintained, publicly available, and not deprecated.

---

## Validation Checks

### 1. Library/Package Status
- ✅ Last updated within 12 months
- ✅ Active maintainer(s) responding to issues
- ✅ Compatible with current language/framework version
- ❌ Deprecated or archived
- ❌ Last commit > 2 years ago (with no activity)
- ❌ Major security vulnerabilities with no fix

### 2. Third-Party API Availability
- ✅ API publicly available (or user has access)
- ✅ API documentation exists and is current
- ✅ Pricing acceptable for user's budget
- ❌ API deprecated (sunset date announced)
- ❌ API requires enterprise plan (user can't afford)
- ❌ API region-locked (not available in user's country)

### 3. Service/Platform Status
- ✅ Service in active development
- ✅ No announced shutdown plans
- ✅ Service matches project requirements (e.g., free tier limits)
- ❌ Service shutting down within 12 months
- ❌ Free tier too restrictive (user will hit limits immediately)
- ❌ Service has recent history of outages/instability

### 4. License Compatibility
- ✅ License allows commercial use (if applicable)
- ✅ No viral licenses that conflict with user's use case
- ❌ GPL library in closed-source project (license conflict)
- ❌ License requires attribution user cannot provide

---

## Red Flags

### 🚨 Critical Issues (Block Project)

1. **Deprecated/Sunset APIs**
   - Example: Heroku free tier shut down (2022)
   - Example: Twitter API v1.1 deprecated (2023)
   - Action: Find alternative or delay project

2. **Unmaintained Critical Dependency**
   - Example: Using `node-sass` (deprecated, use `sass` instead)
   - Example: Using `moment.js` (use `date-fns` or `dayjs` instead)
   - Action: Choose maintained alternative

3. **Security Vulnerabilities**
   - Library has known CVE with no fix
   - Action: Choose secure alternative or wait for fix

4. **Region/Legal Restrictions**
   - Stripe not available in user's country
   - Action: Find alternative payment processor (Razorpay, Paystack, etc.)

### ⚠️ Warning (Proceed with Caution)

1. **Low Activity (but not dead)**
   - Library works but infrequent updates
   - Action: Test thoroughly, have backup plan

2. **Beta/Alpha Services**
   - Service in beta (e.g., Supabase Realtime)
   - Action: Acceptable for MVP, plan migration if needed

3. **Free Tier Limits**
   - Will hit limits within first month
   - Action: Budget for paid tier

---

## Common Deprecated Dependencies to Avoid

### Frontend
- ❌ `moment.js` → Use `date-fns`, `dayjs`, or native `Intl`
- ❌ `node-sass` → Use `sass` (Dart Sass)
- ❌ `create-react-app` → Use `Vite`, `Next.js`, or `Remix`
- ❌ `Backbone.js`, `Knockout.js`, `Meteor.js` → Use modern frameworks

### Backend
- ❌ `request` (Node.js) → Use `axios`, `got`, or `node-fetch`
- ❌ `body-parser` (Express) → Built into Express 4.16+
- ❌ Python 2.x → Use Python 3.9+
- ❌ `passport-local` (unmaintained) → Consider alternatives or fork

### Databases
- ❌ MongoDB < 4.0 → Use 5.0+ (better transactions)
- ❌ MySQL 5.x → Use MySQL 8.0 or PostgreSQL
- ❌ Redis < 6.0 → Use Redis 7.0+ (better security, ACL)

### Services
- ❌ Heroku free tier (shut down 2022) → Use Railway, Fly.io, Render
- ❌ Parse Server (revived but risky) → Use Firebase, Supabase
- ❌ Twitter API v1.1 → Use v2

---

## Validation Process

1. **Check library status:**
   - Visit npm/PyPI/RubyGems
   - Check last publish date
   - Check GitHub (if open source): last commit, open issues, maintainer activity

2. **Check API availability:**
   - Visit API docs
   - Check pricing page (is it accessible?)
   - Check status page (is it stable?)
   - Search for "API_NAME shutting down" or "deprecated"

3. **Check service health:**
   - Visit service website
   - Check service status page
   - Search for recent outages or issues
   - Check if free tier meets needs

4. **Check licenses:**
   - Ensure commercial use allowed (if applicable)
   - Avoid GPL if building closed-source product

---

## Pass Criteria

- ✅ All libraries published within last 12 months
- ✅ No deprecated/archived dependencies
- ✅ All APIs publicly accessible (or user has credentials)
- ✅ Services stable and not shutting down
- ✅ Free tiers sufficient for initial launch (or budget allocated)
- ✅ All licenses compatible with user's use case

---

## Failure Conditions

- ❌ Any critical dependency deprecated with no alternative
- ❌ Required API shutting down within 6 months
- ❌ Service unavailable in user's region (and no VPN workaround)
- ❌ License conflict (e.g., GPL in closed-source project)
- ❌ Free tier too restrictive + no budget for paid tier
- ❌ Library has critical security vulnerability with no fix

---

## Error Message Template

```
GATE FAILED: Dependency Unavailable or Deprecated

Issue: {dependency_name} - {issue_description}

Details:
- Type: {library|api|service}
- Status: {deprecated|unmaintained|shutting_down|unavailable}
- Last updated: {date}
- Impact: {critical|high|medium}

Why this is a problem:
{explanation}

Recommended alternatives:
1. {alternative_1} (most similar)
2. {alternative_2} (better maintained)
3. {alternative_3} (different approach)

Action: Replace {dependency_name} with a maintained alternative
```

**Example 1: Deprecated Library**
```
GATE FAILED: Dependency Unavailable or Deprecated

Issue: moment.js - Project is deprecated since September 2020

Details:
- Type: library (date manipulation)
- Status: deprecated (no new features, security fixes only)
- Last updated: 2022-12-01 (final version)
- Impact: medium (works but discouraged)

Why this is a problem:
Moment.js maintainers recommend using modern alternatives.
The library is large (67KB min+gzip) and has design limitations.
No new features will be added.

Recommended alternatives:
1. date-fns (most similar, tree-shakeable, 2KB per function)
2. dayjs (smallest, 2KB, moment-like API)
3. Native Intl (built-in, zero dependencies)

Action: Replace moment.js with date-fns or dayjs
```

**Example 2: Unavailable API**
```
GATE FAILED: Dependency Unavailable or Deprecated

Issue: Stripe - Not available in your country (Bangladesh)

Details:
- Type: API (payment processing)
- Status: region-locked (not available in BD)
- Last updated: N/A
- Impact: critical (blocks payment feature)

Why this is a problem:
Stripe does not support merchant accounts in Bangladesh.
You cannot receive payments via Stripe.

Recommended alternatives:
1. Razorpay (supports India, Bangladesh, Malaysia)
2. Paystack (supports Africa, expanding globally)
3. bKash/Nagad (local Bangladesh payment gateways)
4. PayPal (if business account available)

Action: Choose payment gateway available in Bangladesh
```

---

## Purpose

Prevents building on deprecated or unavailable dependencies. Ensures project can be deployed and maintained long-term.

---

## Exemptions

- User accepts risk of using deprecated library (has migration plan)
- Beta service acceptable for MVP (not production-critical)
- License issue resolved (e.g., dual-licensed, commercial license purchased)
