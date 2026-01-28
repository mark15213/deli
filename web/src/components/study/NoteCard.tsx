"use client"

import { Button } from "@/components/ui/button"
import { BookmarkPlus, CheckCircle } from "lucide-react"
import { cn } from "@/lib/utils"
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

interface NoteCardProps {
    title?: string
    content: string
    source?: string
    onMarkRead: () => void
    onClip?: () => void
}

export function NoteCard({ title, content, source, onMarkRead, onClip }: NoteCardProps) {
    return (
        <div className="flex flex-col h-full">
            {/* Content Area - Instagram Story style */}
            <div className="flex-1 flex flex-col justify-center px-8 py-12">
                <div className="max-w-2xl mx-auto w-full">
                    {/* Source label */}
                    {source && (
                        <div className="mb-6 text-center">
                            <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider bg-muted px-3 py-1 rounded-full">
                                {source}
                            </span>
                        </div>
                    )}

                    {/* Main content - clean typography */}
                    <div className="bg-card border rounded-2xl p-8 shadow-lg overflow-y-auto max-h-[60vh]">
                        {title && (
                            <h2 className="text-2xl font-bold mb-4 text-center">{title}</h2>
                        )}
                        <div className={cn(
                            "prose dark:prose-invert max-w-none",
                            // Adjust prose style based on whether it is a short quote or a long note
                            content.length < 100 && !title ? "prose-lg text-center font-medium" : "prose-base leading-relaxed text-left"
                        )}>
                            <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                {content}
                            </ReactMarkdown>
                        </div>
                    </div>
                </div>
            </div>

            {/* Action Buttons */}
            <div className="p-6 border-t bg-card/50 backdrop-blur">
                <div className="max-w-md mx-auto flex gap-4">
                    {onClip && (
                        <Button
                            variant="outline"
                            size="lg"
                            className="flex-1 h-14 gap-2"
                            onClick={onClip}
                        >
                            <BookmarkPlus className="h-5 w-5" />
                            Clip
                        </Button>
                    )}
                    <Button
                        size="lg"
                        className={cn(
                            "flex-1 h-14 gap-2 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700",
                            !onClip && "max-w-xs mx-auto"
                        )}
                        onClick={onMarkRead}
                    >
                        <CheckCircle className="h-5 w-5" />
                        Mark as Read
                    </Button>
                </div>
            </div>
        </div>
    )
}
