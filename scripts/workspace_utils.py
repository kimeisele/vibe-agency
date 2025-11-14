#!/usr/bin/env python3
"""
Workspace Utilities for SSF and AOS Integration

This module provides helper functions for workspace management, context resolution,
and registry operations. Used by both SSF (System Steward Framework) and AOS
(Agency Operating System) components.

Functions:
    - get_active_workspace(): Returns current workspace context from environment
    - resolve_manifest_path(): Resolves workspace name to manifest path
    - load_workspace_manifest(): Loads project manifest for given workspace
    - get_workspace_by_project_id(): Looks up workspace by project UUID
    - register_workspace(): Adds new workspace to registry
    - archive_workspace(): Moves workspace from active to archived

Dependencies:
    - pyyaml: For workspace registry operations
    - pathlib: For cross-platform path handling

Author: Vibe Agency - System Steward Framework
Version: 1.0.0
Date: 2025-11-12
"""

import os
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List
from uuid import UUID


# =================================================================
# WORKSPACE CONTEXT RESOLUTION
# =================================================================

def get_active_workspace() -> str:
    """
    Returns current workspace context from environment variable or state file.

    The $ACTIVE_WORKSPACE environment variable is set by SOP_008 (Switch Workspace)
    and determines which workspace manifest all SSF operations target.

    UPDATED: Now persists workspace to .active_workspace file for CLI usage.

    Returns:
        str: Workspace name (e.g., 'acme_corp') or 'ROOT' if not set

    Example:
        >>> os.environ['ACTIVE_WORKSPACE'] = 'acme_corp'
        >>> get_active_workspace()
        'acme_corp'

        >>> del os.environ['ACTIVE_WORKSPACE']
        >>> get_active_workspace()
        'ROOT'
    """
    # Check environment variable first
    env_workspace = os.getenv('ACTIVE_WORKSPACE')
    if env_workspace:
        return env_workspace

    # Fall back to state file
    state_file = Path('.active_workspace')
    if state_file.exists():
        try:
            workspace = state_file.read_text().strip()
            if workspace:
                return workspace
        except Exception:
            pass

    return 'ROOT'


def set_active_workspace(workspace_name: str):
    """
    Persists active workspace to state file.

    This allows workspace context to persist across CLI invocations.

    Args:
        workspace_name: Workspace to activate
    """
    state_file = Path('.active_workspace')
    state_file.write_text(workspace_name)

    # Also set environment variable for current process
    os.environ['ACTIVE_WORKSPACE'] = workspace_name


def resolve_manifest_path(workspace_name: Optional[str] = None) -> Path:
    """
    Resolves workspace name to project_manifest.json path.

    This function implements the workspace context logic used by SSF_ROUTER
    to determine which manifest to load based on active workspace context.

    Args:
        workspace_name: Workspace identifier (e.g., 'acme_corp').
                       If None, uses $ACTIVE_WORKSPACE environment variable.

    Returns:
        Path: Absolute path to project_manifest.json

    Examples:
        >>> resolve_manifest_path('acme_corp')
        PosixPath('workspaces/acme_corp/project_manifest.json')

        >>> resolve_manifest_path('ROOT')
        PosixPath('project_manifest.json')

        >>> resolve_manifest_path()  # Uses $ACTIVE_WORKSPACE
        PosixPath('workspaces/acme_corp/project_manifest.json')
    """
    if workspace_name is None:
        workspace_name = get_active_workspace()

    if workspace_name == 'ROOT':
        return Path('project_manifest.json')
    else:
        return Path(f'workspaces/{workspace_name}/project_manifest.json')


def resolve_artifact_base_path(workspace_name: Optional[str] = None) -> Path:
    """
    Resolves workspace name to artifacts/ base directory.

    Used by SOPs to determine where to save/load artifacts based on active workspace.

    Args:
        workspace_name: Workspace identifier. If None, uses $ACTIVE_WORKSPACE.

    Returns:
        Path: Absolute path to artifacts/ directory

    Examples:
        >>> resolve_artifact_base_path('acme_corp')
        PosixPath('workspaces/acme_corp/artifacts')

        >>> resolve_artifact_base_path('ROOT')
        PosixPath('artifacts')
    """
    if workspace_name is None:
        workspace_name = get_active_workspace()

    if workspace_name == 'ROOT':
        return Path('artifacts')
    else:
        return Path(f'workspaces/{workspace_name}/artifacts')


# =================================================================
# MANIFEST OPERATIONS
# =================================================================

def load_workspace_manifest(workspace_name: Optional[str] = None) -> Dict:
    """
    Loads project manifest for given workspace.

    Args:
        workspace_name: Workspace identifier. If None, uses $ACTIVE_WORKSPACE.

    Returns:
        dict: Parsed project_manifest.json contents

    Raises:
        FileNotFoundError: If manifest file doesn't exist
        json.JSONDecodeError: If manifest is not valid JSON

    Example:
        >>> manifest = load_workspace_manifest('acme_corp')
        >>> manifest['metadata']['name']
        'Booking Tool for Acme'
        >>> manifest['status']['projectPhase']
        'PLANNING'
    """
    manifest_path = resolve_manifest_path(workspace_name)

    if not manifest_path.exists():
        raise FileNotFoundError(
            f"Manifest not found: {manifest_path}. "
            f"Workspace '{workspace_name or get_active_workspace()}' may not exist."
        )

    with open(manifest_path, 'r') as f:
        return json.load(f)


def save_workspace_manifest(manifest: Dict, workspace_name: Optional[str] = None):
    """
    Saves project manifest to workspace.

    Updates lastUpdatedAt timestamp automatically.

    Args:
        manifest: Project manifest dict to save
        workspace_name: Target workspace. If None, uses $ACTIVE_WORKSPACE.

    Raises:
        FileNotFoundError: If workspace directory doesn't exist
    """
    manifest_path = resolve_manifest_path(workspace_name)

    # Auto-update timestamp
    manifest['metadata']['lastUpdatedAt'] = datetime.now().isoformat()

    # Ensure parent directory exists
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)


# =================================================================
# WORKSPACE REGISTRY OPERATIONS
# =================================================================

def load_workspace_registry() -> Dict:
    """
    Loads the workspace registry from .workspace_index.yaml.

    Returns:
        dict: Parsed workspace registry with 'workspaces' and 'archived' arrays

    Raises:
        FileNotFoundError: If registry file doesn't exist
    """
    registry_path = Path('workspaces/.workspace_index.yaml')

    if not registry_path.exists():
        raise FileNotFoundError(
            f"Workspace registry not found: {registry_path}. "
            "Repository may not be properly initialized."
        )

    with open(registry_path, 'r') as f:
        return yaml.safe_load(f)


def save_workspace_registry(registry: Dict):
    """
    Saves workspace registry to .workspace_index.yaml.

    Auto-updates metadata.lastUpdated timestamp.

    Args:
        registry: Registry dict to save
    """
    registry_path = Path('workspaces/.workspace_index.yaml')

    # Auto-update metadata
    registry['metadata']['lastUpdated'] = datetime.now().strftime('%Y-%m-%d')

    with open(registry_path, 'w') as f:
        yaml.dump(registry, f, sort_keys=False, default_flow_style=False)


def get_workspace_by_name(workspace_name: str) -> Optional[Dict]:
    """
    Looks up workspace entry in registry by name.

    Args:
        workspace_name: Workspace identifier (e.g., 'acme_corp')

    Returns:
        dict: Workspace registry entry or None if not found

    Example:
        >>> ws = get_workspace_by_name('acme_corp')
        >>> ws['id']
        'acme-corp-001'
        >>> ws['status']
        'active'
    """
    registry = load_workspace_registry()

    # Search active workspaces
    for ws in registry.get('workspaces', []):
        if ws['name'] == workspace_name:
            return ws

    # Search archived workspaces
    for ws in registry.get('archived', []):
        if ws['name'] == workspace_name:
            return ws

    return None


def get_workspace_by_project_id(project_id: str) -> Optional[Dict]:
    """
    Looks up workspace by project UUID (for AOS Orchestrator).

    This function enables the AOS Orchestrator to resolve a project_id trigger
    to the corresponding workspace manifest path.

    Args:
        project_id: UUID from manifest metadata.projectId

    Returns:
        dict: Workspace registry entry or None if not found

    Example:
        >>> ws = get_workspace_by_project_id('f81d4fae-7dec-11d0-a765-00a0c91e6bf6')
        >>> ws['manifestPath']
        'workspaces/acme_corp/project_manifest.json'
    """
    registry = load_workspace_registry()

    # Search active workspaces
    for ws in registry.get('workspaces', []):
        try:
            manifest = load_workspace_manifest(ws['name'])
            if manifest['metadata']['projectId'] == project_id:
                return ws
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            # Skip invalid workspace
            continue

    # If not found in workspaces, check ROOT manifest
    try:
        root_manifest = load_workspace_manifest('ROOT')
        if root_manifest['metadata']['projectId'] == project_id:
            return {
                'id': 'root-001',
                'name': 'ROOT',
                'manifestPath': 'project_manifest.json',
                'status': 'active'
            }
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        pass

    return None


def list_active_workspaces() -> List[Dict]:
    """
    Returns list of all active workspaces from registry.

    Returns:
        list: Array of workspace registry entries with status='active'

    Example:
        >>> workspaces = list_active_workspaces()
        >>> len(workspaces)
        3
        >>> workspaces[0]['name']
        'acme_corp'
    """
    registry = load_workspace_registry()
    return registry.get('workspaces', [])


def list_archived_workspaces() -> List[Dict]:
    """
    Returns list of all archived workspaces from registry.

    Returns:
        list: Array of archived workspace entries
    """
    registry = load_workspace_registry()
    return registry.get('archived', [])


# =================================================================
# WORKSPACE LIFECYCLE OPERATIONS
# =================================================================

def register_workspace(
    workspace_name: str,
    workspace_type: str,
    project_name: str,
    project_description: str,
    owner_email: str
) -> Dict:
    """
    Adds new workspace to registry (called by SOP_007).

    Args:
        workspace_name: Workspace identifier (snake_case)
        workspace_type: "internal" or "external"
        project_name: Human-readable project name
        project_description: Brief description
        owner_email: Client contact email

    Returns:
        dict: Created workspace registry entry

    Raises:
        ValueError: If workspace already exists
    """
    # Check if workspace already exists
    existing = get_workspace_by_name(workspace_name)
    if existing:
        raise ValueError(
            f"Workspace '{workspace_name}' already exists with ID: {existing['id']}"
        )

    registry = load_workspace_registry()

    # Generate unique workspace ID
    counter = 1
    workspace_id = f"{workspace_name}-{counter:03d}"

    # Check for ID collisions
    existing_ids = [ws['id'] for ws in registry.get('workspaces', [])]
    while workspace_id in existing_ids:
        counter += 1
        workspace_id = f"{workspace_name}-{counter:03d}"

    # Create new workspace entry
    new_entry = {
        'id': workspace_id,
        'name': workspace_name,
        'type': workspace_type,
        'description': project_description,
        'manifestPath': f'workspaces/{workspace_name}/project_manifest.json',
        'status': 'active',
        'createdAt': datetime.now().strftime('%Y-%m-%d'),
        'lastUpdated': datetime.now().strftime('%Y-%m-%d'),
        'metadata': {
            'owner': owner_email,
            'tags': [workspace_type]
        }
    }

    # Add to registry
    registry['workspaces'].append(new_entry)
    registry['metadata']['totalWorkspaces'] = len(registry['workspaces'])

    # Save updated registry
    save_workspace_registry(registry)

    return new_entry


def archive_workspace(
    workspace_name: str,
    reason: str = "Project delivered"
) -> Dict:
    """
    Moves workspace from active to archived in registry (called by SOP_009).

    Args:
        workspace_name: Workspace to archive
        reason: Reason for archival (for audit trail)

    Returns:
        dict: Archived workspace entry

    Raises:
        ValueError: If workspace not found or already archived
    """
    registry = load_workspace_registry()

    # Find workspace in active list
    workspace_entry = None
    for i, ws in enumerate(registry.get('workspaces', [])):
        if ws['name'] == workspace_name:
            workspace_entry = registry['workspaces'].pop(i)
            break

    if not workspace_entry:
        raise ValueError(
            f"Workspace '{workspace_name}' not found in active workspaces. "
            "It may already be archived or not exist."
        )

    # Add archival metadata
    workspace_entry['status'] = 'archived'
    workspace_entry['archivedAt'] = datetime.now().isoformat()
    workspace_entry['archivedReason'] = reason

    # Move to archived list
    if 'archived' not in registry:
        registry['archived'] = []

    registry['archived'].append(workspace_entry)

    # Update totals
    registry['metadata']['totalWorkspaces'] = len(registry['workspaces'])

    # Save updated registry
    save_workspace_registry(registry)

    return workspace_entry


# =================================================================
# VALIDATION UTILITIES
# =================================================================

def validate_workspace_name(name: str) -> bool:
    """
    Validates workspace name follows snake_case convention.

    Args:
        name: Workspace name to validate

    Returns:
        bool: True if valid, False otherwise

    Example:
        >>> validate_workspace_name('acme_corp')
        True
        >>> validate_workspace_name('Acme Corp')
        False
        >>> validate_workspace_name('acme-corp')
        False
    """
    import re
    pattern = r'^[a-z][a-z0-9_]*$'
    return bool(re.match(pattern, name))


def validate_email(email: str) -> bool:
    """
    Basic email validation.

    Args:
        email: Email address to validate

    Returns:
        bool: True if valid format, False otherwise
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_uuid(uuid_string: str) -> bool:
    """
    Validates UUID format.

    Args:
        uuid_string: UUID to validate

    Returns:
        bool: True if valid UUID, False otherwise
    """
    try:
        UUID(uuid_string, version=4)
        return True
    except (ValueError, AttributeError):
        return False


# =================================================================
# MAIN (FOR CLI TESTING)
# =================================================================

if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python workspace_utils.py list           - List active workspaces")
        print("  python workspace_utils.py get <name>     - Get workspace by name")
        print("  python workspace_utils.py active         - Show active workspace")
        sys.exit(1)

    command = sys.argv[1]

    if command == 'list':
        workspaces = list_active_workspaces()
        print(f"\nACTIVE WORKSPACES ({len(workspaces)}):")
        print("-" * 60)
        for ws in workspaces:
            print(f"  [{ws['id']}] {ws['name']}")
            print(f"    Type: {ws['type']} | Status: {ws['status']}")
            print(f"    Owner: {ws['metadata']['owner']}")
            print()

    elif command == 'get' and len(sys.argv) == 3:
        ws_name = sys.argv[2]
        ws = get_workspace_by_name(ws_name)
        if ws:
            print(json.dumps(ws, indent=2))
        else:
            print(f"Workspace '{ws_name}' not found.")

    elif command == 'active':
        active_ws = get_active_workspace()
        print(f"Active workspace: {active_ws}")
        if active_ws != 'ROOT':
            manifest_path = resolve_manifest_path()
            print(f"Manifest path: {manifest_path}")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
