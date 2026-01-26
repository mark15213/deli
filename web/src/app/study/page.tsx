"use client"

import { useState } from "react"
import { FlashcardView } from "@/components/study/FlashcardView"
import { AudioPlayerView } from "@/components/study/AudioPlayerView"
import { BookOpen, Headphones } from "lucide-react"
import { cn } from "@/lib/utils"

export default function StudyPage() {
    const [mode, setMode] = useState<"flashcard" | "audio">("flashcard")

    return (
        <div className="h-full flex flex-col bg-background">
            {/* Tab Navigation */}
            <div className="flex items-center justify-center border-b bg-card">
                <div className="flex pt-4 md:pt-6">
                    <button
                        onClick={() => setMode("flashcard")}
                        className={cn(
                            "flex items-center gap-2 px-6 py-3 border-b-2 font-medium text-sm transition-colors",
                            mode === "flashcard"
                                ? "border-primary text-primary"
                                : "border-transparent text-muted-foreground hover:text-foreground"
                        )}
                    >
                        <BookOpen className="h-4 w-4" />
                        Flashcards
                    </button>
                    <button
                        onClick={() => setMode("audio")}
                        className={cn(
                            "flex items-center gap-2 px-6 py-3 border-b-2 font-medium text-sm transition-colors",
                            mode === "audio"
                                ? "border-primary text-primary"
                                : "border-transparent text-muted-foreground hover:text-foreground"
                        )}
                    >
                        <Headphones className="h-4 w-4" />
                        Audio
                    </button>
                </div>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-hidden">
                {mode === "flashcard" ? <FlashcardView /> : <AudioPlayerView />}
            </div>
        </div>
    )
}
