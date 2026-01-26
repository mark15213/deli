"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { RotateCw, ArrowLeft, ExternalLink } from "lucide-react"
import { cn } from "@/lib/utils"

export function FlashcardView() {
    const [isFlipped, setIsFlipped] = useState(false)

    // Mock data
    const card = {
        front: "What is the 'Lindy Effect'?",
        back: "The Lindy Effect is a theorized phenomenon by which the future life expectancy of some non-perishable things like a technology or an idea is proportional to their current age, so that every additional period of survival implies a longer remaining life expectancy.",
        source: "Nassim Taleb - Antifragile"
    }

    return (
        <div className="flex flex-col h-full max-w-4xl mx-auto px-6 py-10 w-full">
            {/* Header / Nav */}
            <div className="flex items-center justify-between mb-8">
                <Button variant="ghost" className="gap-2">
                    <ArrowLeft className="h-4 w-4" />
                    Back to Dashboard
                </Button>
                <div className="text-sm font-medium text-muted-foreground">
                    Card 5 of 20
                </div>
            </div>

            {/* Card Area */}
            <div className="flex-1 flex flex-col justify-center min-h-[400px]">
                <div
                    className="group relative h-96 w-full cursor-pointer [perspective:1000px]"
                    onClick={() => setIsFlipped(!isFlipped)}
                >
                    <div className={cn(
                        "relative h-full w-full rounded-2xl shadow-xl transition-all duration-500 [transform-style:preserve-3d] border bg-card",
                        isFlipped ? "[transform:rotateY(180deg)]" : ""
                    )}>
                        {/* Front */}
                        <div className="absolute inset-0 flex flex-col items-center justify-center p-12 text-center [backface-visibility:hidden]">
                            <span className="text-sm font-medium text-muted-foreground uppercase tracking-wider mb-6">Question</span>
                            <h2 className="text-3xl font-bold leading-tight">{card.front}</h2>
                            <div className="absolute bottom-6 right-6 text-xs text-muted-foreground flex items-center gap-1 opacity-50">
                                <RotateCw className="h-3 w-3" /> Click to flip
                            </div>
                        </div>

                        {/* Back */}
                        <div className="absolute inset-0 flex flex-col items-center justify-center p-12 text-center [backface-visibility:hidden] [transform:rotateY(180deg)] bg-primary/5 dark:bg-primary/10">
                            <span className="text-sm font-medium text-primary uppercase tracking-wider mb-6">Answer</span>
                            <p className="text-xl leading-relaxed text-foreground/90">{card.back}</p>
                            <div className="absolute bottom-6 left-6">
                                <Button variant="link" className="text-xs text-muted-foreground h-auto p-0 gap-1">
                                    <ExternalLink className="h-3 w-3" /> {card.source}
                                </Button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Controls */}
            <div className="mt-10 grid grid-cols-3 gap-6 max-w-2xl mx-auto w-full">
                <Button variant="outline" className="h-14 border-red-200 hover:bg-red-50 hover:text-red-600 dark:border-red-900/50 dark:hover:bg-red-950/50">
                    <div className="flex flex-col items-center">
                        <span className="font-bold">Forgot</span>
                        <span className="text-[10px] uppercase opacity-70">1 min</span>
                    </div>
                </Button>
                <Button variant="outline" className="h-14 border-yellow-200 hover:bg-yellow-50 hover:text-yellow-600 dark:border-yellow-900/50 dark:hover:bg-yellow-950/50">
                    <div className="flex flex-col items-center">
                        <span className="font-bold">Hard</span>
                        <span className="text-[10px] uppercase opacity-70">2 days</span>
                    </div>
                </Button>
                <Button variant="outline" className="h-14 border-green-200 hover:bg-green-50 hover:text-green-600 dark:border-green-900/50 dark:hover:bg-green-950/50">
                    <div className="flex flex-col items-center">
                        <span className="font-bold">Easy</span>
                        <span className="text-[10px] uppercase opacity-70">4 days</span>
                    </div>
                </Button>
            </div>
        </div>
    )
}
