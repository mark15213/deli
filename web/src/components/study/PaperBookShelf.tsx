"use client"

import { PaperBookCover } from "./PaperBookCover"
import { BookOpen, Library } from "lucide-react"
import type { PaperStudyGroup } from "@/lib/api/study"

interface PaperBookShelfProps {
    papers: PaperStudyGroup[]
    onOpenPaper: (paper: PaperStudyGroup) => void
}

export function PaperBookShelf({ papers, onOpenPaper }: PaperBookShelfProps) {
    if (papers.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center py-20 text-center">
                <div className="p-6 rounded-2xl bg-muted/30 mb-6">
                    <Library className="h-16 w-16 text-muted-foreground/40" />
                </div>
                <h2 className="text-2xl font-bold text-foreground mb-2">
                    Your bookshelf is empty
                </h2>
                <p className="text-muted-foreground max-w-md">
                    No papers are due for review right now. Add sources to start building your reading list.
                </p>
            </div>
        )
    }

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="p-2.5 rounded-xl bg-primary/10">
                        <BookOpen className="h-6 w-6 text-primary" />
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold tracking-tight">Your Reading List</h1>
                        <p className="text-sm text-muted-foreground">
                            {papers.length} {papers.length === 1 ? "paper" : "papers"} ·{" "}
                            {papers.reduce((sum, p) => sum + p.card_count, 0)} cards to review
                        </p>
                    </div>
                </div>
            </div>

            {/* Book Grid */}
            <div className="bookshelf-grid">
                {papers.map((paper) => (
                    <PaperBookCover
                        key={paper.source_id}
                        title={paper.source_title}
                        summary={paper.summary}
                        cardCount={paper.card_count}
                        sourceType={paper.source_type}
                        onClick={() => onOpenPaper(paper)}
                    />
                ))}
            </div>

            {/* Shelf shadow effect */}
            <div className="bookshelf-shadow" />
        </div>
    )
}
