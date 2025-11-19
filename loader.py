"""Alias shim for workflow loader functions/classes."""

from importlib import import_module

_mod = import_module("agency_os.00_system.playbook.loader".replace("/", "."))
WorkflowLoader = _mod.WorkflowLoader
WorkflowLoaderError = _mod.WorkflowLoaderError
WorkflowValidationError = _mod.WorkflowValidationError
load_workflow = _mod.load_workflow
__all__ = [
    "WorkflowLoader",
    "WorkflowLoaderError",
    "WorkflowValidationError",
    "load_workflow",
]
