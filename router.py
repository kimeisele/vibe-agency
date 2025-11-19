"""Alias shim for AgentRouter (playbook router) to satisfy tests without sys.path hacks."""

from importlib import import_module

_mod = import_module("agency_os.00_system.playbook.router".replace("/", "."))
AgentRouter = _mod.AgentRouter
__all__ = ["AgentRouter"]
