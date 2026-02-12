"use client"

import { useState, useEffect, useCallback, useRef } from "react"
import { useRouter } from "next/navigation"
import { ArrowLeft, Loader2, Coffee } from "lucide-react"
import { GulpCard } from "@/components/study/GulpCard"
import { getGulpFeed, bookmarkCard, unbookmarkCard, submitReview, GulpCard as GulpCardType } from "@/lib/api/study"

export default function GulpPage() {
    const router = useRouter()
    const [cards, setCards] = useState<GulpCardType[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const [currentIndex, setCurrentIndex] = useState(0)
    const [hasMore, setHasMore] = useState(false)
    const [total, setTotal] = useState(0)
    const containerRef = useRef<HTMLDivElement>(null)

    const fetchFeed = useCallback(async (offset = 0) => {
        try {
            setLoading(true)
            const feed = await getGulpFeed(30, offset)
            if (offset === 0) {
                setCards(feed.cards)
            } else {
                setCards(prev => [...prev, ...feed.cards])
            }
            setTotal(feed.total)
            setHasMore(feed.has_more)
        } catch (err) {
            setError("Failed to load feed")
            console.error(err)
        } finally {
            setLoading(false)
        }
    }, [])

    useEffect(() => {
        fetchFeed()
    }, [fetchFeed])

    // Snap scroll observer
    useEffect(() => {
        const container = containerRef.current
        if (!container) return

        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        const idx = Number(entry.target.getAttribute("data-index"))
                        if (!isNaN(idx)) {
                            setCurrentIndex(idx)
                            // Load more when near the end
                            if (idx >= cards.length - 5 && hasMore) {
                                fetchFeed(cards.length)
                            }
                        }
                    }
                })
            },
            { root: container, threshold: 0.6 }
        )

        const items = container.querySelectorAll(".gulp-snap-item")
        items.forEach((item) => observer.observe(item))

        return () => observer.disconnect()
    }, [cards, hasMore, fetchFeed])

    const handleBookmark = async (cardId: string) => {
        try {
            await bookmarkCard(cardId)
            setCards(prev => prev.map(c => c.id === cardId ? { ...c, is_bookmarked: true } : c))
        } catch (err) { console.error(err) }
    }

    const handleUnbookmark = async (cardId: string) => {
        try {
            await unbookmarkCard(cardId)
            setCards(prev => prev.map(c => c.id === cardId ? { ...c, is_bookmarked: false } : c))
        } catch (err) { console.error(err) }
    }

    const handleMarkLearned = async (cardId: string) => {
        try {
            await submitReview(cardId, 3) // 3 = GOOD
        } catch (err) { console.error(err) }
        // Scroll to next card
        const nextEl = containerRef.current?.querySelector(`[data-index="${currentIndex + 1}"]`)
        if (nextEl) {
            nextEl.scrollIntoView({ behavior: "smooth" })
        }
    }

    // Empty state
    if (!loading && cards.length === 0) {
        return (
            <div className="h-screen flex flex-col items-center justify-center gap-6 px-8 bg-background">
                <div className="w-20 h-20 rounded-full bg-muted/50 flex items-center justify-center">
                    <Coffee className="h-10 w-10 text-muted-foreground" />
                </div>
                <div className="text-center space-y-2">
                    <h2 className="text-2xl font-bold">Nothing to gulp yet</h2>
                    <p className="text-muted-foreground max-w-sm">
                        Subscribe to some decks and start reading papers. Cards will appear here when they&rsquo;re ready for review.
                    </p>
                </div>
                <button
                    onClick={() => router.push("/study")}
                    className="px-6 py-2.5 rounded-xl bg-primary text-primary-foreground font-medium hover:bg-primary/90 transition-all"
                >
                    Go to Learn
                </button>
            </div>
        )
    }

    return (
        <div className="h-screen w-full flex flex-col bg-background overflow-hidden">
            {/* Top bar */}
            <div className="shrink-0 flex items-center justify-between px-4 py-3 border-b border-border/30 bg-background/80 backdrop-blur-md z-10">
                <button
                    onClick={() => router.push("/study")}
                    className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
                >
                    <ArrowLeft className="h-4 w-4" />
                    Back
                </button>
                <div className="flex items-center gap-2">
                    <span className="text-sm font-bold bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
                        🥤 Gulping
                    </span>
                    <span className="text-xs text-muted-foreground">
                        {currentIndex + 1} / {cards.length}
                    </span>
                </div>
                <div className="w-16" /> {/* Spacer for centering */}
            </div>

            {/* Loading */}
            {loading && cards.length === 0 && (
                <div className="flex-1 flex items-center justify-center">
                    <Loader2 className="h-8 w-8 animate-spin text-primary" />
                </div>
            )}

            {/* Card feed - vertical snap scroll */}
            <div
                ref={containerRef}
                className="flex-1 overflow-y-auto gulp-container"
            >
                {cards.map((card, idx) => (
                    <div
                        key={card.id}
                        data-index={idx}
                        className="gulp-snap-item h-full w-full"
                        style={{ scrollSnapAlign: "start" }}
                    >
                        <GulpCard
                            card={card}
                            isActive={currentIndex === idx}
                            onBookmark={handleBookmark}
                            onUnbookmark={handleUnbookmark}
                            onMarkLearned={handleMarkLearned}
                        />
                    </div>
                ))}

                {/* Loading more indicator */}
                {hasMore && (
                    <div className="flex items-center justify-center py-8">
                        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
                    </div>
                )}
            </div>

            {/* Progress dots */}
            <div className="fixed right-3 top-1/2 -translate-y-1/2 flex flex-col gap-1.5 z-20">
                {cards.slice(Math.max(0, currentIndex - 3), Math.min(cards.length, currentIndex + 4)).map((c, i) => {
                    const realIdx = Math.max(0, currentIndex - 3) + i
                    return (
                        <div
                            key={c.id}
                            className={`w-1.5 rounded-full transition-all duration-300 ${realIdx === currentIndex
                                ? "h-6 bg-primary"
                                : "h-1.5 bg-muted-foreground/30"
                                }`}
                        />
                    )
                })}
            </div>
        </div>
    )
}
