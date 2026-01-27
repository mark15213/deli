"use client"

import { Plus, Link2, FileText, Loader2, CheckCircle, AlertCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog"
import { Textarea } from "@/components/ui/textarea"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useState, useEffect, useRef } from "react"
import { detectSource, createSource } from "@/lib/api/sources"
import { DetectResponse, SourceType } from "@/types/source"

export function QuickAddModal({ onSourceAdded }: { onSourceAdded?: () => void }) {
    const [input, setInput] = useState("")
    const [isDetecting, setIsDetecting] = useState(false)
    const [isSubmitting, setIsSubmitting] = useState(false)
    const [open, setOpen] = useState(false)
    const [detectionResult, setDetectionResult] = useState<DetectResponse | null>(null)
    const [sourceName, setSourceName] = useState("")
    const [config, setConfig] = useState<any>({})

    const debouncedInputRef = useRef<NodeJS.Timeout | null>(null)

    const isUrl = input.trim().startsWith("http")

    useEffect(() => {
        // Reset state when input clears
        if (!input.trim()) {
            setDetectionResult(null)
            setSourceName("")
            return
        }

        // Debounce detection
        if (debouncedInputRef.current) {
            clearTimeout(debouncedInputRef.current)
        }

        debouncedInputRef.current = setTimeout(async () => {
            if (input.length > 5 && isUrl) { // Only auto-detect URLs or long strings
                setIsDetecting(true)
                try {
                    const result = await detectSource(input)
                    setDetectionResult(result)
                    setSourceName(result.metadata.title)
                    setConfig(result.suggested_config)
                } catch (error) {
                    console.error("Detection failed", error)
                } finally {
                    setIsDetecting(false)
                }
            } else if (!isUrl && input.length > 10) {
                // Manual Note detection (mocking logic here if not fully backend driven for simple notes)
                // actually backend handles it.
                setIsDetecting(true)
                try {
                    const result = await detectSource(input)
                    setDetectionResult(result)
                    setSourceName(result.metadata.title)
                    setConfig(result.suggested_config)
                } catch (error) {
                    console.error("Detection failed", error)
                } finally {
                    setIsDetecting(false)
                }
            }
        }, 800)

        return () => {
            if (debouncedInputRef.current) {
                clearTimeout(debouncedInputRef.current)
            }
        }
    }, [input, isUrl])

    const handleSubmit = async () => {
        if (!detectionResult) return

        setIsSubmitting(true)
        try {
            await createSource({
                name: sourceName,
                type: detectionResult.detected_type,
                connection_config: {
                    // This varies by type, for now hacking generic mapping or assuming backend handles 'url' in config
                    // Ideally we map properly. Backend 'connection_config' is JSONB.
                    // For SourceCreate, we need to pass a dict.
                    // Let's assume for now we pass 'url' and whatever config we have.
                    url: detectionResult.metadata.url || input,
                    ...config
                },
                ingestion_rules: config // Using config as ingestion rules for now
            })
            setOpen(false)
            setInput("")
            setDetectionResult(null)
            if (onSourceAdded) onSourceAdded()
        } catch (error) {
            console.error(error)
        } finally {
            setIsSubmitting(false)
        }
    }

    return (
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
                <Button className="gap-2">
                    <Plus className="h-4 w-4" />
                    Quick Add
                </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[600px]">
                <DialogHeader>
                    <DialogTitle>Quick Capture</DialogTitle>
                    <DialogDescription>
                        Paste a URL to automatically detect content, or write a note.
                    </DialogDescription>
                </DialogHeader>

                <div className="grid gap-6 py-4">
                    <div className="relative">
                        <Textarea
                            placeholder="Paste a URL (e.g. Twitter, GitHub, Arxiv) or start typing..."
                            className="min-h-[100px] resize-none pr-10"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                        />
                        <div className="absolute top-3 right-3 text-muted-foreground">
                            {isDetecting ? <Loader2 className="h-4 w-4 animate-spin" /> : (isUrl ? <Link2 className="h-4 w-4" /> : <FileText className="h-4 w-4" />)}
                        </div>
                    </div>

                    {detectionResult && (
                        <div className="bg-muted/50 rounded-lg p-4 border animate-in fade-in slide-in-from-top-2">
                            <div className="flex gap-4">
                                {detectionResult.metadata.image && (
                                    <img src={detectionResult.metadata.image} alt="Preview" className="w-20 h-20 object-cover rounded-md" />
                                )}
                                <div className="flex-1 space-y-2">
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center gap-2">
                                            {detectionResult.metadata.icon_url && <img src={detectionResult.metadata.icon_url} className="w-4 h-4" />}
                                            <span className="text-xs font-semibold uppercase text-muted-foreground">{detectionResult.detected_type}</span>
                                        </div>
                                    </div>
                                    <Input
                                        value={sourceName}
                                        onChange={(e) => setSourceName(e.target.value)}
                                        className="font-medium h-8"
                                    />
                                    {detectionResult.metadata.author && (
                                        <p className="text-xs text-muted-foreground font-medium">
                                            {detectionResult.metadata.author}
                                        </p>
                                    )}
                                    <p className="text-sm text-muted-foreground line-clamp-2">
                                        {detectionResult.metadata.description}
                                    </p>
                                </div>
                            </div>

                            {/* Simple Config Form based on flags */}
                            <div className="mt-4 grid grid-cols-2 gap-4">
                                {detectionResult.form_schema?.allow_frequency_setting && (
                                    <div className="grid gap-1.5">
                                        <Label className="text-xs">Frequency</Label>
                                        <select
                                            className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm"
                                            value={config.fetch_frequency}
                                            onChange={(e) => setConfig({ ...config, fetch_frequency: e.target.value })}
                                        >
                                            <option value="HOURLY">Hourly</option>
                                            <option value="DAILY">Daily</option>
                                            <option value="WEEKLY">Weekly</option>
                                        </select>
                                    </div>
                                )}
                                <div className="grid gap-1.5">
                                    <Label className="text-xs">Tags</Label>
                                    <Input
                                        value={config.tags?.join(", ") || ""}
                                        onChange={(e) => setConfig({ ...config, tags: e.target.value.split(",").map((t: string) => t.trim()) })}
                                        className="h-9"
                                    />
                                </div>
                            </div>
                        </div>
                    )}
                </div>

                <DialogFooter>
                    <Button variant="ghost" onClick={() => setOpen(false)}>Cancel</Button>
                    <Button onClick={handleSubmit} disabled={!detectionResult || isSubmitting}>
                        {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                        Add Source
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    )
}
