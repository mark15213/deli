"use client";

import * as React from "react";
import { Play, SkipBack, SkipForward, Volume2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";

// Mock transcript
const transcript = [
    { time: 0, text: "Welcome to your daily briefing." },
    { time: 2, text: "Today, we're diving into Naval's latest thread on wealth creation." },
    { time: 6, text: "He starts by distinguishing between wealth, money, and status." },
    { time: 10, text: "Wealth is assets that earn while you sleep." },
    { time: 14, text: "Money is how we transfer time and wealth." },
    { time: 18, text: "Status is your place in the social hierarchy." },
];

export function TranscriptSync() {
    const [currentIdx, setCurrentIdx] = React.useState(3);

    return (
        <div className="flex-1 overflow-y-auto p-6">
            <div className="space-y-4 max-w-lg mx-auto">
                {transcript.map((line, i) => (
                    <div
                        key={i}
                        className={cn(
                            "p-3 rounded-lg transition-all cursor-pointer hover:bg-accent/50",
                            currentIdx === i ? "bg-primary/10 border-l-4 border-primary pl-4" : "text-muted-foreground"
                        )}
                        onClick={() => setCurrentIdx(i)}
                    >
                        <span className="text-xs font-mono opacity-50 mr-3">00:{String(line.time).padStart(2, '0')}</span>
                        <span className={cn(
                            "text-sm",
                            currentIdx === i && "font-medium text-foreground"
                        )}>{line.text}</span>
                    </div>
                ))}
            </div>
        </div>
    );
}

export function AudioPlayer() {
    return (
        <div className="flex flex-col h-full bg-background">
            <div className="flex-1 min-h-0 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center p-8 text-white relative overflow-hidden">
                {/* Visualizer Background Mock */}
                <div className="absolute bottom-0 left-0 right-0 h-32 flex items-end justify-center gap-1 opacity-20">
                    {[...Array(40)].map((_, i) => (
                        <div
                            key={i}
                            className="w-2 bg-white rounded-t-sm animate-pulse"
                            style={{
                                height: `${Math.random() * 80 + 20}%`,
                                animationDuration: `${Math.random() * 1 + 0.5}s`
                            }}
                        />
                    ))}
                </div>

                <div className="z-10 text-center space-y-6">
                    <div className="h-48 w-48 mx-auto bg-gradient-to-br from-purple-500 to-blue-500 rounded-2xl shadow-2xl flex items-center justify-center">
                        <span className="text-4xl">🎧</span>
                    </div>
                    <div>
                        <h2 className="text-2xl font-bold">Daily Briefing</h2>
                        <p className="text-slate-300">Naval, Paul Graham, and Arxiv</p>
                    </div>
                </div>
            </div>

            <div className="border-t bg-card p-6 space-y-6">
                {/* Progress */}
                <div className="space-y-2">
                    <div className="h-1 bg-secondary rounded-full overflow-hidden">
                        <div className="h-full w-1/3 bg-primary" />
                    </div>
                    <div className="flex justify-between text-xs text-muted-foreground">
                        <span>4:20</span>
                        <span>12:00</span>
                    </div>
                </div>

                {/* Controls */}
                <div className="flex items-center justify-center gap-8">
                    <Button variant="ghost" size="icon" className="h-10 w-10">
                        <SkipBack className="h-5 w-5" />
                    </Button>
                    <Button size="icon" className="h-14 w-14 rounded-full shadow-lg">
                        <Play className="h-6 w-6 ml-1" />
                    </Button>
                    <Button variant="ghost" size="icon" className="h-10 w-10">
                        <SkipForward className="h-5 w-5" />
                    </Button>
                </div>

                <div className="flex items-center justify-between">
                    <Button variant="ghost" size="sm" className="text-xs">
                        1.0x
                    </Button>
                    <div className="flex items-center gap-2">
                        <Volume2 className="h-4 w-4 text-muted-foreground" />
                        <div className="w-20 h-1 bg-secondary rounded-full">
                            <div className="w-3/4 h-full bg-primary rounded-full" />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
