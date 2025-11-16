# 🔄 Auto-Sync zu vibe-research

## Status

✅ Trigger-Workflow aktiv (`.github/workflows/trigger-research-sync.yml`)

## Wie es funktioniert

Wenn du Code in diesen Bereichen änderst und pushst:
- `agency_os/`
- `core_orchestrator.py`
- `handlers/`
- `vibe-cli.py`

...wird automatisch ein Sync zu `vibe-research` getriggert.

## GitHub Token Setup (einmalig erforderlich)

### Schritt 1: Token erstellen

1. Gehe zu: https://github.com/settings/tokens
2. Click "Generate new token" → "Classic"
3. Name: `vibe-research-sync`
4. Expiration: 90 days (oder länger)
5. Scopes: **Nur `repo` ankreuzen**
6. Generate Token
7. **KOPIERE DEN TOKEN** (wird nur einmal angezeigt!)

### Schritt 2: Token als Secret hinzufügen

1. Gehe zu: https://github.com/kimeisele/vibe-agency/settings/secrets/actions
2. Click "New repository secret"
3. Name: `RESEARCH_SYNC_TOKEN`
4. Value: Dein kopierter Token
5. Add secret

### Schritt 3: Testen

```bash
# Option A: Automatischer Test
# Mache eine kleine Änderung in agency_os/
echo "# sync test" >> agency_os/README.md
git add -A
git commit -m "Test: Sync trigger"
git push

# Option B: Manueller Trigger
# Gehe zu: Actions → "Trigger Research Sync" → "Run workflow"
```

**Check Sync Status:**
- vibe-agency Actions: https://github.com/kimeisele/vibe-agency/actions
- vibe-research Actions: https://github.com/kimeisele/vibe-research/actions

## Troubleshooting

### "Bad credentials" Error
→ Token fehlt oder ist falsch. Wiederhole Schritt 1-2.

### Sync läuft nicht
- Check ob Workflow aktiv ist: `.github/workflows/trigger-research-sync.yml` existiert
- Check ob Änderungen in triggernden Pfaden: `agency_os/`, `handlers/`, etc.
- Check Actions Tab für Error-Logs

### Token abgelaufen
→ Erstelle neuen Token (Schritt 1-2 wiederholen)

## Was NICHT synced wird

- Tests, Dokumentation (nur in vibe-agency)
- Workspaces (projektspezifisch)
- `.env` Files (Security)
- Git History (nur aktuelle Files)

## Erwartetes Ergebnis

Nach erfolgreichem Sync siehst du in vibe-research:
- Neue Commits mit Prefix "🔄 Auto-sync from vibe-agency"
- Aktualisierte `agency_os/` Struktur
- Synced `core_orchestrator.py`, `handlers/`, etc.
