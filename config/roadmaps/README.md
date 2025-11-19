# STEWARD Roadmaps

This directory contains roadmap templates for STEWARD mission management.

## Roadmaps

### `demo_gad701_roadmap.yaml`
**Purpose**: Demonstration roadmap for GAD-701 (Mission Control System)  
**Status**: Bootstrap/Example  
**Tasks**: 3 tasks demonstrating the task management system itself

This roadmap demonstrates the GAD-701 mission control functionality:
1. Task-001: SCAFFOLD_GAD_701_CORE - Core task management files
2. Task-002: INTEGRATE_CLI_DASHBOARD - Rich-based CLI dashboard
3. Task-003: IMPLEMENT_NEXT_TASK_GENERATOR - Auto-select next task

### `steward_gad_roadmap.yaml`
**Purpose**: Real GAD implementation roadmap based on Strategic Plan 2025-11-18  
**Status**: Active Strategic Roadmap  
**Tasks**: 16 tasks across 4 weeks

This is the **actual strategic roadmap** for vibe-agency implementation, tracking:
- Week 1: Runtime Engineering Foundation (GAD-500/501)
- Week 2: Semantic Refinement & Product Packaging
- Week 3: Framework Upgrades (Testing & Maintenance)
- Week 4: Production Polish & Quality Gates

## Usage

### Switching Roadmaps

Use the STEWARD mission CLI to switch between roadmaps:

```bash
# Switch to demo roadmap (GAD-701 demonstration)
./bin/steward-mission.py switch demo

# Switch to GAD roadmap (real strategic work)
./bin/steward-mission.py switch gad
```

### Viewing Status

```bash
# View current mission status
./bin/steward-mission.py status

# Or use the full mission control CLI
python3 agency_os/01_interface/cli/cmd_mission.py status
```

## Roadmap Structure

Each roadmap follows this structure:

```yaml
version: 1
project_name: <name>
description: <description>

phases:
  - name: <phase_name>
    status: <TODO|IN_PROGRESS|DONE>
    progress: <0-100>
    task_ids: [...]

tasks:
  <task_id>:
    id: <task_id>
    name: <TASK_NAME>
    description: <description>
    status: <TODO|IN_PROGRESS|BLOCKED|DONE>
    priority: <1-10>
    time_budget_mins: <minutes>
    validation_checks:
      - id: <check_id>
        description: <check_description>
        validator: <validate_files_exist|validate_tests_passing|validate_manual>
        params: {}
```

## Creating New Roadmaps

1. Copy an existing roadmap as a template
2. Update the `project_name` and `description`
3. Define your phases and tasks
4. Set validation criteria for each task
5. Save to `config/roadmaps/<your_roadmap>.yaml`
6. Update `bin/steward-mission.py` to include your roadmap

## Related Documentation

- **GAD Implementation Status**: `docs/architecture/GAD_IMPLEMENTATION_STATUS.md`
- **Strategic Plan**: `docs/STRATEGIC_PLAN_2025-11-18.md`
- **Task Management (GAD-701)**: `agency_os/00_system/task_management/`
- **Mission Control CLI**: `agency_os/01_interface/cli/cmd_mission.py`
