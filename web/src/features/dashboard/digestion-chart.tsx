"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

interface DigestionChartProps {
    input?: number;
    learned?: number;
    className?: string;
}

export function DigestionChart({ input = 50, learned = 20, className }: DigestionChartProps) {
    const percentage = Math.round((learned / input) * 100);
    const radius = 40;
    const circumference = 2 * Math.PI * radius;
    const strokeDashoffset = circumference - (percentage / 100) * circumference;

    return (
        <div className={cn("flex items-center gap-6", className)}>
            <div className="relative h-32 w-32">
                <svg className="h-full w-full -rotate-90 transform" viewBox="0 0 100 100">
                    {/* Background Circle */}
                    <circle
                        className="text-muted/20"
                        strokeWidth="12"
                        stroke="currentColor"
                        fill="transparent"
                        r={radius}
                        cx="50"
                        cy="50"
                    />
                    {/* Progress Circle */}
                    <circle
                        className="text-primary transition-all duration-1000 ease-out"
                        strokeWidth="12"
                        strokeDasharray={circumference}
                        strokeDashoffset={strokeDashoffset}
                        strokeLinecap="round"
                        stroke="currentColor"
                        fill="transparent"
                        r={radius}
                        cx="50"
                        cy="50"
                    />
                </svg>
                {/* Center Text */}
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span className="text-2xl font-bold">{percentage}%</span>
                    <span className="text-[10px] text-muted-foreground uppercase">Digested</span>
                </div>
            </div>

            <div className="space-y-4">
                <div className="space-y-1">
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <div className="h-2 w-2 rounded-full bg-primary" />
                        <span>Absorbed</span>
                        <span className="ml-auto font-medium text-foreground">{learned}</span>
                    </div>
                </div>
                <div className="space-y-1">
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <div className="h-2 w-2 rounded-full bg-muted/20" />
                        <span>Remaining</span>
                        <span className="ml-auto font-medium text-foreground">{input - learned}</span>
                    </div>
                </div>
            </div>
        </div>
    );
}
