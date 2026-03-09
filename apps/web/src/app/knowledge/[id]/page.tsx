"use client"

import { useState } from "react"
import { ArrowLeft, Search, Plus, Filter, Database, MessageSquareText, Layers, Tag, Trash2, Edit3, Link as LinkIcon, Clock } from "lucide-react"
import Link from "next/link"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

// Mock internal KB data
const KB_DATA = {
    id: "kb-1",
    title: "AI Architecture",
    description: "Core concepts, patterns, and papers regarding LLMs and agent architectures.",
    cardCount: 142,
    lastUpdated: "2 hours ago",
    color: "text-blue-500",
    bg: "bg-blue-50",
    border: "border-blue-100",
    icon: Database
}

// Mock Cards inside the KB
const MOCK_CARDS = [
    {
        id: "c-1",
        title: "Transformer Architecture",
        content: "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder. The best performing models also connect the encoder and decoder through an attention mechanism.",
        sourceTitle: "Attention Is All You Need",
        sourceUrl: "https://arxiv.org/abs/1706.03762",
        tags: ["Core", "Attention", "2017"],
        createdAt: "Oct 12, 2025"
    },
    {
        id: "c-2",
        title: "Retrieval-Augmented Generation (RAG)",
        content: "RAG is an AI framework that retrieves facts from an external knowledge base to ground large language models (LLMs) on the most accurate, up-to-date information and to give users insight into LLMs' generative process.",
        sourceTitle: "What is RAG?",
        sourceUrl: "https://www.ibm.com/topics/retrieval-augmented-generation",
        tags: ["Architecture", "Production"],
        createdAt: "Nov 5, 2025"
    },
    {
        id: "c-3",
        title: "Chain of Thought (CoT) Prompting",
        content: "Chain-of-Thought prompting enables large language models to tackle complex arithmetic, commonsense, and symbolic reasoning tasks by generating intermediate reasoning steps.",
        sourceTitle: "Chain-of-Thought Prompting Elicits Reasoning",
        sourceUrl: "https://arxiv.org/abs/2201.11903",
        tags: ["Prompting", "Reasoning"],
        createdAt: "Dec 1, 2025"
    }
]

export default function KnowledgeBaseDetailPage({ params }: { params: { id: string } }) {
    // In a real app we'd fetch KB_DATA based on params.id
    const [searchQuery, setSearchQuery] = useState("")

    // Filter cards by search
    const filteredCards = MOCK_CARDS.filter(card =>
        card.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        card.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
        card.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
    )

    return (
        <div className="h-full flex flex-col bg-transparent max-w-7xl mx-auto w-full">
            {/* Top Navigation Bar */}
            <div className="flex items-center justify-between px-8 py-6 border-b border-border/50 shrink-0 sticky top-0 bg-zinc-50/80 backdrop-blur-md z-10">
                <div className="flex items-center gap-4">
                    <Link href="/knowledge">
                        <Button variant="ghost" size="icon" className="rounded-full hover:bg-zinc-200/50 text-zinc-500 h-9 w-9 cursor-pointer">
                            <ArrowLeft className="h-4 w-4" />
                        </Button>
                    </Link>
                    <div className="flex items-center gap-3">
                        <div className={`h-8 w-8 rounded-lg ${KB_DATA.bg} flex items-center justify-center border ${KB_DATA.border} flex-shrink-0 shadow-sm`}>
                            <KB_DATA.icon className={`h-4 w-4 ${KB_DATA.color}`} />
                        </div>
                        <h1 className="text-xl font-bold tracking-tight text-zinc-800 drop-shadow-sm line-clamp-1">{KB_DATA.title}</h1>
                    </div>
                </div>

                <div className="flex items-center gap-3 flex-1 max-w-md ml-8">
                    <div className="relative flex-1">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-400" />
                        <Input
                            type="text"
                            placeholder="Search in knowledge base..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="pl-9 h-10 bg-white border-zinc-200 rounded-full text-sm shadow-sm focus-visible:ring-1 focus-visible:ring-blue-500"
                        />
                    </div>
                    <Button variant="outline" size="icon" className="rounded-full h-10 w-10 border-zinc-200 bg-white shadow-sm hover:bg-zinc-50 text-zinc-600 shrink-0">
                        <Filter className="h-4 w-4" />
                    </Button>
                </div>
            </div>

            {/* Main Content Area */}
            <div className="flex-1 overflow-y-auto p-8 pb-20">

                {/* Meta Header */}
                <div className="mb-8 max-w-3xl">
                    <p className="text-zinc-600 leading-relaxed font-medium">
                        {KB_DATA.description}
                    </p>
                    <div className="flex flex-wrap items-center gap-4 mt-4 text-sm font-medium text-zinc-500">
                        <div className="flex items-center gap-1.5 bg-zinc-100 px-3 py-1.5 rounded-full border border-zinc-200/60 shadow-[0_1px_2px_0_rgba(0,0,0,0.02)]">
                            <Layers className="h-4 w-4 text-zinc-400" />
                            {KB_DATA.cardCount} Knowledge Cards
                        </div>
                        <div className="flex items-center gap-1.5">
                            <Clock className="h-4 w-4 text-zinc-400" />
                            Updated {KB_DATA.lastUpdated}
                        </div>
                    </div>
                </div>

                {/* Cards Masonry/Grid View */}
                <div className="columns-1 md:columns-2 lg:columns-3 gap-6 space-y-6">
                    {filteredCards.map((card) => (
                        <Card key={card.id} className="break-inside-avoid border-zinc-200 bg-white shadow-sm hover:shadow-md hover:border-zinc-300 transition-all rounded-3xl overflow-hidden group">
                            <CardHeader className="p-5 pb-3">
                                <div className="flex justify-between items-start mb-3">
                                    <div className="flex flex-wrap gap-2">
                                        {card.tags.map(tag => (
                                            <Badge key={tag} variant="secondary" className="bg-zinc-100 text-zinc-600 hover:bg-zinc-200 border-transparent rounded-sm px-2 text-[10px] font-semibold tracking-wide uppercase">
                                                {tag}
                                            </Badge>
                                        ))}
                                    </div>
                                    <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                        <Button variant="ghost" size="icon" className="h-8 w-8 rounded-full hover:bg-zinc-100 text-zinc-400 hover:text-blue-600">
                                            <Edit3 className="h-4 w-4" />
                                        </Button>
                                        <Button variant="ghost" size="icon" className="h-8 w-8 rounded-full hover:bg-red-50 hover:text-red-600 text-zinc-400">
                                            <Trash2 className="h-4 w-4" />
                                        </Button>
                                    </div>
                                </div>
                                <CardTitle className="text-[17px] font-bold text-zinc-800 leading-snug">
                                    {card.title}
                                </CardTitle>
                            </CardHeader>
                            <CardContent className="px-5 pb-4">
                                <p className="text-[13px] text-zinc-600 leading-relaxed">
                                    {card.content}
                                </p>
                            </CardContent>
                            <div className="px-5 py-3 mt-auto bg-zinc-50 border-t border-zinc-100 flex items-center justify-between group/footer">
                                <div className="flex items-center gap-2 overflow-hidden flex-1">
                                    <LinkIcon className="h-3 w-3 text-zinc-400 shrink-0" />
                                    <a href={card.sourceUrl} target="_blank" rel="noreferrer" className="text-[11px] font-medium text-zinc-500 truncate hover:text-blue-600 transition-colors">
                                        {card.sourceTitle}
                                    </a>
                                </div>
                                <span className="text-[10px] font-semibold text-zinc-400 uppercase tracking-widest shrink-0 ml-4 group-hover/footer:text-zinc-500 transition-colors">{card.createdAt}</span>
                            </div>
                        </Card>
                    ))}

                    {filteredCards.length === 0 && (
                        <div className="col-span-full py-20 flex flex-col items-center justify-center text-center">
                            <MessageSquareText className="h-12 w-12 text-zinc-300 mb-4" />
                            <h3 className="text-lg font-semibold text-zinc-700">No cards found</h3>
                            <p className="text-sm text-zinc-500 mt-1">Try adjusting your search terms or filters.</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}
