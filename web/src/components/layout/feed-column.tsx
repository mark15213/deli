"use client"

import { cn } from "@/lib/utils"
import { useNavigationStore } from "@/store/use-navigation"
import { SourceGrid } from "@/features/sources/SourceGrid"
import { InboxList } from "@/features/inbox/InboxList"
import { StudyList } from "@/features/study/StudyList"

interface FeedColumnProps extends React.HTMLAttributes<HTMLDivElement> { }

export function FeedColumn({ className }: FeedColumnProps) {
    const { currentView } = useNavigationStore()

    return (
        <div className={cn("flex flex-col h-full bg-background/50", className)}>
            {currentView === 'sources' && <SourceGrid />}
            {currentView === 'inbox' && <InboxList />}
            {currentView === 'study' && <StudyList />}
        </div>
    )
}
