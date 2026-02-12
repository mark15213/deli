"use client"

import { useState, useEffect, useCallback } from "react"
import { PaperBookShelf } from "@/components/study/PaperBookShelf"
import { PaperCardReader } from "@/components/study/PaperCardReader"
import { getStudyPapers, type PaperStudyGroup } from "@/lib/api/study"
import { Loader2 } from "lucide-react"

export default function StudyPage() {
    const [papers, setPapers] = useState<PaperStudyGroup[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const [selectedPaper, setSelectedPaper] = useState<PaperStudyGroup | null>(null)

    const fetchPapers = useCallback(async () => {
        try {
            setLoading(true)
            setError(null)
            const data = await getStudyPapers()
            setPapers(data)
        } catch (e) {
            console.error("Failed to fetch study papers:", e)
            setError("Failed to load papers. Please try again.")
        } finally {
            setLoading(false)
        }
    }, [])

    useEffect(() => {
        fetchPapers()
    }, [fetchPapers])

    const handleOpenPaper = useCallback((paper: PaperStudyGroup) => {
        setSelectedPaper(paper)
    }, [])

    const handleBackToShelf = useCallback(() => {
        setSelectedPaper(null)
        // Refresh data when returning to shelf
        fetchPapers()
    }, [fetchPapers])

    const handlePaperComplete = useCallback(() => {
        // Find next paper
        if (!selectedPaper) return
        const currentIdx = papers.findIndex(p => p.source_id === selectedPaper.source_id)
        const nextPaper = papers[currentIdx + 1]
        if (nextPaper) {
            setSelectedPaper(nextPaper)
        } else {
            setSelectedPaper(null)
            fetchPapers()
        }
    }, [selectedPaper, papers, fetchPapers])

    // Loading state
    if (loading) {
        return (
            <div className="flex items-center justify-center h-full min-h-[60vh]">
                <div className="flex flex-col items-center gap-4 animate-pulse">
                    <Loader2 className="h-10 w-10 animate-spin text-primary" />
                    <p className="text-muted-foreground">Loading your papers...</p>
                </div>
            </div>
        )
    }

    // Error state
    if (error) {
        return (
            <div className="flex items-center justify-center h-full min-h-[60vh]">
                <div className="text-center">
                    <p className="text-destructive mb-4">{error}</p>
                    <button
                        onClick={fetchPapers}
                        className="text-primary hover:underline"
                    >
                        Retry
                    </button>
                </div>
            </div>
        )
    }

    // Reader view (a paper is selected)
    if (selectedPaper) {
        return (
            <div className="max-w-4xl mx-auto px-6 py-6">
                <PaperCardReader
                    paper={selectedPaper}
                    onBack={handleBackToShelf}
                    onComplete={handlePaperComplete}
                />
            </div>
        )
    }

    // Bookshelf view (default)
    return (
        <div className="max-w-7xl mx-auto px-6 py-8">
            <PaperBookShelf
                papers={papers}
                onOpenPaper={handleOpenPaper}
            />
        </div>
    )
}
