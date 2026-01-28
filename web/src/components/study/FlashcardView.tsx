"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { ExternalLink, RotateCcw } from "lucide-react"
import { cn } from "@/lib/utils"

interface FlashcardViewProps {
    question: string
    answer: string
    source?: string
    sourceUrl?: string
    onRate: (rating: "forgot" | "hard" | "easy") => void
}

export function FlashcardView({ question, answer, source, sourceUrl, onRate }: FlashcardViewProps) {
    const [isFlipped, setIsFlipped] = useState(false)

    const handleFlip = () => {
        setIsFlipped(!isFlipped)
    }

    return (
        <div className="flex flex-col h-full">
            {/* Card Area */}
            <div className="flex-1 flex flex-col justify-center px-8 py-12">
                <div className="max-w-2xl mx-auto w-full">
                    {/* Flashcard with 3D flip */}
                    <div
                        className="relative h-[400px] w-full cursor-pointer [perspective:1200px]"
                        onClick={handleFlip}
                    >
                        <div className={cn(
                            "relative h-full w-full transition-all duration-700 [transform-style:preserve-3d]",
                            isFlipped && "[transform:rotateY(180deg)]"
                        )}>
                            {/* Front - Question */}
                            <div className="absolute inset-0 [backface-visibility:hidden]">
                                <div className="h-full w-full rounded-2xl bg-card border-2 shadow-2xl flex flex-col items-center justify-center p-12 text-center relative overflow-hidden">
                                    {/* Card depth effect */}
                                    <div className="absolute inset-x-0 bottom-0 h-2 bg-gradient-to-t from-muted to-transparent rounded-b-2xl" />
                                    <div className="absolute inset-y-0 right-0 w-1 bg-gradient-to-l from-muted to-transparent rounded-r-2xl" />

                                    <span className="text-xs font-semibold text-muted-foreground uppercase tracking-widest mb-6 bg-muted px-3 py-1 rounded-full">
                                        Question
                                    </span>
                                    <h2 className="text-2xl md:text-3xl font-bold leading-tight">
                                        {question}
                                    </h2>

                                    {/* Flip hint */}
                                    <div className="absolute bottom-6 flex items-center gap-2 text-xs text-muted-foreground">
                                        <RotateCcw className="h-3 w-3" />
                                        <span>Click to reveal answer</span>
                                    </div>
                                </div>
                            </div>

                            {/* Back - Answer */}
                            <div className="absolute inset-0 [backface-visibility:hidden] [transform:rotateY(180deg)]">
                                <div className="h-full w-full rounded-2xl border-2 shadow-2xl flex flex-col items-center justify-center p-12 text-center relative overflow-hidden bg-gradient-to-br from-primary/5 via-background to-primary/10">
                                    {/* Card depth effect */}
                                    <div className="absolute inset-x-0 bottom-0 h-2 bg-gradient-to-t from-primary/10 to-transparent rounded-b-2xl" />

                                    <span className="text-xs font-semibold text-primary uppercase tracking-widest mb-6 bg-primary/10 px-3 py-1 rounded-full">
                                        Answer
                                    </span>
                                    <p className="text-xl leading-relaxed text-foreground/90">
                                        {answer}
                                    </p>

                                    {/* Source link */}
                                    {source && (
                                        <div className="absolute bottom-6 left-6">
                                            <Button
                                                variant="link"
                                                className="text-xs text-muted-foreground h-auto p-0 gap-1"
                                                onClick={(e) => {
                                                    e.stopPropagation()
                                                    if (sourceUrl) window.open(sourceUrl, '_blank')
                                                }}
                                            >
                                                <ExternalLink className="h-3 w-3" />
                                                {source}
                                            </Button>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Rating Buttons - Only visible after flip */}
            <div className={cn(
                "p-6 border-t bg-card/50 backdrop-blur transition-all duration-300",
                isFlipped ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4 pointer-events-none"
            )}>
                <div className="max-w-lg mx-auto grid grid-cols-3 gap-4">
                    <Button
                        variant="outline"
                        size="lg"
                        className="h-16 border-red-200 hover:bg-red-50 hover:text-red-600 hover:border-red-300 dark:border-red-900/50 dark:hover:bg-red-950/50 flex-col gap-0.5"
                        onClick={() => onRate("forgot")}
                    >
                        <span className="text-2xl">🔴</span>
                        <span className="font-semibold text-sm">Forgot</span>
                        <span className="text-[10px] text-muted-foreground">1 min</span>
                    </Button>
                    <Button
                        variant="outline"
                        size="lg"
                        className="h-16 border-yellow-200 hover:bg-yellow-50 hover:text-yellow-600 hover:border-yellow-300 dark:border-yellow-900/50 dark:hover:bg-yellow-950/50 flex-col gap-0.5"
                        onClick={() => onRate("hard")}
                    >
                        <span className="text-2xl">🟡</span>
                        <span className="font-semibold text-sm">Hard</span>
                        <span className="text-[10px] text-muted-foreground">2 days</span>
                    </Button>
                    <Button
                        variant="outline"
                        size="lg"
                        className="h-16 border-green-200 hover:bg-green-50 hover:text-green-600 hover:border-green-300 dark:border-green-900/50 dark:hover:bg-green-950/50 flex-col gap-0.5"
                        onClick={() => onRate("easy")}
                    >
                        <span className="text-2xl">🟢</span>
                        <span className="font-semibold text-sm">Easy</span>
                        <span className="text-[10px] text-muted-foreground">4 days</span>
                    </Button>
                </div>
            </div>
        </div>
    )
}

