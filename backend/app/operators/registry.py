"""
Operator registry — decorator-based auto-registration + lookup.
"""

from __future__ import annotations

import logging
from typing import Type

from app.operators.base import OperatorBase

logger = logging.getLogger(__name__)

_REGISTRY: dict[str, Type[OperatorBase]] = {}


def register_operator(cls: Type[OperatorBase]) -> Type[OperatorBase]:
    """Class decorator that registers an operator by its ``key``."""
    key = cls.key
    if key in _REGISTRY:
        logger.warning("Operator key '%s' registered twice — overwriting", key)
    _REGISTRY[key] = cls
    return cls


def get_operator(key: str) -> OperatorBase:
    """Instantiate and return an operator by key.  Raises ``KeyError`` if unknown."""
    if key not in _REGISTRY:
        raise KeyError(f"Unknown operator key: '{key}'")
    return _REGISTRY[key]()


def get_all_operators() -> list[OperatorBase]:
    """Return instances of every registered operator."""
    return [cls() for cls in _REGISTRY.values()]


def get_all_manifests() -> list[dict]:
    """Return manifests for every registered operator (for the frontend palette)."""
    return [cls().get_manifest() for cls in _REGISTRY.values()]
