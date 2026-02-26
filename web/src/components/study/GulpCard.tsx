"use client"

import { useState } from "react"
import ReactMarkdown from "react-markdown"
import {
    Bookmark, BookmarkCheck, MessageCircle, ArrowDownToLine,
    SkipForward, ExternalLink, RotateCcw, Check, X, Lightbulb,
    ChevronRight
} from "lucide-react"
import { cn } from "@/lib/utils"
import { GulpCard as GulpCardType } from "@/lib/api/study"

interface GulpCardProps {
    card: GulpCardType
    onBookmark: (cardId: string) => void
    onUnbookmark: (cardId: string) => void
    onMarkLearned: (cardId: string) => void
    onSkip: () => void
    onDeepDive: (sourceId: string) => void
    isActive: boolean
}

export function GulpCard({ card, onBookmark, onUnbookmark, onMarkLearned, onSkip, onDeepDive, isActive }: GulpCardProps) {
    const [isFlipped, setIsFlipped] = useState(false)
    const [selectedOption, setSelectedOption] = useState<number | null>(null)
    const [isChecked, setIsChecked] = useState(false)
    const [isCorrect, setIsCorrect] = useState(false)
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

    const handleQuizCheck = () => {
        if (selectedOption === null || !card.options) return
        const correct = card.options[selectedOption] === card.answer
        setIsCorrect(correct)
        setIsChecked(true)
    }

    const handleQuizContinue = () => {
        onMarkLearned(card.id)
    }

    // Gradient based on card type
    const gradientClass = {
        note: "from-blue-500/8 via-transparent to-indigo-500/8",
        reading_note: "from-emerald-500/8 via-transparent to-teal-500/8",
        flashcard: "from-amber-500/8 via-transparent to-orange-500/8",
        quiz: "from-violet-500/8 via-transparent to-purple-500/8",
    }[card.type] || "from-gray-500/8 to-gray-500/5"

    const typeConfig = {
        note: { label: "Note", accent: "text-blue-600 dark:text-blue-400 bg-blue-500/10 border-blue-500/20" },
        reading_note: { label: "Reading", accent: "text-emerald-600 dark:text-emerald-400 bg-emerald-500/10 border-emerald-500/20" },
        flashcard: { label: "Flash", accent: "text-amber-600 dark:text-amber-400 bg-amber-500/10 border-amber-500/20" },
        quiz: { label: "Quiz", accent: "text-violet-600 dark:text-violet-400 bg-violet-500/10 border-violet-500/20" },
    }[card.type] || { label: card.type, accent: "text-muted-foreground bg-muted" }

    return (
        <div className={cn(
            "gulp-card h-full w-full flex flex-col relative",
            "bg-gradient-to-br",
            gradientClass,
        )}>
            {/* Top bar: type + source */}
            <div className="flex items-center justify-between px-6 pt-6 pb-3 shrink-0">
                <div className="flex items-center gap-3">
                    <span className={cn(
                        "text-xs font-bold uppercase tracking-wider px-3 py-1.5 rounded-lg border",
                        typeConfig.accent
                    )}>
                        {typeConfig.label}
                    </span>
                    {card.batch_index != null && card.batch_total != null && (
                        <div className="flex items-center gap-2">
                            <div className="w-16 h-1.5 rounded-full bg-muted overflow-hidden">
                                <div
                                    className="h-full rounded-full bg-primary transition-all duration-500"
                                    style={{ width: `${((card.batch_index + 1) / card.batch_total) * 100}%` }}
                                />
                            </div>
                            <span className="text-xs text-muted-foreground tabular-nums">
                                {card.batch_index + 1}/{card.batch_total}
                            </span>
                        </div>
                    )}
                </div>
                {card.source_title && (
                    <button
                        className="text-xs text-muted-foreground hover:text-foreground transition-colors flex items-center gap-1.5 max-w-[40%] truncate group"
                        onClick={() => card.source_url && window.open(card.source_url, '_blank')}
                    >
                        <span className="truncate">{card.source_title}</span>
                        <ExternalLink className="h-3 w-3 shrink-0 opacity-0 group-hover:opacity-100 transition-opacity" />
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
                        isChecked={isChecked}
                        isCorrect={isCorrect}
                        onSelect={(idx) => {
                            if (!isChecked) setSelectedOption(idx)
                        }}
                    />
                )}
            </div>

            {/* Tags */}
            {card.tags.length > 0 && (
                <div className="px-6 py-2 flex flex-wrap gap-1.5 shrink-0">
                    {card.tags.slice(0, 4).map((tag, i) => (
                        <span key={i} className="text-[10px] px-2.5 py-1 rounded-md bg-foreground/5 text-muted-foreground font-medium border border-border/50">
                            #{tag}
                        </span>
                    ))}
                </div>
            )}

            {/* Action bar */}
            <div className="shrink-0 px-6 pb-6 pt-4 border-t border-border/20">
                {/* Quiz: show Check/Continue button */}
                {card.type === "quiz" && !isChecked && selectedOption !== null && (
                    <button
                        onClick={handleQuizCheck}
                        className="w-full mb-3 flex items-center justify-center gap-2 px-6 py-3 rounded-xl text-sm font-semibold bg-primary text-primary-foreground hover:bg-primary/90 transition-all shadow-md hover:shadow-lg"
                    >
                        <Check className="h-4 w-4" />
                        Check Answer
                    </button>
                )}
                {card.type === "quiz" && isChecked && (
                    <button
                        onClick={handleQuizContinue}
                        className={cn(
                            "w-full mb-3 flex items-center justify-center gap-2 px-6 py-3 rounded-xl text-sm font-semibold text-white transition-all shadow-md hover:shadow-lg",
                            isCorrect
                                ? "bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 hover:to-teal-600"
                                : "bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600"
                        )}
                    >
                        {isCorrect ? "Correct! Continue" : "Continue"}
                        <ChevronRight className="h-4 w-4" />
                    </button>
                )}

                {/* Main action buttons */}
                <div className="flex items-center justify-center gap-2">
                    {/* Ask */}
                    <ActionButton
                        icon={MessageCircle}
                        label="Ask"
                        onClick={() => {/* TODO: open ask dialog */}}
                        colorClass="hover:text-blue-600 dark:hover:text-blue-400 hover:bg-blue-500/10 hover:border-blue-500/20"
                    />

                    {/* Clip */}
                    <ActionButton
                        icon={localBookmarked ? BookmarkCheck : Bookmark}
                        label={localBookmarked ? "Clipped" : "Clip"}
                        onClick={handleBookmarkToggle}
                        active={localBookmarked}
                        colorClass={localBookmarked
                            ? "text-amber-600 dark:text-amber-400 bg-amber-500/10 border-amber-500/20"
                            : "hover:text-amber-600 dark:hover:text-amber-400 hover:bg-amber-500/10 hover:border-amber-500/20"
                        }
                    />

                    {/* Deep Dive */}
                    <ActionButton
                        icon={ArrowDownToLine}
                        label="Deep"
                        onClick={() => card.source_url && onDeepDive(card.source_url)}
                        colorClass="hover:text-purple-600 dark:hover:text-purple-400 hover:bg-purple-500/10 hover:border-purple-500/20"
                    />

                    {/* Divider */}
                    <div className="w-px h-8 bg-border/50 mx-1" />

                    {/* Got it (primary action) */}
                    {card.type !== "quiz" && (
                        <button
                            onClick={() => onMarkLearned(card.id)}
                            className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold bg-primary text-primary-foreground hover:bg-primary/90 transition-all duration-200 shadow-sm hover:shadow-md hover:-translate-y-0.5"
                        >
                            <Check className="h-4 w-4" />
                            Got it
                        </button>
                    )}

                    {/* Skip */}
                    <ActionButton
                        icon={SkipForward}
                        label="Skip"
                        onClick={onSkip}
                        colorClass="hover:text-foreground hover:bg-muted"
                    />
                </div>
            </div>
        </div>
    )
}

// --- Action Button ---

function ActionButton({ icon: Icon, label, onClick, active, colorClass }: {
    icon: React.ComponentType<{ className?: string }>
    label: string
    onClick: () => void
    active?: boolean
    colorClass: string
}) {
    return (
        <button
            onClick={onClick}
            className={cn(
                "flex items-center gap-2 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 border border-transparent",
                active ? colorClass : `text-muted-foreground ${colorClass}`
            )}
        >
            <Icon className="h-4 w-4" />
            <span className="hidden sm:inline">{label}</span>
        </button>
    )
}

// --- Sub-components ---

function NoteContent({ question, answer, images }: { question: string; answer?: string; images?: string[] }) {
    return (
        <div className="flex flex-col justify-center min-h-full space-y-6">
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
                            loading="lazy"
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

function QuizContent({ question, options, answer, explanation, selectedOption, isChecked, isCorrect, onSelect }: {
    question: string
    options: string[]
    answer: string
    explanation?: string
    selectedOption: number | null
    isChecked: boolean
    isCorrect: boolean
    onSelect: (idx: number) => void
}) {
    return (
        <div className="flex flex-col justify-center min-h-full space-y-6">
            <h2 className="text-xl font-bold leading-tight">{question}</h2>

            <div className="space-y-3">
                {options.map((option, idx) => {
                    const optionIsCorrect = option === answer
                    const isSelected = selectedOption === idx
                    return (
                        <button
                            key={idx}
                            onClick={() => onSelect(idx)}
                            disabled={isChecked}
                            className={cn(
                                "w-full text-left px-4 py-3.5 rounded-xl border-2 transition-all duration-300 font-medium text-sm flex items-center gap-3",
                                !isChecked && !isSelected && "hover:border-primary/50 hover:bg-primary/5 border-border/50 bg-card/50",
                                !isChecked && isSelected && "border-primary bg-primary/5",
                                isChecked && optionIsCorrect && "border-emerald-500 bg-emerald-500/10",
                                isChecked && isSelected && !optionIsCorrect && "border-red-500 bg-red-500/10",
                                isChecked && !isSelected && !optionIsCorrect && "border-border/30 opacity-40",
                            )}
                        >
                            <span className={cn(
                                "inline-flex items-center justify-center w-7 h-7 rounded-lg text-xs font-bold shrink-0 transition-colors",
                                isChecked && optionIsCorrect && "bg-emerald-500 text-white",
                                isChecked && isSelected && !optionIsCorrect && "bg-red-500 text-white",
                                !isChecked && isSelected && "bg-primary text-primary-foreground",
                                !isChecked && !isSelected && "bg-muted/60 text-muted-foreground",
                            )}>
                                {isChecked && optionIsCorrect ? <Check className="h-3.5 w-3.5" /> :
                                 isChecked && isSelected && !optionIsCorrect ? <X className="h-3.5 w-3.5" /> :
                                 String.fromCharCode(65 + idx)}
                            </span>
                            <span className="flex-1">{option}</span>
                        </button>
                    )
                })}
            </div>

            {isChecked && explanation && (
                <div className="p-4 rounded-xl bg-muted/40 border border-border/30 animate-in fade-in slide-in-from-bottom-2 duration-300">
                    <div className="flex items-start gap-3">
                        <Lightbulb className="h-5 w-5 text-amber-500 shrink-0 mt-0.5" />
                        <div>
                            <p className="font-semibold text-sm mb-1">Explanation</p>
                            <p className="text-sm text-muted-foreground leading-relaxed">{explanation}</p>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}
