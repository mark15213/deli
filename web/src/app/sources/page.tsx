"use client"

import { QuickAddModal } from "@/components/sources/QuickAddModal"
import { ConnectorCard } from "@/components/sources/ConnectorCard"
import { StatusStream } from "@/components/sources/StatusStream"
import { SourceDetailDrawer } from "@/components/sources/SourceDetailDrawer"
import { Twitter, AppWindow, Rss, FileText, Wifi, Github, ChevronDown, ChevronRight, FolderOpen, Newspaper, Folder } from "lucide-react"
import { useState, useEffect } from "react"
import { getSources, getChildSources } from "@/lib/api/sources"
import { Source, SourceType, isSubscriptionType } from "@/types/source"

export default function SourcesPage() {
    const [selectedSource, setSelectedSource] = useState<string | null>(null)
    const [sources, setSources] = useState<Source[]>([])
    const [loading, setLoading] = useState(true)
    const [expandedSources, setExpandedSources] = useState<Set<string>>(new Set())
    const [childrenMap, setChildrenMap] = useState<Record<string, Source[]>>({})
    const [loadingChildren, setLoadingChildren] = useState<Set<string>>(new Set())

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

    const toggleExpand = async (sourceId: string, e: React.MouseEvent) => {
        e.stopPropagation();
        const newExpanded = new Set(expandedSources)
        if (newExpanded.has(sourceId)) {
            newExpanded.delete(sourceId)
        } else {
            newExpanded.add(sourceId)
            // Load children if not already loaded
            if (!childrenMap[sourceId]) {
                setLoadingChildren(prev => new Set(prev).add(sourceId))
                try {
                    const children = await getChildSources(sourceId)
                    setChildrenMap(prev => ({ ...prev, [sourceId]: children }))
                } catch (e) {
                    console.error("Failed to load children", e)
                } finally {
                    setLoadingChildren(prev => {
                        const next = new Set(prev)
                        next.delete(sourceId)
                        return next
                    })
                }
            }
        }
        setExpandedSources(newExpanded)
    }

    const getSourceConfig = (type: SourceType) => {
        switch (type) {
            case 'X_SOCIAL': return { icon: <Twitter className="h-6 w-6" />, description: "Auto-sync bookmarks and threads." };
            case 'NOTION_KB': return { icon: <AppWindow className="h-6 w-6" />, description: "Import pages from workspace." };
            case 'WEB_RSS':
            case 'RSS_FEED': return { icon: <Rss className="h-6 w-6" />, description: "RSS feeds aggregator." };
            case 'ARXIV_PAPER': return { icon: <FileText className="h-6 w-6" />, description: "Research papers tracker." };
            case 'GITHUB_REPO': return { icon: <Github className="h-6 w-6" />, description: "Repository tracking." };
            case 'HF_DAILY_PAPERS': return { icon: <Newspaper className="h-6 w-6" />, description: "HuggingFace daily papers." };
            default: return { icon: <Wifi className="h-6 w-6" />, description: "Connected source." };
        }
    }

    const formatLastSync = (dateStr?: string) => {
        if (!dateStr) return "Never";
        const date = new Date(dateStr);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    // Separate subscription sources (folders) from regular sources
    const subscriptionSources = sources.filter(s => isSubscriptionType(s.type));
    const regularSources = sources.filter(s => !isSubscriptionType(s.type));

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

            <div className="flex-1 overflow-y-auto p-8 space-y-8">
                {loading ? (
                    <div className="text-center text-muted-foreground py-10">Loading sources...</div>
                ) : (
                    <>
                        {/* Subscription Folders Section */}
                        {subscriptionSources.length > 0 && (
                            <section>
                                <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                                    <Folder className="h-5 w-5 text-muted-foreground" />
                                    Subscriptions
                                </h2>
                                <div className="space-y-4">
                                    {subscriptionSources.map(source => {
                                        const config = getSourceConfig(source.type);
                                        const isExpanded = expandedSources.has(source.id);
                                        const hasChildren = (source.children_count || 0) > 0;
                                        const isLoadingThisChildren = loadingChildren.has(source.id);
                                        const children = childrenMap[source.id] || [];

                                        return (
                                            <div key={source.id} className="border rounded-lg bg-card overflow-hidden">
                                                {/* Folder Header */}
                                                <div
                                                    className="flex items-center gap-4 p-4 cursor-pointer hover:bg-muted/50 transition-colors"
                                                    onClick={(e) => hasChildren ? toggleExpand(source.id, e) : setSelectedSource(source.id)}
                                                >
                                                    {/* Expand/Collapse Icon */}
                                                    {hasChildren ? (
                                                        <button className="p-1 hover:bg-muted rounded">
                                                            {isExpanded ? (
                                                                <ChevronDown className="h-5 w-5 text-muted-foreground" />
                                                            ) : (
                                                                <ChevronRight className="h-5 w-5 text-muted-foreground" />
                                                            )}
                                                        </button>
                                                    ) : (
                                                        <div className="w-7" />
                                                    )}

                                                    {/* Icon */}
                                                    <div className="p-2 rounded-lg bg-primary/10 text-primary">
                                                        {isExpanded ? <FolderOpen className="h-6 w-6" /> : config.icon}
                                                    </div>

                                                    {/* Info */}
                                                    <div className="flex-1">
                                                        <h3 className="font-medium">{source.name}</h3>
                                                        <p className="text-sm text-muted-foreground">
                                                            {hasChildren ? `${source.children_count} synced items` : config.description}
                                                        </p>
                                                    </div>

                                                    {/* Status & Actions */}
                                                    <div className="flex items-center gap-3">
                                                        <span className={`text-xs px-2 py-1 rounded-full ${source.status === 'ACTIVE' ? 'bg-green-100 text-green-700' :
                                                            source.status === 'ERROR' ? 'bg-red-100 text-red-700' :
                                                                'bg-yellow-100 text-yellow-700'
                                                            }`}>
                                                            {source.status}
                                                        </span>
                                                        <button
                                                            onClick={(e) => { e.stopPropagation(); setSelectedSource(source.id); }}
                                                            className="text-sm text-primary hover:underline"
                                                        >
                                                            Manage
                                                        </button>
                                                    </div>
                                                </div>

                                                {/* Children List */}
                                                {isExpanded && (
                                                    <div className="border-t bg-muted/30">
                                                        {isLoadingThisChildren ? (
                                                            <div className="p-4 text-center text-muted-foreground text-sm">Loading...</div>
                                                        ) : children.length > 0 ? (
                                                            <div className="divide-y">
                                                                {children.map(child => (
                                                                    <div
                                                                        key={child.id}
                                                                        className="flex items-center gap-4 p-3 pl-16 hover:bg-muted/50 cursor-pointer transition-colors"
                                                                        onClick={() => setSelectedSource(child.id)}
                                                                    >
                                                                        <FileText className="h-4 w-4 text-muted-foreground" />
                                                                        <span className="flex-1 text-sm truncate">{child.name}</span>
                                                                        <span className="text-xs text-muted-foreground">
                                                                            {child.created_at ? new Date(child.created_at).toLocaleDateString() : ''}
                                                                        </span>
                                                                        <span className={`text-xs px-2 py-0.5 rounded-full ${child.status === 'COMPLETED' ? 'bg-green-100 text-green-700' :
                                                                            child.status === 'PENDING' ? 'bg-yellow-100 text-yellow-700' :
                                                                                'bg-blue-100 text-blue-700'
                                                                            }`}>
                                                                            {child.status}
                                                                        </span>
                                                                    </div>
                                                                ))}
                                                            </div>
                                                        ) : (
                                                            <div className="p-4 text-center text-muted-foreground text-sm">No items synced yet</div>
                                                        )}
                                                    </div>
                                                )}
                                            </div>
                                        );
                                    })}
                                </div>
                            </section>
                        )}

                        {/* Regular Sources Section */}
                        {regularSources.length > 0 && (
                            <section>
                                <h2 className="text-lg font-semibold mb-4">Sources</h2>
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                    {regularSources.map(source => {
                                        const config = getSourceConfig(source.type);
                                        return (
                                            <ConnectorCard
                                                key={source.id}
                                                name={source.name}
                                                icon={config.icon}
                                                status={source.status === 'ACTIVE' || source.status === 'COMPLETED' ? 'active' : source.status === 'ERROR' ? 'error' : 'syncing'}
                                                lastSync={formatLastSync(source.last_synced_at)}
                                                description={config.description}
                                                onClick={() => setSelectedSource(source.id)}
                                            />
                                        )
                                    })}
                                </div>
                            </section>
                        )}

                        {sources.length === 0 && (
                            <div className="text-center text-muted-foreground py-10">
                                No sources found. Add one to get started.
                            </div>
                        )}
                    </>
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
