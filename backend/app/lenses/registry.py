import yaml
from pathlib import Path
from app.core.lens import Lens

PROMPTS_DIR = Path(__file__).parent / "prompts"

def load_prompt_config(lens_key: str) -> dict:
    """
    Load prompt configuration for a lens from a YAML file.
    """
    prompt_file = PROMPTS_DIR / f"{lens_key}.yaml"
    if not prompt_file.exists():
        raise FileNotFoundError(f"Prompt configuration file not found: {prompt_file}")
    
    with open(prompt_file, "r") as f:
        return yaml.safe_load(f)

def get_default_summary_lens() -> Lens:
    """
    Returns the default Summarization Lens.
    """
    config = load_prompt_config("default_summary")
    return Lens(
        key="default_summary",
        name="TL;DR Summary",
        description="Generates a concise summary of the paper.",
        system_prompt=config["system_prompt"],
        user_prompt_template=config["user_prompt_template"]
    )

def get_profiler_lens() -> Lens:
    """
    Returns the Meta-Lens that suggests other lenses.
    """
    config = load_prompt_config("profiler_meta")
    return Lens(
        key="profiler_meta",
        name="Content Profiler",
        description="Analyzes the text to suggest relevant lenses.",
        system_prompt=config["system_prompt"],
        user_prompt_template=config["user_prompt_template"],
        output_schema={
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "key": {"type": "string"},
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "reason": {"type": "string"}
                }
            }
        }
    )

def get_reading_notes_lens() -> Lens:
    """
    Returns the Reading Notes Lens for comprehensive paper analysis.
    Generates 9 structured notes covering all aspects of the paper.
    """
    config = load_prompt_config("reading_notes")
    return Lens(
        key="reading_notes",
        name="Reading Notes",
        description="Generates structured research report notes from academic papers (9 parts)",
        system_prompt=config["system_prompt"],
        user_prompt_template=config["user_prompt_template"],
        output_schema={
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Descriptive headline for this section"},
                    "content": {"type": "string", "description": "Full markdown content with technical depth"}
                },
                "required": ["title", "content"]
            },
            "minItems": 9,
            "maxItems": 9
        }
    )

def get_study_quiz_lens() -> Lens:
    """
    Returns the Study Quiz Lens.
    Generates flashcards (quiz + glossary).
    """
    config = load_prompt_config("study_quiz")
    return Lens(
        key="study_quiz",
        name="Flashcard Generator",
        description="Generates quiz questions and glossary terms for active recall.",
        system_prompt=config["system_prompt"],
        user_prompt_template=config["user_prompt_template"],
        output_schema={
            "type": "object",
            "properties": {
                "flashcards": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "question": {"type": "string"},
                            "answer": {"type": "string"}
                        },
                        "required": ["question", "answer"]
                    }
                }
            },
            "required": ["flashcards"]
        }
    )

def get_lens_by_key(key: str) -> Lens:
    """
    Factory to retrieve a lens by key.
    """
    if key == "default_summary":
        return get_default_summary_lens()
    elif key == "profiler_meta":
        return get_profiler_lens()
    elif key == "reading_notes":
        return get_reading_notes_lens()
    elif key == "study_quiz":
        return get_study_quiz_lens()
    
    # Dynamic/Generic fallback or other hardcoded lenses
    # For now, return a generic one or raise error
    raise ValueError(f"Lens key '{key}' not found.")
