"use client";

/**
 * Node config drawer — slides in from the right when a node is selected.
 * Allows editing label, config_overrides, and shows port information.
 */

import React, { useState, useEffect } from "react";
import { X, Settings2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { OperatorNodeData } from "./OperatorNode";

interface NodeConfigDrawerProps {
    nodeId: string | null;
    data: OperatorNodeData | null;
    readOnly?: boolean;
    onUpdate: (nodeId: string, updates: Partial<OperatorNodeData>) => void;
    onClose: () => void;
}

export function NodeConfigDrawer({
    nodeId,
    data,
    readOnly,
    onUpdate,
    onClose,
}: NodeConfigDrawerProps) {
    const [label, setLabel] = useState("");
    const [configJson, setConfigJson] = useState("");
    const [jsonError, setJsonError] = useState("");

    useEffect(() => {
        if (data) {
            setLabel(data.label || "");
            setConfigJson(
                JSON.stringify(data.configOverrides || {}, null, 2)
            );
            setJsonError("");
        }
    }, [data, nodeId]);

    if (!nodeId || !data) return null;

    const handleSave = () => {
        try {
            const parsed = JSON.parse(configJson);
            setJsonError("");
            onUpdate(nodeId, { label, configOverrides: parsed });
        } catch {
            setJsonError("Invalid JSON");
        }
    };

    return (
        <div className="w-72 border-l bg-card flex flex-col overflow-hidden">
            {/* Header */}
            <div className="flex items-center justify-between px-3 py-3 border-b">
                <div className="flex items-center gap-2">
                    <Settings2 className="h-4 w-4 text-muted-foreground" />
                    <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                        Node Config
                    </h3>
                </div>
                <button
                    onClick={onClose}
                    className="p-1 rounded-md hover:bg-muted"
                >
                    <X className="h-4 w-4" />
                </button>
            </div>

            <div className="flex-1 overflow-y-auto p-3 space-y-4">
                {/* Operator info */}
                <div>
                    <div className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1">
                        Operator
                    </div>
                    <div className="text-sm font-medium">{data.operatorKey}</div>
                    <span
                        className={`inline-block text-[10px] mt-1 px-1.5 py-0.5 rounded-full uppercase ${data.kind === "llm"
                                ? "bg-purple-500/10 text-purple-400"
                                : "bg-sky-500/10 text-sky-400"
                            }`}
                    >
                        {data.kind}
                    </span>
                </div>

                {/* Label */}
                <div>
                    <label className="text-[10px] uppercase tracking-wider text-muted-foreground block mb-1">
                        Label
                    </label>
                    <input
                        type="text"
                        value={label}
                        onChange={(e) => setLabel(e.target.value)}
                        disabled={readOnly}
                        className="w-full text-sm px-2 py-1.5 rounded-md border bg-background disabled:opacity-50"
                    />
                </div>

                {/* Config overrides */}
                <div>
                    <label className="text-[10px] uppercase tracking-wider text-muted-foreground block mb-1">
                        Config Overrides
                    </label>
                    <textarea
                        value={configJson}
                        onChange={(e) => {
                            setConfigJson(e.target.value);
                            setJsonError("");
                        }}
                        disabled={readOnly}
                        rows={5}
                        className="w-full text-xs font-mono px-2 py-1.5 rounded-md border bg-background resize-none disabled:opacity-50"
                    />
                    {jsonError && (
                        <div className="text-xs text-destructive mt-1">{jsonError}</div>
                    )}
                </div>

                {/* Ports */}
                <div>
                    <div className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1">
                        Input Ports
                    </div>
                    {(data.inputPorts || []).length === 0 ? (
                        <div className="text-xs text-muted-foreground">None</div>
                    ) : (
                        <div className="space-y-1">
                            {data.inputPorts.map((p) => (
                                <div
                                    key={p.key}
                                    className="flex items-center gap-2 text-xs"
                                >
                                    <span className="w-2 h-2 rounded-full bg-muted-foreground" />
                                    <span className="font-mono">{p.key}</span>
                                    <span className="text-muted-foreground">({p.type})</span>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                <div>
                    <div className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1">
                        Output Ports
                    </div>
                    {(data.outputPorts || []).length === 0 ? (
                        <div className="text-xs text-muted-foreground">None</div>
                    ) : (
                        <div className="space-y-1">
                            {data.outputPorts.map((p) => (
                                <div
                                    key={p.key}
                                    className="flex items-center gap-2 text-xs"
                                >
                                    <span className="w-2 h-2 rounded-full bg-primary" />
                                    <span className="font-mono">{p.key}</span>
                                    <span className="text-muted-foreground">({p.type})</span>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>

            {/* Footer */}
            {!readOnly && (
                <div className="border-t p-3">
                    <Button size="sm" className="w-full" onClick={handleSave}>
                        Apply Changes
                    </Button>
                </div>
            )}
        </div>
    );
}
