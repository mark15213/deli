"use client"

import { SourceCategory } from "@/types/source"
import { Camera, RefreshCw } from "lucide-react"
import { cn } from "@/lib/utils"

interface SourceCategoryBadgeProps {
    category: SourceCategory
    className?: string
    showIcon?: boolean
    size?: 'sm' | 'md'
}

export function SourceCategoryBadge({
    category,
    className,
    showIcon = true,
    size = 'md'
}: SourceCategoryBadgeProps) {
    const isSnapshot = category === 'SNAPSHOT'

    const sizeClasses = size === 'sm'
        ? 'text-[10px] px-1.5 py-0.5 gap-1'
        : 'text-xs px-2 py-1 gap-1.5'

    const iconSize = size === 'sm' ? 'h-3 w-3' : 'h-3.5 w-3.5'

    return (
        <span
            className={cn(
                "inline-flex items-center font-medium rounded-full",
                sizeClasses,
                isSnapshot
                    ? "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400"
                    : "bg-blue-500/10 text-blue-600 dark:text-blue-400",
                className
            )}
        >
            {showIcon && (
                isSnapshot
                    ? <Camera className={iconSize} />
                    : <RefreshCw className={iconSize} />
            )}
            <span>{isSnapshot ? '快照' : '订阅'}</span>
        </span>
    )
}

// English version
export function SourceCategoryBadgeEN({
    category,
    className,
    showIcon = true,
    size = 'md'
}: SourceCategoryBadgeProps) {
    const isSnapshot = category === 'SNAPSHOT'

    const sizeClasses = size === 'sm'
        ? 'text-[10px] px-1.5 py-0.5 gap-1'
        : 'text-xs px-2 py-1 gap-1.5'

    const iconSize = size === 'sm' ? 'h-3 w-3' : 'h-3.5 w-3.5'

    return (
        <span
            className={cn(
                "inline-flex items-center font-medium rounded-full",
                sizeClasses,
                isSnapshot
                    ? "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400"
                    : "bg-blue-500/10 text-blue-600 dark:text-blue-400",
                className
            )}
        >
            {showIcon && (
                isSnapshot
                    ? <Camera className={iconSize} />
                    : <RefreshCw className={iconSize} />
            )}
            <span>{isSnapshot ? 'Snapshot' : 'Subscription'}</span>
        </span>
    )
}
