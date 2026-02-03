"use client"

import { DeckCard } from "./DeckCard"
import { BookOpen, Brain, Lightbulb, Code, Rocket, Heart } from "lucide-react"

interface Deck {
    id: string
    title: string
    description?: string
    coverImage?: string
    coverIcon?: React.ReactNode
    cardCount: number
    lastReviewedAt?: string
    masteryPercentage: number
    isSubscribed: boolean
}

interface DeckListProps {
    decks: Deck[]
    onSubscribeChange?: (deckId: string, subscribed: boolean) => void
    onDelete?: (deckId: string) => void
}

export function DeckList({ decks, onSubscribeChange, onDelete }: DeckListProps) {
    return (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {decks.map((deck) => (
                <DeckCard
                    key={deck.id}
                    {...deck}
                    onSubscribeChange={(subscribed) => onSubscribeChange?.(deck.id, subscribed)}
                    onDelete={() => onDelete?.(deck.id)}
                />
            ))}
        </div>
    )
}

// Demo data for the decks page
export const MOCK_DECKS: Deck[] = [
    {
        id: "1",
        title: "Naval's Wisdom",
        description: "Insights on wealth, happiness, and living a meaningful life from Naval Ravikant.",
        coverIcon: <Lightbulb className="h-12 w-12" />,
        cardCount: 48,
        lastReviewedAt: "2 days ago",
        masteryPercentage: 72,
        isSubscribed: true
    },
    {
        id: "2",
        title: "React Hooks Deep Dive",
        description: "Master React hooks with practical examples and advanced patterns.",
        coverIcon: <Code className="h-12 w-12" />,
        cardCount: 86,
        lastReviewedAt: "1 week ago",
        masteryPercentage: 45,
        isSubscribed: true
    },
    {
        id: "3",
        title: "Startup Mindset",
        description: "Key lessons from Y Combinator, Paul Graham essays, and successful founders.",
        coverIcon: <Rocket className="h-12 w-12" />,
        cardCount: 124,
        lastReviewedAt: "3 days ago",
        masteryPercentage: 58,
        isSubscribed: false
    },
    {
        id: "4",
        title: "Neuroscience Fundamentals",
        description: "Understanding the brain: memory, learning, and cognitive enhancement.",
        coverIcon: <Brain className="h-12 w-12" />,
        cardCount: 67,
        lastReviewedAt: "Yesterday",
        masteryPercentage: 89,
        isSubscribed: true
    },
    {
        id: "5",
        title: "Philosophy of Life",
        description: "Stoicism, existentialism, and practical philosophy for everyday life.",
        coverIcon: <BookOpen className="h-12 w-12" />,
        cardCount: 35,
        lastReviewedAt: "5 days ago",
        masteryPercentage: 28,
        isSubscribed: false
    },
    {
        id: "6",
        title: "Health & Wellness",
        description: "Sleep optimization, nutrition, exercise, and mental health protocols.",
        coverIcon: <Heart className="h-12 w-12" />,
        cardCount: 92,
        lastReviewedAt: "Today",
        masteryPercentage: 65,
        isSubscribed: true
    }
]
