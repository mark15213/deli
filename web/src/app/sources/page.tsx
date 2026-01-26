"use client"

import { QuickAddModal } from "@/components/sources/QuickAddModal"
import { ConnectorCard } from "@/components/sources/ConnectorCard"
import { StatusStream } from "@/components/sources/StatusStream"
import { SourceDetailDrawer } from "@/components/sources/SourceDetailDrawer"
import { Twitter, AppWindow, Rss, FileText } from "lucide-react"
import { useState } from "react"

export default function SourcesPage() {
    const [selectedSource, setSelectedSource] = useState<string | null>(null)

    return (
        <div className="flex flex-col h-full bg-slate-50/50 dark:bg-zinc-950 relative">
            <div className="flex items-center justify-between px-8 py-6 border-b bg-card">
                <div>
                    <h1 className="text-2xl font-bold tracking-tight">Source Hub</h1>
                    <p className="text-muted-foreground mt-1">Manage all your knowledge inputs and connections</p>
                </div>
                <QuickAddModal />
            </div>

            <StatusStream />

            <div className="flex-1 overflow-y-auto p-8">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    <ConnectorCard
                        name="X / Twitter"
                        icon={<Twitter className="h-6 w-6" />}
                        status="syncing"
                        lastSync="2 mins ago"
                        description="Auto-sync bookmarks and threads from connected accounts."
                        onClick={() => setSelectedSource("twitter")}
                    />
                    <ConnectorCard
                        name="Notion"
                        icon={<AppWindow className="h-6 w-6" />}
                        status="active"
                        lastSync="1 hour ago"
                        description="Import pages from 'Reading List' database."
                        onClick={() => setSelectedSource("notion")}
                    />
                    <ConnectorCard
                        name="RSS Feeds"
                        icon={<Rss className="h-6 w-6" />}
                        status="active"
                        lastSync="10 mins ago"
                        description="Tech, AI, and Philosophy feeds aggregator."
                        onClick={() => setSelectedSource("rss")}
                    />
                    <ConnectorCard
                        name="Manual Notes"
                        icon={<FileText className="h-6 w-6" />}
                        status="active"
                        lastSync="Just now"
                        description="Direct input notes and quick captures."
                        onClick={() => setSelectedSource("notes")}
                    />
                </div>
            </div>

            <SourceDetailDrawer
                isOpen={!!selectedSource}
                onClose={() => setSelectedSource(null)}
                sourceId={selectedSource}
            />
        </div>
    )
}
