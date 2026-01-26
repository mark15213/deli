"use client";

import * as React from "react";
import { InboxItem, type InboxItem as InboxItemType } from "./inbox-item";

const mockItems: InboxItemType[] = [
    {
        id: "1",
        sourceType: "twitter",
        sourceName: "@naval",
        title: "Thread on Wealth Creation",
        summary: "Naval discusses the difference between wealth and money, emphasizing equity ownership and productizing yourself.",
        receivedAt: "10m ago",
        tags: ["wealth", "mindset"],
        generatedArtifacts: ["flashcard", "summary"],
    },
    {
        id: "2",
        sourceType: "arxiv",
        title: "Agents: An Open-ended Learning System",
        sourceName: "Arxiv:2305.12345",
        summary: "This paper proposes a new architecture for autonomous agents that can learn from open-ended environments without explicit reward functions.",
        receivedAt: "2h ago",
        tags: ["ai", "agents", "research"],
        generatedArtifacts: ["summary", "quiz"],
    },
    {
        id: "3",
        sourceType: "notion",
        title: "Q3 okrs draft",
        sourceName: "Product Wiki",
        summary: "Draft objectives for Q3 focusing on user retention and viral growth loops.",
        receivedAt: "5h ago",
        tags: ["work", "planning"],
        generatedArtifacts: ["summary"],
    },
    {
        id: "4",
        sourceType: "rss",
        title: "How to Do Great Work",
        sourceName: "Paul Graham",
        summary: "A comprehensive guide on finding your life's work, staying curious, and the importance of compounding effort over time.",
        receivedAt: "1d ago",
        tags: ["career", "advice"],
        generatedArtifacts: ["flashcard", "audio"],
    },
];

export function InboxList() {
    return (
        <div className="flex flex-col">
            {mockItems.map((item) => (
                <InboxItem key={item.id} item={item} />
            ))}
        </div>
    );
}
