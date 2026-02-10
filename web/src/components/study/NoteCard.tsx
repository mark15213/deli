import * as React from "react"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogTrigger } from "@/components/ui/dialog"
import { BookmarkPlus, CheckCircle, Quote, ChevronLeft, ChevronRight } from "lucide-react"
import { cn } from "@/lib/utils"
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'

interface NoteCardProps {
    title?: string
    content: string
    images?: string[]
    source?: string
    onMarkRead: () => void
    onClip?: () => void
}

export function NoteCard({ title, content, images, source, onMarkRead, onClip }: NoteCardProps) {
    const [currentImageIndex, setCurrentImageIndex] = React.useState(0)

    const nextImage = () => {
        if (!images) return
        setCurrentImageIndex((prev) => (prev + 1) % images.length)
    }

    const prevImage = () => {
        if (!images) return
        setCurrentImageIndex((prev) => (prev - 1 + images.length) % images.length)
    }

    return (
        <div className="flex flex-col h-full bg-gradient-to-b from-background to-muted/20">
            {/* Unified Scrollable Container */}
            <div className="flex-1 overflow-y-auto custom-scrollbar">
                <div className="max-w-3xl mx-auto w-full flex flex-col p-4 md:p-8 space-y-8">

                    {/* Source Badge */}
                    {source && (
                        <div className="flex justify-center">
                            <span className="inline-flex items-center gap-1.5 text-xs font-semibold text-primary/80 uppercase tracking-widest bg-primary/10 px-4 py-1.5 rounded-full ring-1 ring-primary/20 backdrop-blur-sm">
                                <Quote className="w-3 h-3" />
                                {source}
                            </span>
                        </div>
                    )}

                    {/* Title */}
                    {title && (
                        <h2 className="text-2xl md:text-3xl font-bold text-center text-foreground tracking-tight leading-tight">
                            {title}
                        </h2>
                    )}

                    {/* Image Carousel */}
                    {images && images.length > 0 && (
                        <div className="relative group w-full aspect-video bg-muted/30 rounded-xl border overflow-hidden">
                            <Dialog>
                                <DialogTrigger asChild>
                                    <div className="w-full h-full cursor-zoom-in">
                                        <img
                                            src={`http://127.0.0.1:8000${images[currentImageIndex]}`}
                                            alt={`Figure ${currentImageIndex + 1}`}
                                            className="w-full h-full object-contain p-2"
                                        />
                                    </div>
                                </DialogTrigger>
                                <DialogContent className="max-w-7xl w-full p-1 bg-transparent border-none shadow-none sm:rounded-none">
                                    <div className="relative w-full h-full flex items-center justify-center">
                                        <img
                                            src={`http://127.0.0.1:8000${images[currentImageIndex]}`}
                                            alt={`Figure ${currentImageIndex + 1}`}
                                            className="max-h-[90vh] w-auto max-w-full rounded-lg shadow-2xl object-contain bg-background/95 backdrop-blur-sm"
                                        />
                                    </div>
                                </DialogContent>
                            </Dialog>

                            {/* Carousel Controls */}
                            {images.length > 1 && (
                                <>
                                    <button
                                        onClick={(e) => {
                                            e.stopPropagation()
                                            prevImage()
                                        }}
                                        className="absolute left-2 top-1/2 -translate-y-1/2 bg-background/80 hover:bg-background text-foreground p-2 rounded-full shadow-sm opacity-0 group-hover:opacity-100 transition-opacity"
                                    >
                                        <ChevronLeft className="h-5 w-5" />
                                    </button>
                                    <button
                                        onClick={(e) => {
                                            e.stopPropagation()
                                            nextImage()
                                        }}
                                        className="absolute right-2 top-1/2 -translate-y-1/2 bg-background/80 hover:bg-background text-foreground p-2 rounded-full shadow-sm opacity-0 group-hover:opacity-100 transition-opacity"
                                    >
                                        <ChevronRight className="h-5 w-5" />
                                    </button>
                                    <div className="absolute bottom-2 right-2 bg-background/80 px-2 py-1 rounded text-xs font-medium">
                                        {currentImageIndex + 1} / {images.length}
                                    </div>
                                </>
                            )}
                        </div>
                    )}

                    {/* Markdown Content */}
                    <div className={cn(
                        "prose prose-slate dark:prose-invert max-w-none mx-auto w-full",
                        "prose-headings:font-bold prose-headings:tracking-tight",
                        "prose-p:leading-relaxed prose-p:text-foreground/90",
                        "prose-blockquote:border-l-primary prose-blockquote:bg-muted/50 prose-blockquote:py-1 prose-blockquote:px-4 prose-blockquote:rounded-r-lg prose-blockquote:not-italic",
                        "prose-pre:bg-muted prose-pre:text-foreground prose-pre:border prose-pre:border-border",
                        "prose-code:text-primary prose-code:bg-primary/10 prose-code:px-1 prose-code:py-0.5 prose-code:rounded-md prose-code:before:content-none prose-code:after:content-none",
                        "prose-li:marker:text-primary/50",
                        "prose-img:rounded-lg prose-img:shadow-md",
                        "[&_.katex-display]:my-6 [&_.katex-display]:overflow-x-auto [&_.katex-display]:overflow-y-hidden",
                        content.length < 150 && !title
                            ? "prose-xl md:prose-2xl text-center font-medium leading-normal flex flex-col justify-center min-h-[200px]"
                            : "prose-base md:prose-lg"
                    )}>
                        <ReactMarkdown
                            remarkPlugins={[remarkGfm, remarkMath]}
                            rehypePlugins={[rehypeKatex]}
                            components={{
                                a: ({ node, ...props }) => (
                                    <a target="_blank" rel="noopener noreferrer" className="text-primary hover:underline underline-offset-4 decoration-primary/50 transition-colors" {...props} />
                                )
                            }}
                        >
                            {content}
                        </ReactMarkdown>
                    </div>
                </div>
            </div>

            {/* usage action bar */}
            <div className="shrink-0 p-6 border-t bg-background/80 backdrop-blur-md supports-[backdrop-filter]:bg-background/60">
                <div className="max-w-md mx-auto flex items-center justify-center gap-4">
                    {onClip && (
                        <Button
                            variant="secondary"
                            size="lg"
                            className="flex-1 h-12 shadow-sm border border-border/50 hover:bg-secondary/80 transition-all duration-300 transform hover:-translate-y-0.5 active:translate-y-0"
                            onClick={onClip}
                        >
                            <BookmarkPlus className="h-5 w-5 mr-2" />
                            Clip
                        </Button>
                    )}
                    <Button
                        size="lg"
                        className={cn(
                            "flex-1 h-12 shadow-md hover:shadow-lg transition-all duration-300 transform hover:-translate-y-0.5 active:translate-y-0",
                            "bg-primary hover:bg-primary/90 text-primary-foreground",
                            !onClip && "w-full max-w-sm"
                        )}
                        onClick={onMarkRead}
                    >
                        <CheckCircle className="h-5 w-5 mr-2" />
                        Mark as Read
                    </Button>
                </div>
            </div>
        </div>
    )
}
