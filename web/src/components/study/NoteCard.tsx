import { Button } from "@/components/ui/button"
import { BookmarkPlus, CheckCircle, Quote } from "lucide-react"
import { cn } from "@/lib/utils"
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'

interface NoteCardProps {
    title?: string
    content: string
    source?: string
    onMarkRead: () => void
    onClip?: () => void
}

export function NoteCard({ title, content, source, onMarkRead, onClip }: NoteCardProps) {
    return (
        <div className="flex flex-col h-full bg-gradient-to-b from-background to-muted/20">
            {/* Content Area */}
            <div className="flex-1 flex flex-col px-4 py-8 md:px-8 md:py-10 overflow-hidden">
                <div className="max-w-3xl mx-auto w-full flex flex-col h-full">
                    {/* Header with Source & Title */}
                    <div className="mb-6 space-y-4 shrink-0">
                        {source && (
                            <div className="flex justify-center">
                                <span className="inline-flex items-center gap-1.5 text-xs font-semibold text-primary/80 uppercase tracking-widest bg-primary/10 px-4 py-1.5 rounded-full ring-1 ring-primary/20 backdrop-blur-sm">
                                    <Quote className="w-3 h-3" />
                                    {source}
                                </span>
                            </div>
                        )}
                        {title && (
                            <h2 className="text-2xl md:text-3xl font-bold text-center text-foreground tracking-tight leading-tight">
                                {title}
                            </h2>
                        )}
                    </div>

                    {/* Main Content - Scrollable Note */}
                    <div className="flex-1 min-h-0 relative group">
                        <div className="absolute inset-0 bg-card border rounded-xl sm:rounded-2xl shadow-sm hover:shadow-md transition-shadow duration-300 overflow-hidden">
                            <div className="h-full overflow-y-auto custom-scrollbar p-6 md:p-8 lg:p-10">
                                <div className={cn(
                                    "prose prose-slate dark:prose-invert max-w-none mx-auto",
                                    "prose-headings:font-bold prose-headings:tracking-tight",
                                    "prose-p:leading-relaxed prose-p:text-foreground/90",
                                    "prose-blockquote:border-l-primary prose-blockquote:bg-muted/50 prose-blockquote:py-1 prose-blockquote:px-4 prose-blockquote:rounded-r-lg prose-blockquote:not-italic",
                                    "prose-pre:bg-muted prose-pre:text-foreground prose-pre:border prose-pre:border-border",
                                    "prose-code:text-primary prose-code:bg-primary/10 prose-code:px-1 prose-code:py-0.5 prose-code:rounded-md prose-code:before:content-none prose-code:after:content-none",
                                    "prose-li:marker:text-primary/50",
                                    "prose-img:rounded-lg prose-img:shadow-md",
                                    // Math styling adjustments
                                    "[&_.katex-display]:my-6 [&_.katex-display]:overflow-x-auto [&_.katex-display]:overflow-y-hidden",
                                    content.length < 150 && !title
                                        ? "prose-xl md:prose-2xl text-center font-medium leading-normal flex flex-col justify-center min-h-[200px]"
                                        : "prose-base md:prose-lg"
                                )}>
                                    <ReactMarkdown
                                        remarkPlugins={[remarkGfm, remarkMath]}
                                        rehypePlugins={[rehypeKatex]}
                                        components={{
                                            // Custom link rendering to open in new tab
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
