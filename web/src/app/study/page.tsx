"use client";

import * as React from "react";
import { AppShell } from "@/components/layout/app-shell";
import { FeedColumn } from "@/components/layout/feed-column";
import { DetailColumn } from "@/components/layout/detail-column";
import { FlashcardView } from "@/features/study/flashcard-view";
import { AudioPlayer, TranscriptSync } from "@/features/study/audio-player";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { BookOpen, Headphones } from "lucide-react";

export default function StudyPage() {
    return (
        <AppShell>
            <FeedColumn className="w-full md:w-[350px]">
                <div className="p-4">
                    <h1 className="text-xl font-bold mb-4">Study Mode</h1>
                    <div className="space-y-2">
                        <div className="p-3 bg-accent rounded-lg cursor-pointer border-l-4 border-l-primary">
                            <div className="flex items-center gap-2 mb-1">
                                <BookOpen className="h-4 w-4 text-primary" />
                                <span className="font-medium">Flashcards</span>
                            </div>
                            <p className="text-xs text-muted-foreground">12 cards due today</p>
                        </div>
                        <div className="p-3 hover:bg-accent/50 rounded-lg cursor-pointer transition-colors">
                            <div className="flex items-center gap-2 mb-1">
                                <Headphones className="h-4 w-4" />
                                <span className="font-medium">Daily Briefing</span>
                            </div>
                            <p className="text-xs text-muted-foreground">15 mins audio generated</p>
                        </div>
                    </div>

                    <div className="mt-8 border-t pt-4">
                        <h3 className="text-sm font-medium mb-3">Up Next</h3>
                        <div className="space-y-3">
                            <div className="flex items-center gap-3 text-sm text-muted-foreground">
                                <div className="h-2 w-2 rounded-full bg-green-500" />
                                <span>Design Systems Quiz</span>
                            </div>
                            <div className="flex items-center gap-3 text-sm text-muted-foreground">
                                <div className="h-2 w-2 rounded-full bg-blue-500" />
                                <span>React Hooks Recap</span>
                            </div>
                        </div>
                    </div>
                </div>
            </FeedColumn>

            <DetailColumn>
                <Tabs defaultValue="flashcard" className="h-full flex flex-col">
                    <div className="border-b px-4 py-2">
                        <TabsList>
                            <TabsTrigger value="flashcard" className="gap-2">
                                <BookOpen className="h-4 w-4" /> Flashcards
                            </TabsTrigger>
                            <TabsTrigger value="audio" className="gap-2">
                                <Headphones className="h-4 w-4" /> Audio Player
                            </TabsTrigger>
                        </TabsList>
                    </div>

                    <TabsContent value="flashcard" className="flex-1 m-0 p-0">
                        <FlashcardView />
                    </TabsContent>

                    <TabsContent value="audio" className="flex-1 m-0 p-0 flex h-full">
                        <div className="w-1/2 h-full border-r">
                            <AudioPlayer />
                        </div>
                        <div className="w-1/2 h-full bg-background">
                            <TranscriptSync />
                        </div>
                    </TabsContent>
                </Tabs>
            </DetailColumn>
        </AppShell>
    );
}
