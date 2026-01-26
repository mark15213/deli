"use client"

import { Twitter, MoreHorizontal, PlusCircle, Trash2, Edit2, FileText, Podcast, HelpCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

interface InboxItemProps {
    id: string
    source: string
    sourceType: "twitter" | "article" | "podcast" | "note"
    title: string
    summary: string
    generatedContent: {
        flashcards?: number
        quizzes?: number
        audio?: boolean
    }
    timestamp: string
    onClick: () => void
    selected?: boolean
}

function SourceIcon({ type }: { type: InboxItemProps["sourceType"] }) {
    switch (type) {
        case "twitter": return <Twitter className="h-4 w-4 text-blue-400" />
        case "article": return <FileText className="h-4 w-4 text-orange-400" />
        case "podcast": return <Podcast className="h-4 w-4 text-purple-400" />
        default: return <HelpCircle className="h-4 w-4 text-gray-400" />
    }
}

export function InboxItem({ source, sourceType, title, summary, generatedContent, timestamp, onClick, selected }: InboxItemProps) {
    return (
        <div
            className={cn(
                "group flex items-start gap-4 border-b p-4 transition-colors hover:bg-muted/50 cursor-pointer",
                selected && "bg-muted"
            )}
            onClick={onClick}
        >
            {/* Left: Source Icon */}
            <div className="mt-1">
                <div className="p-2 rounded-full bg-background border shadow-sm">
                    <SourceIcon type={sourceType} />
                </div>
            </div>

            {/* Middle: Content */}
            <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-medium text-muted-foreground">{source}</span>
                    <span className="text-[10px] text-muted-foreground/60">• {timestamp}</span>
                </div>
                <h3 className={cn("text-base font-medium leading-tight mb-1 group-hover:text-primary transition-colors", selected ? "text-primary" : "text-foreground")}>
                    {title}
                </h3>
                <p className="text-sm text-muted-foreground line-clamp-2 leading-relaxed">
                    {summary}
                </p>

                {/* Action Bar (Visible on Hover) */}
                <div className="flex items-center gap-2 mt-3 opacity-0 group-hover:opacity-100 transition-opacity">
                    <Button size="sm" variant="outline" className="h-7 text-xs gap-1">
                        <PlusCircle className="h-3 w-3" />
                        Add to Plan
                    </Button>
                    <Button size="sm" variant="ghost" className="h-7 w-7 p-0">
                        <Edit2 className="h-3 w-3" />
                    </Button>
                    <Button size="sm" variant="ghost" className="h-7 w-7 p-0 text-destructive hover:text-destructive">
                        <Trash2 className="h-3 w-3" />
                    </Button>
                </div>
            </div>

            {/* Right: Tags */}
            <div className="flex flex-col gap-1 items-end">
                {generatedContent.flashcards && (
                    <Badge variant="secondary" className="text-xs">
                        {generatedContent.flashcards} Flashcards
                    </Badge>
                )}
                {generatedContent.quizzes && (
                    <Badge variant="outline" className="text-xs">
                        {generatedContent.quizzes} Quiz
                    </Badge>
                )}
                {generatedContent.audio && (
                    <Badge variant="outline" className="text-xs border-purple-200 text-purple-600 dark:border-purple-800 dark:text-purple-400">
                        Audio
                    </Badge>
                )}
            </div>
        </div>
    )
}
