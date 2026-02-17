"use client"

import { useState } from "react"
import { StudyProgress } from "@/components/shared/ProgressBar"
import { NoteCard } from "./NoteCard"
import { FlashcardView } from "./FlashcardView"
import { QuizCard } from "./QuizCard"
import { Button } from "@/components/ui/button"
import { ArrowLeft, X, SkipForward, RotateCcw } from "lucide-react"
import { cn } from "@/lib/utils"
import Link from "next/link"
import { skipBatch } from "@/lib/api/study"

type CardType = "note" | "flashcard" | "quiz" | "reading_note"

interface StudyCard {
    id: string
    type: CardType
    content: string
    title?: string
    answer?: string
    images?: string[] // For reading notes
    source?: string
    sourceUrl?: string
    quizType?: "mcq" | "true_false" | "cloze"
    options?: Array<{ id: string; text: string; isCorrect: boolean }>
    correctAnswer?: string
    explanation?: string
    // Batch info for reading notes
    batch_id?: string
    batch_index?: number
    batch_total?: number
}

interface StudyContainerProps {
    cards: StudyCard[]
    deckTitle?: string
    onComplete?: () => void
    onBatchSkipped?: (batchId: string) => void
    onReview?: (cardId: string, rating: 1 | 2 | 3 | 4) => Promise<void>
}

export function StudyContainer({ cards, deckTitle = "Learning Session", onComplete, onBatchSkipped, onReview }: StudyContainerProps) {
    const [currentIndex, setCurrentIndex] = useState(0)
    const [completedCards, setCompletedCards] = useState<string[]>([])
    const [skippingBatch, setSkippingBatch] = useState(false)

    const currentCard = cards[currentIndex]
    const remaining = cards.length - currentIndex

    const goToNextCard = () => {
        setCompletedCards([...completedCards, currentCard.id])

        if (currentIndex < cards.length - 1) {
            setCurrentIndex(currentIndex + 1)
        } else {
            // Session complete - move past last index to show completion screen
            setCurrentIndex(currentIndex + 1)
            onComplete?.()
        }
    }

    const goToPreviousCard = () => {
        if (currentIndex > 0) {
            setCurrentIndex(currentIndex - 1)
        }
    }

    const handleNoteRead = async () => {
        if (onReview) {
            await onReview(currentCard.id, 3) // Mark as GOOD/passive review
        }
        goToNextCard()
    }

    const handleFlashcardRate = async (rating: "forgot" | "hard" | "easy") => {
        let numericRating: 1 | 2 | 3 | 4 = 3 // default good
        if (rating === "forgot") numericRating = 1
        else if (rating === "hard") numericRating = 2
        else if (rating === "easy") numericRating = 4

        if (onReview) {
            await onReview(currentCard.id, numericRating)
        }

        console.log("Card rated:", rating)
        goToNextCard()
    }

    const handleQuizComplete = async (isCorrect: boolean) => {
        if (onReview) {
            await onReview(currentCard.id, isCorrect ? 3 : 1) // GOOD or AGAIN
        }
        console.log("Quiz completed:", isCorrect ? "correct" : "incorrect")
        goToNextCard()
    }

    const handleSkipBatch = async () => {
        if (!currentCard.batch_id) return

        setSkippingBatch(true)
        try {
            await skipBatch(currentCard.batch_id)
            onBatchSkipped?.(currentCard.batch_id)

            // Skip to next card that is not in this batch
            const nextNonBatchIndex = cards.findIndex(
                (card, idx) => idx > currentIndex && card.batch_id !== currentCard.batch_id
            )

            if (nextNonBatchIndex !== -1) {
                setCurrentIndex(nextNonBatchIndex)
            } else {
                // No more cards outside this batch
                setCurrentIndex(cards.length)
                onComplete?.()
            }
        } catch (error) {
            console.error("Failed to skip batch:", error)
        } finally {
            setSkippingBatch(false)
        }
    }

    if (!currentCard) {
        return (
            <div className="h-full flex flex-col items-center justify-center text-center p-8">
                <div className="text-6xl mb-4">🎉</div>
                <h2 className="text-2xl font-bold mb-2">Session Complete!</h2>
                <p className="text-muted-foreground mb-6">
                    You've reviewed all {cards.length} cards
                </p>
                <Link href="/decks">
                    <Button>Back to Decks</Button>
                </Link>
            </div>
        )
    }

    // Check if current card is part of a batch (reading notes series)
    const isReadingNote = currentCard.type === "reading_note" && currentCard.batch_id

    return (
        <div className="h-full flex flex-col bg-background">
            {/* Top Bar */}
            <div className="px-6 py-4 border-b bg-card flex items-center gap-4">
                <Link href="/decks">
                    <Button variant="ghost" size="icon">
                        <ArrowLeft className="h-4 w-4" />
                    </Button>
                </Link>
                {currentIndex > 0 && (
                    <Button variant="ghost" size="icon" onClick={goToPreviousCard} title="Previous Card">
                        <RotateCcw className="h-4 w-4" />
                    </Button>
                )}
                <div className="flex-1">
                    <h1 className="font-semibold text-sm">{deckTitle}</h1>
                    {/* Batch indicator for reading notes */}
                    {isReadingNote && (
                        <p className="text-xs text-muted-foreground">
                            Note {currentCard.batch_index} of {currentCard.batch_total}
                        </p>
                    )}
                </div>
                <StudyProgress remaining={remaining} total={cards.length} className="flex-1 max-w-xs" />

                {/* Skip Series button for reading notes */}
                {isReadingNote && (
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={handleSkipBatch}
                        disabled={skippingBatch}
                        className="gap-1"
                    >
                        <SkipForward className="h-3 w-3" />
                        Skip Series
                    </Button>
                )}

                <Link href="/decks">
                    <Button variant="ghost" size="icon">
                        <X className="h-4 w-4" />
                    </Button>
                </Link>
            </div>

            {/* Card Content */}
            <div className="flex-1 overflow-hidden">
                <div className={cn(
                    "h-full transition-all duration-300",
                    "animate-in fade-in slide-in-from-right-4"
                )} key={currentCard.id}>
                    {(currentCard.type === "note" || currentCard.type === "reading_note") && (
                        <NoteCard
                            title={currentCard.title}
                            content={currentCard.content}
                            images={currentCard.images}
                            source={currentCard.source}
                            onMarkRead={handleNoteRead}
                            onClip={() => console.log("Clipped")}
                        />
                    )}

                    {currentCard.type === "flashcard" && (
                        <FlashcardView
                            question={currentCard.content}
                            answer={currentCard.answer || ""}
                            source={currentCard.source}
                            sourceUrl={currentCard.sourceUrl}
                            onRate={handleFlashcardRate}
                        />
                    )}

                    {currentCard.type === "quiz" && (
                        <QuizCard
                            type={currentCard.quizType || "mcq"}
                            question={currentCard.content}
                            options={currentCard.options}
                            correctAnswer={currentCard.correctAnswer}
                            explanation={currentCard.explanation}
                            source={currentCard.source}
                            onComplete={handleQuizComplete}
                        />
                    )}
                </div>
            </div>
        </div>
    )
}
