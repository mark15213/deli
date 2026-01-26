"use client"

import { InboxItem } from "@/components/inbox/InboxItem"
import { SourceCompareDrawer } from "@/components/inbox/SourceCompareDrawer"
import { useState } from "react"

const MOCK_ITEMS = [
    {
        id: "1",
        source: "Naval Ravikant on X",
        sourceType: "twitter" as const,
        title: "How to Get Rich (without getting lucky)",
        summary: "Seek wealth, not money or status. Wealth is having assets that earn while you sleep. Money is how we transfer time and wealth. Status is your place in the social hierarchy.",
        generatedContent: { flashcards: 5, quizzes: 1 },
        timestamp: "2h ago"
    },
    {
        id: "2",
        source: "Paul Graham Essay",
        sourceType: "article" as const,
        title: "Superlinear Returns",
        summary: "One of the most important things you can understand about the world is that returns for performance are superlinear. Teachers and coaches implicitly tell us returns are linear.",
        generatedContent: { flashcards: 3, audio: true },
        timestamp: "5h ago"
    },
    {
        id: "3",
        source: "Huberman Lab #85",
        sourceType: "podcast" as const,
        title: "Optimizing Workspace for Productivity",
        summary: "Key protocols for setting up your work environment: lighting, desk height, sound control, and visual field optimization to enhance focus and reduce fatigue.",
        generatedContent: { flashcards: 8, quizzes: 2, audio: true },
        timestamp: "1d ago"
    }
]

export default function InboxPage() {
    const [selectedItem, setSelectedItem] = useState<typeof MOCK_ITEMS[0] | null>(null)

    return (
        <div className="flex h-full bg-background relative">
            {/* List Connection */}
            <div className="flex-1 flex flex-col min-w-0">
                <div className="flex items-center justify-between px-8 py-6 border-b bg-card">
                    <div>
                        <h1 className="text-2xl font-bold tracking-tight">Insight Inbox</h1>
                        <p className="text-muted-foreground mt-1">Review and process AI-generated knowledge assets</p>
                    </div>
                    <div className="text-sm text-muted-foreground">
                        <span className="font-medium text-foreground">3</span> pending items
                    </div>
                </div>

                <div className="flex-1 overflow-y-auto">
                    {MOCK_ITEMS.map(item => (
                        <InboxItem
                            key={item.id}
                            {...item}
                            onClick={() => setSelectedItem(item)}
                            selected={selectedItem?.id === item.id}
                        />
                    ))}
                </div>
            </div>

            {/* Split Drawer */}
            <SourceCompareDrawer
                isOpen={!!selectedItem}
                onClose={() => setSelectedItem(null)}
                item={selectedItem}
            />
        </div>
    )
}
