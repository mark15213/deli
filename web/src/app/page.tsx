"use client";

import { AppShell } from "@/components/layout/app-shell";
import { FeedColumn } from "@/components/layout/feed-column";
import { DetailColumn } from "@/components/layout/detail-column";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { DigestionChart } from "@/features/dashboard/digestion-chart";

export default function Home() {
    return (
        <AppShell>
            <FeedColumn>
                <div className="p-4 space-y-4">
                    <h2 className="text-lg font-semibold mb-4">Dashboard</h2>

                    {/* Digestion Rate Card */}
                    <Card>
                        <CardHeader className="pb-2">
                            <CardTitle className="text-sm font-medium text-muted-foreground">
                                Today&apos;s Digestion Rate
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <DigestionChart input={50} learned={20} />
                        </CardContent>
                    </Card>

                    {/* Quick Stats */}
                    <div className="grid grid-cols-2 gap-3">
                        <Card>
                            <CardContent className="p-4">
                                <p className="text-sm text-muted-foreground">Pending</p>
                                <p className="text-2xl font-bold">12</p>
                            </CardContent>
                        </Card>
                        <Card>
                            <CardContent className="p-4">
                                <p className="text-sm text-muted-foreground">Sources</p>
                                <p className="text-2xl font-bold">5</p>
                            </CardContent>
                        </Card>
                        <Card>
                            <CardContent className="p-4">
                                <p className="text-sm text-muted-foreground">Flashcards</p>
                                <p className="text-2xl font-bold">156</p>
                            </CardContent>
                        </Card>
                        <Card>
                            <CardContent className="p-4">
                                <p className="text-sm text-muted-foreground">Due Today</p>
                                <p className="text-2xl font-bold">23</p>
                            </CardContent>
                        </Card>
                    </div>
                </div>
            </FeedColumn>

            <DetailColumn>
                <div className="flex h-full items-center justify-center text-muted-foreground">
                    <div className="text-center max-w-lg p-6">
                        <div className="mb-6 flex justify-center">
                            <div className="h-24 w-24 rounded-2xl bg-gradient-to-tr from-primary/20 to-primary/5 flex items-center justify-center">
                                <span className="text-5xl">🧠</span>
                            </div>
                        </div>
                        <h3 className="text-2xl font-bold mb-2 text-foreground">Welcome to Gulp</h3>
                        <p className="text-lg mb-6">
                            Your personal knowledge digestion engine.
                        </p>
                        <div className="grid grid-cols-3 gap-4 text-center">
                            <div className="p-4 rounded-lg bg-card border">
                                <p className="font-bold text-lg">1. Ingest</p>
                                <p className="text-xs text-muted-foreground">Add data sources</p>
                            </div>
                            <div className="p-4 rounded-lg bg-card border">
                                <p className="font-bold text-lg">2. Process</p>
                                <p className="text-xs text-muted-foreground">AI Generates insights</p>
                            </div>
                            <div className="p-4 rounded-lg bg-card border">
                                <p className="font-bold text-lg">3. Learn</p>
                                <p className="text-xs text-muted-foreground">Internalize knowledge</p>
                            </div>
                        </div>
                    </div>
                </div>
            </DetailColumn>
        </AppShell>
    );
}
