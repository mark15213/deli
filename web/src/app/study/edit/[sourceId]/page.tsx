"use client"

import { useState, useEffect, useCallback, useRef } from "react"
import { useParams, useRouter } from "next/navigation"
import { ArrowLeft, Save, Loader2, MessageSquareDashed, CheckCircle2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { TiptapEditor } from "@/components/editor/TiptapEditor"
import { AnnotationSidebar } from "@/components/editor/AnnotationSidebar"
import { ShareDialog } from "@/components/editor/ShareDialog"
import { getEditorContent, saveEditorContent } from "@/lib/api/editor"

export default function EditorPage() {
    const params = useParams()
    const router = useRouter()
    const sourceId = params.sourceId as string

    const [content, setContent] = useState<Record<string, unknown> | null>(null)
    const [sourceTitle, setSourceTitle] = useState("")
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const [saving, setSaving] = useState(false)
    const [saved, setSaved] = useState(false)
    const [showAnnotations, setShowAnnotations] = useState(false)

    // Save queue to prevent concurrent saves from overwriting each other
    const savingRef = useRef(false)
    const pendingSaveRef = useRef<{ json: Record<string, unknown>; text: string } | null>(null)

    // Fetch editor content
    useEffect(() => {
        async function load() {
            try {
                setLoading(true)
                const data = await getEditorContent(sourceId)
                setContent(data.content)
                setSourceTitle(data.source_title)
            } catch (e) {
                console.error("Failed to load editor content:", e)
                setError("Failed to load editor content")
            } finally {
                setLoading(false)
            }
        }
        load()
    }, [sourceId])

    // Auto-save handler with queue to prevent concurrent overwrites
    const handleUpdate = useCallback(async (json: Record<string, unknown>, text: string) => {
        // If a save is already in progress, queue this one (only keep latest)
        if (savingRef.current) {
            pendingSaveRef.current = { json, text }
            return
        }

        savingRef.current = true
        setSaving(true)
        setSaved(false)

        try {
            await saveEditorContent(sourceId, json, text)
            setSaved(true)
            setTimeout(() => setSaved(false), 2000)
        } catch (e) {
            console.error("Failed to save:", e)
        } finally {
            savingRef.current = false
            setSaving(false)

            // Process queued save if any
            const pending = pendingSaveRef.current
            if (pending) {
                pendingSaveRef.current = null
                handleUpdate(pending.json, pending.text)
            }
        }
    }, [sourceId])

    // Manual save
    const handleManualSave = useCallback(async () => {
        if (!content) return
        try {
            setSaving(true)
            await saveEditorContent(sourceId, content)
            setSaved(true)
            setTimeout(() => setSaved(false), 2000)
        } catch (e) {
            console.error("Failed to save:", e)
        } finally {
            setSaving(false)
        }
    }, [sourceId, content])

    if (loading) {
        return (
            <div className="flex items-center justify-center h-screen">
                <div className="flex flex-col items-center gap-4">
                    <Loader2 className="h-8 w-8 animate-spin text-primary" />
                    <p className="text-muted-foreground">Loading editor...</p>
                </div>
            </div>
        )
    }

    if (error) {
        return (
            <div className="flex items-center justify-center h-screen">
                <div className="text-center">
                    <p className="text-destructive mb-4">{error}</p>
                    <Button variant="outline" onClick={() => router.back()}>Go Back</Button>
                </div>
            </div>
        )
    }

    return (
        <div className="editor-page">
            {/* Top bar */}
            <div className="editor-topbar">
                <div className="flex items-center gap-3">
                    <Button variant="ghost" size="sm" onClick={() => router.back()} className="gap-2">
                        <ArrowLeft className="h-4 w-4" />
                        <span className="hidden sm:inline">Back</span>
                    </Button>
                    <div className="min-w-0">
                        <h1 className="text-sm font-semibold truncate max-w-[300px] sm:max-w-[500px]">{sourceTitle}</h1>
                    </div>
                </div>

                <div className="flex items-center gap-2">
                    {/* Save status */}
                    <div className="text-xs text-muted-foreground flex items-center gap-1">
                        {saving && (
                            <>
                                <Loader2 className="h-3 w-3 animate-spin" />
                                Saving...
                            </>
                        )}
                        {saved && (
                            <>
                                <CheckCircle2 className="h-3 w-3 text-green-500" />
                                Saved
                            </>
                        )}
                    </div>

                    {/* Annotations toggle */}
                    <Button
                        variant={showAnnotations ? "secondary" : "ghost"}
                        size="sm"
                        onClick={() => setShowAnnotations(!showAnnotations)}
                        className="gap-2"
                    >
                        <MessageSquareDashed className="h-4 w-4" />
                        <span className="hidden sm:inline">Notes</span>
                    </Button>

                    <ShareDialog sourceId={sourceId} />

                    <Button variant="outline" size="sm" onClick={handleManualSave} disabled={saving} className="gap-2">
                        <Save className="h-4 w-4" />
                        <span className="hidden sm:inline">Save</span>
                    </Button>
                </div>
            </div>

            {/* Main content area */}
            <div className="editor-main">
                <div className="editor-content-area">
                    {content && (
                        <TiptapEditor
                            content={content}
                            onUpdate={handleUpdate}
                            sourceId={sourceId}
                            editable={true}
                        />
                    )}
                </div>

                {/* Annotation sidebar */}
                <AnnotationSidebar sourceId={sourceId} visible={showAnnotations} />
            </div>
        </div>
    )
}
