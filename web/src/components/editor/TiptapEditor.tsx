"use client"

import { useEditor, EditorContent } from "@tiptap/react"
import StarterKit from "@tiptap/starter-kit"
import Image from "@tiptap/extension-image"
import Highlight from "@tiptap/extension-highlight"
import Placeholder from "@tiptap/extension-placeholder"
import Underline from "@tiptap/extension-underline"
import TextAlign from "@tiptap/extension-text-align"
import Link from "@tiptap/extension-link"
import MathExtension from "tiptap-math"
import "katex/dist/katex.min.css"
import "@benrbray/prosemirror-math/dist/prosemirror-math.css"
import { useCallback, useEffect, useRef } from "react"
import { EditorToolbar } from "./EditorToolbar"

interface TiptapEditorProps {
    content: Record<string, unknown>
    onUpdate: (json: Record<string, unknown>, text: string) => void
    sourceId: string
    editable?: boolean
}

export function TiptapEditor({ content, onUpdate, sourceId, editable = true }: TiptapEditorProps) {
    const debounceRef = useRef<NodeJS.Timeout | null>(null)

    const editor = useEditor({
        extensions: [
            StarterKit.configure({
                heading: { levels: [1, 2, 3] },
            }),
            Image.configure({
                HTMLAttributes: { class: "editor-image" },
            }),
            Highlight.configure({
                multicolor: true,
            }),
            Placeholder.configure({
                placeholder: "Start writing your paper analysis...",
            }),
            Underline,
            TextAlign.configure({
                types: ["heading", "paragraph"],
            }),
            Link.configure({
                openOnClick: false,
                HTMLAttributes: {
                    class: "editor-link",
                    target: "_blank",
                    rel: "noopener noreferrer",
                },
            }),
            MathExtension,
        ],
        content: content as any,
        editable,
        immediatelyRender: false,
        editorProps: {
            attributes: {
                class: "tiptap-editor-content",
            },
        },
        onUpdate: ({ editor }) => {
            if (!editable) return
            // Debounce saves
            if (debounceRef.current) clearTimeout(debounceRef.current)
            debounceRef.current = setTimeout(() => {
                const json = editor.getJSON()
                const text = editor.getText()
                onUpdate(json, text)
            }, 3000) // 3 second debounce
        },
    })

    // Update content when prop changes (initial load)
    useEffect(() => {
        if (editor && content && !editor.isDestroyed) {
            const currentJSON = JSON.stringify(editor.getJSON())
            const newJSON = JSON.stringify(content)
            if (currentJSON !== newJSON) {
                editor.commands.setContent(content as any)
            }
        }
    }, [content, editor])

    // Cleanup
    useEffect(() => {
        return () => {
            if (debounceRef.current) clearTimeout(debounceRef.current)
        }
    }, [])

    if (!editor) return null

    return (
        <div className="tiptap-editor">
            {editable && <EditorToolbar editor={editor} sourceId={sourceId} />}
            <div className="tiptap-editor-wrapper">
                <EditorContent editor={editor} />
            </div>
        </div>
    )
}
