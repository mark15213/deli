"use client"

import { useEditor, EditorContent } from "@tiptap/react"
import StarterKit from "@tiptap/starter-kit"
import Image from "@tiptap/extension-image"
import Highlight from "@tiptap/extension-highlight"
import Placeholder from "@tiptap/extension-placeholder"
import Underline from "@tiptap/extension-underline"
import TextAlign from "@tiptap/extension-text-align"
import Link from "@tiptap/extension-link"
import { Table } from "@tiptap/extension-table"
import { TableRow } from "@tiptap/extension-table-row"
import { TableCell } from "@tiptap/extension-table-cell"
import { TableHeader } from "@tiptap/extension-table-header"
import { MathInline, MathDisplay, MathExtension } from "./extensions/MathExtension"
import "katex/dist/katex.min.css"
import "@benrbray/prosemirror-math/dist/prosemirror-math.css"
import { useCallback, useEffect, useRef } from "react"
import { EditorToolbar } from "./EditorToolbar"
import { uploadEditorImage } from "@/lib/api/editor"
import { Plugin, PluginKey } from "@tiptap/pm/state"

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
            Table.configure({
                resizable: true,
                HTMLAttributes: { class: "editor-table" },
            }),
            TableRow,
            TableHeader,
            TableCell,
            MathInline,
            MathDisplay,
            MathExtension,
        ],
        content: content as any,
        editable,
        immediatelyRender: false,
        editorProps: {
            attributes: {
                class: "tiptap-editor-content",
            },
            handlePaste: (view, event, slice) => {
                if (!editable) return false
                const items = Array.from(event.clipboardData?.items || [])
                for (const item of items) {
                    if (item.type.indexOf("image") === 0) {
                        const file = item.getAsFile()
                        if (file) {
                            event.preventDefault()
                            uploadEditorImage(sourceId, file).then((result) => {
                                const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"
                                const fullUrl = result.url.startsWith("http") ? result.url : `${apiUrl}${result.url}`
                                const { schema } = view.state
                                const node = schema.nodes.image.create({ src: fullUrl })
                                const transaction = view.state.tr.replaceSelectionWith(node)
                                view.dispatch(transaction)
                            }).catch(e => console.error("Failed to upload pasted image:", e))
                            return true
                        }
                    }
                }
                return false
            },
            handleDrop: (view, event, slice, moved) => {
                if (!editable || moved) return false
                const items = Array.from(event.dataTransfer?.files || [])
                for (const file of items) {
                    if (file.type.indexOf("image") === 0) {
                        event.preventDefault()
                        uploadEditorImage(sourceId, file).then((result) => {
                            const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"
                            const fullUrl = result.url.startsWith("http") ? result.url : `${apiUrl}${result.url}`
                            const coordinates = view.posAtCoords({ left: event.clientX, top: event.clientY })
                            const { schema } = view.state
                            const node = schema.nodes.image.create({ src: fullUrl })

                            if (coordinates) {
                                const transaction = view.state.tr.insert(coordinates.pos, node)
                                view.dispatch(transaction)
                            }
                        }).catch(e => console.error("Failed to upload dropped image:", e))
                        return true
                    }
                }
                return false
            }
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
