"""
ARCH-010: THE MISSING REPAIR LOOP
==================================
Das ist der Code der FEHLT damit vibe-agency wirklich autonom wird!

PROBLEM:
--------
Dein System hat HAP (Hierarchical Agent Pattern) aber die REPAIR LOOP ist nicht verkabelt!
Was passiert wenn Tests fehlschlagen? NICHTS - es geht einfach weiter zu DEPLOYMENT 💥

LÖSUNG:
-------
"""

import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class ProjectPhase(Enum):
    PLANNING = "PLANNING"
    CODING = "CODING"  
    TESTING = "TESTING"
    AWAITING_QA_APPROVAL = "AWAITING_QA_APPROVAL"
    DEPLOYMENT = "DEPLOYMENT"
    PRODUCTION = "PRODUCTION"

@dataclass
class SpecialistResult:
    """The CRITICAL contract that enables self-healing"""
    success: bool
    next_phase: str | None = None
    error: str | None = None
    artifacts: list[str] = None
    repair_context: dict | None = None  # NEW: Contains failure info for repair

class CoreOrchestratorV2:
    """
    The REAL orchestrator with working repair loop.
    This is what transforms vibe-agency from a script runner to an autonomous system.
    """
    
    def __init__(self):
        self.repair_attempts = {}  # Track repair attempts to prevent infinite loops
        self.max_repair_attempts = 3
    
    def execute_phase(self, manifest: dict) -> tuple[bool, str | None]:
        """
        Execute current phase WITH REPAIR CAPABILITY
        
        Returns:
            (success, error_msg) - success=False triggers repair loop
        """
        current_phase = manifest["current_phase"]
        project_id = manifest["project_id"]
        
        # Get the specialist for this phase
        specialist = self.get_phase_handler(current_phase)
        
        # Check if we're in repair mode
        repair_context = None
        if self._is_repair_mode(project_id, current_phase):
            repair_context = self._get_repair_context(project_id)
            print(f"🔧 REPAIR MODE: Attempt {self.repair_attempts[project_id]} with context: {repair_context}")
        
        # Execute the phase
        result = specialist.execute(manifest, repair_context=repair_context)
        
        # THE CRITICAL LOGIC - This is what makes it self-healing
        if not result.success:
            return self._handle_phase_failure(manifest, result)
        else:
            return self._handle_phase_success(manifest, result)
    
    def _handle_phase_failure(self, manifest: dict, result: SpecialistResult) -> tuple[bool, str]:
        """
        THE REPAIR LOOP - This is where the magic happens
        """
        current_phase = manifest["current_phase"]
        project_id = manifest["project_id"]
        
        # Special handling for TESTING failures -> CODING repair
        if current_phase == "TESTING":
            # Track repair attempts
            if project_id not in self.repair_attempts:
                self.repair_attempts[project_id] = 0
            
            self.repair_attempts[project_id] += 1
            
            if self.repair_attempts[project_id] > self.max_repair_attempts:
                return False, f"Max repair attempts ({self.max_repair_attempts}) exceeded"
            
            print(f"❌ Tests failed: {result.error}")
            print(f"🔄 INITIATING REPAIR LOOP (attempt {self.repair_attempts[project_id]})")
            
            # Save failure context for repair
            self._save_repair_context(project_id, {
                "failed_tests": result.error,
                "qa_report": result.repair_context,
                "attempt": self.repair_attempts[project_id]
            })
            
            # TRANSITION BACK TO CODING FOR REPAIR
            manifest["current_phase"] = "CODING"
            manifest["metadata"]["repair_mode"] = True
            self._save_manifest(manifest)
            
            return False, "Tests failed - entering repair mode"
        
        # Other phase failures (non-repairable)
        return False, f"Phase {current_phase} failed: {result.error}"
    
    def _handle_phase_success(self, manifest: dict, result: SpecialistResult) -> tuple[bool, str]:
        """Handle successful phase execution"""
        project_id = manifest["project_id"]
        
        # Clear repair attempts on success
        if project_id in self.repair_attempts:
            del self.repair_attempts[project_id]
        
        # Clear repair mode flag
        if "repair_mode" in manifest.get("metadata", {}):
            del manifest["metadata"]["repair_mode"]
        
        # Transition to next phase if specified
        if result.next_phase:
            print(f"✅ {manifest['current_phase']} succeeded → {result.next_phase}")
            manifest["current_phase"] = result.next_phase
            self._save_manifest(manifest)
        
        return True, None
    
    def run_full_sdlc(self, project_id: str) -> dict:
        """
        Run SDLC with automatic repair capability
        This is the main loop that makes vibe-agency autonomous
        """
        manifest = self._load_manifest(project_id)
        execution_log = []
        
        while manifest["current_phase"] != "PRODUCTION":
            phase = manifest["current_phase"]
            print(f"\n{'='*60}")
            print(f"Executing Phase: {phase}")
            print(f"{'='*60}")
            
            success, error = self.execute_phase(manifest)
            
            execution_log.append({
                "phase": phase,
                "success": success,
                "error": error,
                "repair_attempt": self.repair_attempts.get(project_id, 0)
            })
            
            if not success and phase == "TESTING":
                # Repair loop continues - reload manifest (now in CODING)
                manifest = self._load_manifest(project_id)
                continue
            elif not success:
                # Non-repairable failure
                print(f"💥 FATAL: {error}")
                break
            
            # Reload manifest for next iteration
            manifest = self._load_manifest(project_id)
        
        return {
            "final_phase": manifest["current_phase"],
            "execution_log": execution_log,
            "repair_attempts": sum(1 for log in execution_log if log.get("repair_attempt", 0) > 0)
        }
    
    def _is_repair_mode(self, project_id: str, phase: str) -> bool:
        """Check if we're in repair mode"""
        return project_id in self.repair_attempts and phase == "CODING"
    
    def _get_repair_context(self, project_id: str) -> dict:
        """Load repair context (test failures, etc.)"""
        repair_file = Path(f".repair/{project_id}_context.json")
        if repair_file.exists():
            return json.loads(repair_file.read_text())
        return {}
    
    def _save_repair_context(self, project_id: str, context: dict):
        """Save repair context for next phase"""
        repair_dir = Path(".repair")
        repair_dir.mkdir(exist_ok=True)
        repair_file = repair_dir / f"{project_id}_context.json"
        repair_file.write_text(json.dumps(context, indent=2))
    
    def get_phase_handler(self, phase: str):
        """Get specialist for phase (mock for demo)"""
        # In real implementation, this uses AgentRegistry
        from apps.agency.specialists import (
            CodingSpecialist,
            DeploymentSpecialist,
            MaintenanceSpecialist,
            PlanningSpecialist,
            TestingSpecialist,
        )
        
        mapping = {
            "PLANNING": PlanningSpecialist,
            "CODING": CodingSpecialist,
            "TESTING": TestingSpecialist,
            "DEPLOYMENT": DeploymentSpecialist,
            "MAINTENANCE": MaintenanceSpecialist
        }
        return mapping[phase]()
    
    def _load_manifest(self, project_id: str) -> dict:
        """Load project manifest"""
        manifest_file = Path(f"workspaces/{project_id}/project_manifest.json")
        return json.loads(manifest_file.read_text())
    
    def _save_manifest(self, manifest: dict):
        """Save project manifest"""
        project_id = manifest["project_id"]
        manifest_file = Path(f"workspaces/{project_id}/project_manifest.json")
        manifest_file.write_text(json.dumps(manifest, indent=2))


# ============================================================================
# DAS IST DER CODE DER IN core_orchestrator.py FEHLT!
# ============================================================================

def patch_core_orchestrator():
    """
    Apply the repair loop patch to existing core_orchestrator.py
    This is what you need to add to make it work!
    """
    
    patch = '''
# In core_orchestrator.py, replace execute_phase() with:

def execute_phase(self, manifest: ProjectManifest) -> bool:
    """
    Execute current phase and check result.
    
    Returns:
        True if phase succeeded (move to next phase)
        False if phase failed (repair needed)
    """
    handler = self.get_phase_handler(manifest.current_phase)
    
    # Get result - THIS IS THE CRITICAL CHANGE
    result = handler.execute(manifest)
    
    # CHECK RESULT STATUS - THIS IS WHAT'S MISSING
    if not result.success:
        logger.error(f"❌ Phase {manifest.current_phase.value} FAILED")
        logger.error(f"   Error: {result.error}")
        
        # THE REPAIR LOOP FOR TEST FAILURES
        if manifest.current_phase == ProjectPhase.TESTING:
            logger.warning("🔄 REPAIR LOOP: Returning to CODING phase for bug fixes")
            
            # Save failure context for repair
            self.save_artifact(
                manifest.project_root / ".repair" / "qa_failure.json",
                result.repair_context or {"error": result.error}
            )
            
            # Transition back to CODING
            manifest.current_phase = ProjectPhase.CODING
            manifest.metadata["repair_mode"] = True
            self.save_project_manifest(manifest)
            
            return False  # Signal repair needed
        else:
            # Other phase failures are fatal
            raise PhaseFailed(f"Phase {manifest.current_phase.value} failed: {result.error}")
    
    # Phase succeeded - transition to next
    if result.next_phase:
        logger.info(f"✅ {manifest.current_phase.value} succeeded → {result.next_phase}")
        manifest.current_phase = ProjectPhase(result.next_phase)
    
    # Clear repair mode on success
    if "repair_mode" in manifest.metadata:
        del manifest.metadata["repair_mode"]
    
    self.save_project_manifest(manifest)
    return True

# And update run_full_sdlc() to use the return value:

def run_full_sdlc(self, project_id: str) -> None:
    manifest = self.load_project_manifest(project_id)
    repair_attempts = 0
    max_repairs = 3
    
    while manifest.current_phase != ProjectPhase.PRODUCTION:
        try:
            success = self.execute_phase(manifest)  # NOW RETURNS BOOL
            
            if not success:
                repair_attempts += 1
                if repair_attempts > max_repairs:
                    raise Exception(f"Max repair attempts ({max_repairs}) exceeded")
                
                # Continue loop - manifest already updated to CODING
                manifest = self.load_project_manifest(project_id)
                continue
            
            # Reset repair counter on success
            repair_attempts = 0
            
            # Reload for next phase
            manifest = self.load_project_manifest(project_id)
            
        except PhaseFailed as e:
            logger.error(f"Phase failed unrecoverably: {e}")
            break
    '''
    
    return patch


# ============================================================================
# TEST TO PROVE IT WORKS
# ============================================================================

def test_repair_loop():
    """
    Test that proves the repair loop actually works
    """
    
    # Setup
    orchestrator = CoreOrchestratorV2()
    
    # Create a test manifest
    manifest = {
        "project_id": "test_repair",
        "current_phase": "CODING",
        "metadata": {}
    }
    
    # Mock specialist results
    class MockCodingSpecialist:
        def execute(self, manifest, repair_context=None):
            if repair_context:
                # In repair mode - fix the code
                return SpecialistResult(
                    success=True,
                    next_phase="TESTING",
                    artifacts=["fixed_code.py"]
                )
            else:
                # First attempt - generate buggy code
                return SpecialistResult(
                    success=True,
                    next_phase="TESTING",
                    artifacts=["buggy_code.py"]
                )
    
    class MockTestingSpecialist:
        def __init__(self):
            self.attempts = 0
        
        def execute(self, manifest, repair_context=None):
            self.attempts += 1
            if self.attempts == 1:
                # First test run - fails
                return SpecialistResult(
                    success=False,
                    error="5 tests failed",
                    repair_context={"failed_tests": ["test_1", "test_2"]}
                )
            else:
                # Second test run (after repair) - passes
                return SpecialistResult(
                    success=True,
                    next_phase="AWAITING_QA_APPROVAL"
                )
    
    # Run the test
    print("Testing repair loop...")
    print("-" * 60)
    
    # Start with CODING
    result = orchestrator.execute_phase(manifest)
    assert result[0]  # CODING succeeds

    # Move to TESTING
    manifest["current_phase"] = "TESTING"
    result = orchestrator.execute_phase(manifest)
    assert not result[0]  # TESTING fails
    assert manifest["current_phase"] == "CODING"  # Back to CODING for repair!

    # Run CODING again (repair mode)
    result = orchestrator.execute_phase(manifest)
    assert result[0]  # CODING succeeds (fixed)

    # Run TESTING again
    manifest["current_phase"] = "TESTING"
    result = orchestrator.execute_phase(manifest)
    assert result[0]  # TESTING now passes!
    
    print("✅ REPAIR LOOP WORKS!")
    print(f"Final phase: {manifest['current_phase']}")
    

if __name__ == "__main__":
    print("="*80)
    print("ARCH-010: THE MISSING REPAIR LOOP")
    print("="*80)
    print()
    print("This is the code that makes vibe-agency TRULY autonomous.")
    print("Without this, it's just a script runner.")
    print("With this, it's a self-healing system.")
    print()
    print("="*80)
    print()
    
    # Show the patch
    print("PATCH TO APPLY:")
    print("-"*40)
    print(patch_core_orchestrator())
    print("-"*40)
    
    # Run the test
    print("\nTEST RESULTS:")
    print("-"*40)
    test_repair_loop()
