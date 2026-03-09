"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { Layers, Library, Zap, Settings, PanelLeftClose, PanelLeftOpen } from "lucide-react"
import Image from "next/image"
import { useState } from "react"

import { cn } from "@/lib/utils"

const navigation = [
    { name: "Feed", href: "/feed", icon: Layers },
    { name: "Knowledge", href: "/knowledge", icon: Library },
    { name: "Gulp", href: "/gulp", icon: Zap },
]

export function Sidebar() {
    const pathname = usePathname()
    const [isCollapsed, setIsCollapsed] = useState(false)

    return (
        <div className={cn(
            "flex z-10 h-screen flex-col border-r border-border/40 bg-white/40 backdrop-blur-md py-6 shadow-sm transition-all duration-300",
            isCollapsed ? "w-20 px-3 flex items-center" : "w-64 px-4"
        )}>
            <div className={cn("flex items-center mb-8", isCollapsed ? "justify-center px-0" : "gap-3 px-2 justify-between")}>
                <div className="flex items-center gap-3">
                    <div className="h-8 w-8 relative flex-shrink-0">
                        <Image src="/logo.png" alt="Gulp Logo" fill className="object-contain drop-shadow-sm" />
                    </div>
                    {!isCollapsed && <span className="text-xl font-bold tracking-tight text-zinc-900 drop-shadow-sm shrink-0">Gulp</span>}
                </div>
                <button
                    onClick={() => setIsCollapsed(!isCollapsed)}
                    className={cn(
                        "text-zinc-400 hover:text-zinc-600 transition-colors p-1 rounded-md hover:bg-zinc-100",
                        isCollapsed && "hidden"
                    )}
                >
                    <PanelLeftClose className="h-5 w-5" />
                </button>
            </div>

            {/* If collapsed, maybe we want a way to open it again at the top or bottom. We'll put it at the top below the logo if collapsed. */}
            {isCollapsed && (
                <button
                    onClick={() => setIsCollapsed(false)}
                    className="text-zinc-400 hover:text-zinc-600 transition-colors p-2 rounded-md hover:bg-zinc-100 mb-6 flex justify-center w-full"
                >
                    <PanelLeftOpen className="h-5 w-5" />
                </button>
            )}

            <nav className="flex-1 space-y-2 w-full">
                {navigation.map((item) => {
                    const isActive = pathname === item.href || pathname.startsWith(item.href + "/")
                    return (
                        <Link
                            key={item.href}
                            href={item.href}
                            title={isCollapsed ? item.name : undefined}
                            className={cn(
                                "flex items-center rounded-md text-sm font-medium transition-all cursor-pointer",
                                isCollapsed ? "justify-center p-3" : "gap-3 px-3 py-2",
                                isActive
                                    ? "bg-white text-zinc-900 shadow-sm border border-zinc-200"
                                    : "text-zinc-500 hover:bg-white/60 hover:text-zinc-900"
                            )}
                        >
                            <item.icon className={cn(isCollapsed ? "h-5 w-5" : "h-4 w-4", isActive ? "text-zinc-900" : "text-zinc-500")} />
                            {!isCollapsed && <span>{item.name}</span>}
                        </Link>
                    )
                })}
            </nav>

            <div className="mt-auto w-full">
                <button
                    title={isCollapsed ? "Settings" : undefined}
                    className={cn(
                        "flex w-full items-center rounded-md text-sm font-medium text-zinc-500 transition-colors hover:bg-white/60 hover:text-zinc-900 cursor-pointer",
                        isCollapsed ? "justify-center p-3" : "gap-3 px-3 py-2"
                    )}
                >
                    <Settings className={cn(isCollapsed ? "h-5 w-5" : "h-4 w-4")} />
                    {!isCollapsed && <span>Settings</span>}
                </button>
            </div>
        </div>
    )
}
