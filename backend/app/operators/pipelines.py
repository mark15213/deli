"""
Built-in pipeline templates.

Each function returns a Pipeline instance that can be executed by PipelineEngine.
"""

from __future__ import annotations

from app.operators.engine import Pipeline, Edge, Step, OpRef


def paper_default() -> Pipeline:
    """
    Default paper-processing pipeline.

    Steps:
      fetch          → pdf_fetch
      summarize      → summary → save_summary
      reading_notes  → reading_notes → save_reading_notes
      flashcards     → study_quiz → save_flashcards
      figures        → extract_figures → figure_association → apply_figure_associations
    """
    steps = [
        Step(
            key="fetch", label="Fetch PDF",
            position={"x": 0, "y": 250},
            operators=[
                OpRef(id="pdf_fetch", operator_key="pdf_fetch"),
            ],
        ),
        Step(
            key="summarize", label="Generate Summary",
            position={"x": 300, "y": 0},
            operators=[
                OpRef(id="summary", operator_key="summary"),
                OpRef(id="save_summary", operator_key="save_summary"),
            ],
        ),
        Step(
            key="reading_notes", label="Reading Notes",
            position={"x": 300, "y": 180},
            operators=[
                OpRef(id="reading_notes", operator_key="reading_notes"),
                OpRef(
                    id="save_reading_notes", operator_key="save_cards",
                    config_overrides={"card_type": "reading_note"},
                ),
            ],
        ),
        Step(
            key="flashcards", label="Flashcards",
            position={"x": 300, "y": 360},
            operators=[
                OpRef(id="study_quiz", operator_key="study_quiz"),
                OpRef(
                    id="save_flashcards", operator_key="save_cards",
                    config_overrides={"card_type": "flashcard"},
                ),
            ],
        ),
        Step(
            key="figures", label="Figure Extraction & Association",
            position={"x": 300, "y": 540},
            operators=[
                OpRef(id="extract_figures", operator_key="extract_figures"),
                OpRef(id="figure_association", operator_key="figure_association"),
                OpRef(id="apply_figure_associations", operator_key="apply_figure_associations"),
            ],
        ),
    ]

    edges = [
        # fetch → __input__
        Edge(id="e0", source_op="__input__", source_port="url", target_op="pdf_fetch", target_port="url"),
        # fetch → text consumers
        Edge(id="e1", source_op="pdf_fetch", source_port="text", target_op="summary", target_port="text"),
        Edge(id="e2", source_op="pdf_fetch", source_port="text", target_op="reading_notes", target_port="text"),
        Edge(id="e3", source_op="pdf_fetch", source_port="text", target_op="study_quiz", target_port="text"),
        # fetch → extract_figures
        Edge(id="e4", source_op="pdf_fetch", source_port="pdf_bytes", target_op="extract_figures", target_port="pdf_bytes"),
        Edge(id="e4b", source_op="__input__", source_port="url", target_op="extract_figures", target_port="url"),
        # extract_figures → figure_association
        Edge(id="e5", source_op="extract_figures", source_port="images", target_op="figure_association", target_port="images"),
        # reading notes -> figure_association
        Edge(id="e7", source_op="reading_notes", source_port="notes", target_op="figure_association", target_port="notes"),
        # summary → save_summary
        Edge(id="e8", source_op="summary", source_port="summary", target_op="save_summary", target_port="summary"),
        # reading_notes → save_reading_notes
        Edge(id="e9", source_op="reading_notes", source_port="notes", target_op="save_reading_notes", target_port="items"),
        # study_quiz → save_flashcards
        Edge(id="e10", source_op="study_quiz", source_port="flashcards", target_op="save_flashcards", target_port="items"),
        # figure_association → apply_figure_associations
        Edge(id="e11", source_op="figure_association", source_port="associations", target_op="apply_figure_associations", target_port="associations"),
        Edge(id="e12", source_op="extract_figures", source_port="saved_paths", target_op="apply_figure_associations", target_port="saved_paths"),
    ]

    return Pipeline(
        id="paper_default",
        name="Paper Processing (Default)",
        description="Fetch PDF → summary + reading notes + quiz + figure association",
        steps=steps,
        edges=edges,
    )
