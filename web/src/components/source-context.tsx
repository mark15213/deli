import { Link2 } from "lucide-react"
import { cn } from "@/lib/utils"

interface SourceContextProps {
    source: string
    type: string
    className?: string
}

export function SourceContext({ source, type, className }: SourceContextProps) {
    return (
        <div className={cn("flex items-center gap-2 text-xs text-muted-foreground", className)}>
            <Link2 className="h-3 w-3" />
            <span className="font-medium">{source}</span>
            <span>•</span>
            <span className="capitalize">{type}</span>
        </div>
    )
}
