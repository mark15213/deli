"use client"

import {
    Sheet,
    SheetContent,
    SheetDescription,
    SheetFooter,
    SheetHeader,
    SheetTitle,
} from "@/components/ui/sheet"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { Switch } from "@/components/ui/switch"
import { SourceFormContainer } from "./forms/SourceFormContainer"
import { ConfigTab } from "./tabs/ConfigTab"
import { RulesTab } from "./tabs/RulesTab"
import { LogsTab } from "./tabs/LogsTab"
import { Power, Save, RefreshCw, Trash2 } from "lucide-react"
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

interface SourceDetailDrawerProps {
    isOpen: boolean
    onClose: () => void
    sourceId: string | null
}

export function SourceDetailDrawer({ isOpen, onClose, sourceId }: SourceDetailDrawerProps) {
    const [source, setSource] = React.useState<Source | null>(null);
    const [loading, setLoading] = React.useState(false);
    const [activeTab, setActiveTab] = React.useState("config");

    // Fetch Source Data
    React.useEffect(() => {
        if (isOpen && sourceId) {
            setLoading(true);
            // TODO: Use React Query or SWR
            fetch(`/api/sources/${sourceId}`)
                .then(res => res.json())
                .then(data => {
                    setSource(data);
                    if (data.type === 'ARXIV_PAPER') {
                        setActiveTab("analysis");
                    }
                })
                .catch(err => console.error(err))
                .finally(() => setLoading(false));
        } else {
            setSource(null);
        }
    }, [isOpen, sourceId]);

    const handleRunLens = async (lensKey: string) => {
        if (!source) return;
        try {
            const res = await fetch("/api/paper/run-lens", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    source_id: source.id,
                    lens_key: lensKey
                })
            });
            const artifact = await res.json();
            // Reload source to get updated rich_data
            fetch(`/api/sources/${source.id}`)
                .then(res => res.json())
                .then(data => setSource(data));
        } catch (e) {
            console.error("Failed to run lens", e);
        }
    };

    if (!source && !loading) return null;

    const paperData = source?.source_materials?.[0]?.rich_data;

    return (
        <Sheet open={isOpen} onOpenChange={onClose}>
            <SheetContent className="w-[400px] sm:w-[600px] sm:max-w-none flex flex-col h-full bg-background" side="right">

                {/* Header */}
                <div className="flex-none space-y-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <SheetTitle className="flex items-center gap-2 text-xl">
                                {source?.name || "Loading..."}
                                <span className={`flex h-2 w-2 rounded-full ring-4 ${source?.status === 'ACTIVE' ? 'bg-green-500 ring-green-500/20' : 'bg-gray-500 ring-gray-500/20'}`} />
                            </SheetTitle>
                            <SheetDescription className="mt-1">
                                {source?.type} • {source?.id}
                            </SheetDescription>
                        </div>
                    </div>
                </div>

                {/* Tabs */}
                <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col mt-6 overflow-hidden">
                    <TabsList>
                        <TabsTrigger value="config">Configuration</TabsTrigger>
                        {source?.type === 'ARXIV_PAPER' && <TabsTrigger value="analysis">Paper Analysis</TabsTrigger>}
                        <TabsTrigger value="logs">Logs</TabsTrigger>
                    </TabsList>

                    <div className="flex-1 overflow-y-auto mt-4 px-1">
                        <TabsContent value="config" className="h-full">
                            {source && (
                                <SourceFormContainer
                                    type={source.type}
                                    onSave={(data) => console.log("Saving:", data)}
                                // Pass initial data if supported by SourceFormContainer
                                />
                            )}
                        </TabsContent>

                        <TabsContent value="analysis" className="space-y-6">
                            {/* Summary Section */}
                            {paperData?.summary ? (
                                <div className="space-y-2">
                                    <h3 className="text-lg font-semibold flex items-center gap-2">
                                        <RefreshCw className="w-4 h-4" />
                                        TL;DR Summary
                                    </h3>
                                    <div className="p-4 bg-muted/30 rounded-lg text-sm leading-relaxed prose prose-sm dark:prose-invert max-w-none break-words">
                                        <ReactMarkdown
                                            remarkPlugins={[remarkGfm]}
                                            components={{
                                                a: ({ node, ...props }) => <a {...props} className="text-blue-500 hover:underline" target="_blank" rel="noopener noreferrer" />,
                                                p: ({ node, ...props }) => <p {...props} className="mb-2 last:mb-0" />,
                                                ul: ({ node, ...props }) => <ul {...props} className="list-disc pl-4 mb-2" />,
                                                ol: ({ node, ...props }) => <ol {...props} className="list-decimal pl-4 mb-2" />,
                                                li: ({ node, ...props }) => <li {...props} className="mb-1" />,
                                                strong: ({ node, ...props }) => <strong {...props} className="font-semibold text-foreground" />,
                                            }}
                                        >
                                            {paperData.summary}
                                        </ReactMarkdown>
                                    </div>
                                </div>
                            ) : (
                                <div className="text-muted-foreground p-4 text-center border rounded-lg border-dashed">
                                    No summary available yet. Check back later.
                                </div>
                            )}

                            {/* Suggestions Section */}
                            <div className="space-y-3">
                                <h3 className="text-lg font-semibold">Suggested Lenses</h3>
                                <div className="grid grid-cols-1 gap-3">
                                    {paperData?.suggestions?.map((lens: any) => (
                                        <div key={lens.key} className="border rounded-lg p-3 hover:bg-muted/50 transition-colors flex justify-between items-start">
                                            <div>
                                                <div className="font-medium text-sm">{lens.name}</div>
                                                <div className="text-xs text-muted-foreground mt-1">{lens.description}</div>
                                                <div className="text-xs text-blue-500 mt-1">{lens.reason}</div>

                                                {/* Show Result if available */}
                                                {paperData.lenses?.[lens.key] && (
                                                    <div className="mt-2 p-2 bg-background rounded border text-xs overflow-auto max-h-40">
                                                        <pre>{JSON.stringify(paperData.lenses[lens.key], null, 2)}</pre>
                                                    </div>
                                                )}
                                            </div>
                                            <Button
                                                size="sm"
                                                variant="outline"
                                                onClick={() => handleRunLens(lens.key)}
                                                disabled={!!paperData.lenses?.[lens.key]}
                                            >
                                                {paperData.lenses?.[lens.key] ? "Ran" : "Run"}
                                            </Button>
                                        </div>
                                    ))}
                                    {(!paperData?.suggestions || paperData.suggestions.length === 0) && (
                                        <div className="text-sm text-muted-foreground">Generating suggestions...</div>
                                    )}
                                </div>
                            </div>
                        </TabsContent>

                        <TabsContent value="logs">
                            <div className="text-sm text-muted-foreground">Logs not implemented.</div>
                        </TabsContent>
                    </div>
                </Tabs>

                {/* Footer */}
                <div className="flex-none pt-6 mt-2 border-t flex justify-between items-center bg-background">
                    <Button variant="ghost" className="text-destructive hover:text-destructive hover:bg-destructive/10 gap-2 h-9 px-3">
                        <Trash2 className="h-4 w-4" />
                        <span className="sr-only sm:not-sr-only">Delete</span>
                    </Button>
                    <div className="flex gap-3">
                        <Button variant="outline" className="gap-2">
                            <RefreshCw className="h-4 w-4" /> Sync Now
                        </Button>
                        <Button className="gap-2">
                            <Save className="h-4 w-4" /> Save Changes
                        </Button>
                    </div>
                </div>

            </SheetContent>
        </Sheet>
    )
}
import { Source } from "@/types/source";
import React from "react";
