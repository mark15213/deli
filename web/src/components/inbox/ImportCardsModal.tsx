"use client"

import React from "react"
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select"
import { FileUp, Loader2, CheckCircle2, AlertCircle } from "lucide-react"
import { uploadDocument, type UploadResult } from "@/lib/api/sources"
import { getSources } from "@/lib/api/sources"
import type { Source } from "@/types/source"

interface ImportCardsModalProps {
    isOpen: boolean
    onClose: () => void
    onSuccess?: () => void
}

export function ImportCardsModal({ isOpen, onClose, onSuccess }: ImportCardsModalProps) {
    const [sources, setSources] = React.useState<Source[]>([])
    const [selectedSourceId, setSelectedSourceId] = React.useState<string>("")
    const [loadingSources, setLoadingSources] = React.useState(false)

    const [uploading, setUploading] = React.useState(false)
    const [uploadResult, setUploadResult] = React.useState<UploadResult | null>(null)
    const [uploadError, setUploadError] = React.useState<string | null>(null)
    const [dragOver, setDragOver] = React.useState(false)
    const fileInputRef = React.useRef<HTMLInputElement>(null)

    // Fetch sources when modal opens
    React.useEffect(() => {
        if (isOpen) {
            setLoadingSources(true)
            getSources()
                .then(data => setSources(data))
                .catch(err => console.error("Failed to load sources:", err))
                .finally(() => setLoadingSources(false))

            // Reset state
            setSelectedSourceId("")
            setUploadResult(null)
            setUploadError(null)
        }
    }, [isOpen])

    const handleFileUpload = async (file: File) => {
        if (!selectedSourceId) {
            setUploadError("Please select a source first")
            return
        }

        setUploading(true)
        setUploadError(null)
        setUploadResult(null)

        try {
            const result = await uploadDocument(selectedSourceId, file)
            setUploadResult(result)
            onSuccess?.()
        } catch (e: any) {
            setUploadError(e.message || "Upload failed")
        } finally {
            setUploading(false)
        }
    }

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault()
        setDragOver(false)

        const file = e.dataTransfer.files[0]
        if (file) {
            handleFileUpload(file)
        }
    }

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault()
        setDragOver(true)
    }

    const handleDragLeave = () => {
        setDragOver(false)
    }

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0]
        if (file) {
            handleFileUpload(file)
        }
    }

    const handleClose = () => {
        if (!uploading) {
            onClose()
        }
    }

    return (
        <Dialog open={isOpen} onOpenChange={handleClose}>
            <DialogContent className="sm:max-w-md">
                <DialogHeader>
                    <DialogTitle>Import Cards</DialogTitle>
                    <DialogDescription>
                        Upload CSV, Markdown, or text files to import flashcards. Cards will be added to your inbox for review.
                    </DialogDescription>
                </DialogHeader>

                <div className="space-y-4 py-4">
                    {/* Source Selection */}
                    <div className="space-y-2">
                        <label className="text-sm font-medium">
                            Associate with Source <span className="text-red-500">*</span>
                        </label>
                        <Select
                            value={selectedSourceId}
                            onValueChange={setSelectedSourceId}
                            disabled={loadingSources || uploading}
                        >
                            <SelectTrigger>
                                <SelectValue placeholder={loadingSources ? "Loading sources..." : "Select a source"} />
                            </SelectTrigger>
                            <SelectContent>
                                {sources.map(source => (
                                    <SelectItem key={source.id} value={source.id}>
                                        <div className="flex items-center gap-2">
                                            <span>{source.name}</span>
                                            <span className="text-xs text-muted-foreground">({source.type})</span>
                                        </div>
                                    </SelectItem>
                                ))}
                                {sources.length === 0 && !loadingSources && (
                                    <div className="px-2 py-4 text-center text-sm text-muted-foreground">
                                        No sources found. Create a source first.
                                    </div>
                                )}
                            </SelectContent>
                        </Select>
                    </div>

                    {/* Drop Zone */}
                    <div
                        className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors cursor-pointer
                            ${!selectedSourceId ? 'opacity-50 pointer-events-none' : ''}
                            ${dragOver ? 'border-primary bg-primary/5' : 'border-muted-foreground/25 hover:border-primary/50'}
                            ${uploading ? 'pointer-events-none opacity-50' : ''}`}
                        onDrop={handleDrop}
                        onDragOver={handleDragOver}
                        onDragLeave={handleDragLeave}
                        onClick={() => selectedSourceId && fileInputRef.current?.click()}
                    >
                        <input
                            ref={fileInputRef}
                            type="file"
                            className="hidden"
                            accept=".csv,.md,.txt"
                            onChange={handleFileSelect}
                        />

                        {uploading ? (
                            <div className="flex flex-col items-center gap-2">
                                <Loader2 className="h-8 w-8 animate-spin text-primary" />
                                <p className="text-sm text-muted-foreground">Parsing document...</p>
                            </div>
                        ) : (
                            <div className="flex flex-col items-center gap-2">
                                <FileUp className="h-8 w-8 text-muted-foreground" />
                                <div>
                                    <p className="font-medium text-sm">
                                        {selectedSourceId ? "Drop file here or click to browse" : "Select a source first"}
                                    </p>
                                    <p className="text-xs text-muted-foreground mt-1">
                                        Supports CSV, Markdown (.md), and Text (.txt)
                                    </p>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* CSV Format Help */}
                    <div className="text-xs text-muted-foreground bg-muted/30 p-3 rounded-lg">
                        <p className="font-medium mb-1">CSV Format:</p>
                        <code className="block bg-background/50 p-2 rounded text-[10px] overflow-x-auto whitespace-pre">
                            {`question,answer,type,tags
"What is React?","A JavaScript library",qa,"react,frontend"`}
                        </code>
                    </div>

                    {/* Result */}
                    {uploadResult && (
                        <div className="p-3 bg-green-500/10 border border-green-500/30 rounded-lg">
                            <div className="flex items-center gap-2 text-green-600 dark:text-green-400 font-medium text-sm">
                                <CheckCircle2 className="h-4 w-4" />
                                Successfully imported {uploadResult.cards_created} cards!
                            </div>
                            <p className="text-xs text-muted-foreground mt-1">
                                Cards are now in your inbox for review.
                            </p>
                        </div>
                    )}

                    {/* Error */}
                    {uploadError && (
                        <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-lg">
                            <div className="flex items-center gap-2 text-red-600 dark:text-red-400 font-medium text-sm">
                                <AlertCircle className="h-4 w-4" />
                                {uploadError}
                            </div>
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="flex justify-end gap-2">
                    <Button variant="outline" onClick={handleClose} disabled={uploading}>
                        {uploadResult ? "Done" : "Cancel"}
                    </Button>
                </div>
            </DialogContent>
        </Dialog>
    )
}
