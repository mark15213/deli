"use client";

import * as React from "react";
import { Sidebar } from "./sidebar";
import { CommandPalette } from "@/components/command-palette";
import { cn } from "@/lib/utils";

interface AppShellProps {
    children: React.ReactNode;
    className?: string;
}

export function AppShell({ children, className }: AppShellProps) {
    return (
        <div className={cn("flex h-screen overflow-hidden", className)}>
            <Sidebar />
            <main className="flex flex-1 overflow-hidden">
                {children}
            </main>
            <CommandPalette />
        </div>
    );
}
