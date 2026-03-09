"use client"

import { useState } from "react"
import { Plus, Loader2, Link as LinkIcon, FileText, Rss } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog"
import { api } from "@/lib/api"

interface AddSourceDialogProps {
    onSuccess?: () => void
}

export function AddSourceDialog({ onSuccess }: AddSourceDialogProps) {
    const [open, setOpen] = useState(false)
    const [url, setUrl] = useState("")
    const [title, setTitle] = useState("")
    const [isDetecting, setIsDetecting] = useState(false)
    const [detectedType, setDetectedType] = useState<"snapshot" | "subscription" | null>(null)
    const [saving, setSaving] = useState(false)

    const handleDetect = () => {
        if (!url) return
        setIsDetecting(true)
        setDetectedType(null)

        // Simple detection logic
        setTimeout(() => {
            setIsDetecting(false)
            // If URL contains rss, feed, or atom, treat as subscription
            if (url.toLowerCase().includes('rss') || url.toLowerCase().includes('feed') || url.toLowerCase().includes('atom')) {
                setDetectedType("subscription")
            } else {
                // Otherwise treat as snapshot
                setDetectedType("snapshot")
            }

            // Try to extract title from URL
            try {
                const urlObj = new URL(url)
                const pathParts = urlObj.pathname.split('/').filter(Boolean)
                if (pathParts.length > 0) {
                    setTitle(pathParts[pathParts.length - 1].replace(/-/g, ' '))
                }
            } catch (e) {
                // Invalid URL, ignore
            }
        }, 800)
    }

    const handleSave = async () => {
        if (!detectedType || !url) return

        setSaving(true)
        try {
            if (detectedType === "snapshot") {
                await api.createSnapshot({
                    title: title || url,
                    url: url,
                    status: "pending"
                })
            } else {
                await api.createSubscription({
                    title: title || url,
                    url: url,
                    frequency: "Manual"
                })
            }

            setOpen(false)
            setUrl("")
            setTitle("")
            setDetectedType(null)
            onSuccess?.()
        } catch (error: any) {
            alert(error.message || '保存失败')
        } finally {
            setSaving(false)
        }
    }

    return (
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
                <Button className="gap-2">
                    <Plus className="h-4 w-4" />
                    Add Source
                </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[500px]">
                <DialogHeader>
                    <DialogTitle>Add Information Source</DialogTitle>
                    <DialogDescription>
                        Paste a URL to a paper, blog post, or RSS feed. Gulp will automatically detect the type.
                    </DialogDescription>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                    <div className="flex gap-2">
                        <div className="relative flex-1">
                            <LinkIcon className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                            <Input
                                placeholder="https://arxiv.org/abs/... or https://.../rss"
                                className="pl-9"
                                value={url}
                                onChange={(e) => setUrl(e.target.value)}
                                onKeyDown={(e) => {
                                    if (e.key === "Enter") handleDetect()
                                }}
                            />
                        </div>
                        <Button variant="secondary" onClick={handleDetect} disabled={isDetecting || !url}>
                            {isDetecting ? <Loader2 className="h-4 w-4 animate-spin" /> : "Detect"}
                        </Button>
                    </div>

                    {detectedType && (
                        <>
                            <div className="rounded-lg border bg-muted/50 p-4 mt-2 flex items-center gap-4 animate-in fade-in slide-in-from-bottom-2">
                                <div className="bg-background p-2 rounded-md shadow-sm">
                                    {detectedType === "snapshot" ? <FileText className="h-6 w-6 text-blue-500" /> : <Rss className="h-6 w-6 text-orange-500" />}
                                </div>
                                <div className="flex-1 space-y-1">
                                    <p className="text-sm font-medium leading-none">
                                        {detectedType === "snapshot" ? "Single Snapshot (e.g. Paper)" : "Subscription Feed (e.g. RSS)"}
                                    </p>
                                    <p className="text-sm text-muted-foreground">
                                        {detectedType === "snapshot"
                                            ? "Will be processed once into a workspace."
                                            : "Will periodically sync new items automatically."}
                                    </p>
                                </div>
                            </div>

                            <div>
                                <label className="text-sm font-medium">Title (optional)</label>
                                <Input
                                    value={title}
                                    onChange={(e) => setTitle(e.target.value)}
                                    placeholder="Enter a custom title"
                                    className="mt-1"
                                />
                            </div>
                        </>
                    )}
                </div>
                <DialogFooter>
                    <Button variant="outline" onClick={() => setOpen(false)}>Cancel</Button>
                    <Button onClick={handleSave} disabled={!detectedType || saving}>
                        {saving ? 'Saving...' : 'Save Source'}
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    )
}
