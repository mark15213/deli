"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { Home, Rss, Inbox, Layers, Brain, ChevronLeft, ChevronRight } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { useState } from "react"
import { ThemeToggle } from "@/components/shared/ThemeToggle"

const sidebarItems = [
    {
        title: "Home",
        href: "/",
        icon: Home,
    },
    {
        title: "Feed",
        href: "/sources",
        icon: Rss,
    },
    {
        title: "Inbox",
        href: "/inbox",
        icon: Inbox,
    },
    {
        title: "Decks",
        href: "/decks",
        icon: Layers,
    },
    {
        title: "Learn",
        href: "/study",
        icon: Brain,
    },
]

export function Sidebar() {
    const pathname = usePathname()
    const [collapsed, setCollapsed] = useState(false)

    return (
        <aside
            className={cn(
                "relative flex flex-col border-r bg-card transition-all duration-300 ease-in-out",
                collapsed ? "w-16" : "w-64"
            )}
        >
            <div className="flex h-16 items-center border-b px-4 justify-between">
                {!collapsed && (
                    <span className="text-xl font-bold text-primary">
                        Deli
                    </span>
                )}
                <Button
                    variant="ghost"
                    size="icon"
                    className={cn("ml-auto", collapsed && "mx-auto")}
                    onClick={() => setCollapsed(!collapsed)}
                >
                    {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
                </Button>
            </div>

            <div className="flex-1 py-4">
                <nav className="grid gap-1 px-2">
                    {sidebarItems.map((item, index) => {
                        const isActive = pathname === item.href
                        return (
                            <Link
                                key={index}
                                href={item.href}
                                className={cn(
                                    "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground",
                                    isActive ? "bg-accent text-accent-foreground" : "text-muted-foreground",
                                    collapsed && "justify-center px-2"
                                )}
                                title={collapsed ? item.title : undefined}
                            >
                                <item.icon className="h-4 w-4" />
                                {!collapsed && <span>{item.title}</span>}
                            </Link>
                        )
                    })}
                </nav>
            </div>

            <div className="border-t p-4">
                <div className={cn("flex items-center gap-3", collapsed ? "justify-center" : "justify-between")}>
                    {!collapsed && <span className="text-sm text-muted-foreground">Theme</span>}
                    <ThemeToggle />
                </div>
            </div>
        </aside>
    )
}
