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

interface SourceDetailDrawerProps {
    isOpen: boolean
    onClose: () => void
    sourceId: string | null
}

export function SourceDetailDrawer({ isOpen, onClose, sourceId }: SourceDetailDrawerProps) {
    // In a real app, use sourceId to fetch data

    return (
        <Sheet open={isOpen} onOpenChange={onClose}>
            <SheetContent className="w-[400px] sm:w-[540px] sm:max-w-none flex flex-col h-full bg-background" side="right">

                {/* Header */}
                <div className="flex-none space-y-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <SheetTitle className="flex items-center gap-2 text-xl">
                                X / Twitter
                                <span className="flex h-2 w-2 rounded-full bg-green-500 ring-4 ring-green-500/20" />
                            </SheetTitle>
                            <SheetDescription className="mt-1">
                                Configure connection, sync rules and view logs.
                            </SheetDescription>
                        </div>
                        <div className="flex items-center gap-2 border rounded-full px-3 py-1 bg-muted/50">
                            <span className="text-xs font-medium text-muted-foreground">Active</span>
                            <Switch defaultChecked />
                        </div>
                    </div>
                </div>

                {/* Body - Unified Form */}
                <div className="flex-1 overflow-hidden mt-6 flex flex-col">
                    <SourceFormContainer
                        type={sourceId === 'twitter' ? 'X_SOCIAL' : sourceId === 'notion' ? 'NOTION_KB' : 'WEB_RSS'}
                        onSave={(data) => console.log("Saving:", data)}
                    />
                </div>

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
