"use client"

import { Button } from "@/components/ui/button"
import { BookmarkPlus, CheckCircle } from "lucide-react"
import { cn } from "@/lib/utils"

interface NoteCardProps {
    content: string
    source?: string
    onMarkRead: () => void
    onClip?: () => void
}

export function NoteCard({ content, source, onMarkRead, onClip }: NoteCardProps) {
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
                    <div className="bg-card border rounded-2xl p-8 shadow-lg">
                        <div className="prose dark:prose-invert prose-lg max-w-none">
                            <p className="text-xl leading-relaxed font-medium text-center">
                                "{content}"
                            </p>
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
