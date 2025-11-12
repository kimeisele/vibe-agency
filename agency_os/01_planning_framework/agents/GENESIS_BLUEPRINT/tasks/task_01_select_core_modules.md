# Task: Select Core Modules

**PHASE:** 1
**TASK ID:** select_core_modules
**TRIGGER:** feature_spec.json available

---

## OBJECTIVE

Analyze feature_spec.json and algorithmically select minimal, necessary core modules based on required capabilities.

---

## INPUT ARTIFACTS

### Required: feature_spec.json

Expected structure:
```json
{
  "project": {
    "name": "string",
    "category": "CLI Tool|Web App|...",
    "scale": "Solo User|Small Team|Production"
  },
  "features": [
    {
      "id": "feature_1",
      "name": "string",
      "priority": "must_have|should_have|could_have",
      "complexity_score": 5,
      "input": {...},
      "processing": {...},
      "output": {...},
      "dependencies": {...}
    }
  ]
}
```

---

## SELECTION ALGORITHM

### Step 1: Foundation Modules (Always Included)

```python
core = ["schema", "entity"]  # Always included (foundation)
```

- **schema.py**: Data models using dataclasses and type hints
- **entity.py**: Business logic entities

### Step 2: Capability Analysis

Analyze ALL features to determine what capabilities are needed:

```python
def analyze_capabilities(features):
    """Extract what capabilities are needed across ALL features."""
    needs = {
        "file_io": False,
        "data_validation": False,
        "data_transform": False,
        "persistence": False,
        "configuration": False,
        "workflow": False
    }

    for feature in features:
        # File I/O needed?
        if any(fmt in feature.input.format.lower()
               for fmt in ["csv", "json", "file", "image", "pdf"]):
            needs["file_io"] = True

        if any(fmt in feature.output.format.lower()
               for fmt in ["csv", "json", "file", "image", "pdf"]):
            needs["file_io"] = True

        # Validation needed?
        if "constraint" in feature.input or "validation" in feature.processing.description.lower():
            needs["data_validation"] = True

        # Transform needed?
        if any(kw in feature.processing.description.lower()
               for kw in ["transform", "convert", "format", "clean", "enrich"]):
            needs["data_transform"] = True

        # Persistence needed?
        if any(kw in str(feature.processing.side_effects)
               for kw in ["database", "cache", "history", "state"]):
            needs["persistence"] = True

        # Workflow needed?
        if len(features) > 2:
            needs["workflow"] = True

        # Config needed? (check project level)
        if "production" in str(feature.priority).lower():
            needs["configuration"] = True

    return needs
```

### Step 3: Map Capabilities to Core Modules

```python
def select_core_modules(features):
    """Algorithmic selection of core modules."""
    core = ["schema", "entity"]  # Foundation

    needs = analyze_capabilities(features)

    if needs["file_io"]:
        core.append("io")

    if needs["data_validation"]:
        core.append("validation")

    if needs["data_transform"]:
        core.append("transform")

    if needs["persistence"]:
        core.append("storage")

    if needs["configuration"]:
        core.append("config")  # ONLY external dep allowed: PyYAML

    if needs["workflow"]:
        core.append("process")

    # Always include infrastructure
    core.extend(["error", "tracking"])

    return core
```

---

## CORE MODULE SPECIFICATIONS

### 1. schema.py (Always included)
```python
"""
Data models using dataclasses and type hints.
Defines the data structures used across the system.
"""

# API
- @dataclass ModelName
- Type[Model]

# Dependencies: ["dataclasses", "typing"]
# LOC: ~50-100
# Test Coverage: 100%
```

### 2. entity.py (Always included)
```python
"""
Business logic entities.
Implements domain model abstractions.
"""

# API
- class EntityName
- entity.method()

# Dependencies: ["schema"]
# LOC: ~100-200
# Test Coverage: 100%
```

### 3. io.py (Conditional)
```python
"""
File I/O operations for CSV, JSON, images, PDFs.
Handles all file system interactions.
"""

# API (only include what's ACTUALLY used)
- read_csv(path: Path) -> List[Dict]
- write_csv(path: Path, data: List[Dict])
- read_json(path: Path) -> Dict
- write_json(path: Path, data: Dict)
# ... only formats actually needed

# Dependencies: ["pathlib", "csv", "json"]
# LOC: ~100-150
# Test Coverage: 100%
```

### 4. validation.py (Conditional)
```python
"""
Input validation, schema checks, constraint enforcement.
"""

# API
- validate(data: Any, schema: Dict) -> ValidationResult
- check_constraints(data: Any, rules: List[Rule]) -> bool

# Dependencies: ["schema"]
# LOC: ~80-120
# Test Coverage: 100%
```

### 5. transform.py (Conditional)
```python
"""
Data manipulation (map, filter, format, normalize).
"""

# API
- transform(data: List[Dict], rules: TransformRules) -> List[Dict]
- normalize(data: Any) -> Any

# Dependencies: ["schema", "entity"]
# LOC: ~100-150
# Test Coverage: 100%
```

### 6. storage.py (Conditional)
```python
"""
Persistence layer (file-based, SQLite, in-memory).
"""

# API
- save(entity: Entity) -> bool
- load(id: str) -> Entity
- query(filters: Dict) -> List[Entity]

# Dependencies: ["pathlib", "sqlite3", "schema"]
# LOC: ~150-200
# Test Coverage: 100%
```

### 7. config.py (Conditional - ONLY external dep allowed)
```python
"""
YAML/JSON config loading, validation, defaults.
"""

# API
- load_config(path: Path) -> Dict
- validate_config(config: Dict, schema: Dict) -> bool
- get(key: str, default: Any = None) -> Any

# Dependencies: ["pathlib", "pyyaml"]  # ONLY external dep in core!
# LOC: ~60-100
# Test Coverage: 100%
```

### 8. process.py (Conditional)
```python
"""
Workflow orchestration (sequential, parallel, conditional).
"""

# API
- execute_workflow(steps: List[Step]) -> WorkflowResult
- run_parallel(tasks: List[Task]) -> List[Result]

# Dependencies: ["schema", "entity"]
# LOC: ~100-150
# Test Coverage: 100%
```

### 9. error.py (Always included)
```python
"""
Error handling, logging, recovery strategies.
"""

# API
- log_error(exception: Exception, context: Dict)
- handle_error(exception: Exception) -> ErrorResult
- retry(func: Callable, max_attempts: int) -> Any

# Dependencies: ["logging"]
# LOC: ~70-100
# Test Coverage: 100%
```

### 10. tracking.py (Always included)
```python
"""
Job status, progress, metrics, history.
"""

# API
- track_job(job_id: str, status: JobStatus)
- log_progress(current: int, total: int)
- get_metrics() -> Dict

# Dependencies: ["storage", "schema"]
# LOC: ~50-80
# Test Coverage: 100%
```

---

## VALIDATION RULES

### Core Module Count Validation

**RULE:** Total core modules must be 6-12.

- **Minimum**: 6 (schema, entity, config, error, tracking, + 1 domain)
- **Maximum**: 12 (all modules)

**If < 6:** Project too simple (maybe doesn't need Genesis)
**If > 12:** Over-engineering (consolidate modules)

---

## OUTPUT ARTIFACT

### core_modules_selection.json

```json
{
  "core_modules": [
    {
      "name": "io",
      "purpose": "File I/O for CSV, JSON, images",
      "why_core": "Needed by 3 features: feature_1, feature_2, feature_3",
      "dependencies": ["pathlib", "csv", "json"],
      "estimated_loc": 120,
      "test_coverage_target": "100%",
      "file_path": "core/io.py"
    }
    // ... more modules
  ],
  "selection_rationale": {
    "file_io": "3 features require CSV/JSON I/O",
    "data_validation": "2 features have input constraints",
    "persistence": "Project requires state history"
  },
  "validation": {
    "module_count": 9,
    "within_range": true,
    "stdlib_only": true
  }
}
```

---

## EXECUTION INSTRUCTIONS

1. Load feature_spec.json
2. Run capability analysis (analyze_capabilities)
3. Select core modules algorithmically (select_core_modules)
4. Validate module count (6-12 range)
5. Generate core_modules_selection.json
6. Proceed to next phase (task_02_design_extensions)

**NO HUMAN JUDGMENT NEEDED - This is purely formula-based.**
