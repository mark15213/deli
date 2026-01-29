"use client"

import { TypeIcon, ContentType } from "@/components/shared/TypePill"
import { cn } from "@/lib/utils"
import { CheckCircle, Circle, ChevronRight, Trash2 } from "lucide-react"

interface CardListItemProps {
    id: string
    type: ContentType
    content: string
    source?: string
    isMastered?: boolean
    onClick?: () => void
    onDelete?: () => void
    isEditing?: boolean
}

export function CardListItem({ id, type, content, source, isMastered, onClick, onDelete, isEditing }: CardListItemProps) {
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
                {source && (
                    <p className="text-xs text-muted-foreground mt-0.5 flex items-center gap-1">
                        <span className="w-1.5 h-1.5 rounded-full bg-primary/40" />
                        {source}
                    </p>
                )}
            </div>

            {/* Status / Action */}
            <div className="flex-shrink-0 flex items-center gap-2">
                {isMastered ? (
                    <CheckCircle className="h-4 w-4 text-green-500" />
                ) : (
                    <Circle className="h-4 w-4 text-muted-foreground/40" />
                )}

                {onDelete && (
                    <button
                        className={cn(
                            "p-1 rounded-md text-muted-foreground hover:bg-destructive/10 hover:text-destructive transition-all",
                            isEditing ? "opacity-100" : "opacity-0 group-hover:opacity-100"
                        )}
                        onClick={(e) => {
                            e.stopPropagation()
                            onDelete()
                        }}
                    >
                        <Trash2 className="h-4 w-4" />
                    </button>
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
    source?: string
    isMastered?: boolean
}

interface CardListProps {
    cards: Card[]
    onCardClick?: (cardId: string) => void
    onDeleteCard?: (cardId: string) => void
    isEditing?: boolean
}

export function CardList({ cards, onCardClick, onDeleteCard, isEditing }: CardListProps) {
    return (
        <div className="space-y-2">
            {cards.map((card) => (
                <CardListItem
                    key={card.id}
                    {...card}
                    onClick={() => onCardClick?.(card.id)}
                    onDelete={onDeleteCard ? () => onDeleteCard(card.id) : undefined}
                    isEditing={isEditing}
                />
            ))}
        </div>
    )
}
