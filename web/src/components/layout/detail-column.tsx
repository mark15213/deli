"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

interface DetailColumnProps {
    children: React.ReactNode;
    className?: string;
}

export function DetailColumn({ children, className }: DetailColumnProps) {
    return (
        <div
            className={cn(
                "flex-1 overflow-y-auto bg-background",
                className
            )}
        >
            {children}
        </div>
    );
}
