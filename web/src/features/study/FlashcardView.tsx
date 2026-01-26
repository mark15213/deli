"use client"

import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { RotateCw, CheckCheck, X as XIcon, Meh } from "lucide-react"
import { Card } from "@/components/ui/card"
import { SourceContext } from "@/components/source-context"


export function FlashcardView() {
    const [isFlipped, setIsFlipped] = useState(false)

    const handleFlip = () => setIsFlipped(!isFlipped)

    return (
        <div className="h-full flex flex-col bg-background relative overflow-hidden">
            {/* Progress Header */}
            <div className="p-4 flex items-center gap-4 border-b bg-background/50 backdrop-blur-sm z-10">
                <span className="text-sm font-medium whitespace-nowrap">Daily Goal</span>
                <Progress value={33} className="h-2" />
                <span className="text-sm font-medium whitespace-nowrap text-muted-foreground">4 / 12</span>
            </div>

            {/* Card Stage */}
            <div className="flex-1 flex items-center justify-center p-8 perspective-1000">
                <div className="relative w-full max-w-2xl aspect-[3/2] cursor-pointer" onClick={handleFlip}>
                    <motion.div
                        className="w-full h-full absolute inset-0"
                        initial={false}
                        animate={{ rotateX: isFlipped ? 180 : 0 }}
                        transition={{ duration: 0.6, type: "spring", stiffness: 260, damping: 20 }}
                        style={{ transformStyle: "preserve-3d" }}
                    >
                        {/* Front */}
                        <Card className="absolute inset-0 w-full h-full backface-hidden flex flex-col items-center justify-center p-12 text-center shadow-xl border-2">
                            <div className="text-muted-foreground text-sm uppercase tracking-widest font-semibold mb-8">Question</div>
                            <h2 className="text-3xl font-bold leading-tight">
                                Why does tokenization hinder arithmetic reasoning in LLMs?
                            </h2>
                        </Card>

                        {/* Back */}
                        <Card
                            className="absolute inset-0 w-full h-full backface-hidden flex flex-col items-center justify-center p-12 text-center shadow-xl border-2 bg-muted/20"
                            style={{ transform: "rotateX(180deg)" }}
                        >
                            <div className="text-muted-foreground text-sm uppercase tracking-widest font-semibold mb-8">Answer</div>
                            <p className="text-xl leading-relaxed">
                                It often groups digits arbitrarily (e.g., 1234 {'->'} 12, 34), confusing the model about place values.
                            </p>
                            <div className="mt-8 pt-6 border-t w-full flex items-center justify-center">
                                <SourceContext source="@karpathy" type="Thread" />
                            </div>
                        </Card>
                    </motion.div>
                </div>
            </div>

            {/* Controls */}
            <div className="p-8 pb-12 flex items-center justify-center gap-6">
                <div className="flex flex-col items-center gap-2">
                    <Button variant="outline" size="lg" className="h-16 w-16 rounded-full border-red-200 hover:bg-red-50 hover:border-red-500 text-red-500">
                        <XIcon className="h-6 w-6" />
                    </Button>
                    <span className="text-xs font-medium text-muted-foreground">Forgot</span>
                </div>

                <div className="flex flex-col items-center gap-2">
                    <Button variant="outline" size="lg" className="h-16 w-16 rounded-full border-yellow-200 hover:bg-yellow-50 hover:border-yellow-500 text-yellow-600">
                        <Meh className="h-6 w-6" />
                    </Button>
                    <span className="text-xs font-medium text-muted-foreground">Hard</span>
                </div>

                <div className="flex flex-col items-center gap-2">
                    <Button variant="outline" size="lg" className="h-16 w-16 rounded-full border-green-200 hover:bg-green-50 hover:border-green-500 text-green-600">
                        <CheckCheck className="h-6 w-6" />
                    </Button>
                    <span className="text-xs font-medium text-muted-foreground">Easy</span>
                </div>
            </div>
        </div>
    )
}
