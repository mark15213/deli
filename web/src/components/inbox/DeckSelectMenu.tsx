"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { ChevronDown, Plus, Check, FolderPlus } from "lucide-react"
import { cn } from "@/lib/utils"

interface Deck {
    id: string
    name: string
    cardCount: number
}

interface DeckSelectMenuProps {
    decks: Deck[]
    onSelect: (deckId: string) => void
    onCreateNew: () => void
    className?: string
    disabled?: boolean
    currentDeckIds?: string[]
}

export function DeckSelectMenu({ decks, onSelect, onCreateNew, className, disabled, currentDeckIds = [] }: DeckSelectMenuProps) {
    const [isOpen, setIsOpen] = useState(false)

    const handleSelect = (deckId: string) => {
        onSelect(deckId)
        setIsOpen(false)
    }

    return (
        <div className={cn("relative", className)}>
            <Button
                variant="outline"
                size="sm"
                className="h-8 text-xs gap-1.5"
                disabled={disabled}
                onClick={(e) => {
                    e.stopPropagation()
                    setIsOpen(!isOpen)
                }}
            >
                <Plus className="h-3 w-3" />
                Add to Deck
                <ChevronDown className={cn("h-3 w-3 transition-transform", isOpen && "rotate-180")} />
            </Button>

            {isOpen && (
                <>
                    {/* Backdrop */}
                    <div
                        className="fixed inset-0 z-40"
                        onClick={(e) => {
                            e.stopPropagation()
                            setIsOpen(false)
                        }}
                    />

                    {/* Menu */}
                    <div className="absolute right-0 top-full mt-1 z-50 min-w-[200px] bg-popover border rounded-lg shadow-lg py-1 overflow-hidden">
                        <div className="px-3 py-2 text-xs font-medium text-muted-foreground border-b">
                            Select a deck
                        </div>

                        <div className="max-h-[200px] overflow-y-auto">
                            {decks.map((deck) => (
                                <button
                                    key={deck.id}
                                    className={cn(
                                        "w-full flex items-center justify-between px-3 py-2 text-sm hover:bg-accent transition-colors text-left",
                                        currentDeckIds.includes(deck.id) && "bg-accent"
                                    )}
                                    onClick={(e) => {
                                        e.stopPropagation()
                                        handleSelect(deck.id)
                                    }}
                                >
                                    <span className="truncate">{deck.name}</span>
                                    <div className="flex items-center gap-2">
                                        <span className="text-xs text-muted-foreground">{deck.cardCount}</span>
                                        {currentDeckIds.includes(deck.id) && <Check className="h-3 w-3 text-primary" />}
                                    </div>
                                </button>
                            ))}
                        </div>

                        <div className="border-t">
                            <button
                                className="w-full flex items-center gap-2 px-3 py-2 text-sm text-primary hover:bg-accent transition-colors"
                                onClick={(e) => {
                                    e.stopPropagation()
                                    onCreateNew()
                                    setIsOpen(false)
                                }}
                            >
                                <FolderPlus className="h-4 w-4" />
                                Create New Deck
                            </button>
                        </div>
                    </div>
                </>
            )}
        </div>
    )
}
