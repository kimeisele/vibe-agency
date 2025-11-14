# Validation Gate: Market Size Has Source

**Gate ID:** gate_market_size_has_source
**Purpose:** Ensure market size estimates include source and methodology
**Enforcement:** MANDATORY - blocks progression if failed

---

## Validation Criteria

This gate passes ONLY if:

1. **TAM has a credible source OR calculation method**
   - Source URL provided OR bottom-up calculation shown
   - Source is credible (FREE sources preferred: Google Search, government statistics, Crunchbase, ILO reports, etc.)
   - Optional: Industry analyst reports (Gartner, Forrester) if user has access
   - Timeframe specified (which year?)

2. **SAM calculation is documented**
   - Shows calculation formula
   - Explains assumptions
   - Logical relationship to TAM

3. **SOM estimate is realistic**
   - Shows calculation formula
   - Assumptions are documented
   - Market share is realistic (typically 1-5% for startups)

4. **All values are numerical**
   - Not vague ("huge market", "growing rapidly")
   - Actual numbers with currency

---

## Validation Logic

```python
def validate_market_size_has_source(market_size):
    """
    Validates that market size estimates have proper sources and methodology.

    Returns:
        {
            "passed": bool,
            "issues": list of str,
            "tam_has_source": bool,
            "sam_has_calculation": bool,
            "som_has_calculation": bool
        }
    """
    issues = []

    # Check TAM
    if "TAM" not in market_size:
        issues.append("TAM not provided")
    else:
        tam = market_size["TAM"]

        # Check TAM has value
        if "value" not in tam or tam["value"] is None:
            issues.append("TAM: No value provided")

        # Check TAM has source OR calculation
        has_source = "source" in tam and tam["source"]
        has_calculation = "calculation" in tam and tam["calculation"]

        if not has_source and not has_calculation:
            issues.append("TAM: No source or calculation method provided")
        elif has_source and not tam["source"].startswith(("http://", "https://", "Bottom-up:")):
            # Allow "Bottom-up:" prefix for calculated estimates
            issues.append(f"TAM: Source should be URL or 'Bottom-up: [calculation]': {tam['source']}")

        # Check TAM has timeframe
        if "timeframe" not in tam or not tam["timeframe"]:
            issues.append("TAM: No timeframe specified (which year?)")

        # Check currency
        if "currency" not in tam or not tam["currency"]:
            issues.append("TAM: No currency specified")

    # Check SAM
    if "SAM" not in market_size:
        issues.append("SAM not provided")
    else:
        sam = market_size["SAM"]

        # Check SAM has value
        if "value" not in sam or sam["value"] is None:
            issues.append("SAM: No value provided")

        # Check SAM has calculation
        if "calculation" not in sam or not sam["calculation"]:
            issues.append("SAM: No calculation/methodology provided")

        # Check SAM has assumptions
        if "assumptions" not in sam or not sam["assumptions"]:
            issues.append("SAM: No assumptions documented")

        # Sanity check: SAM should be <= TAM
        if "TAM" in market_size and "value" in tam and "value" in sam:
            if sam["value"] > tam["value"]:
                issues.append(f"SAM (${sam['value']:,}) is larger than TAM (${tam['value']:,}) - this is illogical")

    # Check SOM
    if "SOM" not in market_size:
        issues.append("SOM not provided")
    else:
        som = market_size["SOM"]

        # Check SOM has value
        if "value" not in som or som["value"] is None:
            issues.append("SOM: No value provided")

        # Check SOM has calculation
        if "calculation" not in som or not som["calculation"]:
            issues.append("SOM: No calculation/methodology provided")

        # Check SOM has assumptions
        if "assumptions" not in som or not som["assumptions"]:
            issues.append("SOM: No assumptions documented")

        # Sanity check: SOM should be <= SAM
        if "SAM" in market_size and "value" in sam and "value" in som:
            if som["value"] > sam["value"]:
                issues.append(f"SOM (${som['value']:,}) is larger than SAM (${sam['value']:,}) - this is illogical")

            # Check market share is realistic
            market_share_pct = (som["value"] / sam["value"]) * 100
            if market_share_pct > 10:
                issues.append(f"SOM implies {market_share_pct:.1f}% market share - this is unrealistic for most startups (typically 1-5%)")

    passed = len(issues) == 0

    return {
        "passed": passed,
        "issues": issues,
        "tam_has_source": "TAM" in market_size and market_size["TAM"].get("source", "").startswith("http"),
        "sam_has_calculation": "SAM" in market_size and "calculation" in market_size["SAM"],
        "som_has_calculation": "SOM" in market_size and "calculation" in market_size["SOM"]
    }
```

---

## Example: Pass vs. Fail

### ✅ PASS (Bottom-up Calculation - FREE)
```json
{
  "market_size": {
    "TAM": {
      "value": 12000000000,
      "currency": "USD",
      "description": "Global project management software market",
      "timeframe": "2024",
      "calculation": "100M knowledge workers × $120/year average spend",
      "source": "Bottom-up: ILO Global Employment Report (100M knowledge workers, free source) × $10/month typical PM tool pricing",
      "methodology": "bottom_up"
    },
    "SAM": {
      "value": 1200000000,
      "currency": "USD",
      "description": "Cloud PM for creative agencies",
      "calculation": "TAM ($12B) × 10% (creative agency segment)",
      "assumptions": ["Creative agencies represent ~10% of PM software users"]
    },
    "SOM": {
      "value": 24000000,
      "currency": "USD",
      "description": "Year 1 capture",
      "calculation": "SAM ($1.2B) × 2% (market share)",
      "assumptions": ["2% market share achievable in Year 1", "Based on 200 customers @ $10k/year"]
    }
  }
}
```

### ❌ FAIL - No TAM source
```json
{
  "market_size": {
    "TAM": {
      "value": 6800000000,
      "currency": "USD"
      // ❌ No source!
    }
  }
}
```

### ❌ FAIL - Vague market size
```json
{
  "market_size": "The market is huge and growing rapidly"  // ❌ Not structured data!
}
```

### ❌ FAIL - No SAM calculation
```json
{
  "market_size": {
    "TAM": {...},  // Has source
    "SAM": {
      "value": 680000000
      // ❌ No calculation or assumptions!
    }
  }
}
```

---

## Error Handling

If this gate fails:
1. List all missing sources
2. List all missing calculations/assumptions
3. Flag any illogical values (SOM > SAM > TAM)
4. Block progression to next task
5. Require MARKET_RESEARCHER to fix and resubmit

---

## Success Message

```
✅ Gate Passed: Market Size Has Source
- TAM: $12B with bottom-up calculation (100M knowledge workers × $120/year)
- SAM: $1.2B with documented calculation
- SOM: $24M with realistic assumptions (2% market share)
- All values logical (SOM < SAM < TAM)
- Ready for next task
```

---

## Failure Message

```
❌ Gate Failed: Market Size Has Source
Issues found:
- TAM: No source provided
- SAM: No calculation/methodology provided
- SOM: Implies 12.5% market share - unrealistic for startups (typically 1-5%)

Action Required: Provide TAM source, document SAM/SOM calculations, and revise SOM estimate.
```
