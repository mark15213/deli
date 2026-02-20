"""
PipelineEngine — DAG executor with topological-level parallelism and Step-level lifecycle.

Architecture: Pipeline → Step → OpRef → Operator

- Operator: reusable atomic processing unit (defined in registry)
- OpRef:    a specific usage of an Operator in a Pipeline (with config overrides)
- Step:     a business-meaningful task composed of one or more OpRefs
            (logged, evaluated, retried as a unit)
- Pipeline: the complete DAG workflow

The engine:
1. Flattens Steps into an operator-level DAG
2. Computes topological levels (Kahn's algorithm)
3. Executes each level in parallel via asyncio.gather
4. Tracks Step lifecycle: started → completed / failed
5. Writes SourceLog entries at both operator and Step level
6. Supports smart-skip: already-completed Steps are skipped on retry
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import select

from app.operators.base import RunContext
from app.operators.registry import get_operator

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Pipeline data model
# ---------------------------------------------------------------------------

class OpRef(BaseModel):
    """An Operator instance within a Step."""
    id: str                                   # unique ID in the pipeline, e.g. "summary"
    operator_key: str                         # which Operator to run, e.g. "summary"
    config_overrides: dict[str, Any] = {}


class Step(BaseModel):
    """Business-meaningful task composed of ordered Operators."""
    key: str                                  # e.g. "summarize"
    label: str = ""                           # e.g. "Generate Summary"
    operators: list[OpRef] = []
    position: dict[str, float] = {"x": 0, "y": 0}


class Edge(BaseModel):
    """Data flow between operators (intra-step or cross-step)."""
    id: str
    source_op: str                            # OpRef.id
    source_port: str
    target_op: str                            # OpRef.id
    target_port: str


class Pipeline(BaseModel):
    id: str = ""
    name: str = ""
    description: str = ""
    steps: list[Step] = []
    edges: list[Edge] = []


# ---------------------------------------------------------------------------
# Sentinel for skipped operators
# ---------------------------------------------------------------------------

_SKIPPED = object()


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

class PipelineEngine:
    """Execute a Pipeline DAG with level-parallel scheduling and Step lifecycle."""

    async def run(
        self,
        pipeline: Pipeline,
        initial_inputs: dict[str, Any],
        context: RunContext,
    ) -> dict[str, dict[str, Any]]:
        """
        Run the full pipeline.

        Parameters
        ----------
        pipeline : the DAG definition.
        initial_inputs : keyed by port_key, injected into operators whose
            incoming edges reference ``__input__`` as the source.
        context : shared execution context.

        Returns
        -------
        Mapping of ``op_id → {port_key: value}`` for every executed operator.
        """
        # Build lookup tables
        op_map, op_to_step = self._build_op_map(pipeline)
        step_map = {s.key: s for s in pipeline.steps}
        levels = self._topological_levels(pipeline)

        # Track outputs and failures
        op_outputs: dict[str, dict[str, Any]] = {"__input__": initial_inputs}
        failed_ops: set[str] = set()

        # Track Step lifecycle
        step_started: set[str] = set()
        step_completed: set[str] = set()
        step_failed: set[str] = set()

        for level_idx, level_op_ids in enumerate(levels):
            logger.info(
                "Pipeline '%s' — executing level %d: %s",
                pipeline.name, level_idx, level_op_ids,
            )

            tasks = []
            op_ids_in_level: list[str] = []

            for op_id in level_op_ids:
                op_ref = op_map[op_id]
                step_key = op_to_step[op_id]

                # Skip if upstream failed
                upstream_ids = self._get_upstream_ops(op_id, pipeline.edges)
                if upstream_ids & failed_ops:
                    logger.warning(
                        "⏭ Op '%s' skipped — upstream op(s) failed: %s",
                        op_id, upstream_ids & failed_ops,
                    )
                    failed_ops.add(op_id)

                    # If this failure causes the whole step to fail
                    if step_key not in step_failed:
                        step_failed.add(step_key)
                        await self._log_step_event(
                            context, step_key, "step_failed", "failed",
                            message=f"Step failed: upstream operator(s) failed",
                        )

                    async def _skip():
                        return _SKIPPED
                    tasks.append(_skip())
                    op_ids_in_level.append(op_id)
                    continue

                # Smart-skip: if entire Step is already completed
                if step_key not in step_started and await self._is_step_completed(context, step_key):
                    logger.info(
                        "⏭ Step '%s' already completed, skipping all its operators",
                        step_key,
                    )
                    step_completed.add(step_key)
                    step_started.add(step_key)
                    # Mark all operators in this step as skipped
                    for op in step_map[step_key].operators:
                        op_outputs[op.id] = {}

                    async def _skip():
                        return _SKIPPED
                    tasks.append(_skip())
                    op_ids_in_level.append(op_id)
                    continue

                # Skip individual op if its Step was already marked as skipped above
                if step_key in step_completed:
                    async def _skip():
                        return _SKIPPED
                    tasks.append(_skip())
                    op_ids_in_level.append(op_id)
                    continue

                # Log Step started (first time we see an op from this Step)
                if step_key not in step_started:
                    step_started.add(step_key)
                    input_snapshot = self._gather_inputs(op_id, pipeline.edges, op_outputs)
                    await self._log_step_event(
                        context, step_key, "step_started", "running",
                        message=f"Starting step: {step_map[step_key].label}",
                        extra_data={"input_keys": list(input_snapshot.keys())},
                    )
                    await context.db.commit()

                inputs = self._gather_inputs(op_id, pipeline.edges, op_outputs)
                tasks.append(self._run_op(op_ref, inputs, context, step_key))
                op_ids_in_level.append(op_id)

            results = await asyncio.gather(*tasks, return_exceptions=True)

            for op_id, result in zip(op_ids_in_level, results):
                if result is _SKIPPED:
                    continue

                step_key = op_to_step[op_id]

                if isinstance(result, BaseException):
                    logger.error(
                        "Op '%s' (operator=%s) failed: %s",
                        op_id, op_map[op_id].operator_key, result,
                    )
                    failed_ops.add(op_id)

                    # Log operator failure
                    await self._log_event(
                        context, "operator_failed", "failed",
                        lens_key=op_id,
                        step_key=step_key,
                        message=str(result),
                    )

                    # Mark Step as failed
                    if step_key not in step_failed:
                        step_failed.add(step_key)
                        await self._log_step_event(
                            context, step_key, "step_failed", "failed",
                            message=f"Step failed at operator '{op_id}': {result}",
                        )
                    continue

                op_outputs[op_id] = result

                # Check if this was the last operator in the Step
                step = step_map[step_key]
                if op_id == step.operators[-1].id and step_key not in step_failed:
                    step_completed.add(step_key)
                    await self._log_step_event(
                        context, step_key, "step_completed", "completed",
                        message=f"Step completed: {step.label}",
                        extra_data={"output_keys": list(result.keys())},
                    )
                    await context.db.commit()

        if failed_ops:
            logger.warning(
                "Pipeline '%s' completed with %d failed op(s): %s",
                pipeline.name, len(failed_ops), failed_ops,
            )

        return op_outputs

    # ------------------------------------------------------------------
    # Build lookup maps
    # ------------------------------------------------------------------

    @staticmethod
    def _build_op_map(pipeline: Pipeline) -> tuple[dict[str, OpRef], dict[str, str]]:
        """
        Returns:
            op_map:     op_id → OpRef
            op_to_step: op_id → step_key
        """
        op_map: dict[str, OpRef] = {}
        op_to_step: dict[str, str] = {}
        for step in pipeline.steps:
            for op in step.operators:
                op_map[op.id] = op
                op_to_step[op.id] = step.key
        return op_map, op_to_step

    # ------------------------------------------------------------------
    # Topological sort → levels (operates on flattened op IDs)
    # ------------------------------------------------------------------

    @staticmethod
    def _topological_levels(pipeline: Pipeline) -> list[list[str]]:
        """
        Kahn's algorithm variant that groups op IDs into levels.
        Operators in the same level have no mutual dependencies and can run in parallel.
        """
        # Collect all op IDs
        all_op_ids: list[str] = []
        for step in pipeline.steps:
            for op in step.operators:
                all_op_ids.append(op.id)

        # Build adjacency + in-degree
        dependents: dict[str, set[str]] = {oid: set() for oid in all_op_ids}
        in_degree: dict[str, int] = {oid: 0 for oid in all_op_ids}

        pair_seen: set[tuple[str, str]] = set()
        for edge in pipeline.edges:
            if edge.source_op == "__input__":
                continue
            pair = (edge.source_op, edge.target_op)
            if pair not in pair_seen:
                pair_seen.add(pair)
                in_degree[edge.target_op] += 1
                dependents[edge.source_op].add(edge.target_op)

        levels: list[list[str]] = []
        queue = [oid for oid, deg in in_degree.items() if deg == 0]

        while queue:
            levels.append(queue)
            next_queue: list[str] = []
            for oid in queue:
                for dep in dependents[oid]:
                    in_degree[dep] -= 1
                    if in_degree[dep] == 0:
                        next_queue.append(dep)
            queue = next_queue

        executed = sum(len(lv) for lv in levels)
        if executed != len(all_op_ids):
            raise ValueError(
                f"Pipeline has a cycle — only {executed}/{len(all_op_ids)} operators reachable"
            )

        return levels

    # ------------------------------------------------------------------
    # Input gathering
    # ------------------------------------------------------------------

    @staticmethod
    def _gather_inputs(
        op_id: str,
        edges: list[Edge],
        op_outputs: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        """Collect inputs for an operator by following incoming edges."""
        inputs: dict[str, Any] = {}
        for edge in edges:
            if edge.target_op != op_id:
                continue
            source_data = op_outputs.get(edge.source_op, {})
            if edge.source_port in source_data:
                inputs[edge.target_port] = source_data[edge.source_port]
        return inputs

    # ------------------------------------------------------------------
    # Upstream dependency lookup
    # ------------------------------------------------------------------

    @staticmethod
    def _get_upstream_ops(op_id: str, edges: list[Edge]) -> set[str]:
        """Return set of op IDs that feed into this operator."""
        return {
            e.source_op
            for e in edges
            if e.target_op == op_id and e.source_op != "__input__"
        }

    # ------------------------------------------------------------------
    # Single operator execution
    # ------------------------------------------------------------------

    async def _run_op(
        self,
        op_ref: OpRef,
        inputs: dict[str, Any],
        context: RunContext,
        step_key: str,
    ) -> dict[str, Any]:
        from app.core.database import async_session_maker
        
        async with async_session_maker() as op_session:
            # Create isolated context for this operator execution
            local_context = context.model_copy()
            local_context.db = op_session
            
            operator = get_operator(op_ref.operator_key)

            # Merge static config_overrides into inputs (lower priority than edge data)
            merged_inputs = {**op_ref.config_overrides, **inputs}

            # --- Smart-skip: check if this operator already completed --------
            if await self._is_operator_completed(local_context, op_ref.id):
                logger.info(
                    "⏭ Op '%s' — operator '%s' already completed, skipping",
                    op_ref.id, op_ref.operator_key,
                )
                return {}

            # --- Log start ---------------------------------------------------
            await self._log_event(
                local_context, "operator_started", "running",
                lens_key=op_ref.id,
                step_key=step_key,
                message=f"Starting operator {op_ref.operator_key}",
            )
            await local_context.db.commit()

            logger.info("▶ Op '%s' — operator '%s' starting", op_ref.id, op_ref.operator_key)
            start = time.time()

            try:
                result = await operator.execute(merged_inputs, local_context)
            except Exception as exc:
                elapsed_ms = int((time.time() - start) * 1000)
                logger.error(
                    "✗ Op '%s' — operator '%s' failed in %d ms: %s",
                    op_ref.id, op_ref.operator_key, elapsed_ms, exc,
                )
                await self._update_lens_log(
                    local_context, op_ref.id, "failed",
                    message=str(exc), duration_ms=elapsed_ms,
                )
                await local_context.db.commit()
                raise

            elapsed_ms = int((time.time() - start) * 1000)
            logger.info(
                "✓ Op '%s' — operator '%s' completed in %d ms",
                op_ref.id, op_ref.operator_key, elapsed_ms,
            )

            await self._update_lens_log(
                local_context, op_ref.id, "completed",
                message=f"Operator {op_ref.operator_key} completed",
                duration_ms=elapsed_ms,
            )
            await local_context.db.commit()

            return result

    # ------------------------------------------------------------------
    # SourceLog helpers
    # ------------------------------------------------------------------

    @staticmethod
    async def _is_operator_completed(context: RunContext, op_id: str) -> bool:
        """Check SourceLog for an existing completed entry for this operator."""
        from app.models.models import SourceLog
        from app.core.database import async_session_maker

        async with async_session_maker() as session:
            stmt = (
                select(SourceLog)
                .where(
                    SourceLog.source_id == UUID(context.source_id),
                    SourceLog.lens_key == op_id,
                    SourceLog.status == "completed",
                )
                .limit(1)
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none() is not None

    @staticmethod
    async def _is_step_completed(context: RunContext, step_key: str) -> bool:
        """Check SourceLog for a completed step_completed event."""
        from app.models.models import SourceLog
        from app.core.database import async_session_maker

        async with async_session_maker() as session:
            stmt = (
                select(SourceLog)
                .where(
                    SourceLog.source_id == UUID(context.source_id),
                    SourceLog.step_key == step_key,
                    SourceLog.event_type == "step_completed",
                    SourceLog.status == "completed",
                )
                .limit(1)
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none() is not None

    @staticmethod
    async def _log_event(
        context: RunContext,
        event_type: str,
        status: str,
        *,
        lens_key: str | None = None,
        step_key: str | None = None,
        message: str | None = None,
        duration_ms: int | None = None,
        extra_data: dict | None = None,
    ) -> None:
        """Write a new SourceLog row."""
        from app.models.models import SourceLog
        from app.core.database import async_session_maker

        async with async_session_maker() as session:
            log = SourceLog(
                source_id=UUID(context.source_id),
                event_type=event_type,
                status=status,
                lens_key=lens_key,
                step_key=step_key,
                message=message,
                duration_ms=duration_ms,
                extra_data=extra_data or {},
            )
            session.add(log)
            await session.commit()

    @staticmethod
    async def _log_step_event(
        context: RunContext,
        step_key: str,
        event_type: str,
        status: str,
        *,
        message: str | None = None,
        duration_ms: int | None = None,
        extra_data: dict | None = None,
    ) -> None:
        """Write or update a Step-level SourceLog row."""
        from app.models.models import SourceLog
        from app.core.database import async_session_maker
        from sqlalchemy import select

        async with async_session_maker() as session:
            stmt = (
                select(SourceLog)
                .where(
                    SourceLog.source_id == UUID(context.source_id),
                    SourceLog.step_key == step_key,
                    SourceLog.status == "running",
                )
                .order_by(SourceLog.created_at.desc())
                .limit(1)
            )
            result = await session.execute(stmt)
            log = result.scalar_one_or_none()

            if log:
                log.status = status
                log.event_type = event_type
                if message is not None:
                    log.message = message
                if duration_ms is not None:
                    log.duration_ms = duration_ms
                if extra_data is not None:
                    # Update dict keys if exists
                    log.extra_data = {**log.extra_data, **extra_data}
            else:
                log = SourceLog(
                    source_id=UUID(context.source_id),
                    event_type=event_type,
                    status=status,
                    step_key=step_key,
                    message=message,
                    duration_ms=duration_ms,
                    extra_data=extra_data or {},
                )
                session.add(log)
            await session.commit()

    @staticmethod
    async def _update_lens_log(
        context: RunContext,
        lens_key: str,
        status: str,
        *,
        message: str | None = None,
        duration_ms: int | None = None,
    ) -> None:
        """Update the most recent 'running' log for an operator, or create a new one."""
        from app.models.models import SourceLog
        from app.core.database import async_session_maker

        async with async_session_maker() as session:
            stmt = (
                select(SourceLog)
                .where(
                    SourceLog.source_id == UUID(context.source_id),
                    SourceLog.lens_key == lens_key,
                    SourceLog.status == "running",
                )
                .order_by(SourceLog.created_at.desc())
                .limit(1)
            )
            result = await session.execute(stmt)
            log = result.scalar_one_or_none()

            if log:
                log.status = status
                log.event_type = f"operator_{status}"
                if message is not None:
                    log.message = message
                if duration_ms is not None:
                    log.duration_ms = duration_ms
            else:
                new_log = SourceLog(
                    source_id=UUID(context.source_id),
                    event_type=f"operator_{status}",
                    status=status,
                    lens_key=lens_key,
                    message=message,
                    duration_ms=duration_ms,
                    extra_data={},
                )
                session.add(new_log)
            await session.commit()
