"use client"

import { Sidebar } from "./Sidebar"

export function MainLayout({ children }: { children: React.ReactNode }) {
    return (
        <div className="flex h-screen bg-background overflow-hidden">
            <Sidebar />
            <main className="flex-1 overflow-y-auto min-h-0 relative">
                {children}
            </main>
        </div>
    )
}
