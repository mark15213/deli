"use client";

import * as React from "react";
import { X } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "./button";

interface SlideOverProps {
    open: boolean;
    onClose: () => void;
    title?: string;
    children: React.ReactNode;
    footer?: React.ReactNode;
    width?: "sm" | "md" | "lg";
}

const widthClasses = {
    sm: "max-w-sm",
    md: "max-w-md",
    lg: "max-w-lg",
};

export function SlideOver({
    open,
    onClose,
    title,
    children,
    footer,
    width = "lg",
}: SlideOverProps) {
    // Handle escape key
    React.useEffect(() => {
        const handleEscape = (e: KeyboardEvent) => {
            if (e.key === "Escape" && open) {
                onClose();
            }
        };
        document.addEventListener("keydown", handleEscape);
        return () => document.removeEventListener("keydown", handleEscape);
    }, [open, onClose]);

    // Prevent body scroll when open
    React.useEffect(() => {
        if (open) {
            document.body.style.overflow = "hidden";
        } else {
            document.body.style.overflow = "";
        }
        return () => {
            document.body.style.overflow = "";
        };
    }, [open]);

    if (!open) return null;

    return (
        <>
            {/* Backdrop */}
            <div
                className="fixed inset-0 z-40 bg-black/50 animate-fade-in"
                onClick={onClose}
            />

            {/* Panel */}
            <div
                className={cn(
                    "fixed inset-y-0 right-0 z-50 w-full bg-background shadow-xl animate-slide-in flex flex-col",
                    widthClasses[width]
                )}
            >
                {/* Header */}
                {title && (
                    <div className="flex items-center justify-between border-b px-6 py-4">
                        <h2 className="text-lg font-semibold">{title}</h2>
                        <Button
                            variant="ghost"
                            size="icon"
                            onClick={onClose}
                            className="h-8 w-8"
                        >
                            <X className="h-4 w-4" />
                        </Button>
                    </div>
                )}

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-6">{children}</div>

                {/* Footer */}
                {footer && (
                    <div className="border-t px-6 py-4">{footer}</div>
                )}
            </div>
        </>
    );
}
