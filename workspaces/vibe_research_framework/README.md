# VIBE RESEARCH FRAMEWORK
## The Knowledge Department (GAD-6: The Arms)

**Purpose**: Central repository for research, patterns, decision records, and code snippets that feed the agency's long-term memory.

**Why**: An agent without organized knowledge is a hallucinator. The Research Framework prevents "knowledge sprawl" by providing strict, physical separation of concerns.

---

## 📁 Directory Structure

This framework implements strict separation of concerns across four domains:

### `research/`
- **Purpose**: Findings, explorations, and experimental results
- **Content**: Markdown documents, research notes, investigation logs
- **Lifecycle**: Raw findings → validated → patterns extraction
- **Audience**: Primarily for internal research and knowledge building

### `patterns/`
- **Purpose**: Reusable architectural and implementation patterns
- **Content**: Pattern descriptions, use cases, implementation examples
- **Lifecycle**: Patterns extracted from research → documented → reusable
- **Audience**: System developers, architects, future implementations

### `snippets/`
- **Purpose**: Vetted code snippets and templates
- **Content**: Working code examples, templates, boilerplate
- **Organization**: By language, by problem domain
- **Lifecycle**: Code from successful implementations → tested → added to snippets
- **Audience**: Developers implementing new features

### `decisions/`
- **Purpose**: Architecture Decision Records (ADRs)
- **Content**: ADR documents following standard format (Status, Context, Decision, Consequences)
- **Lifecycle**: Proposed decision → debated → recorded → implemented
- **Audience**: System architects, decision makers, anyone needing historical context

---

## 🔗 Integration Points

### From GAD-5 (Runtime Foundation)
- Reads: `.vibe/logs/commands.log` for execution patterns
- Reads: `.vibe/runtime/context.json` for system context
- Reads: `.vibe/config/roadmap.yaml` for task history

### To GAD-3 (Strategic Layer)
- Provides: Research findings and analysis
- Provides: Architecture patterns and best practices
- Provides: Code snippets and templates
- Provides: Decision history and rationale

### Within Agency
- Used by: Agents needing to understand system patterns
- Used by: Future implementations needing prior art
- Used by: Strategic decisions needing historical context

---

## 📊 Usage Guidelines

### Adding Research
1. Create file in `research/` with descriptive name
2. Format as Markdown with clear sections
3. Include: objective, methodology, findings, next steps
4. Tag with relevant keywords for semantic search

### Creating Patterns
1. Extract from successful research or implementations
2. Document in `patterns/` with:
   - Problem statement
   - Solution overview
   - When to use / when not to use
   - Implementation example
3. Cross-reference with research origins

### Adding Snippets
1. Ensure code is tested and working
2. Add clear comments explaining purpose
3. Organize in appropriate subdirectory
4. Include usage examples

### Recording Decisions
1. Use standard ADR format (MADR or similar)
2. Include: Status (Proposed/Accepted/Deprecated), Context, Decision, Consequences
3. File in `decisions/` with timestamp
4. Reference in implementation commits

---

## 🚀 Roadmap

**Phase 1 (GAD-601)**: Structural scaffolding (CURRENT)
- ✅ Directory structure created
- ✅ Config system initialized
- ⏳ Initial documentation templates

**Phase 2 (GAD-602)**: Semantic search
- Implement knowledge base indexing
- Build semantic search over stored knowledge
- Connect to LLM context windows

**Phase 3**: Integration with agents
- Agents query knowledge base for patterns
- Agents add findings to research database
- Self-improving through delegation

---

## 🛡️ Anti-Sprawl Guarantee

Every file has a place. Every domain has a clear purpose.

- **No** miscellaneous docs at root
- **No** research scattered in code
- **No** patterns hidden in commit messages
- **No** decisions lost to Slack history

The physical structure forces discipline.
