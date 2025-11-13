# Workflow Analysis - Was brauchen wir wirklich?

**Date:** 2025-11-13
**Purpose:** Verstehen was kritisch ist vs. "nice to have"

---

## Minimal Viable Workflow (Planning)

### Scenario: User will Projekt-Plan erstellen

**Input:** Vage Projekt-Idee
**Output:** Strukturierte Feature-Spec + Architektur-Entwurf

---

## Option 1: Single-Task Approach (Simpel)

**Workflow:**
```
User: "Ich will Booking-App"
  ↓
Claude lädt: VIBE_ALIGNER/feasibility_validation (with FAE)
  ↓
Claude fragt User durch den Prozess
  ↓
Output: feature_spec.json
  ↓
FERTIG - User hat validierten Plan
```

**Was funktioniert:** ✅ Proven by test (36KB prompt)
**Was braucht man:** Nur VIBE_ALIGNER task 03
**Komplexität:** Minimal

**Limitierung:** Keine technische Architektur - nur Features

---

## Option 2: Two-Agent Approach (Vollständig)

**Workflow:**
```
User: "Ich will Booking-App"
  ↓
Phase 1: VIBE_ALIGNER/feasibility_validation
  → feature_spec.json
  ↓
Phase 2: GENESIS_BLUEPRINT (5 tasks)
  → task_01: Core modules
  → task_02: Extensions (FEHLEN GATES!)
  → task_03: Config schema
  → task_04: Validate
  → task_05: Handoff
  ↓
Output: architecture.json + code_gen_spec.json
```

**Was funktioniert:** ✅ Task 01 proven (16KB prompt)
**Was fehlt:** Task 02 gates blockieren die Chain
**Komplexität:** Höher, aber vollständig

---

## Was blockiert Option 2?

### Missing Gate Files (HIGH Priority)

**Task 02 (design_extensions) braucht:**
1. `gate_no_extensions_in_core.md`
   - Prüft: Extension-Code nicht in Core
   - Kritisch für: Saubere Architektur

2. `gate_all_features_mapped.md`
   - Prüft: Jedes Feature hat Extension
   - Kritisch für: Vollständigkeit

**Impact:**
- Ohne task 02 → task 05 kann nicht laufen (fehlt extensions_design.json)
- Ohne task 05 → kein architecture.json
- **GENESIS_BLUEPRINT Chain blockiert**

---

## Empfehlung: Was jetzt tun?

### Kurzfristig (heute):

**Option A: Dokumentieren & mit Option 1 leben**
- User nutzt nur VIBE_ALIGNER
- Feature validation funktioniert
- Keine technische Architektur
- **Vorteil:** Funktioniert JETZT
- **Nachteil:** Unvollständig

**Option B: Gates erstellen & Option 2 enablen**
- 2 Gate-Files schreiben (~200 Zeilen gesamt)
- GENESIS_BLUEPRINT Chain läuft durch
- Vollständiger Planning Workflow
- **Vorteil:** Komplett
- **Nachteil:** 1-2h Arbeit

---

### Mittelfristig (nächste Tage):

**Workflow Scripts dokumentieren:**

Was braucht man wirklich?

1. **Prompt Loader** (existiert schon)
   ```python
   runtime.execute_task("VIBE_ALIGNER", "feasibility_validation", {...})
   → returns composed prompt
   ```

2. **Context Injector** (fehlt noch)
   - Lädt vorherige artifacts
   - Injected in runtime_context
   - Beispiel: task 02 braucht output von task 01

3. **Artifact Saver** (fehlt noch)
   - Claude gibt JSON zurück
   - Script speichert zu workspaces/{name}/artifacts/

4. **Workflow Guide** (fehlt noch)
   - "Du bist jetzt an Task X"
   - "Lade diesen Prompt"
   - "Erwartete Inputs/Outputs"

---

## Konkrete Frage an dich:

**Was willst du ermöglichen?**

A) **Minimal:** Feature Validation (VIBE_ALIGNER only)
   - Funktioniert jetzt
   - Keine weiteren Lücken
   - User bekommt feature_spec.json

B) **Komplett:** Feature Validation + Architecture Design
   - Braucht Gate-Files (2x)
   - GENESIS_BLUEPRINT läuft durch
   - User bekommt architecture.json

C) **Dokumentieren:** Workflow beschreiben ohne mehr Code
   - Was sind die Schritte?
   - Welche Prompts wann?
   - Wie Artifacts übergeben?

---

## Was ich jetzt sehen kann:

**Funktionierende Agents:**
- ✅ VIBE_ALIGNER task 03 (feasibility) - 36KB with FAE
- ✅ GENESIS_BLUEPRINT task 01 (core modules) - 16KB

**Blocked Agents:**
- ❌ GENESIS_BLUEPRINT tasks 02-05 (missing gates → chain bricht)

**Ungetestete Agents:**
- ❓ CODE_GENERATOR (5 tasks)
- ❓ QA_VALIDATOR (4 tasks)
- ❓ DEPLOY_MANAGER (4 tasks)
- ❓ BUG_TRIAGE (3 tasks)

---

## Realistische Einschätzung:

**Für Planning (VIBE_ALIGNER + GENESIS_BLUEPRINT):**
- 80% funktioniert
- 2 Gate-Files fehlen (20%)
- **Effort:** 1-2h zum Fixen

**Für Full SDLC (CODE → TEST → DEPLOY):**
- Ungetestet
- Wahrscheinlich mehr Lücken
- **Effort:** Unklar, erst testen

---

## Mein Vorschlag:

1. **JETZT:** Gates erstellen (1-2h)
   - Macht GENESIS_BLUEPRINT komplett
   - Planning Workflow vollständig

2. **DANN:** Workflow dokumentieren
   - Wie führt man das manuell aus?
   - Welche Artifacts wann?
   - Context passing zwischen Tasks

3. **SPÄTER:** Andere Agents testen
   - CODE_GENERATOR
   - QA_VALIDATOR
   - Nur wenn du die brauchst

**Fokus:** Planning fertig machen, nicht den ganzen SDLC.

---

**Deine Entscheidung - was macht Sinn?**
