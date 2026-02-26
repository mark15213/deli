"use client"

import { RotateCcw, Compass, Shuffle, Target } from "lucide-react"
import { cn } from "@/lib/utils"

type GulpMode = 'review' | 'explore' | 'mixed' | 'deep_dive'

interface GulpModeSwitchProps {
    mode: GulpMode
    onModeChange: (mode: GulpMode) => void
}

const modes = [
    {
        id: 'review' as const,
        label: 'Review',
        icon: RotateCcw,
        color: 'from-emerald-500 to-teal-500',
        bgColor: 'bg-emerald-500/10',
        borderColor: 'border-emerald-500/30',
        textColor: 'text-emerald-600 dark:text-emerald-400',
    },
    {
        id: 'explore' as const,
        label: 'Explore',
        icon: Compass,
        color: 'from-violet-500 to-purple-500',
        bgColor: 'bg-violet-500/10',
        borderColor: 'border-violet-500/30',
        textColor: 'text-violet-600 dark:text-violet-400',
    },
    {
        id: 'mixed' as const,
        label: 'Mixed',
        icon: Shuffle,
        color: 'from-blue-500 to-cyan-500',
        bgColor: 'bg-blue-500/10',
        borderColor: 'border-blue-500/30',
        textColor: 'text-blue-600 dark:text-blue-400',
    },
    {
        id: 'deep_dive' as const,
        label: 'Deep',
        icon: Target,
        color: 'from-amber-500 to-orange-500',
        bgColor: 'bg-amber-500/10',
        borderColor: 'border-amber-500/30',
        textColor: 'text-amber-600 dark:text-amber-400',
    },
]

export function GulpModeSwitch({ mode, onModeChange }: GulpModeSwitchProps) {
    return (
        <div className="flex items-center gap-2 p-1.5 rounded-2xl bg-muted/50 backdrop-blur-sm border border-border/50">
            {modes.map((m) => {
                const Icon = m.icon
                const isActive = mode === m.id

                return (
                    <button
                        key={m.id}
                        onClick={() => onModeChange(m.id)}
                        className={cn(
                            "relative flex items-center gap-2 px-4 py-2 rounded-xl font-medium text-sm transition-all duration-300",
                            isActive
                                ? `${m.bgColor} ${m.borderColor} ${m.textColor} border shadow-sm`
                                : "text-muted-foreground hover:text-foreground hover:bg-muted/50"
                        )}
                    >
                        {isActive && (
                            <div className={cn(
                                "absolute inset-0 rounded-xl bg-gradient-to-r opacity-10",
                                m.color
                            )} />
                        )}
                        <Icon className={cn(
                            "h-4 w-4 transition-transform duration-300",
                            isActive && "scale-110"
                        )} />
                        <span className="relative z-10">{m.label}</span>
                    </button>
                )
            })}
        </div>
    )
}
