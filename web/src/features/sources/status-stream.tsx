"use client";

import * as React from "react";
import { Activity } from "lucide-react";

export function StatusStream() {
    return (
        <div className="flex items-center gap-3 border-b bg-muted/30 px-6 py-2 text-xs text-muted-foreground overflow-hidden">
            <Activity className="h-3 w-3 shrink-0 animate-pulse text-green-500" />
            <div className="flex-1 overflow-hidden">
                <div className="animate-slide-in flex items-center gap-8 whitespace-nowrap">
                    <span>
                        Processing <strong>@naval</strong> latest thread...
                    </span>
                    <span>
                        Generated 3 new flashcards from <strong>Paul Graham</strong>
                    </span>
                    <span>
                        Syncing <strong>Arxiv</strong> papers...
                    </span>
                </div>
            </div>
        </div>
    );
}
