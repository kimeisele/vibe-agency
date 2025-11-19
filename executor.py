"""Alias shim exposing GraphExecutor and related workflow classes without sys.path hacks.

Tests import `executor` expecting GraphExecutor, WorkflowGraph, WorkflowNode, MockAgent.
This module re-exports from agency_os.00_system.playbook.executor.
"""

from importlib import import_module

_mod = import_module("agency_os.00_system.playbook.executor".replace("/", "."))
GraphExecutor = _mod.GraphExecutor
WorkflowGraph = getattr(_mod, "WorkflowGraph", None)
WorkflowNode = getattr(_mod, "WorkflowNode", None)
WorkflowEdge = getattr(_mod, "WorkflowEdge", None)
MockAgent = getattr(_mod, "MockAgent", None)
ExecutionStatus = getattr(_mod, "ExecutionStatus", None)
ExecutionResult = getattr(_mod, "ExecutionResult", None)
ExecutionPlan = getattr(_mod, "ExecutionPlan", None)
__all__ = [
    "ExecutionPlan",
    "ExecutionResult",
    "ExecutionStatus",
    "GraphExecutor",
    "MockAgent",
    "WorkflowEdge",
    "WorkflowGraph",
    "WorkflowNode",
]
