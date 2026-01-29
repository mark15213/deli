"use client"

import { useState } from "react"
import { cn } from "@/lib/utils"
import { Switch } from "@/components/ui/switch"
import { ProgressBar } from "@/components/shared/ProgressBar"
import { FileText, RotateCw, HelpCircle, Clock, Star } from "lucide-react"
import Link from "next/link"

interface DeckCardProps {
    id: string
    title: string
    description?: string
    coverImage?: string
    coverIcon?: React.ReactNode
    cardCount: number
    lastReviewedAt?: string
    masteryPercentage: number
    isSubscribed: boolean
    onSubscribeChange?: (subscribed: boolean) => void
}

export function DeckCard({
    id,
    title,
    description,
    coverImage,
    coverIcon,
    cardCount,
    lastReviewedAt,
    masteryPercentage,
    isSubscribed,
    onSubscribeChange
}: DeckCardProps) {
    const [subscribed, setSubscribed] = useState(isSubscribed)

    const handleSubscribeToggle = () => {
        const newValue = !subscribed
        setSubscribed(newValue)
        onSubscribeChange?.(newValue)
    }

    return (
        <Link href={`/decks/${id}`} className="block">
            <div className={cn(
                "group relative bg-card border rounded-xl overflow-hidden transition-all duration-300",
                "hover:shadow-lg hover:border-primary/30 hover:-translate-y-1",
                subscribed && "ring-2 ring-primary/20"
            )}>
                {/* Cover Image / Icon */}
                <div className="relative h-32 bg-gradient-to-br from-primary/20 via-primary/10 to-background flex items-center justify-center overflow-hidden">
                    {coverImage ? (
                        <img src={coverImage} alt={title} className="w-full h-full object-cover" />
                    ) : (
                        <div className="text-5xl opacity-40">
                            {coverIcon || <FileText className="h-12 w-12" />}
                        </div>
                    )}

                    {/* Subscribe Toggle */}
                    <div
                        className="absolute top-3 right-3 flex items-center gap-2 bg-background/90 backdrop-blur px-3 py-1.5 rounded-full shadow-sm"
                        onClick={(e) => {
                            e.preventDefault()
                            e.stopPropagation()
                        }}
                    >
                        <Star className={cn(
                            "h-3.5 w-3.5 transition-colors",
                            subscribed ? "text-yellow-500 fill-yellow-500" : "text-muted-foreground"
                        )} />
                        <Switch
                            checked={subscribed}
                            onCheckedChange={handleSubscribeToggle}
                            className="scale-75"
                        />
                    </div>
                </div>

                {/* Content */}
                <div className="p-4">
                    <h3 className="font-semibold text-base group-hover:text-primary transition-colors mb-1 truncate">
                        {title}
                    </h3>

                    {description && (
                        <p className="text-sm text-muted-foreground line-clamp-2 mb-3">
                            {description}
                        </p>
                    )}

                    {/* Stats Row */}
                    <div className="flex items-center gap-4 text-xs text-muted-foreground mb-3">
                        <span className="flex items-center gap-1">
                            <FileText className="h-3 w-3" />
                            {cardCount} cards
                        </span>
                        {lastReviewedAt && (
                            <span className="flex items-center gap-1">
                                <Clock className="h-3 w-3" />
                                {lastReviewedAt}
                            </span>
                        )}
                    </div>

                    {/* Mastery Progress */}
                    <div className="space-y-1">
                        <div className="flex justify-between text-xs">
                            <span className="text-muted-foreground">Mastery</span>
                            <span className="font-medium">{masteryPercentage}%</span>
                        </div>
                        <div className="h-1.5 bg-muted rounded-full overflow-hidden">
                            <div
                                className={cn(
                                    "h-full rounded-full transition-all duration-500",
                                    masteryPercentage < 30 ? "bg-red-500" :
                                        masteryPercentage < 70 ? "bg-yellow-500" : "bg-green-500"
                                )}
                                style={{ width: `${masteryPercentage}%` }}
                            />
                        </div>
                    </div>
                </div>
            </div>
        </Link>
    )
}
