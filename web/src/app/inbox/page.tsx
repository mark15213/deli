"use client";

import * as React from "react";
import { AppShell } from "@/components/layout/app-shell";
import { FeedColumn } from "@/components/layout/feed-column";
import { DetailColumn } from "@/components/layout/detail-column";
import { InboxList } from "@/features/inbox/inbox-list";
import { SplitView } from "@/features/inbox/split-view";
import { useUIStore } from "@/store/ui-store";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Filter } from "lucide-react";

export default function InboxPage() {
    const { selectedInboxItemId } = useUIStore();

    return (
        <AppShell>
            <FeedColumn className="w-full md:w-[400px]">
                <div className="sticky top-0 z-10 bg-background border-b p-4">
                    <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                            <h1 className="text-xl font-bold">Inbox</h1>
                            <Badge variant="secondary" className="rounded-full px-2">12</Badge>
                        </div>
                        <Button variant="ghost" size="icon" className="h-8 w-8">
                            <Filter className="h-4 w-4" />
                        </Button>
                    </div>
                    {/* Tabs or Filters could go here */}
                </div>
                <InboxList />
            </FeedColumn>

            <DetailColumn>
                <SplitView itemId={selectedInboxItemId} />
            </DetailColumn>
        </AppShell>
    );
}
