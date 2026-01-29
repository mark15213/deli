"use client"

import { Button } from "@/components/ui/button"
import { CheckCircle2, XCircle, Loader2, Clock, ChevronDown, ChevronRight, Play } from "lucide-react"
import { useState } from "react"

export type LensStatus = "pending" | "running" | "completed" | "failed"

interface LensPipelineCardProps {
    name: string
    description: string
    lensKey: string
    status: LensStatus
    durationMs?: number | null
    errorMessage?: string | null
    result?: any
    isSuggested?: boolean
    onRun?: () => void
}

export function LensPipelineCard({
    name,
    description,
    lensKey,
    status,
    durationMs,
    errorMessage,
    result,
    isSuggested = false,
    onRun
}: LensPipelineCardProps) {
    const [expanded, setExpanded] = useState(false)
    const hasDetails = (status === "failed" && errorMessage) || result

    const formatDuration = (ms: number | null | undefined) => {
        if (!ms) return null
        if (ms < 1000) return `${ms}ms`
        return `${(ms / 1000).toFixed(1)}s`
    }

    const getStatusIcon = () => {
        switch (status) {
            case "running":
                return <Loader2 className="h-4 w-4 text-blue-500 animate-spin" />
            case "completed":
                return <CheckCircle2 className="h-4 w-4 text-green-500" />
            case "failed":
                return <XCircle className="h-4 w-4 text-red-500" />
            case "pending":
            default:
                return <Clock className="h-4 w-4 text-muted-foreground" />
        }
    }

    const getStatusBadge = () => {
        switch (status) {
            case "running":
                return (
                    <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full flex items-center gap-1">
                        <Loader2 className="h-3 w-3 animate-spin" />
                        Running
                    </span>
                )
            case "completed":
                return (
                    <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">
                        ✓ Completed {durationMs && `• ${formatDuration(durationMs)}`}
                    </span>
                )
            case "failed":
                return (
                    <span className="text-xs bg-red-100 text-red-700 px-2 py-0.5 rounded-full">
                        ✗ Failed
                    </span>
                )
            case "pending":
            default:
                return isSuggested ? null : (
                    <span className="text-xs bg-muted text-muted-foreground px-2 py-0.5 rounded-full">
                        Pending
                    </span>
                )
        }
    }

    return (
        <div className="border rounded-lg bg-card overflow-hidden">
            <div
                className={`p-3 flex items-start gap-3 ${hasDetails ? "cursor-pointer hover:bg-muted/50" : ""}`}
                onClick={() => hasDetails && setExpanded(!expanded)}
            >
                {/* Expand/Collapse Icon */}
                {hasDetails && (
                    <div className="mt-0.5">
                        {expanded ? (
                            <ChevronDown className="h-4 w-4 text-muted-foreground" />
                        ) : (
                            <ChevronRight className="h-4 w-4 text-muted-foreground" />
                        )}
                    </div>
                )}

                {/* Status Icon */}
                <div className="mt-0.5">
                    {getStatusIcon()}
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                        <span className="font-medium text-sm">{name}</span>
                        <span className="text-xs text-muted-foreground bg-muted px-1.5 py-0.5 rounded">
                            {lensKey}
                        </span>
                        {getStatusBadge()}
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">{description}</p>
                </div>

                {/* Run Button for Suggested Lenses */}
                {isSuggested && status === "pending" && onRun && (
                    <Button
                        size="sm"
                        variant="outline"
                        onClick={(e) => {
                            e.stopPropagation()
                            onRun()
                        }}
                        className="shrink-0"
                    >
                        <Play className="h-3 w-3 mr-1" />
                        Run
                    </Button>
                )}
            </div>

            {/* Expanded Details */}
            {expanded && hasDetails && (
                <div className="px-3 pb-3 pl-10 space-y-2 border-t bg-muted/30">
                    {status === "failed" && errorMessage && (
                        <div className="text-xs bg-red-50 border border-red-200 rounded p-2 mt-2">
                            <div className="font-semibold text-red-900 mb-1">Error Details:</div>
                            <pre className="whitespace-pre-wrap text-red-700 font-mono">
                                {errorMessage}
                            </pre>
                        </div>
                    )}
                    {result && (
                        <div className="text-xs bg-background border rounded p-2 mt-2 overflow-auto max-h-40">
                            <div className="font-semibold mb-1">Result:</div>
                            <pre className="whitespace-pre-wrap text-muted-foreground font-mono">
                                {typeof result === "string" ? result : JSON.stringify(result, null, 2)}
                            </pre>
                        </div>
                    )}
                </div>
            )}
        </div>
    )
}
