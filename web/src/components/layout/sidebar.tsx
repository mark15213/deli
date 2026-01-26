"use client";

import * as React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
    Database,
    Inbox,
    GraduationCap,
    Settings,
    Search,
    Moon,
    Sun,
    Command,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { useTheme } from "@/components/theme-provider";
import { useUIStore } from "@/store/ui-store";

const navigation = [
    { name: "Source Hub", href: "/sources", icon: Database },
    { name: "Insight Inbox", href: "/inbox", icon: Inbox },
    { name: "Study Mode", href: "/study", icon: GraduationCap },
];

export function Sidebar() {
    const pathname = usePathname();
    const { theme, setTheme } = useTheme();
    const { setCommandPaletteOpen } = useUIStore();

    return (
        <aside className="flex h-full w-[260px] flex-col border-r bg-card">
            {/* Logo */}
            <div className="flex h-16 items-center gap-2 border-b px-6">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground font-bold">
                    G
                </div>
                <span className="text-xl font-semibold">Gulp</span>
            </div>

            {/* Search */}
            <div className="p-4">
                <Button
                    variant="outline"
                    className="w-full justify-start gap-2 text-muted-foreground"
                    onClick={() => setCommandPaletteOpen(true)}
                >
                    <Search className="h-4 w-4" />
                    <span className="flex-1 text-left">Search...</span>
                    <kbd className="flex items-center gap-1 rounded border bg-muted px-1.5 text-xs">
                        <Command className="h-3 w-3" />K
                    </kbd>
                </Button>
            </div>

            {/* Navigation */}
            <nav className="flex-1 space-y-1 px-3">
                {navigation.map((item) => {
                    const isActive = pathname === item.href || pathname?.startsWith(item.href + "/");
                    return (
                        <Link
                            key={item.name}
                            href={item.href}
                            className={cn(
                                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                                isActive
                                    ? "bg-accent text-accent-foreground"
                                    : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                            )}
                        >
                            <item.icon className="h-5 w-5" />
                            {item.name}
                        </Link>
                    );
                })}
            </nav>

            {/* Footer */}
            <div className="border-t p-4 space-y-2">
                {/* Dark Mode Toggle */}
                <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
                    className="w-full justify-start gap-3"
                >
                    {theme === "dark" ? (
                        <Sun className="h-4 w-4" />
                    ) : (
                        <Moon className="h-4 w-4" />
                    )}
                    <span>{theme === "dark" ? "Light Mode" : "Dark Mode"}</span>
                </Button>

                {/* Settings */}
                <Link href="/settings">
                    <Button
                        variant="ghost"
                        size="sm"
                        className="w-full justify-start gap-3"
                    >
                        <Settings className="h-4 w-4" />
                        <span>Settings</span>
                    </Button>
                </Link>
            </div>
        </aside>
    );
}
