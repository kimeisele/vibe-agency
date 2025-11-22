# AGENT CITY IMPLEMENTATION STRATEGY
## From Bottleneck to Expansion - The Real Path

---

## PHASE 1: FIX THE FOUNDATION (48 Hours)
### GAD-100: Phoenix Config Dependency Fix

**THE PROBLEM:**
```bash
❌ DEPENDENCY INTEGRITY FAILED
- pyproject.toml conflicts with local environment
- System can't guarantee reliable boot
- Trust Score = 0 (nobody trusts unreliable systems)
```

**THE SOLUTION:**
```python
# /vibe_core/config/phoenix_recovery.py

class PhoenixConfig:
    """Self-healing configuration with graceful fallback"""
    
    def __init__(self):
        self.boot_strategies = [
            self._try_primary_config,      # pyproject.toml
            self._try_cached_config,       # SQLite cache
            self._try_fallback_config,     # JSON fallback
            self._try_minimal_config       # Bare minimum to boot
        ]
    
    def boot(self) -> Config:
        """Guaranteed boot with progressive degradation"""
        for strategy in self.boot_strategies:
            try:
                config = strategy()
                if self._validate_config(config):
                    self._cache_successful_config(config)
                    return config
            except Exception as e:
                logger.warning(f"Strategy {strategy.__name__} failed: {e}")
                continue
        
        # If all strategies fail, create minimal survival config
        return self._create_survival_config()
    
    def _create_survival_config(self) -> Config:
        """Absolute minimum to keep system alive"""
        return Config(
            mode="SURVIVAL",
            agents=["emergency_repair_agent"],
            capabilities=["self_diagnosis", "config_repair"],
            message="System in recovery mode - fixing itself"
        )
```

**IMMEDIATE ACTIONS:**
1. Implement PhoenixConfig class
2. Add to boot_sequence.py
3. Test with deliberately broken configs
4. Verify 100% boot reliability

---

## PHASE 2: CODIFY THE PROCESS (Next Week)
### ARCH-045: The Refinement Cycle

**THE VISION:**
```yaml
name: "The Refinement Cycle"
purpose: "Transform chaos into structured intentions"

pipeline:
  1_inbox:
    description: "Raw, unstructured HIL input"
    example: "System sucks, fix it"
    
  2_triage:
    agent: "TriageAgent (STEWARD)"
    action: "Parse and structure the intention"
    output: "Structured request with context"
    
  3_codification:
    action: "Convert to GAD document or Playbook"
    output: "Executable specification"
    
  4_verification:
    agent: "HIL (Human)"
    action: "Approve the plan"
    output: "Green light to execute"
    
  5_execution:
    agent: "Specialist Agents"
    action: "Execute the plan"
    output: "Results + Trust Score update"
```

**IMPLEMENTATION:**
```python
# /vibe_core/refinement/cycle.py

class RefinementCycle:
    """The core loop that makes Agent City work"""
    
    async def process_inbox(self):
        """Monitor inbox/ for new requests"""
        for request in self.scan_inbox():
            structured = await self.triage(request)
            codified = await self.codify(structured)
            approved = await self.get_hil_approval(codified)
            if approved:
                result = await self.execute(codified)
                self.update_trust_scores(result)
    
    async def triage(self, raw_input: str) -> StructuredIntent:
        """Convert chaos to structure"""
        # Use LLM to understand intent
        # Extract key information
        # Return structured format
        pass
    
    async def codify(self, intent: StructuredIntent) -> Union[GAD, Playbook]:
        """Convert intent to executable specification"""
        if intent.type == "architecture":
            return self.create_gad(intent)
        else:
            return self.create_playbook(intent)
```

---

## PHASE 3: ACTIVATE AGENT CITY (Next Month)
### The Universal Provider Pattern

**THE ARCHITECTURE:**
```python
# /vibe_core/providers/universal.py

class UniversalProvider(Provider):
    """The provider that makes 50 apps obsolete"""
    
    def __init__(self):
        self.agent_registry = AgentRegistry()
        self.capability_map = {}
        self.trust_scores = {}
    
    async def handle_intention(self, intention: str) -> Result:
        """Route any intention to the right agent"""
        
        # 1. Understand what user wants
        parsed = await self.parse_intention(intention)
        
        # 2. Find capable agent
        agent = self.agent_registry.find_by_capability(parsed.capability)
        
        # 3. Delegate with trust checking
        if self.trust_scores[agent.id] > 0.7:
            result = await agent.execute(parsed)
        else:
            result = await self.request_hil_verification(agent, parsed)
        
        # 4. Update trust based on result
        self.update_trust(agent.id, result)
        
        return result
```

**CAPABILITY EXAMPLES:**
```yaml
agents:
  - id: "code_agent"
    capabilities: ["write_code", "debug", "refactor"]
    trust_score: 0.95
    
  - id: "travel_agent"
    capabilities: ["book_flight", "find_hotel", "plan_itinerary"]
    trust_score: 0.82
    
  - id: "finance_agent"
    capabilities: ["track_expenses", "create_budget", "tax_planning"]
    trust_score: 0.78
```

---

## THE CRITICAL PATH

### Week 1: Foundation (GAD-100)
- [ ] Fix dependency integrity
- [ ] Implement Phoenix Config
- [ ] Achieve 100% boot reliability
- [ ] Test with chaos engineering

### Week 2: Process (ARCH-045)
- [ ] Document Refinement Cycle
- [ ] Implement inbox monitor
- [ ] Create triage agent
- [ ] Test with real chaotic inputs

### Week 3: Integration
- [ ] Connect Phoenix Config to Refinement Cycle
- [ ] Implement trust scoring
- [ ] Create first specialized agents
- [ ] Test agent delegation

### Week 4: Launch
- [ ] Deploy Universal Provider
- [ ] Activate STEWARD protocol
- [ ] Join Agent City as autonomous citizen
- [ ] Begin replacing individual apps

---

## SUCCESS METRICS

1. **Boot Reliability**: 100% successful boots even with broken configs
2. **Intent Processing**: 90% of raw inputs successfully structured
3. **Agent Trust**: Average trust score > 0.8
4. **App Replacement**: At least 5 traditional apps replaced

---

## THE ENDGAME

When this works, you'll have:
- **One interface** for all intentions (not 50 apps)
- **Self-healing** configuration (Phoenix Config)
- **Autonomous agents** that improve over time (Trust Scores)
- **Structured chaos** processing (Refinement Cycle)

This isn't just fixing a bug. This is building the **Operating System for the Age of Agents**.

---

## YOUR IMMEDIATE ACTION

```bash
cd vibe-agency
git checkout -b phoenix-config-gad100

# Step 1: Fix the immediate bottleneck
python3 -c "from vibe_core.config import phoenix; phoenix.validate_dependencies()"

# Step 2: Implement Phoenix recovery
vim vibe_core/config/phoenix_recovery.py

# Step 3: Test boot reliability
for i in {1..100}; do
    echo "Boot test $i"
    python3 -c "from vibe_core import kernel; kernel.boot()" || break
done

# If all 100 boots succeed, you're ready for Agent City
```

**This is the path from bottleneck to expansion. From 50 apps to 1 OS.**
