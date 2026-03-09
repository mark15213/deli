"use client"

import { useState } from "react"
import { ArrowLeft, Zap, FileText, Sparkles, Edit3, Trash2, Send, Plus, ChevronDown, CheckCircle2, Database } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import { RichTextEditor } from "@/components/RichTextEditor"

interface WorkspaceProps {
    source: any;
    onClose: () => void;
}

export function Workspace({ source, onClose }: WorkspaceProps) {
    const [content, setContent] = useState("")
    const [chatInput, setChatInput] = useState("")
    const [isGenerating, setIsGenerating] = useState(false)
    const [cardsGenerated, setCardsGenerated] = useState(0)
    const [isEditing, setIsEditing] = useState(false)
    const [isStudioOpen, setIsStudioOpen] = useState(true)
    const [targetKB, setTargetKB] = useState("AI Architecture")

    // Mock generated cards state
    const [cards, setCards] = useState<number[]>([])

    const handleGenerate = () => {
        setIsGenerating(true)
        setTimeout(() => {
            setIsGenerating(false)
            setCardsGenerated(5)
            setCards([1, 2, 3, 4, 5])
        }, 2000)
    }

    const handleDeleteCard = (id: number) => {
        setCards(cards.filter(c => c !== id))
    }

    return (
        <div className="h-full flex flex-col bg-zinc-100 relative z-10 overflow-hidden text-zinc-900 font-sans p-4 gap-4">

            {/* Top Global Navigation bar (Optional but keeps it grounded) */}
            <div className="flex items-center justify-between px-2 bg-transparent shrink-0 border-b-0 relative">
                <Button variant="ghost" size="sm" onClick={onClose} className="rounded-full hover:bg-zinc-200/50 text-zinc-600 gap-2 h-8 px-3 cursor-pointer">
                    <ArrowLeft className="h-4 w-4" />
                    Back to Feed
                </Button>

                {/* Target KB Selector in Header */}
                <div className="flex items-center justify-center absolute left-1/2 -translate-x-1/2">
                    <Button variant="ghost" size="sm" className="rounded-full h-8 px-4 bg-zinc-200/50 text-zinc-700 hover:bg-zinc-200 gap-2 text-xs font-semibold shadow-[0_1px_2px_0_rgba(0,0,0,0.02)] cursor-pointer">
                        <Database className="h-3.5 w-3.5 text-blue-500" />
                        Target: {targetKB}
                        <ChevronDown className="h-3 w-3 text-zinc-400" />
                    </Button>
                </div>

                <div className="flex items-center gap-2">
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setIsStudioOpen(!isStudioOpen)}
                        className="rounded-full h-8 px-4 bg-white shadow-sm border-zinc-200 text-zinc-600 hover:bg-zinc-50 cursor-pointer"
                    >
                        {isStudioOpen ? "Close Studio" : "Open Studio"}
                    </Button>
                </div>
            </div>

            {/* Main Layout */}
            <div className="flex-1 flex gap-4 overflow-hidden relative">

                {/* Center Column: Editor/Chat/Summary */}
                <div className="flex-1 bg-white rounded-[2rem] shadow-sm border border-zinc-200 flex flex-col overflow-hidden relative">

                    {/* Header Area */}
                    <div className="px-6 py-4 border-b border-zinc-100 flex items-center justify-between shrink-0 bg-white z-10">
                        <div className="flex items-center gap-2">
                            <h2 className="text-base font-semibold text-zinc-700 ml-2">对话 (Chat)</h2>
                            <Button variant="ghost" size="sm" className="h-7 text-xs rounded-full gap-1 text-zinc-500 hover:text-zinc-900 ml-2 cursor-pointer">
                                <ChevronDown className="h-3 w-3" />
                                1 个来源
                            </Button>
                        </div>
                        <Button
                            onClick={() => setIsEditing(!isEditing)}
                            variant={isEditing ? "default" : "outline"}
                            size="sm"
                            className={`rounded-full gap-2 shadow-sm transition-all h-9 px-5 cursor-pointer ${isEditing ? 'bg-zinc-900 text-white hover:bg-zinc-800 border-transparent' : 'bg-white hover:bg-zinc-50 border-zinc-200 text-zinc-700'}`}
                        >
                            <Edit3 className="h-3.5 w-3.5" />
                            {isEditing ? "View Summary" : "Edit Notes"}
                        </Button>
                    </div>

                    {/* Scrollable Content Area */}
                    <div className="flex-1 overflow-y-auto px-8 py-8 md:px-12 pb-32">
                        <div className="max-w-3xl mx-auto">
                            {/* Document Title Header inside content */}
                            <h1 className="text-3xl font-bold tracking-tight text-zinc-900 mb-6 leading-tight">
                                {source.title}
                            </h1>

                            {isEditing ? (
                                <div className="flex flex-col gap-4 animate-in fade-in slide-in-from-bottom-2 duration-300 bg-white">
                                    <div className="p-1 rounded-2xl border border-zinc-200 bg-zinc-50/50 shadow-sm min-h-[400px]">
                                        <RichTextEditor
                                            content={content}
                                            onChange={setContent}
                                        />
                                    </div>
                                    <div className="flex justify-end mt-2">
                                        <Button size="sm" onClick={() => setIsEditing(false)} className="rounded-full shadow-sm bg-zinc-900 text-white hover:bg-zinc-800 px-6 cursor-pointer">
                                            Save Notes
                                        </Button>
                                    </div>
                                </div>
                            ) : (
                                <div className="prose prose-zinc max-w-none animate-in fade-in duration-500">
                                    <p className="text-lg text-zinc-800 leading-relaxed font-medium">
                                        {source.summary || "This is a placeholder for the AI-generated blog summary of the document. The actual summary will provide a concise overview of the key concepts, main arguments, and important details found in the original source material. It reads like a well-crafted article."}
                                    </p>

                                    <div className="mt-8 space-y-6 text-zinc-600 leading-relaxed">
                                        <p>
                                            In this NotebookLM-inspired view, this central area serves as the foundational text. You can read the synthesized blog summary here. It allows the user to quickly scroll through and review the salient points of the paper or article without needing to read the entire original document.
                                        </p>
                                        <p>
                                            If you wish to add your own thoughts, simply click "Edit Notes" at the top. The Rich Text Editor will slide in, allowing you to synthesize knowledge, highlight specific quotes, and write down your own interpretations or questions.
                                        </p>
                                        <p>
                                            At the bottom is a fixed chat input bar. You can chat with the source document directly to ask questions, clarify confusing passages, or request the system to generate specific insights.
                                        </p>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Fixed Chat Input Bar at Bottom */}
                    <div className="absolute bottom-6 left-1/2 -translate-x-1/2 w-full max-w-2xl px-6">
                        <div className="bg-white rounded-[2rem] shadow-[0_8px_30px_-4px_rgba(0,0,0,0.1)] border border-zinc-200 flex items-center p-2 pl-6 focus-within:ring-2 focus-within:ring-zinc-900/20 focus-within:border-zinc-300 transition-all">
                            <input
                                type="text"
                                value={chatInput}
                                onChange={(e) => setChatInput(e.target.value)}
                                placeholder="开始输入... (Ask a question about this source)"
                                className="flex-1 bg-transparent border-none outline-none text-sm text-zinc-900 placeholder:text-zinc-400"
                            />
                            <Button size="icon" className="h-10 w-10 rounded-full bg-zinc-100 hover:bg-zinc-200 text-zinc-600 shrink-0 ml-2 cursor-pointer transition-colors" disabled={!chatInput.trim()}>
                                <Send className="h-4 w-4" />
                            </Button>
                        </div>
                    </div>
                </div>

                {/* Studio / Knowledge Cards (Right) */}
                {isStudioOpen && (
                    <div className="w-[320px] lg:w-[380px] flex-shrink-0 bg-white rounded-[2rem] shadow-sm border border-zinc-200 flex flex-col overflow-hidden animate-in slide-in-from-right duration-300">

                        {/* Pipeline / Studio Top Half */}
                        <div className="p-4 border-b border-zinc-100 bg-white shrink-0">
                            <div className="flex items-center gap-2 mb-4 px-2">
                                <h3 className="font-semibold text-sm text-zinc-800">Studio</h3>
                            </div>

                            <div className="grid grid-cols-2 gap-3 mb-4">
                                <div className="bg-zinc-50 border border-zinc-200 rounded-2xl p-4 flex flex-col gap-3 shadow-sm cursor-pointer hover:border-blue-400 hover:bg-blue-50/50 transition-colors group">
                                    <div className="h-8 w-8 rounded-full bg-white flex items-center justify-center border border-zinc-100 shadow-sm">
                                        <Sparkles className="h-4 w-4 text-blue-500 group-hover:animate-pulse" />
                                    </div>
                                    <span className="text-xs font-semibold text-zinc-700">Audio Overview</span>
                                </div>
                                <div className="bg-zinc-50 border border-zinc-200 rounded-2xl p-4 flex flex-col gap-3 shadow-sm cursor-pointer hover:border-emerald-400 hover:bg-emerald-50/50 transition-colors group">
                                    <div className="h-8 w-8 rounded-full bg-white flex items-center justify-center border border-zinc-100 shadow-sm">
                                        <FileText className="h-4 w-4 text-emerald-500 group-hover:animate-pulse" />
                                    </div>
                                    <span className="text-xs font-semibold text-zinc-700">Study Guide</span>
                                </div>
                            </div>

                            <Button
                                onClick={handleGenerate}
                                disabled={isGenerating}
                                variant="outline"
                                className={`w-full gap-2 rounded-xl h-12 shadow-sm transition-all border-dashed border-2 cursor-pointer ${isGenerating ? 'bg-zinc-50 text-zinc-500 border-zinc-200' : 'bg-white text-zinc-700 hover:bg-zinc-50 hover:text-zinc-900 border-zinc-300'}`}
                            >
                                {isGenerating ? <Zap className="h-4 w-4 animate-pulse text-yellow-500" /> : <Plus className="h-4 w-4" />}
                                {isGenerating ? "Processing Pipeline..." : "Generate Knowledge"}
                            </Button>
                        </div>

                        {/* Knowledge Cards Bottom Half */}
                        <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-4 bg-zinc-50/50">
                            {cards.length === 0 ? (
                                <div className="h-full flex flex-col items-center justify-center text-center p-6 text-zinc-400">
                                    <Sparkles className="h-8 w-8 mb-4 text-zinc-300" />
                                    <p className="text-sm font-medium text-zinc-600">Studio output will save here.</p>
                                    <p className="text-xs mt-1 text-zinc-500 max-w-[200px]">Generate cards to review and delete low quality outputs.</p>
                                </div>
                            ) : (
                                <div className="flex flex-col gap-4 animate-in fade-in duration-500">
                                    <div className="flex items-center justify-between px-1">
                                        <h4 className="text-[11px] font-bold text-zinc-500 uppercase tracking-wider">Generated Cards ({cards.length})</h4>
                                    </div>
                                    {cards.map((id, index) => (
                                        <Card key={id} className="bg-white shadow-sm border-zinc-200 transition-all hover:shadow-md hover:border-zinc-300 rounded-2xl overflow-hidden group">
                                            <CardHeader className="p-3 pb-2 border-b border-transparent">
                                                <div className="flex justify-between items-start">
                                                    <CardTitle className="text-sm font-bold text-zinc-800 pt-1 pl-1">Concept #{index + 1}</CardTitle>
                                                    <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                                        <Button variant="ghost" size="icon" className="h-7 w-7 rounded-lg hover:bg-zinc-100 text-zinc-500 cursor-pointer">
                                                            <Edit3 className="h-3.5 w-3.5" />
                                                        </Button>
                                                        <Button
                                                            variant="ghost"
                                                            size="icon"
                                                            onClick={() => handleDeleteCard(id)}
                                                            className="h-7 w-7 rounded-lg hover:bg-red-50 hover:text-red-600 text-zinc-500 cursor-pointer"
                                                        >
                                                            <Trash2 className="h-3.5 w-3.5" />
                                                        </Button>
                                                    </div>
                                                </div>
                                            </CardHeader>
                                            <CardContent className="p-3 pt-0 text-[13px] text-zinc-600 leading-relaxed">
                                                <p className="line-clamp-4 pl-1">This is a generated knowledge card. It distills complex information from the source text into an atomic piece of knowledge suitable for review in the Studio pipeline.</p>
                                            </CardContent>
                                            <div className="px-3 pb-3 pt-2 flex justify-start border-t border-zinc-100 bg-zinc-50/50">
                                                <Button variant="outline" size="sm" className="h-7 text-xs font-semibold text-zinc-700 bg-white border-zinc-200 hover:bg-zinc-100 px-3 rounded-full gap-1.5 shadow-sm cursor-pointer">
                                                    <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
                                                    Review
                                                </Button>
                                            </div>
                                        </Card>
                                    ))}
                                </div>
                            )}
                        </div>

                    </div>
                )}
            </div>
        </div>
    )
}
