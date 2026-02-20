"use client"

/**
 * Pipeline Step-level status section for source detail drawer.
 * Fetches the system pipeline template, groups operators by Step,
 * and renders Step status cards with expandable operator details.
 */

import React, { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { getPipelines, type PipelineTemplate, type StepDef, type OpRefDef } from "@/lib/api/pipelines"
import {
    CheckCircle2,
    XCircle,
    Loader2,
    Clock,
    ChevronDown,
    ChevronRight,
    ExternalLink,
    Brain,
    Cpu,
    Layers,
} from "lucide-react"
import { Button } from "@/components/ui/button"

interface SourceLog {
    id: string
    source_id: string
    event_type: string
    lens_key: string | null
    step_key: string | null
    status: string
    message: string | null
    duration_ms: number | null
    extra_data: Record<string, unknown>
    created_at: string
}

type StepStatus = "pending" | "running" | "completed" | "failed"

interface PipelineStatusSectionProps {
    logs: SourceLog[]
    sourceData?: any
}

export function PipelineStatusSection({ logs, sourceData }: PipelineStatusSectionProps) {
    const router = useRouter()
    const [pipeline, setPipeline] = useState<PipelineTemplate | null>(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        getPipelines()
            .then((all) => {
                const sys = all.find((p) => p.is_system)
                if (sys) setPipeline(sys)
            })
            .catch(console.error)
            .finally(() => setLoading(false))
    }, [])

    if (loading) {
        return (
            <div className="flex items-center gap-2 text-muted-foreground text-sm p-4">
                <Loader2 className="h-4 w-4 animate-spin" />
                Loading pipeline…
            </div>
        )
    }

    if (!pipeline) return null

    const steps = pipeline.definition?.steps || []

    // Derive Step status from operator-level logs
    const getStepStatus = (step: StepDef): {
        status: StepStatus
        completedOps: number
        totalOps: number
        message?: string | null
    } => {
        const opIds = step.operators.map((op) => op.id)
        const totalOps = opIds.length

        // Check for step-level log entries first (new format)
        const stepLogs = logs.filter((l) => l.step_key === step.key && l.event_type?.startsWith("step_"))
        stepLogs.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())

        if (stepLogs.length > 0) {
            const latest = stepLogs[0]
            if (latest.event_type === "step_completed") {
                return { status: "completed", completedOps: totalOps, totalOps, message: latest.message }
            }
            if (latest.event_type === "step_failed") {
                const completedOps = opIds.filter((id) =>
                    logs.some((l) => l.lens_key === id && l.status === "completed")
                ).length
                return { status: "failed", completedOps, totalOps, message: latest.message }
            }
            if (latest.event_type === "step_started") {
                const completedOps = opIds.filter((id) =>
                    logs.some((l) => l.lens_key === id && l.status === "completed")
                ).length
                return { status: "running", completedOps, totalOps }
            }
        }

        // Fallback: derive status from individual operator logs
        const completedOps = opIds.filter((id) =>
            logs.some((l) => l.lens_key === id && l.status === "completed")
        ).length
        const hasFailed = opIds.some((id) =>
            logs.some((l) => l.lens_key === id && l.status === "failed")
        )
        const hasRunning = opIds.some((id) =>
            logs.some((l) => l.lens_key === id && l.status === "running")
        )

        if (hasFailed) return { status: "failed", completedOps, totalOps }
        if (hasRunning) return { status: "running", completedOps, totalOps }
        if (completedOps === totalOps && totalOps > 0) return { status: "completed", completedOps, totalOps }
        if (completedOps > 0) return { status: "running", completedOps, totalOps }
        return { status: "pending", completedOps: 0, totalOps }
    }

    // Overall stats
    const stepStatuses = steps.map((s) => getStepStatus(s))
    const completedSteps = stepStatuses.filter((s) => s.status === "completed").length
    const failedSteps = stepStatuses.filter((s) => s.status === "failed").length
    const runningSteps = stepStatuses.filter((s) => s.status === "running").length

    return (
        <section className="space-y-4">
            {/* Header */}
            <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold flex items-center gap-2">
                    <Layers className="h-5 w-5 text-primary" />
                    Processing Steps
                </h3>
                <Button
                    variant="outline"
                    size="sm"
                    className="gap-1.5 text-xs"
                    onClick={() => router.push(`/pipelines/${pipeline.id}`)}
                >
                    <ExternalLink className="h-3 w-3" />
                    View Pipeline
                </Button>
            </div>

            {/* Progress summary */}
            <div className="flex items-center gap-3 text-xs text-muted-foreground">
                <span className="flex items-center gap-1">
                    <CheckCircle2 className="h-3 w-3 text-green-500" />
                    {completedSteps}/{steps.length} steps done
                </span>
                {failedSteps > 0 && (
                    <span className="flex items-center gap-1">
                        <XCircle className="h-3 w-3 text-red-500" />
                        {failedSteps} failed
                    </span>
                )}
                {runningSteps > 0 && (
                    <span className="flex items-center gap-1">
                        <Loader2 className="h-3 w-3 text-blue-500 animate-spin" />
                        {runningSteps} running
                    </span>
                )}
            </div>

            {/* Step list */}
            <div className="space-y-2">
                {steps.map((step) => {
                    const stepInfo = getStepStatus(step)
                    return (
                        <StepStatusCard
                            key={step.key}
                            step={step}
                            stepStatus={stepInfo.status}
                            completedOps={stepInfo.completedOps}
                            totalOps={stepInfo.totalOps}
                            message={stepInfo.message}
                            logs={logs}
                        />
                    )
                })}
            </div>
        </section>
    )
}

// ─── Step Status Card ────────────────────────────────────────────────

function StepStatusCard({
    step,
    stepStatus,
    completedOps,
    totalOps,
    message,
    logs,
}: {
    step: StepDef
    stepStatus: StepStatus
    completedOps: number
    totalOps: number
    message?: string | null
    logs: SourceLog[]
}) {
    const [expanded, setExpanded] = useState(false)

    const statusConfig = {
        pending: {
            icon: <Clock className="h-4 w-4 text-muted-foreground" />,
            badge: "bg-muted text-muted-foreground",
            border: "border-border",
            bg: "",
            label: "Pending",
        },
        running: {
            icon: <Loader2 className="h-4 w-4 text-blue-500 animate-spin" />,
            badge: "bg-blue-500/10 text-blue-600",
            border: "border-blue-500/30",
            bg: "bg-blue-500/[0.02]",
            label: "Running",
        },
        completed: {
            icon: <CheckCircle2 className="h-4 w-4 text-green-500" />,
            badge: "bg-green-500/10 text-green-600",
            border: "border-green-500/20",
            bg: "",
            label: "Done",
        },
        failed: {
            icon: <XCircle className="h-4 w-4 text-red-500" />,
            badge: "bg-red-500/10 text-red-500",
            border: "border-red-500/30",
            bg: "bg-red-500/[0.02]",
            label: "Failed",
        },
    }[stepStatus]

    // Progress bar percentage
    const progress = totalOps > 0 ? (completedOps / totalOps) * 100 : 0

    return (
        <div className={`border rounded-xl overflow-hidden transition-colors ${statusConfig.border} ${statusConfig.bg}`}>
            {/* Step header */}
            <div
                className="flex items-center gap-3 px-4 py-3 cursor-pointer hover:bg-muted/30 transition-colors"
                onClick={() => setExpanded(!expanded)}
            >
                {/* Expand indicator */}
                {expanded ? (
                    <ChevronDown className="h-3.5 w-3.5 text-muted-foreground shrink-0" />
                ) : (
                    <ChevronRight className="h-3.5 w-3.5 text-muted-foreground shrink-0" />
                )}

                {/* Status icon */}
                {statusConfig.icon}

                {/* Step label */}
                <div className="flex-1 min-w-0">
                    <span className="font-medium text-sm">{step.label || step.key}</span>
                    <span className="text-[10px] text-muted-foreground ml-2">
                        {totalOps} operator{totalOps !== 1 ? "s" : ""}
                    </span>
                </div>

                {/* Mini progress */}
                {stepStatus === "running" && (
                    <div className="w-16 h-1.5 rounded-full bg-muted overflow-hidden shrink-0">
                        <div
                            className="h-full bg-blue-500 rounded-full transition-all duration-500"
                            style={{ width: `${progress}%` }}
                        />
                    </div>
                )}

                {/* Status badge */}
                <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium shrink-0 ${statusConfig.badge}`}>
                    {stepStatus === "running" ? `${completedOps}/${totalOps}` : statusConfig.label}
                </span>
            </div>

            {/* Error message for failed steps */}
            {stepStatus === "failed" && message && !expanded && (
                <div className="px-4 pb-2 -mt-1">
                    <p className="text-[11px] text-red-500 truncate">{message}</p>
                </div>
            )}

            {/* Expanded: individual operators */}
            {expanded && (
                <div className="border-t bg-muted/20 px-4 py-2 space-y-1">
                    {step.operators.map((op) => (
                        <OperatorRow key={op.id} op={op} logs={logs} />
                    ))}
                    {/* Show error details if failed */}
                    {stepStatus === "failed" && message && (
                        <div className="mt-2 p-2 bg-red-50 dark:bg-red-950/30 rounded-md">
                            <pre className="text-[10px] text-red-600 dark:text-red-400 whitespace-pre-wrap font-mono leading-relaxed">
                                {message}
                            </pre>
                        </div>
                    )}
                </div>
            )}
        </div>
    )
}

// ─── Operator Row (inside expanded Step) ─────────────────────────────

function OperatorRow({ op, logs }: { op: OpRefDef; logs: SourceLog[] }) {
    const opLogs = logs.filter((l) => l.lens_key === op.id)
    opLogs.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    const latest = opLogs[0]

    const status = latest?.status || "pending"
    const durationMs = latest?.duration_ms

    const isLlm = ["summary", "reading_notes", "study_quiz", "figure_association"].some((k) =>
        op.operator_key.includes(k)
    )

    const formatDuration = (ms: number | null | undefined) => {
        if (!ms) return null
        if (ms < 1000) return `${ms}ms`
        return `${(ms / 1000).toFixed(1)}s`
    }

    const statusDot = {
        pending: "bg-gray-300 dark:bg-gray-600",
        running: "bg-blue-500 animate-pulse",
        completed: "bg-green-500",
        failed: "bg-red-500",
    }[status] || "bg-gray-300"

    return (
        <div className="flex items-center gap-2.5 py-1.5 text-xs">
            {/* Status dot */}
            <span className={`h-1.5 w-1.5 rounded-full shrink-0 ${statusDot}`} />

            {/* Kind icon */}
            {isLlm ? (
                <Brain className="h-3 w-3 text-purple-400 shrink-0" />
            ) : (
                <Cpu className="h-3 w-3 text-sky-400 shrink-0" />
            )}

            {/* Operator name */}
            <span className="flex-1 truncate text-muted-foreground">
                {op.operator_key}
            </span>

            {/* Duration */}
            {durationMs && (
                <span className="text-[10px] text-muted-foreground shrink-0">
                    {formatDuration(durationMs)}
                </span>
            )}

            {/* Status text */}
            <span className={`text-[10px] shrink-0 ${status === "completed" ? "text-green-600" :
                    status === "failed" ? "text-red-500" :
                        status === "running" ? "text-blue-500" :
                            "text-muted-foreground"
                }`}>
                {status}
            </span>
        </div>
    )
}
