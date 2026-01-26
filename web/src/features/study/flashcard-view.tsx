"use client";

import * as React from "react";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { KnowledgeLineage } from "./knowledge-lineage";
import { RotateCw } from "lucide-react";

export function FlashcardView() {
    const [isFlipped, setIsFlipped] = React.useState(false);

    return (
        <div className="flex h-full flex-col items-center justify-center p-8 bg-slate-50 dark:bg-slate-950/50">
            {/* Progress Bar */}
            <div className="w-full max-w-2xl mb-8 space-y-2">
                <div className="flex items-center justify-between text-xs text-muted-foreground">
                    <span>Daily Progress</span>
                    <span>12 / 45</span>
                </div>
                <Progress value={25} className="h-1" />
            </div>

            {/* Main Card */}
            <div className="relative h-[400px] w-full max-w-2xl perspective-1000 group">
                <div
                    className="relative h-full w-full transition-transform duration-500 transform-style-3d cursor-pointer"
                    style={{ transform: isFlipped ? 'rotateY(180deg)' : '' }}
                    onClick={() => setIsFlipped(!isFlipped)}
                >
                    {/* Front */}
                    <div className="absolute inset-0 flex flex-col items-center justify-center rounded-2xl border bg-card p-12 text-center shadow-xl backface-hidden">
                        <div className="text-sm font-semibold uppercase tracking-widest text-muted-foreground mb-6">Question</div>
                        <h3 className="text-3xl font-bold leading-tight">
                            "Wealth is assets that earn while you sleep."
                        </h3>
                    </div>

                    {/* Back */}
                    <div
                        className="absolute inset-0 flex flex-col items-center justify-center rounded-2xl border bg-card p-12 text-center shadow-xl backface-hidden rotate-y-180"
                    >
                        <h3 className="text-xl leading-relaxed text-muted-foreground mb-8">
                            True. This distinguishes wealth from money (transfer of time) and status (social hierarchy).
                        </h3>

                        <div className="absolute bottom-8 left-0 w-full flex justify-center">
                            <KnowledgeLineage />
                        </div>
                    </div>
                </div>
            </div>

            {/* Controls */}
            <div className="mt-12 flex items-center gap-4">
                <Button
                    variant="outline"
                    className="w-32 hover:bg-red-50 hover:text-red-500 hover:border-red-200 dark:hover:bg-red-950/20"
                >
                    Forgot
                    <span className="ml-2 text-xs opacity-50">1m</span>
                </Button>
                <Button
                    variant="outline"
                    className="w-32 hover:bg-yellow-50 hover:text-yellow-600 hover:border-yellow-200 dark:hover:bg-yellow-900/20"
                >
                    Hard
                    <span className="ml-2 text-xs opacity-50">10m</span>
                </Button>
                <Button
                    variant="outline"
                    className="w-32 hover:bg-green-50 hover:text-green-600 hover:border-green-200 dark:hover:bg-green-900/20"
                >
                    Easy
                    <span className="ml-2 text-xs opacity-50">4d</span>
                </Button>
            </div>

            <p className="mt-8 text-xs text-muted-foreground flex items-center gap-1.5 opacity-50">
                <RotateCw className="h-3 w-3" />
                Press Space to flip
            </p>
        </div>
    );
}
