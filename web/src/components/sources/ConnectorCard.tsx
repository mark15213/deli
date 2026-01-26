"use client"

import { Wifi, AlertCircle, CheckCircle2 } from "lucide-react"
import { cn } from "@/lib/utils"

interface ConnectorCardProps {
    name: string
    icon: React.ReactNode
    status: "active" | "error" | "syncing"
    lastSync?: string
    description: string
    onClick?: () => void
}

export function ConnectorCard({ name, icon, status, lastSync, description, onClick }: ConnectorCardProps) {
    return (
        <div onClick={onClick} className="group relative overflow-hidden rounded-xl border border-slate-200/60 dark:border-zinc-800 bg-white dark:bg-zinc-900 p-6 shadow-sm transition-all duration-300 hover:shadow-[0_8px_30px_rgb(0,0,0,0.04)] hover:-translate-y-1 hover:border-slate-300/50 dark:hover:border-zinc-700 cursor-pointer">
            <div className="flex items-start justify-between">
                <div className="rounded-lg bg-slate-100 dark:bg-zinc-800 p-3 text-slate-600 dark:text-zinc-400 group-hover:bg-primary/5 group-hover:text-primary transition-colors">
                    {icon}
                </div>
                <div className="flex items-center gap-1.5 rounded-full bg-secondary px-2.5 py-0.5 text-xs font-medium text-secondary-foreground">
                    <span className={cn("relative flex h-2 w-2")}>
                        <span className={cn(
                            "absolute inline-flex h-full w-full animate-ping rounded-full opacity-75",
                            status === "syncing" ? "bg-green-400" : "hidden"
                        )}></span>
                        <span className={cn(
                            "relative inline-flex h-2 w-2 rounded-full",
                            status === "syncing" ? "bg-green-500" :
                                status === "active" ? "bg-blue-500" : "bg-red-500"
                        )}></span>
                    </span>
                    <span className="capitalize">{status}</span>
                </div>
            </div>

            <div className="mt-4">
                <h3 className="font-semibold text-lg text-slate-900 dark:text-zinc-50">{name}</h3>
                <p className="mt-1 text-sm text-slate-500 dark:text-zinc-400 line-clamp-2">{description}</p>
            </div>

            <div className="mt-4 flex items-center gap-2 text-xs text-muted-foreground">
                {status === 'active' && <CheckCircle2 className="h-3 w-3" />}
                {status === 'syncing' && <Wifi className="h-3 w-3 animate-pulse" />}
                {status === 'error' && <AlertCircle className="h-3 w-3" />}
                <span>Last synced: {lastSync || 'Never'}</span>
            </div>
        </div>
    )
}
