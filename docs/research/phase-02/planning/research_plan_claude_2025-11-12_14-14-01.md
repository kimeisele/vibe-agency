# 🔬 RESEARCH-PLÄNE FÜR FEHLENDE FRAMEWORKS

---

## RESEARCH #1: CODE GENERATION FRAMEWORK

**Ziel:** Systematisches Framework für architecture.json → lauffähiger Code

**Research-Fragen:**

### 1. Constraints (FAE-ähnlich)
- Welche technischen Constraints gelten für Code-Generierung?
- Was kann AI NICHT generieren (z.B. Legacy-Integration)?
- Welche Code-Muster führen zu Halluzinationen?
- Welche Sprach-/Framework-Kombinationen sind problematisch?

### 2. Dependencies (FDG-ähnlich)
- Welche Inputs braucht Code-Gen? (architecture.json + was noch?)
- Welche Context-Informationen sind kritisch? (existing code, libs, APIs)
- Welche Artefakte werden erzeugt? (source code, tests, docs)
- Welche Abhängigkeiten zwischen Code-Komponenten?

### 3. Quality Rules (APCE-ähnlich)
- Wie misst man Code-Qualität automatisch?
- Welche Metriken für "good enough for v1.0"?
- Wann ist Code "ready for QA"?
- Wie priorisiert man Code-Generierung? (Core first, Extensions second)

**Output-Format:**
- `CODE_GEN_constraints.yaml`
- `CODE_GEN_dependencies.yaml`
- `CODE_GEN_quality_rules.yaml`

---

## RESEARCH #2: QA/TESTING FRAMEWORK

**Ziel:** Systematisches Framework für Code → Validated Product

**Research-Fragen:**

### 1. Constraints (FAE-ähnlich)
- Was kann NICHT automatisch getestet werden?
- Welche Test-Typen sind für v1.0 unrealistisch? (Load, Security, Penetration)
- Welche Testing-Tools haben welche Limits?
- Wann MUSS ein Mensch testen? (HITL-Constraints)

### 2. Dependencies (FDG-ähnlich)
- Welche Test-Typen brauchen welche Inputs?
- Test-Pyramide: Unit → Integration → E2E (Dependencies?)
- Welche Tests müssen in welcher Reihenfolge laufen?
- Was braucht QA vom Code-Gen-Framework?

### 3. Quality Rules (APCE-ähnlich)
- Welche Test-Coverage für v1.0 ausreichend?
- Wie priorisiert man Tests? (Critical Path zuerst)
- Wann ist "QA approved"? (Pass-Kriterien)
- Wie handled man flaky tests?

**Output-Format:**
- `QA_constraints.yaml`
- `QA_dependencies.yaml`
- `QA_quality_rules.yaml`

---

## RESEARCH #3: DEPLOYMENT FRAMEWORK

**Ziel:** Systematisches Framework für Validated Code → Production

**Research-Fragen:**

### 1. Constraints (FAE-ähnlich)
- Welche Deployment-Strategien sind für v1.0 unrealistisch? (Blue-Green, Canary)
- Welche Infrastruktur-Komplexität ist zu hoch?
- Was kann NICHT automatisiert werden? (DNS, Certs, Compliance)
- Welche Cloud-Provider haben welche Limits?

### 2. Dependencies (FDG-ähnlich)
- Was braucht Deployment vom QA-Framework? (approval report)
- Welche Deployment-Steps in welcher Reihenfolge?
- Rollback-Dependencies?
- Monitoring/Observability-Requirements?

### 3. Quality Rules (APCE-ähnlich)
- Wann ist "deployment successful"?
- Welche Health-Checks für v1.0?
- Wie priorisiert man Deployment-Schritte?
- Wann Rollback triggern?

**Output-Format:**
- `DEPLOY_constraints.yaml`
- `DEPLOY_dependencies.yaml`
- `DEPLOY_quality_rules.yaml`

---

## RESEARCH #4: MAINTENANCE/BUG-TRIAGE FRAMEWORK

**Ziel:** Systematisches Framework für Production Issues → Fixes

**Research-Fragen:**

### 1. Constraints (FAE-ähnlich)
- Welche Bugs können NICHT automatisch getriagt werden?
- Welche Bug-Typen brauchen HITL? (Security, Data Loss)
- Was kann AI NICHT fixen? (Architecture changes, DB migrations)
- Welche Bug-Severity-Levels existieren?

### 2. Dependencies (FDG-ähnlich)
- Was braucht Bug-Triage? (logs, monitoring, user reports)
- Wie wird Bug → Feature Request → Planning Loop geschlossen?
- Welche Bug-Types brauchen welche Fix-Workflows?
- Hotfix vs. Regular Fix Dependencies?

### 3. Quality Rules (APCE-ähnlich)
- Wie priorisiert man Bugs? (Severity × Impact)
- Wann ist ein Bug "fixed"? (Tests passed + deployed)
- SLA-Targets für Bug-Response? (Critical: 1h, Major: 1d, Minor: 1w)
- Wann eskaliert man zum Menschen?

**Output-Format:**
- `MAINTENANCE_constraints.yaml`
- `MAINTENANCE_dependencies.yaml`
- `MAINTENANCE_triage_rules.yaml`

---

## RESEARCH #5: ORCHESTRATION META-FRAMEWORK

**Ziel:** Wie verbindet man alle Frameworks?

**Research-Fragen:**

### 1. Workflow Design
- Wie modelliert man SDLC als State Machine?
- Welche States? (PLANNING → CODING → TESTING → DEPLOYED → MAINTENANCE)
- Welche Transitions? (QA approved → Trigger Deploy)
- Error-Handling? (Test failed → Back to Coding)

### 2. Data Contracts
- JSON-Schema für project_manifest.json finalisieren
- JSON-Schemas für alle Artefakte (code_gen_spec, test_plan, qa_report, deploy_receipt, bug_report)
- Versionierung-Strategy?
- Schema-Evolution?

### 3. Orchestrator Selection
- Temporal vs. Prefect vs. GitHub Actions vs. Custom?
- Trade-offs für v1.0?
- Welche Features sind kritisch? (Durable execution, HITL-support, Observability)
- Setup-Komplexität vs. Capabilities?

**Output-Format:**
- `ORCHESTRATION_workflow_design.yaml`
- `ORCHESTRATION_data_contracts.yaml`
- `ORCHESTRATION_technology_comparison.yaml`

---

## 📋 ZUSAMMENFASSUNG

**5 Research-Pläne:**
1. Code Generation (3 YAMLs)
2. QA/Testing (3 YAMLs)
3. Deployment (3 YAMLs)
4. Maintenance (3 YAMLs)
5. Orchestration (3 YAMLs)

**Total Output:** 15 YAMLs + Knowledge Base

**Execution:** Du leitest diese an externes Research-Team weiter.

**Sobald zurück:** Wir bauen die Frameworks (wie VIBE+GENESIS, aber für Code/QA/Deploy/Maintenance).

---

**FERTIG. Keine Fragen. Copy-paste ready.** 🚀