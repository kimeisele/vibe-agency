# 🔐 Token Setup Verifizierung

## Quick Check - Öffne diese URLs:

### 1. Workflow-Runs in vibe-agency prüfen
**URL:** https://github.com/kimeisele/vibe-agency/actions/workflows/trigger-research-sync.yml

**Was du sehen solltest:**
- ✅ Grüner Haken: Token funktioniert, Trigger wurde gesendet
- ❌ Roter Cross: Token fehlt oder ist falsch
- 🟡 Gelb/Pending: Workflow läuft gerade

### 2. Sync-Ergebnisse in vibe-research prüfen
**URL:** https://github.com/kimeisele/vibe-research/actions

**Was du sehen solltest:**
- ✅ Workflow "Auto-sync from vibe-agency" wurde getriggert
- Neue Commits mit "🔄 Auto-sync from vibe-agency" Prefix

---

## 🧪 Test-Optionen

### Option A: Workflow Status checken (empfohlen)
1. Öffne: https://github.com/kimeisele/vibe-agency/actions
2. Suche nach "Trigger Research Sync" Workflow
3. Check den letzten Run vom Commit "Test: Sync trigger"

**Wenn grün (✅):**
→ Token ist korrekt eingerichtet!

**Wenn rot (❌) mit "Bad credentials":**
→ Token fehlt oder ist falsch. Neue Schritte:
  - Gehe zu: https://github.com/kimeisele/vibe-agency/settings/secrets/actions
  - Check ob `RESEARCH_SYNC_TOKEN` existiert
  - Falls nicht: Erstelle Token (siehe SYNC_TO_RESEARCH.md)

### Option B: Manueller Trigger (wenn du sicher gehen willst)
1. Öffne: https://github.com/kimeisele/vibe-agency/actions/workflows/trigger-research-sync.yml
2. Click "Run workflow" Button (rechts oben)
3. Branch: main
4. Click grüner "Run workflow" Button
5. Warte 10-30 Sekunden
6. Check ob der Run erfolgreich ist (grün)

### Option C: Neuer Push-Test
```bash
# Auf main branch wechseln
git checkout main
git pull origin main

# Kleine Änderung machen
echo "# Token test $(date)" >> agency_os/README.md
git add agency_os/README.md
git commit -m "Test: Verify token setup"
git push origin main

# Dann URLs aus Option A checken
```

---

## 📊 Erwartetes Ergebnis (wenn alles klappt)

### In vibe-agency Actions:
```
Trigger Research Sync
✅ Send sync trigger to vibe-research
✅ Log sync trigger
```

### In vibe-research Actions:
```
Auto-sync from vibe-agency
✅ Checkout code
✅ Copy files from vibe-agency
✅ Commit and push changes
```

---

## 🚨 Häufige Probleme

### "Error 404: Not Found"
→ Token hat nicht genug Rechte
→ Lösung: Token braucht `repo` scope

### "Error 401: Bad credentials"
→ Token nicht als Secret hinterlegt oder falsch
→ Lösung: Check https://github.com/kimeisele/vibe-agency/settings/secrets/actions

### Workflow läuft nicht
→ Änderungen nicht in triggernden Pfaden (agency_os/, handlers/, etc.)
→ Lösung: Ändere Datei in einem der konfigurierten Pfade

---

## ✅ Token ist korrekt eingerichtet, wenn:

- [ ] Workflow "Trigger Research Sync" erscheint in Actions
- [ ] Letzter Run ist grün (✅)
- [ ] Log zeigt "✅ Sync trigger sent to vibe-research"
- [ ] In vibe-research gibt es neue Sync-Commits
