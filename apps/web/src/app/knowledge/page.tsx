"use client"

import { useState, useEffect } from "react"
import { FolderDot, Zap, Clock, Plus, Database, ArrowRight, Loader2 } from "lucide-react"
import Link from "next/link"
import { useRouter } from "next/navigation"

import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { useAuth } from "@/contexts/AuthContext"
import { api } from "@/lib/api"

interface KnowledgeBase {
    id: string
    title: string
    description: string | null
    icon: string
    color: string
    is_subscribed: boolean
    card_count: number
    created_at: string
    updated_at: string
}

export default function KnowledgeLibraryPage() {
    const [kbs, setKbs] = useState<KnowledgeBase[]>([])
    const [loading, setLoading] = useState(true)
    const [dialogOpen, setDialogOpen] = useState(false)
    const [formData, setFormData] = useState({
        title: "",
        description: "",
        icon: "Database",
        color: "blue"
    })
    const [submitting, setSubmitting] = useState(false)
    const { isAuthenticated } = useAuth()
    const router = useRouter()

    useEffect(() => {
        if (!isAuthenticated) {
            router.push('/login')
            return
        }
        loadKnowledgeBases()
    }, [isAuthenticated, router])

    const loadKnowledgeBases = async () => {
        try {
            setLoading(true)
            const data = await api.getKnowledgeBases()
            setKbs(data as KnowledgeBase[])
        } catch (error: any) {
            console.error('Failed to load knowledge bases:', error)
        } finally {
            setLoading(false)
        }
    }

    const handleCreate = async (e: React.FormEvent) => {
        e.preventDefault()
        setSubmitting(true)

        try {
            await api.createKnowledgeBase(formData)
            setDialogOpen(false)
            setFormData({ title: "", description: "", icon: "Database", color: "blue" })
            await loadKnowledgeBases()
        } catch (error: any) {
            alert(error.message || '创建失败')
        } finally {
            setSubmitting(false)
        }
    }

    const toggleSubscription = async (id: string, currentStatus: boolean, e: React.MouseEvent) => {
        e.preventDefault()
        e.stopPropagation()

        try {
            await api.updateKnowledgeBase(id, { is_subscribed: !currentStatus })
            setKbs(kbs.map(kb =>
                kb.id === id ? { ...kb, is_subscribed: !currentStatus } : kb
            ))
        } catch (error: any) {
            alert(error.message || '更新失败')
        }
    }

    const getColorClasses = (color: string) => {
        const colorMap: Record<string, { text: string; bg: string; border: string }> = {
            blue: { text: "text-blue-500", bg: "bg-blue-50", border: "border-blue-100" },
            emerald: { text: "text-emerald-500", bg: "bg-emerald-50", border: "border-emerald-100" },
            amber: { text: "text-amber-500", bg: "bg-amber-50", border: "border-amber-100" },
            red: { text: "text-red-500", bg: "bg-red-50", border: "border-red-100" },
            purple: { text: "text-purple-500", bg: "bg-purple-50", border: "border-purple-100" },
        }
        return colorMap[color] || colorMap.blue
    }

    const formatDate = (dateString: string) => {
        const date = new Date(dateString)
        const now = new Date()
        const diffMs = now.getTime() - date.getTime()
        const diffMins = Math.floor(diffMs / 60000)
        const diffHours = Math.floor(diffMs / 3600000)
        const diffDays = Math.floor(diffMs / 86400000)

        if (diffMins < 60) return `${diffMins} minutes ago`
        if (diffHours < 24) return `${diffHours} hours ago`
        if (diffDays === 1) return 'Yesterday'
        if (diffDays < 7) return `${diffDays} days ago`
        return date.toLocaleDateString()
    }

    if (loading) {
        return (
            <div className="h-full flex items-center justify-center">
                <Loader2 className="h-8 w-8 animate-spin text-zinc-400" />
            </div>
        )
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

                <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
                    <DialogTrigger asChild>
                        <Button className="gap-2 rounded-full px-5 bg-zinc-900 text-white hover:bg-zinc-800 shadow-sm cursor-pointer">
                            <Plus className="h-4 w-4" />
                            New Base
                        </Button>
                    </DialogTrigger>
                    <DialogContent>
                        <DialogHeader>
                            <DialogTitle>Create Knowledge Base</DialogTitle>
                            <DialogDescription>
                                Create a new knowledge base to organize your learning cards.
                            </DialogDescription>
                        </DialogHeader>
                        <form onSubmit={handleCreate} className="space-y-4">
                            <div>
                                <label className="text-sm font-medium">Title</label>
                                <Input
                                    value={formData.title}
                                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                                    placeholder="e.g., AI Architecture"
                                    required
                                    className="mt-1"
                                />
                            </div>
                            <div>
                                <label className="text-sm font-medium">Description</label>
                                <Textarea
                                    value={formData.description}
                                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                    placeholder="Brief description of this knowledge base"
                                    className="mt-1"
                                    rows={3}
                                />
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="text-sm font-medium">Color</label>
                                    <select
                                        value={formData.color}
                                        onChange={(e) => setFormData({ ...formData, color: e.target.value })}
                                        className="mt-1 w-full rounded-md border border-zinc-200 px-3 py-2 text-sm"
                                    >
                                        <option value="blue">Blue</option>
                                        <option value="emerald">Emerald</option>
                                        <option value="amber">Amber</option>
                                        <option value="red">Red</option>
                                        <option value="purple">Purple</option>
                                    </select>
                                </div>
                            </div>
                            <div className="flex justify-end gap-2 pt-4">
                                <Button type="button" variant="outline" onClick={() => setDialogOpen(false)}>
                                    Cancel
                                </Button>
                                <Button type="submit" disabled={submitting}>
                                    {submitting ? 'Creating...' : 'Create'}
                                </Button>
                            </div>
                        </form>
                    </DialogContent>
                </Dialog>
            </div>

            <div className="flex-1 overflow-y-auto pb-20 pr-4">
                {kbs.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-full text-center">
                        <Database className="h-16 w-16 text-zinc-300 mb-4" />
                        <h3 className="text-lg font-semibold text-zinc-700 mb-2">No Knowledge Bases Yet</h3>
                        <p className="text-sm text-zinc-500 mb-6">Create your first knowledge base to start organizing your learning.</p>
                        <Button onClick={() => setDialogOpen(true)} className="gap-2">
                            <Plus className="h-4 w-4" />
                            Create Knowledge Base
                        </Button>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 auto-rows-max">
                        {kbs.map((kb) => (
                            <Card
                                key={kb.id}
                                className="flex flex-col border-zinc-200 bg-white shadow-sm hover:shadow-md hover:border-zinc-300 transition-all group rounded-2xl overflow-hidden cursor-pointer"
                            >
                                <Link href={`/knowledge/${kb.id}`} className="flex flex-col h-full focus:outline-none">
                                    <CardHeader className="pb-3 relative pt-5 px-5">
                                        <div className="absolute top-5 right-5 h-7">
                                            <Database className={`h-4 w-4 text-zinc-300 group-hover:${getColorClasses(kb.color).text} transition-colors`} />
                                        </div>
                                        <div className="pr-8">
                                            <CardTitle className="line-clamp-2 leading-snug group-hover:text-blue-600 transition-colors text-[17px] font-bold text-zinc-800 tracking-tight">
                                                {kb.title}
                                            </CardTitle>
                                            <CardDescription className="line-clamp-2 mt-1.5 font-medium text-[13px] text-zinc-500 leading-relaxed">
                                                {kb.description || 'No description'}
                                            </CardDescription>
                                        </div>
                                    </CardHeader>

                                    <CardContent className="px-5 pb-4 mt-auto">
                                        <div className="flex items-center gap-2 mb-3">
                                            {kb.is_subscribed ? (
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
                                                {kb.card_count} cards
                                            </div>
                                            <div className="flex items-center gap-1.5">
                                                <Clock className="h-3.5 w-3.5" />
                                                {formatDate(kb.updated_at)}
                                            </div>
                                        </div>
                                    </CardContent>

                                    <CardFooter className="p-0 border-t border-zinc-100 bg-zinc-50/50 rounded-b-2xl mt-auto">
                                        <div className="w-full flex items-center justify-between px-5 py-3">
                                            <Button
                                                variant="ghost"
                                                size="sm"
                                                onClick={(e) => toggleSubscription(kb.id, kb.is_subscribed, e)}
                                                className={`rounded-full text-[11px] font-bold h-7 px-3.5 transition-colors z-10 border shadow-sm uppercase tracking-wider
                                                    ${kb.is_subscribed
                                                        ? 'bg-white text-zinc-600 border-zinc-200 hover:bg-zinc-50 hover:text-red-500 hover:border-red-100'
                                                        : 'bg-white text-blue-600 border-blue-200 hover:bg-blue-50'}`}
                                            >
                                                {kb.is_subscribed ? "Unsubscribe" : "Subscribe"}
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
                )}
            </div>
        </div>
    )
}
