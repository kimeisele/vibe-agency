"""Boot Sequence - Main entry point for system-boot.sh → vibe-cli boot

Orchestrates the conveyor belt:
1. Context Loader → Collect signals
2. Playbook Engine → Route to task
3. Prompt Composer → Compose final prompt
"""

import sys
from pathlib import Path
from typing import Optional

from context_loader import ContextLoader
from playbook_engine import PlaybookEngine
from prompt_composer import PromptComposer


class BootSequence:
    """Main entry point for system boot"""
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path.cwd()
        self.context_loader = ContextLoader(self.project_root)
        self.playbook_engine = PlaybookEngine()
        self.prompt_composer = PromptComposer()
    
    def run(self, user_input: Optional[str] = None):
        """Execute the boot sequence"""
        
        # PRE-FLIGHT: Check for uncommitted changes (graceful guardrail)
        git_status = self._check_uncommitted_changes()
        if git_status['has_uncommitted'] and not git_status['is_clean_state']:
            self._display_commit_warning(git_status)
            return  # Soft halt - exit cleanly, agent sees warning
        
        # Conveyor Belt 1: Load Context
        print("🔄 Loading context...", file=sys.stderr)
        context = self.context_loader.load()
        
        # Conveyor Belt 2: Route to Task
        print("🎯 Routing to task...", file=sys.stderr)
        route = self.playbook_engine.route(user_input or "", context)
        
        # Conveyor Belt 3: Compose Prompt
        print("📝 Composing prompt...", file=sys.stderr)
        prompt = self.prompt_composer.compose(route.task, context)
        
        # Add system prompt (prime agent properly)
        system_prompt = self._get_system_prompt(route)
        final_prompt = system_prompt + "\n\n" + prompt
        
        # Display dashboard
        self._display_dashboard(context, route)
        
        # Output prompt for STEWARD
        print("\n" + "=" * 80, file=sys.stderr)
        print(final_prompt)
        print("=" * 80 + "\n", file=sys.stderr)
    
    def _check_uncommitted_changes(self) -> dict:
        """Check for uncommitted changes - graceful detection"""
        try:
            import subprocess
            
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5,
                check=True
            )
            
            uncommitted = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
            
            return {
                'has_uncommitted': len(uncommitted) > 0,
                'files': uncommitted[:10],  # First 10
                'count': len(uncommitted),
                'is_clean_state': len(uncommitted) == 0
            }
        except Exception as e:
            return {
                'has_uncommitted': False,
                'files': [],
                'count': 0,
                'is_clean_state': True,
                'error': str(e)
            }
    
    def _display_commit_warning(self, git_status: dict) -> None:
        """Display graceful halt warning for uncommitted changes"""
        count = git_status['count']
        files = git_status['files']
        
        warning = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         ⚠️  BOOT HALTED - SOFT GUARDRAIL                     ║
╚══════════════════════════════════════════════════════════════════════════════╝

❌ UNCOMMITTED CHANGES DETECTED ({count} files)

Files:
"""
        for f in files:
            warning += f"  {f}\n"
        
        warning += """
ACTION REQUIRED:

  Option 1: Commit changes (recommended)
    git add .
    git commit -m "your message"

  Option 2: Stash changes (if not ready)
    git stash

  Option 3: Force boot (if absolutely necessary)
    ./vibe-cli boot --force

────────────────────────────────────────────────────────────────────────────────
🎯 Why this matters:
  • Agents need clean state to track their work
  • Uncommitted changes hide what was actually changed
  • Forces explicit handoff via git commits
  • Prevents "forgot what I did" scenarios

Boot will resume once changes are committed or stashed.
────────────────────────────────────────────────────────────────────────────────
"""
        print(warning, file=sys.stderr)
    
    def _get_system_prompt(self, route) -> str:
        """System prompt to prime agents properly"""
        return """⚡ STEWARD SYSTEM PROMPT

You are STEWARD, the senior orchestration agent at vibe-agency.

CORE RESPONSIBILITIES:
1. Execute the assigned task methodically
2. Follow anti-slop rules strictly (no shortcuts)
3. Update session state when done (crucial for next boot)
4. Commit work with clear messages
5. Report completion + next steps

EXECUTION PROTOCOL:
✅ READ: Understand task completely
✅ PLAN: Break into steps
✅ EXECUTE: Run each step, verify
✅ TEST: Verify success criteria met
✅ COMMIT: `git add .` + clear message
✅ HANDOFF: Update .session_handoff.json

STATE MANAGEMENT:
Your work is only "done" when:
1. Code changes committed to git
2. .session_handoff.json updated with:
   - current phase
   - last_task completed
   - blockers (if any)
   - backlog (remaining work)

NEXT AGENT DEPENDS ON YOU:
• Next boot reads your commits
• Next agent reads your handoff
• Your clean state = their clarity

DO NOT:
❌ Leave uncommitted changes
❌ Skip .session_handoff.json update
❌ Claim done without testing
❌ Ignore anti-slop rules
❌ Skip documentation updates

DO:
✅ Be surgical and precise
✅ Make minimal changes
✅ Test before claiming complete
✅ Update session state
✅ Commit with context
"""
    
    def _check_git_sync(self) -> dict:
        """Check if repo is behind remote - graceful fallback if git fails"""
        try:
            import subprocess
            
            # Fetch latest refs (non-destructive)
            subprocess.run(
                ['git', 'fetch', 'origin'],
                cwd=self.project_root,
                capture_output=True,
                timeout=5,
                check=False  # Don't fail if fetch fails
            )
            
            # Count commits behind
            result = subprocess.run(
                ['git', 'rev-list', '--count', 'HEAD..origin/main'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5,
                check=True
            )
            
            commits_behind = int(result.stdout.strip())
            return {
                'behind': commits_behind > 0,
                'commits_behind': commits_behind,
                'status': 'sync_needed' if commits_behind > 0 else 'up_to_date'
            }
        except Exception as e:
            # Graceful fallback - don't break boot
            return {
                'behind': False,
                'commits_behind': 0,
                'status': 'unknown',
                'error': str(e)
            }
    
    def _display_dashboard(self, context: dict, route) -> None:
        """Display system status dashboard"""
        
        session = context.get('session', {})
        git = context.get('git', {})
        tests = context.get('tests', {})
        env = context.get('environment', {})
        
        # Check git sync status
        sync_status = self._check_git_sync()
        
        # Calculate status indicators
        test_emoji = '✅' if tests.get('failing_count', 0) == 0 else '❌'
        git_emoji = '✅' if git.get('uncommitted', 0) == 0 else '⚠️'
        env_emoji = '✅' if env.get('status') == 'ready' else '⚠️'
        sync_emoji = '✅' if not sync_status.get('behind') else '⚠️'
        
        dashboard = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           🤖 VIBE AGENCY SYSTEM BOOT                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

📊 SYSTEM STATUS
  {test_emoji} Tests: {tests.get('failing_count', 0)} failing, {tests.get('status', 'unknown')}
  {git_emoji} Git: {git.get('uncommitted', 0)} uncommitted files on '{git.get('branch', 'unknown')}'
  {sync_emoji} Sync: {sync_status.get('commits_behind', 0)} commits behind origin/main
  {env_emoji} Environment: {env.get('status', 'unknown')}

"""
        
        # Add sync suggestion if behind
        if sync_status.get('behind'):
            behind_count = sync_status.get('commits_behind', 0)
            dashboard += f"""⚠️  REPO OUT OF SYNC ({behind_count} commits behind)
  To sync: git pull origin main
  
"""
        
        dashboard += f"""
🎯 RECOMMENDED TASK
  Task: {route.task.upper()}
  Description: {route.description}
  Confidence: {route.confidence}
  Reason: {route.source}

📋 PROJECT STATE
  Phase: {session.get('phase', 'UNKNOWN')}
  Last Task: {session.get('last_task', 'none')}
  Backlog Items: {len(session.get('backlog', []))}

"""
        
        # Show available routes if in suggestion mode
        if route.confidence == 'suggested':
            routes = self.playbook_engine.list_available_routes()
            dashboard += "\n💡 AVAILABLE ROUTES:\n"
            for r in routes[:5]:
                examples = ', '.join(r['examples'][:2])
                dashboard += f"  - {r['name']}: {r['description']}\n"
                dashboard += f"    Examples: {examples}\n"
        
        print(dashboard, file=sys.stderr)
    
    def show_routes(self) -> None:
        """Show all available playbook routes"""
        routes = self.playbook_engine.list_available_routes()
        
        print("\n╔══════════════════════════════════════════════════════════════════════════════╗")
        print("║                        📚 AVAILABLE PLAYBOOK ROUTES                          ║")
        print("╚══════════════════════════════════════════════════════════════════════════════╝\n")
        
        for route in routes:
            print(f"🎯 {route['name'].upper()}")
            print(f"   {route['description']}")
            print(f"   Examples: {', '.join(route['examples'])}")
            print()
    
    def health_check(self) -> bool:
        """Quick health check - returns True if system is operational"""
        try:
            context = self.context_loader.load()
            
            # Check critical components
            git_ok = context.get('git', {}).get('status') == 'available'
            env_ok = context.get('environment', {}).get('status') in ['ready', 'needs_setup']
            
            if not git_ok:
                print("⚠️ Git not available", file=sys.stderr)
            if not env_ok:
                print("⚠️ Environment issues detected", file=sys.stderr)
            
            return git_ok and env_ok
        except Exception as e:
            print(f"❌ Health check failed: {e}", file=sys.stderr)
            return False
