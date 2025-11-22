"""
Tests for ARCH-042 "Senses" tools (ListDirectoryTool, SearchFileTool).
"""

import os
from pathlib import Path
import pytest
from vibe_core.tools.list_directory import ListDirectoryTool
from vibe_core.tools.search_file import SearchFileTool


class TestListDirectoryTool:
    @pytest.fixture
    def tool(self):
        return ListDirectoryTool()

    def test_list_current_directory(self, tool):
        """Test listing the current directory."""
        result = tool.execute({})
        assert result.success is True
        assert "vibe_core" in result.output
        assert "tests" in result.output
        assert "[DIR]" in result.output

    def test_list_subdirectory(self, tool):
        """Test listing a subdirectory."""
        result = tool.execute({"path": "vibe_core"})
        assert result.success is True
        assert "tools" in result.output

    def test_security_block_outside_workspace(self, tool):
        """Test that listing outside workspace is blocked."""
        # Attempt to list root directory
        result = tool.execute({"path": "/"})
        assert result.success is False
        assert "Access denied" in result.error
        assert "outside workspace" in result.error

    def test_security_block_parent_traversal(self, tool):
        """Test that parent traversal is blocked."""
        # Attempt to go up from workspace
        result = tool.execute({"path": "../"})
        assert result.success is False
        assert "Access denied" in result.error

    def test_path_not_found(self, tool):
        """Test listing non-existent path."""
        result = tool.execute({"path": "nonexistent_folder_123"})
        assert result.success is False
        assert "Path not found" in result.error

    def test_path_is_file(self, tool):
        """Test listing a file instead of directory."""
        result = tool.execute({"path": "pyproject.toml"})
        assert result.success is False
        assert "Path is not a directory" in result.error


class TestSearchFileTool:
    @pytest.fixture
    def tool(self):
        return SearchFileTool()

    def test_search_existing_file(self, tool):
        """Test searching for a known file."""
        result = tool.execute({"pattern": "pyproject.toml"})
        assert result.success is True
        assert "pyproject.toml" in result.output

    def test_search_recursive(self, tool):
        """Test recursive search."""
        result = tool.execute({"pattern": "list_directory.py"})
        assert result.success is True
        assert "vibe_core/tools/list_directory.py" in result.output

    def test_search_no_matches(self, tool):
        """Test search with no matches."""
        result = tool.execute({"pattern": "nonexistent_file_pattern_123.xyz"})
        assert result.success is True  # Search succeeded, just found nothing
        assert "No matches found" in result.output

    def test_security_block_outside_workspace(self, tool):
        """Test that searching outside workspace is blocked."""
        result = tool.execute({"pattern": "*", "path": "/"})
        assert result.success is False
        assert "Access denied" in result.error

    def test_security_block_parent_traversal(self, tool):
        """Test that parent traversal is blocked."""
        result = tool.execute({"pattern": "*", "path": "../"})
        assert result.success is False
        assert "Access denied" in result.error
