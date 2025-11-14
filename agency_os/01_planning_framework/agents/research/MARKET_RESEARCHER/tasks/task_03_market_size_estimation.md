# Task 03: Market Size Estimation

**Task ID:** task_03_market_size_estimation
**Dependencies:** task_01_competitor_identification
**Output:** market_size_estimate.json

---

## Objective

Estimate the market size using TAM/SAM/SOM methodology with verifiable sources and clear calculations.

---

## Instructions

### Step 1: Determine Market Category
Based on user vision and competitors, identify the specific market:
- Industry category (e.g., "Project Management Software")
- Market segment (e.g., "Cloud-based PM for SMBs")

### Step 2: Calculate TAM (Total Addressable Market)

**RECOMMENDED: Use bottom-up calculation (FREE!)**
```
TAM = Total potential customers × Average revenue per customer (ARPU)
```

**FREE data sources to use:**
1. **Google Search** (100 searches/day free)
   - Search: "number of [target customers] worldwide"
   - Example: "number of freelancers worldwide" → 100M
2. **Crunchbase free tier** - Similar companies, funding data
3. **Y Combinator directory** - Startup market segments
4. **ProductHunt** - Emerging markets, product categories
5. **Government statistics** - Industry data (free)
6. **Reddit/Stack Overflow** - Community size, adoption trends

**AVOID expensive sources** (unless user explicitly has access):
- ❌ Gartner ($15,000-30,000/year) - unrealistic for individuals
- ❌ Statista ($39-199/month) - too expensive for most
- ❌ IBISWorld ($1,500+/report) - not cost-effective

**Required:** Show your calculation method OR cite a credible free source

### Step 3: Calculate SAM (Serviceable Addressable Market)
From TAM, narrow down to your specific segment:
- Geographic focus (if applicable)
- Customer type (enterprise, SMB, individual)
- Specific use case or vertical

**Formula:** SAM = TAM × % of market segment you're targeting

### Step 4: Estimate SOM (Serviceable Obtainable Market)
Realistic market share you could capture in Year 1-3:
- Startups typically capture 1-5% of SAM
- Consider competitive intensity

**Formula:** SOM = SAM × realistic market share %

### Step 5: Document Methodology
- Show all calculations
- Cite all sources
- Explain all assumptions

---

## Output Format

```json
{
  "market_size": {
    "TAM": {
      "value": 12000000000,
      "currency": "USD",
      "description": "Global project management software market (bottom-up calculation)",
      "timeframe": "2024",
      "calculation": "100M knowledge workers × $120/year average spend",
      "source": "Bottom-up: ILO Global Employment Report (100M knowledge workers, free source) × $10/month typical PM tool pricing",
      "methodology": "bottom_up",
      "growth_rate": "Estimated 15% annual growth based on remote work trends"
    },
    "SAM": {
      "value": 1200000000,
      "currency": "USD",
      "description": "Cloud PM for SMBs (50-500 employees)",
      "calculation": "TAM ($12B) × 10% (SMB segment targeting creative agencies)",
      "assumptions": ["SMBs represent ~10% of PM software spend (source: Crunchbase free tier analysis)", "Creative agencies specifically: ~1M potential customers"]
    },
    "SOM": {
      "value": 24000000,
      "currency": "USD",
      "description": "Realistic Year 1 capture",
      "calculation": "SAM ($1.2B) × 2% (market share)",
      "assumptions": ["2% market share achievable in Year 1", "Based on acquiring 200 paying customers @ $10k/year each"]
    }
  },
  "market_trends": {
    "growth_drivers": ["Remote work adoption", "Cloud migration"],
    "market_maturity": "growth",
    "competition_intensity": "high"
  }
}
```

---

## Knowledge Resources

Reference `RESEARCH_market_sizing_formulas.yaml` for:
- TAM/SAM/SOM formulas
- Estimation heuristics (top-down, bottom-up, value theory)
- Credible data sources

---

## Quality Checklist

- [ ] TAM has credible source with URL
- [ ] SAM calculation shown with assumptions
- [ ] SOM calculation shown with assumptions
- [ ] Timeframe specified (which year?)
- [ ] Currency specified
- [ ] Growth rate included if available
- [ ] All assumptions documented

---

## Common Pitfalls

❌ "The market is huge" without numbers
❌ TAM without source
❌ Overly optimistic SOM (claiming 20%+ market share)
❌ Confusing TAM with SAM (global market vs. your segment)
❌ No clear calculation methodology

---

## Next Task

Proceed to **Task 04: Positioning Analysis**
