"use client"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Plus, Trash2, AtSign, Rss } from "lucide-react"
import { useState } from "react"
import { Badge } from "@/components/ui/badge"

export function RulesTab() {
    const [monitoredAccounts, setMonitoredAccounts] = useState(["naval", "paulg", "sama"])

    const addAccount = () => {
        // Logic to add
    }

    return (
        <div className="space-y-6 py-4">
            {/* Monitored Accounts (Twitter specific example) */}
            <div className="space-y-3">
                <h3 className="text-sm font-medium flex items-center gap-2">
                    <AtSign className="h-4 w-4" /> Monitored Accounts
                </h3>
                <div className="rounded-lg border bg-card p-4 space-y-4">
                    <div className="flex gap-2">
                        <Input placeholder="Enter handle (e.g. elonmusk)" className="h-9" />
                        <Button size="sm" variant="secondary"><Plus className="h-4 w-4" /></Button>
                    </div>

                    <div className="space-y-2">
                        {monitoredAccounts.map(acc => (
                            <div key={acc} className="flex items-center justify-between p-2 rounded-md bg-muted/50 text-sm">
                                <span className="font-medium">@{acc}</span>
                                <button className="text-muted-foreground hover:text-destructive transition-colors">
                                    <Trash2 className="h-4 w-4" />
                                </button>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Content Types */}
            <div className="space-y-3">
                <h3 className="text-sm font-medium flex items-center gap-2">
                    <Rss className="h-4 w-4" /> Content Filters
                </h3>
                <div className="rounded-lg border bg-card p-4 space-y-3">
                    <label className="flex items-center gap-2 cursor-pointer">
                        <input type="checkbox" className="rounded border-input text-primary focus:ring-primary" defaultChecked />
                        <span className="text-sm">Include Bookmarks</span>
                    </label>
                    <label className="flex items-center gap-2 cursor-pointer">
                        <input type="checkbox" className="rounded border-input text-primary focus:ring-primary" defaultChecked />
                        <span className="text-sm">Include Threads</span>
                    </label>
                    <label className="flex items-center gap-2 cursor-pointer">
                        <input type="checkbox" className="rounded border-input text-primary focus:ring-primary" />
                        <span className="text-sm text-muted-foreground">Include Replies (High Noise)</span>
                    </label>
                </div>
            </div>
        </div>
    )
}
