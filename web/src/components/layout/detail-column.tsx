"use client"

import { cn } from "@/lib/utils"
import { useNavigationStore } from "@/store/use-navigation"
import { SplitView } from "@/features/inbox/SplitView"
import { FlashcardView } from "@/features/study/FlashcardView"
import { AudioPlayerView } from "@/features/study/AudioPlayer"

interface DetailColumnProps extends React.HTMLAttributes<HTMLDivElement> { }

export function DetailColumn({ className }: DetailColumnProps) {
    const { currentView, activeInboxId, activeStudyType } = useNavigationStore()

    if (currentView === 'inbox' && activeInboxId) {
        return (
            <div className={cn("h-full bg-background overflow-hidden", className)}>
                <SplitView />
            </div>
        )
    }

    if (currentView === 'study') {
        if (activeStudyType === 'flashcard') {
            return (
                <div className={cn("h-full bg-background overflow-hidden", className)}>
                    <FlashcardView />
                </div>
            )
        }
        if (activeStudyType === 'audio') {
            return (
                <div className={cn("h-full bg-background overflow-hidden", className)}>
                    <AudioPlayerView />
                </div>
            )
        }
    }

    // Default empty state
    return (
        <div className={cn("flex flex-col h-full bg-background", className)}>
            <div className="flex-1 flex items-center justify-center p-8 text-center text-muted-foreground">
                <div>
                    <h3 className="text-lg font-medium text-foreground">Select an item</h3>
                    <p className="mt-2">Choose from the list to view details</p>
                </div>
            </div>
        </div>
    )
}
