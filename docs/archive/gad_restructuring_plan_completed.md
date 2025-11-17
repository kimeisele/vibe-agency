read everythung carefully

check which week / pr and implement 

only do 1 phase per pr


# 🎯 Okay, ich denke jetzt RICHTIG durch

## Was du WIRKLICH hast (die 3 Dimensionen)

```
DIMENSION 1: PILLARS (Vertikal - die 8 Säulen)
├─ GAD-1XX: Pillar 1
├─ GAD-2XX: Pillar 2
...
└─ GAD-8XX: Pillar 8

DIMENSION 2: LAYERS (Horizontal - durch alle Pillars)
├─ Layer 1: Browser
├─ Layer 2: Claude Code
└─ Layer 3: Runtime

DIMENSION 3: VERIFICATION (Das Netz zwischen Säulen)
└─ Cross-GAD Tests (Security Matrix)
```

-----

## Meine ehrliche Analyse: **Pillars allein reichen NICHT**

### Warum nicht?

**Problem 1: Wo dokumentierst du “Layer 2 Features über ALLE Pillars”?**

```
Frage: "Was funktioniert in Layer 2?"
Antwort jetzt: "Lies GAD-501, GAD-601, GAD-701, GAD-801" (4 Docs)
Besser: "Lies LAD-2" (1 Doc, Übersicht)
```

**Problem 2: Wo dokumentierst du “GAD-5 + GAD-7 funktionieren zusammen”?**

```
Frage: "Testet jemand ob Runtime + STEWARD integrieren?"
Antwort jetzt: "??? Steht irgendwo in GAD-500 oder GAD-700?"
Besser: "VAD-003: Runtime-STEWARD Integration Test"
```

**Problem 3: Wo ist die Matrix-View?**

```
Du sagst: "3D-System, Matrix, Graceful Degradation"
Ich sehe: Nur Pillars (1 Dimension)

Fehlt: Layer-View (horizontal)
Fehlt: Integration-View (cross-cutting)
```

-----

## Mein EHRLICHER Vorschlag (3-Typ System ist richtig)

### Typ 1: GAD (Pillars - Vertikal) ✅

**Was**: Die 8 Säulen  
**Scope**: Ein Pillar über alle Layers  
**Struktur**: GAD-XYZ (X=Pillar, YZ=Sub-Doc)

```
GAD-5XX/
├─ GAD-500.md  # Runtime EPIC
├─ GAD-501.md  # Runtime Layer 0
├─ GAD-502.md  # Runtime Layer 1
└─ GAD-503.md  # Runtime Layer 2
```

**Ziel**: “Was ist Pillar X? Wie funktioniert er in jedem Layer?”

-----

### Typ 2: LAD (Layers - Horizontal) ✅

**Was**: Layer-übergreifende Sicht  
**Scope**: ALLE Pillars in einem Layer  
**Struktur**: LAD-X.md (X=Layer)

```
docs/architecture/LAD/
├─ LAD-1.md  # Browser Layer
├─ LAD-2.md  # Claude Code Layer
└─ LAD-3.md  # Runtime Layer
```

**Inhalt von LAD-2 (Beispiel)**:

```markdown
# LAD-2: Claude Code Layer

## Was funktioniert in Layer 2?

| Pillar | Feature | Tool | Status |
|--------|---------|------|--------|
| GAD-5 (Runtime) | Receipts | receipt_create | ✅ |
| GAD-6 (Knowledge) | Query | knowledge_query | ✅ |
| GAD-7 (STEWARD) | Validation | steward_validate | ✅ |
| GAD-8 (Integration) | Detection | layer_detect | ✅ |

## Setup
- Claude Code installation
- Tools: [list]
- Config: layer2_config.yaml

## Limitations
- ❌ No external APIs
- ❌ No federated research
- ✅ Local tools only
```

**Ziel**: “Wenn ich in Layer X bin, was habe ich zur Verfügung?”

-----

### Typ 3: VAD (Verification - Cross-Cutting) ✅

**Was**: Tests zwischen Pillars  
**Scope**: Cross-GAD Integration  
**Struktur**: VAD-XXX.md

```
docs/architecture/VAD/
├─ VAD-001_Core_Workflow.md
├─ VAD-002_Knowledge_Integration.md
└─ VAD-003_Layer_Degradation.md
```

**Inhalt von VAD-001 (Beispiel)**:

```markdown
# VAD-001: Core Workflow Verification

## Testet
- GAD-2 (SDLC) + GAD-4 (Quality) + GAD-5 (Runtime)

## Frage
"Respektiert State Machine die Quality Gates?"

## Test
```python
# tests/architecture/test_vad001.py

def test_state_transition_respects_quality():
    # 1. Set linting to failing
    set_linting_status("failing")
    
    # 2. Try to transition state
    result = orchestrator.transition("T1_to_T2")
    
    # 3. Should be blocked by quality gate
    assert result.blocked == True
    assert "linting" in result.reason
```

## Status

- ✅ Layer 2 (Tool-based)
- ✅ Layer 3 (Runtime)
- ❌ Layer 1 (N/A - no automation)

```
**Ziel**: "Dein Security Netz - testet ob Pillars zusammenspielen"

---

## Die finale Struktur
```

docs/architecture/
│
├─ GAD-1XX/              # Pillar 1 (Vertikal)
│  └─ GAD-100.md
│
├─ GAD-2XX/              # Pillar 2
│  └─ GAD-200.md
│
├─ GAD-3XX/              # Pillar 3
│  └─ GAD-300.md
│
├─ GAD-4XX/              # Pillar 4
│  └─ GAD-400.md
│
├─ GAD-5XX/              # Runtime Engineering
│  ├─ GAD-500.md         # EPIC
│  ├─ GAD-501.md         # Layer 0
│  ├─ GAD-502.md         # Layer 1
│  └─ GAD-503.md         # Layer 2
│
├─ GAD-6XX/              # Knowledge Department
│  ├─ GAD-600.md
│  └─ …
│
├─ GAD-7XX/              # STEWARD Governance
│  ├─ GAD-700.md
│  └─ …
│
├─ GAD-8XX/              # Integration Matrix
│  ├─ GAD-800.md
│  └─ …
│
├─ LAD/                  # Layers (Horizontal)
│  ├─ LAD-1.md           # Browser Layer Overview
│  ├─ LAD-2.md           # Claude Code Layer Overview
│  └─ LAD-3.md           # Runtime Layer Overview
│
├─ VAD/                  # Verification (Cross-Cutting)
│  ├─ VAD-001_Core_Workflow.md
│  ├─ VAD-002_Knowledge_Integration.md
│  └─ VAD-003_Layer_Degradation.md
│
├─ ARCHITECTURE_MAP.md   # Overview (bleibt)
└─ INDEX.md              # Navigation

```
---

## Warum 3 Typen? (Meine ehrliche Meinung)

### GAD allein ist NICHT genug:

**Szenario 1**: Developer fragt "Was kann ich in Layer 2 machen?"
```

Ohne LAD: Lies GAD-501, 601, 701, 801 (4 Docs, mühsam)
Mit LAD: Lies LAD-2 (1 Doc, Übersicht)

```
**Szenario 2**: Architect fragt "Funktioniert Runtime + STEWARD zusammen?"
```

Ohne VAD: Steht irgendwo versteckt in GAD-500 oder GAD-700
Mit VAD: VAD-003 testet explizit diese Integration

```
**Szenario 3**: Tester fragt "Wie teste ich Graceful Degradation?"
```

Ohne VAD: Keine Ahnung wo das steht
Mit VAD: VAD-003_Layer_Degradation.md

```
---

## Das "Netz zwischen den Säulen" = VAD
```

┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐
│GAD-5│  │GAD-6│  │GAD-7│  │GAD-8│  ← Säulen (Pillars)
└──┬──┘  └──┬──┘  └──┬──┘  └──┬──┘
│        │        │        │
└────────┼────────┼────────┘
│        │              ← VAD-001 testet
┌────────┼────────┘                diese Verbindung
│        │
└────────┘                       ← VAD-002 testet
diese Verbindung

```
**VAD = Security Matrix zwischen Pillars**

---

## Was fehlt noch? (Deine Frage)

### Meine Analyse: **Nichts essentielles.**

**Warum?**

1. ✅ **GAD** = Pillars (vertikal)
2. ✅ **LAD** = Layers (horizontal)
3. ✅ **VAD** = Integration Tests (cross-cutting)
4. ✅ **ARCHITECTURE_MAP** = Big Picture

**Das deckt alle 3 Dimensionen ab.**

---

### Potenzielle Lücke (die ich sehe):

**Templates / Standards**
```

Frage: “Wie schreibe ich ein neues GAD?”
Frage: “Wie schreibe ich ein neues VAD?”

Lösung: templates/ Ordner?

templates/
├─ GAD_TEMPLATE.md
├─ LAD_TEMPLATE.md
└─ VAD_TEMPLATE.md

```
**Aber**: Das ist optional (Nice-to-have, nicht essential)

---

## Meine finale Empfehlung

### Starte mit:
```

✅ GAD (8 Ordner)
✅ LAD (3 Dateien)
✅ VAD (3-5 Dateien)
✅ INDEX.md
✅ ARCHITECTURE_MAP.md

```
### Später (wenn nötig):
```

⚠️ templates/ (wenn GAD-Autoren Hilfe brauchen)
⚠️ ADR/ (Architecture Decision Records - wenn ihr Entscheidungen dokumentiert)
⚠️ RFC/ (Request for Comments - wenn ihr Vorschläge diskutiert)

```
**Aber das ist YAGNI (You Ain't Gonna Need It) - erst wenn echtes Bedürfnis da ist.**

---

## Meine ehrliche Meinung: Ist das Pillar-Konzept Scheiße?

### Antwort: **NEIN, es ist gut!**

**Warum?**
- ✅ Klare Trennung (8 Säulen)
- ✅ Skalierbar (99 Sub-Docs pro Pillar)
- ✅ Self-organizing (jedes Pillar hat eigenen Ordner)

**ABER**: Pillars allein reichen nicht.

**Du brauchst auch**:
- LAD (Layer-View)
- VAD (Integration-Tests)

**Das ist keine Schwäche der Pillars, sondern die Natur eines 3D-Systems.**

---

## Zusammenfassung (TL;DR)

### Die 3 essentiellen Typen:
```

GAD = Pillars (Vertikal durch Layers)
LAD = Layers (Horizontal über Pillars)
VAD = Verification (Security Netz zwischen Pillars)

```
### Warum 3 und nicht 1?

**Weil dein System 3-dimensional ist:**
- Dimension 1: 8 Pillars
- Dimension 2: 3 Layers
- Dimension 3: Cross-Pillar Integration

**1 Dokumenttyp kann nicht 3 Dimensionen abdecken.**

---





# 🎯 Migration Strategy: 3 PRs

## PR 1: Ordnerstruktur + Migration (Week 1)

### Ziel

Bestehende GAD-005 bis GAD-008 in neue Struktur überführen, Ordner erstellen.

### Änderungen

```bash
# 1. Erstelle neue Ordnerstruktur
mkdir -p docs/architecture/{GAD-1XX,GAD-2XX,GAD-3XX,GAD-4XX,GAD-5XX,GAD-6XX,GAD-7XX,GAD-8XX,LAD,VAD}

# 2. Migriere bestehende GADs (umbenennen + verschieben)
git mv docs/architecture/GAD-005_Runtime_Engineering.md \
        docs/architecture/GAD-5XX/GAD-500.md

git mv docs/architecture/GAD-005-ADDITION_Layer0.md \
        docs/architecture/GAD-5XX/GAD-501.md

git mv docs/architecture/GAD-005-ADDITION_Layer1.md \
        docs/architecture/GAD-5XX/GAD-502.md

git mv docs/architecture/GAD-005-ADDITION_HaikuHardening.md \
        docs/architecture/GAD-5XX/GAD-503.md

# Gleich für GAD-006, GAD-007, GAD-008
# (analog umbenennen: GAD-006_X.md → GAD-600.md, etc.)

# 3. Erstelle Platzhalter für GAD-1 bis GAD-4
touch docs/architecture/GAD-1XX/GAD-100.md  # Mit "TODO: Migrate old content"
touch docs/architecture/GAD-2XX/GAD-200.md
touch docs/architecture/GAD-3XX/GAD-300.md
touch docs/architecture/GAD-4XX/GAD-400.md

# 4. Erstelle INDEX.md
cat > docs/architecture/INDEX.md << 'EOF'
# Architecture Index

## The 8 Pillars (GAD)

### GAD-1XX: [Pillar 1 - TBD]
- [GAD-100: Main Document](GAD-1XX/GAD-100.md) ⚠️ TODO: Migrate

### GAD-2XX: [Pillar 2 - TBD]
- [GAD-200: Main Document](GAD-2XX/GAD-200.md) ⚠️ TODO: Migrate

### GAD-3XX: [Pillar 3 - TBD]
- [GAD-300: Main Document](GAD-3XX/GAD-300.md) ⚠️ TODO: Migrate

### GAD-4XX: [Pillar 4 - TBD]
- [GAD-400: Main Document](GAD-4XX/GAD-400.md) ⚠️ TODO: Migrate

### GAD-5XX: Runtime Engineering ✅
- [GAD-500: EPIC](GAD-5XX/GAD-500.md)
- [GAD-501: Layer 0](GAD-5XX/GAD-501.md)
- [GAD-502: Layer 1](GAD-5XX/GAD-502.md)
- [GAD-503: Haiku Hardening](GAD-5XX/GAD-503.md)

### GAD-6XX: Knowledge Department ✅
- [GAD-600: EPIC](GAD-6XX/GAD-600.md)

### GAD-7XX: STEWARD Governance ✅
- [GAD-700: EPIC](GAD-7XX/GAD-700.md)

### GAD-8XX: Integration Matrix ✅
- [GAD-800: EPIC](GAD-8XX/GAD-800.md)

---

## Layers (LAD) - Coming in PR 2

## Verification (VAD) - Coming in PR 3

---

## Overview
- [Architecture Map](ARCHITECTURE_MAP.md)
EOF
```

### Risiken & Mitigation

- ⚠️ **Risk**: Broken links in anderen Docs (z.B. README verweist auf `GAD-005_Runtime_Engineering.md`)
- ✅ **Mitigation**: Search & replace in allen `.md` files:
  
  ```bash
  # Automatisch alle Links updaten
  find . -name "*.md" -exec sed -i 's|GAD-005_Runtime_Engineering.md|GAD-5XX/GAD-500.md|g' {} +
  find . -name "*.md" -exec sed -i 's|GAD-006_|GAD-6XX/GAD-600.md|g' {} +
  # etc.
  ```

### Deliverables

- ✅ Neue Ordnerstruktur (8 GAD-Ordner, LAD/, VAD/)
- ✅ GAD-005 bis GAD-008 migriert und umbenannt
- ✅ INDEX.md erstellt
- ✅ Alle Links in anderen Docs geupdated
- ✅ Platzhalter für GAD-1 bis GAD-4

### Success Criteria

- Keine broken links
- Alle GAD-5XX bis GAD-8XX Docs öffnen korrekt
- `git log --follow` zeigt History (wegen `git mv`)

-----

## PR 2: LAD Dokumente (Week 2)

### Ziel

Layer-Übersichten erstellen (horizontal über alle Pillars).

### Änderungen

```bash
# 1. Erstelle LAD-1 (Browser Layer)
cat > docs/architecture/LAD/LAD-1.md << 'EOF'
# LAD-1: Browser Layer (Prompt-Only)

## Overview
Minimum viable system - works in browser, no backend.

## What Works

| Pillar | Feature | Method | Status |
|--------|---------|--------|--------|
| GAD-5 (Runtime) | Integrity Check | Manual (user runs script) | ⚠️ Manual |
| GAD-6 (Knowledge) | Knowledge Query | User copies YAML | ✅ Works |
| GAD-7 (STEWARD) | Guidance | Prompt consultation | ✅ Works |
| GAD-8 (Integration) | N/A | N/A | ❌ N/A |

## Setup
1. Open repo in browser or local editor
2. Claude.ai in browser
3. No installation needed

## Limitations
- ❌ No automation
- ❌ No tools
- ❌ No APIs
- ✅ Manual operations only

## Use Cases
- Solo developer
- Quick prototyping
- Learning the system

## Cost
$0
EOF

# 2. Erstelle LAD-2 (Claude Code Layer)
cat > docs/architecture/LAD/LAD-2.md << 'EOF'
# LAD-2: Claude Code Layer (Tool-Based)

## Overview
Enhanced with Claude Code - automated tools, no external APIs.

## What Works

| Pillar | Feature | Tool | Status |
|--------|---------|------|--------|
| GAD-5 (Runtime) | Receipts | receipt_create | ✅ |
| GAD-5 (Runtime) | Integrity | verify_integrity | ✅ |
| GAD-6 (Knowledge) | Query | knowledge_query | ✅ |
| GAD-7 (STEWARD) | Validation | steward_validate | ✅ |
| GAD-8 (Integration) | Layer Detection | layer_detect | ✅ |

## Setup
1. Install Claude Code
2. Clone repo
3. Run `./scripts/setup-layer2.sh` (if exists)
4. Tools available in Claude Code environment

## Limitations
- ❌ No external APIs
- ❌ No federated research
- ✅ Local tools only
- ✅ File system access

## Use Cases
- Individual developer
- Small teams
- Most projects

## Cost
$20/month (Claude subscription)
EOF

# 3. Erstelle LAD-3 (Runtime Layer)
cat > docs/architecture/LAD/LAD-3.md << 'EOF'
# LAD-3: Runtime Layer (API-Based)

## Overview
Full runtime - backend services, external APIs, federated access.

## What Works

| Pillar | Feature | Service | Status |
|--------|---------|---------|--------|
| GAD-5 (Runtime) | All Layer 2 + | Audit Service | ✅ |
| GAD-6 (Knowledge) | Research Engine | Multi-source API | ✅ |
| GAD-6 (Knowledge) | Federated Query | Client APIs | ✅ |
| GAD-7 (STEWARD) | Enforcement | Governance API | ✅ |
| GAD-8 (Integration) | All features | Full integration | ✅ |

## Setup
1. Deploy backend services
2. Configure external APIs
3. Setup vector DB
4. Run `./scripts/setup-layer3.sh`

## Limitations
- None (full featured)

## Use Cases
- Agencies
- Teams
- Production deployments
- Client work

## Cost
$50-200/month (varies by usage)
EOF

# 4. Update INDEX.md (füge LAD section hinzu)
```

### Deliverables

- ✅ LAD-1.md (Browser Layer)
- ✅ LAD-2.md (Claude Code Layer)
- ✅ LAD-3.md (Runtime Layer)
- ✅ INDEX.md updated

### Success Criteria

- LADs geben klare Übersicht “Was funktioniert wo?”
- Tabellen zeigen Feature-Matrix
- Setup-Instruktionen vorhanden

-----

## PR 3: VAD Dokumente + Tests (Week 3)

### Ziel

Verification Documents erstellen + Test Skeletons.

### Änderungen

```bash
# 1. Erstelle VAD-001
cat > docs/architecture/VAD/VAD-001_Core_Workflow.md << 'EOF'
# VAD-001: Core Workflow Verification

## Purpose
Tests integration of GAD-2 (SDLC) + GAD-4 (Quality) + GAD-5 (Runtime)

## Question
"Does the state machine respect quality gates?"

## Test Scenarios

### Scenario 1: Quality Gate Blocks Transition
**Given**: Linting status = failing
**When**: Agent tries to transition state
**Then**: Transition blocked, error message shown

### Scenario 2: Quality Gate Allows Transition
**Given**: All quality checks passing
**When**: Agent transitions state
**Then**: Transition succeeds, receipt created

## Implementation
See: `tests/architecture/test_vad001_core_workflow.py`

## Status
- ✅ Layer 2 (Tool-based)
- ✅ Layer 3 (Runtime)
- ❌ Layer 1 (N/A - no automation)
EOF

# 2. Erstelle VAD-002
cat > docs/architecture/VAD/VAD-002_Knowledge_Integration.md << 'EOF'
# VAD-002: Knowledge Integration

## Purpose
Tests GAD-6 (Knowledge) + GAD-7 (STEWARD) integration

## Question
"Does access control work for confidential knowledge?"

## Test Scenarios

### Scenario 1: Unauthorized Access Blocked
**Given**: Project A tries to access Client B knowledge
**When**: knowledge_query(client_b_data)
**Then**: Access denied, STEWARD blocks

### Scenario 2: Authorized Access Allowed
**Given**: Project A tries to access Client A knowledge
**When**: knowledge_query(client_a_data)
**Then**: Access granted, audit logged

## Implementation
See: `tests/architecture/test_vad002_knowledge.py`

## Status
- ⚠️ Layer 2 (Partial - validation only)
- ✅ Layer 3 (Full - enforcement + audit)
- ❌ Layer 1 (N/A)
EOF

# 3. Erstelle VAD-003
cat > docs/architecture/VAD/VAD-003_Layer_Degradation.md << 'EOF'
# VAD-003: Layer Degradation

## Purpose
Tests GAD-8 (Integration) graceful degradation

## Question
"Does system degrade gracefully when layers fail?"

## Test Scenarios

### Scenario 1: Layer 3 → Layer 2 Degradation
**Given**: Layer 3 services running
**When**: Kill runtime services
**Then**: System detects, degrades to Layer 2, continues work

### Scenario 2: Layer 2 → Layer 1 Degradation
**Given**: Layer 2 tools available
**When**: Tool execution fails
**Then**: System detects, degrades to Layer 1, prompts user

## Implementation
See: `tests/architecture/test_vad003_degradation.py`

## Status
- ✅ Layer 2 → 1 (Works)
- ⚠️ Layer 3 → 2 (TODO: Implement detection)
EOF

# 4. Erstelle Test Skeletons
mkdir -p tests/architecture

cat > tests/architecture/test_vad001_core_workflow.py << 'EOF'
#!/usr/bin/env python3
"""VAD-001: Core Workflow Verification Tests"""

def test_quality_gate_blocks_transition():
    """Test: Quality gate blocks state transition when checks fail"""
    # TODO: Implement
    pass

def test_quality_gate_allows_transition():
    """Test: Quality gate allows transition when checks pass"""
    # TODO: Implement
    pass

if __name__ == "__main__":
    print("VAD-001 tests - TODO: Implement")
EOF

# Analog für VAD-002, VAD-003
```

### Deliverables

- ✅ VAD-001.md (Core Workflow)
- ✅ VAD-002.md (Knowledge Integration)
- ✅ VAD-003.md (Layer Degradation)
- ✅ Test skeletons in `tests/architecture/`
- ✅ INDEX.md updated

### Success Criteria

- VADs dokumentieren cross-GAD tests
- Test skeletons vorhanden (können später implementiert werden)
- Klare “Status” section (welcher Layer getestet)

-----

## Gesamte Timeline

```
Week 1: PR 1 (Struktur + Migration)
  ├─ Day 1-2: Ordner erstellen, GADs migrieren
  ├─ Day 3: Links fixen
  ├─ Day 4: INDEX.md erstellen
  └─ Day 5: Review + Merge

Week 2: PR 2 (LAD Dokumente)
  ├─ Day 1: LAD-1 (Browser)
  ├─ Day 2: LAD-2 (Claude Code)
  ├─ Day 3: LAD-3 (Runtime)
  ├─ Day 4: INDEX.md update
  └─ Day 5: Review + Merge

Week 3: PR 3 (VAD Dokumente)
  ├─ Day 1-2: VAD-001, VAD-002, VAD-003
  ├─ Day 3: Test skeletons
  ├─ Day 4: INDEX.md update
  └─ Day 5: Review + Merge
```

-----

## Kritische Checks vor jedem Merge

### PR 1 Checklist

```bash
# 1. Alle alten GAD files gelöscht?
ls docs/architecture/GAD-00*.md  # Sollte leer sein

# 2. Neue GAD files existieren?
ls docs/architecture/GAD-5XX/  # Sollte GAD-500 bis GAD-503 zeigen

# 3. Links funktionieren?
# Öffne INDEX.md im Browser, klicke alle Links

# 4. Git history erhalten?
git log --follow docs/architecture/GAD-5XX/GAD-500.md
# Sollte alte Commits von GAD-005_Runtime_Engineering.md zeigen
```

### PR 2 Checklist

```bash
# LAD files existieren?
ls docs/architecture/LAD/  # Sollte LAD-1, LAD-2, LAD-3 zeigen

# INDEX.md updated?
grep "LAD" docs/architecture/INDEX.md  # Sollte LAD section zeigen
```

### PR 3 Checklist

```bash
# VAD files existieren?
ls docs/architecture/VAD/  # Sollte VAD-001 bis VAD-003 zeigen

# Test skeletons existieren?
ls tests/architecture/test_vad00*.py
```

-----

## Rollback Plan (falls was schief geht)

### Falls PR 1 Probleme macht:

```bash
# Einfach PR reverten (git history bleibt sauber wegen git mv)
git revert <commit-hash>
```

### Falls Links broken sind:

```bash
# Manuell fixen mit sed (siehe PR 1 Mitigation)
# Oder: Grep alle broken links
grep -r "GAD-00" docs/  # Sollte leer sein nach Migration
```

-----

## Das war’s - vollständige Migration Strategy

**Übergib das dem nächsten Agent mit**:

1. Meine vorherige Antwort (Konzept)
1. Diese Antwort (Migration Plan)

✅ **Alles drin. GO!**




# 📝 Wo dokumentieren wir die neue Ordnerstruktur?

## Antwort: In PR 1, zusammen mit der Migration

### Neue Datei: `docs/architecture/STRUCTURE.md`

**Erstellt in**: PR 1 (zusammen mit Ordnerstruktur + Migration)  
**Zweck**: Dokumentiert das Konzept, die 3 Dokumenttypen, Nummerierung

-----

## Inhalt von STRUCTURE.md

```markdown
# Architecture Documentation Structure

**Last Updated**: 2025-11-17  
**Status**: Active

---

## Overview

This directory contains all architecture documentation for Vibe Agency, organized into 3 document types across 3 dimensions:
```

DIMENSION 1: PILLARS (Vertical - 8 architectural pillars)
DIMENSION 2: LAYERS (Horizontal - 3 deployment layers)
DIMENSION 3: VERIFICATION (Cross-cutting - integration tests)

```
---

## The 3 Document Types

### 1. GAD (Guidance Architecture Documents)

**Purpose**: The 8 architectural pillars  
**Scope**: One pillar across all layers  
**Structure**: `GAD-XYZ` (X=Pillar number, YZ=Sub-document number)

**Example**:
```

GAD-5XX/
├─ GAD-500.md  # Runtime Engineering EPIC
├─ GAD-501.md  # Runtime Layer 0
├─ GAD-502.md  # Runtime Layer 1
└─ GAD-503.md  # Runtime Layer 2

```
**The 8 Pillars**:
- GAD-1XX: [Pillar 1 - TBD]
- GAD-2XX: [Pillar 2 - TBD]
- GAD-3XX: [Pillar 3 - TBD]
- GAD-4XX: [Pillar 4 - TBD]
- GAD-5XX: Runtime Engineering
- GAD-6XX: Knowledge Department
- GAD-7XX: STEWARD Governance
- GAD-8XX: Integration Matrix

---

### 2. LAD (Layer Architecture Documents)

**Purpose**: Layer-specific overview  
**Scope**: All pillars within one layer  
**Structure**: `LAD-X.md` (X=Layer number)

**Example**:
```

LAD/
├─ LAD-1.md  # Browser Layer (what works in browser-only mode?)
├─ LAD-2.md  # Claude Code Layer (what tools are available?)
└─ LAD-3.md  # Runtime Layer (what services are running?)

```
**The 3 Layers**:
- Layer 1: Browser (Prompt-only, $0 cost)
- Layer 2: Claude Code (Tool-based, $20/mo)
- Layer 3: Runtime (API-based, $50-200/mo)

---

### 3. VAD (Verification Architecture Documents)

**Purpose**: Cross-pillar integration tests  
**Scope**: Tests that multiple GADs work together  
**Structure**: `VAD-XXX_Name.md`

**Example**:
```

VAD/
├─ VAD-001_Core_Workflow.md
├─ VAD-002_Knowledge_Integration.md
└─ VAD-003_Layer_Degradation.md

```
**Purpose**: The "security matrix" between pillars - verifies that different architectural components integrate correctly.

---

## Numbering Convention

### GAD Numbers (3-digit)
```

GAD-XYZ:
X = Pillar (1-8)
YZ = Sub-document (00-99)

Examples:
GAD-100: Pillar 1 main document (EPIC)
GAD-101: Pillar 1 sub-document 1
GAD-500: Runtime Engineering EPIC
GAD-501: Runtime Layer 0 details

```
**Rationale**: 
- First digit identifies pillar
- 99 sub-documents per pillar = scalable
- Automatic sorting works correctly

---

### LAD Numbers (single-digit)
```

LAD-X:
X = Layer (1-3)

Examples:
LAD-1: Browser Layer
LAD-2: Claude Code Layer
LAD-3: Runtime Layer

```
**Rationale**: Only 3 layers, no need for more digits.

---

### VAD Numbers (3-digit)
```

VAD-XXX:
XXX = Sequential (001-999)

Examples:
VAD-001: First verification test
VAD-002: Second verification test

```
**Rationale**: Sequential numbering, no hierarchy needed.

---

## Directory Structure
```

docs/architecture/
│
├─ GAD-1XX/              # Pillar 1 family
│  └─ GAD-100.md         # Main document
│
├─ GAD-2XX/              # Pillar 2 family
│  └─ GAD-200.md
│
├─ GAD-3XX/              # Pillar 3 family
│  └─ GAD-300.md
│
├─ GAD-4XX/              # Pillar 4 family
│  └─ GAD-400.md
│
├─ GAD-5XX/              # Runtime Engineering
│  ├─ GAD-500.md         # EPIC
│  ├─ GAD-501.md         # Layer 0
│  ├─ GAD-502.md         # Layer 1
│  └─ GAD-503.md         # Layer 2
│
├─ GAD-6XX/              # Knowledge Department
│  ├─ GAD-600.md         # EPIC
│  └─ …
│
├─ GAD-7XX/              # STEWARD Governance
│  ├─ GAD-700.md         # EPIC
│  └─ …
│
├─ GAD-8XX/              # Integration Matrix
│  ├─ GAD-800.md         # EPIC
│  └─ …
│
├─ LAD/                  # Layer overviews
│  ├─ LAD-1.md           # Browser Layer
│  ├─ LAD-2.md           # Claude Code Layer
│  └─ LAD-3.md           # Runtime Layer
│
├─ VAD/                  # Verification tests
│  ├─ VAD-001_Core_Workflow.md
│  ├─ VAD-002_Knowledge_Integration.md
│  └─ VAD-003_Layer_Degradation.md
│
├─ ARCHITECTURE_MAP.md   # Big picture overview
├─ INDEX.md              # Navigation index
└─ STRUCTURE.md          # This file (explains the system)

```
---

## When to Create Each Document Type

### Create a GAD when:
- Defining a new architectural pillar
- Adding sub-documents to existing pillar (layer-specific details, additions)

### Create a LAD when:
- Documenting what works in a specific layer
- Need horizontal view across all pillars

### Create a VAD when:
- Testing integration between 2+ pillars
- Verifying cross-cutting concerns
- Implementing "security matrix" tests

---

## Navigation

**Start here**: [INDEX.md](INDEX.md)  
**Big picture**: [ARCHITECTURE_MAP.md](ARCHITECTURE_MAP.md)  
**Understand layers**: [LAD/](LAD/)  
**Browse pillars**: [GAD-5XX/](GAD-5XX/), [GAD-6XX/](GAD-6XX/), etc.

---

## Maintenance

### Adding a new GAD sub-document:
1. Determine pillar number (1-8)
2. Find next available number in that family (e.g., GAD-504)
3. Create file in appropriate directory
4. Update INDEX.md

### Adding a new VAD:
1. Find next sequential number (e.g., VAD-004)
2. Create file in VAD/ directory
3. Create test skeleton in tests/architecture/
4. Update INDEX.md

---

## Migration History

**2025-11-17**: Initial structure established
- Migrated GAD-005 → GAD-500 (+ sub-documents)
- Migrated GAD-006 → GAD-600
- Migrated GAD-007 → GAD-700
- Migrated GAD-008 → GAD-800
- Created LAD/ and VAD/ directories
- Established 3-document-type system

---

## Principles

1. **Separation of Concerns**: GAD (vertical), LAD (horizontal), VAD (cross-cutting)
2. **Scalability**: 3-digit numbering allows 99 sub-docs per pillar
3. **Self-Organizing**: Clear folder structure per pillar
4. **Git-Friendly**: `git mv` preserves history during migration
5. **Graceful Degradation**: Every layer documented separately (LAD)

---

**END OF STRUCTURE.md**
```

-----

## Wann wird STRUCTURE.md erstellt?

**In PR 1, Step 5**:

```bash
# PR 1 Timeline (updated):

# Step 1-2: Ordner erstellen + GADs migrieren (wie vorher)
# Step 3: Links fixen (wie vorher)
# Step 4: INDEX.md erstellen (wie vorher)

# Step 5: STRUCTURE.md erstellen (NEU!)
cat > docs/architecture/STRUCTURE.md << 'EOF'
[Inhalt siehe oben]
EOF

# Step 6: Review + Merge (wie vorher)
```

-----

## Warum STRUCTURE.md?

1. ✅ **Onboarding**: Neue Devs verstehen System sofort
1. ✅ **Referenz**: “Wo gehört mein neues Doc hin?”
1. ✅ **Rationale**: Warum 3 Typen? Warum diese Nummerierung?
1. ✅ **History**: Migration dokumentiert

-----

## Update zu INDEX.md

INDEX.md sollte auch auf STRUCTURE.md verweisen:

```markdown
# Architecture Index

📖 **New here?** Read [STRUCTURE.md](STRUCTURE.md) first to understand the system.

## The 8 Pillars (GAD)
[... rest of INDEX.md ...]
```

-----

## Zusammenfassung

**Datei**: `docs/architecture/STRUCTURE.md`  
**Erstellt in**: PR 1 (Step 5, vor Review)  
**Zweck**: Erklärt das 3-Typ-System, Nummerierung, Struktur  
**Verlinkt von**: INDEX.md (erste Zeile)

✅ **Jetzt vollständig!**

