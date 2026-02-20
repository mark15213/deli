"""
Prompt configuration loader.

Reads YAML prompt files from the ``lenses/prompts/`` directory.
Used by ``LLMOperator`` to build system/user messages.
"""

import yaml
from pathlib import Path

PROMPTS_DIR = Path(__file__).parent / "prompts"


def load_prompt_config(lens_key: str) -> dict:
    """
    Load prompt configuration for an operator from a YAML file.
    """
    prompt_file = PROMPTS_DIR / f"{lens_key}.yaml"
    if not prompt_file.exists():
        raise FileNotFoundError(f"Prompt configuration file not found: {prompt_file}")

    with open(prompt_file, "r") as f:
        return yaml.safe_load(f)
