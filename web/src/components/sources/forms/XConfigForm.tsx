
"use client"

import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Switch } from "@/components/ui/switch"
import { XConnectionConfig, XIngestionRules } from "@/types/source"
import { useEffect, useState } from "react"

interface XFormProps {
    connection: XConnectionConfig
    rules: XIngestionRules
    onChange: (connection: XConnectionConfig, rules: XIngestionRules) => void
}

export function XConfigForm({ connection, rules, onChange }: XFormProps) {
    const handleConnChange = (key: keyof XConnectionConfig, value: any) => {
        onChange({ ...connection, [key]: value }, rules)
    }

    const handleRuleChange = (key: keyof XIngestionRules, value: any) => {
        onChange(connection, { ...rules, [key]: value })
    }

    return (
        <div className="space-y-6">
            <div className="space-y-4">
                <h3 className="text-sm font-medium border-b pb-2">Connection</h3>
                <div className="grid w-full items-center gap-1.5">
                    <Label htmlFor="username">Target Username/Handle</Label>
                    <Input
                        id="username"
                        value={connection.target_username}
                        onChange={e => handleConnChange('target_username', e.target.value)}
                        placeholder="@elonmusk"
                    />
                </div>
                <div className="grid w-full items-center gap-1.5">
                    <Label htmlFor="token">API Token (Secret)</Label>
                    <Input
                        id="token"
                        type="password"
                        value={connection.api_token}
                        onChange={e => handleConnChange('api_token', e.target.value)}
                    />
                </div>
            </div>

            <div className="space-y-4">
                <h3 className="text-sm font-medium border-b pb-2">Ingestion Rules</h3>

                <div className="grid w-full items-center gap-1.5">
                    <Label>Scope</Label>
                    <Select value={rules.scope} onValueChange={v => handleRuleChange('scope', v)}>
                        <SelectTrigger><SelectValue /></SelectTrigger>
                        <SelectContent>
                            <SelectItem value="USER_FEED">User Feed</SelectItem>
                            <SelectItem value="BOOKMARKS">Bookmarks</SelectItem>
                            <SelectItem value="SEARCH_KEYWORD">Search</SelectItem>
                        </SelectContent>
                    </Select>
                </div>

                <div className="flex items-center justify-between">
                    <Label htmlFor="replies">Include Replies</Label>
                    <Switch
                        id="replies"
                        checked={rules.include_replies}
                        onCheckedChange={c => handleRuleChange('include_replies', c)}
                    />
                </div>

                <div className="grid w-full items-center gap-1.5">
                    <Label htmlFor="likes">Min Likes Threshold: {rules.min_likes_threshold}</Label>
                    <input
                        type="range"
                        min="0" max="1000" step="10"
                        value={rules.min_likes_threshold}
                        className="w-full"
                        onChange={e => handleRuleChange('min_likes_threshold', parseInt(e.target.value))}
                    />
                </div>

                <div className="grid w-full items-center gap-1.5">
                    <Label>Grouping Strategy</Label>
                    <Select value={rules.grouping_strategy} onValueChange={v => handleRuleChange('grouping_strategy', v)}>
                        <SelectTrigger><SelectValue /></SelectTrigger>
                        <SelectContent>
                            <SelectItem value="THREAD">Thread (Combined)</SelectItem>
                            <SelectItem value="SINGLE">Single Tweet</SelectItem>
                        </SelectContent>
                    </Select>
                </div>
            </div>
        </div>
    )
}
