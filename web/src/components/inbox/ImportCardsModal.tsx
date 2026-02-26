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
import { FileUp, Loader2, CheckCircle2, AlertCircle, ArrowLeft } from "lucide-react"
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

    const [selectedFile, setSelectedFile] = React.useState<File | null>(null)
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
            setSelectedFile(null)
            setUploadResult(null)
            setUploadError(null)
        }
    }, [isOpen])

    const handleFileUpload = async (file: File, preview: boolean) => {
        if (!selectedSourceId) {
            setUploadError("Please select a source first")
            return
        }

        setUploading(true)
        setUploadError(null)

        if (!preview) {
            setUploadResult(null)
        }

        try {
            const result = await uploadDocument(selectedSourceId, file, preview)
            setUploadResult(result)
            if (!preview) {
                onSuccess?.()
            }
        } catch (e: any) {
            setUploadError(e.message || "Upload failed")
            setUploadResult(null)
        } finally {
            setUploading(false)
        }
    }

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault()
        setDragOver(false)

        const file = e.dataTransfer.files[0]
        if (file) {
            setSelectedFile(file)
            handleFileUpload(file, true) // Always preview first
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
            setSelectedFile(file)
            handleFileUpload(file, true) // Always preview first
        }
        // Reset input so the same file can be selected again if needed
        if (fileInputRef.current) {
            fileInputRef.current.value = ""
        }
    }

    const handleConfirmImport = () => {
        if (selectedFile) {
            handleFileUpload(selectedFile, false)
        }
    }

    const handleReset = () => {
        setSelectedFile(null)
        setUploadResult(null)
        setUploadError(null)
    }

    const handleClose = () => {
        if (!uploading) {
            onClose()
        }
    }

    const isPreviewMode = uploadResult?.is_preview === true
    const isSuccessMode = uploadResult && !uploadResult.is_preview

    return (
        <Dialog open={isOpen} onOpenChange={handleClose}>
            <DialogContent className="sm:max-w-2xl max-h-[90vh] flex flex-col">
                <DialogHeader>
                    <DialogTitle>Import Cards</DialogTitle>
                    <DialogDescription>
                        {isPreviewMode
                            ? "Preview detected cards before finalizing import."
                            : "Upload CSV, Markdown, or text files to import flashcards. Cards will be added to your inbox for review."}
                    </DialogDescription>
                </DialogHeader>

                <div className="flex-1 overflow-y-auto space-y-4 py-4 pr-2">
                    {/* Error Display */}
                    {uploadError && (
                        <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-lg">
                            <div className="flex items-center gap-2 text-red-600 dark:text-red-400 font-medium text-sm">
                                <AlertCircle className="h-4 w-4 shrink-0" />
                                <span>{uploadError}</span>
                            </div>
                        </div>
                    )}

                    {!isPreviewMode && !isSuccessMode && (
                        <>
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
                                className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors cursor-pointer mt-4
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
                            <div className="text-xs text-muted-foreground bg-muted/30 p-3 rounded-lg mt-4">
                                <p className="font-medium mb-1">CSV Format:</p>
                                <code className="block bg-background/50 p-2 rounded text-[10px] overflow-x-auto whitespace-pre">
                                    {`question,answer,type,tags
"What is React?","A JavaScript library",qa,"react,frontend"`}
                                </code>
                            </div>
                        </>
                    )}

                    {/* Preview Mode */}
                    {isPreviewMode && (
                        <div className="space-y-4">
                            <div className="p-3 bg-blue-500/10 border border-blue-500/30 rounded-lg flex items-center justify-between">
                                <div className="flex items-center gap-2 text-blue-600 dark:text-blue-400 font-medium text-sm">
                                    <CheckCircle2 className="h-4 w-4" />
                                    Detected {uploadResult.cards_created} cards in {selectedFile?.name}.
                                </div>
                                <Button variant="ghost" size="sm" onClick={handleReset} className="h-8 text-xs">
                                    <ArrowLeft className="h-3 w-3 mr-1" /> Try Another File
                                </Button>
                            </div>

                            <div className="border rounded-md divide-y overflow-hidden flex flex-col max-h-[400px]">
                                <div className="bg-muted px-4 py-2 text-xs font-semibold grid grid-cols-12 gap-2">
                                    <div className="col-span-2">Type</div>
                                    <div className="col-span-5">Question</div>
                                    <div className="col-span-5">Answer</div>
                                </div>
                                <div className="overflow-y-auto">
                                    {uploadResult.cards.map((card, i) => (
                                        <div key={i} className="px-4 py-3 text-sm grid grid-cols-12 gap-2 hover:bg-muted/50">
                                            <div className="col-span-2">
                                                <span className="px-2 py-0.5 bg-primary/10 text-primary rounded-full text-xs font-medium uppercase">
                                                    {card.type}
                                                </span>
                                            </div>
                                            <div className="col-span-5 font-medium line-clamp-2" title={card.question}>
                                                {card.question}
                                            </div>
                                            <div className="col-span-5 text-muted-foreground line-clamp-2" title={card.answer || ""}>
                                                {card.type === 'mcq' && card.options?.length
                                                    ? `Options: ${card.options.join(', ')}`
                                                    : card.answer || <span className="italic opacity-50">No answer provided</span>}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Success Mode */}
                    {isSuccessMode && (
                        <div className="p-6 text-center space-y-4 flex flex-col items-center justify-center py-12">
                            <div className="h-16 w-16 bg-green-500/20 rounded-full flex items-center justify-center mb-2">
                                <CheckCircle2 className="h-8 w-8 text-green-500" />
                            </div>
                            <h3 className="text-xl font-semibold">Import Successful</h3>
                            <p className="text-muted-foreground text-sm max-w-sm">
                                Successfully imported {uploadResult.cards_created} cards. They are now in your inbox for review.
                            </p>
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="flex justify-end gap-2 pt-4 border-t mt-auto">
                    {!isSuccessMode && (
                        <Button variant="outline" onClick={handleClose} disabled={uploading}>
                            Cancel
                        </Button>
                    )}

                    {isSuccessMode && (
                        <Button onClick={handleClose} className="w-full sm:w-auto">
                            Done
                        </Button>
                    )}

                    {isPreviewMode && (
                        <Button onClick={handleConfirmImport} disabled={uploading} className="gap-2">
                            {uploading ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
                            Confirm Import ({uploadResult?.cards_created})
                        </Button>
                    )}
                </div>
            </DialogContent>
        </Dialog>
    )
}
