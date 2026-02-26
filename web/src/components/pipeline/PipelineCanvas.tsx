"use client";

/**
 * Core pipeline canvas — wraps ReactFlow with pipeline-specific logic:
 * - Loads pipeline definition and converts to Xyflow nodes/edges
 * - Handles drag-n-drop from OperatorPalette
 * - Manages connections, node selection, deletion
 * - Save button persists to API
 */

import React, { useCallback, useRef, useState, useEffect, useMemo } from "react";
import {
    ReactFlow,
    Background,
    Controls,
    MiniMap,
    addEdge,
    useNodesState,
    useEdgesState,
    type Node,
    type Edge,
    type Connection,
    type OnConnect,
    type ReactFlowInstance,
    BackgroundVariant,
    MarkerType,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

import { OperatorNode, type OperatorNodeData } from "./OperatorNode";
import { StepNode, type StepNodeData } from "./StepNode";
import { OperatorPalette } from "./OperatorPalette";
import { NodeConfigDrawer } from "./NodeConfigDrawer";
import {
    type PipelineTemplate,
    type StepDef,
    type OpRefDef,
    type EdgeDef,
    type OperatorManifest,
    updatePipeline,
    getOperators,
} from "@/lib/api/pipelines";
import { Save, Lock, Copy } from "lucide-react";
import { Button } from "@/components/ui/button";

// ─── Node type registry ──────────────────────────────────────────────
const nodeTypes = {
    operator: OperatorNode,
    step: StepNode,
};

const OP_WIDTH = 200;
const OP_HEIGHT = 100;
const OP_GAP = 20;
const PADDING = 40;

/**
 * Flatten steps into individual operator nodes within visual Step groups.
 */
function stepsToFlowNodes(
    steps: StepDef[],
    manifests: Map<string, OperatorManifest>
): Node[] {
    const flowNodes: Node[] = [];

    for (const step of steps) {
        // 1. Create the Step group node
        const opCount = step.operators.length;
        // Calculate dynamic width based on number of operators
        const width = Math.max(
            300,
            PADDING * 2 + opCount * OP_WIDTH + (opCount - 1) * OP_GAP
        );
        const height = PADDING * 2 + OP_HEIGHT + 30; // +30 for label/header

        const stepId = step.key;

        flowNodes.push({
            id: stepId,
            type: "step",
            position: step.position || { x: 0, y: 0 },
            style: { width, height },
            data: {
                label: step.label || step.key,
            } satisfies StepNodeData,
            draggable: true, // Allow moving the whole group
        });

        // 2. Create operator nodes as children
        for (let i = 0; i < step.operators.length; i++) {
            const op = step.operators[i];
            const manifest = manifests.get(op.operator_key);

            flowNodes.push({
                id: op.id,
                type: "operator",
                // Relative position to parent Step node
                position: {
                    x: PADDING + i * (OP_WIDTH + OP_GAP),
                    y: PADDING + 20
                },
                parentId: stepId,
                extent: "parent", // Constrain inside the step
                data: {
                    label: op.id,
                    operatorKey: op.operator_key,
                    kind: manifest?.kind || "tool",
                    inputPorts: manifest?.input_ports || [],
                    outputPorts: manifest?.output_ports || [],
                    configOverrides: op.config_overrides || {},
                    stepKey: step.key,
                } satisfies OperatorNodeData,
            });
        }
    }
    return flowNodes;
}

function apiEdgesToFlow(edges: EdgeDef[]): Edge[] {
    return edges
        .filter((e) => e.source_op !== "__input__")
        .map((e) => ({
            id: e.id,
            source: e.source_op,
            sourceHandle: e.source_port,
            target: e.target_op,
            targetHandle: e.target_port,
            markerEnd: { type: MarkerType.ArrowClosed, width: 16, height: 16 },
            style: { strokeWidth: 2 },
            label: e.source_port,
            labelStyle: { fontSize: 10, fill: "hsl(var(--muted-foreground))" },
            labelBgStyle: { fill: "hsl(var(--background))", fillOpacity: 0.8 },
        }));
}

/**
 * Convert canvas nodes back to StepDefs based on visual grouping (parentId).
 */
function flowToApiSteps(nodes: Node[]): StepDef[] {
    const steps: StepDef[] = [];

    // 1. Identify all Step group nodes
    const stepNodes = nodes.filter((n) => n.type === "step");
    const opNodes = nodes.filter((n) => n.type === "operator");

    // 2. Map operators by parentId
    const opsByParent = new Map<string, Node[]>();
    const orphans: Node[] = [];

    for (const op of opNodes) {
        if (op.parentId) {
            if (!opsByParent.has(op.parentId)) {
                opsByParent.set(op.parentId, []);
            }
            opsByParent.get(op.parentId)!.push(op);
        } else {
            orphans.push(op);
        }
    }

    // 3. Construct StepDefs from group nodes
    for (const sNode of stepNodes) {
        const childOps = opsByParent.get(sNode.id) || [];
        // Sort by X position to maintain logical order
        childOps.sort((a, b) => a.position.x - b.position.x);

        steps.push({
            key: sNode.id, // ID is the step key
            label: (sNode.data as unknown as StepNodeData).label || sNode.id,
            position: sNode.position,
            operators: childOps.map((op) => ({
                id: op.id,
                operator_key: (op.data as unknown as OperatorNodeData).operatorKey,
                config_overrides: (op.data as unknown as OperatorNodeData).configOverrides || {},
            })),
        });
    }

    // 4. Handle orphans (operators not in a step group)
    // We'll group them into a "custom" step or multiple if needed.
    // For simplicity, put all orphans in one "custom" step.
    if (orphans.length > 0) {
        orphans.sort((a, b) => a.position.x - b.position.x); // Sort by X (absolute or relative? if orphan, it's absolute)
        steps.push({
            key: "custom",
            label: "Custom Steps",
            position: { x: 0, y: 0 }, // Maybe calculate bounding box?
            operators: orphans.map((op) => ({
                id: op.id,
                operator_key: (op.data as unknown as OperatorNodeData).operatorKey,
                config_overrides: (op.data as unknown as OperatorNodeData).configOverrides || {},
            })),
        });
    }

    return steps;
}

function flowToApiEdges(edges: Edge[]): EdgeDef[] {
    return edges.map((e) => ({
        id: e.id,
        source_op: e.source,
        source_port: e.sourceHandle || "output",
        target_op: e.target,
        target_port: e.targetHandle || "input",
    }));
}

// ─── Component ───────────────────────────────────────────────────────

interface PipelineCanvasProps {
    pipeline: PipelineTemplate;
    onClone?: () => void;
}

export function PipelineCanvas({ pipeline, onClone }: PipelineCanvasProps) {
    const reactFlowWrapper = useRef<HTMLDivElement>(null);
    const [rfInstance, setRfInstance] = useState<ReactFlowInstance | null>(null);
    const [manifests, setManifests] = useState<Map<string, OperatorManifest>>(
        new Map()
    );
    const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);
    const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
    const [saving, setSaving] = useState(false);
    const [dirty, setDirty] = useState(false);

    const isReadOnly = pipeline.is_system;

    // Load operator manifests
    useEffect(() => {
        getOperators().then((ops) => {
            const m = new Map<string, OperatorManifest>();
            ops.forEach((o) => m.set(o.key, o));
            setManifests(m);
        });
    }, []);

    // Convert pipeline definition to Xyflow format once manifests load
    useEffect(() => {
        if (manifests.size === 0) return;
        const def = pipeline.definition;
        if (!def?.steps) return;
        setNodes(stepsToFlowNodes(def.steps, manifests));
        setEdges(apiEdgesToFlow(def.edges || []));
        setDirty(false);
    }, [pipeline, manifests, setNodes, setEdges]);

    // Fit view when nodes/edges first load
    useEffect(() => {
        if (rfInstance && nodes.length > 0) {
            setTimeout(() => rfInstance.fitView({ padding: 0.2 }), 100);
        }
    }, [rfInstance, nodes.length]);

    // Track dirty state
    const markDirty = useCallback(() => setDirty(true), []);

    const onConnect: OnConnect = useCallback(
        (params: Connection) => {
            if (isReadOnly) return;
            setEdges((eds) =>
                addEdge(
                    {
                        ...params,
                        id: `e-${Date.now()}`,
                        markerEnd: {
                            type: MarkerType.ArrowClosed,
                            width: 16,
                            height: 16,
                        },
                        style: { strokeWidth: 2 },
                    },
                    eds
                )
            );
            markDirty();
        },
        [isReadOnly, setEdges, markDirty]
    );

    // Handle node selection for config drawer
    const onNodeClick = useCallback((_: React.MouseEvent, node: Node) => {
        setSelectedNodeId(node.id);
    }, []);

    const onPaneClick = useCallback(() => {
        setSelectedNodeId(null);
    }, []);

    // Update node data from config drawer
    const handleNodeUpdate = useCallback(
        (nodeId: string, updates: Partial<OperatorNodeData>) => {
            setNodes((nds) =>
                nds.map((n) =>
                    n.id === nodeId
                        ? { ...n, data: { ...n.data, ...updates } }
                        : n
                )
            );
            markDirty();
        },
        [setNodes, markDirty]
    );

    // Drag & drop from palette
    const onDragOver = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        e.dataTransfer.dropEffect = "move";
    }, []);

    const onDrop = useCallback(
        (e: React.DragEvent) => {
            e.preventDefault();
            if (isReadOnly) return;

            const raw = e.dataTransfer.getData("application/pipeline-operator");
            if (!raw) return;

            const operator: OperatorManifest = JSON.parse(raw);
            if (!rfInstance || !reactFlowWrapper.current) return;

            const bounds = reactFlowWrapper.current.getBoundingClientRect();
            const position = rfInstance.screenToFlowPosition({
                x: e.clientX - bounds.left,
                y: e.clientY - bounds.top,
            });

            const newId = `${operator.key}_${Date.now().toString(36)}`;
            const newNode: Node = {
                id: newId,
                type: "operator",
                position,
                data: {
                    label: operator.name,
                    operatorKey: operator.key,
                    kind: operator.kind,
                    inputPorts: operator.input_ports,
                    outputPorts: operator.output_ports,
                    configOverrides: {},
                } satisfies OperatorNodeData,
            };

            setNodes((nds) => nds.concat(newNode));
            markDirty();
        },
        [isReadOnly, rfInstance, setNodes, markDirty]
    );

    // Delete selected node on Backspace/Delete
    const onKeyDown = useCallback(
        (e: React.KeyboardEvent) => {
            if (isReadOnly) return;
            if (e.key === "Backspace" || e.key === "Delete") {
                if (selectedNodeId) {
                    setNodes((nds) => nds.filter((n) => n.id !== selectedNodeId));
                    setEdges((eds) =>
                        eds.filter(
                            (ed) =>
                                ed.source !== selectedNodeId && ed.target !== selectedNodeId
                        )
                    );
                    setSelectedNodeId(null);
                    markDirty();
                }
            }
        },
        [isReadOnly, selectedNodeId, setNodes, setEdges, markDirty]
    );

    // Save handler
    const handleSave = useCallback(async () => {
        if (isReadOnly || !dirty) return;
        setSaving(true);
        try {
            await updatePipeline(pipeline.id, {
                definition: {
                    steps: flowToApiSteps(nodes),
                    edges: flowToApiEdges(edges),
                },
            });
            setDirty(false);
        } catch (err) {
            console.error("Save failed:", err);
        } finally {
            setSaving(false);
        }
    }, [isReadOnly, dirty, pipeline.id, nodes, edges]);

    // Selected node data for drawer
    const selectedNodeData = useMemo(() => {
        if (!selectedNodeId) return null;
        const node = nodes.find((n) => n.id === selectedNodeId);
        return node ? (node.data as OperatorNodeData) : null;
    }, [selectedNodeId, nodes]);

    return (
        <div className="flex h-full" onKeyDown={onKeyDown} tabIndex={0}>
            {/* Left: Operator Palette */}
            <OperatorPalette disabled={isReadOnly} />

            {/* Center: Canvas */}
            <div className="flex-1 flex flex-col relative">
                {/* Toolbar */}
                <div className="flex items-center justify-between px-4 py-2 border-b bg-card/80 backdrop-blur-sm z-10">
                    <div className="flex items-center gap-3">
                        <h2 className="font-semibold text-sm">{pipeline.name}</h2>
                        {isReadOnly && (
                            <span className="flex items-center gap-1 text-[10px] px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-500 border border-amber-500/20">
                                <Lock className="h-3 w-3" />
                                System (Read-Only)
                            </span>
                        )}
                        {dirty && (
                            <span className="text-[10px] px-2 py-0.5 rounded-full bg-orange-500/10 text-orange-500">
                                Unsaved Changes
                            </span>
                        )}
                    </div>
                    <div className="flex items-center gap-2">
                        {isReadOnly && onClone && (
                            <Button size="sm" variant="outline" onClick={onClone}>
                                <Copy className="h-3.5 w-3.5 mr-1.5" />
                                Clone to Edit
                            </Button>
                        )}
                        {!isReadOnly && (
                            <Button
                                size="sm"
                                onClick={handleSave}
                                disabled={!dirty || saving}
                            >
                                <Save className="h-3.5 w-3.5 mr-1.5" />
                                {saving ? "Saving…" : "Save"}
                            </Button>
                        )}
                    </div>
                </div>

                {/* Flow canvas */}
                <div className="flex-1" ref={reactFlowWrapper}>
                    <ReactFlow
                        nodes={nodes}
                        edges={edges}
                        nodeTypes={nodeTypes}
                        onNodesChange={isReadOnly ? undefined : (changes) => {
                            onNodesChange(changes);
                            // Mark dirty only for position changes (not selection)
                            if (changes.some((c) => c.type === "position" || c.type === "remove")) {
                                markDirty();
                            }
                        }}
                        onEdgesChange={isReadOnly ? undefined : (changes) => {
                            onEdgesChange(changes);
                            if (changes.some((c) => c.type === "remove")) {
                                markDirty();
                            }
                        }}
                        onConnect={onConnect}
                        onNodeClick={onNodeClick}
                        onPaneClick={onPaneClick}
                        onInit={setRfInstance}
                        onDragOver={onDragOver}
                        onDrop={onDrop}
                        nodesDraggable={!isReadOnly}
                        nodesConnectable={!isReadOnly}
                        elementsSelectable={true}
                        fitView
                        proOptions={{ hideAttribution: true }}
                        className="pipeline-flow"
                    >
                        <Background
                            variant={BackgroundVariant.Dots}
                            gap={20}
                            size={1}
                            color="hsl(var(--muted-foreground) / 0.15)"
                        />
                        <Controls
                            showInteractive={false}
                            className="!bg-card !border !shadow-sm"
                        />
                        <MiniMap
                            nodeColor={(n) => {
                                const d = n.data as OperatorNodeData;
                                return d.kind === "llm"
                                    ? "rgb(168 85 247)"
                                    : "rgb(56 189 248)";
                            }}
                            className="!bg-card !border !shadow-sm"
                            maskColor="hsl(var(--background) / 0.7)"
                        />
                    </ReactFlow>
                </div>
            </div>

            {/* Right: Node Config Drawer */}
            {selectedNodeId && (
                <NodeConfigDrawer
                    nodeId={selectedNodeId}
                    data={selectedNodeData}
                    readOnly={isReadOnly}
                    onUpdate={handleNodeUpdate}
                    onClose={() => setSelectedNodeId(null)}
                />
            )}
        </div>
    );
}
