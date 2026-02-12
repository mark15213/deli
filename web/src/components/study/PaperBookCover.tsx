"use client"

import { cn } from "@/lib/utils"
import { BookOpen, FileText, GraduationCap } from "lucide-react"

interface PaperBookCoverProps {
    title: string
    summary?: string
    cardCount: number
    sourceType?: string
    onClick: () => void
}

// Generate a deterministic color based on the title string
function getBookColor(title: string): string {
    const colors = [
        "from-blue-600 to-blue-800",
        "from-emerald-600 to-emerald-800",
        "from-violet-600 to-violet-800",
        "from-amber-600 to-amber-800",
        "from-rose-600 to-rose-800",
        "from-cyan-600 to-cyan-800",
        "from-indigo-600 to-indigo-800",
        "from-teal-600 to-teal-800",
        "from-fuchsia-600 to-fuchsia-800",
        "from-orange-600 to-orange-800",
    ]
    let hash = 0
    for (let i = 0; i < title.length; i++) {
        hash = title.charCodeAt(i) + ((hash << 5) - hash)
    }
    return colors[Math.abs(hash) % colors.length]
}

export function PaperBookCover({ title, summary, cardCount, sourceType, onClick }: PaperBookCoverProps) {
    const bookColor = getBookColor(title)

    return (
        <div
            className="book-container cursor-pointer group"
            onClick={onClick}
        >
            <div className="book">
                {/* Front Cover */}
                <div className={cn(
                    "book-cover",
                    "bg-gradient-to-br",
                    bookColor,
                    "text-white"
                )}>
                    {/* Spine effect */}
                    <div className="absolute left-0 top-0 bottom-0 w-4 bg-black/20 rounded-l-md" />

                    {/* Top decorative bar */}
                    <div className="absolute top-0 left-4 right-0 h-1 bg-white/20 rounded-tr-md" />

                    {/* Content */}
                    <div className="relative z-10 p-5 pl-7 flex flex-col h-full">
                        {/* Type badge */}
                        <div className="flex items-center gap-1.5 mb-3">
                            <div className="bg-white/20 px-2 py-0.5 rounded text-[10px] font-semibold uppercase tracking-wider backdrop-blur-sm">
                                {sourceType === "ARXIV_PAPER" ? "Paper" : sourceType === "WEB_ARTICLE" ? "Article" : "Source"}
                            </div>
                        </div>

                        {/* Title */}
                        <h3 className="text-sm font-bold leading-tight line-clamp-3 mb-3 group-hover:underline decoration-white/40 underline-offset-2 transition-all">
                            {title}
                        </h3>

                        {/* TL;DR Summary */}
                        {summary && (
                            <div className="flex-1 overflow-hidden">
                                <p className="text-[11px] leading-relaxed text-white/75 line-clamp-5">
                                    {summary}
                                </p>
                            </div>
                        )}
                        {!summary && (
                            <div className="flex-1 flex items-center justify-center">
                                <BookOpen className="h-10 w-10 text-white/20" />
                            </div>
                        )}

                        {/* Bottom info */}
                        <div className="mt-auto pt-3 border-t border-white/15 flex items-center justify-between">
                            <div className="flex items-center gap-1.5 text-white/70">
                                <GraduationCap className="h-3.5 w-3.5" />
                                <span className="text-[11px] font-medium">
                                    {cardCount} {cardCount === 1 ? "card" : "cards"}
                                </span>
                            </div>
                            <div className="text-[10px] text-white/50 font-medium uppercase tracking-wider bg-white/10 px-2 py-0.5 rounded">
                                Open →
                            </div>
                        </div>
                    </div>

                    {/* Subtle paper texture overlay */}
                    <div className="absolute inset-0 rounded-md opacity-[0.03] bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIzMDAiIGhlaWdodD0iMzAwIj48ZmlsdGVyIGlkPSJhIj48ZmVUdXJidWxlbmNlIHR5cGU9ImZyYWN0YWxOb2lzZSIgYmFzZUZyZXF1ZW5jeT0iLjc1IiBzdGl0Y2hUaWxlcz0ic3RpdGNoIi8+PC9maWx0ZXI+PHJlY3Qgd2lkdGg9IjMwMCIgaGVpZ2h0PSIzMDAiIGZpbHRlcj0idXJsKCNhKSIgb3BhY2l0eT0iMC4xIi8+PC9zdmc+')]" />
                </div>

                {/* Book side (pages effect) */}
                <div className="book-pages" />
            </div>
        </div>
    )
}
