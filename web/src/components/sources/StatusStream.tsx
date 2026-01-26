"use client"

import { Loader2 } from "lucide-react"

const statuses = [
    "Analyzing X thread by @naval...",
    "Generating flashcards for 'The Almanack of Naval Ravikant'...",
    "Syncing latest RSS feeds from Paul Graham...",
    "Processing audio transcript from Podcast #123..."
]

export function StatusStream() {
    return (
        <div className="w-full bg-muted/30 border-y py-2 px-4 overflow-hidden">
            <div className="flex items-center gap-4 animate-in slide-in-from-right duration-500">
                <span className="flex items-center gap-2 text-xs font-medium text-primary whitespace-nowrap">
                    <Loader2 className="h-3 w-3 animate-spin" />
                    Live Activity
                </span>
                <div className="h-4 w-px bg-border mx-2" />
                <div className="flex-1 overflow-hidden relative h-5">
                    <div className="absolute top-0 left-0 w-full animate-accordion-down">
                        <p className="text-xs text-muted-foreground truncate">
                            {statuses[0]} <span className="text-green-500 font-mono ml-2">Done</span>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    )
}
