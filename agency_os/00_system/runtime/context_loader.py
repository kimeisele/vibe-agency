"""Context Loader - Conveyor Belt #1: Collect ALL signals

Loads project context from multiple sources:
- Session handoff state
- Git status
- Test results
- Project manifest
- Environment checks
"""

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional


class ContextLoader:
    """Loads project context from multiple sources"""
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path.cwd()
    
    def load(self) -> Dict[str, Any]:
        """Load all context sources with robust error handling"""
        return {
            'session': self._load_session_handoff(),
            'git': self._load_git_status(),
            'tests': self._load_test_status(),
            'manifest': self._load_project_manifest(),
            'environment': self._load_environment(),
        }
    
    def _load_session_handoff(self) -> Dict[str, Any]:
        """Read .session_handoff.json - safe defaults if missing"""
        try:
            handoff_file = self.project_root / '.session_handoff.json'
            if handoff_file.exists():
                with open(handoff_file) as f:
                    data = json.load(f)
                return {
                    'phase': data.get('phase', 'PLANNING'),
                    'last_task': data.get('last_task', 'none'),
                    'blockers': data.get('blockers', []),
                    'backlog': data.get('backlog', []),
                    'backlog_item': data.get('backlog', [''])[0] if data.get('backlog') else '',
                }
            else:
                return {
                    'phase': 'PLANNING',
                    'last_task': 'none',
                    'blockers': [],
                    'backlog': [],
                    'backlog_item': '',
                }
        except Exception as e:
            return {
                'phase': 'PLANNING',
                'last_task': 'none',
                'blockers': [f'Error loading session: {str(e)}'],
                'backlog': [],
                'backlog_item': '',
            }
    
    def _load_git_status(self) -> Dict[str, Any]:
        """Get git status - safe defaults if git unavailable"""
        try:
            # Get current branch
            branch = subprocess.run(
                ['git', 'branch', '--show-current'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            # Get uncommitted changes count
            status = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            # Get recent commits
            log = subprocess.run(
                ['git', 'log', '-3', '--oneline'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            uncommitted_files = [line for line in status.stdout.strip().split('\n') if line]
            
            return {
                'branch': branch.stdout.strip() or 'unknown',
                'uncommitted': len(uncommitted_files),
                'uncommitted_files': uncommitted_files[:5],  # First 5
                'recent_commits': log.stdout.strip().split('\n'),
                'last_commit': log.stdout.strip().split('\n')[0] if log.stdout.strip() else 'none',
                'status': 'available',
            }
        except Exception as e:
            return {
                'branch': 'unknown',
                'uncommitted': 0,
                'uncommitted_files': [],
                'recent_commits': [],
                'last_commit': 'none',
                'status': f'git_unavailable: {str(e)}',
            }
    
    def _load_test_status(self) -> Dict[str, Any]:
        """Check test status - safe defaults if pytest unavailable"""
        try:
            # Check for last failed tests
            cache_file = self.project_root / '.pytest_cache' / 'v' / 'cache' / 'lastfailed'
            if cache_file.exists():
                with open(cache_file) as f:
                    failed_data = json.load(f)
                failing_tests = list(failed_data.keys())
            else:
                failing_tests = []
            
            return {
                'status': 'available',
                'failing': failing_tests,
                'failing_count': len(failing_tests),
                'errors': [],  # Would need actual test run to populate
            }
        except Exception as e:
            return {
                'status': f'pytest_unavailable: {str(e)}',
                'failing': [],
                'failing_count': 0,
                'errors': [],
            }
    
    def _load_project_manifest(self) -> Dict[str, Any]:
        """Read project_manifest.json - safe defaults if missing"""
        try:
            manifest_file = self.project_root / 'project_manifest.json'
            if manifest_file.exists():
                with open(manifest_file) as f:
                    data = json.load(f)
                return {
                    'project_type': data.get('project_type', 'unknown'),
                    'phase': data.get('phase', 'PLANNING'),
                    'focus_area': data.get('focus_area', 'general'),
                    'test_framework': data.get('test_framework', 'pytest'),
                    'docs_path': data.get('docs_path', 'docs/'),
                    'structure': data.get('structure', {}),
                }
            else:
                return {
                    'project_type': 'unknown',
                    'phase': 'PLANNING',
                    'focus_area': 'general',
                    'test_framework': 'pytest',
                    'docs_path': 'docs/',
                    'structure': {},
                }
        except Exception as e:
            return {
                'project_type': 'unknown',
                'phase': 'PLANNING',
                'focus_area': 'general',
                'test_framework': 'pytest',
                'docs_path': 'docs/',
                'structure': {},
                'error': str(e),
            }
    
    def _load_environment(self) -> Dict[str, Any]:
        """Check environment setup - safe defaults"""
        try:
            venv_exists = (self.project_root / '.venv').exists()
            
            # Check if we're in a virtual environment
            in_venv = hasattr(subprocess.sys, 'real_prefix') or \
                     (hasattr(subprocess.sys, 'base_prefix') and 
                      subprocess.sys.base_prefix != subprocess.sys.prefix)
            
            return {
                'venv_exists': venv_exists,
                'in_venv': in_venv,
                'python_version': subprocess.sys.version.split()[0],
                'status': 'ready' if (venv_exists or in_venv) else 'needs_setup',
            }
        except Exception as e:
            return {
                'venv_exists': False,
                'in_venv': False,
                'python_version': 'unknown',
                'status': f'error: {str(e)}',
            }
