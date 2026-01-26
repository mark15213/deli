"use client";

import * as React from "react";
// import { ScrollArea } from "@/components/ui/scroll-area"; // Removed to avoid dependency issue
import { SourceType } from "@/features/sources/source-card";
import { Badge } from "@/components/ui/badge";

interface SourcePreviewProps {
    type: SourceType;
    title: string;
    content: string; // Simplified content
    metadata?: any;
}

export function SourcePreview({ type, title, content }: SourcePreviewProps) {
    return (
        <div className="h-full overflow-y-auto p-6 bg-card/50">
            <div className="max-w-prose mx-auto space-y-6">
                <div className="border-b pb-4">
                    <Badge variant="outline" className="mb-2 capitalize">{type}</Badge>
                    <h1 className="text-2xl font-bold tracking-tight">{title}</h1>
                </div>

                {/* Content Rendering based on type */}
                <div className="prose dark:prose-invert">
                    {type === "twitter" ? (
                        <div className="space-y-4">
                            {content.split('\n\n').map((tweet, i) => (
                                <div key={i} className="rounded-xl border p-4 bg-background shadow-sm">
                                    <div className="flex items-center gap-2 mb-2">
                                        <div className="h-8 w-8 rounded-full bg-slate-200 dark:bg-slate-700" />
                                        <div className="text-sm font-semibold">Naval Ravikant <span className="text-muted-foreground font-normal">@naval</span></div>
                                    </div>
                                    <p className="whitespace-pre-wrap">{tweet}</p>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="whitespace-pre-wrap leading-relaxed text-lg">
                            {content}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
