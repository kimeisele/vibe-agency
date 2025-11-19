#!/usr/bin/env python3
"""
Test suite for GAD-903: Workflow Loader

Tests the data layer → logic layer connection:
1. YAML loading and parsing
2. Schema validation
3. WorkflowGraph construction
4. Error handling and diagnostics
"""

import tempfile
from pathlib import Path

import pytest
import yaml

# Add playbook directory to path
playbook_dir = Path(__file__).parent.parent / "agency_os" / "00_system" / "playbook"

from executor import WorkflowEdge, WorkflowGraph, WorkflowNode
from loader import WorkflowLoader, WorkflowLoaderError, WorkflowValidationError


class TestWorkflowLoaderInitialization:
    """Tests for WorkflowLoader initialization and schema handling"""

    def test_loader_initializes_with_default_schema(self):
        """Loader finds schema in default location"""
        loader = WorkflowLoader()
        assert loader.schema is not None
        assert "workflow" in loader.schema["properties"]

    def test_loader_raises_on_missing_schema(self):
        """Loader raises error when schema file not found"""
        with pytest.raises(WorkflowLoaderError, match="Schema file not found"):
            WorkflowLoader(schema_path="/nonexistent/schema.json")

    def test_loader_raises_on_invalid_json_schema(self):
        """Loader raises error when schema is invalid JSON"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("{ invalid json")
            temp_path = f.name

        try:
            with pytest.raises(WorkflowLoaderError, match="Invalid JSON"):
                WorkflowLoader(schema_path=temp_path)
        finally:
            Path(temp_path).unlink()

    def test_schema_contains_required_properties(self):
        """Loaded schema has required workflow properties"""
        loader = WorkflowLoader()
        workflow_schema = loader.schema["properties"]["workflow"]
        required_fields = ["id", "name", "intent", "nodes", "edges", "entry_point", "exit_points"]
        for field in required_fields:
            assert field in workflow_schema["properties"]


class TestWorkflowFileLoading:
    """Tests for YAML file loading and parsing"""

    def test_load_valid_yaml_workflow(self):
        """Loader successfully loads valid YAML workflow"""
        loader = WorkflowLoader()
        yaml_path = playbook_dir / "workflows" / "auto_debug.yaml"
        workflow = loader.load_workflow(yaml_path)

        assert workflow.id == "auto_debug"
        assert workflow.name == "Automated Debug & Fix Workflow"
        assert workflow.intent.startswith("Investigate")

    def test_loader_raises_on_missing_file(self):
        """Loader raises error when workflow file not found"""
        loader = WorkflowLoader()
        with pytest.raises(WorkflowLoaderError, match="not found"):
            loader.load_workflow("/nonexistent/workflow.yaml")

    def test_loader_raises_on_invalid_yaml(self):
        """Loader raises error when YAML is malformed"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("{ invalid: yaml: content:")
            temp_path = f.name

        try:
            loader = WorkflowLoader()
            with pytest.raises(WorkflowLoaderError, match="Invalid YAML"):
                loader.load_workflow(temp_path)
        finally:
            Path(temp_path).unlink()

    def test_loader_raises_on_empty_yaml(self):
        """Loader raises error when YAML file is empty"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("")
            temp_path = f.name

        try:
            loader = WorkflowLoader()
            with pytest.raises(WorkflowLoaderError, match="empty"):
                loader.load_workflow(temp_path)
        finally:
            Path(temp_path).unlink()


class TestWorkflowValidation:
    """Tests for schema validation"""

    def test_valid_workflow_passes_validation(self):
        """Valid workflow passes jsonschema validation"""
        loader = WorkflowLoader()
        yaml_path = playbook_dir / "workflows" / "auto_debug.yaml"

        # Should not raise
        workflow = loader.load_workflow(yaml_path)
        assert workflow is not None

    def test_missing_required_field_fails_validation(self):
        """Workflow missing required field fails validation"""
        loader = WorkflowLoader()

        # Create invalid workflow missing 'intent'
        invalid_workflow = {
            "workflow": {
                "id": "test",
                "name": "Test",
                # Missing 'intent'
                "nodes": [],
                "edges": [],
                "entry_point": "start",
                "exit_points": ["end"],
            }
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(invalid_workflow, f)
            temp_path = f.name

        try:
            with pytest.raises(WorkflowValidationError, match="validation failed"):
                loader.load_workflow(temp_path)
        finally:
            Path(temp_path).unlink()

    def test_invalid_node_fails_validation(self):
        """Workflow with invalid node fails validation"""
        loader = WorkflowLoader()

        # Create workflow with node missing 'action'
        invalid_workflow = {
            "workflow": {
                "id": "test",
                "name": "Test",
                "intent": "Test intent",
                "nodes": [{"id": "step1"}],  # Missing 'action'
                "edges": [],
                "entry_point": "step1",
                "exit_points": ["step1"],
            }
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(invalid_workflow, f)
            temp_path = f.name

        try:
            with pytest.raises(WorkflowValidationError):
                loader.load_workflow(temp_path)
        finally:
            Path(temp_path).unlink()


class TestWorkflowGraphConstruction:
    """Tests for converting YAML to WorkflowGraph objects"""

    def test_loader_builds_workflow_graph(self):
        """Loader constructs WorkflowGraph from YAML"""
        loader = WorkflowLoader()
        yaml_path = playbook_dir / "workflows" / "auto_debug.yaml"
        workflow = loader.load_workflow(yaml_path)

        assert isinstance(workflow, WorkflowGraph)
        assert isinstance(workflow.nodes, dict)
        assert isinstance(workflow.edges, list)

    def test_loader_creates_workflow_nodes(self):
        """Loader converts YAML nodes to WorkflowNode objects"""
        loader = WorkflowLoader()
        yaml_path = playbook_dir / "workflows" / "auto_debug.yaml"
        workflow = loader.load_workflow(yaml_path)

        assert len(workflow.nodes) == 4
        assert all(isinstance(node, WorkflowNode) for node in workflow.nodes.values())

        # Verify specific node
        assert "analyze_logs" in workflow.nodes
        analyze_node = workflow.nodes["analyze_logs"]
        assert analyze_node.action == "analyze"
        assert "code_analysis" in analyze_node.required_skills

    def test_loader_creates_workflow_edges(self):
        """Loader converts YAML edges to WorkflowEdge objects"""
        loader = WorkflowLoader()
        yaml_path = playbook_dir / "workflows" / "auto_debug.yaml"
        workflow = loader.load_workflow(yaml_path)

        assert len(workflow.edges) == 3
        assert all(isinstance(edge, WorkflowEdge) for edge in workflow.edges)

        # Verify edge sequence
        assert workflow.edges[0].from_node == "analyze_logs"
        assert workflow.edges[0].to_node == "identify_root_cause"
        assert workflow.edges[0].condition == "success"

    def test_loader_preserves_node_details(self):
        """Loader preserves all node details from YAML"""
        loader = WorkflowLoader()
        yaml_path = playbook_dir / "workflows" / "auto_debug.yaml"
        workflow = loader.load_workflow(yaml_path)

        node = workflow.nodes["generate_fix"]
        assert node.id == "generate_fix"
        assert node.action == "implement"
        assert node.timeout_seconds == 900
        assert "coding" in node.required_skills

    def test_loader_sets_entry_and_exit_points(self):
        """Loader correctly sets entry and exit points"""
        loader = WorkflowLoader()
        yaml_path = playbook_dir / "workflows" / "auto_debug.yaml"
        workflow = loader.load_workflow(yaml_path)

        assert workflow.entry_point == "analyze_logs"
        assert "verify_fix" in workflow.exit_points

    def test_loader_calculates_cost(self):
        """Loader preserves cost estimation"""
        loader = WorkflowLoader()
        yaml_path = playbook_dir / "workflows" / "auto_debug.yaml"
        workflow = loader.load_workflow(yaml_path)

        assert workflow.estimated_cost_usd == 1.50


class TestWorkflowLoaderIntegration:
    """Tests for loader integration with executor"""

    def test_loaded_workflow_is_executable(self):
        """Loaded workflow can be validated by executor"""
        from executor import GraphExecutor, MockAgent

        loader = WorkflowLoader()
        yaml_path = playbook_dir / "workflows" / "auto_debug.yaml"
        workflow = loader.load_workflow(yaml_path)

        # Create a capable mock agent with all required skills for auto_debug
        capable_agent = MockAgent(
            skills=[
                "code_analysis",
                "debugging",
                "pattern_recognition",
                "reasoning",
                "architecture_understanding",
                "coding",
                "testing",
                "refactoring",
                "validation",
            ]
        )

        executor = GraphExecutor()
        executor.set_agent(capable_agent)
        is_valid, message = executor.validate_workflow(workflow)
        assert is_valid
        assert "valid" in message.lower()

    def test_loaded_workflow_dry_run(self):
        """Loaded workflow can be dry-run by executor"""
        from executor import GraphExecutor, MockAgent

        loader = WorkflowLoader()
        yaml_path = playbook_dir / "workflows" / "auto_debug.yaml"
        workflow = loader.load_workflow(yaml_path)

        # Create a capable mock agent with all required skills for auto_debug
        capable_agent = MockAgent(
            skills=[
                "code_analysis",
                "debugging",
                "pattern_recognition",
                "reasoning",
                "architecture_understanding",
                "coding",
                "testing",
                "refactoring",
                "validation",
            ]
        )

        executor = GraphExecutor()
        executor.set_agent(capable_agent)
        result = executor.dry_run(workflow)

        assert result["is_valid"]
        assert result["workflow_id"] == "auto_debug"
        assert len(result["nodes"]) == 4
        assert result["execution_plan"]["execution_order"] == [
            "analyze_logs",
            "identify_root_cause",
            "generate_fix",
            "verify_fix",
        ]

    def test_loaded_workflow_detects_cycles(self):
        """Loader catches circular dependencies"""
        loader = WorkflowLoader()

        # Create workflow with circular dependency
        circular_workflow = {
            "workflow": {
                "id": "circular",
                "name": "Circular Workflow",
                "intent": "Test circular dependency detection",
                "nodes": [
                    {"id": "step1", "action": "analyze"},
                    {"id": "step2", "action": "implement"},
                    {"id": "step3", "action": "test"},
                ],
                "edges": [
                    {"from": "step1", "to": "step2"},
                    {"from": "step2", "to": "step3"},
                    {"from": "step3", "to": "step1"},  # Creates cycle
                ],
                "entry_point": "step1",
                "exit_points": ["step3"],
            }
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(circular_workflow, f)
            temp_path = f.name

        try:
            workflow = loader.load_workflow(temp_path)

            # Executor should detect the cycle
            from executor import GraphExecutor

            executor = GraphExecutor()
            is_valid, message = executor.validate_workflow(workflow)
            assert not is_valid
            assert "circular" in message.lower()
        finally:
            Path(temp_path).unlink()


class TestWorkflowDirectoryLoading:
    """Tests for loading multiple workflows from directory"""

    def test_load_workflows_from_directory(self):
        """Loader can load all workflows from directory"""
        loader = WorkflowLoader()
        workflows_dir = playbook_dir / "workflows"

        workflows = loader.load_workflows_from_directory(workflows_dir)

        # Should at least have auto_debug
        assert "auto_debug" in workflows
        assert workflows["auto_debug"].name == "Automated Debug & Fix Workflow"

    def test_directory_loader_skips_schema_files(self):
        """Loader skips schema and other special files"""
        loader = WorkflowLoader()
        workflows_dir = playbook_dir / "workflows"

        workflows = loader.load_workflows_from_directory(workflows_dir)

        # Should not try to load _schema.json as a workflow
        assert "_schema" not in [w.id.lower() for w in workflows.values()]

    def test_directory_loader_handles_invalid_files(self):
        """Loader gracefully handles invalid files in directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create one valid workflow
            valid_workflow = {
                "workflow": {
                    "id": "valid",
                    "name": "Valid",
                    "intent": "Valid intent",
                    "nodes": [{"id": "start", "action": "analyze"}],
                    "edges": [],
                    "entry_point": "start",
                    "exit_points": ["start"],
                }
            }
            with open(tmpdir / "valid.yaml", "w") as f:
                yaml.dump(valid_workflow, f)

            # Create one invalid workflow
            with open(tmpdir / "invalid.yaml", "w") as f:
                f.write("{ invalid yaml content")

            loader = WorkflowLoader()
            workflows = loader.load_workflows_from_directory(tmpdir)

            # Should load the valid one and skip the invalid one
            assert "valid" in workflows
            assert len(workflows) == 1


class TestAutoDebugWorkflow:
    """Specific tests for the auto_debug.yaml workflow"""

    def test_auto_debug_has_four_steps(self):
        """auto_debug workflow has all four debugging steps"""
        loader = WorkflowLoader()
        yaml_path = playbook_dir / "workflows" / "auto_debug.yaml"
        workflow = loader.load_workflow(yaml_path)

        node_ids = list(workflow.nodes.keys())
        assert "analyze_logs" in node_ids
        assert "identify_root_cause" in node_ids
        assert "generate_fix" in node_ids
        assert "verify_fix" in node_ids

    def test_auto_debug_has_correct_skills(self):
        """auto_debug nodes have appropriate required skills"""
        loader = WorkflowLoader()
        yaml_path = playbook_dir / "workflows" / "auto_debug.yaml"
        workflow = loader.load_workflow(yaml_path)

        # analyze_logs needs code_analysis
        assert "code_analysis" in workflow.nodes["analyze_logs"].required_skills

        # identify_root_cause needs reasoning
        assert "reasoning" in workflow.nodes["identify_root_cause"].required_skills

        # generate_fix needs coding
        assert "coding" in workflow.nodes["generate_fix"].required_skills

        # verify_fix needs testing
        assert "testing" in workflow.nodes["verify_fix"].required_skills

    def test_auto_debug_linear_execution_order(self):
        """auto_debug steps execute in linear order"""
        from executor import GraphExecutor

        loader = WorkflowLoader()
        yaml_path = playbook_dir / "workflows" / "auto_debug.yaml"
        workflow = loader.load_workflow(yaml_path)

        executor = GraphExecutor()
        plan = executor._topological_sort(workflow)

        expected_order = ["analyze_logs", "identify_root_cause", "generate_fix", "verify_fix"]
        assert plan.execution_order == expected_order

    def test_auto_debug_cost_estimation(self):
        """auto_debug has cost estimation"""
        loader = WorkflowLoader()
        yaml_path = playbook_dir / "workflows" / "auto_debug.yaml"
        workflow = loader.load_workflow(yaml_path)

        assert workflow.estimated_cost_usd == 1.50


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
