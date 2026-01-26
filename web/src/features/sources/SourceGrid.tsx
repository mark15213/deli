"use client"

import { useState } from "react"
import { Plus, Twitter, Rss, Github, BookOpen, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { SourceConfigSheet } from "./SourceConfigSheet"

const sources = [
    { id: "1", type: "twitter", name: "@naval", status: "syncing", items: 12 },
    { id: "2", type: "rss", name: "Paul Graham", status: "idle", items: 5 },
    { id: "3", type: "github", name: "langchain-ai", status: "error", items: 0 },
    { id: "4", type: "arxiv", name: "LLM Agents", status: "idle", items: 42 },
]

export function SourceGrid() {
    const [selectedSource, setSelectedSource] = useState<string | null>(null)
    const [sheetOpen, setSheetOpen] = useState(false)

    const handleSourceClick = (id: string) => {
        setSelectedSource(id)
        setSheetOpen(true)
    }

    return (
        <div className="h-full flex flex-col">
            {/* Status Stream */}
            <div className="h-8 bg-muted/30 border-b flex items-center px-4 overflow-hidden">
                <div className="flex items-center gap-2 text-xs text-muted-foreground animate-pulse">
                    <Loader2 className="h-3 w-3 animate-spin" />
                    <span>Analyzing @naval latest threads... Generating 3 cards</span>
                </div>
            </div>

            <div className="p-4 space-y-4">
                <div className="flex items-center justify-between">
                    <h3 className="font-semibold">My Sources</h3>
                    <Button size="sm" className="gap-1">
                        <Plus className="h-4 w-4" /> Quick Add
                    </Button>
                </div>

                <div className="grid grid-cols-1 gap-3">
                    {sources.map((source) => (
                        <Card
                            key={source.id}
                            className="cursor-pointer hover:bg-muted/50 transition-colors group"
                            onClick={() => handleSourceClick(source.id)}
                        >
                            <CardContent className="p-4 flex items-center gap-4">
                                <div className="h-10 w-10 rounded-full bg-muted flex items-center justify-center shrink-0">
                                    {source.type === 'twitter' && <Twitter className="h-5 w-5" />}
                                    {source.type === 'rss' && <Rss className="h-5 w-5" />}
                                    {source.type === 'github' && <Github className="h-5 w-5" />}
                                    {source.type === 'arxiv' && <BookOpen className="h-5 w-5" />}
                                </div>
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-2">
                                        <h4 className="font-medium truncate">{source.name}</h4>
                                        {source.status === 'syncing' && <span className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />}
                                        {source.status === 'error' && <span className="h-2 w-2 rounded-full bg-destructive" />}
                                    </div>
                                    <p className="text-xs text-muted-foreground">{source.items} items ingested</p>
                                </div>
                                <Badge variant="secondary" className="group-hover:bg-background">
                                    {source.type}
                                </Badge>
                            </CardContent>
                        </Card>
                    ))}
                </div>
            </div>

            <SourceConfigSheet
                open={sheetOpen}
                onOpenChange={setSheetOpen}
                sourceId={selectedSource}
            />
        </div>
    )
}
