"use client"

import { TypeIcon, ContentType } from "@/components/shared/TypePill"
import { cn } from "@/lib/utils"
import { CheckCircle, Circle, ChevronRight } from "lucide-react"

interface CardListItemProps {
    id: string
    type: ContentType
    content: string
    isMastered?: boolean
    onClick?: () => void
}

export function CardListItem({ id, type, content, isMastered, onClick }: CardListItemProps) {
    return (
        <div
            className={cn(
                "group flex items-center gap-3 p-3 rounded-lg border bg-card transition-colors cursor-pointer",
                "hover:bg-muted/50 hover:border-primary/20",
                isMastered && "opacity-60"
            )}
            onClick={onClick}
        >
            {/* Type Icon */}
            <div className="flex-shrink-0">
                <TypeIcon type={type} className="h-5 w-5" />
            </div>

            {/* Content Preview */}
            <div className="flex-1 min-w-0">
                <p className="text-sm truncate">{content}</p>
            </div>

            {/* Status / Action */}
            <div className="flex-shrink-0 flex items-center gap-2">
                {isMastered ? (
                    <CheckCircle className="h-4 w-4 text-green-500" />
                ) : (
                    <Circle className="h-4 w-4 text-muted-foreground/40" />
                )}
                <ChevronRight className="h-4 w-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
            </div>
        </div>
    )
}

export interface Card {
    id: string
    type: ContentType
    content: string
    isMastered?: boolean
}

interface CardListProps {
    cards: Card[]
    onCardClick?: (cardId: string) => void
}

export function CardList({ cards, onCardClick }: CardListProps) {
    return (
        <div className="space-y-2">
            {cards.map((card) => (
                <CardListItem
                    key={card.id}
                    {...card}
                    onClick={() => onCardClick?.(card.id)}
                />
            ))}
        </div>
    )
}
