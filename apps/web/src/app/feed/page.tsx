"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { FileText, Rss, ArrowRight, Clock, Loader2 } from "lucide-react"
import { AddSourceDialog } from "@/components/AddSourceDialog"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Workspace } from "@/components/Workspace"
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"
import { SubscriptionSettingsDialog } from "@/components/SubscriptionSettingsDialog"
import { Button } from "@/components/ui/button"
import { useAuth } from "@/contexts/AuthContext"
import { api } from "@/lib/api"

interface Snapshot {
    id: string
    title: string
    url: string
    summary: string | null
    added_at: string
    status: string
}

interface Subscription {
    id: string
    title: string
    url: string
    frequency: string
    is_active: boolean
}

export default function FeedPage() {
    const [activeWorkspaceSource, setActiveWorkspaceSource] = useState<any>(null)
    const [snapshots, setSnapshots] = useState<Snapshot[]>([])
    const [subscriptions, setSubscriptions] = useState<Subscription[]>([])
    const [loading, setLoading] = useState(true)
    const { isAuthenticated } = useAuth()
    const router = useRouter()

    useEffect(() => {
        if (!isAuthenticated) {
            router.push('/login')
            return
        }
        loadData()
    }, [isAuthenticated, router])

    const loadData = async () => {
        try {
            setLoading(true)
            const [snapshotsData, subscriptionsData] = await Promise.all([
                api.getSnapshots({ limit: 20 }),
                api.getSubscriptions()
            ])
            setSnapshots(snapshotsData.items || snapshotsData as Snapshot[])
            setSubscriptions(subscriptionsData as Subscription[])
        } catch (error: any) {
            console.error('Failed to load data:', error)
        } finally {
            setLoading(false)
        }
    }

    const formatDate = (dateString: string) => {
        const date = new Date(dateString)
        const now = new Date()
        const diffMs = now.getTime() - date.getTime()
        const diffMins = Math.floor(diffMs / 60000)
        const diffHours = Math.floor(diffMs / 3600000)
        const diffDays = Math.floor(diffMs / 86400000)

        if (diffMins < 60) return `${diffMins} minutes ago`
        if (diffHours < 24) return `${diffHours} hours ago`
        if (diffDays === 1) return 'Yesterday'
        if (diffDays < 7) return `${diffDays} days ago`
        return date.toLocaleDateString()
    }

    if (activeWorkspaceSource) {
        return (
            <Workspace
                source={activeWorkspaceSource}
                onClose={() => {
                    setActiveWorkspaceSource(null)
                    loadData() // Reload data when closing workspace
                }}
            />
        )
    }

    if (loading) {
        return (
            <div className="h-full flex items-center justify-center">
                <Loader2 className="h-8 w-8 animate-spin text-zinc-400" />
            </div>
        )
    }

    return (
        <div className="h-full flex flex-col p-8 bg-transparent max-w-7xl mx-auto w-full">
            <div className="flex items-center justify-between mb-8 pb-6 border-b border-border/50">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight text-zinc-900 drop-shadow-sm">Feed</h1>
                    <p className="text-zinc-500 mt-2 text-sm font-medium">Manage your info sources and subscriptions.</p>
                </div>
                <AddSourceDialog onSuccess={loadData} />
            </div>

            <div className="flex-1 overflow-y-auto pb-20 pr-4">

                {/* Independent Snapshots Section */}
                <div className="mb-12">
                    <div className="flex items-center gap-2 mb-6">
                        <FileText className="h-5 w-5 text-zinc-400" />
                        <h2 className="text-lg font-semibold text-zinc-800">Recent Snapshots</h2>
                    </div>

                    {snapshots.length === 0 ? (
                        <div className="text-center py-12 text-zinc-500">
                            <FileText className="h-12 w-12 mx-auto mb-4 text-zinc-300" />
                            <p>No snapshots yet. Add a source to get started.</p>
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 auto-rows-max">
                            {snapshots.map((source) => (
                                <Card
                                    key={source.id}
                                    className="flex flex-col border-zinc-200 bg-white shadow-sm hover:shadow-md hover:border-zinc-300 transition-all cursor-pointer group rounded-2xl"
                                    onClick={() => setActiveWorkspaceSource(source)}
                                >
                                    <CardHeader className="pb-3 relative">
                                        <div className="absolute top-4 right-4">
                                            <FileText className="h-4 w-4 text-zinc-400 group-hover:text-zinc-600 transition-colors" />
                                        </div>
                                        <CardTitle className="line-clamp-2 leading-snug group-hover:text-blue-600 transition-colors text-[17px] pr-6">
                                            {source.title}
                                        </CardTitle>
                                        <CardDescription className="line-clamp-1 mt-1 font-medium text-xs text-zinc-400">
                                            {source.url}
                                        </CardDescription>
                                    </CardHeader>
                                    <CardFooter className="pt-3 border-t border-zinc-50 text-xs text-zinc-500 flex justify-between items-center bg-zinc-50/50 rounded-b-2xl mt-auto">
                                        <div className="flex items-center gap-1.5 font-medium">
                                            <Clock className="h-3.5 w-3.5" />
                                            {formatDate(source.added_at)}
                                        </div>
                                        <div className="flex items-center gap-1.5 text-blue-600 opacity-0 group-hover:opacity-100 transition-opacity font-semibold">
                                            Open <ArrowRight className="h-3.5 w-3.5" />
                                        </div>
                                    </CardFooter>
                                </Card>
                            ))}
                        </div>
                    )}
                </div>

                {/* Subscriptions Accordion Section */}
                <div>
                    <div className="flex items-center gap-2 mb-6">
                        <Rss className="h-5 w-5 text-zinc-400" />
                        <h2 className="text-lg font-semibold text-zinc-800">Subscriptions</h2>
                    </div>

                    {subscriptions.length === 0 ? (
                        <div className="text-center py-12 text-zinc-500 bg-white rounded-2xl border border-zinc-200">
                            <Rss className="h-12 w-12 mx-auto mb-4 text-zinc-300" />
                            <p>No subscriptions yet. Create one to automatically fetch content.</p>
                        </div>
                    ) : (
                        <div className="bg-white rounded-[2rem] shadow-sm border border-zinc-200 overflow-hidden">
                            <Accordion type="multiple" className="w-full">
                                {subscriptions.map((sub) => (
                                    <AccordionItem value={sub.id} key={sub.id} className="last:border-0 group data-[state=open]:bg-zinc-50/30 transition-colors relative">
                                        <div className="flex items-center w-full group/header relative px-6 z-10">
                                            <AccordionTrigger className="hover:no-underline font-semibold text-base py-5 gap-4 flex-[1_1_auto] border-b-0">
                                                <div className="flex items-center justify-between w-full h-full pr-10">
                                                    <div className="flex items-center gap-4">
                                                        <div className="h-10 w-10 rounded-full bg-orange-50 flex items-center justify-center border border-orange-100 flex-shrink-0">
                                                            <Rss className="h-5 w-5 text-orange-500" />
                                                        </div>
                                                        <div className="flex flex-col gap-0.5 items-start">
                                                            <span className="text-zinc-900 group-data-[state=open]:text-blue-600 transition-colors block leading-tight">{sub.title}</span>
                                                            <span className="text-xs font-normal text-zinc-500 line-clamp-1">{sub.url}</span>
                                                        </div>
                                                    </div>
                                                    <div className="flex items-center gap-3">
                                                        <Badge variant="outline" className="text-xs">
                                                            {sub.frequency}
                                                        </Badge>
                                                    </div>
                                                </div>
                                            </AccordionTrigger>
                                            <div className="flex items-center justify-center shrink-0 w-8 h-full absolute right-[4.5rem]" onClick={(e) => e.stopPropagation()}>
                                                <SubscriptionSettingsDialog subscription={sub} onUpdate={loadData} />
                                            </div>
                                        </div>

                                        <AccordionContent className="pb-6 pt-2 pr-12 pl-[5.5rem] relative z-0">
                                            <div className="text-sm text-zinc-500">
                                                Click "Fetch" in settings to manually fetch content from this subscription.
                                            </div>
                                        </AccordionContent>
                                    </AccordionItem>
                                ))}
                            </Accordion>
                        </div>
                    )}

                </div>
            </div>
        </div>
    )
}
