"use client"

import { type Editor } from "@tiptap/react"
import {
    Bold, Italic, Underline, Strikethrough,
    Heading1, Heading2, Heading3,
    List, ListOrdered, Quote,
    AlignLeft, AlignCenter, AlignRight,
    Link, Unlink, Image as ImageIcon,
    Undo, Redo, Minus, Highlighter,
    Table, Rows3, Columns3, Trash2,
} from "lucide-react"
import { useCallback, useRef, useState } from "react"
import { uploadEditorImage } from "@/lib/api/editor"
import { cn } from "@/lib/utils"

interface EditorToolbarProps {
    editor: Editor
    sourceId: string
}

function ToolbarButton({
    onClick,
    active,
    disabled,
    children,
    title,
}: {
    onClick: () => void
    active?: boolean
    disabled?: boolean
    children: React.ReactNode
    title?: string
}) {
    return (
        <button
            type="button"
            onClick={onClick}
            disabled={disabled}
            title={title}
            className={cn(
                "p-1.5 rounded-md transition-colors duration-150",
                "hover:bg-accent hover:text-accent-foreground",
                "disabled:opacity-40 disabled:cursor-not-allowed",
                active && "bg-accent text-accent-foreground ring-1 ring-border"
            )}
        >
            {children}
        </button>
    )
}

function ToolbarDivider() {
    return <div className="w-px h-5 bg-border mx-1" />
}

export function EditorToolbar({ editor, sourceId }: EditorToolbarProps) {
    const fileInputRef = useRef<HTMLInputElement>(null)

    const handleImageUpload = useCallback(async (file: File) => {
        try {
            const result = await uploadEditorImage(sourceId, file)
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"
            const fullUrl = result.url.startsWith("http") ? result.url : `${apiUrl}${result.url}`
            editor.chain().focus().setImage({ src: fullUrl }).run()
        } catch (e) {
            console.error("Failed to upload image:", e)
        }
    }, [editor, sourceId])

    const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0]
        if (file) {
            handleImageUpload(file)
            e.target.value = ""
        }
    }, [handleImageUpload])

    const handleLinkAdd = useCallback(() => {
        const previousUrl = editor.getAttributes("link").href
        const url = window.prompt("URL", previousUrl)
        if (url === null) return
        if (url === "") {
            editor.chain().focus().extendMarkRange("link").unsetLink().run()
            return
        }
        editor.chain().focus().extendMarkRange("link").setLink({ href: url }).run()
    }, [editor])

    const iconSize = 16

    return (
        <div className="editor-toolbar">
            <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleFileSelect}
                className="hidden"
            />

            <div className="flex items-center flex-wrap gap-0.5">
                {/* History */}
                <ToolbarButton onClick={() => editor.chain().focus().undo().run()} disabled={!editor.can().undo()} title="Undo">
                    <Undo size={iconSize} />
                </ToolbarButton>
                <ToolbarButton onClick={() => editor.chain().focus().redo().run()} disabled={!editor.can().redo()} title="Redo">
                    <Redo size={iconSize} />
                </ToolbarButton>

                <ToolbarDivider />

                {/* Text formatting */}
                <ToolbarButton onClick={() => editor.chain().focus().toggleBold().run()} active={editor.isActive("bold")} title="Bold">
                    <Bold size={iconSize} />
                </ToolbarButton>
                <ToolbarButton onClick={() => editor.chain().focus().toggleItalic().run()} active={editor.isActive("italic")} title="Italic">
                    <Italic size={iconSize} />
                </ToolbarButton>
                <ToolbarButton onClick={() => editor.chain().focus().toggleUnderline().run()} active={editor.isActive("underline")} title="Underline">
                    <Underline size={iconSize} />
                </ToolbarButton>
                <ToolbarButton onClick={() => editor.chain().focus().toggleStrike().run()} active={editor.isActive("strike")} title="Strikethrough">
                    <Strikethrough size={iconSize} />
                </ToolbarButton>
                <ToolbarButton onClick={() => editor.chain().focus().toggleHighlight().run()} active={editor.isActive("highlight")} title="Highlight">
                    <Highlighter size={iconSize} />
                </ToolbarButton>

                <ToolbarDivider />

                {/* Headings */}
                <ToolbarButton onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()} active={editor.isActive("heading", { level: 1 })} title="Heading 1">
                    <Heading1 size={iconSize} />
                </ToolbarButton>
                <ToolbarButton onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()} active={editor.isActive("heading", { level: 2 })} title="Heading 2">
                    <Heading2 size={iconSize} />
                </ToolbarButton>
                <ToolbarButton onClick={() => editor.chain().focus().toggleHeading({ level: 3 }).run()} active={editor.isActive("heading", { level: 3 })} title="Heading 3">
                    <Heading3 size={iconSize} />
                </ToolbarButton>

                <ToolbarDivider />

                {/* Lists */}
                <ToolbarButton onClick={() => editor.chain().focus().toggleBulletList().run()} active={editor.isActive("bulletList")} title="Bullet List">
                    <List size={iconSize} />
                </ToolbarButton>
                <ToolbarButton onClick={() => editor.chain().focus().toggleOrderedList().run()} active={editor.isActive("orderedList")} title="Ordered List">
                    <ListOrdered size={iconSize} />
                </ToolbarButton>
                <ToolbarButton onClick={() => editor.chain().focus().toggleBlockquote().run()} active={editor.isActive("blockquote")} title="Blockquote">
                    <Quote size={iconSize} />
                </ToolbarButton>
                <ToolbarButton onClick={() => editor.chain().focus().setHorizontalRule().run()} title="Horizontal Rule">
                    <Minus size={iconSize} />
                </ToolbarButton>

                <ToolbarDivider />

                {/* Alignment */}
                <ToolbarButton onClick={() => editor.chain().focus().setTextAlign("left").run()} active={editor.isActive({ textAlign: "left" })} title="Align Left">
                    <AlignLeft size={iconSize} />
                </ToolbarButton>
                <ToolbarButton onClick={() => editor.chain().focus().setTextAlign("center").run()} active={editor.isActive({ textAlign: "center" })} title="Align Center">
                    <AlignCenter size={iconSize} />
                </ToolbarButton>
                <ToolbarButton onClick={() => editor.chain().focus().setTextAlign("right").run()} active={editor.isActive({ textAlign: "right" })} title="Align Right">
                    <AlignRight size={iconSize} />
                </ToolbarButton>

                <ToolbarDivider />

                {/* Table */}
                <ToolbarButton onClick={() => editor.chain().focus().insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run()} title="Insert Table">
                    <Table size={iconSize} />
                </ToolbarButton>
                {editor.isActive("table") && (
                    <>
                        <ToolbarButton onClick={() => editor.chain().focus().addRowAfter().run()} title="Add Row">
                            <Rows3 size={iconSize} />
                        </ToolbarButton>
                        <ToolbarButton onClick={() => editor.chain().focus().addColumnAfter().run()} title="Add Column">
                            <Columns3 size={iconSize} />
                        </ToolbarButton>
                        <ToolbarButton onClick={() => editor.chain().focus().deleteRow().run()} title="Delete Row">
                            <span className="flex items-center gap-0.5"><Rows3 size={iconSize - 2} /><Trash2 size={iconSize - 4} /></span>
                        </ToolbarButton>
                        <ToolbarButton onClick={() => editor.chain().focus().deleteColumn().run()} title="Delete Column">
                            <span className="flex items-center gap-0.5"><Columns3 size={iconSize - 2} /><Trash2 size={iconSize - 4} /></span>
                        </ToolbarButton>
                        <ToolbarButton onClick={() => editor.chain().focus().deleteTable().run()} title="Delete Table">
                            <Trash2 size={iconSize} />
                        </ToolbarButton>
                    </>
                )}

                <ToolbarDivider />

                {/* Media */}
                <ToolbarButton onClick={() => fileInputRef.current?.click()} title="Upload Image">
                    <ImageIcon size={iconSize} />
                </ToolbarButton>
                <ToolbarButton onClick={handleLinkAdd} active={editor.isActive("link")} title="Add Link">
                    <Link size={iconSize} />
                </ToolbarButton>
                {editor.isActive("link") && (
                    <ToolbarButton onClick={() => editor.chain().focus().unsetLink().run()} title="Remove Link">
                        <Unlink size={iconSize} />
                    </ToolbarButton>
                )}
            </div>
        </div>
    )
}
