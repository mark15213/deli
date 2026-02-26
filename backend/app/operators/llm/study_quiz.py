"""study_quiz operator — flashcard generation."""

from typing import Any

from app.operators.base import Port, PortType
from app.operators.registry import register_operator
from app.operators.llm import LLMOperator


@register_operator
class StudyQuizOperator(LLMOperator):
    key = "study_quiz"
    name = "Flashcard Generator"
    description = "Generates quiz questions and glossary terms for active recall."
    prompt_file = "study_quiz"
    output_schema = {
        "type": "object",
        "properties": {
            "flashcards": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "question": {"type": "string"},
                        "answer": {"type": "string"},
                    },
                    "required": ["question", "answer"],
                },
            },
        },
        "required": ["flashcards"],
    }

    input_ports = [
        Port(key="text", type=PortType.TEXT, description="Paper full text"),
    ]
    output_ports = [
        Port(key="flashcards", type=PortType.JSON, description="List of {question, answer} flashcards"),
    ]

    def _map_output(self, content: Any) -> dict[str, Any]:
        if isinstance(content, dict) and "flashcards" in content:
            return {"flashcards": content["flashcards"]}
        return {"flashcards": content}
