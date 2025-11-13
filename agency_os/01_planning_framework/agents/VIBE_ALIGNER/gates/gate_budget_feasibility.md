# Validation Gate: Budget Feasibility

## Rule
Estimated project costs must not exceed available budget (or user must acknowledge budget increase).

---

## Cost Components

### 1. Development Labor
```
dev_cost = (estimated_weeks * team_size * hourly_rate * hours_per_week)
```
- Junior dev: $25-45/hr
- Mid-level dev: $50-85/hr
- Senior dev: $80-180/hr
- Agency rate: $100-250/hr (blended)

### 2. Infrastructure (Monthly)
```
infrastructure_cost = hosting + database + storage + third_party_apis
```

**Typical Ranges:**
- **Low:** $20-100/month (Vercel free tier, small database)
- **Medium:** $100-500/month (Production-grade, scaling)
- **High:** $500-2000+/month (High traffic, complex infrastructure)

**First 6 months:** `infrastructure_cost * 6`

### 3. Third-Party Services (Setup + Monthly)

**Common Services:**
- Stripe (payments): $0 setup, ~2.9% transaction fees
- SendGrid (email): $0-$15/month (up to 40k emails)
- Cloudflare (CDN): $0-$20/month
- Auth0 (authentication): $0-$240/month (up to 7k users)
- Supabase (backend): $0-$25/month
- Firebase: $0-$50/month (Blaze plan)
- Algolia (search): $0-$1/month (up to 10k searches)

**Estimate:** $0-500 setup + $50-500/month

### 4. Buffer (Contingency)
```
buffer = (dev_cost + infrastructure_cost + services_cost) * 0.15-0.25
```

**15-25% buffer for:**
- Scope changes
- Bug fixes post-launch
- Unexpected complications
- Learning curve with new tech

---

## Validation Process

1. Calculate `dev_cost` from timeline * team size * rate
2. Estimate `infrastructure_cost` for first 6 months
3. Calculate `third_party_costs` based on required services
4. Add 20% buffer
5. Compare `total_estimated_cost` against `user_budget`

---

## Pass Criteria

- ✅ **Green:** `user_budget` ≥ 120% of estimated cost (comfortable, room for expansion)
- ✅ **Yellow:** `user_budget` = 85-120% of estimated cost (tight but workable, scope must be locked)
- ✅ User has contingency funds or can adjust scope
- ✅ Infrastructure costs sustainable for 6+ months

---

## Failure Conditions

- ❌ **Red:** `user_budget` < 85% of estimated cost (insufficient - cannot deliver full scope)
- ❌ Infrastructure cost > 30% of monthly revenue (unsustainable)
- ❌ No budget allocated for infrastructure/services (only dev time)
- ❌ User expects "free" hosting for production app (unrealistic)

**Note:** Yellow (85-120%) is a PASS with warnings, not a failure. Educate user on tight budget risks but don't block project.

---

## Budget Estimation Examples

**Example 1: Small SaaS MVP**
```
Project: Simple booking system
Timeline: 6 weeks
Team: 1 mid-level dev @ $70/hr, 40hr/week

Development:
  6 weeks * 40 hrs * $70/hr = $16,800

Infrastructure (first 6 months):
  Vercel Pro: $20/mo * 6 = $120
  Supabase Pro: $25/mo * 6 = $150
  SendGrid: $15/mo * 6 = $90
  Total: $360

Services:
  Stripe: $0 setup, transaction-based
  Domain: $15/year
  Total: $15

Buffer (20%):
  ($16,800 + $360 + $15) * 0.20 = $3,435

TOTAL ESTIMATE: $20,610

Recommended budget: $22,000-25,000
```

**Example 2: Mobile App with Backend**
```
Project: React Native + API backend
Timeline: 10 weeks
Team: 1 senior dev @ $120/hr, 40hr/week

Development:
  10 weeks * 40 hrs * $120/hr = $48,000

Infrastructure (first 6 months):
  Railway (backend): $30/mo * 6 = $180 (small app; can range $20-50/mo)
  PostgreSQL: $30/mo * 6 = $180
  Firebase (push): $20/mo * 6 = $120
  S3 storage: $10/mo * 6 = $60
  Total: $540

Services:
  Apple Developer: $99/year
  Google Play: $25 one-time
  Expo EAS: $19/mo * 3 months (builds) = $57
  Total: $181

Buffer (20%):
  ($48,000 + $540 + $181) * 0.20 = $9,744

TOTAL ESTIMATE: $58,465

Recommended budget: $60,000-65,000
```

---

## Warning Levels

### 🟢 Green (Sufficient Budget)
- Budget ≥ 120% of estimate
- Room for scope expansion or complications

### 🟡 Yellow (Tight Budget)
- Budget = 85-120% of estimate
- Little margin for error, scope must be locked

### 🔴 Red (Insufficient Budget)
- Budget < 85% of estimate
- Cannot deliver full scope without cutting features or quality

---

## Error Message Template

```
GATE FAILED: Budget Insufficient

Your budget: ${user_budget}
Estimated cost: ${total_estimated_cost}
Shortfall: ${shortfall} ({percentage}% under)

Cost Breakdown:
- Development labor: ${dev_cost} ({weeks} weeks * {team_size} devs * ${rate}/hr)
- Infrastructure (6 months): ${infrastructure_cost}
- Third-party services: ${services_cost}
- Buffer (20%): ${buffer}
- TOTAL: ${total_estimated_cost}

⚠️ With the current budget, you can afford:
- {affordable_weeks} weeks of development, OR
- {reduced_complexity} complexity points (down from {total_complexity})

Options:
1. Increase budget to ${recommended_budget} (recommended)
2. Reduce scope by {features_to_cut} features
3. Choose lower-cost tech stack (reduce infrastructure)
4. DIY certain features (e.g., skip Stripe, handle payments manually)
5. Phase the project (build v1.0 now, add features later with additional budget)

Action: Adjust budget or reduce scope
```

---

## Purpose

Prevents projects from running out of money mid-development. Ensures sustainable infrastructure costs.

---

## Common Budget Mistakes

1. **Forgetting infrastructure:** "I budgeted for dev time, but not hosting"
2. **Underestimating third-party costs:** "I didn't know Stripe takes 3% per transaction"
3. **No buffer:** "The estimate was exact, but we had complications"
4. **Post-launch costs:** "Who pays for servers after launch?"
5. **Maintenance not budgeted:** "We need bug fixes but budget is spent"

---

## Recommendations

- Always include 20-25% buffer
- Plan for 6 months of infrastructure costs upfront
- Consider monthly costs, not just development
- For SaaS: Infrastructure should be <30% of projected MRR
- For agencies: Budget at least 10-15% for client revisions
