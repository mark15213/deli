"use client"

import { useState, useEffect } from "react"
import { useParams } from "next/navigation"
import { Loader2, ExternalLink, Eye } from "lucide-react"
import { getSharedContent, type SharedContent } from "@/lib/api/editor"
import { TiptapEditor } from "@/components/editor/TiptapEditor"

export default function SharedPage() {
    const params = useParams()
    const token = params.token as string

    const [data, setData] = useState<SharedContent | null>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        async function load() {
            try {
                setLoading(true)
                const content = await getSharedContent(token)
                setData(content)
            } catch (e) {
                console.error("Failed to load shared content:", e)
                setError("This link is invalid or has expired.")
            } finally {
                setLoading(false)
            }
        }
        load()
    }, [token])

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-background">
                <div className="flex flex-col items-center gap-4">
                    <Loader2 className="h-8 w-8 animate-spin text-primary" />
                    <p className="text-muted-foreground">Loading shared paper...</p>
                </div>
            </div>
        )
    }

    if (error || !data) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-background">
                <div className="text-center p-8 max-w-md">
                    <div className="text-5xl mb-4">🔗</div>
                    <h2 className="text-xl font-bold mb-2">Link Not Found</h2>
                    <p className="text-muted-foreground">{error || "This shared link doesn't exist."}</p>
                </div>
            </div>
        )
    }

    return (
        <div className="min-h-screen bg-background">
            {/* Header */}
            <header className="shared-header">
                <div className="max-w-4xl mx-auto px-6 py-4">
                    <div className="flex items-center justify-between">
                        <div className="min-w-0 flex-1">
                            <h1 className="text-xl font-bold text-foreground truncate">{data.source_title}</h1>
                            {data.source_url && (
                                <a
                                    href={data.source_url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="inline-flex items-center gap-1 text-xs text-primary hover:underline mt-1"
                                >
                                    <ExternalLink className="h-3 w-3" />
                                    View Original
                                </a>
                            )}
                        </div>
                        <div className="flex items-center gap-2 text-xs text-muted-foreground">
                            <Eye className="h-3.5 w-3.5" />
                            {data.view_count} views
                        </div>
                    </div>
                </div>
            </header>

            {/* Content */}
            <main className="max-w-4xl mx-auto px-6 py-8">
                <div className="shared-content-wrapper">
                    <TiptapEditor
                        content={data.content}
                        onUpdate={() => { }}
                        sourceId=""
                        editable={false}
                    />
                </div>

                {/* Annotations */}
                {data.annotations.length > 0 && (
                    <div className="mt-8 pt-8 border-t border-border">
                        <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-4">
                            Annotations ({data.annotations.length})
                        </h3>
                        <div className="grid gap-3">
                            {data.annotations.map((ann) => (
                                <div
                                    key={ann.id}
                                    className="p-3 rounded-lg border border-border"
                                    style={ann.type === "highlight" ? { borderLeftColor: ann.color || "#fef08a", borderLeftWidth: 3 } : undefined}
                                >
                                    <div className="text-xs text-muted-foreground capitalize mb-1">{ann.type}</div>
                                    {ann.body && <p className="text-sm text-foreground">{ann.body}</p>}
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </main>

            {/* Footer */}
            <footer className="border-t border-border mt-16">
                <div className="max-w-4xl mx-auto px-6 py-6 text-center">
                    <p className="text-xs text-muted-foreground">
                        Powered by <span className="font-semibold text-primary">Deli</span> — AI-powered paper analysis
                    </p>
                </div>
            </footer>
        </div>
    )
}
