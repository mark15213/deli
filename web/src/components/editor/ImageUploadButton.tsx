"use client"

import { useRef, useCallback } from "react"
import { ImagePlus } from "lucide-react"
import { uploadEditorImage } from "@/lib/api/editor"

interface ImageUploadButtonProps {
    sourceId: string
    onImageUploaded: (url: string) => void
}

export function ImageUploadButton({ sourceId, onImageUploaded }: ImageUploadButtonProps) {
    const fileInputRef = useRef<HTMLInputElement>(null)

    const handleFileSelect = useCallback(async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0]
        if (!file) return

        try {
            const result = await uploadEditorImage(sourceId, file)
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"
            const fullUrl = result.url.startsWith("http") ? result.url : `${apiUrl}${result.url}`
            onImageUploaded(fullUrl)
        } catch (err) {
            console.error("Failed to upload image:", err)
        }
        e.target.value = ""
    }, [sourceId, onImageUploaded])

    return (
        <>
            <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleFileSelect}
                className="hidden"
            />
            <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="inline-flex items-center gap-2 px-3 py-2 text-sm font-medium rounded-lg border border-dashed border-border hover:border-primary/50 hover:bg-accent transition-colors"
            >
                <ImagePlus className="h-4 w-4" />
                Upload Image
            </button>
        </>
    )
}
