"use client"

import { useState, useEffect } from "react"
import { useSearchParams } from "next/navigation"
import { StudyContainer } from "@/components/study/StudyContainer"
import { getStudyQueue, submitReview, type StudyCard as ApiStudyCard, type Rating } from "@/lib/api/study"
import { Loader2 } from "lucide-react"

// Transform API response to component format
function mapApiCardToStudyCard(card: ApiStudyCard) {
    const baseCard = {
        id: card.id,
        source: card.source_title || (card.deck_titles && card.deck_titles[0]) || "Unknown Deck",
        sourceUrl: undefined,
    }

    if (card.type === "note" || card.type === "reading_note") {
        return {
            ...baseCard,
            // Map "reading_note" to "reading_note", otherwise "note"
            type: (card.type === "reading_note" ? "reading_note" : "note") as "reading_note" | "note",
            // For reading_note: title is question(headline), content is answer(body)
            // For note: content is question(text), title is undefined
            title: card.type === "reading_note" ? card.question : undefined,
            content: (card.type === "reading_note" && card.answer) ? card.answer : card.question,
            batch_id: card.batch_id,
            batch_index: card.batch_index,
            batch_total: card.batch_total,
            images: card.images,
        }
    } else if (card.type === "flashcard" || card.type === "qa") {
        return {
            ...baseCard,
            type: "flashcard" as const,
            content: card.question,
            answer: card.answer || "",
        }
    } else {
        // Quiz types: mcq, cloze, true_false
        const isCloze = card.type === "cloze"
        return {
            ...baseCard,
            type: "quiz" as const,
            content: card.question,
            quizType: isCloze ? "cloze" as const : "mcq" as const,
            options: card.options?.map((opt, i) => ({
                id: String.fromCharCode(97 + i),
                text: opt,
                isCorrect: opt === card.answer,
            })),
            correctAnswer: isCloze ? card.answer : undefined,
            explanation: card.explanation,
        }
    }
}

export default function StudyPage() {
    const searchParams = useSearchParams()
    const deckId = searchParams.get("deck")
    const [cards, setCards] = useState<ReturnType<typeof mapApiCardToStudyCard>[]>([])
    const [loading, setLoading] = useState(true)
    const [deckTitle, setDeckTitle] = useState("Study Queue")

    useEffect(() => {
        fetchStudyQueue()
    }, [deckId])

    const fetchStudyQueue = async () => {
        try {
            setLoading(true)
            const apiCards = await getStudyQueue(20, deckId || undefined)
            const mappedCards = apiCards.map(mapApiCardToStudyCard)
            setCards(mappedCards)
            if (apiCards.length > 0) {
                setDeckTitle(apiCards[0].deck_titles[0] || "Learning Session")
            }
        } catch (error) {
            console.error("Failed to fetch study queue:", error)
        } finally {
            setLoading(false)
        }
    }

    if (loading) {
        return (
            <div className="h-full flex items-center justify-center">
                <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
        )
    }

    if (cards.length === 0) {
        return (
            <div className="h-full flex flex-col items-center justify-center text-center p-8">
                <div className="text-6xl mb-4">🎉</div>
                <h2 className="text-2xl font-bold mb-2">All caught up!</h2>
                <p className="text-muted-foreground">
                    No cards due for review right now. Check back later!
                </p>
            </div>
        )
    }

    return (
        <div className="h-full">
            <StudyContainer
                cards={cards}
                deckTitle={deckTitle}
                onComplete={() => console.log("Study session complete!")}
            />
        </div>
    )
}


