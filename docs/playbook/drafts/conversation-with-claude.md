# **Arbeitsauftrag**:

- Konversation lesen, Nuancen verstehen und Auftrag unten ausfhüren als SENIOR Claude-Code Instanz.
 
---

(CLAUDE.AI)

---

# 🚀 LET’S FUCKING GO!

Ja, wir sind angekommen! Lass uns das Playbook-System bauen - **prompt-only, no bullshit, pure configuration.**

-----

## 📦 Was ich JETZT erstelle:

### 1. **Playbook Registry** (Semantic Router)

### 2. **Core Playbooks** (Bootstrap, Session Resume)

### 3. **Domain Example** (Restaurant)

### 4. **System-Boot Integration**

Alles als downloadbare Artifacts. Los geht’s!

-----

# 🎉 FERTIG! Das Playbook-System ist komplett!

## ✅ Was du jetzt hast:

### 1. **_registry.yaml** (Semantic Router)

- 9 vordefinierte Routes (core + domains)
- Embedding-basiertes Matching
- Threshold-Konfiguration
- Fallback-Strategie

### 2. **bootstrap.md** (Core Playbook)

- First-time initialization
- System health check
- User onboarding
- Session handoff creation

### 3. **restaurant.yaml** (Domain Example)

- Domain-spezifischer Context
- Pre-Questions für Restaurants
- POS/Payment-Integration
- Quality Gates
- Graceful Degradation (LAD 1/2/3)

### 4. **system-boot.sh** (Enhanced)

- Playbook Registry Loading
- Semantic Routing Awareness
- Klare Instruktionen für STEWARD

-----

## 📁 Wo speichern:

```bash
# Von claude.ai runtergeladen:
_registry.yaml          → docs/playbook/_registry.yaml
bootstrap.md            → docs/playbook/core/bootstrap.md
restaurant.yaml         → docs/playbook/domains/hospitality/restaurant.yaml
system-boot-enhanced.sh → bin/system-boot.sh (REPLACE existing)

# Ordnerstruktur erstellen:
mkdir -p docs/playbook/{core,domains/hospitality,domains/healthcare,domains/ecommerce}
```

-----

## 🧪 Wie testen:

```bash
# 1. Files an richtige Orte kopieren
mv _registry.yaml docs/playbook/
mv bootstrap.md docs/playbook/core/
mv restaurant.yaml docs/playbook/domains/hospitality/
mv system-boot-enhanced.sh bin/system-boot.sh
chmod +x bin/system-boot.sh

# 2. Boot testen
./bin/system-boot.sh

# 3. Claude Code starten und sagen:
"I want to build a restaurant app"

# STEWARD sollte jetzt:
# - Registry checken
# - "restaurant" matchen (similarity > 0.80)
# - restaurant.yaml laden
# - Context enrichment anwenden
# - VIBE_ALIGNER mit Restaurant-Expertise starten
```

-----

## 🚀 Next Steps:

1. **Test Bootstrap Flow**
1. **Test Restaurant Playbook**
1. **Add more domain playbooks** (healthcare, ecommerce)
1. **Measure:** Does context enrichment improve output quality?

-----

**Das war’s! Pure prompt-based infrastructure. Keine Code-Changes. Nur YAML + Markdown.** 🔥

Willst du noch was anpassen oder sollen wir es so lassen?​​​​​​​​​​​​​​​​

---

(HIL):
---

Heißt das - ich sag Agent Boot Script sh - er liest Dashboard und hat dann auch playbook ? Kontext? Aber das ist nixjt möglich ich müsste den System prompt im boot Sequenz anpassen? Das playbook ist faktisch noch nicht abgeschlossen so? Wie ist die Logik?

---

(CLAUDE.AI):

---


Ah FUCK, du hast recht! Ich hab einen **kritischen Fehler** gemacht:

-----

## ❌ Das Problem:

```bash
./bin/system-boot.sh
# Zeigt nur TEXT im Terminal
# Claude liest es im Chat
# Aber: Kein automatisches "Playbook laden"
```

**Claude kriegt:**

- ✅ .session_handoff.json (im System Prompt vom Script)
- ✅ Text: “Playbook System existiert”
- ❌ NICHT: Die eigentlichen Playbook-Files

-----

## 🤔 Die echte Logik sollte sein:

### Option A: **Playbook = Teil vom System Prompt**

```bash
# system-boot.sh müsste machen:

# 1. User Input analysieren
USER_INPUT="I want to build a restaurant app"

# 2. Semantic Match (im Script selbst!)
MATCHED_ROUTE=$(grep -A5 "restaurant" docs/playbook/_registry.yaml | grep "target_chain" | cut -d: -f2)
# → "domains/hospitality/restaurant.yaml"

# 3. Playbook-File laden UND in System Prompt injizieren
cat << EOF
SYSTEM PROMPT:
- .session_handoff.json
- STEWARD instructions
- PLAYBOOK CONTEXT (from $MATCHED_ROUTE):
$(cat docs/playbook/$MATCHED_ROUTE)
EOF
```

**Problem:** Bash-Script kann kein Embedding-Matching machen!

-----

### Option B: **Claude macht Semantic Routing**

```bash
# system-boot.sh zeigt nur:

cat << EOF
PLAYBOOK SYSTEM AVAILABLE:
Registry: docs/playbook/_registry.yaml

Your job (Claude):
1. Read user input
2. Check _registry.yaml for semantic match
3. If match found, load corresponding playbook file
4. Apply context transformation
5. Execute workflow
EOF
```

**Dann muss Claude:**

```
1. view docs/playbook/_registry.yaml
2. Manuell matchen: "restaurant" in intent_patterns?
3. view docs/playbook/domains/hospitality/restaurant.yaml
4. Lesen & anwenden
```

-----

### Option C: **Zwei-Schritt-Prozess** (Realistisch!)

**Schritt 1: Boot**

```bash
./bin/system-boot.sh
# Zeigt: Session context + "Playbook available"
```

**Schritt 2: User sagt was**

```
User: "I want to build a restaurant app"

Claude:
1. Erkennt: "restaurant" keyword
2. view docs/playbook/_registry.yaml
3. Findet: target_chain = "domains/hospitality/restaurant.yaml"
4. view docs/playbook/domains/hospitality/restaurant.yaml
5. Wendet Context an
6. Startet VIBE_ALIGNER mit enrichment
```

-----

## ✅ Die RICHTIGE Implementierung:

### **Playbook = Instruction für Claude, NICHT automatisch geladen**

```markdown
# system-boot.sh sagt:

PLAYBOOK SYSTEM:
Location: docs/playbook/

If user mentions domain keywords (restaurant, healthcare, ecommerce):
1. Check: view docs/playbook/_registry.yaml
2. Find matching route (semantic similarity or keyword)
3. Load playbook: view docs/playbook/{route}
4. Apply context transformation from playbook
5. Execute target workflow

Example:
User: "restaurant app"
→ view docs/playbook/_registry.yaml (find "restaurant_app" route)
→ view docs/playbook/domains/hospitality/restaurant.yaml
→ Apply pre_enrichment + context_sources
→ Execute VIBE_ALIGNER with restaurant expertise
```

**Claude führt den Lookup aus. Nicht das Script.**

-----

## 🔧 Was ich fixen muss:

### **system-boot.sh sollte sagen:**

```bash
echo "📚 PLAYBOOK SYSTEM (Manual Routing):"
echo ""
echo "When user mentions domains (restaurant, healthcare, etc.):"
echo "  1. view docs/playbook/_registry.yaml"
echo "  2. Match user input to intent_patterns"
echo "  3. Load corresponding playbook file"
echo "  4. Apply context enrichment"
echo "  5. Execute target workflow"
echo ""
echo "Available routes: $(grep -c '^  - name:' docs/playbook/_registry.yaml) registered"
```

**Claude muss dann aktiv:**

1. Registry lesen
1. Matchen
1. Playbook laden
1. Anwenden

-----

## 💡 Oder: Python Helper Script?

```python
# bin/playbook-match.py

import sys
from sentence_transformers import SentenceTransformer

user_input = sys.argv[1]
registry = load_yaml("docs/playbook/_registry.yaml")

# Embedding match
best_route = semantic_match(user_input, registry['routes'])

if best_route['similarity'] > best_route['threshold']:
    print(f"MATCHED: {best_route['target_chain']}")
    print(open(f"docs/playbook/{best_route['target_chain']}").read())
else:
    print("NO_MATCH")
```

**Dann:**

```bash
PLAYBOOK=$(python3 bin/playbook-match.py "$USER_INPUT")
# → Outputs playbook content
# → Claude kriegt es im System Prompt
```

-----

## 🎯 Welchen Ansatz willst du?

**A) Claude macht Lookup manuell** (kein Code, pure instructions)  
**B) Python Helper für Semantic Matching** (1 kleines Script)  
**C) Ganz anders?**

Was macht am meisten Sinn für vibe-agency?​​​​​​​​​​​​​​​​

-----

(HIL):

---

Jetzt hab ich den kritischen Logikfehler entdeckt beziehungsweise wie wir’s eigentlich machen müssten, Das Problem ist, wir können nicht nur auf prompt setzen, sondern eigentlich ist ja die Logik dahinter so, wir müssen das Boot Upscript quasi anpassen, dass es logisch und schlau, den richtigen Kontext zusammenwürfelt und im Endeffekt, also pass mal auf, es muss so sein, User sagt zum Agenten, Cloud Code, Du bist stword. Dann macht Cloud das Er er er wird das Bootup Script laden. Dann müsste es eigentlich so sein. Das Boot up Script müsste irgendwie ihm einen geben, was ihn selber dazu bringt, dass er irgendwie was semantisch überlegen muss. Dass er herausfinden kann, welche Frage er den User stellen will, weil das System hat ja einen Status. Es gibt To dos und so weiter. Das heißt, Cloud müsste eigentlich kurz selbst ’n Brief Flight ’n Check machen, Und dabei verschiedenes abgleichen. Er müsste abgleichen in Systemstatus, Projekt, aktives Projekt, dann müsste er, dann könnte er quasi damit in Playbook quasi arbeiten, mit deinem Playbook zusammenarbeiten und so weiter. Und dann müsste er quasi dann erst wieder auf den User reagieren. Besser gesagt. Dann könnte er erst sagen, ah okay, schau, ich hab das So der User sagt, Cloud, Du bist Stewart. Cloud sagt, okay, ich mach kurz ‘n Check. Check da alles. Ah, schau mal, das das liegt an. Für dich heute. Das ist zu tun. Das müssen wir machen, so ungefähr. Und die Frage ist, wie es am einfachsten geht, also ja genau, es es geht muss eigentlich so sein. Man kann ja auch zum Beispiel könnte man nicht machen, Und dann pausiert das Skript und er fragt kurz den User, der antwortet, dann gibt Klotz wieder weiter. Das könnte man ja auch so machen. Klotz würde ja diese Anweisung befolgen. Er würde ja auf Antwort reagieren. Von dem her verstehst Du, ich mein, wir müssen das Bootscript mit einbeziehen, damit das quasi den richtigen Kontext zur richtigen Zeit an Chlord liefert, damit er von Anfang an den richtigen Weg eingehen kann, damit er immer wieder, stell dir mal vor, wie son Transformator eben. Ganz oben ist der User Input. Dann gehst Du eine Stufe runter, hast Du vier Auswahlmöglichkeiten. Wählst Du eine davon? Dann gehst Du ja quasi auf die nächste Ebene, entscheidet sich dann daher auch dann der nächste der nächste Brand, den Du nehmen kannst, ne. Ne. Und so wird dann der intent oder wie auch immer geroutet, dann alles kombiniert synthetisiert und dann kann dem User gesagt werden, ah okay, schau mal, das das das und das und das. Ich glaub, das ist die Antwort, weil dann können wir weil anders können wir nicht alles verbinden. Wir brauchen ein Skript, und deswegen haben wir ja diese verschiedenen Layers, diese verschiedenen Degradation. Auf der untersten Ebene ist es nur der prompt. Es funktioniert trotzdem, aber es ist halt nicht so gut, wie wenn Cloud Code dann tatsächlich auch das Bootabscript benutzen kann halt, verstehst Du? Dann auf der höchsten Ebene könnte man zum Beispiel sagen, okay, könnte man noch andere API sogar noch mal dazuschalten, die dann für Cloud noch mal noch mal weiterdenkt. Also wir reduzieren im Endeffekt die kognitive Last auf Cloud. Co je nachdem, auf welchem Tier wir uns befinden halt. Irgendwann ist es dann quasi bloß noch Stellvertreter. Jetzt müsste es hundert Prozent klar sein. Und die Frage ist, dein Konzept, was Du schon gemacht hast, lass es so wie’s ist und versuche mir einfach jetzt das Bootup Script eben daran noch anzupassen, dass das den richtigen Kontext zur richtigen Zeit an die richtige Stelle setzt. Damit Cloud quasi das hinkriegt. Das Ding ist aber, vielleicht müsstest Du dafür auch das Modul mit einbeziehen, damit wir das besser verknüpfen können. Schau dir das mal genau an, wie das funktioniert bei uns im System. Wenn Du nicht weißt, wie wo was, dann müsste wir erst mal das recherchieren, erforschen. Bitte nicht spekulieren, nicht weil das muss jetzt quasi integriert werden. Die wird wahrscheinlich Teil davon werden von diesem Standard Routing. Das Routing ist am Anfang nach innen und von innen nach außen am Schluss. Müssen da irgendwie auch ins System reinfinden und das geht nicht anders. Du verstehst, was ich mein, oder? Prompt Registry. Dieser Mechanismus, der ist entscheidend für den Erfolg weil der injiziert den richtigen Kontext zur richtigen Zeit an die richtige Stelle. Die richtige Variable zur richtigen Zeit, das ist eigentlich die Antwort. Und dann müssten wir eben auch schon mal, ja, nee, wir haben ja dann alles die die die Domainwissen, ist ja sowieso maschinenlesbar. Das können wir einfach super easy integrieren und dann dann später. Also Schritt eins quasi ist, wir tun einfach das Wissen dem Agenten geben, ohne jetzt Das Einzige, was wir machen ist, wir verändern das Boot up Skript. Das ist das einzige Script, was wir jetzt ändern, aber damit haben wir dann den riesigsten Effekt, weil wir dann quasi noch mehr Wissen mit einbauen können.

---

(CLAUDE.AI):

---

JETZT hab ich’s! Du hast den **kritischen Punkt** erkannt:

-----

## 🎯 Das echte Problem:

```
User: "Du bist STEWARD"
Claude: Lädt system-boot.sh
        Liest Output
        Wartet auf User Input
        
❌ Zu spät! Claude hat schon den "falschen" Kontext!
```

**Was WIRKLICH passieren muss:**

```
User: "Du bist STEWARD"
Claude: 1. Lädt system-boot.sh
        2. Script macht PRE-FLIGHT CHECK:
           - Liest .session_handoff.json
           - Liest project_manifest.json
           - Checkt todos/status
           - ⚠️ PAUSIERT und fragt User
        3. User antwortet: "restaurant app"
        4. Script macht SEMANTIC MATCH
        5. Script lädt RICHTIGES Playbook
        6. Script gibt Claude ENRICHED CONTEXT
        7. Claude startet mit VOLLEM Kontext
```

-----

## ✅ Die Lösung: **Interactive Boot Script**

Das Script muss:

1. ✅ Status checken (handoff, manifest)
1. ✅ User fragen: “Was willst du machen?”
1. ✅ Semantic Match (Python helper)
1. ✅ Playbook laden
1. ✅ Prompt Registry nutzen
1. ✅ Enriched Context an Claude geben

-----

## 🔍 Erst mal: Prompt Registry verstehen

Lass mich checken wie **Prompt Registry** aktuell funktioniert:​​​​​​​​​​​​​​​​

---

## **Anweisung an Claude Code**:

- Die Artifacts habe ich entsprechend abgespeichert im Repo unter docs/playbook/
- Bitte übernehme du anhand Ideen, und der realen Code Basis
- Integriere die erstellten Artifacts, passe nur das boot script an (enthaltene Logik sowie Systemprompt)
- Die vorliegenden Artifacts dürfen final von dir angepasst / eingepasst werden damit Sie sich smooth ins System integrieren lassen
- Funktionsweise abschauen bei VIBE_ALIGNER (Prompt Registry composition und allgemein Abläufe)
- Noch Fragen? Alles da? Stelle diese final den den user
