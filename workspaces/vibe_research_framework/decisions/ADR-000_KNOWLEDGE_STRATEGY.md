# ADR-000: Knowledge Management Strategy

**Status:** Accepted

**Date:** 2025-11-19

## Context

The VIBE AGENCY system needs to grow beyond simple script execution into true knowledge-driven automation. Agents cannot hallucinate answers to technical questions—they must query a persistent knowledge base.

Early consideration: Vector embeddings (RAG, semantic search with LLM embeddings) are powerful but introduce:
- External dependencies (vector DB, embedding APIs)
- Cost and latency overhead
- Complexity in maintenance

## Decision

We implement a **lightweight, file-based knowledge retrieval system** as the foundation (GAD-602).

**Phase 1 (NOW)**: Keyword-based search with relevance scoring
- Scan markdown files in designated domains
- Simple keyword matching with relevance scoring
- Results returned as structured hits with path, preview, score

**Phase 2 (FUTURE)**: Upgrade to semantic search when needed
- Add vector embeddings if keyword search proves insufficient
- Migrate to vector database (Pinecone, Weaviate, or local embedding)
- Keep the same KnowledgeRetriever interface for backward compatibility

## Benefits

1. **No external dependencies** in Phase 1
2. **Fast iteration** - agents can learn patterns today
3. **Transparent** - easy to debug what was found and why
4. **Extensible** - can add embeddings without changing the CLI

## Implementation

- `agency_os/02_knowledge/retriever.py`: Core KnowledgeRetriever class
- `bin/vibe-knowledge`: CLI interface (search, list, read, domains)
- `workspaces/vibe_research_framework/{research,patterns,snippets,decisions}/`: Knowledge artifacts

## Consequences

- Agents cannot find knowledge that doesn't exist in structured form
- Keyword search may miss semantically similar content
- We'll need to curate knowledge deliberately

These are FEATURES, not bugs. They force discipline.

---

## Next Steps

- Implement semantic search upgrade when keyword search shows limitations
- Build feedback mechanism: agents report "I couldn't find X"
- Track search patterns to identify gaps in knowledge base
