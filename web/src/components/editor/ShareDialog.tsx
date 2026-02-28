"use client"

import { useState, useCallback } from "react"
import { Share2, Copy, Check, ExternalLink, Trash2, Eye, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogTrigger } from "@/components/ui/dialog"
import { createShareLink, revokeShareLink, type ShareLink } from "@/lib/api/editor"

interface ShareDialogProps {
    sourceId: string
}

export function ShareDialog({ sourceId }: ShareDialogProps) {
    const [shareLink, setShareLink] = useState<ShareLink | null>(null)
    const [loading, setLoading] = useState(false)
    const [copied, setCopied] = useState(false)
    const [open, setOpen] = useState(false)

    const handleGenerate = useCallback(async () => {
        try {
            setLoading(true)
            const link = await createShareLink(sourceId)
            setShareLink(link)
        } catch (e) {
            console.error("Failed to create share link:", e)
        } finally {
            setLoading(false)
        }
    }, [sourceId])

    const handleRevoke = useCallback(async () => {
        try {
            setLoading(true)
            await revokeShareLink(sourceId)
            setShareLink(null)
        } catch (e) {
            console.error("Failed to revoke share link:", e)
        } finally {
            setLoading(false)
        }
    }, [sourceId])

    const handleCopy = useCallback(() => {
        if (!shareLink) return
        navigator.clipboard.writeText(shareLink.url)
        setCopied(true)
        setTimeout(() => setCopied(false), 2000)
    }, [shareLink])

    return (
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
                <Button variant="outline" size="sm" className="gap-2" onClick={() => { if (!shareLink) handleGenerate() }}>
                    <Share2 className="h-4 w-4" />
                    Share
                </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-md">
                <div className="space-y-4">
                    <div>
                        <h3 className="text-lg font-semibold">Share Paper</h3>
                        <p className="text-sm text-muted-foreground mt-1">
                            Generate a public link to share your paper analysis with anyone.
                        </p>
                    </div>

                    {loading ? (
                        <div className="flex items-center justify-center py-6">
                            <Loader2 className="h-6 w-6 animate-spin text-primary" />
                        </div>
                    ) : shareLink ? (
                        <div className="space-y-4">
                            {/* Link display */}
                            <div className="flex items-center gap-2 p-3 bg-muted/50 rounded-lg border">
                                <input
                                    type="text"
                                    value={shareLink.url}
                                    readOnly
                                    className="flex-1 bg-transparent text-sm text-foreground border-none outline-none"
                                />
                                <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={handleCopy}
                                    className="h-8 w-8 p-0 shrink-0"
                                >
                                    {copied ? (
                                        <Check className="h-4 w-4 text-green-500" />
                                    ) : (
                                        <Copy className="h-4 w-4" />
                                    )}
                                </Button>
                            </div>

                            {/* Stats */}
                            <div className="flex items-center gap-4 text-sm text-muted-foreground">
                                <span className="flex items-center gap-1">
                                    <Eye className="h-3.5 w-3.5" />
                                    {shareLink.view_count} views
                                </span>
                                <span className={`flex items-center gap-1 ${shareLink.is_active ? "text-green-600" : "text-destructive"}`}>
                                    <span className={`w-1.5 h-1.5 rounded-full ${shareLink.is_active ? "bg-green-500" : "bg-destructive"}`} />
                                    {shareLink.is_active ? "Active" : "Revoked"}
                                </span>
                            </div>

                            {/* Actions */}
                            <div className="flex gap-2">
                                <Button
                                    variant="outline"
                                    size="sm"
                                    className="flex-1 gap-2"
                                    onClick={() => window.open(shareLink.url, "_blank")}
                                >
                                    <ExternalLink className="h-4 w-4" />
                                    Open
                                </Button>
                                <Button
                                    variant="destructive"
                                    size="sm"
                                    className="gap-2"
                                    onClick={handleRevoke}
                                >
                                    <Trash2 className="h-4 w-4" />
                                    Revoke
                                </Button>
                            </div>
                        </div>
                    ) : (
                        <div className="text-center py-4">
                            <p className="text-sm text-muted-foreground mb-4">No share link generated yet.</p>
                            <Button onClick={handleGenerate} className="gap-2">
                                <Share2 className="h-4 w-4" />
                                Generate Link
                            </Button>
                        </div>
                    )}
                </div>
            </DialogContent>
        </Dialog>
    )
}
