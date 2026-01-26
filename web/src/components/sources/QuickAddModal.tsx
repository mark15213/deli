"use client"

import { Plus, Link2, FileText, Loader2 } from "lucide-react"
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
import { useState } from "react"

export function QuickAddModal() {
    const [input, setInput] = useState("")
    const [isSubmitting, setIsSubmitting] = useState(false)
    const [open, setOpen] = useState(false)

    const isUrl = input.trim().startsWith("http")

    const handleSubmit = async () => {
        setIsSubmitting(true)
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1500))
        setIsSubmitting(false)
        setOpen(false)
        setInput("")
    }

    return (
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
                <Button className="gap-2">
                    <Plus className="h-4 w-4" />
                    Quick Add
                </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[500px]">
                <DialogHeader>
                    <DialogTitle>Quick Capture</DialogTitle>
                    <DialogDescription>
                        Save a URL to read later or jot down a quick note.
                    </DialogDescription>
                </DialogHeader>

                <div className="grid gap-4 py-4">
                    <div className="relative">
                        <Textarea
                            placeholder="Paste a URL or start typing..."
                            className="min-h-[150px] resize-none pr-10"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                        />
                        <div className="absolute top-3 right-3 text-muted-foreground">
                            {isUrl ? <Link2 className="h-4 w-4" /> : <FileText className="h-4 w-4" />}
                        </div>
                    </div>
                </div>

                <DialogFooter>
                    <Button variant="ghost" onClick={() => setOpen(false)}>Cancel</Button>
                    <Button onClick={handleSubmit} disabled={!input.trim() || isSubmitting}>
                        {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                        {isUrl ? "Save Link" : "Save Note"}
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    )
}
