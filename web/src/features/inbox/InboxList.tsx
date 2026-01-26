"use client"

import { useNavigationStore } from "@/store/use-navigation"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { cn } from "@/lib/utils"
import { Twitter, FileText, BookOpen } from "lucide-react"

const inboxItems = [
    {
        id: "1",
        source: "twitter",
        author: "@karpathy",
        summary: "Discussions on LLM tokenization and its impact on reasoning capabilities...",
        tags: ["Flashcard x3", "Summary"],
        time: "2h ago",
    },
    {
        id: "2",
        source: "arxiv",
        author: "DeepMind",
        summary: "AlphaGeometry: An Olympiad-level AI system for geometry...",
        tags: ["Flashcard x5", "Quiz"],
        time: "5h ago",
    },
    {
        id: "3",
        source: "web",
        author: "Paul Graham",
        summary: "How to do great work. The most important thing is to work on something you find interesting...",
        tags: ["Summary", "Action Plan"],
        time: "1d ago",
    },
]

export function InboxList() {
    const { activeInboxId, setActiveInboxId } = useNavigationStore()

    return (
        <div className="h-full flex flex-col">
            <div className="p-4 border-b h-14 flex items-center justify-between">
                <span className="font-semibold">Inbox ({inboxItems.length})</span>
            </div>
            <ScrollArea className="flex-1">
                <div className="flex flex-col">
                    {inboxItems.map((item) => (
                        <div
                            key={item.id}
                            className={cn(
                                "flex flex-col gap-2 p-4 border-b cursor-pointer hover:bg-muted/50 transition-colors",
                                activeInboxId === item.id && "bg-muted"
                            )}
                            onClick={() => setActiveInboxId(item.id)}
                        >
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
                                    {item.source === 'twitter' && <Twitter className="h-3 w-3" />}
                                    {item.source === 'arxiv' && <BookOpen className="h-3 w-3" />}
                                    {item.source === 'web' && <FileText className="h-3 w-3" />}
                                    <span>{item.author}</span>
                                </div>
                                <span className="text-xs text-muted-foreground">{item.time}</span>
                            </div>
                            <p className="text-sm line-clamp-2 font-medium leading-snug">
                                {item.summary}
                            </p>
                            <div className="flex gap-2 mt-1">
                                {item.tags.map(tag => (
                                    <Badge key={tag} variant="secondary" className="text-[10px] h-5 px-1.5 font-normal">
                                        {tag}
                                    </Badge>
                                ))}
                            </div>
                        </div>
                    ))}
                </div>
            </ScrollArea>
        </div>
    )
}
