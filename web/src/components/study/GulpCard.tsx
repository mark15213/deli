"use client"

import { useState } from "react"
import ReactMarkdown from "react-markdown"
import { Bookmark, BookmarkCheck, CheckCircle, RotateCcw, ExternalLink } from "lucide-react"
import { cn } from "@/lib/utils"
import { GulpCard as GulpCardType } from "@/lib/api/study"

interface GulpCardProps {
    card: GulpCardType
    onBookmark: (cardId: string) => void
    onUnbookmark: (cardId: string) => void
    onMarkLearned: (cardId: string) => void
    isActive: boolean
}

export function GulpCard({ card, onBookmark, onUnbookmark, onMarkLearned, isActive }: GulpCardProps) {
    const [isFlipped, setIsFlipped] = useState(false)
    const [selectedOption, setSelectedOption] = useState<number | null>(null)
    const [showAnswer, setShowAnswer] = useState(false)
    const [localBookmarked, setLocalBookmarked] = useState(card.is_bookmarked)

    const handleBookmarkToggle = () => {
        if (localBookmarked) {
            onUnbookmark(card.id)
            setLocalBookmarked(false)
        } else {
            onBookmark(card.id)
            setLocalBookmarked(true)
        }
    }

    const handleQuizSelect = (idx: number) => {
        setSelectedOption(idx)
        setShowAnswer(true)
    }

    // Determine gradient based on card type
    const gradientClass = {
        note: "from-blue-500/10 via-indigo-500/5 to-purple-500/10",
        reading_note: "from-emerald-500/10 via-teal-500/5 to-cyan-500/10",
        flashcard: "from-amber-500/10 via-orange-500/5 to-rose-500/10",
        quiz: "from-violet-500/10 via-purple-500/5 to-fuchsia-500/10",
    }[card.type] || "from-gray-500/10 to-gray-500/5"

    const typeLabel = {
        note: "📝 Note",
        reading_note: "📖 Reading Note",
        flashcard: "🔄 Flashcard",
        quiz: "❓ Quiz",
    }[card.type] || card.type

    return (
        <div className={cn(
            "gulp-card h-full w-full flex flex-col relative",
            "bg-gradient-to-br",
            gradientClass,
        )}>
            {/* Top bar: source + type */}
            <div className="flex items-center justify-between px-6 pt-6 pb-2 shrink-0">
                <div className="flex items-center gap-2">
                    <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider bg-muted/60 px-2.5 py-1 rounded-full backdrop-blur-sm">
                        {typeLabel}
                    </span>
                    {card.batch_index != null && card.batch_total != null && (
                        <span className="text-xs text-muted-foreground">
                            {card.batch_index + 1}/{card.batch_total}
                        </span>
                    )}
                </div>
                {card.source_title && (
                    <button
                        className="text-xs text-muted-foreground hover:text-foreground transition-colors flex items-center gap-1 max-w-[40%] truncate"
                        onClick={() => card.source_url && window.open(card.source_url, '_blank')}
                    >
                        <ExternalLink className="h-3 w-3 shrink-0" />
                        <span className="truncate">{card.source_title}</span>
                    </button>
                )}
            </div>

            {/* Card content area */}
            <div className="flex-1 overflow-y-auto px-6 py-4">
                {(card.type === "note" || card.type === "reading_note") && (
                    <NoteContent question={card.question} answer={card.answer} images={card.images} />
                )}
                {card.type === "flashcard" && (
                    <FlashcardContent
                        question={card.question}
                        answer={card.answer || ""}
                        isFlipped={isFlipped}
                        onFlip={() => setIsFlipped(!isFlipped)}
                    />
                )}
                {card.type === "quiz" && (
                    <QuizContent
                        question={card.question}
                        options={card.options || []}
                        answer={card.answer || ""}
                        explanation={card.explanation}
                        selectedOption={selectedOption}
                        showAnswer={showAnswer}
                        onSelect={handleQuizSelect}
                    />
                )}
            </div>

            {/* Tags */}
            {card.tags.length > 0 && (
                <div className="px-6 py-2 flex flex-wrap gap-1.5 shrink-0">
                    {card.tags.slice(0, 4).map((tag, i) => (
                        <span key={i} className="text-[10px] px-2 py-0.5 rounded-full bg-primary/10 text-primary font-medium">
                            #{tag}
                        </span>
                    ))}
                </div>
            )}

            {/* Bottom action bar */}
            <div className="shrink-0 px-6 pb-6 pt-3 border-t border-border/30 backdrop-blur-sm">
                <div className="flex items-center justify-center gap-3">
                    <button
                        onClick={handleBookmarkToggle}
                        className={cn(
                            "flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium transition-all duration-300",
                            localBookmarked
                                ? "bg-amber-500/20 text-amber-600 dark:text-amber-400 hover:bg-amber-500/30"
                                : "bg-muted/60 text-muted-foreground hover:bg-muted hover:text-foreground"
                        )}
                    >
                        {localBookmarked
                            ? <BookmarkCheck className="h-4 w-4" />
                            : <Bookmark className="h-4 w-4" />
                        }
                        {localBookmarked ? "Clipped" : "Clip"}
                    </button>

                    <button
                        onClick={() => onMarkLearned(card.id)}
                        className="flex items-center gap-2 px-6 py-2.5 rounded-xl text-sm font-medium bg-primary text-primary-foreground hover:bg-primary/90 transition-all duration-300 shadow-md hover:shadow-lg"
                    >
                        <CheckCircle className="h-4 w-4" />
                        Got it
                    </button>
                </div>
            </div>
        </div>
    )
}

// --- Sub-components ---

function NoteContent({ question, answer, images }: { question: string; answer?: string; images?: string[] }) {
    return (
        <div className="space-y-6">
            <div className="prose prose-sm dark:prose-invert max-w-none">
                <h2 className="text-xl font-bold leading-tight mb-4">{question}</h2>
                {answer && (
                    <ReactMarkdown>{answer}</ReactMarkdown>
                )}
            </div>
            {images && images.length > 0 && (
                <div className="space-y-3">
                    {images.map((img, i) => (
                        <img
                            key={i}
                            src={img}
                            alt=""
                            className="w-full rounded-xl object-contain max-h-[300px] bg-muted/30"
                        />
                    ))}
                </div>
            )}
        </div>
    )
}

function FlashcardContent({ question, answer, isFlipped, onFlip }: {
    question: string
    answer: string
    isFlipped: boolean
    onFlip: () => void
}) {
    return (
        <div className="flex flex-col items-center justify-center h-full">
            <div
                className="relative w-full max-w-lg h-[320px] cursor-pointer [perspective:1200px]"
                onClick={onFlip}
            >
                <div className={cn(
                    "relative h-full w-full transition-all duration-700 [transform-style:preserve-3d]",
                    isFlipped && "[transform:rotateY(180deg)]"
                )}>
                    {/* Front */}
                    <div className="absolute inset-0 [backface-visibility:hidden]">
                        <div className="h-full w-full rounded-2xl bg-card border-2 shadow-2xl flex flex-col items-center justify-center p-8 text-center relative overflow-hidden">
                            <span className="text-xs font-semibold text-muted-foreground uppercase tracking-widest mb-4 bg-muted px-3 py-1 rounded-full">
                                Question
                            </span>
                            <h2 className="text-xl md:text-2xl font-bold leading-tight">{question}</h2>
                            <div className="absolute bottom-4 flex items-center gap-2 text-xs text-muted-foreground">
                                <RotateCcw className="h-3 w-3" />
                                <span>Tap to reveal</span>
                            </div>
                        </div>
                    </div>
                    {/* Back */}
                    <div className="absolute inset-0 [backface-visibility:hidden] [transform:rotateY(180deg)]">
                        <div className="h-full w-full rounded-2xl border-2 shadow-2xl flex flex-col items-center justify-center p-8 text-center bg-gradient-to-br from-primary/5 via-background to-primary/10">
                            <span className="text-xs font-semibold text-primary uppercase tracking-widest mb-4 bg-primary/10 px-3 py-1 rounded-full">
                                Answer
                            </span>
                            <p className="text-lg leading-relaxed text-foreground/90">{answer}</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

function QuizContent({ question, options, answer, explanation, selectedOption, showAnswer, onSelect }: {
    question: string
    options: string[]
    answer: string
    explanation?: string
    selectedOption: number | null
    showAnswer: boolean
    onSelect: (idx: number) => void
}) {
    return (
        <div className="flex flex-col justify-center h-full space-y-6">
            <h2 className="text-xl font-bold leading-tight">{question}</h2>

            <div className="space-y-3">
                {options.map((option, idx) => {
                    const isCorrect = option === answer
                    const isSelected = selectedOption === idx
                    return (
                        <button
                            key={idx}
                            onClick={() => !showAnswer && onSelect(idx)}
                            disabled={showAnswer}
                            className={cn(
                                "w-full text-left px-4 py-3.5 rounded-xl border-2 transition-all duration-300 font-medium text-sm",
                                !showAnswer && "hover:border-primary/50 hover:bg-primary/5 border-border/50 bg-card/50",
                                showAnswer && isCorrect && "border-green-500 bg-green-500/10 text-green-700 dark:text-green-400",
                                showAnswer && isSelected && !isCorrect && "border-red-500 bg-red-500/10 text-red-700 dark:text-red-400",
                                showAnswer && !isSelected && !isCorrect && "border-border/30 opacity-50",
                            )}
                        >
                            <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-muted/60 text-xs font-bold mr-3">
                                {String.fromCharCode(65 + idx)}
                            </span>
                            {option}
                        </button>
                    )
                })}
            </div>

            {showAnswer && explanation && (
                <div className="p-4 rounded-xl bg-muted/40 border border-border/30 text-sm text-muted-foreground animate-in fade-in slide-in-from-bottom-2 duration-300">
                    <span className="font-semibold text-foreground">💡 Explanation: </span>
                    {explanation}
                </div>
            )}
        </div>
    )
}
