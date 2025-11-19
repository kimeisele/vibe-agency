#!/usr/bin/env python3
"""
Knowledge Retriever Module (GAD-602)

Lightweight, file-based semantic search for the VIBE AGENCY knowledge base.
No expensive embeddings - uses keyword matching and file-based indexing.

This is the "Librarian" that helps agents find the right knowledge artifact.
"""

import os
import re
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional, Dict


@dataclass
class KnowledgeHit:
    """A knowledge artifact found in the search."""
    path: Path
    domain: str  # research, patterns, snippets, decisions
    title: str
    preview: str  # First 200 chars of content
    relevance_score: float  # 0.0 to 1.0


class KnowledgeRetriever:
    """
    Librarian for the VIBE AGENCY knowledge base.

    Scans workspaces/vibe_research_framework for knowledge artifacts
    and returns matches based on keyword search.
    """

    DOMAINS = ["research", "patterns", "snippets", "decisions"]
    DEFAULT_PREVIEW_LENGTH = 200

    def __init__(self, vibe_root: Optional[Path] = None):
        """
        Initialize the retriever.

        Args:
            vibe_root: Root directory of the vibe-agency project.
                      If None, uses current working directory.
        """
        if vibe_root is None:
            vibe_root = Path.cwd()

        self.vibe_root = Path(vibe_root)
        self.knowledge_base = self.vibe_root / "workspaces" / "vibe_research_framework"

        if not self.knowledge_base.exists():
            raise FileNotFoundError(
                f"Knowledge base not found at {self.knowledge_base}. "
                "Run GAD-601 scaffolding first."
            )

    def search(
        self,
        query: str,
        domain: str = "all",
        limit: int = 10
    ) -> List[KnowledgeHit]:
        """
        Search for knowledge artifacts matching the query.

        Args:
            query: Search term (case-insensitive)
            domain: Domain to search ("all", "research", "patterns", "snippets", "decisions")
            limit: Maximum number of results

        Returns:
            List of KnowledgeHit objects, sorted by relevance
        """
        if domain != "all" and domain not in self.DOMAINS:
            raise ValueError(f"Unknown domain: {domain}. Valid: {self.DOMAINS}")

        query_lower = query.lower()
        hits: List[KnowledgeHit] = []

        # Determine which domains to search
        domains_to_search = self.DOMAINS if domain == "all" else [domain]

        for search_domain in domains_to_search:
            domain_path = self.knowledge_base / search_domain

            if not domain_path.exists():
                continue

            # Recursively find all markdown files
            for file_path in domain_path.rglob("*.md"):
                # Skip .gitkeep files and hidden files
                if file_path.name.startswith("."):
                    continue

                # Read file content
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                except (OSError, UnicodeDecodeError):
                    continue

                # Calculate relevance score
                relevance = self._calculate_relevance(query_lower, file_path, content)

                # Only include if there's some match
                if relevance > 0:
                    # Extract title from first heading or filename
                    title = self._extract_title(file_path, content)

                    # Get preview
                    preview = self._get_preview(content)

                    hit = KnowledgeHit(
                        path=file_path,
                        domain=search_domain,
                        title=title,
                        preview=preview,
                        relevance_score=relevance
                    )
                    hits.append(hit)

        # Sort by relevance (highest first)
        hits.sort(key=lambda h: h.relevance_score, reverse=True)

        # Return limited results
        return hits[:limit]

    def _calculate_relevance(self, query: str, path: Path, content: str) -> float:
        """
        Calculate relevance score for a match.

        Scoring:
        - Exact match in filename: 1.0
        - Match in title (first line): 0.8
        - Match in first 100 chars: 0.6
        - Match elsewhere in content: 0.3
        """
        score = 0.0

        # Check filename
        if query in path.name.lower():
            score = max(score, 1.0)

        # Check first line (title/heading)
        first_line = content.split("\n")[0].lower() if content else ""
        if query in first_line:
            score = max(score, 0.8)

        # Check first 100 chars
        first_chars = content[:100].lower()
        if query in first_chars:
            score = max(score, 0.6)

        # Check full content
        if query in content.lower():
            score = max(score, 0.3)

        # Bonus: count occurrences for popular matches
        occurrence_count = content.lower().count(query)
        if occurrence_count > 5:
            score = min(1.0, score + 0.2)
        elif occurrence_count > 2:
            score = min(1.0, score + 0.1)

        return score

    def _extract_title(self, path: Path, content: str) -> str:
        """
        Extract a title from the file.

        Prefers the first markdown heading, falls back to filename.
        """
        # Try to find first markdown heading
        lines = content.split("\n")
        for line in lines:
            if line.startswith("#"):
                # Remove markdown symbols and return
                return line.lstrip("#").strip()

        # Fall back to filename (without extension)
        return path.stem.replace("_", " ").replace("-", " ").title()

    def _get_preview(self, content: str, length: int = None) -> str:
        """
        Get a preview of the content.

        Returns first N characters, trimmed to word boundary.
        """
        if length is None:
            length = self.DEFAULT_PREVIEW_LENGTH

        if len(content) <= length:
            return content.strip()

        # Get first N chars and trim to word boundary
        preview = content[:length]

        # Find last space to avoid cutting words
        last_space = preview.rfind(" ")
        if last_space > length * 0.7:  # Only trim if we don't lose too much
            preview = preview[:last_space]

        return preview.strip() + "..."

    def list_domain(self, domain: str) -> List[Path]:
        """
        List all files in a domain.

        Args:
            domain: Domain name (research, patterns, snippets, decisions)

        Returns:
            List of file paths in the domain
        """
        if domain not in self.DOMAINS:
            raise ValueError(f"Unknown domain: {domain}. Valid: {self.DOMAINS}")

        domain_path = self.knowledge_base / domain

        if not domain_path.exists():
            return []

        files = []
        for file_path in domain_path.rglob("*.md"):
            if not file_path.name.startswith("."):
                files.append(file_path)

        return sorted(files)

    def read_file(self, file_path: Path) -> str:
        """
        Read a knowledge artifact file.

        Args:
            file_path: Path to the file (relative to knowledge base)

        Returns:
            File content as string
        """
        # Ensure path is within knowledge base
        full_path = self.knowledge_base / file_path

        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not full_path.is_file():
            raise ValueError(f"Not a file: {file_path}")

        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()

    def get_vibe_root(self) -> Path:
        """Return the vibe-agency root directory."""
        return self.vibe_root
