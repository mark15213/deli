"use client"

import { InboxItem } from "@/components/inbox/InboxItem"
import { SourceCompareDrawer } from "@/components/inbox/SourceCompareDrawer"
import { ImportCardsModal } from "@/components/inbox/ImportCardsModal"
import { useState, useEffect, useCallback } from "react"
import { getPendingBySource, addCardToDeck, removeCardFromDeck, type InboxSourceGroup } from "@/lib/api/inbox"
import { getDecks, createDeck, type Deck } from "@/lib/api/decks"
import { Loader2, X, Upload } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"

type StatusFilter = "all" | "pending" | "active" | "rejected"

const STATUS_TABS: { value: StatusFilter; label: string }[] = [
    { value: "all", label: "All" },
    { value: "pending", label: "Pending" },
    { value: "active", label: "Approved" },
    { value: "rejected", label: "Rejected" },
]

// Simple Create Deck Modal
function CreateDeckModal({ isOpen, onClose, onCreated }: {
    isOpen: boolean
    onClose: () => void
    onCreated: (deck: Deck) => void
}) {
    const [title, setTitle] = useState("")
    const [creating, setCreating] = useState(false)

    if (!isOpen) return null

    const handleCreate = async () => {
        if (!title.trim()) return
        try {
            setCreating(true)
            const newDeck = await createDeck({ title: title.trim() })
            onCreated(newDeck)
            setTitle("")
            onClose()
        } catch (error) {
            console.error("Failed to create deck:", error)
        } finally {
            setCreating(false)
        }
    }

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
            <div className="bg-background border rounded-lg shadow-lg w-full max-w-md p-6">
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-lg font-semibold">Create New Deck</h2>
                    <button onClick={onClose} className="text-muted-foreground hover:text-foreground">
                        <X className="h-5 w-5" />
                    </button>
                </div>
                <input
                    type="text"
                    placeholder="Deck name"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    className="w-full px-3 py-2 border rounded-md mb-4 bg-background"
                    autoFocus
                    onKeyDown={(e) => e.key === "Enter" && handleCreate()}
                />
                <div className="flex justify-end gap-2">
                    <Button variant="outline" onClick={onClose} disabled={creating}>Cancel</Button>
                    <Button onClick={handleCreate} disabled={creating || !title.trim()}>
                        {creating ? <Loader2 className="h-4 w-4 animate-spin" /> : "Create"}
                    </Button>
                </div>
            </div>
        </div>
    )
}

export default function InboxPage() {
    const [items, setItems] = useState<InboxSourceGroup[]>([])
    const [decks, setDecks] = useState<Deck[]>([])
    const [loading, setLoading] = useState(true)
    const [selectedItem, setSelectedItem] = useState<InboxSourceGroup | null>(null)
    const [statusFilter, setStatusFilter] = useState<StatusFilter>("all")
    const [showCreateDeckModal, setShowCreateDeckModal] = useState(false)
    const [showImportModal, setShowImportModal] = useState(false)

    const fetchDecks = useCallback(async () => {
        try {
            const data = await getDecks()
            setDecks(data)
        } catch (error) {
            console.error("Failed to fetch decks:", error)
        }
    }, [])

    const fetchInboxItems = useCallback(async () => {
        try {
            setLoading(true)
            const status = statusFilter === "all" ? undefined : statusFilter
            const data = await getPendingBySource(status)
            setItems(data)
        } catch (error) {
            console.error("Failed to fetch inbox items:", error)
        } finally {
            setLoading(false)
        }
    }, [statusFilter])

    useEffect(() => {
        fetchDecks()
    }, [fetchDecks])

    useEffect(() => {
        fetchInboxItems()
    }, [fetchInboxItems])

    const handleItemProcessed = () => {
        // Refresh the list after approving/rejecting
        fetchInboxItems()
        setSelectedItem(null)
    }

    // Helper to get common deck IDs if all cards are in same deck
    const getCommonDeckIds = (item: InboxSourceGroup) => {
        if (item.cards.length === 0) return []

        // Find deck ids present in ALL cards (intersection)
        const initialDecks = new Set(item.cards[0].deck_ids)

        for (const card of item.cards) {
            const cardDecks = new Set(card.deck_ids)
            for (const deckId of Array.from(initialDecks)) {
                if (!cardDecks.has(deckId)) {
                    initialDecks.delete(deckId)
                }
            }
        }
        return Array.from(initialDecks)
    }

    const handleToggleDeck = async (sourceId: string, deckId: string) => {
        const source = items.find(i => (i.source_id || i.source_title) === sourceId)
        if (!source) return

        // Determine target state based on common decks
        const commonDecks = getCommonDeckIds(source)
        const isCurrentlyIn = commonDecks.includes(deckId)

        // Apply logic to ALL cards (pending or active)
        for (const card of source.cards) {
            try {
                if (isCurrentlyIn) {
                    // Remove if present
                    if (card.deck_ids.includes(deckId)) {
                        await removeCardFromDeck(card.id, deckId)
                    }
                } else {
                    // Add if missing
                    if (!card.deck_ids.includes(deckId)) {
                        await addCardToDeck(card.id, deckId)
                    }
                }
            } catch (error) {
                console.error(`Failed to toggle deck ${deckId} for card ${card.id}`, error)
            }
        }

        // Refresh
        fetchInboxItems()
    }

    const handleDeckCreated = (newDeck: Deck) => {
        setDecks(prev => [...prev, newDeck])
    }

    // Map API source type to UI source type
    const getSourceType = (sourceUrl?: string): "twitter" | "article" | "podcast" | "note" => {
        if (!sourceUrl) return "article"
        if (sourceUrl.includes("twitter.com") || sourceUrl.includes("x.com")) return "twitter"
        if (sourceUrl.includes("huberman") || sourceUrl.includes("podcast")) return "podcast"
        if (sourceUrl.includes("notion")) return "note"
        return "article"
    }

    // Convert decks to the format InboxItem expects
    const deckOptions = decks.map(d => ({
        id: d.id,
        name: d.title,
        cardCount: d.card_count
    }))

    const totalCards = items.reduce((sum, item) => sum + item.total_count, 0)

    return (
        <div className="flex h-full bg-background relative">
            {/* List Section */}
            <div className="flex-1 flex flex-col min-w-0">
                <div className="px-8 py-6 border-b bg-card">
                    <div className="flex items-center justify-between mb-4">
                        <div>
                            <h1 className="text-2xl font-bold tracking-tight">Inbox</h1>
                            <p className="text-muted-foreground mt-1">Review and organize new cards</p>
                        </div>
                        <div className="flex items-center gap-4">
                            <Button onClick={() => setShowImportModal(true)} variant="outline" className="gap-2">
                                <Upload className="h-4 w-4" />
                                Import Cards
                            </Button>
                            <div className="text-sm text-muted-foreground">
                                <span className="font-medium text-foreground">{totalCards}</span> items
                            </div>
                        </div>
                    </div>

                    {/* Status Filter Tabs */}
                    <div className="flex gap-1 bg-muted/50 p-1 rounded-lg w-fit">
                        {STATUS_TABS.map(tab => (
                            <button
                                key={tab.value}
                                onClick={() => setStatusFilter(tab.value)}
                                className={cn(
                                    "px-4 py-1.5 text-sm font-medium rounded-md transition-all",
                                    statusFilter === tab.value
                                        ? "bg-background text-foreground shadow-sm"
                                        : "text-muted-foreground hover:text-foreground"
                                )}
                            >
                                {tab.label}
                            </button>
                        ))}
                    </div>
                </div>

                <div className="flex-1 overflow-y-auto">
                    {loading ? (
                        <div className="flex items-center justify-center h-64">
                            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
                        </div>
                    ) : items.length === 0 ? (
                        <div className="flex flex-col items-center justify-center h-64 text-center p-8">
                            <div className="text-5xl mb-4">📭</div>
                            <p className="text-muted-foreground">No {statusFilter === "all" ? "" : statusFilter} items</p>
                            <p className="text-sm text-muted-foreground/70 mt-1">
                                {statusFilter === "pending"
                                    ? "All items have been reviewed!"
                                    : "New content will appear here when sources are processed"}
                            </p>
                        </div>
                    ) : (
                        items.map(item => (
                            <InboxItem
                                key={item.source_id || item.source_title}
                                id={item.source_id || item.source_title}
                                source={item.source_title}
                                sourceType={getSourceType(item.source_url)}
                                title={item.source_title}
                                summary={`${item.notes_count} notes, ${item.flashcards_count} flashcards, ${item.quizzes_count} quizzes`}
                                generatedContent={{
                                    notes: item.notes_count,
                                    flashcards: item.flashcards_count,
                                    quizzes: item.quizzes_count
                                }}
                                timestamp={new Date(item.created_at).toLocaleDateString()}
                                onClick={() => setSelectedItem(item)}
                                selected={selectedItem?.source_id === item.source_id}
                                decks={deckOptions}
                                onToggleDeck={handleToggleDeck}
                                onCreateDeck={() => setShowCreateDeckModal(true)}
                                currentDeckIds={getCommonDeckIds(item)}
                            />
                        ))
                    )}
                </div>
            </div>

            {/* Split Drawer */}
            <SourceCompareDrawer
                isOpen={!!selectedItem}
                onClose={() => setSelectedItem(null)}
                item={selectedItem}
                onProcessed={handleItemProcessed}
            />

            {/* Create Deck Modal */}
            <CreateDeckModal
                isOpen={showCreateDeckModal}
                onClose={() => setShowCreateDeckModal(false)}
                onCreated={handleDeckCreated}
            />

            {/* Import Cards Modal */}
            <ImportCardsModal
                isOpen={showImportModal}
                onClose={() => setShowImportModal(false)}
                onSuccess={fetchInboxItems}
            />
        </div>
    )
}
