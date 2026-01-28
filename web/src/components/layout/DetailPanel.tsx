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
    return (
        <>
            <div
                className={cn(
                    "fixed inset-0 z-10 bg-black/40 backdrop-blur-sm transition-opacity duration-300 ease-in-out",
                    isOpen ? "opacity-100" : "opacity-0 pointer-events-none"
                )}
                onClick={onClose}
                aria-hidden="true"
            />
            <div
                className={cn(
                    "w-96 border-l bg-card h-full overflow-y-auto z-20 fixed right-0 top-0 bottom-0 transition-transform duration-300 ease-in-out",
                    isOpen ? "translate-x-0 shadow-2xl" : "translate-x-full",
                    className
                )}
                onClick={(e) => e.stopPropagation()}
                {...props}
            >
                <div className="p-4">{children}</div>
            </div>
        </>
    )
}
