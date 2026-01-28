"use client"

import { DeckList } from "@/components/decks/DeckList"
import { Button } from "@/components/ui/button"
import { Plus, Search, SlidersHorizontal, Loader2 } from "lucide-react"
import { Input } from "@/components/ui/input"
import { useState, useEffect } from "react"
import { getDecks, subscribeToDeck, unsubscribeFromDeck, type Deck } from "@/lib/api/decks"

export default function DecksPage() {
    const [decks, setDecks] = useState<Deck[]>([])
    const [loading, setLoading] = useState(true)
    const [searchQuery, setSearchQuery] = useState("")
    const [showSubscribedOnly, setShowSubscribedOnly] = useState(false)

    useEffect(() => {
        fetchDecks()
    }, [])

    const fetchDecks = async () => {
        try {
            setLoading(true)
            const data = await getDecks()
            setDecks(data)
        } catch (error) {
            console.error("Failed to fetch decks:", error)
        } finally {
            setLoading(false)
        }
    }

    const handleSubscribeChange = async (deckId: string, subscribed: boolean) => {
        try {
            if (subscribed) {
                await subscribeToDeck(deckId)
            } else {
                await unsubscribeFromDeck(deckId)
            }
            // Update local state
            setDecks(decks.map(d =>
                d.id === deckId ? { ...d, is_subscribed: subscribed } : d
            ))
        } catch (error) {
            console.error("Failed to update subscription:", error)
        }
    }

    // Map API response to component format
    const mappedDecks = decks.map(deck => ({
        id: deck.id,
        title: deck.title,
        description: deck.description,
        coverIcon: deck.is_public ? "code" as const : "lightbulb" as const,
        cardCount: deck.card_count,
        masteryPercentage: deck.mastery_percent,
        isSubscribed: deck.is_subscribed,
        lastReviewAt: deck.last_review_at,
    }))

    const filteredDecks = mappedDecks.filter(deck => {
        const matchesSearch = deck.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
            deck.description?.toLowerCase().includes(searchQuery.toLowerCase())
        const matchesSubscribed = showSubscribedOnly ? deck.isSubscribed : true
        return matchesSearch && matchesSubscribed
    })

    const subscribedCount = mappedDecks.filter(d => d.isSubscribed).length
    const totalCards = mappedDecks.reduce((sum, d) => sum + d.cardCount, 0)

    if (loading) {
        return (
            <div className="h-full flex items-center justify-center">
                <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
        )
    }

    return (
        <div className="h-full flex flex-col bg-background">
            {/* Header */}
            <div className="px-8 py-6 border-b bg-card">
                <div className="flex items-center justify-between mb-4">
                    <div>
                        <h1 className="text-2xl font-bold tracking-tight">My Library</h1>
                        <p className="text-muted-foreground mt-1">
                            {decks.length} decks • {totalCards} cards • {subscribedCount} subscribed
                        </p>
                    </div>
                    <Button className="gap-2">
                        <Plus className="h-4 w-4" />
                        New Deck
                    </Button>
                </div>

                {/* Search & Filters */}
                <div className="flex items-center gap-3">
                    <div className="relative flex-1 max-w-md">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                        <Input
                            placeholder="Search decks..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="pl-10"
                        />
                    </div>
                    <Button
                        variant={showSubscribedOnly ? "default" : "outline"}
                        size="sm"
                        onClick={() => setShowSubscribedOnly(!showSubscribedOnly)}
                    >
                        Subscribed Only
                    </Button>
                    <Button variant="ghost" size="icon">
                        <SlidersHorizontal className="h-4 w-4" />
                    </Button>
                </div>
            </div>

            {/* Deck Grid */}
            <div className="flex-1 overflow-y-auto p-8">
                {filteredDecks.length > 0 ? (
                    <DeckList
                        decks={filteredDecks}
                        onSubscribeChange={handleSubscribeChange}
                    />
                ) : (
                    <div className="flex flex-col items-center justify-center h-64 text-center">
                        <p className="text-muted-foreground">No decks found</p>
                        <p className="text-sm text-muted-foreground/70 mt-1">
                            Try adjusting your search or filters
                        </p>
                    </div>
                )}
            </div>
        </div>
    )
}

