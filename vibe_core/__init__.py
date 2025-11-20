"""
Vibe Core - The Operating System Kernel

Domain-agnostic infrastructure for building AI-powered applications.

Components:
- config: Configuration management (Phoenix)
- store: Persistence layer (SQLite)
- runtime: LLM invocation, prompt composition, boot sequence
- playbook: Workflow engine
- specialists: Base classes for specialist agents
- task_management: Roadmap and task management
- tools: Generic tool implementations
"""

__version__ = "2.0.0"
__all__ = ["config"]
