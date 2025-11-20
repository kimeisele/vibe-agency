# Gate: NFR Security Validation

**Gate ID:** gate_nfr_security
**Type:** Quality Gate
**Scope:** All code, configuration, and knowledge bases
**Enforcement:** BLOCKING (must pass before commit)

---

## Rule

All code and configuration must meet security requirements defined in `docs/requirements/NFR_SECURITY.yaml`:

1. **No Hardcoded Secrets:** No API keys, passwords, or tokens in code/config
2. **Safe YAML Loading:** Only `yaml.safe_load()` allowed (never `yaml.load()`)
3. **Input Validation:** All user inputs sanitized and validated
4. **Secure Dependencies:** No known critical vulnerabilities in dependencies
5. **Audit Logging:** Sensitive operations must be logged

---

## Rationale

**Why this rule exists:**

- **Secret Exposure:** Hardcoded secrets in git history can be exploited by attackers. Once committed, secrets remain in history forever (even after deletion).
- **YAML Injection:** `yaml.load()` allows arbitrary code execution. Using `yaml.safe_load()` prevents this attack vector (CVE-2020-14343).
- **Input Validation:** Unvalidated inputs enable path traversal, command injection, and other attacks.
- **Supply Chain Security:** Vulnerable dependencies (e.g., old PyYAML < 5.4) introduce known exploits.
- **Accountability:** Audit logs enable incident investigation and compliance (GDPR, SOC2).

**Impact of violations:**
- 🔴 Hardcoded secrets → Unauthorized access, cost, data breach
- 🔴 Unsafe YAML loading → Remote code execution
- 🟡 Missing input validation → Path traversal, injection attacks
- 🟡 Vulnerable dependencies → Known exploits
- 🟡 Missing audit logs → Cannot investigate incidents

---

## Validation

### Automated Checks

**1. Secret Detection (PRE-COMMIT HOOK ✅)**

**Tool:** `detect-secrets`

**Setup:**
```bash
# Install
pip install detect-secrets

# Create baseline
detect-secrets scan > .secrets.baseline

# Add to pre-commit (already in .pre-commit-config.yaml)
```

**What it detects:**
- API keys (AWS, Anthropic, OpenAI, etc.)
- Private keys (SSH, PGP)
- Passwords in environment variables
- JWTs and tokens

**Example violation:**
```python
# ❌ BLOCKED by pre-commit
ANTHROPIC_API_KEY = "sk-ant-api03-abc123..."

# ✅ ALLOWED
import os
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
```

---

**2. Safe YAML Loading (LINTING ✅)**

**Tool:** Custom `grep` check (can be added to pre-commit)

```bash
# Check for unsafe yaml.load()
if grep -r "yaml\.load(" agency_os/ tests/; then
    echo "❌ FAIL: Found yaml.load() - use yaml.safe_load() instead"
    exit 1
fi
```

**Example violations:**
```python
# ❌ BLOCKED - Arbitrary code execution risk
import yaml
data = yaml.load(file)  # NEVER USE THIS

# ✅ ALLOWED - Safe loading only
import yaml
data = yaml.safe_load(file)  # ALWAYS USE THIS
```

**Status:** IMPLEMENTED ✅ (all code uses safe_load)

**Verification:**
```bash
# Confirm no unsafe usage
grep -r "yaml\.load(" agency_os/ tests/
# (Should return nothing)
```

---

**3. Input Validation (CODE REVIEW ✅)**

**Checklist for reviewers:**

```markdown
## Security Checklist (PR Review)

### Input Validation
- [ ] All user inputs validated (agent_id, task_id, context)
- [ ] File paths validated (no path traversal with ../)
- [ ] No shell metacharacters in user input (if used in commands)

### Authentication
- [ ] API keys loaded from environment (not hardcoded)
- [ ] No secrets in logs or error messages

### Error Handling
- [ ] Error messages don't leak sensitive paths
- [ ] Stack traces sanitized in production

### Data Protection
- [ ] No PII in logs without user consent
- [ ] Sensitive data marked as such
```

**Example violations:**
```python
# ❌ Path traversal vulnerability
agent_path = f"{base_path}/{agent_id}"  # agent_id = "../../etc/passwd"

# ✅ Validated path
agent_path = self._get_agent_path(agent_id)  # Validates against AGENT_REGISTRY
if not agent_path.exists():
    raise AgentNotFoundError(...)
```

**Status:** PARTIALLY IMPLEMENTED ⚠️
- Agent paths validated (AGENT_REGISTRY whitelist) ✅
- Task paths validated (file existence check) ✅
- Runtime context validation (TO DO) ❌

---

**4. Dependency Scanning (CI/CD ⚠️)**

**Tool:** `pip-audit`

**Setup:**
```bash
# Install
pip install pip-audit

# Scan for vulnerabilities
pip-audit

# Add to CI (GitHub Actions future)
```

**What it checks:**
- Known CVEs in dependencies
- Outdated packages with security fixes
- Severity levels (LOW, MEDIUM, HIGH, CRITICAL)

**Example output:**
```
Found 2 vulnerabilities in 1 package:

pyyaml (5.3.1)
├── CVE-2020-14343 (CRITICAL)
│   ├── Arbitrary code execution via yaml.load()
│   └── Fixed in: 5.4+
└── Upgrade to: pyyaml>=6.0.1
```

**Current Status:** TO IMPLEMENT ❌

**Required Action:**
- Run `pip-audit` before each release
- Update requirements.txt with fixed versions
- Add to CI pipeline (GitHub Actions)

---

**5. Audit Logging (TO IMPLEMENT ❌)**

**Required Logs:**
```python
# Composition events
logger.info(f"composition_start: {agent_id}.{task_id} by {user}")

# Knowledge file access
logger.info(f"knowledge_loaded: {filepath} ({size_kb} KB)")

# Validation gate failures
logger.warning(f"gate_failed: {gate_id} - {reason}")

# Errors and exceptions
logger.error(f"composition_failed: {agent_id}.{task_id} - {error}", exc_info=True)

# Security events
logger.warning(f"security_violation: {violation_type} - {details}")
```

**Log Location:** `~/.vibe_agency/logs/audit.log`

**Current Status:** PARTIALLY IMPLEMENTED ⚠️
- Error logging ✅
- Info logging ✅
- Security event logging ❌
- Audit trail ❌

---

### Manual Checks

**Pre-Release Security Checklist:**

```markdown
## Security Audit (Before v1.0)

### Code Security
- [ ] No hardcoded secrets (run detect-secrets scan)
- [ ] All yaml.load() replaced with yaml.safe_load()
- [ ] Input validation implemented
- [ ] Error messages sanitized (no sensitive data)

### Dependency Security
- [ ] Run pip-audit (no CRITICAL vulnerabilities)
- [ ] All dependencies pinned (requirements.txt)
- [ ] Third-party licenses documented

### Configuration Security
- [ ] API keys in environment variables only
- [ ] File permissions correct (600 for sensitive files)
- [ ] No world-readable secrets

### Git Security
- [ ] No secrets in git history (run git log -S "sk-ant-")
- [ ] .gitignore includes .env, credentials, etc.
- [ ] Pre-commit hooks installed

### Operational Security
- [ ] Audit logging configured
- [ ] Log retention policy defined (30-90 days)
- [ ] Incident response plan documented
```

---

## Failure Guidance

### If Secret Detected in Code

**DO NOT COMMIT!**

**Immediate Actions:**
1. Remove secret from code
2. Rotate the exposed secret (API key, password, etc.)
3. Check if already committed to git history

**If already committed:**
```bash
# Check git history
git log -S "sk-ant-api" --all

# Remove from history (DESTRUCTIVE - use carefully)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch <file_with_secret>" \
  --prune-empty --tag-name-filter cat -- --all

# Or use BFG Repo-Cleaner (safer)
bfg --replace-text secrets.txt  # List secrets to remove
git reflog expire --expire=now --all && git gc --prune=now --aggressive
```

**Prevention:**
```bash
# Install pre-commit hooks
pre-commit install

# Test detection
echo "ANTHROPIC_API_KEY=sk-ant-api03-test" > test.py
git add test.py
git commit -m "test"  # Should be BLOCKED
```

---

### If Unsafe YAML Loading Found

**Example violation:**
```python
# ❌ UNSAFE
with open(file) as f:
    data = yaml.load(f)
```

**Fix:**
```python
# ✅ SAFE
with open(file) as f:
    data = yaml.safe_load(f)
```

**Why this matters:**
```yaml
# Malicious YAML file
!!python/object/apply:os.system
args: ['rm -rf /']
```

**With `yaml.load()`:** This executes `os.system('rm -rf /')` 🔥
**With `yaml.safe_load()`:** This raises `yaml.constructor.ConstructorError` ✅

**Global fix:**
```bash
# Find all instances
grep -rn "yaml\.load(" agency_os/ tests/

# Replace (use sed or manual)
sed -i 's/yaml\.load(/yaml.safe_load(/g' agency_os/**/*.py
```

---

### If Vulnerable Dependency Found

**Example:**
```
pyyaml (5.3.1) - CVE-2020-14343 (CRITICAL)
```

**Resolution:**
```bash
# Update dependency
pip install --upgrade pyyaml>=6.0.1

# Update requirements.txt
pip freeze | grep pyyaml >> requirements.txt

# Verify fix
pip-audit
```

**If upgrade breaks compatibility:**
1. Check CHANGELOG for breaking changes
2. Update code to new API
3. Run full test suite
4. If tests fail, investigate and fix

**If no fix available:**
1. Check for alternative package
2. Apply workaround (if documented)
3. Document risk in security log
4. Monitor for updates

---

## Monitoring

### Security Metrics

**Track Monthly:**
- Secrets detected (should be 0)
- Dependency vulnerabilities (by severity)
- Security-related issues created
- Time to fix vulnerabilities (goal: < 7 days for CRITICAL)

### Incident Response

**If security breach occurs:**

1. **Assess Impact:**
   - What was exposed?
   - Who has access?
   - What data was compromised?

2. **Contain:**
   - Rotate all affected secrets immediately
   - Revoke compromised access
   - Block attacker IP (if applicable)

3. **Investigate:**
   - Review audit logs
   - Identify attack vector
   - Document timeline

4. **Remediate:**
   - Fix vulnerability
   - Deploy patch
   - Verify fix

5. **Report:**
   - Notify affected users (GDPR: within 72 hours)
   - Create incident report
   - Update security procedures

---

## Implementation Status

- [x] Pre-commit hooks (detect-secrets, yamllint) - `.pre-commit-config.yaml`
- [x] Safe YAML loading - All code uses `yaml.safe_load()`
- [x] Input validation (partial) - Agent/task paths validated
- [ ] Dependency scanning - Add `pip-audit` to workflow
- [ ] Audit logging - Implement security event logging
- [ ] Secret rotation policy - Document in operations manual

**Next Steps:**
1. Run `pip-audit` and fix vulnerabilities
2. Implement audit logging for security events
3. Document secret rotation procedure
4. Set up dependency scanning in CI

---

## References

- `docs/requirements/NFR_SECURITY.yaml` - Full security requirements
- `.pre-commit-config.yaml` - Pre-commit hook configuration
- OWASP Top 10 - https://owasp.org/www-project-top-ten/
- CVE-2020-14343 - PyYAML arbitrary code execution
- `prompt_runtime.py` - Input validation implementation
