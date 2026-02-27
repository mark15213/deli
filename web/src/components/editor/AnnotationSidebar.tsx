"use client"

import { useState, useEffect, useCallback } from "react"
import { MessageSquare, Highlighter, Trash2, Check, X, Plus } from "lucide-react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import {
    getAnnotations,
    createAnnotation,
    updateAnnotation,
    deleteAnnotation,
    type Annotation,
} from "@/lib/api/editor"

interface AnnotationSidebarProps {
    sourceId: string
    visible: boolean
}

const HIGHLIGHT_COLORS = [
    { name: "Yellow", value: "#fef08a" },
    { name: "Green", value: "#bbf7d0" },
    { name: "Blue", value: "#bfdbfe" },
    { name: "Pink", value: "#fbcfe8" },
    { name: "Orange", value: "#fed7aa" },
]

export function AnnotationSidebar({ sourceId, visible }: AnnotationSidebarProps) {
    const [annotations, setAnnotations] = useState<Annotation[]>([])
    const [loading, setLoading] = useState(true)
    const [showAddForm, setShowAddForm] = useState(false)
    const [newBody, setNewBody] = useState("")
    const [newType, setNewType] = useState<"comment" | "highlight">("comment")
    const [newColor, setNewColor] = useState(HIGHLIGHT_COLORS[0].value)

    const fetchAnnotations = useCallback(async () => {
        try {
            setLoading(true)
            const data = await getAnnotations(sourceId)
            setAnnotations(data)
        } catch (e) {
            console.error("Failed to fetch annotations:", e)
        } finally {
            setLoading(false)
        }
    }, [sourceId])

    useEffect(() => {
        if (visible) fetchAnnotations()
    }, [visible, fetchAnnotations])

    const handleCreate = useCallback(async () => {
        if (!newBody.trim() && newType === "comment") return
        try {
            const ann = await createAnnotation(sourceId, {
                type: newType,
                color: newType === "highlight" ? newColor : undefined,
                anchor: { from: 0, to: 0 }, // Placeholder — real integration would use editor selection
                body: newBody || undefined,
            })
            setAnnotations((prev) => [...prev, ann])
            setNewBody("")
            setShowAddForm(false)
        } catch (e) {
            console.error("Failed to create annotation:", e)
        }
    }, [sourceId, newBody, newType, newColor])

    const handleDelete = useCallback(async (id: string) => {
        try {
            await deleteAnnotation(sourceId, id)
            setAnnotations((prev) => prev.filter((a) => a.id !== id))
        } catch (e) {
            console.error("Failed to delete annotation:", e)
        }
    }, [sourceId])

    const handleResolve = useCallback(async (id: string, resolved: boolean) => {
        try {
            const updated = await updateAnnotation(sourceId, id, { resolved })
            setAnnotations((prev) => prev.map((a) => (a.id === id ? updated : a)))
        } catch (e) {
            console.error("Failed to update annotation:", e)
        }
    }, [sourceId])

    if (!visible) return null

    return (
        <div className="annotation-sidebar">
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-semibold text-foreground">Annotations</h3>
                <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setShowAddForm(!showAddForm)}
                    className="h-7 w-7 p-0"
                >
                    <Plus className="h-4 w-4" />
                </Button>
            </div>

            {/* Add Form */}
            {showAddForm && (
                <div className="mb-4 p-3 bg-muted/50 rounded-lg border border-border space-y-3">
                    {/* Type selector */}
                    <div className="flex gap-2">
                        <button
                            onClick={() => setNewType("comment")}
                            className={cn(
                                "flex-1 flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-colors",
                                newType === "comment" ? "bg-primary text-primary-foreground" : "bg-background border border-border hover:bg-accent"
                            )}
                        >
                            <MessageSquare className="h-3 w-3" /> Comment
                        </button>
                        <button
                            onClick={() => setNewType("highlight")}
                            className={cn(
                                "flex-1 flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-colors",
                                newType === "highlight" ? "bg-primary text-primary-foreground" : "bg-background border border-border hover:bg-accent"
                            )}
                        >
                            <Highlighter className="h-3 w-3" /> Highlight
                        </button>
                    </div>

                    {/* Color picker for highlights */}
                    {newType === "highlight" && (
                        <div className="flex gap-1.5">
                            {HIGHLIGHT_COLORS.map((c) => (
                                <button
                                    key={c.value}
                                    onClick={() => setNewColor(c.value)}
                                    className={cn(
                                        "w-6 h-6 rounded-full border-2 transition-transform",
                                        newColor === c.value ? "border-foreground scale-110" : "border-transparent hover:scale-105"
                                    )}
                                    style={{ backgroundColor: c.value }}
                                    title={c.name}
                                />
                            ))}
                        </div>
                    )}

                    {/* Body input */}
                    <textarea
                        value={newBody}
                        onChange={(e) => setNewBody(e.target.value)}
                        placeholder={newType === "comment" ? "Write a comment..." : "Note (optional)"}
                        className="w-full px-3 py-2 text-sm bg-background border border-border rounded-md resize-none focus:outline-none focus:ring-1 focus:ring-primary"
                        rows={2}
                    />

                    {/* Actions */}
                    <div className="flex justify-end gap-2">
                        <Button variant="ghost" size="sm" onClick={() => setShowAddForm(false)}>
                            <X className="h-3 w-3 mr-1" /> Cancel
                        </Button>
                        <Button size="sm" onClick={handleCreate}>
                            <Check className="h-3 w-3 mr-1" /> Add
                        </Button>
                    </div>
                </div>
            )}

            {/* Annotation list */}
            {loading ? (
                <div className="text-xs text-muted-foreground text-center py-4">Loading...</div>
            ) : annotations.length === 0 ? (
                <div className="text-xs text-muted-foreground text-center py-4">No annotations yet</div>
            ) : (
                <div className="space-y-2">
                    {annotations.map((ann) => (
                        <div
                            key={ann.id}
                            className={cn(
                                "group p-3 rounded-lg border border-border transition-colors hover:border-border/80",
                                ann.resolved && "opacity-50"
                            )}
                            style={ann.type === "highlight" ? { borderLeftColor: ann.color || "#fef08a", borderLeftWidth: 3 } : undefined}
                        >
                            <div className="flex items-start justify-between gap-2">
                                <div className="flex items-center gap-1.5">
                                    {ann.type === "comment" ? (
                                        <MessageSquare className="h-3.5 w-3.5 text-primary" />
                                    ) : (
                                        <Highlighter className="h-3.5 w-3.5" style={{ color: ann.color }} />
                                    )}
                                    <span className="text-xs font-medium capitalize text-muted-foreground">{ann.type}</span>
                                </div>
                                <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                    <button
                                        onClick={() => handleResolve(ann.id, !ann.resolved)}
                                        className="p-0.5 rounded hover:bg-accent"
                                        title={ann.resolved ? "Unresolve" : "Resolve"}
                                    >
                                        <Check className={cn("h-3 w-3", ann.resolved ? "text-green-500" : "text-muted-foreground")} />
                                    </button>
                                    <button
                                        onClick={() => handleDelete(ann.id)}
                                        className="p-0.5 rounded hover:bg-destructive/10"
                                        title="Delete"
                                    >
                                        <Trash2 className="h-3 w-3 text-destructive" />
                                    </button>
                                </div>
                            </div>
                            {ann.body && (
                                <p className="text-sm text-foreground/90 mt-1.5 leading-relaxed">{ann.body}</p>
                            )}
                            <span className="text-[10px] text-muted-foreground mt-1 block">
                                {new Date(ann.created_at).toLocaleDateString()}
                            </span>
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}
