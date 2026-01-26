"use client"

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { ModeToggle } from "@/components/mode-toggle"
import { ScrollArea } from "@/components/ui/scroll-area"
import {
    Search,
    Database,
    Inbox,
    GraduationCap,
    Settings,
    UserCircle
} from "lucide-react"
import { useNavigationStore, ViewType } from "@/store/use-navigation"

interface SidebarProps extends React.HTMLAttributes<HTMLDivElement> { }

export function Sidebar({ className }: SidebarProps) {
    const { currentView, setCurrentView } = useNavigationStore()

    const navItems: { id: ViewType; label: string; icon: React.ReactNode }[] = [
        { id: 'sources', label: 'Source Hub', icon: <Database className="mr-2 h-4 w-4" /> },
        { id: 'inbox', label: 'Insight Inbox', icon: <Inbox className="mr-2 h-4 w-4" /> },
        { id: 'study', label: 'Study Mode', icon: <GraduationCap className="mr-2 h-4 w-4" /> },
    ]

    return (
        <div className={cn("flex flex-col h-full bg-background border-r", className)}>
            <div className="p-4 h-14 flex items-center justify-between border-b">
                <h2 className="font-semibold text-lg tracking-tight flex items-center gap-2">
                    Gulp
                </h2>
                <Button variant="ghost" size="icon" className="h-8 w-8">
                    <Search className="h-4 w-4" />
                </Button>
            </div>

            <ScrollArea className="flex-1 px-2 py-4">
                <div className="space-y-1">
                    {navItems.map((item) => (
                        <Button
                            key={item.id}
                            variant={currentView === item.id ? "secondary" : "ghost"}
                            className="w-full justify-start font-medium"
                            onClick={() => setCurrentView(item.id)}
                        >
                            {item.icon}
                            {item.label}
                        </Button>
                    ))}
                </div>
            </ScrollArea>

            <div className="mt-auto p-4 border-t space-y-2">
                <div className="flex items-center justify-between">
                    <Button variant="ghost" size="sm" className="w-full justify-start px-2">
                        <UserCircle className="mr-2 h-4 w-4" />
                        User
                    </Button>
                    <ModeToggle />
                </div>
                <Button variant="ghost" size="sm" className="w-full justify-start px-2 text-muted-foreground">
                    <Settings className="mr-2 h-4 w-4" />
                    Settings
                </Button>
            </div>
        </div>
    )
}
