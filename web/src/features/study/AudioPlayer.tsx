"use client"

import { Button } from "@/components/ui/button"
import { Slider } from "@/components/ui/slider"
import { Play, SkipBack, SkipForward, Volume2, FastForward } from "lucide-react"
import { ScrollArea } from "@/components/ui/scroll-area"

export function AudioPlayerView() {
    return (
        <div className="h-full flex flex-col bg-background">
            <div className="flex-1 flex flex-col items-center justify-center p-12 text-center space-y-8">
                <div className="h-64 w-64 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-500 shadow-2xl flex items-center justify-center">
                    <span className="text-white text-4xl font-bold">Daily Brief</span>
                </div>

                <div className="space-y-2 max-w-md w-full">
                    <h2 className="text-2xl font-bold">AI News Roundup</h2>
                    <p className="text-muted-foreground">Episode 42 • 15 min</p>
                </div>

                <div className="w-full max-w-md space-y-2">
                    <Slider defaultValue={[33]} max={100} step={1} />
                    <div className="flex items-center justify-between text-xs text-muted-foreground font-mono">
                        <span>05:12</span>
                        <span>15:00</span>
                    </div>
                </div>

                <div className="flex items-center gap-8">
                    <Button variant="ghost" size="icon" className="h-12 w-12 text-muted-foreground hover:text-foreground">
                        <SkipBack className="h-6 w-6" />
                    </Button>
                    <Button size="icon" className="h-16 w-16 rounded-full shadow-xl">
                        <Play className="h-8 w-8 ml-1" />
                    </Button>
                    <Button variant="ghost" size="icon" className="h-12 w-12 text-muted-foreground hover:text-foreground">
                        <SkipForward className="h-6 w-6" />
                    </Button>
                </div>

                <div className="flex items-center gap-4">
                    <Button variant="ghost" size="sm" className="text-xs gap-1 font-mono">
                        <FastForward className="h-3 w-3" /> 1.5x
                    </Button>
                </div>
            </div>

            {/* Transcript Snippet */}
            <div className="h-48 border-t bg-muted/10">
                <div className="p-2 px-4 border-b text-xs font-semibold uppercase text-muted-foreground">Transcript</div>
                <ScrollArea className="h-full p-6">
                    <p className="text-lg leading-relaxed text-muted-foreground text-center max-w-2xl mx-auto">
                        ...and that's a wrap on the latest developments in Gemini.
                        <span className="text-foreground font-medium bg-yellow-100 dark:bg-yellow-900/30 px-1 rounded mx-1">
                            Moving on to OpenAI's new release, we see a shift towards more agentic workflows.
                        </span>
                        This is consistent with what we observed last week...
                    </p>
                </ScrollArea>
            </div>
        </div>
    )
}
