"use client";

import * as React from "react";
import { Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogFooter,
} from "@/components/ui/modal";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { useUIStore } from "@/store/ui-store";

export function QuickAddModal() {
    const { slideOverOpen, closeSlideOver, slideOverContent } = useUIStore();
    const isOpen = slideOverOpen && slideOverContent === "quick-add";

    // Using SlideOver store but rendering as Dialog for Quick Add as per design preference? 
    // Wait, design says "点击弹出 Markdown 模态框" (Click to pop up Markdown Modal).
    // So I should separate state or reuse store mechanism. 
    // Let's use the store's mechanism but map "quick-add" to this Dialog.

    if (!isOpen) return null;

    return (
        <Dialog open={isOpen} onOpenChange={(open) => !open && closeSlideOver()}>
            <DialogContent className="sm:max-w-[600px]">
                <DialogHeader>
                    <DialogTitle>Quick Add Source</DialogTitle>
                </DialogHeader>

                <Tabs defaultValue="url" className="w-full">
                    <TabsList className="grid w-full grid-cols-2">
                        <TabsTrigger value="url">URL Import</TabsTrigger>
                        <TabsTrigger value="manual">Manual Entry</TabsTrigger>
                    </TabsList>

                    <TabsContent value="url" className="space-y-4 py-4">
                        <div className="space-y-2">
                            <label className="text-sm font-medium">Paste URL</label>
                            <div className="flex gap-2">
                                <Input
                                    placeholder="https://twitter.com/username or https://github.com/..."
                                    className="flex-1"
                                />
                                <Button>Auto Detect</Button>
                            </div>
                            <p className="text-xs text-muted-foreground">
                                Supports Twitter profiles, GitHub repos, Substack RSS, Notion pages, and Arxiv papers.
                            </p>
                        </div>
                    </TabsContent>

                    <TabsContent value="manual" className="py-4">
                        <div className="space-y-2">
                            <label className="text-sm font-medium">Quick Note (Markdown)</label>
                            <textarea
                                className="flex min-h-[150px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                                placeholder="# Idea&#10;&#10;Jotted down something quick..."
                            />
                        </div>
                    </TabsContent>
                </Tabs>

                <DialogFooter>
                    <Button variant="outline" onClick={closeSlideOver}>Cancel</Button>
                    <Button onClick={closeSlideOver}>Add Source</Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
}

export function QuickAddButton() {
    const { openSlideOver } = useUIStore();

    return (
        <Button onClick={() => openSlideOver("quick-add")} className="gap-2">
            <Plus className="h-4 w-4" />
            Quick Add
        </Button>
    );
}
