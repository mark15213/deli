"""
Operator framework for pipeline-based content processing.

Operators are typed processing units with declared input/output ports.
Two kinds: LLM operators (prompt-driven) and Tool operators (code logic).

Architecture: Pipeline → Step → OpRef → Operator

Importing this package auto-registers every built-in operator so that
``registry.get_operator(key)`` works without manual setup.
"""

from app.operators.base import OperatorBase, Port, PortType, RunContext
from app.operators.engine import Pipeline, Edge, Step, OpRef, PipelineEngine

# -- Auto-register LLM operators (decorated with @register_operator) ------
import app.operators.llm.summary  # noqa: F401
import app.operators.llm.reading_notes  # noqa: F401
import app.operators.llm.study_quiz  # noqa: F401
import app.operators.llm.figure_association  # noqa: F401

# -- Auto-register Tool operators (YAML manifest scan) --------------------
from app.operators.tool.loader import load_tool_operators as _load_tools

_load_tools()

__all__ = [
    "OperatorBase",
    "Port",
    "PortType",
    "RunContext",
    "Pipeline",
    "Step",
    "OpRef",
    "Edge",
    "PipelineEngine",
]
