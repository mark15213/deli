"use client"

import { cn } from "@/lib/utils"

interface ProgressRingProps {
    progress: number
    size?: number
    strokeWidth?: number
    className?: string
}

export function ProgressRing({ progress, size = 120, strokeWidth = 8, className }: ProgressRingProps) {
    const radius = (size - strokeWidth) / 2
    const circumference = radius * 2 * Math.PI
    const offset = circumference - (progress / 100) * circumference

    return (
        <div className={cn("relative flex items-center justify-center", className)} style={{ width: size, height: size }}>
            <svg
                className="transform -rotate-90 w-full h-full"
                width={size}
                height={size}
            >
                <circle
                    className="text-secondary stroke-current"
                    strokeWidth={strokeWidth}
                    fill="transparent"
                    r={radius}
                    cx={size / 2}
                    cy={size / 2}
                />
                <circle
                    className="text-primary stroke-current transition-all duration-1000 ease-in-out"
                    strokeWidth={strokeWidth}
                    strokeDasharray={circumference}
                    strokeDashoffset={offset}
                    strokeLinecap="round"
                    fill="transparent"
                    r={radius}
                    cx={size / 2}
                    cy={size / 2}
                />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-3xl font-bold">{progress}%</span>
                <span className="text-xs text-muted-foreground uppercase tracking-widest">Rate</span>
            </div>
        </div>
    )
}
