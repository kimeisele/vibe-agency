"""
GAD-701: MISSION CONTROL CLI
Rich-based interactive dashboard for Task Management System

Features:
- mission status -> Show current mission dashboard
- mission start <id> -> Start a task
- mission validate -> Run validation checks
- mission complete -> Complete current task (hard validation)
"""

import importlib.util
import sys
from datetime import datetime
from pathlib import Path

from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

# Load task_management module dynamically to handle 00_system directory name
_task_mgmt_path = (
    Path(__file__).parent.parent.parent / "core_system" / "task_management" / "__init__.py"
)
_spec = importlib.util.spec_from_file_location("task_management", _task_mgmt_path)
_task_mgmt = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_task_mgmt)

TaskManager = _task_mgmt.TaskManager
TaskStatus = _task_mgmt.TaskStatus
Roadmap = _task_mgmt.Roadmap

# Load metrics module dynamically
_metrics_path = (
    Path(__file__).parent.parent.parent / "core_system" / "task_management" / "metrics.py"
)
_metrics_spec = importlib.util.spec_from_file_location("metrics", _metrics_path)
_metrics_module = importlib.util.module_from_spec(_metrics_spec)
_metrics_spec.loader.exec_module(_metrics_module)
MetricsCalculator = _metrics_module.MetricsCalculator


console = Console()


def format_duration(start_dt: datetime | None, end_dt: datetime | None = None) -> str:
    """Format duration between two datetimes"""
    if not start_dt:
        return "N/A"

    end = end_dt or datetime.now()
    delta = end - start_dt

    hours = delta.seconds // 3600
    minutes = (delta.seconds % 3600) // 60

    if hours > 0:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"


def mission_status(manager: TaskManager) -> None:
    """
    Display Mission Control Dashboard

    Shows:
    - Current task with status and time used
    - Validation criteria as checklist
    - Validation errors (if any)
    - Quick stats
    """
    console.clear()

    # Header
    console.print()
    console.print(Align.center(Text("🎯 MISSION CONTROL", style="bold cyan", justify="center")))
    console.print(Align.center("─" * 60))
    console.print()

    # Load mission state
    try:
        mission = manager.get_active_mission()
    except Exception as e:
        console.print(
            Panel(
                f"[red]❌ Error loading mission state[/red]\n{e}",
                border_style="red",
                title="[red]ERROR[/red]",
            )
        )
        return

    # Current Task Section
    current_task = mission.current_task

    if not current_task:
        console.print(
            Panel(
                "[yellow]No active task[/yellow]\n\nUse: [bold]vibe mission start <id>[/bold] to start a task",
                border_style="yellow",
                title="[yellow]STATUS[/yellow]",
            )
        )
        return

    # Current Task Panel
    status_color = {
        TaskStatus.TODO: "yellow",
        TaskStatus.IN_PROGRESS: "blue",
        TaskStatus.BLOCKED: "red",
        TaskStatus.DONE: "green",
    }.get(current_task.status, "white")

    elapsed = format_duration(current_task.started_at)
    time_budget = f"{current_task.time_used_mins}/{current_task.time_budget_mins} mins"

    task_info = f"""
[bold]{current_task.name}[/bold]
{current_task.description}

[dim]ID:[/dim] {current_task.id}
[dim]Status:[/dim] [{status_color}]{current_task.status.value}[/{status_color}]
[dim]Time Elapsed:[/dim] {elapsed}
[dim]Time Used:[/dim] {time_budget}
[dim]Priority:[/dim] {current_task.priority}/10
"""

    if current_task.blocking_reason:
        task_info += f"[dim]Blocker:[/dim] [red]{current_task.blocking_reason}[/red]\n"

    console.print(
        Panel(task_info.strip(), border_style=status_color, title="[bold]CURRENT TASK[/bold]")
    )
    console.print()

    # Validation Checks Table
    if current_task.validation_checks:
        validation_table = Table(title="Validation Criteria", show_header=True, header_style="bold")
        validation_table.add_column("Status", style="dim")
        validation_table.add_column("Check", width=40)
        validation_table.add_column("Result", style="dim")

        for check in current_task.validation_checks:
            status_icon = "✅" if check.status else "❌"
            status_text = "[green]PASS[/green]" if check.status else "[red]FAIL[/red]"
            validation_table.add_row(status_icon, check.description, status_text)

        console.print(validation_table)
        console.print()

    # Validation Errors Section
    failed_checks = current_task.get_failed_checks()
    if failed_checks:
        error_text = ""
        for check in failed_checks:
            error_msg = check.error or "Unknown error"
            error_text += f"• {check.description}: {error_msg}\n"

        console.print(
            Panel(error_text.strip(), border_style="red", title="[red]❌ VALIDATION ERRORS[/red]")
        )
        console.print()

    # Quick Stats
    stats_table = Table(show_header=False, box=None)
    stats_table.add_row(
        "[dim]Tasks Completed:[/dim]", f"[bold]{mission.total_tasks_completed}[/bold]"
    )
    stats_table.add_row(
        "[dim]Total Time Spent:[/dim]", f"[bold]{mission.total_time_spent_mins} mins[/bold]"
    )
    stats_table.add_row("[dim]Current Phase:[/dim]", f"[bold]{mission.current_phase}[/bold]")

    console.print(stats_table)
    console.print()

    # Available Commands
    console.print(Align.center("─" * 60))
    console.print()
    console.print("[dim]Quick Commands:[/dim]")
    console.print("[dim]  vibe mission validate      - Run validation checks[/dim]")
    console.print("[dim]  vibe mission complete      - Complete current task[/dim]")
    console.print("[dim]  vibe mission start <id>    - Start new task[/dim]")
    console.print()


def mission_start(manager: TaskManager, task_id: str) -> None:
    """Start a task by ID"""
    try:
        task = manager.start_task(task_id)
        console.print(f"[green]✅ Task started: {task.name}[/green]")
        console.print(f"[dim]ID: {task.id}[/dim]")
        console.print(f"[dim]Status: {task.status.value}[/dim]")
    except ValueError as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]❌ Unexpected error: {e}[/red]")
        sys.exit(1)


def mission_validate(manager: TaskManager) -> None:
    """Run validation checks on current task"""
    try:
        console.print("[cyan]🔍 Running validation checks...[/cyan]")
        console.print()

        result = manager.validate_current_task()

        if result.get("valid"):
            console.print("[green]✅ All validation checks passed![/green]")
        else:
            console.print("[red]❌ Validation failed:[/red]")
            for failed in result.get("failed", []):
                console.print(f"  • [red]{failed}[/red]")

        # Show detailed results
        console.print()
        console.print("Validation Results:")
        for check_id, status in result.get("checks", {}).items():
            icon = "✅" if status else "❌"
            console.print(f"  {icon} {check_id}: {'PASS' if status else 'FAIL'}")

    except RuntimeError as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]❌ Unexpected error: {e}[/red]")
        sys.exit(1)


def mission_complete(manager: TaskManager) -> None:
    """Complete current task (with hard validation)"""
    try:
        console.print("[cyan]🎬 Completing task...[/cyan]")
        console.print()

        # This will validate and complete
        next_task = manager.complete_current_task()

        console.print("[green]✅ Task completed successfully![/green]")

        if next_task:
            console.print()
            console.print(f"[cyan]Next task: {next_task.name}[/cyan]")
            console.print(f"[dim]ID: {next_task.id}[/dim]")
        else:
            console.print("[yellow]ℹ️  No more tasks in roadmap[/yellow]")

    except RuntimeError as e:
        console.print("[red]❌ Task validation failed:[/red]")
        console.print(f"[red]{e}[/red]")
        console.print()
        console.print("[yellow]Fix validation errors and try again[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]❌ Unexpected error: {e}[/red]")
        sys.exit(1)


def mission_metrics(manager: TaskManager, phase_name: str | None = None) -> None:
    """Display project metrics and progress analytics"""
    try:
        roadmap = manager.load_roadmap()
        calc = MetricsCalculator(roadmap)

        console.clear()
        console.print()
        console.print(Align.center(Text("📊 PROJECT METRICS", style="bold cyan", justify="center")))
        console.print(Align.center("─" * 60))
        console.print()

        if phase_name:
            # Show metrics for specific phase
            metrics = calc.get_phase_metrics(phase_name)
            if not metrics:
                console.print(f"[red]❌ Phase not found: {phase_name}[/red]")
                return

            console.print(f"[bold cyan]Phase: {metrics['phase_name']}[/bold cyan]")
            console.print(f"[dim]Status: {metrics['phase_status']}[/dim]")
            console.print()

            metrics_table = Table(show_header=False, box=None)
            metrics_table.add_row(
                "[dim]Total Tasks:[/dim]", f"[bold]{metrics['total_tasks']}[/bold]"
            )
            metrics_table.add_row(
                "[dim]Completed:[/dim]", f"[green]{metrics['completed_tasks']}[/green]"
            )
            metrics_table.add_row(
                "[dim]In Progress:[/dim]", f"[blue]{metrics['in_progress_tasks']}[/blue]"
            )
            metrics_table.add_row("[dim]Todo:[/dim]", f"[yellow]{metrics['todo_tasks']}[/yellow]")
            metrics_table.add_row("[dim]Blocked:[/dim]", f"[red]{metrics['blocked_tasks']}[/red]")
            metrics_table.add_row(
                "[dim]Progress:[/dim]", f"[bold]{metrics['progress_percent']}%[/bold]"
            )

            console.print(metrics_table)
        else:
            # Show overall metrics
            overall = calc.get_overall_progress()
            time_metrics = calc.get_time_metrics()
            validation_metrics = calc.get_validation_metrics()

            # Overall Progress
            console.print("[bold cyan]OVERALL PROGRESS[/bold cyan]")
            progress_table = Table(show_header=False, box=None)
            progress_table.add_row(
                "[dim]Total Tasks:[/dim]", f"[bold]{overall['total_tasks']}[/bold]"
            )
            progress_table.add_row(
                "[dim]Completed:[/dim]", f"[green]{overall['completed_tasks']}[/green]"
            )
            progress_table.add_row(
                "[dim]In Progress:[/dim]", f"[blue]{overall['in_progress_tasks']}[/blue]"
            )
            progress_table.add_row("[dim]Todo:[/dim]", f"[yellow]{overall['todo_tasks']}[/yellow]")
            progress_table.add_row("[dim]Blocked:[/dim]", f"[red]{overall['blocked_tasks']}[/red]")
            progress_table.add_row(
                "[dim]Progress:[/dim]", f"[bold]{overall['progress_percent']}%[/bold]"
            )
            console.print(progress_table)
            console.print()

            # Time Metrics
            console.print("[bold cyan]TIME METRICS[/bold cyan]")
            time_table = Table(show_header=False, box=None)
            time_table.add_row(
                "[dim]Total Budgeted:[/dim]",
                f"[bold]{time_metrics['total_time_budgeted_mins']} mins[/bold]",
            )
            time_table.add_row(
                "[dim]Total Used:[/dim]",
                f"[bold]{time_metrics['total_time_used_mins']} mins[/bold]",
            )
            time_table.add_row(
                "[dim]Utilization:[/dim]",
                f"[bold]{time_metrics['time_utilization_percent']}%[/bold]",
            )
            console.print(time_table)
            console.print()

            # Validation Metrics
            console.print("[bold cyan]VALIDATION CHECKS[/bold cyan]")
            validation_table = Table(show_header=False, box=None)
            validation_table.add_row(
                "[dim]Total Checks:[/dim]", f"[bold]{validation_metrics['total_checks']}[/bold]"
            )
            validation_table.add_row(
                "[dim]Passing:[/dim]", f"[green]{validation_metrics['passing_checks']}[/green]"
            )
            validation_table.add_row(
                "[dim]Failing:[/dim]", f"[red]{validation_metrics['failing_checks']}[/red]"
            )
            validation_table.add_row(
                "[dim]Pass Rate:[/dim]", f"[bold]{validation_metrics['check_pass_percent']}%[/bold]"
            )
            console.print(validation_table)
            console.print()

            # Phase Metrics
            console.print("[bold cyan]PHASE BREAKDOWN[/bold cyan]")
            phases = calc.get_all_phase_metrics()
            phase_table = Table(title="Phase Metrics", show_header=True, header_style="bold")
            phase_table.add_column("Phase", style="bold")
            phase_table.add_column("Status", style="dim")
            phase_table.add_column("Tasks", justify="right")
            phase_table.add_column("Done", justify="right", style="green")
            phase_table.add_column("Progress", justify="right", style="bold")

            for phase_metrics in phases:
                phase_table.add_row(
                    phase_metrics["phase_name"],
                    phase_metrics["phase_status"],
                    str(phase_metrics["total_tasks"]),
                    str(phase_metrics["completed_tasks"]),
                    f"{phase_metrics['progress_percent']}%",
                )

            console.print(phase_table)

        console.print()
        console.print(Align.center("─" * 60))
        console.print()

    except Exception as e:
        console.print(f"[red]❌ Error generating metrics: {e}[/red]")
        sys.exit(1)


def main():
    """Main CLI entry point for mission control"""
    import argparse

    # Find vibe root (where .vibe directory exists or should be)
    # Start from current directory and walk up
    vibe_root = Path.cwd()
    while vibe_root != vibe_root.parent:
        if (vibe_root / ".vibe").exists() or (vibe_root / "agency_os").exists():
            break
        vibe_root = vibe_root.parent

    parser = argparse.ArgumentParser(
        description="🎯 VIBE Mission Control - Task Management Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  vibe mission status              - Show dashboard
  vibe mission start task-001      - Start task-001
  vibe mission validate            - Run validation checks
  vibe mission complete            - Complete current task

Related:
  See .vibe/config/roadmap.yaml for task definitions
  See .vibe/state/active_mission.json for current state
        """,
    )

    parser.add_argument(
        "command",
        type=str,
        choices=["status", "start", "validate", "complete", "metrics"],
        help="Mission control command",
    )
    parser.add_argument(
        "task_id",
        type=str,
        nargs="?",
        help="Task ID (required for 'start' command) or phase name (optional for 'metrics')",
    )

    args = parser.parse_args()

    # Initialize TaskManager
    try:
        manager = TaskManager(vibe_root)
    except Exception as e:
        console.print(f"[red]❌ Failed to initialize TaskManager: {e}[/red]")
        sys.exit(1)

    # Execute command
    if args.command == "status":
        mission_status(manager)

    elif args.command == "start":
        if not args.task_id:
            parser.error("'start' command requires task_id argument")
        mission_start(manager, args.task_id)

    elif args.command == "validate":
        mission_validate(manager)

    elif args.command == "complete":
        mission_complete(manager)

    elif args.command == "metrics":
        mission_metrics(manager, args.task_id)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
