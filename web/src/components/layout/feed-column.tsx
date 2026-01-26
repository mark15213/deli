"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

interface FeedColumnProps {
    children: React.ReactNode;
    className?: string;
}

export function FeedColumn({ children, className }: FeedColumnProps) {
    return (
        <div
            className={cn(
                "w-[400px] flex-shrink-0 border-r bg-background overflow-y-auto",
                className
            )}
        >
            {children}
        </div>
    );
}
