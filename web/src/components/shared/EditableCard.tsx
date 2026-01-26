"use client"

import { useState } from "react"
import { Pencil, Check, X, AlertOctagon } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { cn } from "@/lib/utils"

interface EditableCardProps {
    content: string
    onSave: (newContent: string) => void
    className?: string
}

export function EditableCard({ content, onSave, className }: EditableCardProps) {
    const [isEditing, setIsEditing] = useState(false)
    const [value, setValue] = useState(content)

    const handleSave = () => {
        onSave(value)
        setIsEditing(false)
    }

    const handleCancel = () => {
        setValue(content)
        setIsEditing(false)
    }

    if (isEditing) {
        return (
            <div className={cn("relative rounded-xl border-2 border-primary/50 p-4 bg-background", className)}>
                <Textarea
                    value={value}
                    onChange={(e) => setValue(e.target.value)}
                    className="min-h-[120px] mb-10 text-base"
                />
                <div className="absolute bottom-4 right-4 flex items-center gap-2">
                    <Button size="sm" variant="ghost" onClick={handleCancel}>
                        <X className="h-4 w-4" />
                    </Button>
                    <Button size="sm" onClick={handleSave}>
                        <Check className="h-4 w-4 mr-1" /> Save
                    </Button>
                </div>
            </div>
        )
    }

    return (
        <div
            className={cn(
                "group relative rounded-xl border p-6 bg-card hover:border-primary/30 transition-all",
                className
            )}
        >
            <p className="whitespace-pre-wrap">{value}</p>

            <div className="absolute top-4 right-4 flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                <Button
                    variant="outline"
                    size="sm"
                    className="h-8 w-8 p-0"
                    onClick={() => setIsEditing(true)}
                    title="Edit Content"
                >
                    <Pencil className="h-3 w-3" />
                </Button>
                <Button
                    variant="outline"
                    size="sm"
                    className="h-8 w-8 p-0 text-destructive hover:text-destructive"
                    title="Mark as Bad Generation"
                >
                    <AlertOctagon className="h-3 w-3" />
                </Button>
            </div>
        </div>
    )
}
