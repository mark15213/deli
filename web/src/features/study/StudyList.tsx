"use client"

import { useNavigationStore } from "@/store/use-navigation"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { cn } from "@/lib/utils"
import { Play, Copy } from "lucide-react"

const studyItems = [
    {
        id: "1",
        type: "flashcard",
        title: "LLM Reasoning",
        count: 12,
        progress: 45,
        dueDate: "Today",
    },
    {
        id: "2",
        type: "audio",
        title: "Daily Briefing: AI News",
        duration: "15 min",
        progress: 0,
        dueDate: "Today",
    },
    {
        id: "3",
        type: "flashcard",
        title: "React Server Components",
        count: 8,
        progress: 80,
        dueDate: "Tomorrow",
    },
]

export function StudyList() {
    const { activeStudyType, setActiveStudyType } = useNavigationStore()

    return (
        <div className="h-full flex flex-col">
            <div className="p-4 border-b h-14 flex items-center justify-between">
                <span className="font-semibold">Study Plan</span>
            </div>
            <ScrollArea className="flex-1">
                <div className="flex flex-col">
                    {studyItems.map((item) => (
                        <div
                            key={item.id}
                            className={cn(
                                "flex flex-col gap-2 p-4 border-b cursor-pointer hover:bg-muted/50 transition-colors",
                                activeStudyType === item.type && "bg-muted"
                            )}
                            onClick={() => setActiveStudyType(item.type as any)}
                        >
                            <div className="flex items-center justify-between mb-1">
                                <Badge variant={item.type === 'audio' ? "default" : "outline"} className="text-[10px] h-5 px-1.5 uppercase font-bold">
                                    {item.type}
                                </Badge>
                                <span className="text-xs text-muted-foreground font-medium text-orange-500">{item.dueDate}</span>
                            </div>

                            <h4 className="font-semibold text-sm leading-tight">{item.title}</h4>

                            <div className="flex items-center gap-2 text-xs text-muted-foreground mt-1">
                                {item.type === 'flashcard' && <Copy className="h-3 w-3" />}
                                {item.type === 'audio' && <Play className="h-3 w-3" />}

                                {item.type === 'flashcard' && <span>{item.count} Cards • {item.progress}% done</span>}
                                {item.type === 'audio' && <span>{item.duration} • Not started</span>}
                            </div>
                        </div>
                    ))}
                </div>
            </ScrollArea>
        </div>
    )
}
