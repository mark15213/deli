"""
ToolOperator — generic wrapper that loads metadata from a YAML manifest
and delegates execution to a plain async handler function.

Also provides ``load_tool_operators()`` to scan the manifests/ directory
and register every tool it finds.
"""

from __future__ import annotations

import importlib
import logging
from pathlib import Path
from typing import Any, Callable, Awaitable

import yaml

from app.operators.base import OperatorBase, Port, PortType, RunContext
from app.operators.registry import register_operator

logger = logging.getLogger(__name__)

MANIFESTS_DIR = Path(__file__).parent / "manifests"

HandlerFn = Callable[[dict[str, Any], RunContext], Awaitable[dict[str, Any]]]


class ToolOperator(OperatorBase):
    """
    A tool operator whose metadata comes from a YAML manifest
    and whose logic lives in a handler function.
    """

    kind = "tool"

    def __init__(self, manifest: dict, handler_fn: HandlerFn):
        self.key = manifest["key"]
        self.name = manifest["name"]
        self.description = manifest.get("description", "")
        self.input_ports = [
            Port(key=p["key"], type=PortType(p["type"]), description=p.get("description", ""), required=p.get("required", True))
            for p in manifest.get("input_ports", [])
        ]
        self.output_ports = [
            Port(key=p["key"], type=PortType(p["type"]), description=p.get("description", ""))
            for p in manifest.get("output_ports", [])
        ]
        self._handler = handler_fn

    async def execute(self, inputs: dict[str, Any], context: RunContext) -> dict[str, Any]:
        self.validate_inputs(inputs)
        return await self._handler(inputs, context)


def _import_handler(dotted_path: str) -> HandlerFn:
    """
    Import a handler function from a dotted module path.
    E.g. ``"app.operators.tool.handlers.pdf_fetch"`` → module.handle
    """
    module = importlib.import_module(dotted_path)
    fn = getattr(module, "handle", None)
    if fn is None:
        raise ImportError(f"Handler module '{dotted_path}' has no 'handle' function")
    return fn


def load_tool_operators() -> list[ToolOperator]:
    """
    Scan ``manifests/`` for YAML files, pair each with its handler,
    and register the resulting ToolOperator in the global registry.
    """
    operators: list[ToolOperator] = []

    if not MANIFESTS_DIR.exists():
        logger.warning("Tool manifests directory not found: %s", MANIFESTS_DIR)
        return operators

    for yaml_path in sorted(MANIFESTS_DIR.glob("*.yaml")):
        try:
            manifest = yaml.safe_load(yaml_path.read_text())
            handler_fn = _import_handler(manifest["handler"])
            op = ToolOperator(manifest, handler_fn)

            # Register in the global registry so the engine can look it up by key
            from app.operators.registry import _REGISTRY
            _REGISTRY[op.key] = type(
                f"_Tool_{op.key}",
                (ToolOperator,),
                {"key": op.key, "__init_args": (manifest, handler_fn)},
            )
            # Patch __init__ so get_operator() can instantiate it
            _REGISTRY[op.key].__init__ = lambda self, m=manifest, h=handler_fn: ToolOperator.__init__(self, m, h)

            operators.append(op)
            logger.info("Registered tool operator: %s", op.key)
        except Exception:
            logger.exception("Failed to load tool manifest %s", yaml_path)

    return operators
