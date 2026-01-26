"use client";

import * as React from "react";
import { 
    Twitter, 
    Rss, 
    Github, 
    FileText, 
    Database, 
    RefreshCw, 
    AlertCircle,
    CheckCircle2
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useUIStore } from "@/store/ui-store";

export type SourceType = "twitter" | "rss" | "notion" | "github" | "arxiv";

export interface Source {
    id: string;
    type: SourceType;
    name: string;
    description: string;
    status: "active" | "error" | "syncing";
    lastSync: string;
    itemCount: number;
    tags: string[];
}

interface SourceCardProps {
    source: Source;
}

const iconMap: Record<SourceType, React.ElementType> = {
    twitter: Twitter,
    rss: Rss,
    notion: Database,
    github: Github,
    arxiv: FileText,
};

const statusColorMap = {
    active: "bg-green-500",
    error: "bg-red-500",
    syncing: "bg-blue-500",
};

export function SourceCard({ source }: SourceCardProps) {
    const { openSlideOver, setSelectedSourceId } = useUIStore();
    const Icon = iconMap[source.type];

    const handleClick = () => {
        setSelectedSourceId(source.id);
        openSlideOver("source-detail");
    };

    return (
        <Card 
            className="cursor-pointer transition-all hover:border-primary/50 hover:shadow-md group relative overflow-hidden"
            onClick={handleClick}
        >
            {/* Status indicator glow */}
            <div className={cn(
                "absolute -right-4 -top-4 h-16 w-16 bg-gradient-to-br opacity-10 transition-opacity group-hover:opacity-20 rounded-full blur-xl",
                source.status === "active" ? "from-green-500 to-transparent" :
                source.status === "error" ? "from-red-500 to-transparent" :
                "from-blue-500 to-transparent"
            )} />

            <CardHeader className="flex flex-row items-start justify-between space-y-0 pb-2">
                <div className="flex items-center gap-3">
                    <div className={cn(
                        "flex h-10 w-10 items-center justify-center rounded-lg border bg-muted/50 transition-colors group-hover:bg-primary/5 group-hover:text-primary",
                    )}>
                        <Icon className="h-5 w-5" />
                    </div>
                    <div>
                        <h3 className="font-semibold leading-none tracking-tight">{source.name}</h3>
                        <p className="text-xs text-muted-foreground mt-1 capitalize">{source.type}</p>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    {source.status === "syncing" && (
                        <RefreshCw className="h-3 w-3 animate-spin text-blue-500" />
                    )}
                    {source.status === "error" && (
                        <AlertCircle className="h-3 w-3 text-red-500" />
                    )}
                    <div className={cn(
                        "h-2 w-2 rounded-full",
                        statusColorMap[source.status],
                        source.status === "syncing" && "animate-pulse"
                    )} />
                </div>
            </CardHeader>
            <CardContent>
                <div className="text-xs text-muted-foreground line-clamp-2 mb-4 h-8">
                    {source.description}
                </div>
                
                <div className="flex items-center justify-between text-xs text-muted-foreground border-t pt-3">
                    <div className="flex items-center gap-1">
                        <CheckCircle2 className="h-3 w-3 opacity-50" />
                        <span>{source.itemCount} items</span>
                    </div>
                    <span>{source.lastSync}</span>
                </div>
            </CardContent>
        </Card>
    );
}
