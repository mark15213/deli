"use client"

import {
    Sheet,
    SheetContent,
    SheetDescription,
    SheetHeader,
    SheetTitle,
} from "@/components/ui/sheet"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Switch } from "@/components/ui/switch"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import { Badge } from "@/components/ui/badge"

interface SourceConfigSheetProps {
    open: boolean
    onOpenChange: (open: boolean) => void
    sourceId?: string | null
}

export function SourceConfigSheet({ open, onOpenChange, sourceId }: SourceConfigSheetProps) {
    return (
        <Sheet open={open} onOpenChange={onOpenChange}>
            <SheetContent className="w-[500px] sm:max-w-[500px] flex flex-col gap-0 p-0">
                <SheetHeader className="p-6 border-b">
                    <SheetTitle className="flex items-center gap-2">
                        <span className="text-xl">@naval</span>
                        <Badge variant="outline">Twitter</Badge>
                    </SheetTitle>
                    <SheetDescription>
                        Configure content ingestion rules for this source.
                    </SheetDescription>
                </SheetHeader>

                <div className="flex-1 overflow-y-auto">
                    <Tabs defaultValue="config" className="w-full">
                        <div className="p-6 pb-0">
                            <TabsList className="w-full grid grid-cols-3">
                                <TabsTrigger value="config">Config</TabsTrigger>
                                <TabsTrigger value="rules">Rules</TabsTrigger>
                                <TabsTrigger value="logs">Logs</TabsTrigger>
                            </TabsList>
                        </div>

                        <div className="p-6">
                            <TabsContent value="config" className="space-y-6 mt-0">
                                <div className="flex items-center justify-between">
                                    <div className="space-y-0.5">
                                        <Label>Auto-Sync</Label>
                                        <p className="text-sm text-muted-foreground">Automatically fetch new content</p>
                                    </div>
                                    <Switch defaultChecked />
                                </div>
                                <div className="space-y-2">
                                    <Label>Sync Frequency</Label>
                                    <select className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background disabled:cursor-not-allowed disabled:opacity-50">
                                        <option>Real-time</option>
                                        <option>Hourly</option>
                                        <option>Daily</option>
                                    </select>
                                </div>
                                <div className="space-y-2">
                                    <Label>Auth Status</Label>
                                    <div className="flex items-center gap-2">
                                        <div className="h-2 w-2 rounded-full bg-green-500"></div>
                                        <span className="text-sm">Connected</span>
                                        <Button variant="link" size="sm" className="ml-auto">Reconnect</Button>
                                    </div>
                                </div>
                            </TabsContent>

                            <TabsContent value="rules" className="space-y-6 mt-0">
                                <div className="space-y-4">
                                    <Label>Content Types</Label>
                                    <div className="flex flex-col gap-2">
                                        <label className="flex items-center gap-2 text-sm">
                                            <input type="checkbox" className="rounded border-gray-300" defaultChecked /> Threads
                                        </label>
                                        <label className="flex items-center gap-2 text-sm">
                                            <input type="checkbox" className="rounded border-gray-300" defaultChecked /> Bookmarks
                                        </label>
                                        <label className="flex items-center gap-2 text-sm">
                                            <input type="checkbox" className="rounded border-gray-300" /> Replies
                                        </label>
                                    </div>
                                </div>
                            </TabsContent>

                            <TabsContent value="logs" className="space-y-4 mt-0">
                                <div className="space-y-4">
                                    <div className="flex flex-col gap-2">
                                        {[1, 2, 3].map((i) => (
                                            <div key={i} className="flex items-center gap-3 text-sm">
                                                <span className="text-green-500 text-xs font-mono">SUCCESS</span>
                                                <span className="text-muted-foreground">Synced 5 items</span>
                                                <span className="ml-auto text-muted-foreground text-xs">2m ago</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </TabsContent>
                        </div>
                    </Tabs>
                </div>

                <div className="p-6 border-t mt-auto bg-muted/20 flex justify-between items-center">
                    <Button variant="destructive" size="sm">Delete Source</Button>
                    <div className="flex gap-2">
                        <Button variant="ghost" size="sm">Sync Now</Button>
                        <Button size="sm">Save Changes</Button>
                    </div>
                </div>
            </SheetContent>
        </Sheet>
    )
}
