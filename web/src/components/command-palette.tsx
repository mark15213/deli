"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import {
    Command,
    Search,
    Database,
    Inbox,
    GraduationCap,
    Settings,
    FileText,
    Github,
    Twitter
} from "lucide-react";
import { Dialog, DialogContent } from "@/components/ui/modal";
import { Input } from "@/components/ui/input";
import { useUIStore } from "@/store/ui-store";

export function CommandPalette() {
    const { commandPaletteOpen, setCommandPaletteOpen } = useUIStore();
    const router = useRouter();

    React.useEffect(() => {
        const down = (e: KeyboardEvent) => {
            if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
                e.preventDefault();
                setCommandPaletteOpen(!commandPaletteOpen);
            }
        };
        document.addEventListener("keydown", down);
        return () => document.removeEventListener("keydown", down);
    }, [setCommandPaletteOpen]);

    const navigate = (path: string) => {
        router.push(path);
        setCommandPaletteOpen(false);
    };

    if (!commandPaletteOpen) return null;

    return (
        <Dialog open={commandPaletteOpen} onOpenChange={setCommandPaletteOpen}>
            <DialogContent className="p-0 overflow-hidden max-w-2xl bg-popover text-popover-foreground">
                <div className="flex items-center border-b px-3">
                    <Search className="mr-2 h-4 w-4 shrink-0 opacity-50" />
                    <Input
                        placeholder="Type a command or search..."
                        className="flex h-11 w-full rounded-md bg-transparent py-3 text-sm outline-none placeholder:text-muted-foreground border-none ring-0 shadow-none focus-visible:ring-0"
                        autoFocus
                    />
                </div>
                <div className="max-h-[300px] overflow-y-auto p-2">
                    <div className="px-2 py-1.5 text-xs font-medium text-muted-foreground text-left">
                        Navigation
                    </div>
                    <div
                        className="flex cursor-pointer items-center rounded-sm px-2 py-1.5 text-sm outline-none aria-selected:bg-accent aria-selected:text-accent-foreground hover:bg-accent hover:text-accent-foreground"
                        onClick={() => navigate("/sources")}
                    >
                        <Database className="mr-2 h-4 w-4" />
                        <span>Source Hub</span>
                    </div>
                    <div
                        className="flex cursor-pointer items-center rounded-sm px-2 py-1.5 text-sm outline-none aria-selected:bg-accent aria-selected:text-accent-foreground hover:bg-accent hover:text-accent-foreground"
                        onClick={() => navigate("/inbox")}
                    >
                        <Inbox className="mr-2 h-4 w-4" />
                        <span>Insight Inbox</span>
                    </div>
                    <div
                        className="flex cursor-pointer items-center rounded-sm px-2 py-1.5 text-sm outline-none aria-selected:bg-accent aria-selected:text-accent-foreground hover:bg-accent hover:text-accent-foreground"
                        onClick={() => navigate("/study")}
                    >
                        <GraduationCap className="mr-2 h-4 w-4" />
                        <span>Study Mode</span>
                    </div>

                    <div className="px-2 py-1.5 text-xs font-medium text-muted-foreground text-left mt-2">
                        Recent Sources
                    </div>
                    <div className="flex cursor-pointer items-center rounded-sm px-2 py-1.5 text-sm outline-none aria-selected:bg-accent aria-selected:text-accent-foreground hover:bg-accent hover:text-accent-foreground">
                        <Twitter className="mr-2 h-4 w-4 text-blue-400" />
                        <span>@naval</span>
                    </div>
                    <div className="flex cursor-pointer items-center rounded-sm px-2 py-1.5 text-sm outline-none aria-selected:bg-accent aria-selected:text-accent-foreground hover:bg-accent hover:text-accent-foreground">
                        <FileText className="mr-2 h-4 w-4 text-red-500" />
                        <span>Arxiv: Agents Paper</span>
                    </div>
                </div>
            </DialogContent>
        </Dialog>
    );
}
