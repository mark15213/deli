"use client";

import * as React from "react";
import {
    Twitter,
    Rss,
    Github,
    FileText,
    Database,
    MoreHorizontal,
    PlusCircle,
    Archive,
    Trash2,
    Edit3
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useUIStore } from "@/store/ui-store";

export type InboxItemStatus = "pending" | "processed" | "archived";

export interface InboxItem {
    id: string;
    sourceType: "twitter" | "rss" | "notion" | "github" | "arxiv";
    sourceName: string;
    title: string;
    summary: string;
    receivedAt: string;
    tags: string[];
    generatedArtifacts: ("flashcard" | "quiz" | "summary" | "audio")[];
}

interface InboxItemProps {
    item: InboxItem;
}

const iconMap = {
    twitter: Twitter,
    rss: Rss,
    notion: Database,
    github: Github,
    arxiv: FileText,
};

export function InboxItem({ item }: InboxItemProps) {
    const { selectedInboxItemId, setSelectedInboxItemId } = useUIStore();
    const isSelected = selectedInboxItemId === item.id;
    const Icon = iconMap[item.sourceType];

    return (
        <div
            className={cn(
                "group relative flex cursor-pointer flex-col gap-2 border-b p-4 transition-colors hover:bg-accent/50",
                isSelected && "bg-accent border-l-2 border-l-primary pl-[14px]"
            )}
            onClick={() => setSelectedInboxItemId(item.id)}
        >
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <Icon className="h-4 w-4 text-muted-foreground" />
                    <span className="text-xs font-medium text-muted-foreground">{item.sourceName}</span>
                    <span className="text-xs text-muted-foreground">• {item.receivedAt}</span>
                </div>
                {/* Hover Actions */}
                <div className="hidden group-hover:flex items-center gap-1">
                    <Button variant="ghost" size="icon" className="h-6 w-6" title="Add to Plan">
                        <PlusCircle className="h-4 w-4" />
                    </Button>
                    <Button variant="ghost" size="icon" className="h-6 w-6" title="Edit">
                        <Edit3 className="h-4 w-4" />
                    </Button>
                    <Button variant="ghost" size="icon" className="h-6 w-6 text-destructive" title="Archive">
                        <Archive className="h-4 w-4" />
                    </Button>
                </div>
            </div>

            <h3 className="font-semibold leading-tight line-clamp-1">
                {item.title}
            </h3>

            <p className="text-sm text-muted-foreground line-clamp-2">
                {item.summary}
            </p>

            <div className="flex flex-wrap gap-2 mt-1">
                {item.generatedArtifacts.map((artifact, i) => (
                    <Badge key={i} variant="secondary" className="text-[10px] px-1.5 py-0 h-5">
                        {artifact}
                    </Badge>
                ))}
            </div>
        </div>
    );
}
