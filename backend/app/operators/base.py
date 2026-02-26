"""
OperatorBase, Port, PortType, RunContext — core abstractions for the operator framework.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel


class PortType(str, Enum):
    """Data types that can flow between operator ports."""
    TEXT = "text"            # str
    JSON = "json"            # dict | list
    IMAGES = "images"        # list[bytes]
    PDF_BYTES = "pdf_bytes"  # bytes
    CARDS = "cards"          # list[dict]  (card-shaped dicts)


class Port(BaseModel):
    """Typed input or output slot on an operator."""
    key: str
    type: PortType
    description: str = ""
    required: bool = True


class RunContext(BaseModel):
    """Execution context threaded through every operator call."""
    model_config = {"arbitrary_types_allowed": True}

    db: Any                              # AsyncSession — kept as Any to avoid import cycle
    source_id: str
    user_id: str
    source_material_id: Optional[str] = None

    # Populated by the engine so operators can write SourceLog rows
    log_event: Any = None                # async callable(event_type, status, lens_key, message, duration_ms, extra_data)


class OperatorBase(ABC):
    """
    Abstract base for all operators (LLM and Tool).

    Subclasses must set the class-level attributes and implement ``execute``.
    """
    key: str
    name: str
    kind: str                            # "llm" | "tool"
    description: str = ""
    input_ports: list[Port] = []
    output_ports: list[Port] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @abstractmethod
    async def execute(
        self,
        inputs: dict[str, Any],
        context: RunContext,
    ) -> dict[str, Any]:
        """
        Run the operator.

        Parameters
        ----------
        inputs : mapping of port-key → value gathered from upstream edges.
        context : shared execution context (db session, ids, logger helper).

        Returns
        -------
        mapping of port-key → value to be forwarded downstream.
        """
        ...

    def validate_inputs(self, inputs: dict[str, Any]) -> None:
        """Raise ``ValueError`` if any required input port is missing."""
        for port in self.input_ports:
            if port.required and port.key not in inputs:
                raise ValueError(
                    f"Operator '{self.key}': missing required input port '{port.key}'"
                )

    def get_manifest(self) -> dict:
        """Return a JSON-serialisable description for the frontend node palette."""
        return {
            "key": self.key,
            "name": self.name,
            "kind": self.kind,
            "description": self.description,
            "input_ports": [p.model_dump() for p in self.input_ports],
            "output_ports": [p.model_dump() for p in self.output_ports],
        }
