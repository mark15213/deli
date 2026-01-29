"use client"

import { DetailPanel } from "@/components/layout/DetailPanel"
import { Button } from "@/components/ui/button"
import { X, Check, Loader2, FileText, HelpCircle, StickyNote } from "lucide-react"
import { useState } from "react"
import { bulkApprove, bulkReject, type InboxSourceGroup, type InboxCardPreview } from "@/lib/api/inbox"
import { cn } from "@/lib/utils"

interface SourceCompareDrawerProps {
    isOpen: boolean
    onClose: () => void
    item: InboxSourceGroup | null
    onProcessed?: () => void
}

export function SourceCompareDrawer({ isOpen, onClose, item, onProcessed }: SourceCompareDrawerProps) {
    const [processing, setProcessing] = useState(false)
    const [selectedCards, setSelectedCards] = useState<Set<string>>(new Set())
    const [cachedItem, setCachedItem] = useState<InboxSourceGroup | null>(item)

    // Cache the item so we can display it while closing animation plays
    if (item && item !== cachedItem) {
        setCachedItem(item)
    }

    const displayItem = item || cachedItem

    // Compute derived state safely
    const pendingCards = displayItem?.cards.filter(c => c.status === "pending") || []
    const pendingCardIds = pendingCards.map(c => c.id)
    const allPendingSelected = selectedCards.size === pendingCardIds.length && pendingCardIds.length > 0
    const hasPendingCards = pendingCards.length > 0

    const toggleCard = (cardId: string) => {
        if (!displayItem) return
        const card = displayItem.cards.find(c => c.id === cardId)
        if (card?.status !== "pending") return // Can't select non-pending cards

        const newSet = new Set(selectedCards)
        if (newSet.has(cardId)) {
            newSet.delete(cardId)
        } else {
            newSet.add(cardId)
        }
        setSelectedCards(newSet)
    }

    const toggleAll = () => {
        if (allPendingSelected) {
            setSelectedCards(new Set())
        } else {
            setSelectedCards(new Set(pendingCardIds))
        }
    }

    const handleApprove = async () => {
        const idsToApprove = selectedCards.size > 0 ? Array.from(selectedCards) : pendingCardIds
        if (idsToApprove.length === 0) return

        try {
            setProcessing(true)
            await bulkApprove(idsToApprove)
            onProcessed?.()
        } catch (error) {
            console.error("Failed to approve cards:", error)
        } finally {
            setProcessing(false)
        }
    }

    const handleReject = async () => {
        const idsToReject = selectedCards.size > 0 ? Array.from(selectedCards) : pendingCardIds
        if (idsToReject.length === 0) return

        try {
            setProcessing(true)
            await bulkReject(idsToReject)
            onProcessed?.()
        } catch (error) {
            console.error("Failed to reject cards:", error)
        } finally {
            setProcessing(false)
        }
    }

    const getCardIcon = (type: string) => {
        switch (type) {
            case "note": return <StickyNote className="h-4 w-4 text-blue-500" />
            case "flashcard": return <FileText className="h-4 w-4 text-green-500" />
            default: return <HelpCircle className="h-4 w-4 text-purple-500" />
        }
    }

    const getStatusBadge = (status: string) => {
        switch (status) {
            case "pending":
                return <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400">Pending</span>
            case "active":
                return <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400">Approved</span>
            case "rejected":
                return <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400">Rejected</span>
            default:
                return null
        }
    }

    return (
        <DetailPanel
            isOpen={isOpen}
            onClose={onClose}
            className="w-[600px] border-l shadow-2xl flex flex-col p-0 bg-background"
        >
            {displayItem && (
                <>
                    {/* Header */}
                    <div className="flex items-center justify-between px-6 py-4 border-b bg-card">
                        <div>
                            <h2 className="text-lg font-semibold">{displayItem.source_title}</h2>
                            <p className="text-sm text-muted-foreground">
                                {displayItem.total_count} cards ({pendingCards.length} pending)
                            </p>
                        </div>
                        <div className="flex items-center gap-2">
                            <Button
                                variant="outline"
                                size="sm"
                                onClick={handleReject}
                                disabled={processing || !hasPendingCards}
                            >
                                {processing ? <Loader2 className="h-4 w-4 animate-spin" /> : <X className="h-4 w-4" />}
                                Reject {selectedCards.size > 0 ? `(${selectedCards.size})` : `All (${pendingCards.length})`}
                            </Button>
                            <Button
                                size="sm"
                                className="gap-2"
                                onClick={handleApprove}
                                disabled={processing || !hasPendingCards}
                            >
                                {processing ? <Loader2 className="h-4 w-4 animate-spin" /> : <Check className="h-4 w-4" />}
                                Approve {selectedCards.size > 0 ? `(${selectedCards.size})` : `All (${pendingCards.length})`}
                            </Button>
                        </div>
                    </div>

                    {/* Select All (only if pending cards exist) */}
                    {hasPendingCards && (
                        <div className="px-6 py-3 border-b bg-muted/30 flex items-center gap-3">
                            <input
                                type="checkbox"
                                checked={allPendingSelected}
                                onChange={toggleAll}
                                className="h-4 w-4 rounded"
                            />
                            <span className="text-sm text-muted-foreground">
                                {allPendingSelected ? 'Deselect all pending' : `Select all pending (${pendingCards.length})`}
                            </span>
                        </div>
                    )}

                    {/* Cards List */}
                    <div className="flex-1 overflow-y-auto p-6">
                        <div className="space-y-3">
                            {displayItem.cards.map((card) => {
                                const isPending = card.status === "pending"
                                const isSelected = selectedCards.has(card.id)

                                return (
                                    <div
                                        key={card.id}
                                        className={cn(
                                            "border rounded-lg p-4 text-sm bg-card transition-colors",
                                            isPending && "hover:border-primary/50 cursor-pointer",
                                            isSelected && "border-primary ring-1 ring-primary/20",
                                            !isPending && "opacity-60"
                                        )}
                                        onClick={() => isPending && toggleCard(card.id)}
                                    >
                                        <div className="flex items-start gap-3">
                                            {isPending && (
                                                <input
                                                    type="checkbox"
                                                    checked={isSelected}
                                                    onChange={() => toggleCard(card.id)}
                                                    onClick={(e) => e.stopPropagation()}
                                                    className="mt-1 h-4 w-4 rounded"
                                                />
                                            )}
                                            <div className="flex-1">
                                                <div className="flex items-center gap-2 mb-2">
                                                    {getCardIcon(card.type)}
                                                    <span className="text-xs uppercase text-muted-foreground font-medium">
                                                        {card.type}
                                                    </span>
                                                    {getStatusBadge(card.status)}
                                                </div>
                                                <p className="text-foreground">{card.question}</p>
                                            </div>
                                        </div>
                                    </div>
                                )
                            })}
                        </div>
                    </div>
                </>
            )}
        </DetailPanel>
    )
}
