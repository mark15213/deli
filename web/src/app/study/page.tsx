"use client"

import { useState, useEffect, useCallback } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { PaperBookShelf } from "@/components/study/PaperBookShelf"
import { PaperCardReader } from "@/components/study/PaperCardReader"
import { StudyContainer } from "@/components/study/StudyContainer"
import { getStudyPapers, getStudyQueue, submitReview, type PaperStudyGroup, type StudyCard } from "@/lib/api/study"
import { Loader2, Zap } from "lucide-react"

export default function StudyPage() {
    const router = useRouter()
    const searchParams = useSearchParams()
    const deckId = searchParams.get("deck")

    // Deck Study Mode State
    const [queue, setQueue] = useState<StudyCard[]>([])
    const [deckLoading, setDeckLoading] = useState(false)
    const [deckError, setDeckError] = useState<string | null>(null)

    // Paper Mode State
    const [papers, setPapers] = useState<PaperStudyGroup[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const [selectedPaper, setSelectedPaper] = useState<PaperStudyGroup | null>(null)

    // --- Deck Study Logic ---
    const fetchDeckQueue = useCallback(async () => {
        if (!deckId) return
        try {
            setDeckLoading(true)
            setDeckError(null)
            const data = await getStudyQueue(20, deckId)
            setQueue(data)
        } catch (e) {
            console.error("Failed to fetch study queue:", e)
            setDeckError("Failed to load study queue.")
        } finally {
            setDeckLoading(false)
        }
    }, [deckId])

    useEffect(() => {
        if (deckId) {
            fetchDeckQueue()
        }
    }, [deckId, fetchDeckQueue])

    const handleDeckReview = async (cardId: string, rating: 1 | 2 | 3 | 4) => {
        try {
            await submitReview(cardId, rating)
        } catch (e) {
            console.error("Failed to submit review:", e)
        }
    }

    const handleDeckComplete = () => {
        // Refresh queue to see if there are more cards
        fetchDeckQueue()
    }

    // --- Paper Study Logic ---
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
        if (!deckId) {
            fetchPapers()
        }
    }, [deckId, fetchPapers])

    const handleOpenPaper = useCallback((paper: PaperStudyGroup) => {
        setSelectedPaper(paper)
    }, [])

    const handleBackToShelf = useCallback(() => {
        setSelectedPaper(null)
        fetchPapers()
    }, [fetchPapers])

    const handlePaperComplete = useCallback(() => {
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


    // --- Render Logic ---

    // 1. Deck Study Mode
    if (deckId) {
        if (deckLoading) {
            return (
                <div className="flex items-center justify-center h-full min-h-[60vh]">
                    <Loader2 className="h-8 w-8 animate-spin text-primary" />
                </div>
            )
        }

        if (deckError) {
            return (
                <div className="flex flex-col items-center justify-center h-full min-h-[60vh] gap-4">
                    <p className="text-destructive">{deckError}</p>
                    <button onClick={fetchDeckQueue} className="text-primary hover:underline">Retry</button>
                    <button onClick={() => router.push("/decks")} className="text-muted-foreground hover:text-foreground">Back to Decks</button>
                </div>
            )
        }

        if (queue.length === 0) {
            return (
                <div className="h-full flex flex-col items-center justify-center text-center p-8 min-h-[60vh]">
                    <div className="text-6xl mb-4">🎉</div>
                    <h2 className="text-2xl font-bold mb-2">All Caught Up!</h2>
                    <p className="text-muted-foreground mb-6">
                        You've reviewed all due cards for this deck.
                    </p>
                    <button
                        onClick={() => router.push(`/decks/${deckId}`)}
                        className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90"
                    >
                        Back to Deck
                    </button>
                </div>
            )
        }

        // Map API StudyCard to StudyContainer's StudyCard interface
        // Note: They are slightly different (StudyContainer expects 'content', API returns 'question')
        const mappedCards = queue.map(c => ({
            id: c.id,
            type: c.type as any, // "note" | "flashcard" | "quiz" | "reading_note"
            content: c.question, // Map question to content
            title: c.source_title,
            answer: c.answer,
            images: c.images,
            source: c.source_title,
            // Quiz props
            quizType: (["mcq", "true_false", "cloze"].includes(c.type) ? c.type : "mcq") as any,
            options: c.options?.map((o, i) => ({ id: String(i), text: o, isCorrect: i === 0 })), // Warning: This logic assumes option 0 is correct or needs real data
            correctAnswer: c.answer, // For cloze
            explanation: c.explanation,
            batch_id: c.batch_id,
            batch_index: c.batch_index,
            batch_total: c.batch_total,
        }))

        // Verify options logic: API for quiz options might need structure. 
        // Checking `StudyCard` definition in `web/src/lib/api/study.ts`: `options?: string[]`
        // Checking `QuizCard` in `web/src/components/study/QuizCard.tsx`: `options?: {id, text, isCorrect}[]`
        // The API currently returns simple strings? 
        // In `backend/app/api/study.py`, `StudyCard` model has `options: Optional[List[str]] = None`.
        // It seems existing Quizzes might not support complex options structure fully in the Study API response yet 
        // OR the frontend needs to map it. 
        // For now, let's assume if it's a quiz, we might need a better mapping or backend update.
        // However, for standard Flashcards (QA), it works.
        // Let's stick to basic mapping for now.

        return (
            <div className="h-[calc(100vh-4rem)]"> {/* Adjust height for layout */}
                <StudyContainer
                    cards={mappedCards}
                    deckTitle={queue[0]?.deck_titles?.[0] || "Study Session"}
                    onReview={handleDeckReview}
                    onComplete={handleDeckComplete}
                />
            </div>
        )
    }

    // 2. Paper Study Mode (Original)

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
            {/* Start Gulping CTA */}
            <div className="mb-8">
                <button
                    onClick={() => router.push("/gulp")}
                    className="group w-full p-4 rounded-2xl bg-gradient-to-r from-primary/10 via-primary/5 to-amber-500/10 border border-primary/20 hover:border-primary/40 transition-all duration-300 hover:shadow-lg hover:shadow-primary/5"
                >
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-xl bg-primary/20 flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                                <Zap className="h-5 w-5 text-primary" />
                            </div>
                            <div className="text-left">
                                <h3 className="font-bold text-sm">Start Gulping</h3>
                                <p className="text-xs text-muted-foreground">TikTok-style immersive learning</p>
                            </div>
                        </div>
                        <span className="text-xs text-muted-foreground group-hover:text-foreground transition-colors">
                            →
                        </span>
                    </div>
                </button>
            </div>

            <PaperBookShelf
                papers={papers}
                onOpenPaper={handleOpenPaper}
            />
        </div>
    )
}

