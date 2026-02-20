"use client";

import React, { memo } from "react";
import { type NodeProps } from "@xyflow/react";

export interface StepNodeData {
    label: string;
    [key: string]: unknown;
}

function StepNodeComponent({ data, selected }: NodeProps) {
    const { label } = data as unknown as StepNodeData;

    return (
        <div
            className={`
        relative rounded-xl border-2 border-dashed
        bg-slate-50/50 dark:bg-slate-900/20
        transition-all duration-200
        ${selected
                    ? "border-primary/50 bg-primary/5 shadow-sm"
                    : "border-muted-foreground/20 hover:border-muted-foreground/40"
                }
      `}
            style={{ width: "100%", height: "100%" }}
        >
            {/* Label Badge */}
            <div className="absolute -top-3 left-4 px-2 py-0.5 bg-background border rounded-full shadow-sm text-xs font-medium text-muted-foreground flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-primary/50" />
                {label}
            </div>
        </div>
    );
}

export const StepNode = memo(StepNodeComponent);
