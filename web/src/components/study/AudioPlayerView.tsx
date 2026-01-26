"use client"

import { Play, Pause, SkipBack, SkipForward, Volume2, FastForward } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useState } from "react"
import { cn } from "@/lib/utils"

export function AudioPlayerView() {
    const [isPlaying, setIsPlaying] = useState(false)
    const [speed, setSpeed] = useState(1)

    const transcript = [
        { time: "00:00", text: "Welcome to your daily briefing. Today we're discussing Superlinear Returns." },
        { time: "00:15", text: "One of the most important things you can understand about the world is that returns for performance are superlinear.", active: true },
        { time: "00:45", text: "Teachers and coaches implicitly tell us returns are linear. 'You get out what you put in.' But that's only true for simple tasks." },
        { time: "01:20", text: "In complex domains, being twice as good can mean getting 100x the results." },
        { time: "01:45", text: "Think about startup founders or athletes. The winner often takes all." },
    ]

    return (
        <div className="flex h-full bg-background">
            {/* Playlist Sidebar */}
            <div className="w-80 border-r bg-muted/10 flex flex-col">
                <div className="p-6 border-b">
                    <h2 className="font-semibold mb-1">Daily Briefing</h2>
                    <p className="text-xs text-muted-foreground uppercase tracking-wider">Jan 26, 2026</p>
                </div>
                <div className="flex-1 overflow-y-auto p-4 space-y-2">
                    <div className="p-3 rounded-lg bg-primary/10 border border-primary/20 cursor-pointer">
                        <div className="text-xs text-primary font-medium mb-1">Now Playing</div>
                        <div className="font-medium text-sm">Superlinear Returns</div>
                        <div className="text-xs text-muted-foreground mt-1">Paul Graham • 12 mins</div>
                    </div>
                    {[1, 2, 3].map(i => (
                        <div key={i} className="p-3 rounded-lg hover:bg-muted cursor-pointer opacity-70">
                            <div className="font-medium text-sm">Naval on Wealth</div>
                            <div className="text-xs text-muted-foreground mt-1">Naval Ravikant • 8 mins</div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Main Player */}
            <div className="flex-1 flex flex-col">
                {/* Visualizer / Cover */}
                <div className="h-64 bg-gradient-to-br from-indigo-900 to-slate-900 flex items-center justify-center text-white p-8">
                    <div className="text-center">
                        <div className="w-32 h-32 bg-white/10 rounded-2xl mx-auto mb-6 shadow-2xl flex items-center justify-center backdrop-blur-sm">
                            <Volume2 className="h-12 w-12 opacity-50" />
                        </div>
                        <h1 className="text-2xl font-bold">Superlinear Returns</h1>
                        <p className="text-white/60 mt-2">Paul Graham Essay Analysis</p>
                    </div>
                </div>

                {/* Controls */}
                <div className="border-b p-6 bg-card">
                    {/* Progress Bar */}
                    <div className="w-full h-1 bg-secondary rounded-full mb-6 relative group cursor-pointer">
                        <div className="absolute left-0 top-0 h-full w-[30%] bg-primary rounded-full"></div>
                        <div className="absolute left-[30%] top-1/2 -translate-y-1/2 h-3 w-3 bg-primary rounded-full opacity-0 group-hover:opacity-100 shadow transition-opacity"></div>
                    </div>

                    <div className="flex items-center justify-between">
                        <div className="text-xs text-muted-foreground w-12">04:12</div>

                        <div className="flex items-center gap-6">
                            <Button variant="ghost" size="icon" className="hover:bg-transparent"><SkipBack className="h-5 w-5" /></Button>
                            <Button
                                size="icon"
                                className="h-12 w-12 rounded-full shadow-lg"
                                onClick={() => setIsPlaying(!isPlaying)}
                            >
                                {isPlaying ? <Pause className="h-5 w-5" /> : <Play className="h-5 w-5 ml-1" />}
                            </Button>
                            <Button variant="ghost" size="icon" className="hover:bg-transparent"><SkipForward className="h-5 w-5" /></Button>
                        </div>

                        <div className="flex items-center gap-4 w-12 justify-end">
                            <Button
                                variant="ghost"
                                size="sm"
                                className="h-8 px-2 text-xs font-medium"
                                onClick={() => setSpeed(s => s === 1 ? 1.5 : s === 1.5 ? 2 : 1)}
                            >
                                {speed}x
                            </Button>
                        </div>
                    </div>
                </div>

                {/* Transcript */}
                <div className="flex-1 overflow-y-auto p-8 bg-background relative">
                    <div className="max-w-2xl mx-auto space-y-6 pb-20">
                        {transcript.map((line, i) => (
                            <div
                                key={i}
                                className={cn(
                                    "transition-all duration-300 cursor-pointer hover:bg-muted/50 p-2 -mx-2 rounded",
                                    line.active ? "opacity-100 scale-105 origin-left" : "opacity-40 hover:opacity-70"
                                )}
                            >
                                <span className="text-xs font-mono text-muted-foreground mr-4 select-none">{line.time}</span>
                                <span className={cn(
                                    "text-lg leading-relaxed",
                                    line.active ? "text-primary font-medium" : "text-foreground"
                                )}>
                                    {line.text}
                                </span>
                            </div>
                        ))}
                    </div>
                    <div className="absolute bottom-0 left-0 w-full h-24 bg-gradient-to-t from-background to-transparent pointer-events-none" />
                </div>
            </div>
        </div>
    )
}
