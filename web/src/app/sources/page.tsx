"use client"

import { QuickAddModal } from "@/components/sources/QuickAddModal"
import { ConnectorCard } from "@/components/sources/ConnectorCard"
import { StatusStream } from "@/components/sources/StatusStream"
import { SourceDetailDrawer } from "@/components/sources/SourceDetailDrawer"
import { Twitter, AppWindow, Rss, FileText, Wifi, Github } from "lucide-react"
import { useState, useEffect } from "react"
import { getSources } from "@/lib/api/sources"
import { Source, SourceType } from "@/types/source"

export default function SourcesPage() {
    const [selectedSource, setSelectedSource] = useState<string | null>(null)
    const [sources, setSources] = useState<Source[]>([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        loadSources()
    }, [])

    const loadSources = async () => {
        try {
            setLoading(true)
            const data = await getSources()
            setSources(data)
        } catch (e) {
            console.error("Failed to load sources", e)
        } finally {
            setLoading(false)
        }
    }

    const getSourceConfig = (type: SourceType) => {
        switch (type) {
            case 'X_SOCIAL': return { icon: <Twitter className="h-6 w-6" />, description: "Auto-sync bookmarks and threads." };
            case 'NOTION_KB': return { icon: <AppWindow className="h-6 w-6" />, description: "Import pages from workspace." };
            case 'WEB_RSS': return { icon: <Rss className="h-6 w-6" />, description: "RSS feeds aggregator." };
            case 'ARXIV_PAPER': return { icon: <FileText className="h-6 w-6" />, description: "Research papers tracker." };
            case 'GITHUB_REPO': return { icon: <Github className="h-6 w-6" />, description: "Repository tracking." };
            default: return { icon: <Wifi className="h-6 w-6" />, description: "Connected source." };
        }
    }

    // Helper to format date relative
    const formatLastSync = (dateStr?: string) => {
        if (!dateStr) return "Never";
        const date = new Date(dateStr);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    return (
        <div className="flex flex-col h-full bg-slate-50/50 dark:bg-zinc-950 relative">
            <div className="flex items-center justify-between px-8 py-6 border-b bg-card">
                <div>
                    <h1 className="text-2xl font-bold tracking-tight">Feed</h1>
                    <p className="text-muted-foreground mt-1">Your content sources and subscriptions</p>
                </div>
                <QuickAddModal onSourceAdded={loadSources} />
            </div>

            <StatusStream />

            <div className="flex-1 overflow-y-auto p-8">
                {loading ? (
                    <div className="text-center text-muted-foreground py-10">Loading sources...</div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {sources.map(source => {
                            const config = getSourceConfig(source.type);
                            return (
                                <ConnectorCard
                                    key={source.id}
                                    name={source.name}
                                    icon={config.icon}
                                    status={source.status === 'ACTIVE' ? 'active' : source.status === 'ERROR' ? 'error' : 'syncing'}
                                    lastSync={formatLastSync(source.last_synced_at)}
                                    description={config.description}
                                    onClick={() => setSelectedSource(source.id)}
                                />
                            )
                        })}

                        {sources.length === 0 && (
                            <div className="col-span-full text-center text-muted-foreground py-10">
                                No sources found. Add one to get started.
                            </div>
                        )}
                    </div>
                )}
            </div>

            <SourceDetailDrawer
                isOpen={!!selectedSource}
                onClose={() => setSelectedSource(null)}
                sourceId={selectedSource}
                onDeleted={loadSources}
            />
        </div>
    )
}
