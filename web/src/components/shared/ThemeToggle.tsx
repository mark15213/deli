"use client"

import * as React from "react"
import { Moon, Sun } from "lucide-react"
import { useTheme } from "next-themes"
import { cn } from "@/lib/utils"

export function ThemeToggle({ className }: { className?: string }) {
    const { setTheme, theme } = useTheme()

    return (
        <button
            className={cn(
                "inline-flex h-9 w-9 items-center justify-center rounded-md border border-input bg-transparent shadow-sm hover:bg-accent hover:text-accent-foreground active:scale-95 transition-all text-sm font-medium",
                className
            )}
            onClick={() => setTheme(theme === "light" ? "dark" : "light")}
            title="Toggle theme"
        >
            <Sun className="h-[1.2rem] w-[1.2rem] rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
            <Moon className="absolute h-[1.2rem] w-[1.2rem] rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
            <span className="sr-only">Toggle theme</span>
        </button>
    )
}
