"use client"

import { useState, useEffect } from "react"
import { useParams, useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Switch } from "@/components/ui/switch"
import { CardList, Card } from "@/components/decks/CardListItem"
import { ProgressBar } from "@/components/shared/ProgressBar"
import { ArrowLeft, Play, Star, MoreHorizontal, Settings, Trash2, Loader2, FileText, Lightbulb } from "lucide-react"
import { cn } from "@/lib/utils"
import Link from "next/link"
import { getDeck, deleteDeck, subscribeToDeck, unsubscribeFromDeck, type DeckDetail, type CardInDeck } from "@/lib/api/decks"
import { removeCardFromDeck } from "@/lib/api/inbox"

// Helper to map API card to UI card
function mapApiCardToUiCard(card: CardInDeck): Card {
    let type: "note" | "flashcard" | "quiz" = "note"
    if (card.type === "flashcard" || card.type === "qa") type = "flashcard"
    else if (["mcq", "cloze", "quiz", "true_false"].includes(card.type)) type = "quiz"

    return {
        id: card.id,
        type,
        content: card.question,
        source: card.source_title,
        isMastered: card.status === "archived", // Simplified mastery check
    }
}

export default function DeckDetailPage() {
    const params = useParams()
    const router = useRouter()
    const deckId = params.id as string

    const [deck, setDeck] = useState<DeckDetail | null>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const [isSubscribed, setIsSubscribed] = useState(false)
    const [isEditing, setIsEditing] = useState(false)

    useEffect(() => {
        const fetchDeck = async () => {
            try {
                setLoading(true)
                const data = await getDeck(deckId)
                setDeck(data)
                setIsSubscribed(data.is_subscribed)
            } catch (err) {
                console.error("Failed to fetch deck:", err)
                setError("Deck not found")
            } finally {
                setLoading(false)
            }
        }

        if (deckId) {
            fetchDeck()
        }
    }, [deckId])

    const handleSubscribeToggle = async (checked: boolean) => {
        try {
            if (checked) {
                await subscribeToDeck(deckId)
            } else {
                await unsubscribeFromDeck(deckId)
            }
            setIsSubscribed(checked)
        } catch (err) {
            console.error("Failed to update subscription:", err)
        }
    }

    const handleDeleteCard = async (cardId: string) => {
        if (!confirm("Are you sure you want to remove this card from the deck?")) return;

        try {
            await removeCardFromDeck(cardId, deckId);
            // Update local state
            if (deck) {
                setDeck({
                    ...deck,
                    cards: deck.cards.filter(c => c.id !== cardId),
                    card_count: deck.card_count - 1
                });
            }
        } catch (err) {
            console.error("Failed to remove card:", err);
            alert("Failed to remove card");
        }
    }

    if (loading) {
        return (
            <div className="h-full flex items-center justify-center">
                <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
        )
    }

    if (error || !deck) {
        return (
            <div className="h-full flex flex-col items-center justify-center gap-4">
                <p className="text-muted-foreground">{error || "Deck not found"}</p>
                <Button variant="outline" onClick={() => router.push("/decks")}>
                    Back to Library
                </Button>
            </div>
        )
    }

    const uiCards = deck.cards.map(mapApiCardToUiCard)
    const masteredCount = uiCards.filter(c => c.isMastered).length
    const coverIcon = deck.is_public ? <FileText className="h-12 w-12" /> : <Lightbulb className="h-12 w-12" />

    // Simplified for now - assuming mastery is mostly 0 for new decks
    const masteryPercentage = deck.card_count > 0 ? Math.round((masteredCount / deck.card_count) * 100) : 0

    return (
        <div className="h-full flex flex-col bg-background">
            {/* Header */}
            <div className="px-8 py-6 border-b bg-card">
                <div className="flex items-center gap-4 mb-4">
                    <Button variant="ghost" size="icon" onClick={() => router.back()}>
                        <ArrowLeft className="h-4 w-4" />
                    </Button>
                    <Link href="/decks" className="text-sm text-muted-foreground hover:text-foreground">
                        Library
                    </Link>
                    <span className="text-muted-foreground">/</span>
                    <span className="text-sm font-medium">{deck.title}</span>
                </div>

                <div className="flex items-start gap-6">
                    {/* Cover */}
                    <div className="w-32 h-32 rounded-xl bg-gradient-to-br from-primary/20 to-background flex items-center justify-center shadow-lg">
                        <div className="text-4xl opacity-40">
                            {coverIcon}
                        </div>
                    </div>

                    {/* Info */}
                    <div className="flex-1">
                        <h1 className="text-2xl font-bold mb-1">{deck.title}</h1>
                        <p className="text-muted-foreground mb-4">{deck.description}</p>

                        <div className="flex items-center gap-6 text-sm text-muted-foreground mb-4">
                            <span>{deck.card_count} cards</span>
                            <span>{masteredCount} mastered</span>
                            {/* <span>Last reviewed: {deck.last_review_at || 'Never'}</span> */}
                        </div>

                        <div className="flex items-center gap-4">
                            <Link href={`/study?deck=${deckId}`}>
                                <Button className="gap-2">
                                    <Play className="h-4 w-4" />
                                    Start Study
                                </Button>
                            </Link>

                            <div className="flex items-center gap-2 bg-muted/50 rounded-full px-4 py-2">
                                <Star className={cn(
                                    "h-4 w-4 transition-colors",
                                    isSubscribed ? "text-yellow-500 fill-yellow-500" : "text-muted-foreground"
                                )} />
                                <span className="text-sm">Subscribe</span>
                                <Switch
                                    checked={isSubscribed}
                                    onCheckedChange={handleSubscribeToggle}
                                />
                            </div>

                            <Button
                                variant={isEditing ? "secondary" : "ghost"}
                                size="icon"
                                onClick={() => setIsEditing(!isEditing)}
                            >
                                <Settings className="h-4 w-4" />
                            </Button>
                            <Button
                                variant="ghost"
                                size="icon"
                                className="text-destructive hover:bg-destructive/10"
                                onClick={async () => {
                                    if (confirm(`Delete "${deck.title}"? This cannot be undone.`)) {
                                        try {
                                            await deleteDeck(deckId)
                                            router.push("/decks")
                                        } catch (err) {
                                            console.error("Failed to delete deck:", err)
                                            alert("Failed to delete deck")
                                        }
                                    }
                                }}
                            >
                                <Trash2 className="h-4 w-4" />
                            </Button>
                        </div>
                    </div>
                </div>

                {/* Progress */}
                <div className="mt-6 max-w-md">
                    <ProgressBar current={masteredCount} total={deck.card_count || 1} />
                </div>
            </div>

            {/* Card List */}
            <div className="flex-1 overflow-y-auto p-8">
                <div className="flex items-center justify-between mb-4">
                    <h2 className="font-semibold">Cards ({deck.cards.length})</h2>
                    <Button variant="ghost" size="sm">
                        <MoreHorizontal className="h-4 w-4" />
                    </Button>
                </div>
                {uiCards.length > 0 ? (
                    <CardList
                        cards={uiCards}
                        onCardClick={(cardId) => {
                            console.log("Card clicked:", cardId)
                        }}
                        onDeleteCard={isEditing ? handleDeleteCard : undefined}
                        isEditing={isEditing}
                    />
                ) : (
                    <div className="text-center py-12 text-muted-foreground">
                        No cards in this deck yet.
                    </div>
                )}
            </div>
        </div>
    )
}
