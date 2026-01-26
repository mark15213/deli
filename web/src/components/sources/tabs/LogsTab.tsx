"use client"

import { ScrollArea } from "@/components/ui/scroll-area"
import { CheckCircle2, XCircle, Clock } from "lucide-react"

const logs = [
    { status: "success", message: "Fetched 3 new threads from @naval", time: "10:42 AM" },
    { status: "success", message: "Synced 12 bookmarks", time: "09:30 AM" },
    { status: "error", message: "Rate limit exceeded (429)", time: "08:15 AM" },
    { status: "success", message: "Routine check - no new content", time: "07:00 AM" },
    { status: "success", message: "Token refreshed successfully", time: "Yesterday" },
]

export function LogsTab() {
    return (
        <div className="h-full py-4">
            <h3 className="text-sm font-medium mb-3 flex items-center gap-2">
                <Clock className="h-4 w-4" /> Recent Activity
            </h3>
            <div className="rounded-lg border bg-card overflow-hidden">
                <ScrollArea className="h-[400px]">
                    <div className="divide-y">
                        {logs.map((log, i) => (
                            <div key={i} className="p-3 flex items-start gap-3 hover:bg-muted/50 transition-colors text-sm">
                                <div className="mt-0.5">
                                    {log.status === 'success' ? (
                                        <CheckCircle2 className="h-4 w-4 text-green-500" />
                                    ) : (
                                        <XCircle className="h-4 w-4 text-red-500" />
                                    )}
                                </div>
                                <div className="flex-1 space-y-0.5">
                                    <p className="font-medium leading-none">{log.message}</p>
                                    <p className="text-xs text-muted-foreground">{log.time}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </ScrollArea>
            </div>
            <p className="text-[10px] text-muted-foreground text-center mt-2">Showing last 24 hours</p>
        </div>
    )
}
