"use client";

import * as React from "react";
import { Source, SourceCard } from "./source-card";

// Mock data for sources
const items: Source[] = [
    {
        id: "1",
        type: "twitter",
        name: "Naval Ravikant",
        description: "Monitoring tweets and threads from @naval for wisdom and investing opacity.",
        status: "syncing",
        lastSync: "Just now",
        itemCount: 142,
        tags: ["wisdom", "investing"],
    },
    {
        id: "2",
        type: "rss",
        name: "Paul Graham Essays",
        description: "New essays from paulgraham.com/articles.html",
        status: "active",
        lastSync: "2h ago",
        itemCount: 23,
        tags: ["startup", "essay"],
    },
    {
        id: "3",
        type: "notion",
        name: "Research Workspace",
        description: "Syncing pages from 'Research' database for processing.",
        status: "active",
        lastSync: "5h ago",
        itemCount: 89,
        tags: ["work", "research"],
    },
    {
        id: "4",
        type: "arxiv",
        name: "LLM Papers",
        description: "Daily CS.AI papers matching 'Large Language Model' or 'Agent'.",
        status: "active",
        lastSync: "1d ago",
        itemCount: 15,
        tags: ["ai", "papers"],
    },
    {
        id: "5",
        type: "github",
        name: "LangChain Repo",
        description: "Tracking releases and major PRs in langchain-ai/langchain.",
        status: "error",
        lastSync: "Failed 2m ago",
        itemCount: 0,
        tags: ["code", "library"],
    },
];

export function SourceGrid() {
    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 xl:grid-cols-3 gap-4 p-4">
            {items.map((source) => (
                <SourceCard key={source.id} source={source} />
            ))}
        </div>
    );
}
