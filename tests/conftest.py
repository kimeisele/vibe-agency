"""Pytest configuration for vibe-agency tests."""

import sys
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec

# Add project root to sys.path for proper package discovery
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))

# Dynamically load modules from 00_system (which has numeric prefix, not importable directly)
def _load_module_from_path(module_name: str, file_path: str) -> None:
    """Load a module from a file path and inject into sys.modules."""
    target = repo_root / file_path
    if target.exists():
        spec = spec_from_file_location(module_name, target)
        if spec and spec.loader:
            module = module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

# Load real modules (no longer shims in root)
_load_module_from_path("orchestrator", "agency_os/00_system/orchestrator/__init__.py")
_load_module_from_path("executor", "agency_os/00_system/playbook/executor.py")
_load_module_from_path("prompt_registry", "agency_os/00_system/runtime/prompt_registry.py")
_load_module_from_path("router", "agency_os/00_system/playbook/router.py")
_load_module_from_path("loader", "agency_os/00_system/playbook/loader.py")
_load_module_from_path("legacy_config_loader", "config/legacy_config_loader.py")

# Load handlers module
_load_module_from_path("handlers", "agency_os/00_system/orchestrator/handlers/__init__.py")

# Legacy shim names for backward compatibility (map to real modules)
sys.modules["agency_os_orchestrator"] = sys.modules.get("orchestrator", type(sys)("orchestrator"))


