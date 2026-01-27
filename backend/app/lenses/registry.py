from app.core.lens import Lens

def get_default_summary_lens() -> Lens:
    """
    Returns the default Summarization Lens.
    """
    return Lens(
        key="default_summary",
        name="TL;DR Summary",
        description="Generates a concise summary of the paper.",
        system_prompt=(
            "You are an expert research assistant. Your task is to provide a concise 'TL;DR' summary of the provided research paper text. "
            "Focus on the core problem, the proposed solution/method, and the key results. "
            "Format the output as Markdown."
        ),
        user_prompt_template="Here is the text of the paper:\n\n{text}\n\nPlease provide the summary."
    )

def get_profiler_lens() -> Lens:
    """
    Returns the Meta-Lens that suggests other lenses.
    """
    return Lens(
        key="profiler_meta",
        name="Content Profiler",
        description="Analyzes the text to suggest relevant lenses.",
        system_prompt=(
            "You are an intelligent system that analyzes research papers to recommend specific 'Lenses' for further analysis. "
            "A 'Lens' is a specific way to view or process the paper (e.g., 'Math Explainer' for heavy formulas, 'Code Refactoring' for algorithms, 'Historical Context' for surveys). "
            "Analyze the provided text and suggest 3 specific Lenses that would be most useful for this particular paper. "
            "Output strictly valid JSON as a list of objects with keys: 'key', 'name', 'description', 'reason'."
        ),
        user_prompt_template="Analyze this paper context and suggest lenses:\n\n{text}",
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

def get_lens_by_key(key: str) -> Lens:
    """
    Factory to retrieve a lens by key.
    """
    if key == "default_summary":
        return get_default_summary_lens()
    elif key == "profiler_meta":
        return get_profiler_lens()
    
    # Dynamic/Generic fallback or other hardcoded lenses
    # For now, return a generic one or raise error
    raise ValueError(f"Lens key '{key}' not found.")
