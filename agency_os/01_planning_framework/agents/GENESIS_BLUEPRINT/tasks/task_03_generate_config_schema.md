# Task: Generate Configuration System

**PHASE:** 3
**TASK ID:** generate_config_schema
**TRIGGER:** extensions_design.json available

---

## OBJECTIVE

Generate YAML configuration schema for all configurable items (global settings + per-extension configs).

---

## INPUT ARTIFACTS

### Required:
1. **feature_spec.json** (project metadata)
2. **core_modules_selection.json** (to check if config module exists)
3. **extensions_design.json** (to extract configurable fields per extension)

---

## CONFIG SCHEMA GENERATION ALGORITHM

```python
def generate_config_schema(project, features, extensions):
    """Create YAML schema for configuration."""
    schema = {
        "version": "1.0",
        "sections": {}
    }

    # Global section (always included)
    schema["sections"]["global"] = {
        "description": "Project-wide settings",
        "fields": [
            {"name": "log_level", "type": "enum",
             "values": ["DEBUG", "INFO", "WARNING"], "default": "INFO"},
            {"name": "output_dir", "type": "path", "default": "./output"},
            {"name": "max_workers", "type": "int", "default": 4}
        ]
    }

    # Per-extension sections
    for ext in extensions:
        section = {
            "description": f"Configuration for {ext.purpose}",
            "fields": extract_configurable_fields(ext)
        }
        schema["sections"][ext.name] = section

    return schema

def extract_configurable_fields(extension):
    """Extract what should be configurable for this extension."""
    fields = []

    # Based on external deps, infer config needs
    if "pillow" in extension.external_deps:
        fields.extend([
            {"name": "image_quality", "type": "int", "default": 85},
            {"name": "image_format", "type": "enum",
             "values": ["PNG", "JPEG"], "default": "PNG"}
        ])

    if "stripe" in extension.external_deps:
        fields.extend([
            {"name": "stripe_api_key", "type": "string", "required": True},
            {"name": "webhook_secret", "type": "string", "required": True}
        ])

    if "requests" in extension.external_deps:
        fields.extend([
            {"name": "api_base_url", "type": "string", "required": True},
            {"name": "timeout_seconds", "type": "int", "default": 30},
            {"name": "retry_count", "type": "int", "default": 3}
        ])

    # Generic fields all extensions need
    fields.extend([
        {"name": "enabled", "type": "bool", "default": True},
        {"name": "timeout_seconds", "type": "int", "default": 30}
    ])

    return fields
```

---

## EXAMPLE CONFIG FILES

### config/_schema.yaml (Validation schema)
```yaml
version: "1.0"

sections:
  global:
    description: "Project-wide settings"
    fields:
      - name: log_level
        type: enum
        values: [DEBUG, INFO, WARNING]
        default: INFO
      - name: output_dir
        type: path
        default: ./output

  feature_1_extension:
    description: "Configuration for Feature 1"
    fields:
      - name: enabled
        type: bool
        default: true
      - name: image_quality
        type: int
        default: 85
```

### config/config.yaml (Default config)
```yaml
version: "1.0"

global:
  log_level: "INFO"
  output_dir: "./output"
  max_workers: 4

feature_1_extension:
  enabled: true
  timeout_seconds: 30
  image_quality: 85
  image_format: "PNG"

feature_2_extension:
  enabled: true
  timeout_seconds: 30
  api_base_url: "https://api.example.com"
  retry_count: 3
```

### config/config.example.yaml (Example for users)
```yaml
# Copy this to config.yaml and customize

version: "1.0"

global:
  log_level: "INFO"  # DEBUG, INFO, WARNING
  output_dir: "./output"
  max_workers: 4

feature_1_extension:
  enabled: true
  # Add your settings here

feature_2_extension:
  enabled: true
  api_base_url: "YOUR_API_URL_HERE"  # REQUIRED
  timeout_seconds: 30
```

---

## DIRECTORY STRUCTURE GENERATION

Generate the full Genesis Core directory layout:

```
{project_name}/
├── core/
│   ├── __init__.py
│   ├── schema.py           # Data models (always)
│   ├── entity.py           # Business entities (always)
│   ├── io.py               # (if file I/O needed)
│   ├── validation.py       # (if validation needed)
│   ├── transform.py        # (if data transform needed)
│   ├── storage.py          # (if persistence needed)
│   ├── config.py           # (if configurable)
│   ├── process.py          # (if workflow needed)
│   ├── error.py            # Error handling (always)
│   └── tracking.py         # Job tracking (always)
│
├── extensions/
│   ├── __init__.py
│   ├── feature_1.py        # One per feature
│   ├── feature_2.py
│   └── ...
│
├── config/
│   ├── _schema.yaml        # Validation schema
│   ├── config.yaml         # Default config
│   └── config.example.yaml # Example config
│
├── tests/
│   ├── core/
│   │   ├── test_schema.py
│   │   ├── test_entity.py
│   │   └── ...
│   └── extensions/
│       ├── test_feature_1.py
│       └── ...
│
├── cli.py                  # (if CLI tool)
├── main.py                 # Entry point
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
└── .gitignore
```

---

## OUTPUT ARTIFACT

### config_system.json

```json
{
  "config_system": {
    "mandatory": true,
    "reason": "Project is production-ready",
    "schema_location": "config/_schema.yaml",
    "schema": {
      "sections": {
        "global": {
          "fields": [...]
        },
        "feature_1_extension": {
          "fields": [...]
        }
      }
    },
    "example_configs": [
      "config/config.yaml",
      "config/config.example.yaml"
    ]
  },
  "directory_structure": {
    "root": "{project_name}/",
    "core": "core/ (Foundation modules, stdlib only except config)",
    "extensions": "extensions/ (Feature implementations, can use external deps)",
    "config": "config/ (YAML configs and validation schema)",
    "tests": "tests/ (Unit tests for core + extensions)",
    "entry_points": ["main.py", "cli.py (if CLI tool)"]
  }
}
```

---

## EXECUTION INSTRUCTIONS

1. Load all input artifacts
2. Generate global config section
3. For each extension, extract configurable fields based on external deps
4. Create config schema (_schema.yaml)
5. Create default config (config.yaml)
6. Create example config (config.example.yaml)
7. Generate directory structure layout
8. Output config_system.json
9. Proceed to next phase (task_04_validate_architecture)

**NO HARDCODED VALUES ALLOWED IN CODE.**
