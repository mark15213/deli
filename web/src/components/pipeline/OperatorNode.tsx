"use client";

/**
 * Custom Xyflow node for pipeline operators.
 *
 * - Colored header (purple = LLM, blue = tool)
 * - Input handles on left, output handles on right
 * - Label + operator key subtitle
 */

import React, { memo } from "react";
import { Handle, Position, type NodeProps } from "@xyflow/react";

export interface OperatorNodeData {
    label: string;
    operatorKey: string;
    kind: "llm" | "tool";
    inputPorts: { key: string; type: string }[];
    outputPorts: { key: string; type: string }[];
    configOverrides: Record<string, any>;
    isSystem?: boolean;
    [key: string]: unknown;
}

const kindColors = {
    llm: {
        bg: "bg-purple-500/10",
        border: "border-purple-500/30",
        header: "bg-purple-500",
        dot: "bg-purple-400",
    },
    tool: {
        bg: "bg-sky-500/10",
        border: "border-sky-500/30",
        header: "bg-sky-500",
        dot: "bg-sky-400",
    },
};

function OperatorNodeComponent({ data, selected }: NodeProps) {
    const nodeData = data as unknown as OperatorNodeData;
    const colors = kindColors[nodeData.kind] || kindColors.tool;
    const inputPorts = nodeData.inputPorts || [];
    const outputPorts = nodeData.outputPorts || [];

    return (
        <div
            className={`
        rounded-lg border shadow-md min-w-[180px] max-w-[240px]
        ${colors.bg} ${colors.border}
        ${selected ? "ring-2 ring-primary ring-offset-1 ring-offset-background" : ""}
        transition-shadow
      `}
        >
            {/* Header */}
            <div
                className={`${colors.header} text-white text-[11px] font-semibold px-3 py-1.5 rounded-t-lg flex items-center gap-1.5`}
            >
                <span className="uppercase tracking-wider opacity-80">
                    {nodeData.kind}
                </span>
            </div>

            {/* Body */}
            <div className="px-3 py-2">
                <div className="font-medium text-sm truncate">
                    {nodeData.label || nodeData.operatorKey}
                </div>
                {nodeData.label && nodeData.label !== nodeData.operatorKey && (
                    <div className="text-[10px] text-muted-foreground truncate">
                        {nodeData.operatorKey}
                    </div>
                )}

                {/* Config overrides badge */}
                {Object.keys(nodeData.configOverrides || {}).length > 0 && (
                    <div className="mt-1 flex flex-wrap gap-1">
                        {Object.entries(nodeData.configOverrides).map(([k, v]) => (
                            <span
                                key={k}
                                className="text-[9px] bg-muted px-1.5 py-0.5 rounded-full"
                            >
                                {k}: {String(v)}
                            </span>
                        ))}
                    </div>
                )}
            </div>

            {/* Handles */}
            {inputPorts.map((port, i) => (
                <Handle
                    key={`in-${port.key}`}
                    type="target"
                    position={Position.Left}
                    id={port.key}
                    style={{
                        top: `${40 + i * 20}px`,
                        background: "hsl(var(--muted-foreground))",
                        width: 8,
                        height: 8,
                        border: "2px solid hsl(var(--background))",
                    }}
                    title={`${port.key} (${port.type})`}
                />
            ))}

            {outputPorts.map((port, i) => (
                <Handle
                    key={`out-${port.key}`}
                    type="source"
                    position={Position.Right}
                    id={port.key}
                    style={{
                        top: `${40 + i * 20}px`,
                        background: "hsl(var(--primary))",
                        width: 8,
                        height: 8,
                        border: "2px solid hsl(var(--background))",
                    }}
                    title={`${port.key} (${port.type})`}
                />
            ))}
        </div>
    );
}

export const OperatorNode = memo(OperatorNodeComponent);
