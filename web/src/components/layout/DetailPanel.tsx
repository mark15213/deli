"use client"

import * as React from "react"
import { cn } from "@/lib/utils"

export interface DetailPanelProps extends React.HTMLAttributes<HTMLDivElement> {
    children?: React.ReactNode
    isOpen?: boolean
    onClose?: () => void
}

export function DetailPanel({
    children,
    className,
    isOpen = false,
    onClose,
    ...props
}: DetailPanelProps) {
    if (!isOpen) return null

    return (
        <div
            className={cn(
                "w-96 border-l bg-card h-full overflow-y-auto transition-all shadow-xl z-20",
                className
            )}
            {...props}
        >
            <div className="p-4">{children}</div>
        </div>
    )
}
