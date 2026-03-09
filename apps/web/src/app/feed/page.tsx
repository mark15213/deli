"use client"

import { useState } from "react"
import { FileText, Rss, ArrowRight, Clock, Link as LinkIcon, Sparkles } from "lucide-react"
import { AddSourceDialog } from "@/components/AddSourceDialog"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Workspace } from "@/components/Workspace"
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"
import { SubscriptionSettingsDialog } from "@/components/SubscriptionSettingsDialog"
import { Button } from "@/components/ui/button"

// Mock Data
const MOCK_SNAPSHOTS = [
    {
        id: "1",
        title: "Attention Is All You Need",
        url: "https://arxiv.org/abs/1706.03762",
        addedAt: "2 hours ago",
        status: "processed",
        summary: "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer..."
    },
    {
        id: "3",
        title: "Understanding React Server Components",
        url: "https://vercel.com/blog/understanding-react-server-components",
        addedAt: "2 days ago",
        status: "processed",
        summary: "React Server Components allow you to render components on the server, reducing the amount of JavaScript sent to the client and improving performance."
    }
]

const MOCK_SUBSCRIPTIONS = [
    {
        id: "sub-1",
        title: "HuggingFace Daily Papers",
        url: "https://huggingface.co/papers",
        frequency: "Daily",
        unreadCount: 3,
        snapshots: [
            { id: "s-101", title: "Language Models are Few-Shot Learners", url: "https://arxiv.org/abs/2005.14165", addedAt: "1 day ago" },
            { id: "s-102", title: "BERT: Pre-training of Deep Bidirectional Transformers", url: "https://arxiv.org/abs/1810.04805", addedAt: "2 days ago" },
            { id: "s-103", title: "LoRA: Low-Rank Adaptation of Large Language Models", url: "https://arxiv.org/abs/2106.09685", addedAt: "3 days ago" },
        ]
    },
    {
        id: "sub-2",
        title: "Vercel Product Updates",
        url: "https://vercel.com/changelog",
        frequency: "Weekly",
        unreadCount: 1,
        snapshots: [
            { id: "s-201", title: "Next.js 15 Release Candidate", url: "https://nextjs.org/blog/next-15-rc", addedAt: "3 days ago" }
        ]
    }
]

export default function FeedPage() {
    const [activeWorkspaceSource, setActiveWorkspaceSource] = useState<any>(null)

    if (activeWorkspaceSource) {
        return (
            <Workspace
                source={activeWorkspaceSource}
                onClose={() => setActiveWorkspaceSource(null)}
            />
        )
    }

    return (
        <div className="h-full flex flex-col p-8 bg-transparent max-w-7xl mx-auto w-full">
            <div className="flex items-center justify-between mb-8 pb-6 border-b border-border/50">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight text-zinc-900 drop-shadow-sm">Feed</h1>
                    <p className="text-zinc-500 mt-2 text-sm font-medium">Manage your info sources and subscriptions.</p>
                </div>
                <AddSourceDialog />
            </div>

            <div className="flex-1 overflow-y-auto pb-20 pr-4">

                {/* Independent Snapshots Section */}
                <div className="mb-12">
                    <div className="flex items-center gap-2 mb-6">
                        <FileText className="h-5 w-5 text-zinc-400" />
                        <h2 className="text-lg font-semibold text-zinc-800">Recent Snapshots</h2>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 auto-rows-max">
                        {MOCK_SNAPSHOTS.map((source) => (
                            <Card
                                key={source.id}
                                className="flex flex-col border-zinc-200 bg-white shadow-sm hover:shadow-md hover:border-zinc-300 transition-all cursor-pointer group rounded-2xl"
                                onClick={() => setActiveWorkspaceSource(source)}
                            >
                                <CardHeader className="pb-3 relative">
                                    <div className="absolute top-4 right-4">
                                        <FileText className="h-4 w-4 text-zinc-400 group-hover:text-zinc-600 transition-colors" />
                                    </div>
                                    <CardTitle className="line-clamp-2 leading-snug group-hover:text-blue-600 transition-colors text-[17px] pr-6">
                                        {source.title}
                                    </CardTitle>
                                    <CardDescription className="line-clamp-1 mt-1 font-medium text-xs text-zinc-400">
                                        {source.url}
                                    </CardDescription>
                                </CardHeader>
                                <CardFooter className="pt-3 border-t border-zinc-50 text-xs text-zinc-500 flex justify-between items-center bg-zinc-50/50 rounded-b-2xl mt-auto">
                                    <div className="flex items-center gap-1.5 font-medium">
                                        <Clock className="h-3.5 w-3.5" />
                                        {source.addedAt}
                                    </div>
                                    <div className="flex items-center gap-1.5 text-blue-600 opacity-0 group-hover:opacity-100 transition-opacity font-semibold">
                                        Open <ArrowRight className="h-3.5 w-3.5" />
                                    </div>
                                </CardFooter>
                            </Card>
                        ))}
                    </div>
                </div>

                {/* Subscriptions Accordion Section */}
                <div>
                    <div className="flex items-center gap-2 mb-6">
                        <Rss className="h-5 w-5 text-zinc-400" />
                        <h2 className="text-lg font-semibold text-zinc-800">Subscriptions</h2>
                    </div>

                    <div className="bg-white rounded-[2rem] shadow-sm border border-zinc-200 overflow-hidden">
                        <Accordion type="multiple" className="w-full">
                            {MOCK_SUBSCRIPTIONS.map((sub) => (
                                <AccordionItem value={sub.id} key={sub.id} className="last:border-0 group data-[state=open]:bg-zinc-50/30 transition-colors relative">
                                    <div className="flex items-center w-full group/header relative px-6 z-10">
                                        <AccordionTrigger className="hover:no-underline font-semibold text-base py-5 gap-4 flex-[1_1_auto] border-b-0">
                                            <div className="flex items-center justify-between w-full h-full pr-10">
                                                <div className="flex items-center gap-4">
                                                    <div className="h-10 w-10 rounded-full bg-orange-50 flex items-center justify-center border border-orange-100 flex-shrink-0">
                                                        <Rss className="h-5 w-5 text-orange-500" />
                                                    </div>
                                                    <div className="flex flex-col gap-0.5 items-start">
                                                        <span className="text-zinc-900 group-data-[state=open]:text-blue-600 transition-colors block leading-tight">{sub.title}</span>
                                                        <span className="text-xs font-normal text-zinc-500 line-clamp-1">{sub.url}</span>
                                                    </div>
                                                </div>
                                                <div className="flex items-center gap-3">
                                                </div>
                                            </div>
                                        </AccordionTrigger>
                                        <div className="flex items-center justify-center shrink-0 w-8 h-full absolute right-[4.5rem]" onClick={(e) => e.stopPropagation()}>
                                            <SubscriptionSettingsDialog subscription={sub} />
                                        </div>
                                    </div>

                                    <AccordionContent className="pb-6 pt-2 pr-12 pl-[5.5rem] relative z-0">
                                        <div className="flex flex-col gap-3">
                                            {sub.snapshots.map((snap) => (
                                                <div
                                                    key={snap.id}
                                                    onClick={() => setActiveWorkspaceSource(snap)}
                                                    className="flex items-center justify-between p-3.5 rounded-xl border border-zinc-100 bg-white hover:border-blue-200 hover:bg-blue-50/50 shadow-[0_1px_3px_0_rgba(0,0,0,0.02)] hover:shadow-sm cursor-pointer transition-all group/item"
                                                >
                                                    <div className="flex items-center gap-3 overflow-hidden">
                                                        <FileText className="h-4 w-4 text-zinc-300 group-hover/item:text-blue-400 shrink-0 transition-colors" />
                                                        <div className="flex flex-col gap-1 overflow-hidden">
                                                            <span className="text-sm font-medium text-zinc-700 group-hover/item:text-zinc-900 truncate transition-colors leading-none">{snap.title}</span>
                                                            <span className="text-xs text-zinc-400 truncate leading-none">{snap.url}</span>
                                                        </div>
                                                    </div>
                                                    <div className="flex items-center gap-4 shrink-0 ml-4">
                                                        <span className="text-xs font-medium text-zinc-400 flex items-center gap-1.5"><Clock className="h-3.5 w-3.5" /> {snap.addedAt}</span>
                                                        <Button variant="ghost" size="sm" className="h-7 rounded-full text-xs font-medium opacity-0 group-hover/item:opacity-100 transition-opacity bg-white border border-zinc-200 hover:bg-zinc-100 hover:text-blue-600 px-3 flex items-center gap-1">
                                                            Open
                                                        </Button>
                                                    </div>
                                                </div>
                                            ))}

                                            <div className="flex justify-center pt-3">
                                                <Button variant="ghost" size="sm" className="text-xs font-medium text-zinc-500 rounded-full h-8 hover:bg-zinc-100 transition-colors px-4">
                                                    View all snapshots
                                                </Button>
                                            </div>
                                        </div>
                                    </AccordionContent>
                                </AccordionItem>
                            ))}
                        </Accordion>
                    </div>

                </div>
            </div>
        </div>
    )
}
