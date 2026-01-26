"use client"

import {
    ResizableHandle,
    ResizablePanel,
    ResizablePanelGroup,
} from "@/components/ui/resizable"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Pencil, ThumbsDown } from "lucide-react"

export function SplitView() {
    return (
        <div className="h-full w-full">
            <ResizablePanelGroup direction="horizontal">
                {/* Source Content */}
                <ResizablePanel defaultSize={50} minSize={30}>
                    <div className="h-full flex flex-col bg-background">
                        <div className="h-14 border-b flex items-center px-4 font-semibold text-sm bg-muted/10">
                            Original Source
                        </div>
                        <ScrollArea className="flex-1 p-8">
                            <div className="max-w-2xl mx-auto space-y-6">
                                <div className="flex gap-4">
                                    <div className="h-10 w-10 rounded-full bg-blue-500 shrink-0" />
                                    <div>
                                        <div className="font-bold">Andrej Karpathy</div>
                                        <div className="text-muted-foreground text-sm">@karpathy</div>
                                    </div>
                                </div>
                                <div className="text-lg leading-relaxed space-y-4">
                                    <p>
                                        Tokenization is a fundamental step in LLMs but also a major source of headaches.
                                        It splits text into chunks, but how it does so can affect reasoning.
                                    </p>
                                    <p>
                                        For example, simple arithmetic on tokenized numbers is harder for models because
                                        digits are often grouped in arbitrary ways (e.g. "1234" might be "12" and "34").
                                    </p>
                                    <div className="rounded-lg border bg-muted/50 p-4 font-mono text-sm">
                                        [12, 34] vs [1, 2, 3, 4]
                                    </div>
                                    <p>
                                        We need better inductive biases or just raw character-level processing,
                                        although that comes with context length costs.
                                    </p>
                                </div>
                            </div>
                        </ScrollArea>
                    </div>
                </ResizablePanel>

                <ResizableHandle withHandle />

                {/* AI Output */}
                <ResizablePanel defaultSize={50} minSize={30}>
                    <div className="h-full flex flex-col bg-muted/30">
                        <div className="h-14 border-b flex items-center justify-between px-4 font-semibold text-sm bg-background">
                            <span>AI Generated Insights</span>
                            <div className="flex gap-2">
                                <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                                    <Pencil className="h-4 w-4" />
                                </Button>
                                <Button variant="ghost" size="sm" className="h-8 w-8 p-0 text-destructive">
                                    <ThumbsDown className="h-4 w-4" />
                                </Button>
                            </div>
                        </div>
                        <ScrollArea className="flex-1 p-6">
                            <div className="space-y-6">
                                <div className="space-y-2">
                                    <h4 className="text-xs uppercase tracking-wider text-muted-foreground font-bold">Summary</h4>
                                    <Card>
                                        <CardContent className="p-4 text-sm leading-relaxed">
                                            Tokenization methods significantly impact LLM reasoning capabilities, particularly in arithmetic tasks where arbitrary digit grouping creates difficulties. Character-level processing offers a solution but increases computational cost due to longer context requirements.
                                        </CardContent>
                                    </Card>
                                </div>

                                <div className="space-y-2">
                                    <h4 className="text-xs uppercase tracking-wider text-muted-foreground font-bold">Generated Flashcards</h4>
                                    <div className="grid gap-4">
                                        <Card>
                                            <CardHeader className="p-4 pb-2">
                                                <CardTitle className="text-sm font-medium">Q: Why does tokenization hinder arithmetic in LLMs?</CardTitle>
                                            </CardHeader>
                                            <CardContent className="p-4 pt-0 text-sm text-muted-foreground">
                                                A: Because it often groups digits arbitrarily (e.g., 1234 {'->'} 12, 34), making place-value reasoning difficult for the model.
                                            </CardContent>
                                        </Card>
                                        <Card>
                                            <CardHeader className="p-4 pb-2">
                                                <CardTitle className="text-sm font-medium">Q: What is the trade-off of character-level processing?</CardTitle>
                                            </CardHeader>
                                            <CardContent className="p-4 pt-0 text-sm text-muted-foreground">
                                                A: Better reasoning per token/character, but much longer sequence lengths, increasing computational cost.
                                            </CardContent>
                                        </Card>
                                    </div>
                                </div>
                            </div>
                        </ScrollArea>
                    </div>
                </ResizablePanel>
            </ResizablePanelGroup>
        </div>
    )
}
