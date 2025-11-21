"""
Tests for ToolRegistry (ARCH-027).

This module tests the tool registry system including:
- Tool registration
- Tool execution
- Governance integration (ARCH-029)
- Error handling
"""

from vibe_core.governance import InvariantChecker
from vibe_core.tools import ReadFileTool, ToolRegistry, WriteFileTool


class MockTool:
    """Mock tool for testing."""

    def __init__(self, return_value="mock result"):
        self.return_value = return_value
        self.called_with = None

    def execute(self, **kwargs):
        self.called_with = kwargs
        return self.return_value


class TestToolRegistryBasics:
    """Test basic ToolRegistry functionality."""

    def test_initialize_without_governance(self):
        """Test that registry can be created without governance checker."""
        registry = ToolRegistry(invariant_checker=None)
        assert registry is not None
        assert not registry.has_governance
        assert registry.tool_count == 0

    def test_initialize_with_governance(self):
        """Test that registry can be created with governance checker."""
        checker = InvariantChecker("tests/fixtures/test_soul.yaml")
        registry = ToolRegistry(invariant_checker=checker)

        assert registry is not None
        assert registry.has_governance
        assert registry.tool_count == 0

    def test_register_tool(self):
        """Test registering a tool."""
        registry = ToolRegistry()
        tool = MockTool()

        registry.register("mock_tool", tool)

        assert registry.has_tool("mock_tool")
        assert registry.tool_count == 1
        assert "mock_tool" in registry.list_tools()

    def test_register_multiple_tools(self):
        """Test registering multiple tools."""
        registry = ToolRegistry()

        registry.register("tool1", MockTool("result1"))
        registry.register("tool2", MockTool("result2"))
        registry.register("tool3", MockTool("result3"))

        assert registry.tool_count == 3
        assert registry.has_tool("tool1")
        assert registry.has_tool("tool2")
        assert registry.has_tool("tool3")


class TestToolExecution:
    """Test tool execution through registry."""

    def test_execute_tool_success(self):
        """Test successful tool execution."""
        registry = ToolRegistry()
        tool = MockTool(return_value="success!")

        registry.register("test_tool", tool)
        result = registry.execute("test_tool", param1="value1", param2="value2")

        assert result["success"] is True
        assert result["result"] == "success!"
        assert tool.called_with == {"param1": "value1", "param2": "value2"}

    def test_execute_nonexistent_tool(self):
        """Test executing a tool that doesn't exist."""
        registry = ToolRegistry()

        result = registry.execute("nonexistent_tool", param="value")

        assert result["success"] is False
        assert "not found" in result["error"].lower()

    def test_execute_tool_with_exception(self):
        """Test handling tool execution exceptions."""

        class FailingTool:
            def execute(self, **kwargs):
                raise RuntimeError("Tool failed!")

        registry = ToolRegistry()
        registry.register("failing_tool", FailingTool())

        result = registry.execute("failing_tool", param="value")

        assert result["success"] is False
        assert "Tool failed!" in result["error"]


class TestGovernanceIntegration:
    """Test governance integration with InvariantChecker."""

    def test_governance_blocks_dangerous_paths(self):
        """Test that governance blocks dangerous file paths."""
        checker = InvariantChecker("tests/fixtures/test_soul.yaml")
        registry = ToolRegistry(invariant_checker=checker)
        registry.register("write_file", MockTool())

        # Try to write to .git (should be blocked by Soul)
        result = registry.execute("write_file", path=".git/config", content="bad")

        assert result["success"] is False
        assert result.get("blocked") is True
        assert "Governance Violation" in result["error"]

    def test_governance_allows_safe_paths(self):
        """Test that governance allows safe file paths."""
        checker = InvariantChecker("tests/fixtures/test_soul.yaml")
        registry = ToolRegistry(invariant_checker=checker)
        tool = MockTool(return_value="file written")
        registry.register("write_file", tool)

        # Try to write to safe location
        result = registry.execute("write_file", path="docs/test.md", content="ok")

        assert result["success"] is True
        assert result["result"] == "file written"

    def test_governance_blocks_kernel_modification(self):
        """Test that governance blocks kernel.py modification."""
        checker = InvariantChecker("tests/fixtures/test_soul.yaml")
        registry = ToolRegistry(invariant_checker=checker)
        registry.register("write_file", MockTool())

        # Try to modify kernel.py (exact path match)
        result = registry.execute(
            "write_file", path="vibe_core/kernel.py", content="hacked"
        )

        assert result["success"] is False
        assert result.get("blocked") is True
        assert "Governance Violation" in result["error"]

    def test_governance_blocks_directory_traversal(self):
        """Test that governance blocks directory traversal."""
        checker = InvariantChecker("tests/fixtures/test_soul.yaml")
        registry = ToolRegistry(invariant_checker=checker)
        registry.register("read_file", MockTool())

        # Try to escape sandbox
        result = registry.execute("read_file", path="../../../etc/passwd")

        assert result["success"] is False
        assert result.get("blocked") is True

    def test_no_governance_allows_everything(self):
        """Test that without governance, all operations are allowed."""
        registry = ToolRegistry(invariant_checker=None)
        tool = MockTool(return_value="executed")
        registry.register("write_file", tool)

        # Try dangerous path (should work without governance)
        result = registry.execute("write_file", path=".git/config", content="test")

        assert result["success"] is True
        assert result["result"] == "executed"


class TestFileTools:
    """Test actual file tools (ReadFileTool, WriteFileTool)."""

    def test_write_and_read_file(self, tmp_path):
        """Test writing and reading a file."""
        registry = ToolRegistry()
        registry.register("write_file", WriteFileTool())
        registry.register("read_file", ReadFileTool())

        # Write file
        test_file = tmp_path / "test.txt"
        content = "Hello, World!"

        write_result = registry.execute(
            "write_file", path=str(test_file), content=content
        )

        assert write_result["success"] is True
        assert write_result["result"]["bytes_written"] == len(content)

        # Read file
        read_result = registry.execute("read_file", path=str(test_file))

        assert read_result["success"] is True
        assert read_result["result"]["content"] == content

    def test_write_file_creates_directories(self, tmp_path):
        """Test that WriteFileTool creates parent directories."""
        registry = ToolRegistry()
        registry.register("write_file", WriteFileTool())

        # Write to nested path that doesn't exist
        nested_file = tmp_path / "level1" / "level2" / "test.txt"

        result = registry.execute(
            "write_file",
            path=str(nested_file),
            content="nested",
            create_dirs=True,
        )

        assert result["success"] is True
        assert nested_file.exists()

    def test_read_nonexistent_file(self):
        """Test reading a file that doesn't exist."""
        registry = ToolRegistry()
        registry.register("read_file", ReadFileTool())

        result = registry.execute("read_file", path="/nonexistent/file.txt")

        assert result["success"] is False
        assert "error" in result


class TestListAndQuery:
    """Test tool listing and query methods."""

    def test_list_tools(self):
        """Test listing registered tools."""
        registry = ToolRegistry()
        registry.register("tool1", MockTool())
        registry.register("tool2", MockTool())

        tools = registry.list_tools()

        assert len(tools) == 2
        assert "tool1" in tools
        assert "tool2" in tools

    def test_has_tool(self):
        """Test checking if tool exists."""
        registry = ToolRegistry()
        registry.register("existing_tool", MockTool())

        assert registry.has_tool("existing_tool")
        assert not registry.has_tool("nonexistent_tool")

    def test_tool_count(self):
        """Test tool count property."""
        registry = ToolRegistry()

        assert registry.tool_count == 0

        registry.register("tool1", MockTool())
        assert registry.tool_count == 1

        registry.register("tool2", MockTool())
        assert registry.tool_count == 2
