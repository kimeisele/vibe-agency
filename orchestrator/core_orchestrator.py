"""Re-export from agency_os orchestrator."""
from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path

_target = Path(__file__).parent.parent / "agency_os" / "00_system" / "orchestrator" / "core_orchestrator.py"
_spec = spec_from_file_location("core_orchestrator_real", _target)
_mod = module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_mod)

for name in dir(_mod):
    if not name.startswith('_'):
        globals()[name] = getattr(_mod, name)
