"use client"

import { Button } from "@/components/ui/button"
import { Switch } from "@/components/ui/switch"
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select"
import { RefreshCw, UserCheck, Tag } from "lucide-react"

export function ConfigTab() {
    return (
        <div className="space-y-6 py-4">
            {/* Authentication */}
            <div className="space-y-3">
                <h3 className="text-sm font-medium flex items-center gap-2">
                    <UserCheck className="h-4 w-4" /> Authentication
                </h3>
                <div className="rounded-lg border bg-card p-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-bold dark:bg-blue-900/30 dark:text-blue-400">
                                NW
                            </div>
                            <div>
                                <p className="font-medium text-sm">Connected as @naval_watcher</p>
                                <p className="text-xs text-muted-foreground">Access valid until Feb 2026</p>
                            </div>
                        </div>
                        <Button variant="outline" size="sm">Reconnect</Button>
                    </div>
                </div>
            </div>

            {/* Sync Frequency */}
            <div className="space-y-3">
                <h3 className="text-sm font-medium flex items-center gap-2">
                    <RefreshCw className="h-4 w-4" /> Sync Frequency
                </h3>
                <div className="rounded-lg border bg-card p-4 space-y-2">
                    <label className="text-xs text-muted-foreground">Check for updates every:</label>
                    <Select defaultValue="1h">
                        <SelectTrigger>
                            <SelectValue placeholder="Select frequency" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="realtime">Real-time (Stream)</SelectItem>
                            <SelectItem value="15m">15 Minutes</SelectItem>
                            <SelectItem value="1h">1 Hour</SelectItem>
                            <SelectItem value="6h">6 Hours</SelectItem>
                            <SelectItem value="24h">24 Hours</SelectItem>
                        </SelectContent>
                    </Select>
                    <p className="text-[10px] text-muted-foreground mt-1">High frequency may consume more API credits.</p>
                </div>
            </div>

            {/* Auto-tagging */}
            <div className="space-y-3">
                <h3 className="text-sm font-medium flex items-center gap-2">
                    <Tag className="h-4 w-4" /> Automation
                </h3>
                <div className="rounded-lg border bg-card p-4 flex items-center justify-between">
                    <div className="space-y-0.5">
                        <label className="text-sm font-medium">Auto-tagging</label>
                        <p className="text-xs text-muted-foreground">AI automatically categorizes content</p>
                    </div>
                    <Switch defaultChecked />
                </div>
            </div>
        </div>
    )
}
