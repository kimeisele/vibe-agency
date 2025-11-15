# How to Fix: Google Search API Keys Not Accessible

## The Problem

You set up keys in **GitHub Secrets** (Settings → Secrets → Actions).
But GitHub Secrets are **ONLY** available in GitHub Actions CI/CD, **NOT** in Claude Code sessions.

## The Solution

Claude Code needs keys in `.claude/settings.local.json`:

### Step 1: Copy the template

```bash
cd /home/user/vibe-agency
cp .claude/settings.local.json.template .claude/settings.local.json
```

### Step 2: Edit with your ACTUAL keys

```bash
nano .claude/settings.local.json
```

Replace `YOUR_GOOGLE_API_KEY_HERE` with your actual Google API key.
Replace `YOUR_SEARCH_ENGINE_ID_HERE` with your actual search engine ID.

### Step 3: Verify it works

```bash
python scripts/validate_research_tools.py
```

You should see:
```
✅ Google Search API keys found
✅ Got 3 results from Google Search API
```

## Where to Get the Keys

### Google API Key:
https://console.cloud.google.com/apis/credentials

### Search Engine ID:
https://programmablesearchengine.google.com/controlpanel/all

## File Structure

```
vibe-agency/
├── .claude/
│   ├── settings.local.json  ← YOUR KEYS (gitignored, not committed)
│   └── settings.local.json.template  ← Template (committed)
```

## Security

✅ `.claude/settings.local.json` is gitignored
✅ Won't be committed to repo
✅ Local to your Claude Code session only

## Why Two Places?

| Location | Used By | When |
|----------|---------|------|
| GitHub Secrets | GitHub Actions | CI/CD workflows |
| .claude/settings.local.json | Claude Code | Development sessions |

You need BOTH if you want keys to work in both places.
