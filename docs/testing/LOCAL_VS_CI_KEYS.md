# Local Development vs CI/CD API Keys

## The Problem

GitHub Secrets (`secrets.GOOGLE_SEARCH_API_KEY`) are ONLY available in GitHub Actions CI/CD workflows.

They are **NOT** available in:
- ✗ Local development
- ✗ Claude Code sessions
- ✗ Manual script execution

## Solutions

### Option 1: Use Local .env File (Recommended for Development)

```bash
# Create .env from template
cp .env.template .env

# Edit .env with your actual keys
nano .env

# Source it before running scripts
source .env
python scripts/validate_research_tools.py
```

### Option 2: Export Keys Manually

```bash
export GOOGLE_SEARCH_API_KEY="your-actual-key"
export GOOGLE_SEARCH_ENGINE_ID="your-actual-id"
python scripts/validate_research_tools.py
```

### Option 3: Run Validation in GitHub Actions (Current Setup)

The keys work in CI/CD:

```bash
# Trigger the workflow
git push

# Or manually trigger
gh workflow run test-secrets.yml
```

## Current Status

✅ **GitHub Actions**: Keys configured and available
✗ **Local Development**: Keys NOT available (need .env or export)

## Recommendation

For dogfooding/testing, create `.env` file:

```bash
# .env (DO NOT COMMIT!)
GOOGLE_SEARCH_API_KEY=AIzaSy...your-key
GOOGLE_SEARCH_ENGINE_ID=your-cx-id

# Then run:
source .env && python scripts/validate_research_tools.py
```
