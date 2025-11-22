# 🚀 VIBE OS Setup Guide

## Quick Start (5 Minutes)

### No API Keys? NO PROBLEM!
```bash
# Clone the repository
git clone https://github.com/kimeisele/vibe-agency.git
cd vibe-agency

# Boot the system (works offline with SmartLocalProvider)
./bin/system-boot.sh

# Run a mission (offline mode - no external APIs needed)
uv run apps/agency/cli.py --mission "Plan a simple calculator app"
```

**That's it!** The system runs **100% offline by default** using SmartLocalProvider.

---

## Understanding the Modes

### 🔌 **Offline Mode (Default)**
- **No API keys required**
- **Works everywhere** (no internet needed)
- Uses: `SmartLocalProvider` (intelligent local orchestration)
- Perfect for: Development, testing, proof-of-concept
- Limitation: LLM responses are templated, not real AI

**To use offline mode:**
Just don't set any API keys. The system auto-detects and activates SmartLocalProvider.

### 🌐 **Online Mode (Optional - Enhanced)**
- **Requires API keys** (free tier available)
- Uses real AI (Google Gemini 2.5 Flash)
- Much more capable and intelligent
- Fallback: If API fails, automatically uses StewardProvider (Claude Code integration)

---

## Setting Up Online Mode (Optional)

### Step 1: Get API Keys

#### Google Gemini API (Recommended - Free during preview)
1. Visit: https://aistudio.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key

#### Anthropic API (Alternative)
1. Visit: https://console.anthropic.com/
2. Sign up for account
3. Create an API key
4. Copy the key

#### Google Custom Search (Optional - For research features)
1. Visit: https://programmablesearchengine.google.com/
2. Create a custom search engine
3. Get your Search Engine ID
4. Visit: https://console.cloud.google.com/apis/library/customsearch.googleapis.com
5. Enable the API and create a key

### Step 2: Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API keys
nano .env
```

**Example .env file:**
```env
# Google Gemini (Primary LLM - Recommended)
GOOGLE_API_KEY=AIzaSyDxxx...your-key-here...xxxxx

# Anthropic Claude (Alternative LLM)
ANTHROPIC_API_KEY=sk-ant-xxx...your-key-here...xxxxx

# Google Search (Optional - for research phase)
GOOGLE_SEARCH_API_KEY=xxx...your-key-here...xxx
GOOGLE_SEARCH_ENGINE_ID=abc123456789

# Execution mode
VIBE_AUTO_MODE=true
```

### Step 3: Boot with APIs

```bash
./bin/system-boot.sh
```

The system will detect your API keys and activate Online Mode automatically.

---

## How API Fallback Works

The system has an intelligent **5-layer fallback chain**:

```
Layer 1: Try Google Gemini (best quality, free during preview)
         ↓ (if 403 or network error)
Layer 2: Try Anthropic Claude (fallback to paid API)
         ↓ (if unavailable)
Layer 3: Try STEWARD Provider (Claude Code environment integration)
         ↓ (if not in Claude Code environment)
Layer 4: Use SmartLocalProvider (offline orchestration, no APIs needed)
         ↓ (guaranteed - always works)
Layer 5: NoOp Provider (mock responses for CI/CD)
```

**What this means:**
- Your missions **never fail** due to missing APIs
- Online mode gives you 10x better results
- Offline mode still works, just with templated responses
- You can start with offline, upgrade to online later

---

## Verification

### Check if System is Ready

```bash
# Health check (shows current mode)
./bin/vibe status

# Expected output:
# ✅ Git: clean
# ✅ Tests: passing
# ✅ Environment: ready
# 🔌 Mode: Offline (SmartLocalProvider)
# or
# 🌐 Mode: Online (Google Gemini)
```

### Run a Test Mission

```bash
# Offline test
uv run apps/agency/cli.py --mission "Explain what you are in 2 sentences"

# Online test (if you have API keys)
uv run apps/agency/cli.py --mission "Plan a React app with TypeScript and Tailwind"
```

---

## Troubleshooting

### Error: "Google Gemini invocation failed: 403 Forbidden"

**This is NORMAL and EXPECTED if:**
- You don't have `GOOGLE_API_KEY` in .env
- Your API key is invalid or expired
- Google API is temporarily blocked

**Fix:**
```bash
# Check your .env file
cat .env | grep GOOGLE_API_KEY

# If empty or says "your-key-here", the system will use offline mode
# This is fine! Just continue.

# If you have a valid key, try:
uv run apps/agency/cli.py --mission "test"
# System should auto-switch to offline mode (SmartLocalProvider)
```

### Error: ".env file not found"

```bash
# Create it from the template
cp .env.example .env
# Or create a new one (system auto-creates with defaults)
```

### System boots but missions fail

1. Check boot status:
   ```bash
   ./bin/system-boot.sh
   ```
   Should show: `✅ SYSTEM BOOT COMPLETE`

2. Check dependencies:
   ```bash
   uv sync
   ```

3. Run smoke tests:
   ```bash
   uv run pytest tests/test_*_workflow.py -v
   ```

---

## What Each Mode Can Do

### 🔌 Offline Mode (SmartLocalProvider)
✅ Plan software architecture
✅ Generate code templates
✅ Create test structures
✅ Coordinate task delegation
⚠️ Responses are templated, not AI-generated

### 🌐 Online Mode (Google Gemini / Anthropic)
✅ Everything offline can do
✅ Generate real code (with AI analysis)
✅ Understand requirements deeply
✅ Suggest architectures intelligently
✅ Debug code and suggest fixes
✅ Smart test generation
✅ Production-grade completions

---

## Next Steps

- **Offline?** Start building! See: [QUICKSTART.md](../QUICKSTART.md)
- **Online?** Try: `uv run apps/agency/cli.py --mission "Build a REST API with FastAPI"`
- **Trouble?** Open an issue: https://github.com/kimeisele/vibe-agency/issues

---

## Architecture Notes (ARCH-041: Offline Sovereignty)

Vibe OS is designed with **offline-first** philosophy:
- Default: SmartLocalProvider (100% local, no external dependencies)
- Optional: Online APIs for enhanced capabilities
- Graceful degradation: If APIs fail, system automatically downgrades

This means:
1. You can always run the system (no dependency on external services)
2. You can add APIs later for better results
3. The system never crashes due to missing API keys

**This is intentional.** We believe in sovereignty and resilience.

---

**Version:** v0.5.0-beta | **Last Updated:** 2025-11-22
