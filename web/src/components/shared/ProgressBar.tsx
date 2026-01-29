"use client"

import { cn } from "@/lib/utils"

interface ProgressBarProps {
    current: number
    total: number
    className?: string
    showLabel?: boolean
}

export function ProgressBar({ current, total, className, showLabel = true }: ProgressBarProps) {
    const percentage = total > 0 ? Math.round((current / total) * 100) : 0

    return (
        <div className={cn("w-full", className)}>
            {showLabel && (
                <div className="flex justify-between items-center mb-2 text-sm">
                    <span className="text-muted-foreground">Progress</span>
                    <span className="font-medium">
                        <span className="text-primary">{current}</span>
                        <span className="text-muted-foreground"> / {total}</span>
                    </span>
                </div>
            )}
            <div className="h-2 w-full bg-muted rounded-full overflow-hidden">
                <div
                    className="h-full bg-gradient-to-r from-primary to-primary/80 rounded-full transition-all duration-500 ease-out"
                    style={{ width: `${percentage}%` }}
                />
            </div>
        </div>
    )
}

interface StudyProgressProps {
    remaining: number
    total: number
    className?: string
}

export function StudyProgress({ remaining, total, className }: StudyProgressProps) {
    const completed = total - remaining
    const percentage = total > 0 ? Math.round((completed / total) * 100) : 0

    return (
        <div className={cn("flex items-center gap-4", className)}>
            <div className="flex-1 h-1.5 bg-muted rounded-full overflow-hidden">
                <div
                    className="h-full bg-gradient-to-r from-green-500 to-emerald-400 rounded-full transition-all duration-300"
                    style={{ width: `${percentage}%` }}
                />
            </div>
            <span className="text-sm font-medium text-muted-foreground whitespace-nowrap">
                {remaining} left
            </span>
        </div>
    )
}
