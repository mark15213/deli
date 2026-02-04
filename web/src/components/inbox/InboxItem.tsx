"use client"

import { Twitter, Trash2, Eye, FileText, Podcast, HelpCircle, ChevronDown, ChevronUp } from "lucide-react"
import { Button } from "@/components/ui/button"
import { TypePill } from "@/components/shared/TypePill"
import { DeckSelectMenu } from "@/components/inbox/DeckSelectMenu"
import { cn } from "@/lib/utils"
import { useState } from "react"

interface DeckOption {
    id: string
    name: string
    cardCount: number
}

interface InboxItemProps {
    id: string
    source: string
    sourceType: "twitter" | "article" | "podcast" | "note"
    title: string
    summary: string
    generatedContent: {
        notes?: number
        flashcards?: number
        quizzes?: number
    }
    timestamp: string
    onClick: () => void
    selected?: boolean
    decks?: DeckOption[]
    onToggleDeck?: (sourceId: string, deckId: string) => Promise<void>
    onCreateDeck?: () => void
    currentDeckIds?: string[]
    onDelete?: (id: string) => Promise<void>
}

function SourceIcon({ type }: { type: InboxItemProps["sourceType"] }) {
    switch (type) {
        case "twitter": return <Twitter className="h-4 w-4 text-blue-400" />
        case "article": return <FileText className="h-4 w-4 text-orange-400" />
        case "podcast": return <Podcast className="h-4 w-4 text-purple-400" />
        default: return <HelpCircle className="h-4 w-4 text-gray-400" />
    }
}

export function InboxItem({
    id,
    source,
    sourceType,
    title,
    summary,
    generatedContent,
    timestamp,
    onClick,
    selected,
    decks = [],
    onToggleDeck,
    onCreateDeck,
    currentDeckIds = [],
    onDelete
}: InboxItemProps) {
    const [isExpanded, setIsExpanded] = useState(false)
    const [isProcessing, setIsProcessing] = useState(false)
    const [isDeleting, setIsDeleting] = useState(false)

    const handleDeckSelect = async (deckId: string) => {
        if (!onToggleDeck) {
            console.log("Toggle deck not implemented, selected:", deckId)
            return
        }

        try {
            setIsProcessing(true)
            await onToggleDeck(id, deckId)
        } catch (error) {
            console.error("Failed to toggle deck:", error)
        } finally {
            setIsProcessing(false)
        }
    }

    const handleCreateDeck = () => {
        if (onCreateDeck) {
            onCreateDeck()
        } else {
            console.log("Create deck not implemented")
        }
    }

    const handleDelete = async () => {
        if (!onDelete) {
            console.log("Delete not implemented")
            return
        }

        if (!confirm(`Delete all cards from "${title}"? This cannot be undone.`)) {
            return
        }

        try {
            setIsDeleting(true)
            await onDelete(id)
        } catch (error) {
            console.error("Failed to delete:", error)
        } finally {
            setIsDeleting(false)
        }
    }

    return (
        <div
            className={cn(
                "group border-b transition-colors",
                selected && "bg-muted"
            )}
        >
            {/* Main Row */}
            <div
                className="flex items-start gap-4 p-4 cursor-pointer hover:bg-muted/50"
                onClick={(e) => {
                    e.stopPropagation()
                    onClick()
                }}
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
                    <h3 className={cn("text-base font-medium leading-tight mb-2 group-hover:text-primary transition-colors", selected ? "text-primary" : "text-foreground")}>
                        {title}
                    </h3>

                    {/* Type Pills */}
                    <div className="flex flex-wrap items-center gap-2 mb-2">
                        <TypePill type="note" count={generatedContent.notes || 0} />
                        <TypePill type="flashcard" count={generatedContent.flashcards || 0} />
                        <TypePill type="quiz" count={generatedContent.quizzes || 0} />
                    </div>

                    <p className="text-sm text-muted-foreground line-clamp-2 leading-relaxed">
                        {summary}
                    </p>
                </div>

                {/* Right: Actions */}
                <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity" onClick={(e) => e.stopPropagation()}>
                    <DeckSelectMenu
                        decks={decks}
                        onSelect={handleDeckSelect}
                        onCreateNew={handleCreateDeck}
                        disabled={isProcessing}
                        currentDeckIds={currentDeckIds}
                    />
                    <Button
                        size="sm"
                        variant="ghost"
                        className="h-8 text-xs gap-1"
                        onClick={(e) => {
                            e.stopPropagation()
                            setIsExpanded(!isExpanded)
                        }}
                    >
                        {isExpanded ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
                        <Eye className="h-3 w-3" />
                        Preview
                    </Button>
                    <Button
                        size="sm"
                        variant="ghost"
                        className="h-8 w-8 p-0 text-destructive hover:text-destructive"
                        onClick={(e) => {
                            e.stopPropagation()
                            handleDelete()
                        }}
                        disabled={isDeleting}
                    >
                        <Trash2 className="h-3.5 w-3.5" />
                    </Button>
                </div>
            </div>

            {/* Expandable Preview Section */}
            {isExpanded && (
                <div className="px-4 pb-4 pt-0 ml-14 border-t bg-muted/30">
                    <div className="py-4 space-y-3">
                        <h4 className="text-sm font-medium text-muted-foreground">Generated Content Preview</h4>
                        <div className="grid gap-2">
                            {generatedContent.flashcards && generatedContent.flashcards > 0 && (
                                <div className="p-3 rounded-lg border bg-card text-sm">
                                    <span className="text-orange-500 font-medium">Flashcard: </span>
                                    <span className="text-muted-foreground">What is the core concept discussed here?</span>
                                </div>
                            )}
                            {generatedContent.notes && generatedContent.notes > 0 && (
                                <div className="p-3 rounded-lg border bg-card text-sm">
                                    <span className="text-blue-500 font-medium">Note: </span>
                                    <span className="text-muted-foreground">{summary.slice(0, 100)}...</span>
                                </div>
                            )}
                            {generatedContent.quizzes && generatedContent.quizzes > 0 && (
                                <div className="p-3 rounded-lg border bg-card text-sm">
                                    <span className="text-purple-500 font-medium">Quiz: </span>
                                    <span className="text-muted-foreground">Which statement best describes the author's main argument?</span>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}
