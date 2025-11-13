# Implementierungsplan: Härtung des 01_planning_framework

Dieser Plan beschreibt die konkreten Schritte zur Implementierung der im "Fulfillment-Bericht zur Härtung des 01_planning_framework" (Datum: 2025-11-20) definierten Lösungen.

---

## 1. Aktualisierung der Wissensbasen

**Ziel:** Erstellung neuer und Aktualisierung bestehender Wissensbasen gemäß den Forschungsergebnissen.

### 1.1 Neue Wissensbasis: `PRODUCT_QUALITY_METRICS.yaml`

*   **Beschreibung:** Definiert quantifizierbare Metriken zur Kalibrierung von Produkt-Sentiment-Begriffen (z.B. "lovable", "shippable", "focused").
*   **Speicherort:** `system_steward_framework/knowledge/PRODUCT_QUALITY_METRICS.yaml`
*   **Inhalt:** Siehe "Teil 2.6 Ausgeliefertes Artefakt (Schema): PRODUCT_QUALITY_METRICS.yaml" im Fulfillment-Bericht.

### 1.2 Neue Wissensbasis: `NFR_CATALOG.yaml`

*   **Beschreibung:** Systematischer NFR-Katalog basierend auf ISO 25010 zur Erfassung nicht-funktionaler Anforderungen.
*   **Speicherort:** `system_steward_framework/knowledge/NFR_CATALOG.yaml`
*   **Inhalt:** Siehe "Teil 6.5 Ausgeliefertes Artefakt (Wissensbasis): NFR_CATALOG.yaml" im Fulfillment-Bericht.

### 1.3 Neue Governance-Richtlinie: `PROMPT_SECURITY_GUIDELINES.md`

*   **Beschreibung:** Verbindliche Governance-Richtlinie zur Minderung von Prompt-Injection-Angriffen.
*   **Speicherort:** `system_steward_framework/knowledge/architecture/PROMPT_SECURITY_GUIDELINES.md`
*   **Inhalt:** Siehe "Teil 5.4 Ausgeliefertes Artefakt (Wissensbasis): PROMPT_SECURITY_GUIDELINES.md" im Fulfillment-Bericht.

### 1.4 Aktualisierung: `FAE_constraints.yaml`

*   **Beschreibung:** Erweiterung des Schemas um ein `evidence`-Feld und Aktualisierung des Eintrags für `FAE-002` mit validierten Evidenz-Einträgen.
*   **Speicherort:** `agency_os/01_planning_framework/knowledge/FAE_constraints.yaml`
*   **Änderungen:**
    *   Schema-Erweiterung für `evidence` (siehe "Schritt 1: Schema-Erweiterung" in Forschungsbereich 2 des ursprünglichen Audit-Berichts).
    *   Aktualisierung des Eintrags für `FAE-002` (real_time_chat_self_hosted) mit dem neuen `reason`, `recommendation` und `evidence`-Block (siehe "Teil 3.5 Ausgeliefertes Artefakt (Erweitertes Schema): FAE_constraints.yaml" im Fulfillment-Bericht).

---

## 2. Aktualisierung der Agenten-Prompts

**Ziel:** Anpassung bestehender Prompts und Erstellung neuer Prompts zur Integration der Forschungsergebnisse.

### 2.1 Neuer Agent-Prompt: `LEAN_CANVAS_VALIDATOR.md`

*   **Beschreibung:** Implementiert ein geführtes Interview zur Füllung des Lean Canvas und Identifizierung risikoreichster Annahmen.
*   **Speicherort:** `agency_os/01_planning_framework/prompts/LEAN_CANVAS_VALIDATOR.md`
*   **Inhalt:** Siehe "Teil 4.5 Ausgeliefertes Artefakt (Prompt-Entwurf): LEAN_CANVAS_VALIDATOR" im Fulfillment-Bericht.

### 2.2 Aktualisierung: `VIBE_ALIGNER_v3.md`

*   **Beschreibung:** Umfassende Aktualisierung zur Integration von Produktqualitäts-Metriken, Prompt-Sicherheitsleitplanken und NFR-Erhebung.
*   **Speicherort:** `agency_os/01_planning_framework/prompts/VIBE_ALIGNER_v3.md`
*   **Änderungen:**
    *   **Produktqualität (KB-3.4):** Integration der `PRODUCT_QUALITY_METRICS.yaml` und Anpassung des Dialogs in Phase 1 (Education).
    *   **Prompt-Sicherheit (BS-4.3):** Implementierung der mehrstufigen Verarbeitungs-Chain (Input Isolation, Threat Analysis, etc.) in Phase 2 (Extraction).
    *   **NFR-Erhebung (DC-2.2):** Einführung einer neuen "Phase 4: NFR Triage" zur systematischen Erfassung nicht-funktionaler Anforderungen.

---

## 3. Aktualisierung der Standard Operating Procedures (SOPs)

**Ziel:** Anpassung der SOPs zur Orchestrierung des neuen Validierungsprozesses.

### 3.1 Aktualisierung: `SOP_001_Start_New_Project.md`

*   **Beschreibung:** Anpassung der SOP, um den `LEAN_CANVAS_VALIDATOR` als obligatorischen ersten Schritt vor dem `VIBE_ALIGNER` aufzurufen.
*   **Speicherort:** `system_steward_framework/knowledge/sops/SOP_001_Start_New_Project.md`
*   **Änderungen:** Der Workflow muss angepasst werden, um den Aufruf des `LEAN_CANVAS_VALIDATOR` vor dem `VIBE_ALIGNER` zu integrieren.

---

## 4. Aktualisierung des Datenvertrags

**Ziel:** Erweiterung des zentralen Datenvertrags, um die neuen Informationen aus dem Lean Canvas und den NFRs aufzunehmen.

### 4.1 Aktualisierung: `ORCHESTRATION_data_contracts.yaml`

*   **Beschreibung:** Aktualisierung des Schemas für `feature_spec.json`, um die neue, erweiterte Struktur mit `nfr_requirements` und `lean_canvas_summary` widerzuspiegeln.
*   **Speicherort:** `agency_os/00_system/contracts/ORCHESTRATION_data_contracts.yaml`
*   **Änderungen:** Erweiterung des `feature_spec.json`-Schemas um die Felder `lean_canvas_summary` und `nfr_requirements`.

---

## 5. Aktualisierung des SSF-Routers

**Ziel:** Anpassung der Intent-Routing-Logik, um den neuen zweistufigen Planungsprozess zu orchestrieren.

### 5.1 Aktualisierung: `AGENCY_OS_ORCHESTRATOR_v1.md`

*   **Beschreibung:** Aktualisierung der Intent-Routing-Logik, um den neuen zweistufigen Planungsprozess (Lean Canvas -> Vibe Aligner) korrekt zu orchestrieren.
*   **Speicherort:** `agency_os/00_system/prompts/AGENCY_OS_ORCHESTRATOR_v1.md`
*   **Annahme:** Diese Datei wird als korrekte Entsprechung für den im Fulfillment-Bericht erwähnten, aber nicht existierenden `SYSTEM_STEWARD_ENTRY_PROMPT.md` angenommen.
*   **Änderungen:** Anpassung der Logik, um den `LEAN_CANVAS_VALIDATOR` als ersten Schritt für neue Projektplanungsanfragen zu identifizieren und aufzurufen.

---

**Nächste Schritte:**

Dieser Implementierungsplan dient als detaillierte Arbeitsanweisung. Die tatsächliche Durchführung der Änderungen in den jeweiligen Dateien ist der nächste Schritt.
