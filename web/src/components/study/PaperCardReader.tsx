"use client"

import { useState, useCallback } from "react"
import { ArrowLeft, ExternalLink, BookOpen, CheckCircle2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { NoteCard } from "./NoteCard"
import { FlashcardView } from "./FlashcardView"
import { QuizCard } from "./QuizCard"
import { submitReview, skipBatch, type Rating } from "@/lib/api/study"
import type { PaperStudyGroup, StudyCard } from "@/lib/api/study"

interface PaperCardReaderProps {
    paper: PaperStudyGroup
    onBack: () => void
    onComplete: () => void
}

export function PaperCardReader({ paper, onBack, onComplete }: PaperCardReaderProps) {
    const [currentIndex, setCurrentIndex] = useState(0)
    const [completed, setCompleted] = useState(false)

    const cards = paper.cards
    const currentCard = cards[currentIndex]
    const progress = cards.length > 0 ? ((currentIndex) / cards.length) * 100 : 0

    const handleNext = useCallback(() => {
        if (currentIndex + 1 >= cards.length) {
            setCompleted(true)
        } else {
            setCurrentIndex(currentIndex + 1)
        }
    }, [currentIndex, cards.length])

    const handleMarkRead = useCallback(async () => {
        if (!currentCard) return
        try {
            await submitReview(currentCard.id, 3 as Rating) // GOOD rating
        } catch (e) {
            console.error("Failed to submit review:", e)
        }
        handleNext()
    }, [currentCard, handleNext])

    const ratingMap: Record<string, Rating> = {
        forgot: 1,
        hard: 2,
        easy: 4,
    }

    const handleFlashcardRate = useCallback(async (rating: "forgot" | "hard" | "easy") => {
        if (!currentCard) return
        try {
            await submitReview(currentCard.id, ratingMap[rating])
        } catch (e) {
            console.error("Failed to submit review:", e)
        }
        handleNext()
    }, [currentCard, handleNext])

    const handleQuizAnswer = useCallback(async (correct: boolean) => {
        if (!currentCard) return
        try {
            await submitReview(currentCard.id, (correct ? 3 : 1) as Rating)
        } catch (e) {
            console.error("Failed to submit review:", e)
        }
        handleNext()
    }, [currentCard, handleNext])

    const handleSkipBatch = useCallback(async () => {
        if (!currentCard?.batch_id) return
        try {
            await skipBatch(currentCard.batch_id)
        } catch (e) {
            console.error("Failed to skip batch:", e)
        }
        // Skip ahead past the current batch
        const batchId = currentCard.batch_id
        let nextIdx = currentIndex + 1
        while (nextIdx < cards.length && cards[nextIdx].batch_id === batchId) {
            nextIdx++
        }
        if (nextIdx >= cards.length) {
            setCompleted(true)
        } else {
            setCurrentIndex(nextIdx)
        }
    }, [currentCard, currentIndex, cards])

    const handleClip = useCallback(async () => {
        // Future: clip/save functionality
        console.log("Clip card:", currentCard?.id)
    }, [currentCard])

    // Completed state
    if (completed) {
        return (
            <div className="reader-container">
                <div className="flex flex-col items-center justify-center py-16 text-center animate-in fade-in slide-in-from-bottom-4 duration-500">
                    <div className="p-6 rounded-2xl bg-green-500/10 mb-6">
                        <CheckCircle2 className="h-16 w-16 text-green-500" />
                    </div>
                    <h2 className="text-2xl font-bold mb-2">Paper Complete!</h2>
                    <p className="text-muted-foreground mb-2 max-w-md">
                        You&apos;ve finished reviewing all {cards.length} cards from
                    </p>
                    <p className="text-sm font-medium text-foreground mb-8 max-w-lg">
                        &ldquo;{paper.source_title}&rdquo;
                    </p>
                    <div className="flex gap-3">
                        <Button variant="outline" onClick={onBack} className="gap-2">
                            <ArrowLeft className="h-4 w-4" />
                            Back to Shelf
                        </Button>
                        <Button onClick={onComplete} className="gap-2">
                            <BookOpen className="h-4 w-4" />
                            Next Paper
                        </Button>
                    </div>
                </div>
            </div>
        )
    }

    if (!currentCard) return null

    return (
        <div className="reader-container animate-in fade-in duration-300">
            {/* Top bar */}
            <div className="reader-topbar">
                <Button variant="ghost" size="sm" onClick={onBack} className="gap-2 text-muted-foreground hover:text-foreground">
                    <ArrowLeft className="h-4 w-4" />
                    <span className="hidden sm:inline">Back to Shelf</span>
                </Button>

                <div className="flex-1 min-w-0 mx-4 text-center">
                    <h2 className="text-sm font-semibold truncate">{paper.source_title}</h2>
                    <p className="text-xs text-muted-foreground">
                        Card {currentIndex + 1} of {cards.length}
                    </p>
                </div>

                {paper.source_url && (
                    <a
                        href={paper.source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-muted-foreground hover:text-foreground transition-colors"
                    >
                        <ExternalLink className="h-4 w-4" />
                    </a>
                )}
            </div>

            {/* Progress bar */}
            <div className="w-full h-1 bg-muted rounded-full overflow-hidden">
                <div
                    className="h-full bg-primary rounded-full transition-all duration-500 ease-out"
                    style={{ width: `${progress}%` }}
                />
            </div>

            {/* Batch info */}
            {currentCard.type === "reading_note" && currentCard.batch_id && currentCard.batch_total && (
                <div className="flex items-center justify-between px-1 py-2">
                    <span className="text-xs text-muted-foreground">
                        Series: Note {(currentCard.batch_index ?? 0) + 1} of {currentCard.batch_total}
                    </span>
                    <Button
                        variant="ghost"
                        size="sm"
                        className="text-xs h-7 text-muted-foreground"
                        onClick={handleSkipBatch}
                    >
                        Skip Series
                    </Button>
                </div>
            )}

            {/* Card content */}
            <div className="reader-card-area">
                {(currentCard.type === "note" || currentCard.type === "reading_note") && (
                    <NoteCard
                        // For reading notes, the 'question' acts as the Section Title/Header
                        // and 'answer' contains the detailed markdown body.
                        // Fallback: if no answer, use question as body content (legacy note support)
                        title={currentCard.answer ? currentCard.question : undefined}
                        content={currentCard.answer || currentCard.question}
                        images={currentCard.images}
                        onMarkRead={handleMarkRead}
                        onClip={handleClip}
                    />
                )}
                {currentCard.type === "flashcard" && (
                    <FlashcardView
                        question={currentCard.question}
                        answer={currentCard.answer || ""}
                        onRate={handleFlashcardRate}
                    />
                )}
                {currentCard.type === "quiz" && (
                    <QuizCard
                        type="mcq"
                        question={currentCard.question}
                        options={(currentCard.options || []).map((opt, i) => ({
                            id: String(i),
                            text: opt,
                            isCorrect: opt === currentCard.answer,
                        }))}
                        correctAnswer={currentCard.answer || ""}
                        explanation={currentCard.explanation}
                        onComplete={handleQuizAnswer}
                    />
                )}
            </div>
        </div>
    )
}
