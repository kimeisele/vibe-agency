# Google Custom Search API Setup Guide

## Problem: 400 Bad Request Error

If you're seeing this error:
```
RuntimeError: Google Search API error: 400 Client Error: Bad Request
```

It means your Google Custom Search Engine (CSE) is not properly configured.

## Solution: Create Your Custom Search Engine

### Step 1: Create a Custom Search Engine

1. Go to: **https://programmablesearchengine.google.com/controlpanel/create**

2. Fill in the form:
   - **Search engine name:** `VIBE Agency Research`
   - **What to search:** Select "Search the entire web"
   - Check the box: "Search the entire web"
   - Click **"Create"**

3. **WICHTIG:** Finde deine **Search Engine ID** (es gibt 2 Wege):

   **Weg 1 - Im Setup Code (EINFACHSTE METHODE):**
   - Nach dem Erstellen siehst du Code wie:
     ```html
     <script async src="https://cse.google.com/cse.js?cx=a1b2c3d4e5f6g7h8i">
     ```
   - **Der Wert nach `cx=` ist deine Search Engine ID!**
   - Beispiel: `cx=a1b2c3d4e5f6g7h8i` → deine ID ist `a1b2c3d4e5f6g7h8i`

   **Weg 2 - Im Control Panel:**
   - Gehe zu: **https://programmablesearchengine.google.com/controlpanel/all**
   - Klicke auf deine Search Engine
   - Die ID steht unter "Search engine ID"

4. **Kopiere NUR den Wert nach `cx=`** (OHNE `cx=` selbst!)
   - ✅ Richtig: `a1b2c3d4e5f6g7h8i`
   - ❌ Falsch: `cx=a1b2c3d4e5f6g7h8i`

### Step 2: Get Your API Key

1. Go to: **https://console.cloud.google.com/apis/credentials**

2. If you don't have a project:
   - Click **"Create Project"**
   - Name it: `vibe-agency-research`
   - Click **"Create"**

3. Enable the Custom Search API:
   - Go to: **https://console.cloud.google.com/apis/library/customsearch.googleapis.com**
   - Click **"Enable"**

4. Create an API key:
   - Go back to: **https://console.cloud.google.com/apis/credentials**
   - Click **"Create Credentials"** → **"API Key"**
   - **Copy the API key!**

5. (Optional but recommended) Restrict the key:
   - Click on the key you just created
   - Under "API restrictions", select "Restrict key"
   - Choose "Custom Search API"
   - Click **"Save"**

### Step 3: Update GitHub Secrets

1. Go to: **https://github.com/kimeisele/vibe-agency/settings/secrets/actions**

2. Update or create these secrets:

   **Secret #1: GOOGLE_SEARCH_API_KEY**
   - Name: `GOOGLE_SEARCH_API_KEY`
   - Value: Der API Key aus Step 2 (z.B. `AIzaSyDa...`)

   **Secret #2: GOOGLE_SEARCH_ENGINE_ID**
   - Name: `GOOGLE_SEARCH_ENGINE_ID`
   - Value: **NUR der Wert nach `cx=`** aus Step 1
   - Beispiel: Wenn dein Code ist `cx=a1b2c3d4e5f6g7h8i`, dann trage ein: `a1b2c3d4e5f6g7h8i`
   - ⚠️ **OHNE** `cx=`!

### Step 4: Test Your Configuration

Run this in your terminal (replace with your actual values):

```bash
export GOOGLE_SEARCH_API_KEY="your-api-key-here"
export GOOGLE_SEARCH_ENGINE_ID="your-search-engine-id-here"

python agency_os/00_system/orchestrator/tools/google_search_client.py
```

You should see:
```
1. Title of search result
   https://example.com/...

2. Title of search result
   https://example.com/...
...
```

## Troubleshooting

### Error: "API key not valid"
- Check that you copied the full API key (no extra spaces)
- Make sure the Custom Search API is **enabled** in your Google Cloud project
- Check that billing is enabled (required for Custom Search API)

### Error: "Invalid Value" for cx parameter
- This means your Search Engine ID is wrong
- **Häufiger Fehler:** Du hast `cx=` mit kopiert
  - ❌ Falsch: `GOOGLE_SEARCH_ENGINE_ID=cx=a1b2c3d4e5f6g7h8i`
  - ✅ Richtig: `GOOGLE_SEARCH_ENGINE_ID=a1b2c3d4e5f6g7h8i`
- Go back to https://programmablesearchengine.google.com/controlpanel/all
- Find your search engine and copy the **Search engine ID** (not the name!)

### Error: "Quota exceeded"
- Free tier: 100 queries/day
- Wait 24 hours or upgrade to paid tier

### Error: "Billing must be enabled"
- Google requires a billing account even for free tier
- Go to: https://console.cloud.google.com/billing
- Add a credit card (you won't be charged unless you exceed free tier)

## Free Tier Limits

- **100 queries per day** (free)
- After 100 queries, you'll get a quota error
- Resets at midnight Pacific Time
- Paid tier: $5 per 1000 queries after free tier

## Verification Checklist

- [ ] Created Custom Search Engine
- [ ] Got Search Engine ID (format: `a1b2c3d4e5f6g7h8i`)
- [ ] Enabled Custom Search API in Google Cloud
- [ ] Created API key
- [ ] Billing enabled (required even for free tier)
- [ ] Updated GitHub Secrets
- [ ] Tested locally (python script returns results)
