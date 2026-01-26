"use client";

import * as React from "react";
import { Link2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface KnowledgeLineageProps {
    className?: string;
}

export function KnowledgeLineage({ className }: KnowledgeLineageProps) {
    return (
        <div className={cn("flex items-center gap-2 text-xs text-muted-foreground", className)}>
            <div className="flex items-center gap-1 hover:text-foreground cursor-pointer transition-colors">
                <span className="font-semibold text-blue-500">@naval</span>
            </div>
            <span>→</span>
            <div className="flex items-center gap-1 hover:text-foreground cursor-pointer transition-colors">
                <Link2 className="h-3 w-3" />
                <span>Thread</span>
            </div>
            <span>→</span>
            <div className="hover:text-foreground cursor-pointer transition-colors">
                AI Summary
            </div>
        </div>
    );
}
