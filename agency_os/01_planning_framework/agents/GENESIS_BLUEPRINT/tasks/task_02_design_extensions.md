# Task: Design Extension Modules

**PHASE:** 2
**TASK ID:** design_extensions
**TRIGGER:** core_modules_selection.json available

---

## OBJECTIVE

Map each feature from feature_spec.json to one extension module. Extensions implement features using core modules + external libraries.

---

## INPUT ARTIFACTS

### Required:
1. **feature_spec.json** (from VIBE_ALIGNER)
2. **core_modules_selection.json** (from task_01)

---

## MAPPING RULE: 1 Feature = 1 Extension

**Usually:** Each feature gets exactly one extension module.

**Exception:** If features are tightly coupled (e.g., "user_registration" and "user_login"), they MAY share an extension, but this is rare.

---

## EXTENSION DESIGN ALGORITHM

```python
def map_features_to_extensions(features, core_modules):
    """
    Create extension modules for each feature.
    Extensions use core + external libs.
    """
    extensions = []

    for feature in features:
        # Skip wont_have features
        if feature.priority == "wont_have_v1":
            continue

        ext = {
            "name": to_snake_case(feature.name),
            "purpose": feature.processing.description,
            "implements_feature": feature.id,
            "uses_core": determine_core_usage(feature, core_modules),
            "external_deps": feature.processing.external_dependencies,
            "api": design_extension_api(feature),
            "complexity_score": feature.complexity_score,
            "estimated_loc": estimate_loc(feature.complexity_score)
        }

        extensions.append(ext)

    return extensions

def determine_core_usage(feature, core_modules):
    """Determine which core modules this extension needs."""
    uses = []

    # Always use config if it exists
    if "config" in core_modules:
        uses.append("config")

    # File I/O?
    if any(fmt in feature.input.format.lower()
           for fmt in ["csv", "json", "file"]):
        uses.append("io")

    # Validation?
    if "validation" in feature.processing.description.lower():
        uses.append("validation")

    # Transform?
    if any(kw in feature.processing.description.lower()
           for kw in ["transform", "convert", "format"]):
        uses.append("transform")

    # Always use error handling
    uses.append("error")

    return uses

def design_extension_api(feature):
    """Design the public API for this extension."""
    api = []

    # Main processing function
    input_type = feature.input.format
    output_type = feature.output.format
    api.append(f"process(input: {input_type}) -> {output_type}")

    # Validation function
    api.append(f"validate_input(data: Any) -> bool")

    # Config-based constructor
    api.append(f"from_config(config: Dict) -> {to_class_name(feature.name)}")

    return api

def estimate_loc(complexity_score):
    """Estimate lines of code based on APCE complexity score."""
    # Modified Fibonacci scale from APCE
    if complexity_score == 1:
        return 100
    elif complexity_score == 3:
        return 200
    elif complexity_score == 5:
        return 300
    elif complexity_score == 8:
        return 500
    else:
        return 800  # complexity_score 13+
```

---

## EXTENSION TEMPLATE

Every extension follows this structure:

```python
# extensions/feature_name.py

"""
{feature.processing.description}

Implements: {feature.id}
Uses Core: {uses_core}
External Deps: {external_deps}
"""

from pathlib import Path
from typing import List, Dict, Any

# Core imports
from core.config import load_config
from core.io import read_csv, write_json
from core.validation import validate
from core.error import log_error, handle_error

# External imports
{external_imports}

class FeatureName:
    """
    {feature.processing.description}

    Example:
        >>> feature = FeatureName.from_config("config.yaml")
        >>> result = feature.process(input_data)
    """

    def __init__(self, config: Dict):
        self.config = config
        # No hardcoded values!

    @classmethod
    def from_config(cls, config_path: str) -> "FeatureName":
        """Load from configuration file."""
        config = load_config(Path(config_path))
        return cls(config)

    def validate_input(self, data: Any) -> bool:
        """Validate input data against constraints."""
        # Use validation core module
        pass

    def process(self, input_data: {input_type}) -> {output_type}:
        """
        Main processing logic.

        Args:
            input_data: {feature.input.example}

        Returns:
            {output_type}: {feature.output.example}
        """
        try:
            # 1. Validate
            if not self.validate_input(input_data):
                raise ValueError("Invalid input")

            # 2. Process
            result = self._process_internal(input_data)

            # 3. Return
            return result

        except Exception as e:
            log_error(e, {"feature": "feature_name"})
            return handle_error(e)

    def _process_internal(self, data: Any) -> Any:
        """Internal processing logic."""
        # Implementation here
        pass
```

---

## CRITICAL CONSTRAINT: Extension Isolation

**RULE:** Extensions MUST NOT import each other.

```python
def validate_extension_isolation(extensions):
    """Ensure no extension imports another extension."""
    violations = []
    ext_names = {e.name for e in extensions}

    for ext in extensions:
        # Check if uses_core contains extension names
        for used in ext.uses_core:
            if used in ext_names:
                violations.append(
                    f"Extension '{ext.name}' imports extension '{used}'"
                )

    return violations
```

**If violations found:** REJECT and redesign.

**Why this matters:**
- Extensions are isolated features
- If Extension A needs Extension B, the shared logic belongs in Core
- This keeps the architecture clean and testable

---

## OUTPUT ARTIFACT

### extensions_design.json

```json
{
  "extensions": [
    {
      "name": "feature_1_extension",
      "purpose": "Feature 1 description",
      "implements_feature": "feature_1",
      "uses_core": ["io", "config", "validation"],
      "external_deps": ["pillow"],
      "why_external_dep": "Image manipulation not in stdlib",
      "api": [
        "process(data: Dict, config: Dict) -> Image",
        "validate_input(data: Dict) -> bool",
        "from_config(config_path: str) -> Feature1Extension"
      ],
      "estimated_loc": 200,
      "test_coverage_target": "90%",
      "file_path": "extensions/feature_1_extension.py"
    }
    // ... one extension per feature
  ],
  "validation": {
    "isolation_check": "passed",
    "all_features_mapped": true,
    "violations": []
  }
}
```

---

## EXECUTION INSTRUCTIONS

1. Load feature_spec.json
2. Load core_modules_selection.json
3. For each feature (priority != "wont_have_v1"):
   - Create extension spec
   - Determine core module usage
   - Extract external dependencies
   - Design API
4. Validate extension isolation
5. Generate extensions_design.json
6. Proceed to next phase (task_03_generate_config_schema)

**NO HARDCODED VALUES. EVERYTHING CONFIGURABLE.**
