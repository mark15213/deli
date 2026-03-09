"use client"

import { useState } from "react"
import { FileText, Rss, ArrowRight, Clock } from "lucide-react"
import { AddSourceDialog } from "@/components/AddSourceDialog"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Workspace } from "@/components/Workspace"

// Mock Data
const MOCK_SOURCES = [
    {
        id: "1",
        type: "snapshot",
        title: "Attention Is All You Need",
        url: "https://arxiv.org/abs/1706.03762",
        addedAt: "2 hours ago",
        status: "processed"
    },
    {
        id: "2",
        type: "subscription",
        title: "HuggingFace Daily Papers",
        url: "https://huggingface.co/papers",
        addedAt: "Yesterday",
        status: "syncing",
        itemsCount: 12
    },
    {
        id: "3",
        type: "snapshot",
        title: "Understanding React Server Components",
        url: "https://vercel.com/blog/understanding-react-server-components",
        addedAt: "2 days ago",
        status: "processed"
    }
]

export default function FeedPage() {
    const [activeWorkspaceSource, setActiveWorkspaceSource] = useState<any>(null)

    if (activeWorkspaceSource) {
        return (
            <Workspace
                source={activeWorkspaceSource}
                onClose={() => setActiveWorkspaceSource(null)}
            />
        )
    }

    return (
        <div className="h-full flex flex-col p-8 bg-transparent">
            <div className="flex items-center justify-between mb-8 pb-4 border-b border-border/50">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight text-zinc-900 drop-shadow-sm">Feed</h1>
                    <p className="text-zinc-500 mt-2 text-sm font-medium">Manage your info sources and subscriptions.</p>
                </div>
                <AddSourceDialog />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 auto-rows-max overflow-y-auto pb-20">
                {MOCK_SOURCES.map((source) => (
                    <Card
                        key={source.id}
                        className="flex flex-col border-border/50 bg-white/80 backdrop-blur-sm shadow-sm hover:shadow-md hover:border-zinc-300 transition-all cursor-pointer group"
                        onClick={() => {
                            if (source.type === "snapshot") {
                                setActiveWorkspaceSource(source)
                            }
                        }}
                    >
                        <CardHeader className="pb-3">
                            <div className="flex justify-between items-start mb-2">
                                <Badge variant={source.type === "snapshot" ? "default" : "secondary"} className="mb-2">
                                    {source.type === "snapshot" ? "Snapshot" : "Subscription"}
                                </Badge>
                                {source.type === "snapshot" ? (
                                    <FileText className="h-4 w-4 text-muted-foreground" />
                                ) : (
                                    <Rss className="h-4 w-4 text-muted-foreground" />
                                )}
                            </div>
                            <CardTitle className="line-clamp-2 leading-snug group-hover:text-primary transition-colors">
                                {source.title}
                            </CardTitle>
                            <CardDescription className="line-clamp-1 mt-1">
                                {source.url}
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="flex-1">
                            {/* Content area if we wanted to show excerpts or recent items for subscriptions */}
                            {source.type === "subscription" && source.itemsCount && (
                                <div className="text-sm text-muted-foreground bg-muted/50 p-2 rounded-md">
                                    {source.itemsCount} unseen items
                                </div>
                            )}
                        </CardContent>
                        <CardFooter className="pt-3 border-t text-xs text-muted-foreground flex justify-between items-center">
                            <div className="flex items-center gap-1">
                                <Clock className="h-3 w-3" />
                                {source.addedAt}
                            </div>
                            {source.type === "snapshot" && (
                                <div className="flex items-center gap-1 text-primary opacity-0 group-hover:opacity-100 transition-opacity">
                                    Open Workspace <ArrowRight className="h-3 w-3" />
                                </div>
                            )}
                        </CardFooter>
                    </Card>
                ))}
            </div>
        </div>
    )
}
