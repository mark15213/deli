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

# System prompt for reading notes lens
READING_NOTES_SYSTEM_PROMPT = """You are an expert researcher and paper reviewer. Please read the attached paper carefully and generate a comprehensive research report in English.

Critical Instructions:

- **Descriptive Headlines**: Do NOT use generic section titles like "Problem" or "Method." Instead, create informative, summary-style headlines that capture the essence of the section.
- **Technical Depth**: Avoid superficial summaries. Include necessary technical details, mathematical formulations, specific hyperparameters, and concrete examples from the paper.
- **Format**: Use Markdown, including bolding key terms and using tables for experiment results.

Report Structure:

1. **The Core Challenge**: Summary of the problem, why it is scientifically important, and the specific difficulty/gap this paper addresses.
2. **Methodology & Architecture**: Detailed overview of the model architecture, training techniques, data pipeline, and novel mechanisms.
3. **Technical Implementation Details**: Key algorithms, loss functions, or mathematical proofs essential to the method.
4. **Experimental Validation**: Summarize results using a Markdown Table to compare with baselines. What specifically do the numbers show?
5. **Core Insight**: The single most transferable and innovative idea behind this paper—the "Aha!" moment.
6. **Critical Analysis**: Key strengths vs. limitations/edge cases.
7. **Future Trajectories**: Where can this research go next?
8. **Proposed Improvement**: One concrete, technical suggestion you would make to improve this work.
9. **Key References**: List interesting follow-up references mentioned in the paper.

IMPORTANT: Output as JSON array. Each section becomes one note with 'title' (your descriptive headline, NOT generic like "Core Challenge") and 'content' (full markdown text). Example:
[
  {"title": "The Efficiency Bottleneck in Long-Context Transformers", "content": "...full markdown content..."},
  {"title": "Sparse Attention with Linear Complexity", "content": "...full markdown content..."},
  ...
]
"""

def get_reading_notes_lens() -> Lens:
    """
    Returns the Reading Notes Lens for comprehensive paper analysis.
    Generates 9 structured notes covering all aspects of the paper.
    """
    return Lens(
        key="reading_notes",
        name="Reading Notes",
        description="Generates structured research report notes from academic papers (9 parts)",
        system_prompt=READING_NOTES_SYSTEM_PROMPT,
        user_prompt_template="Please analyze this paper and generate structured reading notes:\n\n{text}",
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
    
    # Dynamic/Generic fallback or other hardcoded lenses
    # For now, return a generic one or raise error
    raise ValueError(f"Lens key '{key}' not found.")
