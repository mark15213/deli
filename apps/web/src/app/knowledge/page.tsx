"use client"

import { useState } from "react"
import { FolderDot, Settings, Zap, Clock, Plus, Database, ChevronRight, Layers, FileText, ArrowRight } from "lucide-react"
import Link from "next/link"

import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"

// Mock Knowledge Bases
const MOCK_KBS = [
    {
        id: "kb-1",
        title: "AI Architecture",
        description: "Core concepts, patterns, and papers regarding LLMs and agent architectures.",
        cardCount: 142,
        lastUpdated: "2 hours ago",
        subscribed: true,
        icon: Database,
        color: "text-blue-500",
        bg: "bg-blue-50",
        border: "border-blue-100"
    },
    {
        id: "kb-2",
        title: "Product Management",
        description: "Mental models, frameworks, and user research methodologies.",
        cardCount: 56,
        lastUpdated: "Yesterday",
        subscribed: true,
        icon: Layers,
        color: "text-emerald-500",
        bg: "bg-emerald-50",
        border: "border-emerald-100"
    },
    {
        id: "kb-3",
        title: "Personal Log",
        description: "Daily reflections and random unstructured thoughts.",
        cardCount: 12,
        lastUpdated: "3 days ago",
        subscribed: false,
        icon: FileText,
        color: "text-amber-500",
        bg: "bg-amber-50",
        border: "border-amber-100"
    }
]

export default function KnowledgeLibraryPage() {
    const [kbs, setKbs] = useState(MOCK_KBS)

    const toggleSubscription = (id: string, e: React.MouseEvent) => {
        e.preventDefault()
        e.stopPropagation()
        setKbs(kbs.map(kb =>
            kb.id === id ? { ...kb, subscribed: !kb.subscribed } : kb
        ))
    }

    return (
        <div className="h-full flex flex-col p-8 bg-transparent max-w-7xl mx-auto w-full">
            <div className="flex items-center justify-between mb-8 pb-6 border-b border-border/50">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight text-zinc-900 drop-shadow-sm flex items-center gap-3">
                        Knowledge Library
                    </h1>
                    <p className="text-zinc-500 mt-2 text-sm font-medium">Manage your structured knowledge bases for Gulp generation.</p>
                </div>
                <Button className="gap-2 rounded-full px-5 bg-zinc-900 text-white hover:bg-zinc-800 shadow-sm cursor-pointer">
                    <Plus className="h-4 w-4" />
                    New Base
                </Button>
            </div>

            <div className="flex-1 overflow-y-auto pb-20 pr-4">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 auto-rows-max">
                    {kbs.map((kb) => (
                        <Card
                            key={kb.id}
                            className="flex flex-col border-zinc-200 bg-white shadow-sm hover:shadow-md hover:border-zinc-300 transition-all group rounded-2xl overflow-hidden cursor-pointer"
                        >
                            <Link href={`/knowledge/${kb.id}`} className="flex flex-col h-full focus:outline-none">
                                <CardHeader className="pb-3 relative pt-5 px-5">
                                    <div className="absolute top-5 right-5 h-7">
                                        <kb.icon className={`h-4 w-4 text-zinc-300 group-hover:${kb.color} transition-colors`} />
                                    </div>
                                    <div className="pr-8">
                                        <CardTitle className="line-clamp-2 leading-snug group-hover:text-blue-600 transition-colors text-[17px] font-bold text-zinc-800 tracking-tight">
                                            {kb.title}
                                        </CardTitle>
                                        <CardDescription className="line-clamp-2 mt-1.5 font-medium text-[13px] text-zinc-500 leading-relaxed">
                                            {kb.description}
                                        </CardDescription>
                                    </div>
                                </CardHeader>

                                <CardContent className="px-5 pb-4 mt-auto">
                                    <div className="flex items-center gap-2 mb-3">
                                        {kb.subscribed ? (
                                            <Badge variant="default" className="bg-zinc-900 text-white hover:bg-zinc-800 shadow-none px-2 py-0 h-5 text-[10px] tracking-wide uppercase font-bold">
                                                <Zap className="h-3 w-3 mr-1 fill-white" /> Subscribed
                                            </Badge>
                                        ) : (
                                            <Badge variant="outline" className="text-zinc-500 border-zinc-200 bg-zinc-50 px-2 py-0 h-5 text-[10px] tracking-wide uppercase font-bold">
                                                Ignored
                                            </Badge>
                                        )}
                                    </div>
                                    <div className="flex items-center gap-4 text-xs font-medium text-zinc-500">
                                        <div className="flex items-center gap-1.5">
                                            <FolderDot className="h-3.5 w-3.5" />
                                            {kb.cardCount} cards
                                        </div>
                                        <div className="flex items-center gap-1.5">
                                            <Clock className="h-3.5 w-3.5" />
                                            {kb.lastUpdated}
                                        </div>
                                    </div>
                                </CardContent>

                                <CardFooter className="p-0 border-t border-zinc-100 bg-zinc-50/50 rounded-b-2xl mt-auto">
                                    <div className="w-full flex items-center justify-between px-5 py-3">
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            onClick={(e) => toggleSubscription(kb.id, e)}
                                            className={`rounded-full text-[11px] font-bold h-7 px-3.5 transition-colors z-10 border shadow-sm uppercase tracking-wider
                                                ${kb.subscribed
                                                    ? 'bg-white text-zinc-600 border-zinc-200 hover:bg-zinc-50 hover:text-red-500 hover:border-red-100'
                                                    : 'bg-white text-blue-600 border-blue-200 hover:bg-blue-50'}`}
                                        >
                                            {kb.subscribed ? "Unsubscribe" : "Subscribe"}
                                        </Button>
                                        <div className="flex items-center gap-1 text-xs font-bold text-blue-600 opacity-0 group-hover:opacity-100 transition-opacity">
                                            Open <ArrowRight className="h-3.5 w-3.5" />
                                        </div>
                                    </div>
                                </CardFooter>
                            </Link>
                        </Card>
                    ))}
                </div>
            </div>
        </div>
    )
}
