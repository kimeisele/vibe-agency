"""
GAD-907: Semantic Lens Loader
==============================

Load mental models and thinking frameworks from YAML and format them
into imperative system prompts that transform agent mindset.

Purpose:
  Transform raw lens YAML → Powerful system prompt injection

Architecture:
  - Reads lens YAML from agency_os/core_system/knowledge/lenses/
  - Extracts key_concepts, framing_questions, execution_protocol
  - Formats into a strong, imperative mindset injection prompt
  - Returns formatted string ready for context injection

Usage:
  from agency_os.core_system.knowledge.lens_loader import load_lens

  lens_prompt = load_lens("first_principles")
  # Use lens_prompt to enrich agent context

Version: 1.0 (GAD-907 - Lens Injection Mechanism)
"""

import logging
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)


class LensLoadError(Exception):
    """Raised when lens loading fails."""

    pass


def load_lens(lens_id: str) -> str:
    """
    Load a semantic lens and format it as a system prompt.

    Args:
        lens_id: The lens identifier (e.g., "first_principles")

    Returns:
        Formatted system prompt string with lens mindset

    Raises:
        LensLoadError: If lens file not found or invalid

    Example:
        >>> lens_prompt = load_lens("first_principles")
        >>> print(lens_prompt[:50])
        [MINDSET: First Principles Thinking]
    """
    # Locate lens file
    repo_root = Path(__file__).parent.parent.parent.parent
    lens_path = repo_root / "agency_os" / "core_system" / "knowledge" / "lenses" / f"{lens_id}.yaml"

    if not lens_path.exists():
        available_lenses = list_available_lenses()
        raise LensLoadError(
            f"Lens '{lens_id}' not found at {lens_path}\n"
            f"Available lenses: {', '.join(available_lenses)}"
        )

    # Load YAML
    try:
        with open(lens_path) as f:
            lens_data = yaml.safe_load(f)
    except Exception as e:
        raise LensLoadError(f"Failed to parse lens YAML: {e}")

    if "lens" not in lens_data:
        raise LensLoadError("Invalid lens file: missing 'lens' root key")

    lens = lens_data["lens"]

    # Format lens into system prompt
    prompt = _format_lens_prompt(lens)

    logger.info(f"✅ Loaded lens: {lens.get('name', lens_id)} ({len(prompt)} chars)")

    return prompt


def _format_lens_prompt(lens: dict) -> str:
    """
    Format lens data into an imperative system prompt.

    Strategy:
      1. Header with lens identity
      2. Mindset shift (worker → engineer)
      3. Key concepts (mental model building blocks)
      4. Framing questions (how to think)
      5. Execution protocol (step-by-step process)
      6. Footer with activation reminder

    Returns:
        Formatted prompt string
    """
    parts = []

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # HEADER
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    name = lens.get("name", "Unknown Lens")
    description = lens.get("description", "")

    parts.append("=" * 80)
    parts.append(f"[MINDSET INJECTION: {name.upper()}]")
    parts.append("=" * 80)
    parts.append("")
    parts.append(f"MENTAL MODEL: {name}")
    parts.append(f"PURPOSE: {description}")
    parts.append("")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # PERSPECTIVE SHIFT (Most Important!)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    if "perspective_shift" in lens:
        shift = lens["perspective_shift"]
        parts.append("━" * 80)
        parts.append("⚡ MINDSET TRANSFORMATION")
        parts.append("━" * 80)
        parts.append("")

        if "mindset_shift" in shift:
            # Use the raw mindset shift text (most powerful part)
            parts.append(shift["mindset_shift"].strip())
            parts.append("")

        if "from" in shift and "to" in shift:
            from_mode = shift["from"]
            to_mode = shift["to"]

            parts.append(f"FROM: {from_mode.get('mode', 'worker').upper()} MODE")
            if "characteristics" in from_mode:
                for char in from_mode["characteristics"][:3]:  # Top 3
                    parts.append(f"  ❌ {char}")
            parts.append("")

            parts.append(f"TO: {to_mode.get('mode', 'engineer').upper()} MODE")
            if "characteristics" in to_mode:
                for char in to_mode["characteristics"][:3]:  # Top 3
                    parts.append(f"  ✅ {char}")
            parts.append("")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # KEY CONCEPTS (Mental Model Building Blocks)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    if "key_concepts" in lens:
        parts.append("━" * 80)
        parts.append("🧠 KEY CONCEPTS (Mental Model)")
        parts.append("━" * 80)
        parts.append("")

        for i, concept in enumerate(lens["key_concepts"][:5], 1):  # Top 5
            name = concept.get("name", "Concept")
            definition = concept.get("definition", "")

            parts.append(f"{i}. {name.upper()}")
            parts.append(f"   {definition}")

            # Include "how_to_identify" if present (most actionable)
            if "how_to_identify" in concept:
                parts.append("")
                parts.append("   How to apply:")
                # Indent each line
                how_to = concept["how_to_identify"].strip()
                for line in how_to.split("\n"):
                    parts.append(f"   {line}")

            parts.append("")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # FRAMING QUESTIONS (How to Think)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    if "framing_questions" in lens:
        parts.append("━" * 80)
        parts.append("❓ FRAMING QUESTIONS (How to Think)")
        parts.append("━" * 80)
        parts.append("")

        questions = lens["framing_questions"]

        if "pre_execution" in questions:
            parts.append("BEFORE STARTING:")
            pre = questions["pre_execution"]
            if isinstance(pre, dict) and "questions" in pre:
                for q in pre["questions"][:4]:  # Top 4
                    parts.append(f"  • {q}")
            parts.append("")

        if "during_execution" in questions:
            parts.append("WHILE WORKING:")
            during = questions["during_execution"]
            if isinstance(during, dict) and "questions" in during:
                for q in during["questions"][:4]:  # Top 4
                    parts.append(f"  • {q}")
            parts.append("")

        if "post_execution" in questions:
            parts.append("AFTER COMPLETING:")
            post = questions["post_execution"]
            if isinstance(post, dict) and "questions" in post:
                for q in post["questions"][:3]:  # Top 3
                    parts.append(f"  • {q}")
            parts.append("")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # EXECUTION PROTOCOL (Step-by-step Process)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    if "execution_protocol" in lens:
        parts.append("━" * 80)
        parts.append("⚙️  EXECUTION PROTOCOL")
        parts.append("━" * 80)
        parts.append("")

        protocol = lens["execution_protocol"]

        # Extract steps (step_1, step_2, etc.)
        steps = [(k, v) for k, v in protocol.items() if k.startswith("step_")]
        steps.sort()  # Ensure order

        for step_key, step_data in steps:
            if isinstance(step_data, dict):
                action = step_data.get("action", "")
                method = step_data.get("method", "")

                step_num = step_key.replace("step_", "").replace("_", " ").upper()
                parts.append(f"STEP {step_num}: {action}")

                if method:
                    parts.append("Method:")
                    for line in method.strip().split("\n"):
                        parts.append(f"  {line}")

                parts.append("")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # FOOTER
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    parts.append("=" * 80)
    parts.append(f"🎯 {name.upper()} ACTIVATED")
    parts.append("=" * 80)
    parts.append("")
    parts.append("⚠️  CRITICAL INSTRUCTION:")
    parts.append("Apply this mental model to the task below. Think deeply, question assumptions,")
    parts.append("and provide reasoning that reflects this mindset. Do not just execute.")
    parts.append("THINK. Then execute with understanding.")
    parts.append("")
    parts.append("=" * 80)
    parts.append("")

    return "\n".join(parts)


def list_available_lenses() -> list[str]:
    """
    List all available lens IDs.

    Returns:
        List of lens IDs (e.g., ["first_principles", "systems_thinking"])
    """
    repo_root = Path(__file__).parent.parent.parent.parent
    lenses_dir = repo_root / "agency_os" / "core_system" / "knowledge" / "lenses"

    if not lenses_dir.exists():
        return []

    lens_files = lenses_dir.glob("*.yaml")
    return [f.stem for f in lens_files]


def get_lens_metadata(lens_id: str) -> dict | None:
    """
    Get lens metadata without loading full prompt.

    Args:
        lens_id: The lens identifier

    Returns:
        Dictionary with lens metadata (name, description, tags, etc.)
        or None if lens not found
    """
    repo_root = Path(__file__).parent.parent.parent.parent
    lens_path = repo_root / "agency_os" / "core_system" / "knowledge" / "lenses" / f"{lens_id}.yaml"

    if not lens_path.exists():
        return None

    try:
        with open(lens_path) as f:
            lens_data = yaml.safe_load(f)

        if "lens" not in lens_data:
            return None

        lens = lens_data["lens"]

        return {
            "id": lens.get("id", lens_id),
            "name": lens.get("name", lens_id),
            "description": lens.get("description", ""),
            "category": lens.get("category", "unknown"),
            "tags": lens.get("metadata", {}).get("tags", []),
            "version": lens.get("metadata", {}).get("version", "1.0.0"),
            "status": lens.get("metadata", {}).get("status", "unknown"),
        }
    except Exception:
        return None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CLI UTILITIES (For Testing)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


if __name__ == "__main__":
    """Test lens loader from command line."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python lens_loader.py <lens_id>")
        print("\nAvailable lenses:")
        for lens_id in list_available_lenses():
            metadata = get_lens_metadata(lens_id)
            if metadata:
                print(f"  • {lens_id}: {metadata['name']}")
        sys.exit(1)

    lens_id = sys.argv[1]

    try:
        prompt = load_lens(lens_id)
        print(prompt)
    except LensLoadError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
