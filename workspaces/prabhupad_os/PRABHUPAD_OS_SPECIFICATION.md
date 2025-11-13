# PrabhupadaOS - Vollständige Projekt-Spezifikation

**Projekt-Typ:** Nonprofit/Spiritual
**Framework-Version:** v1.1 (Pragmatic Mode - Quick Research)
**Generiert:** 2025-11-13
**Status:** Planning Complete ✓

---

## 📋 Executive Summary

### Vision
Modular CLI platform delivering **100% authentic Srila Prabhupada texts** with verified EPUB parsing, extensible for devotional tools, prioritizing text integrity over convenience.

### Mission
Preserve and distribute original Prabhupada books with absolute authenticity, enabling global Hare Krishna community to study sacred texts on any platform.

### Kernproblem (Research-basiert)
1. **Fragmentierte App-Landschaft:** 150+ standalone Hare Krishna Apps ohne Interoperabilität
2. **Sanskrit-Darstellungsprobleme:** Diakritische Zeichen werden inkorrekt über verschiedene EPUB-Reader hinweg angezeigt
3. **Fehlende Authentizitätsprüfung:** Keine Verifikationssystem für unveränderte Originaltexte
4. **Technologie vs. Spiritualität:** Balance zwischen digitalen Tools und authentischer spiritueller Praxis

### Unique Value Proposition
**Einzige Plattform mit:**
- Kryptografischer Textverifikation (SHA-256 Checksums)
- Modularer Plugin-Architektur für Community-driven Tools
- 100% Offline-Verfügbarkeit (keine Cloud-Abhängigkeit)
- Originalgetreue Sanskrit-Unicode-Unterstützung

---

## 🎯 Zielgruppen

| Segment | Beschreibung | Bedürfnisse |
|---------|--------------|-------------|
| **ISKCON Devotees** | Hare Krishna Anhänger weltweit | Authentische Texte, offline-fähig, einfach nutzbar |
| **Scholars/Translators** | Akademiker, Übersetzer | Verifizierte Quelltexte, strukturierte Daten, Vers-IDs |
| **Plugin Developers** | Community-Entwickler | Stabile API, Erweiterbarkeit, Dokumentation |
| **Spiritual Seekers** | Vedische Literatur-Interessierte | Zugänglichkeit, Suchfunktion, Lesezeichen |

---

## 🏗️ System-Architektur

### Architektur-Stil
**Modular Monolith mit Plugin-Architektur**

```
┌─────────────────────────────────────────────────────────────────┐
│                        PrabhupadaOS CLI                         │
│                    (prabhupad-os command)                       │
└───────────────────────────┬─────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐   ┌──────────────┐   ┌──────────────────┐
│  Reader Core  │   │ EPUB Parser  │   │  Plugin Manager  │
│  (CLI UX)     │   │ (Text Ext.)  │   │  (Extensions)    │
└───────┬───────┘   └──────┬───────┘   └────────┬─────────┘
        │                  │                     │
        ▼                  ▼                     ▼
┌─────────────────────────────────────────────────────────┐
│            Shared Data Layer (SQLite)                   │
│  - books_metadata (Titel, Autor, Checksum)              │
│  - user_bookmarks (Lesezeichen, Position)               │
│  - fts5_search (Volltext-Index)                         │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│              File System (Local Storage)                │
│  - books/ (EPUB-Dateien, Git LFS)                       │
│  - books_manifest.yaml (SHA-256 Checksums)              │
│  - plugins/ (Community Extensions)                      │
└─────────────────────────────────────────────────────────┘
```

### Komponenten (Monorepo-Pakete)

#### 1. `@prabhupad-os/reader`
**Verantwortung:** CLI-Interface, User Interaction, Command Routing

**Technologien:**
- Python Click (CLI Framework)
- Rich (Terminal-Styling, Unicode-safe)

**Key Classes:**
- `ReaderCLI` - Main entry point
- `BookNavigator` - Kapitel-Navigation, Suche
- `BookmarkManager` - Lesezeichen verwalten
- `DisplayEngine` - Unicode-safe Terminal-Rendering

---

#### 2. `@prabhupad-os/parser`
**Verantwortung:** EPUB-Parsing, Sanskrit Unicode, Textextraktion

**Technologien:**
- EbookLib (EPUB2/EPUB3)
- BeautifulSoup4 (HTML-Parsing)

**Key Classes:**
- `EPUBParser` - Haupt-Parsing-Logik
- `SanskritUnicodeHandler` - Font/Encoding-Handling
- `VerseExtractor` - Vers-Level-Granularität
- `ChecksumVerifier` - SHA-256 Validation

**Critical Implementation Detail:**
```python
# Sanskrit Unicode Preservation
# Devanagari: U+0900–U+097F
# IAST (Latin Extended-A): U+0100–U+017F
# Beispiel: ā, ī, ū, ṛ, ṃ, ḥ

class SanskritUnicodeHandler:
    def preserve_diacritics(self, text: str) -> str:
        # Ensure UTF-8 encoding preserved
        # Handle font embedding from EPUB
        # Validate Unicode ranges
        pass
```

---

#### 3. `@prabhupad-os/storage`
**Verantwortung:** SQLite DB, User Data Persistence, Full-Text Search

**Technologien:**
- SQLite3 (stdlib)
- SQLAlchemy (ORM)
- FTS5 (Full-Text Search Extension)

**Schema:**
```sql
-- Bücher-Metadaten
CREATE TABLE books_metadata (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT DEFAULT 'A.C. Bhaktivedanta Swami Prabhupada',
    epub_path TEXT NOT NULL,
    checksum_sha256 TEXT NOT NULL,
    bbt_source_url TEXT,
    verified BOOLEAN DEFAULT 0,
    total_chapters INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Lesezeichen
CREATE TABLE user_bookmarks (
    id INTEGER PRIMARY KEY,
    book_id INTEGER REFERENCES books_metadata(id),
    verse_id TEXT,
    chapter_number INTEGER,
    position_percent REAL,
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Volltext-Suche (FTS5)
CREATE VIRTUAL TABLE fts5_search USING fts5(
    book_id, chapter_number, verse_id, content
);
```

---

#### 4. `@prabhupad-os/plugin-sdk`
**Verantwortung:** Plugin API, Discovery, Lifecycle Management

**Plugin API Beispiel:**
```python
from prabhupad_os.plugin_sdk import PluginAPI

class VerseOfTheDayPlugin(PluginAPI):
    def get_metadata(self):
        return {
            'name': 'Verse of the Day',
            'version': '1.0.0',
            'author': 'Community'
        }

    def on_init(self, config):
        self.db = config['db']

    def on_book_open(self, book):
        verse = self._get_random_verse(book)
        print(f'📖 Verse of the Day: {verse.text}')
```

**Plugin Hooks:**
- `on_init(config)` - Plugin initialisieren
- `on_book_open(book)` - Buch geöffnet
- `on_verse_display(verse)` - Vers-Anzeige modifizieren
- `on_bookmark_create(bookmark)` - Lesezeichen erstellt

---

## 🎨 Features (MoSCoW-Priorisierung)

### MUST HAVE (MVP - Phase 1)

| ID | Feature | Komplexität | Zeit | Beschreibung |
|----|---------|-------------|------|--------------|
| **F001** | CLI E-Book Reader Core | 8 | 2-3 Wochen | Terminal-basierter Reader mit Navigation, Suche, Lesezeichen |
| **F002** | EPUB Parser + Sanskrit | 13 | 3-4 Wochen | EPUB2/EPUB3 Parsing, Sanskrit Unicode (Devanagari, IAST) |
| **F003** | Authentizitätsprüfung | 5 | 1 Woche | SHA-256 Checksums, Verifikations-Command |
| **F006** | Git-Distribution | 3 | 3-5 Tage | Git LFS, install.sh, Update-Mechanismus |
| **F008** | Offline Storage | 5 | 1 Woche | SQLite Bookmarks, Progress, XDG-Compliance |

**Gesamt MVP:** 34 Komplexitätspunkte, **8-12 Wochen**

---

### SHOULD HAVE (Phase 2)

| ID | Feature | Komplexität | Zeit | Beschreibung |
|----|---------|-------------|------|--------------|
| **F004** | Plugin-Architektur | 21 | 4-5 Wochen | Plugin SDK, Discovery, Sample Plugins |
| **F005** | Monorepo Build System | 8 | 1-2 Wochen | Poetry Workspaces, Shared Config |

**Gesamt Phase 2:** 29 Komplexitätspunkte, **5-7 Wochen**

---

### COULD HAVE (Future Phase 3)

| ID | Feature | Komplexität | Status |
|----|---------|-------------|--------|
| **F007** | Translation Data Export | 13 | **DEFERRED** per User Request ("später geplant") |

---

## 🔒 Non-Functional Requirements (NFR)

### Mission-Critical NFRs

#### 1. **SEC-AUTHENTICITY** - Text-Integrität (CRITICAL)
**Anforderung:** Kryptografische Verifikation, dass Texte unverändert sind

**Implementation:**
- `books_manifest.yaml` mit SHA-256 Checksums
- Auto-Verifikation beim ersten Start
- CLI-Command: `prabhupad-os verify <book>`
- Output: `✓ VERIFIED | ✗ MODIFIED | ? UNKNOWN`
- BBT-Quellenangaben im Manifest

**Acceptance Criteria:**
- ✓ Jedes Buch hat SHA-256 Checksum
- ✓ Verifizierungs-Command funktioniert
- ✓ Modifizierte Bücher werden abgelehnt
- ✓ BBT-Quellen dokumentiert

---

#### 2. **REL-AVAILABILITY** - 100% Offline (CRITICAL)
**Anforderung:** Keine Internet-Abhängigkeit

**Implementation:**
- Alle Bücher lokal (Git LFS)
- SQLite (kein Cloud-DB)
- Keine REST-APIs in Core-Features
- Offline-first Architektur

**Acceptance Criteria:**
- ✓ Alle Features funktionieren ohne Internet
- ✓ Keine Cloud-Services required
- ✓ Git LFS installiert Bücher lokal

---

#### 3. **MAIN-MODULARITY** - Plugin-Architektur (CRITICAL)
**Anforderung:** "das Ziel ist eben das Modular zu gestalten" (User-Quote)

**Implementation:**
- Plugin SDK mit stabiler API
- Directory-based Discovery (`plugins/`)
- Sample Plugin (verse-of-the-day)
- Developer Documentation

**Acceptance Criteria:**
- ✓ Plugin API dokumentiert
- ✓ Third-party kann Plugins bauen ohne Core zu ändern
- ✓ Sample Plugin funktioniert

---

#### 4. **PORT-UNICODE** - Sanskrit Support (CRITICAL)
**Anforderung:** Originalgetreue Sanskrit-Darstellung

**Implementation:**
- Devanagari Unicode (U+0900–U+097F)
- IAST Diacritics (ā, ī, ū, ṛ, ṃ, ḥ)
- Rich Library (Unicode-safe Terminal)
- Font-Fallback-Dokumentation

**Acceptance Criteria:**
- ✓ Devanagari rendert korrekt
- ✓ IAST Diacritics rendern korrekt
- ✓ Getestet auf Major Terminals (gnome-terminal, iTerm2, Windows Terminal)

---

### High-Priority NFRs

#### PERF-LATENCY - Performance
- Buch laden: **< 2 Sekunden**
- Kapitel-Navigation: **< 100ms**
- Volltext-Suche: **< 3 Sekunden**

**Implementation:** Caching (SQLite), FTS5-Index, Rich-Library

---

#### USAB-LEARNABILITY - Onboarding
- **5-Minuten-Ziel:** User kann in 5 Minuten erstes Buch lesen

**Implementation:**
- One-Command Install: `./install.sh`
- Interaktiver Reader-Modus
- Exzellente `--help` Texte
- README Quick Start: 3 Steps

---

## 🛠️ Technology Stack

### Empfehlung: **Python 3.10+ (MVP)**

| Komponente | Technologie | Rationale |
|------------|-------------|-----------|
| **Sprache** | Python 3.10+ | Cross-platform, EbookLib, Rapid Development |
| **CLI Framework** | Click + Rich | Industry Standard, Unicode-safe Terminal |
| **EPUB Parser** | EbookLib | EPUB2/EPUB3, aktiv maintained, Unicode-Support |
| **Storage** | SQLite3 + FTS5 | Offline-first, Full-Text Search built-in |
| **ORM** | SQLAlchemy | Standard Python ORM |
| **Monorepo** | Poetry Workspaces | Native Python Monorepo-Support |
| **Testing** | pytest + coverage | Standard Stack, 70%+ Coverage-Ziel |
| **Terminal UI** | Rich | Beautiful Unicode-safe Output |

### Alternative: **Rust (Phase 4)**
**Vorteile:**
- Single-Binary Distribution (keine Python Runtime nötig)
- Performance
- Type Safety

**Nachteile:**
- Langsamere Development-Zeit
- epub-rs weniger mature als EbookLib
- Plugin-System komplexer

**Empfehlung:** Rust-Rewrite in v2.0 für bessere Distribution, **aber MVP in Python** für schnelle Validation.

---

## 📁 File System Struktur

```
prabhupad-os/
├── books/                      # EPUB-Dateien (Git LFS)
│   ├── bhagavad-gita.epub
│   ├── srimad-bhagavatam-01.epub
│   └── ...
├── books_manifest.yaml         # SHA-256 Checksums + BBT Sources
├── data/
│   └── prabhupad_os.db        # SQLite (Bookmarks, Progress)
├── plugins/                    # Community Extensions
│   └── verse_of_the_day/
│       ├── __init__.py
│       └── plugin.py
├── packages/                   # Monorepo Packages
│   ├── reader/
│   ├── parser/
│   ├── storage/
│   ├── plugin-sdk/
│   └── cli/
├── pyproject.toml             # Poetry Workspace Config
├── install.sh                 # Installation Script
├── README.md                  # Documentation
└── tests/
    ├── unit/
    └── integration/
```

---

## 🚀 Implementation Roadmap

### Phase 1: MVP (8-12 Wochen)

| Woche | Task | Deliverable |
|-------|------|-------------|
| **1-2** | Monorepo Setup, SQLite Schema, Basic CLI | Poetry Workspace, DB Schema |
| **3-5** | EPUB Parser + Sanskrit Unicode | `@prabhupad-os/parser` mit Tests |
| **6-8** | Reader Core (Navigation, Suche, Bookmarks) | `@prabhupad-os/reader` + Rich TUI |
| **9-10** | Checksum-Verifikation | `books_manifest.yaml`, Verify-Command |
| **11-12** | Install Script, Docs, Final Testing | `install.sh`, README, 70%+ Coverage |

**MVP Deliverables:**
- ✅ CLI E-Book Reader mit Kapitel-Navigation
- ✅ EPUB Parser mit Sanskrit Unicode
- ✅ Text-Authentizitätsprüfung (SHA-256)
- ✅ Git-Distribution (install.sh)
- ✅ SQLite Bookmarks/Progress
- ✅ 70%+ Test Coverage
- ✅ Cross-Platform (Linux/macOS/Windows)

---

### Phase 2: Plugins (5-7 Wochen)

**Features:** F004, F005

**Deliverables:**
- Plugin SDK mit stabiler API
- Plugin Discovery + Lifecycle
- Sample Plugins (verse-of-the-day, annotations)
- Developer Documentation
- Monorepo Optimization (Poetry Workspaces)

---

### Future: Phase 3 (Translation Framework)

**Status:** **DEFERRED** per User Requirement

**Feature:** F007 (Translation Data Export)

**Notes:** "später soll auch geplant sein Übersetzung Framework"

---

## 🧪 Testing Strategy

### Unit Tests (70%+ Coverage)

**Focus Areas:**
1. **EPUB Parser**
   - Alle Buchstrukturen (Bhagavad Gita, Srimad Bhagavatam, etc.)
   - Sanskrit Unicode (Devanagari + IAST)
   - Edge Cases (malformed EPUB, missing chapters)

2. **Checksum Verifier**
   - Valid checksums → VERIFIED
   - Invalid checksums → MODIFIED
   - Missing checksums → UNKNOWN

3. **BookNavigator**
   - Chapter navigation edge cases
   - Search mit Sanskrit terms
   - Bookmark save/restore

**Tools:** pytest, coverage.py

---

### Integration Tests

**Szenarien:**
1. **End-to-End:** Install → List Books → Read Chapter → Bookmark → Exit
2. **Verification:** Load Book → Verify Checksum → Detect Modification
3. **Search:** Index Book → Search Sanskrit Term → Display Results

---

### Platform Tests

**Platforms:**
- Ubuntu 22.04
- macOS 13+
- Windows 10+

**Terminals:**
- gnome-terminal (Linux)
- iTerm2 (macOS)
- Windows Terminal (Windows)

**Unicode Validation:**
- Test Sanskrit rendering on all platforms
- Document recommended terminals
- Provide fallback instructions

---

## 📦 Installation & Distribution

### Installation (One-Command)

```bash
git clone https://github.com/prabhupad-os/prabhupad-os.git
cd prabhupad-os
./install.sh
prabhupad-os --help
```

### install.sh Responsibilities

1. ✓ Check Python 3.10+ installed
2. ✓ Install Poetry if missing
3. ✓ Run `poetry install` (all dependencies)
4. ✓ Setup Git LFS + fetch books
5. ✓ Initialize SQLite database
6. ✓ Run auto-verification of books
7. ✓ Add `prabhupad-os` to PATH
8. ✓ Display success message + quick start

### Update Mechanism

```bash
prabhupad-os update
# Internally: git pull origin main && poetry install
```

---

## 🎯 CLI Commands

| Command | Description |
|---------|-------------|
| `prabhupad-os list` | Alle verfügbaren Bücher auflisten |
| `prabhupad-os read <book>` | Buch im interaktiven Reader öffnen |
| `prabhupad-os search <query>` | Volltext-Suche über alle Bücher |
| `prabhupad-os verify [book]` | Authentizität prüfen (Checksums) |
| `prabhupad-os bookmarks` | Alle Lesezeichen auflisten |
| `prabhupad-os plugins` | Installierte Plugins auflisten |
| `prabhupad-os update` | Software updaten (git pull) |
| `prabhupad-os --help` | Hilfe + Beispiele |

---

## ⚠️ Risiken & Mitigationen

### Technische Risiken

#### 1. Sanskrit Unicode-Rendering variiert über Terminals
**Wahrscheinlichkeit:** MEDIUM
**Impact:** MEDIUM

**Mitigation:**
- Dokumentiere empfohlene Terminals
- Teste auf Major Platforms
- Fallback-Instruktionen in README
- Rich Library (Unicode-safe)

---

#### 2. EbookLib handhabt nicht alle BBT-EPUB-Variationen
**Wahrscheinlichkeit:** LOW
**Impact:** HIGH

**Mitigation:**
- Teste mit **allen BBT-Büchern early**
- Fallback-Parser bereit (epub-rs in Rust)
- Contact BBT für EPUB-Specs

---

#### 3. Plugin-System verzögert MVP
**Wahrscheinlichkeit:** LOW
**Impact:** LOW

**Mitigation:**
- **Defer Plugins to Phase 2**
- Focus: Core Reader first
- Simple Plugin API (kein Dynamic Runtime Loading)

---

### Organisatorische Risiken

#### 1. BBT Copyright-Concerns für Distribution
**Wahrscheinlichkeit:** MEDIUM
**Impact:** CRITICAL

**Mitigation:**
- **Koordination mit BBT early**
- Cite sources in `books_manifest.yaml`
- Respect distribution terms
- Open-Source License (respects BBT copyright)

---

#### 2. CLI schüchtert nicht-technische Devotees ein
**Wahrscheinlichkeit:** HIGH
**Impact:** HIGH

**Mitigation:**
- **Exzellentes Onboarding:** One-command install
- **Interaktiver TUI-Modus** (nicht nur reine CLI)
- **Video-Tutorials** für Community
- **5-Minuten-Ziel** strikt einhalten

---

## 📊 Success Metrics

### MVP Success Criteria

1. ✅ **Usability:** 10 Devotees können innerhalb 5 Minuten erstes Buch lesen
2. ✅ **Authenticity:** Alle originalen BBT-Bücher mit Checksums verifiziert
3. ✅ **Quality:** 70%+ Test Coverage
4. ✅ **Portability:** Funktioniert auf Linux/macOS/Windows

---

### Phase 2 Success Criteria

1. ✅ **Modularity:** 3+ Community-entwickelte Plugins publiziert
2. ✅ **Maintainability:** Developer Docs rated 4/5+ von Plugin-Entwicklern

---

### Long-Term Vision

1. 📈 **1000+ aktive User** in Hare Krishna Community
2. 🌍 **10+ Sprachen** via Translation Framework
3. 🏆 **BBT-Referenced** als offizielles CLI-Tool

---

## 🔄 v1.1 Framework Test - Observations

### Quick Research Mode Performance

| Metric | Result |
|--------|--------|
| **Mode Used** | Quick Research (nonprofit project_type) |
| **WebSearch Triggered** | ✅ Yes (3 searches) |
| **Duration** | ~7 minutes (vs. 15-20 min Full Interview) |
| **Research Quality** | HIGH - Found pain points, existing solutions, technical requirements |
| **User Confidence** | LOW initially → HIGH after research |

### Framework Strengths (v1.1)

✅ **Auto-WebSearch Detection:** User sagte "so viele Fragezeichen" → Framework recherchierte automatisch
✅ **NFR Triage:** Verhinderte Overengineering (z.B. Plugin-System simplified per FAE-013)
✅ **project_type Routing:** Nonprofit → Quick Research → 60% schneller
✅ **Adaptive Workflow:** Volle VIBE_ALIGNER trotz Quick-Mode (keine Quality-Opferung)

---

## 📝 Nächste Schritte

### Immediate Actions

1. **User Review:** Diese Spezifikation reviewen, Feedback geben
2. **BBT Coordination:** Kontakt mit Bhaktivedanta Book Trust aufnehmen für EPUB-Permissions
3. **Tech Stack Finalization:** Python vs. Rust entscheiden (Empfehlung: Python MVP)
4. **Repository Setup:** GitHub Repo erstellen, Monorepo initialisieren

### Week 1 Sprint

1. Poetry Workspace Setup
2. SQLite Schema Implementation
3. Basic CLI Structure (Click)
4. Sample EPUB Test Fixture

---

## 📚 Appendix

### Referenzen

- **ISO 25010:** Software Quality Standard (NFR-Kategorisierung)
- **BBT:** Bhaktivedanta Book Trust (Original Prabhupada Books)
- **ISKCON:** International Society for Krishna Consciousness
- **EbookLib:** https://pypi.org/project/EbookLib/
- **Rich:** https://rich.readthedocs.io/
- **FTS5:** https://www.sqlite.org/fts5.html

### Glossar

- **BBT:** Bhaktivedanta Book Trust (Original Publisher)
- **IAST:** International Alphabet of Sanskrit Transliteration
- **Devanagari:** Sanskrit Script (U+0900–U+097F)
- **FTS5:** SQLite Full-Text Search Extension
- **TUI:** Text User Interface
- **NFR:** Non-Functional Requirements
- **MVP:** Minimum Viable Product

---

**Generated by:** VIBE Agency Planning Framework v1.1 (Pragmatic Mode)
**Workflow:** LEAN_CANVAS_VALIDATOR (Quick Research) → VIBE_ALIGNER (Phase 1-4 + NFR Triage) → GENESIS_BLUEPRINT
**Total Artifacts:** 8 (lean_canvas, 4 phases, blueprint, specification, manifest)
