#!/usr/bin/env python3
"""
Tests for The Archivist Cartridge - ARCH-050

Tests the knowledge base builder functionality.
"""

import json
import tempfile
from pathlib import Path

import pytest

from vibe_core.cartridges.archivist import ArchivistCartridge
from vibe_core.cartridges.registry import CartridgeRegistry


class TestArchivistCartridge:
    """Tests for ArchivistCartridge functionality."""

    @pytest.fixture
    def archivist(self):
        """Create an Archivist instance."""
        return ArchivistCartridge()

    @pytest.fixture
    def temp_documents(self):
        """Create temporary test documents."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create test documents
            (tmpdir / "doc1.md").write_text("# Document 1\n\nThis is a test document.")
            (tmpdir / "doc2.txt").write_text("This is another test document in plain text.")
            (tmpdir / "subdir").mkdir()
            (tmpdir / "subdir" / "doc3.md").write_text("# Nested Document\n\nStored in subfolder.")

            yield tmpdir

    def test_cartridge_initialization(self, archivist):
        """Test that Archivist initializes correctly."""
        assert archivist.name == "archivist"
        assert archivist.version == "1.0.0"
        assert archivist.description is not None
        assert len(archivist.supported_formats) > 0

    def test_cartridge_spec(self, archivist):
        """Test that Archivist spec is correct."""
        spec = archivist.get_spec()
        assert spec.name == "archivist"
        assert spec.version == "1.0.0"
        assert spec.offline_capable is True

    def test_scan_directory_basic(self, archivist, temp_documents):
        """Test scanning a directory for documents."""
        docs = archivist.scan_directory(str(temp_documents))
        assert len(docs) == 3
        assert all("name" in doc and "path" in doc for doc in docs)

    def test_scan_directory_nonexistent(self, archivist):
        """Test scanning a nonexistent directory."""
        docs = archivist.scan_directory("/nonexistent/path")
        assert docs == []

    def test_extract_text_markdown(self, archivist, temp_documents):
        """Test extracting text from Markdown file."""
        doc_path = temp_documents / "doc1.md"
        text = archivist.extract_text(str(doc_path))

        assert text is not None
        assert "Document 1" in text
        assert "test document" in text

    def test_extract_text_plaintext(self, archivist, temp_documents):
        """Test extracting text from plain text file."""
        doc_path = temp_documents / "doc2.txt"
        text = archivist.extract_text(str(doc_path))

        assert text is not None
        assert "another test document" in text

    def test_extract_text_nonexistent(self, archivist):
        """Test extracting from nonexistent file."""
        text = archivist.extract_text("/nonexistent/file.txt")
        assert text is None

    def test_summarize_basic(self, archivist):
        """Test summarization functionality."""
        text = "This is a test document. " * 50  # Create a longer text
        summary = archivist.summarize(text)

        assert summary is not None
        assert len(summary) > 0

    def test_summarize_respects_max_length(self, archivist):
        """Test that summary respects max_length parameter."""
        text = "This is a test document. " * 100
        max_length = 100
        summary = archivist.summarize(text, max_length=max_length)

        # Allow some flexibility due to truncation
        assert len(summary) <= max_length + 50

    def test_build_index_empty_folder(self, archivist):
        """Test building index for empty folder."""
        with tempfile.TemporaryDirectory() as tmpdir:
            index = archivist.build_index(tmpdir)
            assert index["status"] == "empty"
            assert index["documents"] == []

    def test_build_index_success(self, archivist, temp_documents):
        """Test building a complete knowledge index."""
        index = archivist.build_index(str(temp_documents))

        assert index["total_documents"] == 3
        assert len(index["documents"]) == 3
        assert all("name" in doc and "summary" in doc for doc in index["documents"])

    def test_build_index_with_output(self, archivist, temp_documents):
        """Test building index and saving to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "index.json"

            _ = archivist.build_index(str(temp_documents), str(output_path))

            # Check output file exists
            assert output_path.exists()

            # Verify saved JSON
            with open(output_path) as f:
                saved_index = json.load(f)

            assert saved_index["total_documents"] == 3
            assert len(saved_index["documents"]) == 3

    def test_execution_count_increments(self, archivist, temp_documents):
        """Test that execution_count increments after build_index."""
        initial_count = archivist.execution_count
        archivist.build_index(str(temp_documents))
        assert archivist.execution_count == initial_count + 1

    def test_report_status(self, archivist):
        """Test cartridge status reporting."""
        status = archivist.report_status()

        assert status["name"] == "archivist"
        assert "supported_formats" in status
        assert "max_document_size_mb" in status


class TestCartridgeRegistry:
    """Tests for cartridge registry integration."""

    def test_registry_discovers_archivist(self):
        """Test that CartridgeRegistry auto-discovers Archivist."""
        registry = CartridgeRegistry()
        cartridges = registry.get_cartridge_names()

        assert "archivist" in cartridges

    def test_registry_get_archivist_instance(self):
        """Test getting Archivist instance from registry."""
        registry = CartridgeRegistry()
        archivist = registry.get_cartridge("archivist")

        assert isinstance(archivist, ArchivistCartridge)
        assert archivist.name == "archivist"

    def test_registry_caching(self):
        """Test that registry caches cartridge instances."""
        registry = CartridgeRegistry()
        archivist1 = registry.get_cartridge("archivist", cached=True)
        archivist2 = registry.get_cartridge("archivist", cached=True)

        # Should be the same instance
        assert archivist1 is archivist2

    def test_registry_no_cache(self):
        """Test getting new instance when caching disabled."""
        registry = CartridgeRegistry()
        archivist1 = registry.get_cartridge("archivist", cached=False)
        archivist2 = registry.get_cartridge("archivist", cached=False)

        # Should be different instances
        assert archivist1 is not archivist2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
