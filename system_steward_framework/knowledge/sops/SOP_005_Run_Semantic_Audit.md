
# SOP-005: Durchführung eines Semantischen Design-Audits

**ID:** SOP-005
**Titel:** Durchführung eines Semantischen Design-Audits (Prä-Implementierung)
**Ziel:** Systematische Identifizierung von logischen und semantischen Fehlern, Inkonsistenzen und Lücken im Design des "Agency Operating System" (AOS) vor der Implementierung von Code.
**Verantwortlich:** System Steward (Menschlicher Auditor)
**Frequenz:**
*   Vor der ersten Implementierung (Initial-Audit).
*   Nach jeder wesentlichen Design-Änderung an der State Machine, den Datenverträgen oder der globalen Wissensbasis (Regressions-Audit).
**Erforderliche Artefakte (Eingaben):**
*   `AUDITOR_AGENT_v1.md` (Die Audit-Persona)
*   `AUDIT_CHECKLIST.md` (Die Audit-Methodik)
*   Die vollständigen Design-Spezifikationen des AOS (Prompts, YAML-Dateien, etc.)

---

## PROZEDUR

### 1. Phase: Kontext-Erstellung (Der wichtigste Schritt)

**Ziel:** Erstellung einer vollständigen, in sich geschlossenen "Momentaufnahme" des zu prüfenden Systems.

1.1. Erstellen Sie eine temporäre Datei namens `AOS_CONTEXT.md`.
1.2. **(Kritisch)** Füllen Sie diese Datei mit einer vollständigen und detaillierten Zusammenfassung aller relevanten System-Blaupausen. Kopieren Sie den vollständigen Inhalt der folgenden Dateien in die `AOS_CONTEXT.md`:
    *   Die vollständige Definition der Master-Orchestrator State Machine (z.B. `orchestrator.yaml`).
    *   Die vollständigen System-Prompts für jeden Spezialisten-Agenten (z.B. `PLANNING.md`, `CODE_GEN.md`, `QA.md`).
    *   Die vollständigen YAML-Schemata für jeden Datenvertrag (z.B. `planning_output.yaml`, `qa_report.json.yaml`).
    *   Die vollständigen Inhalte aller relevanten Wissensdatenbank-Dateien (z.B. `global_constraints.yaml`, `agent_specific_rules.yaml`).
1.3. **Rationale:** Die Qualität dieses Audits ist direkt proportional zur Vollständigkeit dieses Kontextes. Ein unzureichend spezifizierter oder unter-spezifizierter Kontext ist die Hauptursache Nr. 1 für "False Positives" (Falschmeldungen) bei KI-gesteuerten Red-Team-Audits. Der Auditor-Agent kann nur finden, was Sie ihm zur Verfügung stellen.

### 2. Phase: Ausführung des Audits

**Ziel:** Ausführung des Audits durch eine unvoreingenommene, "blinde" KI-Instanz.

2.1. Öffnen Sie eine neue, unabhängige KI-Instanz (z.B. ein neues Chat-Fenster in einem separaten Browser-Tab oder -Profil).
2.2. **(Kritisch)** Verwenden Sie nicht dieselbe Instanz, denselben Thread oder dasselbe Projekt, das Sie für die Entwicklung des Systems verwenden. Dies ist der entscheidende Schritt, um Kontamination und "Betriebsblindheit" zu verhindern.
2.3. **Laden der Persona:** Kopieren Sie den vollständigen Inhalt von `AUDITOR_AGENT_v1.md` als ersten Prompt in die neue Instanz. Senden Sie ihn. Die KI sollte ihre Rolle bestätigen.
2.4. **Starten des Audits:** Kopieren Sie in einem einzigen, zweiten Prompt den gesamten Inhalt von (A) der von Ihnen erstellten `AOS_CONTEXT.md` und (B) der `AUDIT_CHECKLIST.md`.
2.5. Fügen Sie am Ende dieses großen Prompts den folgenden Befehl hinzu:
    > "Sie haben nun den vollständigen System-Kontext und Ihre Audit-Checkliste erhalten. Bitte führen Sie das Audit-Protokoll gemäß Ihrer Kernanweisung durch. Stellen Sie den vollständigen Audit-Bericht bereit."
2.6. **Bericht-Generierung:** Lassen Sie die KI-Instanz den vollständigen Bericht generieren. Dies kann Zeit in Anspruch nehmen.
2.7. **Speichern des Berichts:** Speichern Sie den generierten Bericht als `AUDIT_REPORT__v1.md`.

### 3. Phase: Triage und Analyse (Menschliche Validierung)

**Ziel:** Menschliche Überprüfung und Klassifizierung der vom KI-Auditor gemeldeten Befunde.

3.1. Nehmen Sie den generierten `AUDIT_REPORT_..._v1.md` entgegen.
3.2. **(Kritisch)** Führen Sie eine Triage für jeden einzelnen gemeldeten Befund durch. Klassifizieren Sie jeden Befund als:
    *   **"True Positive (TP)":** Der Auditor hat einen validen Designfehler, eine Inkonsistenz oder eine Lücke gefunden.
    *   **"False Positive (FP)":** Der Auditor hat den Kontext falsch interpretiert oder einen Fehler gemeldet, der bei menschlicher Betrachtung keiner ist.
3.3. **Rationale:** Erwarten Sie False Positives. Sie sind ein normales Ergebnis bei der Verwendung von LLMs für die Benotung ("model-graded metrics"). Ein FP ist oft kein Fehler des Auditors, sondern ein Indikator für einen unklaren oder mehrdeutigen `AOS_CONTEXT.md`.

### 4. Phase: Remediation und Versionierung

**Ziel:** Behebung der gefundenen Fehler und Erstellung eines unveränderlichen Audit-Trails.

4.1. **Für TPs (True Positives):** Erstellen Sie für jeden 'True Positive'-Befund ein Ticket in Ihrem Projektmanagement-Tool (z.B. Jira, GitHub Issue). Weisen Sie das Ticket der Behebung im Design zu.
4.2. **Für FPs (False Positives):** Ignorieren Sie den Befund nicht. Behandeln Sie ihn als Bug in Ihrem Audit-Prozess. Gehen Sie zurück zu Phase 1 (1.2) und verbessern Sie die `AOS_CONTEXT.md`-Datei, um die Mehrdeutigkeit zu beseitigen, die zum FP geführt hat.
4.3. **Archivierung (Audit Trail):** Archivieren Sie die folgenden Artefakte in einem unveränderlichen Speicher (z.B. Git-Repository) mit einem Zeitstempel:
    *   `AOS_CONTEXT.md` (Version, die auditiert wurde)
    *   `AUDIT_REPORT__v1.md` (Der Rohbericht)
    *   Eine Triage-Liste (z.B. `TRIAGE_REPORT_v1.md`), die alle Befunde und ihre Klassifizierung (TP/FP) auflistet.
4.4. **Rationale:** Diese Archivierung bildet Ihren Audit-Trail für die Design-Provenienz. Sie schafft eine nachvollziehbare, unveränderliche Aufzeichnung, die belegt, was validiert wurde und welche Ergebnisse gefunden wurden, ein Kernprinzip robuster System-Governance.
4.5. **Regression:** Führen Sie diese SOP nach der Behebung der TPs (und der Aktualisierung des Kontexts) erneut durch (`AUDIT_REPORT_..._v2.md`), um die Behebung zu validieren und auf neue (Regression-)Fehler zu prüfen.
