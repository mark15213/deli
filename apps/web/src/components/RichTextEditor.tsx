"use client"

import { useEditor, EditorContent } from "@tiptap/react"
import StarterKit from "@tiptap/starter-kit"
import Image from "@tiptap/extension-image"
import Placeholder from "@tiptap/extension-placeholder"
import CharacterCount from "@tiptap/extension-character-count"
import {
    Bold,
    Italic,
    Heading1,
    Heading2,
    List,
    ListOrdered,
    Quote,
    Image as ImageIcon,
    FunctionSquare
} from "lucide-react"

import { cn } from "@/lib/utils"

interface RichTextEditorProps {
    content: string
    onChange: (content: string) => void
}

const MenuBar = ({ editor }: { editor: any }) => {
    if (!editor) {
        return null
    }

    const addImage = () => {
        const url = window.prompt("Enter image URL")
        if (url) {
            editor.chain().focus().setImage({ src: url }).run()
        }
    }

    const insertMath = () => {
        window.alert("Math formula editing is temporarily disabled pending extension installation.")
    }

    return (
        <div className="flex flex-wrap items-center gap-1 p-2 border-b bg-muted/20 sticky top-0 z-10 backdrop-blur-sm">
            <button
                onClick={() => editor.chain().focus().toggleBold().run()}
                disabled={!editor.can().chain().focus().toggleBold().run()}
                className={cn(
                    "p-2 rounded-md transition-colors",
                    editor.isActive("bold") ? "bg-accent text-accent-foreground" : "text-muted-foreground hover:bg-muted/50 hover:text-foreground"
                )}
                title="Bold"
            >
                <Bold className="h-4 w-4" />
            </button>
            <button
                onClick={() => editor.chain().focus().toggleItalic().run()}
                disabled={!editor.can().chain().focus().toggleItalic().run()}
                className={cn(
                    "p-2 rounded-md transition-colors",
                    editor.isActive("italic") ? "bg-accent text-accent-foreground" : "text-muted-foreground hover:bg-muted/50 hover:text-foreground"
                )}
                title="Italic"
            >
                <Italic className="h-4 w-4" />
            </button>

            <div className="w-px h-4 bg-border mx-1" />

            <button
                onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()}
                className={cn(
                    "p-2 rounded-md transition-colors",
                    editor.isActive("heading", { level: 1 }) ? "bg-accent text-accent-foreground" : "text-muted-foreground hover:bg-muted/50 hover:text-foreground"
                )}
                title="Heading 1"
            >
                <Heading1 className="h-4 w-4" />
            </button>
            <button
                onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
                className={cn(
                    "p-2 rounded-md transition-colors",
                    editor.isActive("heading", { level: 2 }) ? "bg-accent text-accent-foreground" : "text-muted-foreground hover:bg-muted/50 hover:text-foreground"
                )}
                title="Heading 2"
            >
                <Heading2 className="h-4 w-4" />
            </button>

            <div className="w-px h-4 bg-border mx-1" />

            <button
                onClick={() => editor.chain().focus().toggleBulletList().run()}
                className={cn(
                    "p-2 rounded-md transition-colors",
                    editor.isActive("bulletList") ? "bg-accent text-accent-foreground" : "text-muted-foreground hover:bg-muted/50 hover:text-foreground"
                )}
                title="Bullet List"
            >
                <List className="h-4 w-4" />
            </button>
            <button
                onClick={() => editor.chain().focus().toggleOrderedList().run()}
                className={cn(
                    "p-2 rounded-md transition-colors",
                    editor.isActive("orderedList") ? "bg-accent text-accent-foreground" : "text-muted-foreground hover:bg-muted/50 hover:text-foreground"
                )}
                title="Ordered List"
            >
                <ListOrdered className="h-4 w-4" />
            </button>
            <button
                onClick={() => editor.chain().focus().toggleBlockquote().run()}
                className={cn(
                    "p-2 rounded-md transition-colors",
                    editor.isActive("blockquote") ? "bg-accent text-accent-foreground" : "text-muted-foreground hover:bg-muted/50 hover:text-foreground"
                )}
                title="Quote"
            >
                <Quote className="h-4 w-4" />
            </button>

            <div className="w-px h-4 bg-border mx-1" />

            <button
                onClick={addImage}
                className="p-2 rounded-md transition-colors text-muted-foreground hover:bg-muted/50 hover:text-foreground"
                title="Insert Image"
            >
                <ImageIcon className="h-4 w-4" />
            </button>

            <button
                onClick={insertMath}
                className="p-2 rounded-md transition-colors text-muted-foreground hover:bg-muted/50 hover:text-foreground"
                title="Insert Math"
            >
                <FunctionSquare className="h-4 w-4" />
            </button>
        </div>
    )
}

export function RichTextEditor({ content, onChange }: RichTextEditorProps) {
    const editor = useEditor({
        extensions: [
            StarterKit,
            Image.configure({
                inline: true,
                allowBase64: true,
            }),
            Placeholder.configure({
                placeholder: 'Start writing your rich notes here...',
            }),
            CharacterCount
        ],
        content,
        onUpdate: ({ editor }) => {
            onChange(editor.getHTML())
        },
        immediatelyRender: false,
        editorProps: {
            attributes: {
                class: "prose prose-sm sm:prose-base focus:outline-none max-w-none px-8 py-6 min-h-[500px] text-foreground mx-auto",
            },
        },
    })

    return (
        <div className="border border-border rounded-xl bg-card shadow-sm overflow-hidden flex flex-col w-full h-full max-h-[calc(100vh-250px)]">
            <MenuBar editor={editor} />
            <div className="flex-1 overflow-y-auto w-full bg-background/50">
                <EditorContent editor={editor} className="h-full" />
            </div>
            <div className="border-t py-1.5 px-4 text-xs text-muted-foreground text-right bg-muted/10">
                {editor?.storage.characterCount.words()} words
            </div>
        </div>
    )
}
