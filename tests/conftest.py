"""Pytest configuration for vibe-agency tests.

With proper package installation (uv pip install -e .), all imports work naturally.
No sys.path manipulation needed.
"""

import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

# Legacy backward compatibility: Create module aliases for old test code
# These map old bare imports to new package imports
try:
    import agency_os.core_system.orchestrator as orchestrator_module
    import agency_os.core_system.playbook.executor as executor_module
    import agency_os.core_system.playbook.loader as loader_module
    import agency_os.core_system.playbook.router as router_module
    import agency_os.core_system.runtime.prompt_registry as prompt_registry_module

    sys.modules["orchestrator"] = orchestrator_module
    sys.modules["executor"] = executor_module
    sys.modules["prompt_registry"] = prompt_registry_module
    sys.modules["router"] = router_module
    sys.modules["loader"] = loader_module
    sys.modules["agency_os_orchestrator"] = orchestrator_module
except ImportError as e:
    # If package not installed, provide helpful error message
    print(
        f"\n❌ Import error: {e}\n"
        "Please install the package in editable mode:\n"
        "  uv pip install -e .\n"
        "Or:\n"
        "  make install\n"
    )
    raise

# Load legacy_config_loader dynamically (it's not in the main package)
repo_root = Path(__file__).parent.parent
legacy_config_path = repo_root / "config" / "legacy_config_loader.py"
if legacy_config_path.exists():
    spec = spec_from_file_location("legacy_config_loader", legacy_config_path)
    if spec and spec.loader:
        legacy_config = module_from_spec(spec)
        sys.modules["legacy_config_loader"] = legacy_config
        spec.loader.exec_module(legacy_config)

# Load handlers module with fallback
try:
    import agency_os.core_system.orchestrator.handlers as handlers_module

    sys.modules["handlers"] = handlers_module
except ImportError:
    pass  # handlers module might not exist in all configs
