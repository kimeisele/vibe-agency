"""Alias shim for LLMClient and BudgetExceededError."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

_path = Path(__file__).resolve().parent / "agency_os" / "00_system" / "runtime" / "llm_client.py"
_spec = spec_from_file_location("llm_client_original", _path)
module = module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(module)  # type: ignore
LLMClient = module.LLMClient
BudgetExceededError = getattr(module, "BudgetExceededError", None)
__all__ = ["BudgetExceededError", "LLMClient"]
