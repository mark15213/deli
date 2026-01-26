"use client";

import * as React from "react";
import { MessageSquare, Wand2, ThumbsDown, Check, Edit2, Copy } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

interface AiOutputPreviewProps {
    type: "flashcard" | "quiz" | "summary";
}

export function AiOutputPreview() {
    return (
        <div className="h-full overflow-y-auto p-6 bg-background border-l">
            <div className="max-w-md mx-auto space-y-6">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <Wand2 className="h-5 w-5 text-purple-500" />
                        <h2 className="text-lg font-semibold">AI Generation</h2>
                    </div>
                    <div className="flex gap-2">
                        <Button variant="outline" size="sm" className="h-8 gap-2 text-red-500 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-950/20">
                            <ThumbsDown className="h-3 w-3" />
                            Bad
                        </Button>
                        <Button size="sm" className="h-8 gap-2">
                            <Check className="h-3 w-3" />
                            Approve
                        </Button>
                    </div>
                </div>

                <Tabs defaultValue="flashcards">
                    <TabsList className="w-full">
                        <TabsTrigger value="flashcards" className="flex-1">Flashcards (3)</TabsTrigger>
                        <TabsTrigger value="summary" className="flex-1">Summary</TabsTrigger>
                    </TabsList>

                    <TabsContent value="flashcards" className="space-y-4 pt-4">
                        {/* Flashcard 1 */}
                        <Card>
                            <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
                                <CardTitle className="text-sm font-medium text-muted-foreground">
                                    Card 1/3
                                </CardTitle>
                                <Button variant="ghost" size="icon" className="h-6 w-6">
                                    <Edit2 className="h-3 w-3" />
                                </Button>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div className="space-y-2">
                                    <label className="text-xs font-semibold uppercase text-muted-foreground">Front</label>
                                    <div className="text-sm font-medium">What is the difference between wealth and money according to Naval?</div>
                                </div>
                                <div className="space-y-2">
                                    <label className="text-xs font-semibold uppercase text-muted-foreground">Back</label>
                                    <div className="text-sm">Money is how we transfer wealth. Wealth is assets that earn while you sleep (equity, code, media).</div>
                                </div>
                            </CardContent>
                        </Card>

                        {/* Flashcard 2 */}
                        <Card>
                            <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
                                <CardTitle className="text-sm font-medium text-muted-foreground">
                                    Card 2/3
                                </CardTitle>
                                <Button variant="ghost" size="icon" className="h-6 w-6">
                                    <Edit2 className="h-3 w-3" />
                                </Button>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div className="space-y-2">
                                    <label className="text-xs font-semibold uppercase text-muted-foreground">Front</label>
                                    <div className="text-sm font-medium">Why is renting out your time a bad strategy for wealth?</div>
                                </div>
                                <div className="space-y-2">
                                    <label className="text-xs font-semibold uppercase text-muted-foreground">Back</label>
                                    <div className="text-sm">Your inputs are linearly related to your outputs. You can't earn non-linearly or have leverage.</div>
                                </div>
                            </CardContent>
                        </Card>
                    </TabsContent>

                    <TabsContent value="summary" className="pt-4">
                        <Card>
                            <CardContent className="pt-6">
                                <p className="text-sm leading-relaxed text-muted-foreground">
                                    Naval argues that to get rich, you need to own equity (a piece of a business). Renting out your time will never make you wealthy because it's not scalable. He distinguishes "Money" (transfer of wealth) from "Wealth" (assets that earn while you sleep). The goal is to productize yourself using code or media to gain leverage.
                                </p>
                            </CardContent>
                            <CardFooter className="justify-end pt-0">
                                <Button variant="ghost" size="sm" className="gap-2">
                                    <Copy className="h-3 w-3" /> Copy
                                </Button>
                            </CardFooter>
                        </Card>
                    </TabsContent>
                </Tabs>
            </div>
        </div>
    );
}
