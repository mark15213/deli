"use client"

import { cn } from "@/lib/utils"
import { FileText, RotateCw, HelpCircle } from "lucide-react"

export type ContentType = "note" | "flashcard" | "quiz"

interface TypePillProps {
    type: ContentType
    count: number
    className?: string
}

const typeConfig: Record<ContentType, { label: string; icon: React.ElementType; colorClass: string }> = {
    note: {
        label: "Notes",
        icon: FileText,
        colorClass: "bg-blue-100 text-blue-700 dark:bg-blue-950 dark:text-blue-400 border-blue-200 dark:border-blue-800"
    },
    flashcard: {
        label: "Flashcards",
        icon: RotateCw,
        colorClass: "bg-orange-100 text-orange-700 dark:bg-orange-950 dark:text-orange-400 border-orange-200 dark:border-orange-800"
    },
    quiz: {
        label: "Quiz",
        icon: HelpCircle,
        colorClass: "bg-purple-100 text-purple-700 dark:bg-purple-950 dark:text-purple-400 border-purple-200 dark:border-purple-800"
    }
}

export function TypePill({ type, count, className }: TypePillProps) {
    if (count === 0) return null

    const config = typeConfig[type]
    const Icon = config.icon

    return (
        <span
            className={cn(
                "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border transition-colors",
                config.colorClass,
                className
            )}
        >
            <Icon className="h-3 w-3" />
            <span>{count}</span>
            <span className="hidden sm:inline">{config.label}</span>
        </span>
    )
}

interface TypeIconProps {
    type: ContentType
    className?: string
}

export function TypeIcon({ type, className }: TypeIconProps) {
    const config = typeConfig[type]
    const Icon = config.icon

    const iconColorClass = {
        note: "text-blue-500",
        flashcard: "text-orange-500",
        quiz: "text-purple-500"
    }[type]

    return <Icon className={cn("h-4 w-4", iconColorClass, className)} />
}
