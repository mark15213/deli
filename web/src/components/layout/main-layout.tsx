"use client"

import * as React from "react"
import {
    ResizableHandle,
    ResizablePanel,
    ResizablePanelGroup,
} from "@/components/ui/resizable"
import { Sidebar } from "./sidebar"
import { FeedColumn } from "./feed-column"
import { DetailColumn } from "./detail-column"

export function MainLayout() {
    return (
        <div className="h-screen w-full bg-background">
            <ResizablePanelGroup direction="horizontal">
                <ResizablePanel defaultSize={20} minSize={15} maxSize={25}>
                    <Sidebar h-full />
                </ResizablePanel>

                <ResizableHandle />

                <ResizablePanel defaultSize={30} minSize={25} maxSize={40}>
                    <FeedColumn h-full />
                </ResizablePanel>

                <ResizableHandle />

                <ResizablePanel defaultSize={50}>
                    <DetailColumn h-full />
                </ResizablePanel>
            </ResizablePanelGroup>
        </div>
    )
}
