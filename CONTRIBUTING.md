# Contributing to Vibe Agency

Thank you for your interest in contributing to Vibe Agency! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Code Standards](#code-standards)
- [Testing](#testing)

---

## Code of Conduct

This project adheres to a simple code of conduct:
- Be respectful and constructive
- Welcome newcomers and help them learn
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Basic understanding of YAML and Markdown

### Development Setup

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/vibe-agency.git
   cd vibe-agency
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install pre-commit hooks:**
   ```bash
   pip install pre-commit
   pre-commit install
   ```

4. **Verify installation:**
   ```bash
   python3 validate_knowledge_index.py
   python3 agency_os/00_system/runtime/prompt_runtime.py
   ```

## Making Changes

### Branch Naming

Use descriptive branch names:
- `feature/add-new-agent` - New features
- `bugfix/fix-yaml-parsing` - Bug fixes
- `docs/update-readme` - Documentation updates
- `refactor/simplify-runtime` - Code refactoring

### Workflow

1. Create a new branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes

3. Run tests and linters:
   ```bash
   # Run tests
   pytest tests/

   # Format code
   black agency_os/ tests/

   # Lint code
   flake8 agency_os/ tests/

   # Validate YAML
   yamllint agency_os/
   ```

4. Commit your changes (see [Commit Guidelines](#commit-guidelines))

5. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

6. Open a Pull Request

## Commit Guidelines

We follow [Conventional Commits](https://www.conventionalcommits.org/) specification:

### Format

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples

```bash
feat(planning): Add VIBE_ALIGNER task 3
fix(runtime): Handle missing knowledge files gracefully
docs(nfr): Add performance requirements
refactor(prompt): Simplify composition logic
test(runtime): Add error handling tests
```

### Sign your commits (DCO)

We use the Developer Certificate of Origin (DCO) for contributions:

```bash
git commit --signoff -m "feat(planning): Add new template"
```

This adds a `Signed-off-by` line to your commit message, certifying that you have the right to submit the code.

## Pull Request Process

### Before Submitting

- [ ] All tests pass (`pytest`)
- [ ] Code is formatted (`black`)
- [ ] Linting passes (`flake8`)
- [ ] YAML is valid (`yamllint`)
- [ ] Pre-commit hooks pass (`pre-commit run --all-files`)
- [ ] Documentation is updated (if needed)
- [ ] CHANGELOG.md is updated (if applicable)

### PR Description Template

```markdown
## Summary
[Brief description of changes]

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
[How did you test these changes?]

## Checklist
- [ ] Code follows PEP 8 style
- [ ] All public functions have docstrings
- [ ] Tests added for new features
- [ ] No hardcoded secrets
- [ ] CHANGELOG.md updated
- [ ] Documentation updated
```

### Review Process

1. Automated checks must pass (pre-commit hooks, tests)
2. At least 1 approving review required
3. Breaking changes require 2 approving reviews
4. Maintainer will merge once approved

## Code Standards

### Python Style

- Follow [PEP 8](https://pep8.org/)
- Use `black` for formatting (line length: 100)
- Maximum cyclomatic complexity: 10
- Add docstrings to all public functions (Google style)

**Example:**

```python
def execute_task(agent_id: str, task_id: str, context: Dict[str, Any]) -> str:
    """
    Compose and execute an atomized task.

    Args:
        agent_id: Agent identifier (e.g., "GENESIS_BLUEPRINT")
        task_id: Task identifier (e.g., "select_core_modules")
        context: Runtime context (project_id, artifacts, etc.)

    Returns:
        Composed prompt string ready for LLM execution

    Raises:
        AgentNotFoundError: If agent_id not found
        TaskNotFoundError: If task files not found
    """
```

### YAML Style

- Indentation: 2 spaces
- Max line length: 120 characters
- Use `yamllint` to validate

**Example:**

```yaml
# Purpose: Feasibility Analysis Engine constraints
# Version: 1.0

constraints:
  tech_stack:
    - type: "incompatibility"
      condition: "vercel AND websocket"
      reason: "Vercel does not support persistent WebSocket connections"
```

### Markdown Style

- Use ATX-style headings (`# Heading`)
- Max line length: 120 characters (soft limit)
- Always specify language for code blocks

**Example:**

````markdown
# Section Title

Brief introduction.

## Subsection

```python
# Code example with language specified
def example():
    pass
```
````

### Knowledge Base Guidelines

When adding or modifying knowledge bases:

1. **Add header comment:**
   ```yaml
   # <filename>.yaml
   # Purpose: <what this file contains>
   # Version: <semantic version>
   # Last Updated: <YYYY-MM-DD>
   ```

2. **Provide examples:**
   - Include real-world examples
   - Show both valid and invalid cases

3. **Document constraints:**
   - Explain WHY, not just WHAT
   - Include rationale for each rule

4. **Keep files focused:**
   - One purpose per file
   - Split if file exceeds 1 MB

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=agency_os --cov-report=html

# Run specific test
pytest tests/test_prompt_composition.py

# Run fast tests only (< 30s)
pytest -m "not slow"
```

### Writing Tests

- Location: `tests/`
- Naming: `test_<function_name>_<scenario>.py`
- Use fixtures for test data
- Aim for 80%+ code coverage

**Example:**

```python
def test_execute_task_success():
    """Test successful prompt composition"""
    runtime = PromptRuntime()
    context = {"project_id": "test_001"}

    result = runtime.execute_task(
        agent_id="GENESIS_BLUEPRINT",
        task_id="01_select_core_modules",
        context=context
    )

    assert isinstance(result, str)
    assert len(result) > 0
```

### Test Coverage Requirements

- Unit tests: 80% minimum
- Critical paths: 100% coverage
- Integration tests: All agent compositions

## Adding New Content

### Adding a New Agent

1. Create agent directory:
   ```bash
   mkdir -p agency_os/XX_framework/agents/NEW_AGENT/{tasks,gates}
   ```

2. Create required files:
   - `_prompt_core.md` (personality)
   - `_composition.yaml` (assembly rules)
   - `_knowledge_deps.yaml` (dependencies)
   - `tasks/task_01_*.md` + `tasks/task_01_*.meta.yaml`

3. Add to `AGENT_REGISTRY` in `prompt_runtime.py`

4. Update `.knowledge_index.yaml`

5. Add integration test

### Adding a Knowledge Base

1. Create YAML file in appropriate framework's `knowledge/` directory

2. Add header comment:
   ```yaml
   # <filename>.yaml
   # Purpose: <description>
   # Version: 1.0
   # Last Updated: YYYY-MM-DD
   ```

3. Update `.knowledge_index.yaml`

4. Reference in agent's `_knowledge_deps.yaml`

5. Validate:
   ```bash
   yamllint <filename>.yaml
   python3 validate_knowledge_index.py
   ```

### Adding a Task

1. Create task prompt: `task_XX_<name>.md`

2. Create task metadata: `task_XX_<name>.meta.yaml`

3. Add validation gates (if needed)

4. Update agent's composition

5. Add integration test

## Questions?

- **Documentation:** Check `docs/guides/DEVELOPER_GUIDE.md`
- **Glossary:** See `docs/GLOSSARY.md` for terminology
- **Issues:** [GitHub Issues](https://github.com/kimeisele/vibe-agency/issues)
- **Discussions:** [GitHub Discussions](https://github.com/kimeisele/vibe-agency/discussions)

---

**Thank you for contributing to Vibe Agency!** 🚀
