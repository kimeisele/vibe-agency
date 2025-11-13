# API Key Management Guide

**Document Version:** 1.0
**Last Updated:** 2025-11-13
**Status:** Official Guideline

---

## Table of Contents

- [Overview](#overview)
- [Key Storage](#key-storage)
- [Key Rotation](#key-rotation)
- [Security Best Practices](#security-best-practices)
- [Incident Response](#incident-response)
- [Troubleshooting](#troubleshooting)

---

## Overview

This document defines the official policy for managing API keys in the Vibe Agency system. API keys are sensitive credentials that must be protected to prevent unauthorized access and cost.

**Scope:** This policy applies to:
- Anthropic API keys (Claude)
- Any future LLM provider keys (OpenAI, Cohere, etc.)
- Third-party service keys (if integrated)

**Principle:** **NEVER** store API keys in code, configuration files, or git history.

---

## Key Storage

### ✅ CORRECT: Environment Variables

**Always** store API keys in environment variables.

#### Linux/macOS

**Option 1: Session-Only (Temporary)**
```bash
# Set for current terminal session only
export ANTHROPIC_API_KEY="sk-ant-api03-..."

# Verify
echo $ANTHROPIC_API_KEY
```

**Option 2: Permanent (Recommended)**
```bash
# Add to ~/.bashrc or ~/.zshrc
echo 'export ANTHROPIC_API_KEY="sk-ant-api03-..."' >> ~/.bashrc
source ~/.bashrc

# Or use ~/.profile for login shells
echo 'export ANTHROPIC_API_KEY="sk-ant-api03-..."' >> ~/.profile
```

**Option 3: .env File (Development Only)**
```bash
# Create .env file (NOT committed to git)
echo 'ANTHROPIC_API_KEY=sk-ant-api03-...' > .env

# Load in Python
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")
```

**Important:** Add `.env` to `.gitignore`:
```bash
echo '.env' >> .gitignore
```

#### Windows

**PowerShell:**
```powershell
# Session-only
$env:ANTHROPIC_API_KEY = "sk-ant-api03-..."

# Permanent (user-level)
[System.Environment]::SetEnvironmentVariable('ANTHROPIC_API_KEY', 'sk-ant-api03-...', 'User')

# Permanent (system-level, requires admin)
[System.Environment]::SetEnvironmentVariable('ANTHROPIC_API_KEY', 'sk-ant-api03-...', 'Machine')
```

**CMD:**
```cmd
REM Session-only
set ANTHROPIC_API_KEY=sk-ant-api03-...

REM Permanent
setx ANTHROPIC_API_KEY "sk-ant-api03-..."
```

### ❌ INCORRECT: Hardcoded Keys

**NEVER do this:**

```python
# ❌ BLOCKED by pre-commit hooks
ANTHROPIC_API_KEY = "sk-ant-api03-abc123..."

# ❌ Also blocked
config = {
    "api_key": "sk-ant-api03-abc123..."
}

# ❌ Even in comments!
# My API key is sk-ant-api03-abc123...
```

**Why this is dangerous:**
- Keys remain in git history forever (even after deletion)
- Anyone with repository access can use your key
- Costs can skyrocket if key is abused
- Data breaches if malicious usage

---

## Key Rotation

### When to Rotate Keys

**Mandatory Rotation (Immediately):**
- ✅ Key exposed in git history
- ✅ Key shared via insecure channel (email, Slack, etc.)
- ✅ Suspected unauthorized usage
- ✅ Team member with key access leaves

**Routine Rotation (Every 90 Days):**
- ✅ Good security hygiene
- ✅ Limits window of exposure if key compromised
- ✅ Recommended by NIST guidelines

### How to Rotate Keys

**Step 1: Generate New Key**

```bash
# For Anthropic:
# 1. Go to https://console.anthropic.com/settings/keys
# 2. Click "Create Key"
# 3. Copy new key (sk-ant-api03-NEW...)
```

**Step 2: Update Environment Variable**

```bash
# Linux/macOS
export ANTHROPIC_API_KEY="sk-ant-api03-NEW..."

# Update in ~/.bashrc or ~/.zshrc
sed -i 's/sk-ant-api03-OLD.../sk-ant-api03-NEW.../' ~/.bashrc
source ~/.bashrc
```

**Step 3: Verify New Key Works**

```bash
# Test with a simple API call (if LLM integration implemented)
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{
    "model": "claude-sonnet-4-5-20250929",
    "max_tokens": 10,
    "messages": [{"role": "user", "content": "Test"}]
  }'
```

**Expected Response:**
```json
{
  "id": "msg_...",
  "type": "message",
  "role": "assistant",
  "content": [{"type": "text", "text": "Test response"}],
  ...
}
```

**Step 4: Revoke Old Key**

```bash
# In Anthropic Console:
# 1. Go to https://console.anthropic.com/settings/keys
# 2. Find old key (sk-ant-api03-OLD...)
# 3. Click "Delete"
```

**Step 5: Verify Old Key Revoked**

```bash
# Should return 401 Unauthorized
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: sk-ant-api03-OLD..." \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{...}'
```

**Expected Response:**
```json
{
  "error": {
    "type": "authentication_error",
    "message": "invalid x-api-key"
  }
}
```

---

## Security Best Practices

### 1. Principle of Least Privilege

**Only share keys with those who need them.**

```markdown
## Key Access Control

### Who Needs Access?
- ✅ Developers running Vibe Agency locally
- ✅ CI/CD systems (GitHub Actions, if implemented)
- ❌ Product managers (don't need API access)
- ❌ Clients (they use their own keys)

### How to Share Securely?
- ✅ Encrypted password manager (1Password, LastPass, Bitwarden)
- ✅ Secure secret management (AWS Secrets Manager, HashiCorp Vault)
- ❌ Email (plain text)
- ❌ Slack/Discord (logged)
- ❌ GitHub Issues (public)
```

### 2. Use Separate Keys for Environments

**Isolate production from development:**

```bash
# Development
export ANTHROPIC_API_KEY_DEV="sk-ant-api03-dev..."

# Staging
export ANTHROPIC_API_KEY_STAGING="sk-ant-api03-staging..."

# Production
export ANTHROPIC_API_KEY_PROD="sk-ant-api03-prod..."
```

**Benefits:**
- Rotate dev key without affecting production
- Track usage separately (costs, rate limits)
- Revoke compromised key without downtime

### 3. Monitor API Usage

**Track key usage to detect anomalies:**

```bash
# Check usage in Anthropic Console
# https://console.anthropic.com/settings/usage

# Look for:
- Unexpected spikes in usage
- Requests from unknown IPs
- Unusual request patterns
```

**Set up alerts:**
- Daily usage threshold (e.g., > 1M tokens/day)
- Cost threshold (e.g., > $100/day)
- Failed authentication attempts

### 4. Never Log Keys

**Ensure keys don't appear in logs:**

```python
# ❌ BAD: Key in logs
logger.info(f"Using API key: {os.getenv('ANTHROPIC_API_KEY')}")

# ✅ GOOD: Sanitized logs
api_key = os.getenv('ANTHROPIC_API_KEY')
logger.info(f"Using API key: {api_key[:10]}...{api_key[-4:]}")
# Output: "Using API key: sk-ant-api...xyz"

# ✅ BEST: No key in logs
logger.info("API key loaded from environment")
```

**Check logs for leaks:**
```bash
# Search logs for keys
grep -r "sk-ant-api" ~/.vibe_agency/logs/
# (Should return nothing)
```

### 5. Git History Scanning

**Regularly scan git history for exposed keys:**

```bash
# Scan for API keys
git log -S "sk-ant-api" --all

# Use automated tools
pip install truffleHog
truffleHog --regex --entropy=True https://github.com/your/repo

# Or
pip install gitleaks
gitleaks detect --source .
```

**If key found in history:**
1. Rotate key immediately
2. Remove from history (see [Incident Response](#incident-response))
3. Notify team

---

## Incident Response

### If API Key is Exposed

**DO NOT PANIC. Follow these steps:**

#### Step 1: Assess Exposure (< 5 minutes)

```markdown
## Exposure Checklist

- [ ] Where was key exposed?
  - [ ] Git commit (public or private repo?)
  - [ ] Logs (who has access?)
  - [ ] Slack/email (who saw it?)
  - [ ] Screenshot (where posted?)

- [ ] Who has access?
  - [ ] Team members only
  - [ ] External parties
  - [ ] Public internet

- [ ] How long exposed?
  - [ ] Just now (< 1 hour)
  - [ ] Recent (< 24 hours)
  - [ ] Old (> 24 hours)
```

#### Step 2: Rotate Key (< 10 minutes)

```bash
# 1. Generate new key (Anthropic Console)
NEW_KEY="sk-ant-api03-NEW..."

# 2. Update environment variable
export ANTHROPIC_API_KEY="$NEW_KEY"

# 3. Update ~/.bashrc
sed -i.bak "s/ANTHROPIC_API_KEY=.*/ANTHROPIC_API_KEY=\"$NEW_KEY\"/" ~/.bashrc

# 4. Verify new key works
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $NEW_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model": "claude-sonnet-4-5-20250929", "max_tokens": 10, "messages": [{"role": "user", "content": "Test"}]}'
```

#### Step 3: Revoke Old Key (< 2 minutes)

```bash
# In Anthropic Console:
# 1. Go to https://console.anthropic.com/settings/keys
# 2. Delete old key
```

#### Step 4: Review Usage Logs (< 15 minutes)

```bash
# Check Anthropic Console for suspicious activity:
# - Unusual IP addresses
# - Unexpected request volume
# - Strange prompts

# Document findings:
# - Date/time of suspicious activity
# - Request IDs
# - IP addresses
```

#### Step 5: Remove from Git History (if committed)

**Tool: BFG Repo-Cleaner (Recommended)**

```bash
# 1. Install BFG
brew install bfg  # macOS
# Or download from https://rtyley.github.io/bfg-repo-cleaner/

# 2. Create file with keys to remove
echo "sk-ant-api03-OLD..." > secrets.txt

# 3. Run BFG
bfg --replace-text secrets.txt .git

# 4. Cleanup
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 5. Force push (WARNING: Rewrites history)
git push --force --all
git push --force --tags
```

**Alternative: git filter-branch**

```bash
# More manual, but works without tools
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch <file_with_key>" \
  --prune-empty --tag-name-filter cat -- --all

git reflog expire --expire=now --all
git gc --prune=now --aggressive
git push --force --all
```

**Important:** Notify all team members to `git clone` fresh copy (their local history still has key).

#### Step 6: Document Incident (< 30 minutes)

**Create incident report:**

```markdown
# Security Incident Report

**Date:** 2025-11-13
**Incident ID:** INC-20251113-001
**Reporter:** [Your Name]
**Severity:** HIGH

## Summary
API key exposed in git commit [commit hash].

## Timeline
- 10:00 - Key accidentally committed to repo
- 10:15 - Exposure detected by pre-commit hook (failed)
- 10:20 - Key rotated
- 10:25 - Old key revoked
- 10:30 - Git history cleaned
- 10:45 - Team notified

## Impact
- No unauthorized usage detected
- Key exposed for 15 minutes
- Private repository (limited exposure)

## Root Cause
Developer disabled pre-commit hooks temporarily.

## Remediation
- Key rotated
- Git history cleaned
- Pre-commit hooks re-enabled
- Team training scheduled

## Lessons Learned
- Never disable pre-commit hooks
- Always verify hooks active before commit
- Consider CI-based secret scanning as backup
```

#### Step 7: Notify Stakeholders

**Who to notify:**
- Team members (immediate)
- Manager/lead (within 1 hour)
- Security team (if applicable)
- Clients (if their data affected - GDPR: within 72 hours)

**Template Email:**

```
Subject: [URGENT] API Key Rotation Required

Team,

An API key was accidentally exposed in git commit [hash].

ACTION REQUIRED:
1. Pull latest code (key removed from history)
2. Update your ANTHROPIC_API_KEY environment variable
3. New key: [sent separately via secure channel]

The old key has been revoked and is no longer valid.

Timeline:
- Exposure: 10:00
- Detected: 10:15
- Rotated: 10:20
- Impact: None (private repo, 15-minute exposure)

No further action required. If you have questions, contact [security team].

Thanks,
[Your Name]
```

---

## Troubleshooting

### Error: "Authentication failed"

**Symptoms:**
```
anthropic.APIError: authentication_error: invalid x-api-key
```

**Causes:**
1. Key not set in environment
2. Typo in key
3. Key revoked

**Solutions:**

```bash
# 1. Check if key is set
echo $ANTHROPIC_API_KEY
# (Should output: sk-ant-api03-...)

# 2. Verify key format
# Anthropic keys start with: sk-ant-api03-
# Length: ~90 characters

# 3. Test key manually
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model": "claude-sonnet-4-5-20250929", "max_tokens": 10, "messages": [{"role": "user", "content": "Test"}]}'

# 4. If still failing, generate new key
```

---

### Error: "Rate limit exceeded"

**Symptoms:**
```
anthropic.APIError: rate_limit_error: requests per minute limit exceeded
```

**Causes:**
1. Too many requests in short time
2. Key shared across multiple processes
3. Exceeded tier limits

**Solutions:**

```bash
# 1. Check current rate limits (Anthropic Console)
# https://console.anthropic.com/settings/limits

# 2. Implement rate limiting in code
import time

def call_api_with_backoff(prompt, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = client.messages.create(...)
            return response
        except anthropic.RateLimitError:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                logger.warning(f"Rate limited, waiting {wait_time}s")
                time.sleep(wait_time)
            else:
                raise

# 3. Upgrade tier (if consistently hitting limits)
```

---

### Key Not Loading from .env

**Symptoms:**
```python
os.getenv('ANTHROPIC_API_KEY')  # Returns None
```

**Solutions:**

```python
# 1. Install python-dotenv
pip install python-dotenv

# 2. Load .env file
from dotenv import load_dotenv
load_dotenv()  # Must be called BEFORE os.getenv()

api_key = os.getenv('ANTHROPIC_API_KEY')

# 3. Check .env file location
# Must be in same directory as script, or specify path
load_dotenv('/path/to/.env')

# 4. Verify .env format
# File: .env
# Content: ANTHROPIC_API_KEY=sk-ant-api03-...
# (No quotes, no spaces around =)
```

---

## Appendix: Key Formats

### Anthropic API Keys

```
Format: sk-ant-api03-[base64-encoded-data]-[more-data]-AA
Example: sk-ant-api03-abc123def456ghi789jkl012mno345pqr678stu901vwx234yz-ABCDEFG-AA
Length: ~90 characters
```

**Validation Regex:**
```python
import re

def is_valid_anthropic_key(key):
    pattern = r'^sk-ant-api\d{2}-[A-Za-z0-9_-]{80,100}-[A-Za-z0-9_-]+-[A-Z]{2}$'
    return bool(re.match(pattern, key))
```

---

## References

- Anthropic Console: https://console.anthropic.com/
- Anthropic API Docs: https://docs.anthropic.com/
- NIST Key Management Guidelines: https://csrc.nist.gov/publications/detail/sp/800-57-part-1/rev-5/final
- OWASP Secrets Management: https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html
- `docs/requirements/NFR_SECURITY.yaml` - Security NFRs

---

**Questions?** Contact the security team or file an issue at https://github.com/kimeisele/vibe-agency/issues
