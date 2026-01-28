"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import Link from "next/link"
import {
    BookOpen,
    Brain,
    Flame,
    Inbox,
    Library,
    Plus,
    TrendingUp,
    Zap,
    Clock,
    Target,
    Award,
    ChevronRight,
    FileText,
    Sparkles,
} from "lucide-react"
import { getStudyStats, type StudyStats } from "@/lib/api/study"
import { getPendingBySource, type InboxSourceGroup } from "@/lib/api/inbox"
import { getDecks, type Deck } from "@/lib/api/decks"
import { getSources, type Source } from "@/lib/api/sources"
import { cn } from "@/lib/utils"

// Stat Card Component
function StatCard({
    icon: Icon,
    label,
    value,
    subtext,
    trend,
    color = "blue",
}: {
    icon: React.ElementType
    label: string
    value: string | number
    subtext?: string
    trend?: { value: number; positive: boolean }
    color?: "blue" | "green" | "orange" | "purple" | "pink"
}) {
    const colorClasses = {
        blue: "bg-blue-500/10 text-blue-500",
        green: "bg-green-500/10 text-green-500",
        orange: "bg-orange-500/10 text-orange-500",
        purple: "bg-purple-500/10 text-purple-500",
        pink: "bg-pink-500/10 text-pink-500",
    }

    return (
        <div className="bg-card border rounded-xl p-5 hover:shadow-lg transition-shadow">
            <div className="flex items-start justify-between">
                <div className={cn("p-2.5 rounded-lg", colorClasses[color])}>
                    <Icon className="h-5 w-5" />
                </div>
                {trend && (
                    <div className={cn(
                        "flex items-center gap-1 text-xs font-medium px-2 py-1 rounded-full",
                        trend.positive ? "bg-green-500/10 text-green-500" : "bg-red-500/10 text-red-500"
                    )}>
                        <TrendingUp className={cn("h-3 w-3", !trend.positive && "rotate-180")} />
                        {trend.value}%
                    </div>
                )}
            </div>
            <div className="mt-4">
                <p className="text-3xl font-bold tracking-tight">{value}</p>
                <p className="text-sm text-muted-foreground mt-1">{label}</p>
                {subtext && <p className="text-xs text-muted-foreground/70 mt-0.5">{subtext}</p>}
            </div>
        </div>
    )
}

// Quick Action Card
function QuickAction({
    icon: Icon,
    title,
    description,
    href,
    color,
}: {
    icon: React.ElementType
    title: string
    description: string
    href: string
    color: string
}) {
    return (
        <Link href={href}>
            <div className="group bg-card border rounded-xl p-4 hover:shadow-lg hover:border-primary/50 transition-all cursor-pointer">
                <div className="flex items-center gap-4">
                    <div className={cn("p-3 rounded-lg", color)}>
                        <Icon className="h-5 w-5" />
                    </div>
                    <div className="flex-1">
                        <h3 className="font-semibold group-hover:text-primary transition-colors">{title}</h3>
                        <p className="text-sm text-muted-foreground">{description}</p>
                    </div>
                    <ChevronRight className="h-5 w-5 text-muted-foreground group-hover:text-primary group-hover:translate-x-1 transition-all" />
                </div>
            </div>
        </Link>
    )
}

// Recent Activity Item
function ActivityItem({
    icon: Icon,
    title,
    time,
    type,
}: {
    icon: React.ElementType
    title: string
    time: string
    type: "study" | "create" | "sync"
}) {
    const typeColors = {
        study: "bg-blue-500/10 text-blue-500",
        create: "bg-green-500/10 text-green-500",
        sync: "bg-orange-500/10 text-orange-500",
    }

    return (
        <div className="flex items-center gap-3 py-3 border-b last:border-0">
            <div className={cn("p-2 rounded-lg", typeColors[type])}>
                <Icon className="h-4 w-4" />
            </div>
            <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{title}</p>
                <p className="text-xs text-muted-foreground">{time}</p>
            </div>
        </div>
    )
}

export default function DashboardPage() {
    const [stats, setStats] = useState<StudyStats | null>(null)
    const [pendingItems, setPendingItems] = useState<InboxSourceGroup[]>([])
    const [decks, setDecks] = useState<Deck[]>([])
    const [sources, setSources] = useState<Source[]>([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        async function fetchData() {
            try {
                const [statsData, pendingData, decksData, sourcesData] = await Promise.all([
                    getStudyStats().catch(() => null),
                    getPendingBySource("pending").catch(() => []),
                    getDecks().catch(() => []),
                    getSources().catch(() => []),
                ])
                setStats(statsData)
                setPendingItems(pendingData)
                setDecks(decksData)
                setSources(sourcesData)
            } catch (error) {
                console.error("Failed to fetch dashboard data:", error)
            } finally {
                setLoading(false)
            }
        }
        fetchData()
    }, [])

    const totalPendingCards = pendingItems.reduce((sum, item) => sum + item.total_count, 0)
    const totalCards = decks.reduce((sum, deck) => sum + deck.card_count, 0)

    // Calculate greeting based on time
    const hour = new Date().getHours()
    const greeting = hour < 12 ? "Good morning" : hour < 18 ? "Good afternoon" : "Good evening"

    if (loading) {
        return (
            <div className="flex items-center justify-center h-full">
                <div className="animate-pulse flex flex-col items-center gap-4">
                    <div className="h-12 w-12 rounded-full bg-muted"></div>
                    <div className="h-4 w-32 rounded bg-muted"></div>
                </div>
            </div>
        )
    }

    return (
        <div className="min-h-full bg-gradient-to-br from-background via-background to-muted/20">
            <div className="max-w-7xl mx-auto px-6 py-8">
                {/* Header */}
                <header className="mb-8">
                    <div className="flex items-center justify-between">
                        <div>
                            <h1 className="text-3xl font-bold tracking-tight">
                                {greeting}! 👋
                            </h1>
                            <p className="text-muted-foreground mt-1">
                                Here's your learning overview for today
                            </p>
                        </div>
                        <Link href="/study">
                            <Button size="lg" className="gap-2 shadow-lg hover:shadow-xl transition-shadow">
                                <Zap className="h-5 w-5" />
                                Start Studying
                            </Button>
                        </Link>
                    </div>
                </header>

                {/* Stats Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                    <StatCard
                        icon={Target}
                        label="Today's Progress"
                        value={stats?.today_reviewed || 0}
                        subtext={`${stats?.today_remaining || 0} cards remaining`}
                        color="blue"
                    />
                    <StatCard
                        icon={Flame}
                        label="Study Streak"
                        value={`${stats?.streak_days || 0} days`}
                        subtext="Keep it going!"
                        color="orange"
                    />
                    <StatCard
                        icon={Inbox}
                        label="Pending Review"
                        value={totalPendingCards}
                        subtext={`From ${pendingItems.length} sources`}
                        color="purple"
                    />
                    <StatCard
                        icon={Award}
                        label="Mastered Cards"
                        value={stats?.total_mastered || 0}
                        subtext={`of ${stats?.total_cards || totalCards} total`}
                        color="green"
                    />
                </div>

                {/* Main Content Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Left Column - Quick Actions & Decks */}
                    <div className="lg:col-span-2 space-y-6">
                        {/* Quick Actions */}
                        <section>
                            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                                <Sparkles className="h-5 w-5 text-primary" />
                                Quick Actions
                            </h2>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                                <QuickAction
                                    icon={Brain}
                                    title="Start Study Session"
                                    description={`${stats?.today_remaining || 0} cards due today`}
                                    href="/study"
                                    color="bg-blue-500/10 text-blue-500"
                                />
                                <QuickAction
                                    icon={Inbox}
                                    title="Review Inbox"
                                    description={`${totalPendingCards} pending items`}
                                    href="/inbox"
                                    color="bg-purple-500/10 text-purple-500"
                                />
                                <QuickAction
                                    icon={Library}
                                    title="Browse Library"
                                    description={`${decks.length} decks, ${totalCards} cards`}
                                    href="/decks"
                                    color="bg-green-500/10 text-green-500"
                                />
                                <QuickAction
                                    icon={Plus}
                                    title="Add New Source"
                                    description="Import from Twitter, Notion, etc."
                                    href="/sources"
                                    color="bg-orange-500/10 text-orange-500"
                                />
                            </div>
                        </section>

                        {/* Your Decks */}
                        <section>
                            <div className="flex items-center justify-between mb-4">
                                <h2 className="text-lg font-semibold flex items-center gap-2">
                                    <BookOpen className="h-5 w-5 text-primary" />
                                    Your Decks
                                </h2>
                                <Link href="/decks">
                                    <Button variant="ghost" size="sm" className="gap-1 text-muted-foreground">
                                        View all <ChevronRight className="h-4 w-4" />
                                    </Button>
                                </Link>
                            </div>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                                {decks.slice(0, 4).map((deck) => (
                                    <Link key={deck.id} href={`/decks/${deck.id}`}>
                                        <div className="bg-card border rounded-xl p-4 hover:shadow-md hover:border-primary/50 transition-all group">
                                            <div className="flex items-start justify-between">
                                                <div>
                                                    <h3 className="font-semibold group-hover:text-primary transition-colors">
                                                        {deck.title}
                                                    </h3>
                                                    <p className="text-sm text-muted-foreground mt-1">
                                                        {deck.card_count} cards
                                                    </p>
                                                </div>
                                                <div className="flex items-center gap-1.5">
                                                    <div className="h-2 w-16 bg-muted rounded-full overflow-hidden">
                                                        <div
                                                            className="h-full bg-primary rounded-full transition-all"
                                                            style={{ width: `${deck.mastery_percent}%` }}
                                                        />
                                                    </div>
                                                    <span className="text-xs text-muted-foreground">
                                                        {Math.round(deck.mastery_percent)}%
                                                    </span>
                                                </div>
                                            </div>
                                        </div>
                                    </Link>
                                ))}
                                {decks.length === 0 && (
                                    <div className="col-span-2 bg-muted/30 border border-dashed rounded-xl p-8 text-center">
                                        <BookOpen className="h-10 w-10 mx-auto text-muted-foreground/50 mb-3" />
                                        <p className="text-muted-foreground">No decks yet</p>
                                        <p className="text-sm text-muted-foreground/70 mt-1">
                                            Create your first deck to start learning
                                        </p>
                                    </div>
                                )}
                            </div>
                        </section>
                    </div>

                    {/* Right Column - Activity & Sources */}
                    <div className="space-y-6">
                        {/* Recent Activity */}
                        <section className="bg-card border rounded-xl p-5">
                            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                                <Clock className="h-5 w-5 text-primary" />
                                Recent Activity
                            </h2>
                            <div className="space-y-1">
                                {stats && stats.today_reviewed > 0 && (
                                    <ActivityItem
                                        icon={Brain}
                                        title={`Reviewed ${stats.today_reviewed} cards today`}
                                        time="Today"
                                        type="study"
                                    />
                                )}
                                {pendingItems.slice(0, 3).map((item, idx) => (
                                    <ActivityItem
                                        key={item.source_id || idx}
                                        icon={FileText}
                                        title={`${item.total_count} new cards from ${item.source_title}`}
                                        time={new Date(item.created_at).toLocaleDateString()}
                                        type="sync"
                                    />
                                ))}
                                {(!stats || stats.today_reviewed === 0) && pendingItems.length === 0 && (
                                    <p className="text-sm text-muted-foreground text-center py-4">
                                        No recent activity
                                    </p>
                                )}
                            </div>
                        </section>

                        {/* Connected Sources */}
                        <section className="bg-card border rounded-xl p-5">
                            <div className="flex items-center justify-between mb-4">
                                <h2 className="text-lg font-semibold flex items-center gap-2">
                                    <Zap className="h-5 w-5 text-primary" />
                                    Sources
                                </h2>
                                <Link href="/sources">
                                    <Button variant="ghost" size="sm" className="gap-1 text-muted-foreground">
                                        Manage <ChevronRight className="h-4 w-4" />
                                    </Button>
                                </Link>
                            </div>
                            <div className="space-y-2">
                                {sources.slice(0, 5).map((source) => (
                                    <div
                                        key={source.id}
                                        className="flex items-center gap-3 p-2 rounded-lg hover:bg-muted/50 transition-colors"
                                    >
                                        <div className={cn(
                                            "w-2 h-2 rounded-full",
                                            source.status === "ACTIVE" ? "bg-green-500" : "bg-gray-400"
                                        )} />
                                        <span className="text-sm font-medium flex-1 truncate">{source.name}</span>
                                        <span className="text-xs text-muted-foreground">{source.type}</span>
                                    </div>
                                ))}
                                {sources.length === 0 && (
                                    <div className="text-center py-4">
                                        <p className="text-sm text-muted-foreground">No sources connected</p>
                                        <Link href="/sources">
                                            <Button variant="link" size="sm" className="mt-1">
                                                Connect a source
                                            </Button>
                                        </Link>
                                    </div>
                                )}
                            </div>
                        </section>
                    </div>
                </div>
            </div>
        </div>
    )
}
