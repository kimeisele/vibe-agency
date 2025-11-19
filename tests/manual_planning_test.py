#!/usr/bin/env python3
"""
Manual E2E Test: PLANNING Workflow with File-Based Delegation

This script runs the PLANNING workflow and pauses for manual responses.

How to use:
1. Run this script: python3 manual_planning_test.py
2. When it pauses, read the request file shown
3. Write a response file manually (or use the helper below)
4. The workflow continues automatically

This tests the COMPLETE integration:
- CoreOrchestrator ✓
- PlanningHandler ✓
- PromptRegistry ✓
- File-based delegation ✓
- All PLANNING agents ✓
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Add orchestrator to path
from agency_os_orchestrator import CoreOrchestrator


def show_request_file(request_file: Path):
    """Display request file for manual inspection"""
    print("\n" + "=" * 70)
    print("📬 INTELLIGENCE REQUEST")
    print("=" * 70)

    with open(request_file) as f:
        request = json.load(f)

    print(f"\n🤖 Agent: {request['agent']}")
    print(f"📋 Task: {request['task_id']}")
    print(f"🕐 Timestamp: {request['timestamp']}")
    print(f"\n📄 Request file: {request_file}")

    # Show first 500 chars of prompt
    prompt = request["prompt"]
    print("\n📝 Prompt preview (first 500 chars):")
    print("-" * 70)
    print(prompt[:500])
    if len(prompt) > 500:
        print(f"\n... ({len(prompt) - 500} more chars)")
    print("-" * 70)

    return request


def create_mock_response(request_file: Path, request: dict):
    """Helper to create mock response file"""

    # Determine response based on agent
    agent = request["agent"]
    task_id = request["task_id"]

    print(f"\n🤔 Generating mock response for {agent}.{task_id}...")

    # Mock responses for different agents (schema-compliant)
    if agent == "VIBE_ALIGNER":
        # Task: 05_scope_negotiation (planning_handler.py:339-344)
        # Schema: feature_spec.json (ORCHESTRATION_data_contracts.yaml:71-177)
        # Required: project, features, scope_negotiation, validation, metadata
        if task_id == "05_scope_negotiation":
            result = {
                "project": {
                    "name": "SimplePM - Project Management for Small Teams",
                    "category": "Web App",
                    "scale": "Small Team",
                    "target_scope": "mvp",
                    "core_problem": "Small teams (5-10 people) struggle with overcomplicated project management tools that have too many features and poor UX",
                    "target_users": "Small development teams, design agencies, and consultancies",
                },
                "features": [
                    {
                        "id": "F001",
                        "name": "User Authentication",
                        "priority": "must_have",
                        "complexity_score": 3,
                        "estimated_effort": "2 days",
                        "input": {
                            "format": "Email + password form",
                            "example": "user@example.com, password123",
                            "constraints": "Email validation, password min 8 chars",
                        },
                        "processing": {
                            "description": "Hash password, create session token",
                            "external_dependencies": ["bcrypt", "JWT library"],
                            "side_effects": ["User session created", "Auth token stored"],
                        },
                        "output": {
                            "format": "Auth token + user profile",
                            "example": "{'token': 'abc123', 'user': {...}}",
                            "success_criteria": "User can login and access dashboard",
                        },
                        "dependencies": {
                            "required": [],
                            "optional": [],
                        },
                        "fae_validation": {
                            "passed": True,
                            "constraints_checked": ["Security", "Data validation"],
                            "issues": [],
                        },
                    },
                    {
                        "id": "F002",
                        "name": "Project Dashboard",
                        "priority": "must_have",
                        "complexity_score": 5,
                        "estimated_effort": "3 days",
                        "input": {
                            "format": "User ID from auth",
                            "example": "user_123",
                            "constraints": "Authenticated user required",
                        },
                        "processing": {
                            "description": "Fetch user projects, render dashboard UI",
                            "external_dependencies": ["React", "API backend"],
                            "side_effects": ["Dashboard view loaded"],
                        },
                        "output": {
                            "format": "Dashboard page with project list",
                            "example": "List of 5 projects with status",
                            "success_criteria": "User sees all their projects",
                        },
                        "dependencies": {
                            "required": [
                                {
                                    "component": "F001",
                                    "reason": "Needs authentication",
                                    "source": "Auth Service",
                                }
                            ],
                            "optional": [],
                        },
                        "fae_validation": {
                            "passed": True,
                            "constraints_checked": ["Performance", "UX"],
                            "issues": [],
                        },
                    },
                ],
                "scope_negotiation": {
                    "total_complexity": 8,
                    "complexity_breakdown": {
                        "must_have": 8,
                        "should_have": 0,
                        "wont_have_v1": 5,
                    },
                    "timeline_estimate": "1 week MVP",
                    "v1_exclusions": ["Team Collaboration", "Data Export", "Mobile App"],
                },
                "validation": {
                    "fae_passed": True,
                    "fdg_passed": True,
                    "apce_passed": True,
                    "all_features_complete": True,
                    "ready_for_genesis": True,
                },
                "metadata": {
                    "vibe_version": "1.0",
                    "created_at": "2025-11-16T08:00:00Z",
                    "user_educated": True,
                    "scope_negotiated": True,
                },
            }
        else:
            result = {"status": "success", "data": f"Mock response for {task_id}"}

    elif agent == "MARKET_RESEARCHER":
        # Task: competitor_identification (planning_handler.py:150-155)
        result = {
            "competitors": [
                {"name": "Asana", "market_position": "Leader"},
                {"name": "Trello", "market_position": "Challenger"},
            ],
            "market_size": "$4.5B TAM",
            "trends": ["Remote work adoption", "AI-powered project management"],
            "opportunities": "Underserved small teams market",
        }

    elif agent == "TECH_RESEARCHER":
        # Task: api_evaluation (planning_handler.py:157-162)
        result = {
            "recommended_stack": {
                "backend": "Python (FastAPI)",
                "frontend": "React + TypeScript",
                "database": "PostgreSQL",
                "hosting": "AWS Lambda + RDS",
            },
            "api_integrations": ["Auth0", "Stripe", "SendGrid"],
            "architectural_pattern": "Serverless microservices",
            "scalability_notes": "Auto-scaling with Lambda, RDS read replicas for growth",
        }

    elif agent == "FACT_VALIDATOR":
        # Task: knowledge_base_audit (planning_handler.py:165-170)
        # CRITICAL: quality_score must be >= 50 or workflow blocks
        result = {
            "quality_score": 85,
            "flagged_issues": [],
            "validated_claims": [
                "Market size estimate verified via Gartner report",
                "Tech stack choices align with project constraints",
            ],
            "confidence": "HIGH",
        }

    elif agent == "USER_RESEARCHER":
        # Task: persona_generation (planning_handler.py:186-192)
        result = {
            "personas": [
                {
                    "name": "Sarah - Project Manager",
                    "goals": "Track team progress efficiently",
                    "pain_points": "Complex tools, poor mobile UX",
                },
                {
                    "name": "Mike - Developer",
                    "goals": "Quick task updates",
                    "pain_points": "Too many notifications",
                },
            ],
            "user_insights": "Small teams want simplicity over enterprise features",
        }

    elif agent == "LEAN_CANVAS_VALIDATOR":
        # LEAN_CANVAS_VALIDATOR has 3 tasks (planning_handler.py:229-309)

        if task_id == "01_canvas_interview":
            # Task 01: Canvas Interview (collect 9 fields)
            result = {
                "problem": "Small teams struggle with overcomplicated project tools",
                "solution": "Simple, focused project management for 5-10 person teams",
                "unique_value_proposition": "Get started in 5 minutes, not 5 hours",
                "unfair_advantage": "Team has built PM tools at 3 previous startups",
                "customer_segments": ["Small dev teams", "Design agencies", "Consultancies"],
                "key_metrics": ["Weekly active teams", "Tasks created per team", "Retention rate"],
                "channels": ["Product Hunt launch", "Developer communities", "Content marketing"],
                "cost_structure": ["AWS hosting", "Developer salaries", "Marketing spend"],
                "revenue_streams": ["Monthly SaaS subscription ($20/month per team)"],
            }

        elif task_id == "02_risk_analysis":
            # Task 02: Risk Analysis
            result = {
                "riskiest_assumptions": [
                    {
                        "assumption": "Small teams will pay $20/month",
                        "risk_level": "HIGH",
                        "validation_method": "Landing page + pre-sales",
                    },
                    {
                        "assumption": "Users want simplicity over features",
                        "risk_level": "MEDIUM",
                        "validation_method": "User interviews (10 target customers)",
                    },
                ]
            }

        elif task_id == "03_handoff":
            # Task 03: Handoff - Generate lean_canvas_summary.json
            # CRITICAL: readiness.status must be "READY"
            # Schema requires: canvas_fields (not canvas), riskiest_assumptions, readiness
            result = {
                "version": "1.0",
                "canvas_fields": {
                    "problem": "Small teams struggle with overcomplicated project tools. Too many features, poor UX, expensive pricing.",
                    "customer_segments": "Small dev teams (5-10 people), Design agencies, Consultancies",
                    "unique_value_proposition": "Get started in 5 minutes, not 5 hours - Simple PM tool built for small teams",
                    "solution": "User authentication, Project dashboard, Task tracking - Core PM features only",
                    "channels": "Product Hunt launch, Developer communities, Content marketing, GitHub sponsorships",
                    "revenue_streams": "Monthly SaaS subscription ($20/month per team)",
                    "cost_structure": "AWS hosting ($100/mo), Developer salaries ($8k/mo), Marketing spend ($1k/mo)",
                    "key_metrics": "Weekly active teams, Tasks created per team, Monthly retention rate",
                    "unfair_advantage": "Team has built PM tools at 3 previous startups - Deep domain knowledge",
                },
                "riskiest_assumptions": [
                    {
                        "assumption": "Small teams will pay $20/month",
                        "why_risky": "Price point untested, competition offers free tiers",
                        "validation_method": "Landing page + pre-sales campaign with 50 signups target",
                    },
                    {
                        "assumption": "Users want simplicity over features",
                        "why_risky": "May underestimate feature requirements",
                        "validation_method": "User interviews with 10 target customers",
                    },
                ],
                "readiness": {
                    "status": "READY",
                    "confidence_level": "high",
                    "missing_inputs": [],
                },
            }

        else:
            result = {"status": "success", "data": f"Mock response for {task_id}"}

    elif agent == "GENESIS_BLUEPRINT":
        # Task: 05_handoff (planning_handler.py:397-402)
        # Must return: modules, dependencies, build_config, test_strategy
        if task_id == "05_handoff":
            result = {
                "architecture_pattern": "Serverless Microservices",
                "modules": [
                    {
                        "name": "auth-service",
                        "type": "backend",
                        "tech": "Python FastAPI",
                        "responsibilities": ["User authentication", "Session management"],
                    },
                    {
                        "name": "project-service",
                        "type": "backend",
                        "tech": "Python FastAPI",
                        "responsibilities": ["Project CRUD", "Task management"],
                    },
                    {
                        "name": "web-ui",
                        "type": "frontend",
                        "tech": "React + TypeScript",
                        "responsibilities": ["User interface", "State management"],
                    },
                ],
                "dependencies": [
                    {"from": "web-ui", "to": "auth-service", "type": "REST API"},
                    {"from": "web-ui", "to": "project-service", "type": "REST API"},
                    {"from": "project-service", "to": "auth-service", "type": "Auth validation"},
                ],
                "build_config": {
                    "backend": {
                        "runtime": "Python 3.11",
                        "package_manager": "uv",
                        "deployment": "AWS Lambda",
                    },
                    "frontend": {
                        "runtime": "Node 20",
                        "build_tool": "Vite",
                        "deployment": "S3 + CloudFront",
                    },
                },
                "test_strategy": {
                    "unit_tests": "pytest (backend), Jest (frontend)",
                    "integration_tests": "Postman collections",
                    "e2e_tests": "Playwright",
                    "coverage_target": "80%",
                },
                "deployment_plan": {
                    "environments": ["dev", "staging", "prod"],
                    "ci_cd": "GitHub Actions",
                    "infrastructure": "Terraform",
                },
            }
        else:
            result = {"status": "success", "data": f"Mock response for {task_id}"}

    else:
        result = {
            "status": "success",
            "message": f"Mock response for {agent}",
            "data": "Generated by mock responder",
        }

    # Write response file
    response_file = request_file.parent / f"response_{request['request_id']}.json"
    response = {"result": result}

    with open(response_file, "w") as f:
        json.dump(response, f, indent=2)

    print(f"✅ Response written: {response_file}")
    print(f"📊 Result: {json.dumps(result, indent=2)[:200]}...")

    return response_file


def main():
    print("\n" + "=" * 70)
    print("🧪 MANUAL E2E TEST: PLANNING Workflow")
    print("=" * 70)

    # Create test project
    project_id = "manual-test-project"
    user_input = """
    Build a simple project management tool for small teams.

    Key features:
    - User authentication
    - Project dashboard
    - Task tracking
    - Team collaboration
    - Data export

    Target: Small teams (5-10 people)
    Timeline: 3 months MVP
    Budget: Limited
    """

    print(f"\n📋 Project ID: {project_id}")
    print(f"📝 User input: {user_input[:100]}...")

    # Initialize orchestrator
    print("\n🚀 Initializing CoreOrchestrator (delegated mode)...")
    orchestrator = CoreOrchestrator(repo_root=Path.cwd(), execution_mode="delegated")

    print("✅ Orchestrator initialized")

    # Create workspace directory
    workspace_dir = Path("workspaces") / project_id
    workspace_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ Workspace created: {workspace_dir}")

    # Create manifest JSON (initial)
    print("\n📦 Creating project manifest...")
    manifest_data = {
        "apiVersion": "agency.os/v1alpha1",
        "kind": "Project",
        "metadata": {
            "projectId": project_id,
            "name": project_id,
            "owner": "manual-test",
            "createdAt": datetime.now().isoformat() + "Z",
            "sdlc_version": "1.0",
            "orchestrator_version": "1.0",
        },
        "status": {
            "projectPhase": "PLANNING",
            "planningSubState": None,
            "lastUpdated": datetime.now().isoformat() + "Z",
        },
        "artifacts": {"user_input": user_input},
        "budget": {
            "max_cost_usd": 10.0,
            "current_cost_usd": 0.0,
            "alert_threshold": 0.80,
            "cost_breakdown": {},
        },
    }

    # Write manifest to disk
    manifest_path = workspace_dir / "project_manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest_data, f, indent=2)
    print(f"✅ Manifest written: {manifest_path}")

    # Load manifest (orchestrator will validate it)
    manifest = orchestrator.load_project_manifest(project_id)
    print(f"✅ Manifest loaded: phase={manifest.current_phase.value}")

    # Start planning workflow
    print("\n🎯 Starting PLANNING workflow...")
    print("   This will execute all PLANNING sub-states")
    print("   Auto-responder will handle delegation requests")
    print()

    try:
        # Execute PLANNING phase (this triggers all sub-states)
        print("📤 Calling: orchestrator.execute_phase(manifest)")
        orchestrator.execute_phase(manifest)

        print("\n" + "=" * 70)
        print("✅ PLANNING WORKFLOW COMPLETE!")
        print("=" * 70)

        print("\n📊 Final manifest:")
        print(f"   Phase: {manifest.current_phase}")
        print(f"   Sub-state: {manifest.current_sub_state}")
        print(f"   Artifacts: {len(manifest.artifacts)} items")

        # Show artifacts
        print("\n📦 Artifacts created:")
        for key, value in manifest.artifacts.items():
            if isinstance(value, dict):
                print(f"   - {key}: {len(value)} items")
            else:
                print(f"   - {key}: {type(value).__name__}")

        return True

    except Exception as e:
        print(f"\n❌ Workflow failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Check if we should use mock auto-responder
    import threading
    import time

    def auto_responder():
        """Automatically respond to delegation requests"""
        workspace_dir = Path("workspaces/manual-test-project/.delegation")

        print("\n[AUTO-RESPONDER] 🤖 Starting auto-responder thread...")

        while True:
            if not workspace_dir.exists():
                time.sleep(0.1)
                continue

            # Look for request files
            request_files = list(workspace_dir.glob("request_*.json"))

            for request_file in request_files:
                # Check if response already exists
                request_id = request_file.stem.replace("request_", "")
                response_file = workspace_dir / f"response_{request_id}.json"

                if response_file.exists():
                    continue

                print(f"\n[AUTO-RESPONDER] 📬 Found request: {request_file.name}")

                # Read request
                with open(request_file) as f:
                    request = json.load(f)

                # Show request
                show_request_file(request_file)

                # Create mock response
                create_mock_response(request_file, request)

                print("[AUTO-RESPONDER] ✅ Response ready, workflow continues...")

            time.sleep(0.2)

    # Start auto-responder in background
    responder_thread = threading.Thread(target=auto_responder, daemon=True)
    responder_thread.start()

    # Give responder time to start
    time.sleep(0.5)

    # Run main workflow
    success = main()

    sys.exit(0 if success else 1)
