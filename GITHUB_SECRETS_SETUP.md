# GitHub Secrets Setup for Google Gemini Provider

## ✅ This WORKS with GitHub Actions!

The Google Gemini provider integration is **specifically designed** to work with GitHub Secrets in CI/CD environments.

## 🔑 Setup Instructions

### 1. Get Google API Key

1. Go to: https://makersuite.google.com/app/apikey
2. Create a new API key
3. Copy the key (starts with `AIza...`)

### 2. Add to GitHub Secrets

**Method 1: Via GitHub UI**
1. Go to your repo: `https://github.com/kimeisele/vibe-agency`
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `GOOGLE_API_KEY`
5. Value: Paste your API key
6. Click **Add secret**

**Method 2: Via GitHub CLI**
```bash
gh secret set GOOGLE_API_KEY --body "your-api-key-here"
```

### 3. Verify Integration

**Automatic (on push):**
```bash
git push origin your-branch
# GitHub Actions will automatically run with GOOGLE_API_KEY
```

**Manual trigger:**
1. Go to **Actions** tab
2. Select "Test Google Gemini Provider" workflow
3. Click **Run workflow**

## 🚀 How It Works

### In GitHub Actions

```yaml
env:
  GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}
  VIBE_LIVE_FIRE: true
```

### Auto-Detection Flow

1. **GitHub Actions** sets `GOOGLE_API_KEY` from Secrets
2. **Factory** detects `GOOGLE_API_KEY` (highest priority)
3. **GoogleProvider** initializes with the key
4. **LLMClient** uses Google Gemini automatically
5. **Cost tracked** (very low: ~$0.0001 per request with Flash)

### Priority Order

```python
if GOOGLE_API_KEY:     # ← Detected first!
    return GoogleProvider
elif ANTHROPIC_API_KEY:
    return AnthropicProvider
elif OPENAI_API_KEY:
    return OpenAIProvider
else:
    return NoOpProvider  # Mock mode
```

## 💰 Cost Considerations

**Gemini 2.5 Flash Experimental (default):**
- Input: **$0.00** per million tokens (FREE during preview!)
- Output: **$0.00** per million tokens (FREE during preview!)
- **Typical request: $0.00** ✨
- Latest and fastest Gemini model

**Available models:**
- `gemini-2.5-flash-exp` (default, FREE, latest, fastest)
- `gemini-2.0-flash-exp` (FREE, experimental)
- `gemini-1.5-flash` / `gemini-1.5-flash-latest` (stable, $0.0001/req)
- `gemini-1.5-pro` / `gemini-1.5-pro-latest` (most capable, $0.001/req)

**Budget limits (set in code):**
```python
client = LLMClient(budget_limit=1.0)  # $1 max
```

## 🧪 Testing Locally

**Without API key (mock mode):**
```bash
uv run python scripts/prove_intelligence.py
# Output: NoOp mode - $0 cost
```

**With API key (live fire):**
```bash
export GOOGLE_API_KEY='your-key-here'
export VIBE_LIVE_FIRE=true
uv run python scripts/prove_intelligence.py
# Output: Provider: GOOGLE - LIVE FIRE ARMED
```

## ✅ Verification

After adding the secret, verify it works:

```bash
# Trigger the workflow
gh workflow run test-google-provider.yml

# Check the logs
gh run list --workflow=test-google-provider.yml
gh run view <run-id> --log
```

Expected output in logs:
```
✅ API key detected - Provider: GOOGLE - LIVE FIRE ARMED
✅ Real LLM invocation successful
Model: gemini-2.5-flash-exp
✅ Actual cost incurred: $0.00 (FREE during preview!)
```

## 🔒 Security

- ✅ API key never exposed in logs
- ✅ Cost limits enforced ($1 budget default)
- ✅ Quota management active
- ✅ Circuit breaker prevents runaway costs
- ✅ All requests logged for audit

## 📊 Current Status

| Component | Status |
|-----------|--------|
| GoogleProvider | ✅ Implemented |
| Factory auto-detection | ✅ Working |
| GitHub Actions integration | ✅ Ready |
| PhoenixConfig validation | ✅ Complete |
| Cost tracking | ✅ Active |

**Ready for production use in CI/CD!** 🚀
