"""
GAD-302: PERSONA FRAMEWORK

Specialized agent personas inheriting from BaseAgent.

Each persona specializes in a specific domain:
- Coder: Python/JavaScript development
- Researcher: Investigation and analysis
- Reviewer: Code quality and architecture
- Architect: System design and decisions
"""

import importlib.util
from pathlib import Path

# Use dynamic imports to handle numeric directory names
persona_dir = Path(__file__).parent

# Load Coder
spec = importlib.util.spec_from_file_location("coder", persona_dir / "coder.py")
coder_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(coder_module)
CoderAgent = coder_module.CoderAgent

# Load Researcher
spec = importlib.util.spec_from_file_location("researcher", persona_dir / "researcher.py")
researcher_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(researcher_module)
ResearcherAgent = researcher_module.ResearcherAgent

# Load Reviewer
spec = importlib.util.spec_from_file_location("reviewer", persona_dir / "reviewer.py")
reviewer_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reviewer_module)
ReviewerAgent = reviewer_module.ReviewerAgent

# Load Architect
spec = importlib.util.spec_from_file_location("architect", persona_dir / "architect.py")
architect_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(architect_module)
ArchitectAgent = architect_module.ArchitectAgent

__all__ = [
    "CoderAgent",
    "ResearcherAgent",
    "ReviewerAgent",
    "ArchitectAgent",
]
