"use client"

import { useState, useEffect, useCallback, useRef } from "react"
import { useRouter } from "next/navigation"
import { ArrowLeft, Loader2, Coffee, Sparkles } from "lucide-react"
import { GulpCard } from "@/components/study/GulpCard"
import { getGulpFeed, bookmarkCard, unbookmarkCard, submitReview, GulpCard as GulpCardType } from "@/lib/api/study"
import { GulpModeSwitch } from "./_components/GulpModeSwitch"

type GulpMode = 'review' | 'explore' | 'mixed' | 'deep_dive'

export default function GulpPage() {
    const router = useRouter()
    const [cards, setCards] = useState<GulpCardType[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const [currentIndex, setCurrentIndex] = useState(0)
    const [hasMore, setHasMore] = useState(false)
    const [total, setTotal] = useState(0)
    const [mode, setMode] = useState<GulpMode>('mixed')
    const [deepDiveSourceId, setDeepDiveSourceId] = useState<string | null>(null)
    const containerRef = useRef<HTMLDivElement>(null)

    // Load mode from localStorage on mount
    useEffect(() => {
        const savedMode = localStorage.getItem('gulp_mode') as GulpMode
        if (savedMode && ['review', 'explore', 'mixed', 'deep_dive'].includes(savedMode)) {
            setMode(savedMode)
        }
    }, [])

    const fetchFeed = useCallback(async (offset = 0, newMode?: GulpMode) => {
        try {
            setLoading(true)
            const feedMode = newMode || mode
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
    }, [mode])

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

    const handleModeChange = (newMode: GulpMode) => {
        setMode(newMode)
        localStorage.setItem('gulp_mode', newMode)
        setCurrentIndex(0)
        fetchFeed(0, newMode)
    }

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

    const handleSkip = () => {
        const nextEl = containerRef.current?.querySelector(`[data-index="${currentIndex + 1}"]`)
        if (nextEl) {
            nextEl.scrollIntoView({ behavior: "smooth" })
        }
    }

    const handleDeepDive = (sourceMaterialId: string) => {
        setMode('deep_dive')
        setDeepDiveSourceId(sourceMaterialId)
        // TODO: Fetch cards for this source only
    }

    // Empty state
    if (!loading && cards.length === 0) {
        return (
            <div className="h-screen flex flex-col items-center justify-center gap-6 px-8 bg-gradient-to-br from-background via-background to-primary/5">
                <div className="relative">
                    <div className="absolute inset-0 bg-primary/20 blur-3xl rounded-full animate-pulse" />
                    <div className="relative w-24 h-24 rounded-full bg-gradient-to-br from-primary/20 to-primary/10 flex items-center justify-center backdrop-blur-sm border border-primary/20">
                        <Coffee className="h-12 w-12 text-primary" />
                    </div>
                </div>
                <div className="text-center space-y-3 max-w-md">
                    <h2 className="text-3xl font-bold bg-gradient-to-r from-foreground to-foreground/60 bg-clip-text text-transparent">
                        Nothing to gulp yet
                    </h2>
                    <p className="text-muted-foreground leading-relaxed">
                        Subscribe to some decks and start reading papers. Cards will appear here when they're ready for review.
                    </p>
                </div>
                <button
                    onClick={() => router.push("/study")}
                    className="group relative px-8 py-3.5 rounded-2xl bg-primary text-primary-foreground font-semibold hover:shadow-lg hover:shadow-primary/25 transition-all duration-300 hover:-translate-y-0.5"
                >
                    <span className="relative z-10">Go to Learn</span>
                    <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-primary to-primary/80 opacity-0 group-hover:opacity-100 transition-opacity" />
                </button>
            </div>
        )
    }

    return (
        <div className="h-screen w-full flex flex-col bg-gradient-to-br from-background via-background to-primary/5 overflow-hidden">
            {/* Top bar with mode switcher */}
            <div className="shrink-0 flex items-center justify-between px-6 py-4 border-b border-border/30 bg-background/80 backdrop-blur-xl z-10">
                <button
                    onClick={() => router.push("/study")}
                    className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors group"
                >
                    <ArrowLeft className="h-4 w-4 group-hover:-translate-x-1 transition-transform" />
                    <span className="font-medium">Back</span>
                </button>

                <GulpModeSwitch mode={mode} onModeChange={handleModeChange} />

                <div className="flex items-center gap-3">
                    <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary/10 border border-primary/20">
                        <Sparkles className="h-3.5 w-3.5 text-primary" />
                        <span className="text-sm font-bold bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
                            Gulping
                        </span>
                    </div>
                    <span className="text-xs text-muted-foreground font-medium tabular-nums">
                        {currentIndex + 1} / {cards.length}
                    </span>
                </div>
            </div>

            {/* Loading */}
            {loading && cards.length === 0 && (
                <div className="flex-1 flex items-center justify-center">
                    <div className="flex flex-col items-center gap-4">
                        <Loader2 className="h-8 w-8 animate-spin text-primary" />
                        <p className="text-sm text-muted-foreground">Loading your feed...</p>
                    </div>
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
                            onSkip={handleSkip}
                            onDeepDive={handleDeepDive}
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
            <div className="fixed right-6 top-1/2 -translate-y-1/2 flex flex-col gap-2 z-20">
                {cards.slice(Math.max(0, currentIndex - 3), Math.min(cards.length, currentIndex + 4)).map((c, i) => {
                    const realIdx = Math.max(0, currentIndex - 3) + i
                    return (
                        <div
                            key={c.id}
                            className={`rounded-full transition-all duration-300 ${
                                realIdx === currentIndex
                                    ? "w-2 h-8 bg-primary shadow-lg shadow-primary/50"
                                    : "w-2 h-2 bg-muted-foreground/30 hover:bg-muted-foreground/50"
                            }`}
                        />
                    )
                })}
            </div>
        </div>
    )
}
