"""
Tests for SimpleLLMAgent with tool-use capability (ARCH-027)

Verifies that LLM agents can detect and execute tool calls.
"""

import tempfile
from pathlib import Path

from vibe_core.agents.llm_agent import SimpleLLMAgent
from vibe_core.scheduling import Task
from vibe_core.tools import ReadFileTool, ToolRegistry, WriteFileTool

# ============================================================================
# MOCK LLM PROVIDER
# ============================================================================


class MockLLMProviderWithTools:
    """Mock LLM provider that returns tool calls"""

    def __init__(self, response: str = "Hello!"):
        self.response = response
        self.system_prompt = "You are a helpful assistant"
        self.call_count = 0

    def chat(self, messages, model=None):
        """Mock chat method that returns configured response"""
        self.call_count += 1
        self.last_messages = messages
        return self.response


# ============================================================================
# TESTS: TOOL REGISTRY
# ============================================================================


def test_tool_registry_register():
    """ToolRegistry should register tools"""
    registry = ToolRegistry()
    registry.register(ReadFileTool())

    assert registry.has("read_file")
    assert "read_file" in registry.list_tools()


def test_tool_registry_get():
    """ToolRegistry should retrieve registered tools"""
    registry = ToolRegistry()
    tool = ReadFileTool()
    registry.register(tool)

    retrieved = registry.get("read_file")
    assert retrieved is tool


def test_tool_registry_execute_success():
    """ToolRegistry should execute tool calls successfully"""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
        f.write("Hello, world!")
        temp_path = f.name

    try:
        from vibe_core.tools.tool_protocol import ToolCall

        registry = ToolRegistry()
        registry.register(ReadFileTool())

        call = ToolCall(tool_name="read_file", parameters={"path": temp_path})
        result = registry.execute(call)

        assert result.success is True
        assert result.output == "Hello, world!"
    finally:
        Path(temp_path).unlink()


def test_tool_registry_execute_unknown_tool():
    """ToolRegistry should return error for unknown tools"""
    from vibe_core.tools.tool_protocol import ToolCall

    registry = ToolRegistry()

    call = ToolCall(tool_name="nonexistent_tool", parameters={})
    result = registry.execute(call)

    assert result.success is False
    assert "not found in registry" in result.error


# ============================================================================
# TESTS: FILE TOOLS
# ============================================================================


def test_read_file_tool_success():
    """ReadFileTool should read file content"""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
        f.write("Test content")
        temp_path = f.name

    try:
        tool = ReadFileTool()
        result = tool.execute({"path": temp_path})

        assert result.success is True
        assert result.output == "Test content"
        assert result.metadata["path"] == temp_path
    finally:
        Path(temp_path).unlink()


def test_read_file_tool_not_found():
    """ReadFileTool should return error for missing files"""
    tool = ReadFileTool()
    result = tool.execute({"path": "/nonexistent/file.txt"})

    assert result.success is False
    assert "File not found" in result.error


def test_write_file_tool_success():
    """WriteFileTool should write file content"""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir) / "test.txt"

        tool = WriteFileTool()
        result = tool.execute({"path": str(temp_path), "content": "Hello, world!"})

        assert result.success is True
        assert temp_path.exists()
        assert temp_path.read_text() == "Hello, world!"


def test_write_file_tool_creates_dirs():
    """WriteFileTool should create parent dirs with create_dirs=true"""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir) / "subdir" / "test.txt"

        tool = WriteFileTool()
        result = tool.execute(
            {
                "path": str(temp_path),
                "content": "Hello!",
                "create_dirs": True,
            }
        )

        assert result.success is True
        assert temp_path.exists()
        assert temp_path.read_text() == "Hello!"


# ============================================================================
# TESTS: SIMPLELLLMAGENT WITH TOOLS
# ============================================================================


def test_llm_agent_with_tool_registry():
    """SimpleLLMAgent should accept tool_registry parameter"""
    provider = MockLLMProviderWithTools()
    registry = ToolRegistry()
    registry.register(ReadFileTool())

    agent = SimpleLLMAgent(
        agent_id="test-agent",
        provider=provider,
        tool_registry=registry,
    )

    assert agent.tool_registry is registry


def test_llm_agent_includes_tools_in_system_prompt():
    """SimpleLLMAgent should include tool descriptions in system prompt"""
    provider = MockLLMProviderWithTools()
    registry = ToolRegistry()
    registry.register(ReadFileTool())

    agent = SimpleLLMAgent(
        agent_id="test-agent",
        provider=provider,
        system_prompt="You are helpful",
        tool_registry=registry,
    )

    task = Task(agent_id="test-agent", payload={"user_message": "Hello"})
    _ = agent.process(task)

    # Check that system prompt includes tool descriptions
    system_message = provider.last_messages[0]
    assert system_message["role"] == "system"
    assert "Available tools" in system_message["content"]
    assert "read_file" in system_message["content"]


def test_llm_agent_detects_tool_call():
    """SimpleLLMAgent should detect tool call in LLM response"""
    provider = MockLLMProviderWithTools(
        response='{"tool": "read_file", "parameters": {"path": "/tmp/test.txt"}}'
    )
    registry = ToolRegistry()
    registry.register(ReadFileTool())

    agent = SimpleLLMAgent(
        agent_id="test-agent",
        provider=provider,
        tool_registry=registry,
    )

    # Create temp file for reading
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
        f.write("File content")
        temp_path = f.name

    try:
        # Override provider response to use actual file path
        provider.response = f'{{"tool": "read_file", "parameters": {{"path": "{temp_path}"}}}}'

        task = Task(agent_id="test-agent", payload={"user_message": "Read the file"})
        result = agent.process(task)

        # Verify tool call was detected and executed
        assert result.success is True
        assert result.output["tool_call"] is not None
        assert result.output["tool_call"]["tool"] == "read_file"
        assert result.output["tool_call"]["success"] is True
        assert result.output["tool_call"]["output"] == "File content"
    finally:
        Path(temp_path).unlink()


def test_llm_agent_no_tool_call_without_registry():
    """SimpleLLMAgent without tool_registry should not execute tools"""
    provider = MockLLMProviderWithTools(
        response='{"tool": "read_file", "parameters": {"path": "/tmp/test.txt"}}'
    )

    agent = SimpleLLMAgent(agent_id="test-agent", provider=provider, tool_registry=None)

    task = Task(agent_id="test-agent", payload={"user_message": "Hello"})
    result = agent.process(task)

    # Tool call should not be detected/executed
    assert result.output["tool_call"] is None


def test_llm_agent_write_file_via_tool_call():
    """SimpleLLMAgent should execute WriteFileTool via tool call"""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir) / "output.txt"

        provider = MockLLMProviderWithTools(
            response=f'{{"tool": "write_file", "parameters": {{"path": "{temp_path}", "content": "Generated content"}}}}'
        )
        registry = ToolRegistry()
        registry.register(WriteFileTool())

        agent = SimpleLLMAgent(
            agent_id="test-agent",
            provider=provider,
            tool_registry=registry,
        )

        task = Task(agent_id="test-agent", payload={"user_message": "Write a file"})
        result = agent.process(task)

        # Verify tool call executed
        assert result.output["tool_call"] is not None
        assert result.output["tool_call"]["tool"] == "write_file"
        assert result.output["tool_call"]["success"] is True

        # Verify file was created
        assert temp_path.exists()
        assert temp_path.read_text() == "Generated content"


# ============================================================================
# TESTS: INTEGRATION WITH KERNEL
# ============================================================================


def test_llm_agent_with_tools_via_kernel():
    """Kernel should dispatch LLM agent with tool capability"""
    from vibe_core.kernel import VibeKernel

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
        f.write("Kernel test content")
        temp_path = f.name

    try:
        provider = MockLLMProviderWithTools(
            response=f'{{"tool": "read_file", "parameters": {{"path": "{temp_path}"}}}}'
        )
        registry = ToolRegistry()
        registry.register(ReadFileTool())

        agent = SimpleLLMAgent(
            agent_id="llm-agent",
            provider=provider,
            tool_registry=registry,
        )

        kernel = VibeKernel(ledger_path=":memory:")
        kernel.boot()
        kernel.register_agent(agent)

        # Submit task
        task = Task(agent_id="llm-agent", payload={"user_message": "Read the file"})
        _ = kernel.submit(task)

        # Execute via kernel
        busy = kernel.tick()

        assert busy is True

        # Query ledger
        history = kernel.ledger.get_history(limit=1)
        assert len(history) == 1
        assert history[0]["status"] == "COMPLETED"
        # get_history() already deserializes JSON
        output_data = history[0]["output_result"]
        assert output_data["success"] is True
        assert output_data["output"]["tool_call"]["success"] is True
        assert output_data["output"]["tool_call"]["output"] == "Kernel test content"
    finally:
        Path(temp_path).unlink()
