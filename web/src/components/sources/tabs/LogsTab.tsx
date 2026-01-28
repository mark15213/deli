"use client"

import { useEffect, useState } from "react"
import { ScrollArea } from "@/components/ui/scroll-area"
import { CheckCircle2, XCircle, Clock, Loader2, Play } from "lucide-react"
import { formatDistanceToNow } from "date-fns"

interface SourceLog {
    id: string
    source_id: string
    event_type: string
    lens_key: string | null
    status: string
    message: string | null
    duration_ms: number | null
    extra_data: Record<string, unknown>
    created_at: string
}

interface LogsTabProps {
    sourceId: string
}

export function LogsTab({ sourceId }: LogsTabProps) {
    const [logs, setLogs] = useState<SourceLog[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        async function fetchLogs() {
            try {
                setLoading(true)
                const res = await fetch(`/api/sources/${sourceId}/logs`)
                if (!res.ok) throw new Error("Failed to fetch logs")
                const data = await res.json()
                setLogs(data)
            } catch (e) {
                setError(e instanceof Error ? e.message : "Unknown error")
            } finally {
                setLoading(false)
            }
        }

        if (sourceId) {
            fetchLogs()
        }
    }, [sourceId])

    const getStatusIcon = (status: string, eventType: string) => {
        if (status === "running") {
            return <Loader2 className="h-4 w-4 text-blue-500 animate-spin" />
        } else if (status === "completed") {
            return <CheckCircle2 className="h-4 w-4 text-green-500" />
        } else if (status === "failed") {
            return <XCircle className="h-4 w-4 text-red-500" />
        } else if (eventType.includes("started")) {
            return <Play className="h-4 w-4 text-blue-500" />
        }
        return <Clock className="h-4 w-4 text-muted-foreground" />
    }

    const formatDuration = (ms: number | null) => {
        if (!ms) return null
        if (ms < 1000) return `${ms}ms`
        return `${(ms / 1000).toFixed(1)}s`
    }

    if (loading) {
        return (
            <div className="h-full py-4 flex items-center justify-center">
                <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
            </div>
        )
    }

    if (error) {
        return (
            <div className="h-full py-4 text-center text-destructive">
                Error: {error}
            </div>
        )
    }

    return (
        <div className="h-full py-4">
            <h3 className="text-sm font-medium mb-3 flex items-center gap-2">
                <Clock className="h-4 w-4" /> Lens Execution History
            </h3>
            {logs.length === 0 ? (
                <div className="text-center text-muted-foreground py-8 border rounded-lg border-dashed">
                    No logs yet. Processing will appear here.
                </div>
            ) : (
                <div className="rounded-lg border bg-card overflow-hidden">
                    <ScrollArea className="h-[400px]">
                        <div className="divide-y">
                            {logs.map((log) => (
                                <div key={log.id} className="p-3 flex items-start gap-3 hover:bg-muted/50 transition-colors text-sm">
                                    <div className="mt-0.5">
                                        {getStatusIcon(log.status, log.event_type)}
                                    </div>
                                    <div className="flex-1 space-y-0.5">
                                        <div className="flex items-center gap-2">
                                            <p className="font-medium leading-none">
                                                {log.message || log.event_type}
                                            </p>
                                            {log.lens_key && (
                                                <span className="text-xs bg-muted px-1.5 py-0.5 rounded">
                                                    {log.lens_key}
                                                </span>
                                            )}
                                        </div>
                                        <div className="flex items-center gap-2 text-xs text-muted-foreground">
                                            <span>
                                                {formatDistanceToNow(new Date(log.created_at), { addSuffix: true })}
                                            </span>
                                            {log.duration_ms && (
                                                <span className="text-green-600">
                                                    • {formatDuration(log.duration_ms)}
                                                </span>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </ScrollArea>
                </div>
            )}
        </div>
    )
}
