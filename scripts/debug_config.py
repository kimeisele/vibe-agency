#!/usr/bin/env python3
"""
GAD-100: Configuration Diagnostic Tool
=======================================

Diagnoses why the system claims "No API Keys" even when they are set.

This script:
1. Shows raw os.environ keys (MASKED VALUES) to prove they exist
2. Shows loaded PhoenixConfig values to prove they are parsed
3. Shows what factory.py sees when detecting providers
4. Identifies naming mismatches (e.g., VIBE_GOOGLE_API_KEY vs GOOGLE_API_KEY)

Usage:
    python3 scripts/debug_config.py

Version: 1.0 (GAD-100 Emergency)
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def mask_value(value: str) -> str:
    """Mask sensitive values, showing only first/last 4 chars"""
    if not value or len(value) < 8:
        return "***MASKED***"
    return f"{value[:4]}...{value[-4:]}"


def print_section(title: str) -> None:
    """Print a section header"""
    print()
    print("=" * 80)
    print(f"  {title}")
    print("=" * 80)


def check_env_vars():
    """Check raw environment variables"""
    print_section("1. RAW ENVIRONMENT VARIABLES")

    # API Keys we're looking for
    api_key_vars = [
        "GOOGLE_API_KEY",
        "ANTHROPIC_API_KEY",
        "OPENAI_API_KEY",
        "VIBE_GOOGLE_API_KEY",
        "VIBE_ANTHROPIC_API_KEY",
        "VIBE_OPENAI_API_KEY",
        "VIBE_MODEL_API_KEY",
    ]

    print("\nAPI Key Environment Variables:")
    found_any = False
    for var in api_key_vars:
        value = os.environ.get(var)
        if value:
            print(f"  ✅ {var} = {mask_value(value)}")
            found_any = True
        else:
            print(f"  ❌ {var} = NOT SET")

    if not found_any:
        print("\n⚠️  WARNING: No API key environment variables found!")
        print("   The system will run in NoOp mode (mock/knowledge-only).")

    # Other relevant env vars
    print("\nOther Relevant Variables:")
    other_vars = ["VIBE_LIVE_FIRE", "VIBE_SAFETY_LIVE_FIRE_ENABLED", "VIBE_MODEL_PROVIDER"]
    for var in other_vars:
        value = os.environ.get(var)
        status = "✅" if value else "❌"
        print(f"  {status} {var} = {value or 'NOT SET'}")

    # Show ALL VIBE_* vars
    print("\nAll VIBE_* Variables:")
    vibe_vars = {k: v for k, v in os.environ.items() if k.startswith("VIBE_")}
    if vibe_vars:
        for var, value in sorted(vibe_vars.items()):
            # Mask if it looks like a key
            if "KEY" in var or "TOKEN" in var or "SECRET" in var:
                print(f"  {var} = {mask_value(value)}")
            else:
                print(f"  {var} = {value}")
    else:
        print("  (none found)")


def check_phoenix_config():
    """Check PhoenixConfig loading"""
    print_section("2. PHOENIX CONFIG LOADING")

    try:
        from agency_os.config.phoenix import get_config

        config = get_config()

        print("\n✅ PhoenixConfig loaded successfully")

        print("\nModel Configuration:")
        print(f"  Provider: {config.model.provider}")
        print(f"  Model Name: {config.model.model_name}")
        print(f"  API Key: {'✅ SET' if config.model.api_key else '❌ NOT SET'}")
        if config.model.api_key:
            print(f"    (masked: {mask_value(config.model.api_key)})")
        print(f"  Max Tokens: {config.model.max_tokens}")
        print(f"  Temperature: {config.model.temperature}")

        print("\nSafety Configuration:")
        print(f"  Live Fire Enabled: {config.safety.live_fire_enabled}")
        print(f"  Quota Enforcement: {config.safety.enable_quota_enforcement}")
        print(f"  Cost Tracking: {config.safety.enable_cost_tracking}")

        print("\nSystem Configuration:")
        print(f"  Environment: {config.system.environment}")
        print(f"  Debug: {config.system.debug}")
        print(f"  Log Level: {config.system.log_level}")

    except Exception as e:
        print(f"\n❌ Failed to load PhoenixConfig: {e}")
        import traceback

        traceback.print_exc()


def check_provider_detection():
    """Check what factory.py sees"""
    print_section("3. PROVIDER FACTORY DETECTION")

    try:
        # Import factory detection functions using importlib to bypass naming issues
        import importlib.util
        import sys

        factory_path = (
            project_root / "agency_os" / "00_system" / "runtime" / "providers" / "factory.py"
        )
        spec = importlib.util.spec_from_file_location("factory", factory_path)
        if spec and spec.loader:
            factory = importlib.util.module_from_spec(spec)
            sys.modules["factory"] = factory
            spec.loader.exec_module(factory)

            print("\nProvider Detection:")
            detected = factory._detect_provider()
            print(f"  Detected Provider: {detected}")

            print("\nAPI Key Lookup for Each Provider:")
            for provider in ["google", "anthropic", "openai", "local"]:
                api_key = factory._get_api_key_for_provider(provider)
                status = "✅ FOUND" if api_key else "❌ NOT FOUND"
                print(f"  {provider}: {status}")
                if api_key:
                    print(f"    (masked: {mask_value(api_key)})")
        else:
            print("\n❌ Failed to load factory module")

    except Exception as e:
        print(f"\n❌ Failed to check provider detection: {e}")
        import traceback

        traceback.print_exc()


def check_llm_client_init():
    """Check LLM Client initialization"""
    print_section("4. LLM CLIENT INITIALIZATION")

    try:
        # Import LLMClient using importlib to bypass naming issues
        import importlib.util
        import sys

        llm_client_path = project_root / "agency_os" / "00_system" / "runtime" / "llm_client.py"
        spec = importlib.util.spec_from_file_location("llm_client", llm_client_path)
        if spec and spec.loader:
            llm_client = importlib.util.module_from_spec(spec)
            sys.modules["llm_client"] = llm_client
            spec.loader.exec_module(llm_client)

            print("\nInitializing LLMClient...")
            client = llm_client.LLMClient()

            print(f"  Mode: {client.mode}")
            print(f"  Provider: {client.provider.get_provider_name()}")

            if client.mode == "noop":
                print("\n⚠️  WARNING: Client is in NoOp mode!")
                print("   This means no API keys were detected.")
                print("   Real LLM invocations will be mocked.")
            else:
                print(
                    f"\n✅ Client initialized with {client.provider.get_provider_name()} provider"
                )
                print("   Real LLM invocations are possible.")
        else:
            print("\n❌ Failed to load llm_client module")

    except Exception as e:
        print(f"\n❌ Failed to initialize LLMClient: {e}")
        import traceback

        traceback.print_exc()


def print_recommendations():
    """Print recommendations based on findings"""
    print_section("5. RECOMMENDATIONS")

    # Check if any standard API keys are set
    has_google = os.environ.get("GOOGLE_API_KEY")
    has_anthropic = os.environ.get("ANTHROPIC_API_KEY")
    has_openai = os.environ.get("OPENAI_API_KEY")

    if not (has_google or has_anthropic or has_openai):
        print("\n⚠️  NO API KEYS DETECTED")
        print("\nThe system expects API keys in these exact environment variable names:")
        print("  • GOOGLE_API_KEY (for Google Gemini)")
        print("  • ANTHROPIC_API_KEY (for Claude)")
        print("  • OPENAI_API_KEY (for OpenAI)")
        print("\nTo fix this:")
        print("  1. Check your .env file (should be in project root)")
        print("  2. Ensure variable names match exactly (case-sensitive)")
        print("  3. Source the .env file: source .env")
        print("  4. Or export manually: export GOOGLE_API_KEY='your-key-here'")
        print("\n💡 The factory.py checks os.environ directly, NOT PhoenixConfig.")
        print("   So the keys must be in the environment, not just in .env file.")
    else:
        print("\n✅ API keys detected in environment")
        print("\nFound:")
        if has_google:
            print("  • GOOGLE_API_KEY ✅")
        if has_anthropic:
            print("  • ANTHROPIC_API_KEY ✅")
        if has_openai:
            print("  • OPENAI_API_KEY ✅")

        print("\n💡 If you're still seeing 'No API Keys' errors:")
        print("  1. Ensure you sourced .env: source .env")
        print("  2. Check if the keys are in the current shell: echo $GOOGLE_API_KEY")
        print("  3. Try running with explicit env: GOOGLE_API_KEY=xxx python script.py")


def main():
    """Run all diagnostics"""
    print("=" * 80)
    print("  VIBE AGENCY - CONFIGURATION DIAGNOSTIC TOOL")
    print("  GAD-100: Debugging 'No API Keys' Issue")
    print("=" * 80)

    check_env_vars()
    check_phoenix_config()
    check_provider_detection()
    check_llm_client_init()
    print_recommendations()

    print()
    print("=" * 80)
    print("  DIAGNOSTIC COMPLETE")
    print("=" * 80)
    print()


if __name__ == "__main__":
    main()
