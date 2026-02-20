"use client";

/**
 * Left sidebar — lists all registered operators grouped by kind.
 * Users drag operators onto the canvas to add new nodes.
 */

import React, { useEffect, useState } from "react";
import { getOperators, OperatorManifest } from "@/lib/api/pipelines";
import { Cpu, Brain, GripVertical } from "lucide-react";

interface OperatorPaletteProps {
    disabled?: boolean;
}

export function OperatorPalette({ disabled }: OperatorPaletteProps) {
    const [operators, setOperators] = useState<OperatorManifest[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        getOperators()
            .then(setOperators)
            .catch(console.error)
            .finally(() => setLoading(false));
    }, []);

    const llmOps = operators.filter((o) => o.kind === "llm");
    const toolOps = operators.filter((o) => o.kind === "tool");

    const onDragStart = (
        e: React.DragEvent,
        operator: OperatorManifest
    ) => {
        if (disabled) return;
        e.dataTransfer.setData(
            "application/pipeline-operator",
            JSON.stringify(operator)
        );
        e.dataTransfer.effectAllowed = "move";
    };

    return (
        <div className="w-56 border-r bg-card overflow-y-auto flex flex-col">
            <div className="px-3 py-3 border-b">
                <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                    Operators
                </h3>
            </div>

            {loading ? (
                <div className="p-4 text-sm text-muted-foreground">Loading…</div>
            ) : (
                <div className="flex-1 overflow-y-auto p-2 space-y-4">
                    {/* LLM group */}
                    <div>
                        <div className="flex items-center gap-1.5 px-2 mb-1.5">
                            <Brain className="h-3 w-3 text-purple-400" />
                            <span className="text-[10px] font-semibold uppercase tracking-wider text-purple-400">
                                LLM
                            </span>
                        </div>
                        {llmOps.map((op) => (
                            <div
                                key={op.key}
                                draggable={!disabled}
                                onDragStart={(e) => onDragStart(e, op)}
                                className={`
                  flex items-center gap-2 px-2 py-1.5 rounded-md text-sm
                  border border-transparent
                  ${disabled
                                        ? "opacity-50 cursor-not-allowed"
                                        : "cursor-grab hover:bg-purple-500/10 hover:border-purple-500/20 active:cursor-grabbing"
                                    }
                `}
                            >
                                <GripVertical className="h-3 w-3 text-muted-foreground shrink-0" />
                                <span className="truncate">{op.name}</span>
                            </div>
                        ))}
                    </div>

                    {/* Tool group */}
                    <div>
                        <div className="flex items-center gap-1.5 px-2 mb-1.5">
                            <Cpu className="h-3 w-3 text-sky-400" />
                            <span className="text-[10px] font-semibold uppercase tracking-wider text-sky-400">
                                Tool
                            </span>
                        </div>
                        {toolOps.map((op) => (
                            <div
                                key={op.key}
                                draggable={!disabled}
                                onDragStart={(e) => onDragStart(e, op)}
                                className={`
                  flex items-center gap-2 px-2 py-1.5 rounded-md text-sm
                  border border-transparent
                  ${disabled
                                        ? "opacity-50 cursor-not-allowed"
                                        : "cursor-grab hover:bg-sky-500/10 hover:border-sky-500/20 active:cursor-grabbing"
                                    }
                `}
                            >
                                <GripVertical className="h-3 w-3 text-muted-foreground shrink-0" />
                                <span className="truncate">{op.name}</span>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
