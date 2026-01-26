"use client";

import * as React from "react";
import { AppShell } from "@/components/layout/app-shell";
import { FeedColumn } from "@/components/layout/feed-column";
import { DetailColumn } from "@/components/layout/detail-column";
import { SourceGrid } from "@/features/sources/source-grid";
import { SourceDetailDrawer } from "@/features/sources/source-detail-drawer";
import { QuickAddButton, QuickAddModal } from "@/features/sources/quick-add-modal";
import { StatusStream } from "@/features/sources/status-stream";
import { Badge } from "@/components/ui/badge";

export default function SourcesPage() {
    return (
        <AppShell>
            {/* Feed Column - Source List */}
            <FeedColumn className="w-full md:w-[450px] lg:w-[500px]">
                <div className="sticky top-0 z-10 bg-background border-b">
                    <StatusStream />
                    <div className="flex items-center justify-between p-4 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
                        <div className="flex items-center gap-2">
                            <h1 className="text-xl font-bold">Source Hub</h1>
                            <Badge variant="secondary" className="rounded-full px-2">5</Badge>
                        </div>
                        <QuickAddButton />
                    </div>
                </div>

                <SourceGrid />
            </FeedColumn>

            {/* Detail Column - Empty State or Info */}
            <DetailColumn>
                <div className="flex h-full flex-col items-center justify-center p-8 text-center text-muted-foreground">
                    <div className="max-w-md space-y-4">
                        <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-full bg-muted">
                            <span className="text-4xl">🔌</span>
                        </div>
                        <h2 className="text-2xl font-semibold text-foreground">Connect Data Sources</h2>
                        <p>
                            Integrate your information streams to start the digestion process.
                            Gulp currently supports Twitter/X, RSS Feeds, Notion Databases, and more.
                        </p>
                    </div>
                </div>
            </DetailColumn>

            {/* Overlays */}
            <SourceDetailDrawer />
            <QuickAddModal />
        </AppShell>
    );
}
