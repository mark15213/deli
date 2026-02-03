"use client"

import { Plus, Link2, FileText, Loader2, Camera, RefreshCw, ExternalLink } from "lucide-react"
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
import { DetectResponse, SourceType, SourceCategory, SyncFrequency } from "@/types/source"
import { SourceCategoryBadge } from "./SourceCategoryBadge"

export function QuickAddModal({ onSourceAdded }: { onSourceAdded?: () => void }) {
    const [input, setInput] = useState("")
    const [isDetecting, setIsDetecting] = useState(false)
    const [isSubmitting, setIsSubmitting] = useState(false)
    const [open, setOpen] = useState(false)
    const [detectionResult, setDetectionResult] = useState<DetectResponse | null>(null)
    const [sourceName, setSourceName] = useState("")
    const [tags, setTags] = useState<string[]>([])

    // Subscription-specific config
    const [syncFrequency, setSyncFrequency] = useState<SyncFrequency>("DAILY")
    const [subscriptionConfig, setSubscriptionConfig] = useState<Record<string, any>>({})

    const debouncedInputRef = useRef<NodeJS.Timeout | null>(null)

    const isUrl = input.trim().startsWith("http")
    const isSubscription = detectionResult?.category === 'SUBSCRIPTION'

    useEffect(() => {
        // Reset state when input clears
        if (!input.trim()) {
            setDetectionResult(null)
            setSourceName("")
            setTags([])
            setSubscriptionConfig({})
            return
        }

        // Debounce detection
        if (debouncedInputRef.current) {
            clearTimeout(debouncedInputRef.current)
        }

        debouncedInputRef.current = setTimeout(async () => {
            if (input.length > 5) {
                setIsDetecting(true)
                try {
                    const result = await detectSource(input)
                    setDetectionResult(result)
                    setSourceName(result.metadata.title)
                    setTags(result.suggested_config?.tags || [])

                    // Set default subscription config if available
                    if (result.subscription_hints?.suggested_frequency) {
                        setSyncFrequency(result.subscription_hints.suggested_frequency)
                    }
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
    }, [input])

    const handleSubmit = async () => {
        if (!detectionResult) return

        setIsSubmitting(true)
        setOpen(false)

        const submittedName = sourceName
        const submittedTags = tags

        // Reset form state
        setInput("")
        setDetectionResult(null)
        setSourceName("")
        setTags([])
        setSubscriptionConfig({})

        try {
            const sourceData: any = {
                name: submittedName,
                type: detectionResult.detected_type,
                connection_config: {
                    url: detectionResult.metadata.url || input,
                    author: detectionResult.metadata.author,
                },
                ingestion_rules: {
                    tags: submittedTags,
                },
            }

            // Add subscription config for subscription sources
            if (isSubscription) {
                sourceData.subscription_config = {
                    sync_frequency: syncFrequency,
                    enabled: true,
                    ...subscriptionConfig,
                }
            }

            await createSource(sourceData)
            if (onSourceAdded) onSourceAdded()
        } catch (error) {
            console.error("Failed to create source:", error)
        } finally {
            setIsSubmitting(false)
        }
    }

    const getSourceTypeIcon = (type: SourceType) => {
        switch (type) {
            case 'ARXIV_PAPER':
            case 'PDF_DOCUMENT':
                return '📄'
            case 'WEB_ARTICLE':
                return '🌐'
            case 'TWEET_THREAD':
            case 'X_SOCIAL':
                return '🐦'
            case 'GITHUB_REPO':
                return '💻'
            case 'MANUAL_NOTE':
                return '📝'
            case 'RSS_FEED':
                return '📡'
            case 'HF_DAILY_PAPERS':
                return '🤗'
            case 'AUTHOR_BLOG':
                return '✍️'
            default:
                return '📎'
        }
    }

    const getSourceTypeName = (type: SourceType) => {
        const names: Record<SourceType, string> = {
            'ARXIV_PAPER': 'Arxiv Paper',
            'WEB_ARTICLE': 'Web Article',
            'TWEET_THREAD': 'Tweet/Thread',
            'GITHUB_REPO': 'GitHub Repo',
            'MANUAL_NOTE': 'Note',
            'PDF_DOCUMENT': 'PDF Document',
            'RSS_FEED': 'RSS Feed',
            'HF_DAILY_PAPERS': 'HuggingFace Daily',
            'AUTHOR_BLOG': 'Author Blog',
            'X_SOCIAL': 'X/Twitter',
            'NOTION_KB': 'Notion',
            'WEB_RSS': 'RSS Feed',
        }
        return names[type] || type
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
                            placeholder="Paste a URL (e.g. Arxiv, GitHub, RSS feed) or start typing..."
                            className="min-h-[100px] resize-none pr-10"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                        />
                        <div className="absolute top-3 right-3 text-muted-foreground">
                            {isDetecting ? <Loader2 className="h-4 w-4 animate-spin" /> : (isUrl ? <Link2 className="h-4 w-4" /> : <FileText className="h-4 w-4" />)}
                        </div>
                    </div>

                    {detectionResult && (
                        <div className={`rounded-lg p-4 border animate-in fade-in slide-in-from-top-2 ${isSubscription
                                ? 'bg-blue-500/5 border-blue-500/20'
                                : 'bg-emerald-500/5 border-emerald-500/20'
                            }`}>
                            {/* Category Header */}
                            <div className="flex items-center justify-between mb-3">
                                <SourceCategoryBadge category={detectionResult.category} />
                                <span className="text-xs text-muted-foreground">
                                    {getSourceTypeIcon(detectionResult.detected_type)} {getSourceTypeName(detectionResult.detected_type)}
                                </span>
                            </div>

                            <div className="flex gap-4">
                                {detectionResult.metadata.image && (
                                    <img src={detectionResult.metadata.image} alt="Preview" className="w-20 h-20 object-cover rounded-md" />
                                )}
                                <div className="flex-1 space-y-2">
                                    <Input
                                        value={sourceName}
                                        onChange={(e) => setSourceName(e.target.value)}
                                        className="font-medium h-9"
                                        placeholder="Source name"
                                    />
                                    {detectionResult.metadata.author && (
                                        <p className="text-xs text-muted-foreground font-medium">
                                            {detectionResult.metadata.author}
                                        </p>
                                    )}
                                    {detectionResult.metadata.description && (
                                        <p className="text-sm text-muted-foreground line-clamp-2">
                                            {detectionResult.metadata.description}
                                        </p>
                                    )}
                                </div>
                            </div>

                            {/* Subscription-specific UI */}
                            {isSubscription && (
                                <div className="mt-4 space-y-4">
                                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                                        <RefreshCw className="h-4 w-4" />
                                        <span>系统将定期检查新内容，自动解析入库</span>
                                    </div>

                                    <div className="grid grid-cols-2 gap-4">
                                        <div className="grid gap-1.5">
                                            <Label className="text-xs">同步频率</Label>
                                            <select
                                                className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm focus:outline-none focus:ring-1 focus:ring-ring"
                                                value={syncFrequency}
                                                onChange={(e) => setSyncFrequency(e.target.value as SyncFrequency)}
                                            >
                                                <option value="HOURLY">每小时</option>
                                                <option value="DAILY">每天</option>
                                                <option value="WEEKLY">每周</option>
                                            </select>
                                        </div>
                                        <div className="grid gap-1.5">
                                            <Label className="text-xs">Tags</Label>
                                            <Input
                                                value={tags.join(", ")}
                                                onChange={(e) => setTags(e.target.value.split(",").map((t: string) => t.trim()).filter(Boolean))}
                                                className="h-9"
                                                placeholder="Research, AI"
                                            />
                                        </div>
                                    </div>

                                    {/* Preview Items */}
                                    {detectionResult.subscription_hints?.preview_items &&
                                        detectionResult.subscription_hints.preview_items.length > 0 && (
                                            <div className="space-y-2">
                                                <Label className="text-xs text-muted-foreground">最近内容预览</Label>
                                                <div className="bg-background/50 rounded-md p-2 space-y-1">
                                                    {detectionResult.subscription_hints.preview_items.slice(0, 3).map((item, i) => (
                                                        <a
                                                            key={i}
                                                            href={item.url}
                                                            target="_blank"
                                                            rel="noopener noreferrer"
                                                            className="flex items-center gap-2 text-xs text-muted-foreground hover:text-foreground transition-colors group"
                                                        >
                                                            <span className="truncate flex-1">{item.title}</span>
                                                            {item.date && <span className="text-[10px] opacity-70">{item.date}</span>}
                                                            <ExternalLink className="h-3 w-3 opacity-0 group-hover:opacity-100" />
                                                        </a>
                                                    ))}
                                                </div>
                                            </div>
                                        )}
                                </div>
                            )}

                            {/* Snapshot-specific UI */}
                            {!isSubscription && (
                                <div className="mt-4 grid grid-cols-2 gap-4">
                                    <div className="grid gap-1.5 col-span-2">
                                        <Label className="text-xs">Tags</Label>
                                        <Input
                                            value={tags.join(", ")}
                                            onChange={(e) => setTags(e.target.value.split(",").map((t: string) => t.trim()).filter(Boolean))}
                                            className="h-9"
                                            placeholder="Research, Paper"
                                        />
                                    </div>
                                </div>
                            )}
                        </div>
                    )}
                </div>

                <DialogFooter>
                    <Button variant="ghost" onClick={() => setOpen(false)}>Cancel</Button>
                    <Button onClick={handleSubmit} disabled={!detectionResult || isSubmitting}>
                        {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                        {isSubscription ? (
                            <>
                                <RefreshCw className="mr-2 h-4 w-4" />
                                Subscribe
                            </>
                        ) : (
                            <>
                                <Camera className="mr-2 h-4 w-4" />
                                Parse & Save
                            </>
                        )}
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    )
}
