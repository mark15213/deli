"use client";

import * as React from "react";
import { Trash2, Save, RefreshCw, AlertCircle, Clock } from "lucide-react";
import { Button } from "@/components/ui/button";
import { SlideOver } from "@/components/ui/slide-over";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Switch } from "@/components/ui/switch";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { useUIStore } from "@/store/ui-store";

export function SourceDetailDrawer() {
    const { slideOverOpen, closeSlideOver, slideOverContent, selectedSourceId } = useUIStore();
    const isOpen = slideOverOpen && slideOverContent === "source-detail";

    // In a real app, we would fetch source details by ID here
    const sourceName = "Naval Ravikant";

    if (!isOpen) return null;

    return (
        <SlideOver
            open={isOpen}
            onClose={closeSlideOver}
            title={sourceName}
            footer={
                <div className="flex items-center justify-between w-full">
                    <Button variant="destructive" size="sm" className="gap-2">
                        <Trash2 className="h-4 w-4" />
                        Delete
                    </Button>
                    <div className="flex items-center gap-2">
                        <Button variant="outline" size="sm" className="gap-2">
                            <RefreshCw className="h-4 w-4" />
                            Sync Now
                        </Button>
                        <Button size="sm" className="gap-2">
                            <Save className="h-4 w-4" />
                            Save
                        </Button>
                    </div>
                </div>
            }
        >
            <div className="space-y-6">
                {/* Header Status */}
                <div className="flex items-center justify-between rounded-lg border bg-muted/40 p-4">
                    <div className="space-y-1">
                        <div className="flex items-center gap-2">
                            <span className="font-medium">Status</span>
                            <Badge variant="default" className="bg-blue-500 hover:bg-blue-600">Syncing</Badge>
                        </div>
                        <p className="text-xs text-muted-foreground">Last synced: Just now</p>
                    </div>
                    <Button variant="ghost" size="icon">
                        <RefreshCw className="h-4 w-4 animate-spin text-muted-foreground" />
                    </Button>
                </div>

                <Tabs defaultValue="config" className="w-full">
                    <TabsList className="w-full">
                        <TabsTrigger value="config" className="flex-1">Config</TabsTrigger>
                        <TabsTrigger value="rules" className="flex-1">Rules</TabsTrigger>
                        <TabsTrigger value="logs" className="flex-1">Logs</TabsTrigger>
                    </TabsList>

                    <TabsContent value="config" className="space-y-4 py-4">
                        <div className="space-y-4">
                            <div className="space-y-2">
                                <label className="text-sm font-medium">Sync Frequency</label>
                                <select className="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50">
                                    <option value="realtime">Real-time (Stream)</option>
                                    <option value="hourly">Hourly</option>
                                    <option value="daily">Daily at 08:00</option>
                                </select>
                            </div>

                            <div className="flex items-center justify-between space-x-2 rounded-lg border p-4">
                                <div className="space-y-0.5">
                                    <label className="text-sm font-medium peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                                        Auto-tagging
                                    </label>
                                    <p className="text-xs text-muted-foreground">
                                        Automatically generate tags using AI
                                    </p>
                                </div>
                                <Switch />
                            </div>

                            <div className="flex items-center justify-between space-x-2 rounded-lg border p-4">
                                <div className="space-y-0.5">
                                    <label className="text-sm font-medium peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                                        Notifications
                                    </label>
                                    <p className="text-xs text-muted-foreground">
                                        Alert when new items are found
                                    </p>
                                </div>
                                <Switch defaultChecked />
                            </div>
                        </div>
                    </TabsContent>

                    <TabsContent value="rules" className="space-y-4 py-4">
                        <div className="space-y-4">
                            <div className="space-y-2">
                                <label className="text-sm font-medium">Content Types</label>
                                <div className="grid grid-cols-2 gap-2">
                                    <label className="flex items-center gap-2 rounded-md border p-3 hover:bg-accent cursor-pointer">
                                        <input type="checkbox" className="rounded border-gray-300" defaultChecked />
                                        <span className="text-sm">Threads</span>
                                    </label>
                                    <label className="flex items-center gap-2 rounded-md border p-3 hover:bg-accent cursor-pointer">
                                        <input type="checkbox" className="rounded border-gray-300" defaultChecked />
                                        <span className="text-sm">Bookmarks</span>
                                    </label>
                                    <label className="flex items-center gap-2 rounded-md border p-3 hover:bg-accent cursor-pointer">
                                        <input type="checkbox" className="rounded border-gray-300" />
                                        <span className="text-sm">Replies</span>
                                    </label>
                                    <label className="flex items-center gap-2 rounded-md border p-3 hover:bg-accent cursor-pointer">
                                        <input type="checkbox" className="rounded border-gray-300" />
                                        <span className="text-sm">Quotes</span>
                                    </label>
                                </div>
                            </div>

                            <div className="space-y-2">
                                <label className="text-sm font-medium">Keyword Filtering</label>
                                <Input placeholder="e.g. AI, Crypto, Biology (comma separated)" />
                                <p className="text-xs text-muted-foreground">Only import items matching these keywords. Leave empty for all.</p>
                            </div>
                        </div>
                    </TabsContent>

                    <TabsContent value="logs" className="py-4">
                        <div className="space-y-4">
                            <div className="space-y-4 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-slate-300 before:to-transparent">
                                {/* Log Item 1 */}
                                <div className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full border bg-background shadow md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2">
                                        <RefreshCw className="h-4 w-4 text-blue-500 animate-spin" />
                                    </div>
                                    <div className="w-[calc(100%-4rem)] rounded-lg border bg-card p-4 shadow-sm md:w-[calc(50%-2.5rem)]">
                                        <div className="mb-1 flex items-center justify-between">
                                            <div className="font-bold text-sm">Syncing...</div>
                                            <time className="text-xs text-muted-foreground">Now</time>
                                        </div>
                                        <p className="text-xs text-muted-foreground">
                                            Fetching latest 20 tweets...
                                        </p>
                                    </div>
                                </div>

                                {/* Log Item 2 */}
                                <div className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group">
                                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full border bg-background shadow md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2">
                                        <div className="h-2.5 w-2.5 bg-green-500 rounded-full"></div>
                                    </div>
                                    <div className="w-[calc(100%-4rem)] rounded-lg border bg-card p-4 shadow-sm md:w-[calc(50%-2.5rem)]">
                                        <div className="mb-1 flex items-center justify-between">
                                            <div className="font-bold text-sm">Success</div>
                                            <time className="text-xs text-muted-foreground">1h ago</time>
                                        </div>
                                        <p className="text-xs text-muted-foreground">
                                            Imported 3 new threads. Generated 15 flashcards.
                                        </p>
                                    </div>
                                </div>

                                {/* Log Item 3 */}
                                <div className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group">
                                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full border bg-background shadow md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2">
                                        <AlertCircle className="h-4 w-4 text-red-500" />
                                    </div>
                                    <div className="w-[calc(100%-4rem)] rounded-lg border bg-card p-4 shadow-sm md:w-[calc(50%-2.5rem)]">
                                        <div className="mb-1 flex items-center justify-between">
                                            <div className="font-bold text-sm text-red-500">Error</div>
                                            <time className="text-xs text-muted-foreground">5h ago</time>
                                        </div>
                                        <p className="text-xs text-muted-foreground">
                                            Rate limit exceeded. Waiting 15min before retry.
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </TabsContent>
                </Tabs>
            </div>
        </SlideOver>
    );
}
