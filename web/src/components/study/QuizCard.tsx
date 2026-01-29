"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { cn } from "@/lib/utils"
import { Check, X, ArrowRight, Lightbulb } from "lucide-react"

type QuizType = "mcq" | "true_false" | "cloze"

interface QuizOption {
    id: string
    text: string
    isCorrect: boolean
}

interface QuizCardProps {
    type: QuizType
    question: string
    options?: QuizOption[]
    correctAnswer?: string  // For cloze type
    explanation?: string
    source?: string
    onComplete: (isCorrect: boolean) => void
}

export function QuizCard({ type, question, options, correctAnswer, explanation, source, onComplete }: QuizCardProps) {
    const [selectedOption, setSelectedOption] = useState<string | null>(null)
    const [clozeAnswer, setClozeAnswer] = useState("")
    const [isChecked, setIsChecked] = useState(false)
    const [isCorrect, setIsCorrect] = useState(false)
    const [showExplanation, setShowExplanation] = useState(false)

    const handleCheck = () => {
        let correct = false

        if (type === "cloze") {
            correct = clozeAnswer.toLowerCase().trim() === correctAnswer?.toLowerCase().trim()
        } else if (options) {
            const selected = options.find(o => o.id === selectedOption)
            correct = selected?.isCorrect || false
        }

        setIsCorrect(correct)
        setIsChecked(true)
        setShowExplanation(true)
    }

    const handleContinue = () => {
        onComplete(isCorrect)
    }

    const canCheck = type === "cloze" ? clozeAnswer.trim() !== "" : selectedOption !== null

    return (
        <div className={cn(
            "flex flex-col h-full transition-colors duration-300",
            isChecked && (isCorrect ? "bg-green-50 dark:bg-green-950/30" : "bg-red-50 dark:bg-red-950/30")
        )}>
            {/* Question Area */}
            <div className="flex-1 flex flex-col justify-center px-8 py-12">
                <div className="max-w-2xl mx-auto w-full">
                    {/* Source Label */}
                    {source && (
                        <div className="mb-4 text-center">
                            <span className="inline-flex items-center gap-1.5 text-xs font-semibold text-muted-foreground/80 uppercase tracking-widest bg-muted/50 px-3 py-1 rounded-full">
                                {source}
                            </span>
                        </div>
                    )}

                    {/* Quiz type label */}
                    <div className="mb-6 text-center">
                        <span className={cn(
                            "text-xs font-medium uppercase tracking-wider px-3 py-1 rounded-full",
                            "bg-purple-100 text-purple-700 dark:bg-purple-950 dark:text-purple-400"
                        )}>
                            {type === "mcq" ? "Multiple Choice" : type === "true_false" ? "True or False" : "Fill in the Blank"}
                        </span>
                    </div>

                    {/* Question */}
                    <div className="bg-card border rounded-2xl p-8 shadow-lg mb-6">
                        <h2 className="text-xl font-semibold text-center leading-relaxed">
                            {question}
                        </h2>
                    </div>

                    {/* Answer Area */}
                    {type === "cloze" ? (
                        <div className="space-y-4">
                            <Input
                                value={clozeAnswer}
                                onChange={(e) => setClozeAnswer(e.target.value)}
                                placeholder="Type your answer..."
                                className={cn(
                                    "h-14 text-lg text-center",
                                    isChecked && (isCorrect
                                        ? "border-green-500 bg-green-50 dark:bg-green-950/50"
                                        : "border-red-500 bg-red-50 dark:bg-red-950/50")
                                )}
                                disabled={isChecked}
                            />
                            {isChecked && !isCorrect && correctAnswer && (
                                <p className="text-center text-sm text-muted-foreground">
                                    Correct answer: <span className="font-medium text-green-600 dark:text-green-400">{correctAnswer}</span>
                                </p>
                            )}
                        </div>
                    ) : (
                        <div className="space-y-3">
                            {options?.map((option) => {
                                const isSelected = selectedOption === option.id
                                let optionClass = "border-border hover:border-primary/50"

                                if (isChecked) {
                                    if (option.isCorrect) {
                                        optionClass = "border-green-500 bg-green-50 dark:bg-green-950/50"
                                    } else if (isSelected && !option.isCorrect) {
                                        optionClass = "border-red-500 bg-red-50 dark:bg-red-950/50"
                                    }
                                } else if (isSelected) {
                                    optionClass = "border-primary bg-primary/5"
                                }

                                return (
                                    <button
                                        key={option.id}
                                        className={cn(
                                            "w-full flex items-center gap-3 p-4 rounded-xl border transition-all text-left",
                                            optionClass,
                                            !isChecked && "cursor-pointer"
                                        )}
                                        onClick={() => !isChecked && setSelectedOption(option.id)}
                                        disabled={isChecked}
                                    >
                                        <div className={cn(
                                            "w-6 h-6 rounded-full border-2 flex items-center justify-center flex-shrink-0 transition-colors",
                                            isSelected ? "border-primary bg-primary" : "border-muted-foreground/30"
                                        )}>
                                            {isSelected && <div className="w-2 h-2 rounded-full bg-white" />}
                                        </div>
                                        <span className="flex-1">{option.text}</span>
                                        {isChecked && option.isCorrect && (
                                            <Check className="h-5 w-5 text-green-500" />
                                        )}
                                        {isChecked && isSelected && !option.isCorrect && (
                                            <X className="h-5 w-5 text-red-500" />
                                        )}
                                    </button>
                                )
                            })}
                        </div>
                    )}

                    {/* Explanation */}
                    {showExplanation && explanation && (
                        <div className="mt-6 p-4 rounded-xl bg-muted/50 border">
                            <div className="flex items-start gap-3">
                                <Lightbulb className="h-5 w-5 text-yellow-500 flex-shrink-0 mt-0.5" />
                                <div>
                                    <p className="font-medium mb-1">Explanation</p>
                                    <p className="text-sm text-muted-foreground">{explanation}</p>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* Action Buttons */}
            <div className="p-6 border-t bg-card/50 backdrop-blur">
                <div className="max-w-md mx-auto">
                    {!isChecked ? (
                        <Button
                            size="lg"
                            className="w-full h-14 gap-2"
                            disabled={!canCheck}
                            onClick={handleCheck}
                        >
                            <Check className="h-5 w-5" />
                            Check Answer
                        </Button>
                    ) : (
                        <Button
                            size="lg"
                            className={cn(
                                "w-full h-14 gap-2",
                                isCorrect
                                    ? "bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600"
                                    : "bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600"
                            )}
                            onClick={handleContinue}
                        >
                            Continue
                            <ArrowRight className="h-5 w-5" />
                        </Button>
                    )}
                </div>
            </div>
        </div>
    )
}
