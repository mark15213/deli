
"use client"

import { Source, SourceType } from "@/types/source"
import { useState } from "react"
import { XConfigForm } from "./XConfigForm"
// Import others later...

interface SourceFormContainerProps {
    type: SourceType
    initialData?: Source
    onSave: (data: Partial<Source>) => void
}

export function SourceFormContainer({ type, initialData, onSave }: SourceFormContainerProps) {
    // Initialize state with defaults or initialData
    const [connection, setConnection] = useState(initialData?.connection_config || getDefaultConnection(type))
    const [rules, setRules] = useState(initialData?.ingestion_rules || getDefaultRules(type))
    const [name, setName] = useState(initialData?.name || "")

    const handleSave = () => {
        onSave({
            name,
            type,
            connection_config: connection as any,
            ingestion_rules: rules as any
        })
    }

    // Render logic
    const renderForm = () => {
        switch (type) {
            case 'X_SOCIAL':
                return <XConfigForm
                    connection={connection as any}
                    rules={rules as any}
                    onChange={(c, r) => { setConnection(c); setRules(r); }}
                />
            case 'NOTION_KB':
                return <div>Notion Form Placeholder</div>
            default:
                return <div>Unsupported Source Type</div>
        }
    }

    return (
        <div className="flex flex-col h-full">
            <div className="flex-1 overflow-y-auto p-1">
                <div className="mb-4">
                    <label className="text-sm font-medium">Source Name</label>
                    <input
                        className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
                        value={name}
                        onChange={e => setName(e.target.value)}
                        placeholder="My Awesome Source"
                    />
                </div>
                {renderForm()}
            </div>
            {/* Save Button is usually in the footer of Drawer, but we can expose onSave */}
        </div>
    )
}

// Helpers for defaults
function getDefaultConnection(type: SourceType) {
    switch (type) {
        case 'X_SOCIAL': return { target_username: '', auth_mode: 'API_KEY', api_token: '' }
            // ... others
            return {}
    }
}

function getDefaultRules(type: SourceType) {
    switch (type) {
        case 'X_SOCIAL': return { scope: 'USER_FEED', include_replies: false, min_likes_threshold: 50, fetch_frequency: 'HOURLY', grouping_strategy: 'THREAD' }
            // ... others
            return {}
    }
}
