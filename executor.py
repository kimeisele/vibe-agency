"""Import shim: executor classes from playbook layer."""
import sys
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec

_playbook_executor = Path(__file__).parent / "agency_os" / "00_system" / "playbook" / "executor.py"
_spec = spec_from_file_location("executor_original", _playbook_executor)
_executor_module = module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_executor_module)

GraphExecutor = _executor_module.GraphExecutor
WorkflowGraph = _executor_module.WorkflowGraph
WorkflowNode = _executor_module.WorkflowNode
WorkflowEdge = _executor_module.WorkflowEdge
MockAgent = _executor_module.MockAgent
ExecutionStatus = _executor_module.ExecutionStatus
ExecutionResult = _executor_module.ExecutionResult
ExecutionPlan = _executor_module.ExecutionPlan

__all__ = [
    "GraphExecutor",
    "WorkflowGraph",
    "WorkflowNode",
    "WorkflowEdge",
    "MockAgent",
    "ExecutionStatus",
    "ExecutionResult",
    "ExecutionPlan",
]
