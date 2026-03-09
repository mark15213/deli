"use client"

import { useState } from "react"
import { Sparkles, FileText, CheckCircle2, Zap, BrainCircuit, ArrowRight, X, ChevronRight, Image as ImageIcon, Play, BookOpen } from "lucide-react"

import { Card, CardContent, CardFooter, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"

// --- MOCK DATA ---
const MOCK_STREAM_CARDS = [
    {
        id: "stream-1",
        title: "The Architecture of a Modern AI Agent",
        summary: "This article breaks down the cognitive architecture of ReAct, Tool use, and Memory structures that power modern autonomous agents like AutoGPT and BabyAGI.",
        imageUrl: "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?q=80&w=600&auto=format&fit=crop",
        source: "AI Architecture",
        height: "h-64", // Mocked varied height for masonry
        content: "Delving into the ReAct pattern, we find that combining reasoning and acting traces allows agents to hallucinate less and perform better. Agents use external tools like calculators or web search to augment their LLM capabilities. Memory, both short-term (context window) and long-term (vector databases), forms the backbone of sustained interaction."
    },
    {
        id: "stream-2",
        title: "Understanding React Server Components",
        summary: "A deep dive into how RSCs differ from SSR, their impact on bundle size, and why they represent a paradigm shift in full-stack web development.",
        imageUrl: "https://images.unsplash.com/photo-1555066931-4365d14bab8c?q=80&w=600&auto=format&fit=crop",
        source: "Web Development",
        height: "h-80",
        content: "React Server Components (RSC) allow developers to write components that only execute on the server. They never ship their JavaScript dependencies to the client, drastically reducing bundle sizes. This conceptually splits the component tree into server-only and client-interactive parts."
    },
    {
        id: "stream-3",
        title: "Mental Models for Product Management",
        summary: "Explore the top 5 mental models every PM should master, including First Principles, Inversion, and the Jobs-to-be-Done framework to build better products.",
        imageUrl: null,
        source: "Product Management",
        height: "h-48",
        content: "When analyzing product failures, it's often useful to apply Inversion: ask 'how could we ruin this user experience?' to figure out what not to do. Jobs-to-be-Done focuses on the core reason a customer 'hires' a product, abstracting away from the specific features."
    },
    {
        id: "stream-4",
        title: "The Physics of Data Centers",
        summary: "An exploration of power usage effectiveness (PUE), cooling tower mechanics, and the sheer physical scale required to run modern cloud infrastructure.",
        imageUrl: "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?q=80&w=600&auto=format&fit=crop",
        source: "Infrastructure",
        height: "h-72",
        content: "Data centers consume gigawatts of electricity globally. The primary challenge isn't just powering the servers, but removing the heat they generate. Liquid cooling and innovative heat exchange models are becoming standard."
    },
    {
        id: "stream-5",
        title: "Designing for Attention",
        summary: "How modern interfaces balance information density with cognitive load, employing progressive disclosure and hierarchical typography.",
        imageUrl: null,
        source: "UX Design",
        height: "h-56",
        content: "Attention is a scarce resource. Designing for it means anticipating what the user needs right now and hiding the rest until necessary. Progressive disclosure is a key technique."
    }
]

type QuizType = 'flashcard' | 'single-choice' | 'multiple-choice'

const MOCK_QUIZ_CARDS = [
    {
        id: "quiz-1",
        type: 'flashcard' as QuizType,
        question: "What is the primary difference between zero-shot and few-shot prompting?",
        answer: "Zero-shot prompting provides no examples to the model before requesting a task, relying entirely on its pre-trained knowledge. Few-shot prompting provides a small number of examples (usually 2-5) within the prompt.",
        topic: "Prompt Engineering"
    },
    {
        id: "quiz-2",
        type: 'single-choice' as QuizType,
        question: "In the context of database indexing, what does a B-Tree optimize for?",
        options: [
            "Constant time O(1) lookups for single keys",
            "Minimizing disk I/O operations by storing multiple keys per node",
            "Compressing text data efficiently",
            "Handling exclusively geospatial coordinates"
        ],
        correctOptionIndex: 1,
        topic: "Databases"
    },
    {
        id: "quiz-3",
        type: 'multiple-choice' as QuizType,
        question: "Which of the following are valid React hooks?",
        options: [
            "useFetch",
            "useEffect",
            "useMemo",
            "useState",
            "useComponent"
        ],
        correctOptionIndices: [1, 2, 3],
        topic: "React"
    }
]

export default function GulpPage() {
    // Article Detail Modal State
    const [selectedArticle, setSelectedArticle] = useState<typeof MOCK_STREAM_CARDS[0] | null>(null)

    // Quiz Mode State
    const [isQuizMode, setIsQuizMode] = useState(false)
    const [currentQuizIndex, setCurrentQuizIndex] = useState(0)
    const [isFlashcardFlipped, setIsFlashcardFlipped] = useState(false)
    const [selectedSingleOption, setSelectedSingleOption] = useState<number | null>(null)
    const [selectedMultiOptions, setSelectedMultiOptions] = useState<number[]>([])
    const [showQuizResult, setShowQuizResult] = useState(false)

    // Derived
    const currentQuiz = MOCK_QUIZ_CARDS[currentQuizIndex]

    // --- QUIZ HANDLERS ---
    const handleStartQuiz = () => {
        setIsQuizMode(true)
        setCurrentQuizIndex(0)
        setIsFlashcardFlipped(false)
        setSelectedSingleOption(null)
        setSelectedMultiOptions([])
        setShowQuizResult(false)
    }

    const handleExitQuiz = () => {
        setIsQuizMode(false)
    }

    const handleSelectSingle = (index: number) => {
        if (showQuizResult) return
        setSelectedSingleOption(index)
    }

    const handleSelectMulti = (index: number) => {
        if (showQuizResult) return
        setSelectedMultiOptions(prev =>
            prev.includes(index) ? prev.filter(i => i !== index) : [...prev, index]
        )
    }

    const handleSubmitQuiz = () => {
        setShowQuizResult(true)
    }

    const handleNextQuiz = () => {
        if (currentQuizIndex < MOCK_QUIZ_CARDS.length - 1) {
            setCurrentQuizIndex(prev => prev + 1)
            setIsFlashcardFlipped(false)
            setSelectedSingleOption(null)
            setSelectedMultiOptions([])
            setShowQuizResult(false)
        } else {
            // Finished
            setIsQuizMode(false)
        }
    }

    const renderQuizContent = () => {
        if (!currentQuiz) {
            return (
                <div className="flex flex-col items-center justify-center p-12 text-center h-[400px]">
                    <CheckCircle2 className="h-12 w-12 text-emerald-500 mb-4" />
                    <h3 className="text-xl font-bold text-zinc-800">All caught up!</h3>
                    <p className="text-zinc-500 mt-2">You've completed your daily knowledge review.</p>
                    <Button onClick={handleExitQuiz} className="mt-8 rounded-full bg-zinc-900 text-white hover:bg-zinc-800">
                        Finish
                    </Button>
                </div>
            )
        }

        if (currentQuiz.type === 'flashcard') {
            return (
                <div className="flex flex-col h-full w-full max-w-2xl mx-auto">
                    <div className="mb-6 flex items-center justify-between px-2">
                        <Badge variant="outline" className="text-zinc-500 border-zinc-200 bg-white/50 uppercase tracking-wider text-[10px] font-bold">
                            {currentQuiz.topic}
                        </Badge>
                        <span className="text-xs font-bold text-zinc-400">{currentQuizIndex + 1} of {MOCK_QUIZ_CARDS.length}</span>
                    </div>

                    <div
                        className={`relative w-full flex-1 perspective-1000 cursor-pointer transition-all duration-500 transform-style-3d ${isFlashcardFlipped ? 'rotate-y-180' : ''}`}
                        onClick={() => setIsFlashcardFlipped(!isFlashcardFlipped)}
                    >
                        {/* Front */}
                        <div className="absolute inset-0 backface-hidden flex flex-col items-center justify-center p-10 bg-white border border-zinc-200 rounded-[2rem] shadow-xl shadow-zinc-200/50 hover:shadow-2xl transition-shadow">
                            <Zap className="h-10 w-10 text-amber-500 mb-8" />
                            <h3 className="text-3xl font-bold text-center text-zinc-900 leading-snug">{currentQuiz.question}</h3>
                            <p className="absolute bottom-8 text-sm text-zinc-400 font-semibold flex items-center gap-2">
                                Click to reveal answer <ArrowRight className="h-4 w-4" />
                            </p>
                        </div>

                        {/* Back */}
                        <div className="absolute inset-0 backface-hidden rotate-y-180 flex flex-col items-center justify-center p-10 bg-zinc-900 border border-zinc-800 rounded-[2rem] shadow-2xl">
                            <h3 className="text-xl font-medium text-zinc-400 mb-6 uppercase tracking-widest text-center">Answer</h3>
                            <p className="text-2xl text-zinc-100 leading-relaxed text-center font-medium max-w-xl">{currentQuiz.answer}</p>

                            <div className="absolute bottom-8 flex gap-4 w-full px-10 justify-center">
                                <Button
                                    onClick={handleNextQuiz}
                                    className="bg-white text-zinc-900 hover:bg-zinc-100 rounded-full px-12 h-14 font-bold text-lg shadow-xl hover:scale-105 transition-transform"
                                >
                                    {currentQuizIndex === MOCK_QUIZ_CARDS.length - 1 ? 'Finish' : 'Got it, Next'}
                                </Button>
                            </div>
                        </div>
                    </div>
                </div>
            )
        }

        return (
            <div className="flex flex-col h-full w-full max-w-2xl mx-auto">
                <div className="mb-6 flex items-center justify-between px-2">
                    <Badge variant="outline" className="text-zinc-500 border-zinc-200 bg-white/50 uppercase tracking-wider text-[10px] font-bold">
                        {currentQuiz.topic} · {currentQuiz.type === 'single-choice' ? 'Single Choice' : 'Multiple Choice'}
                    </Badge>
                    <span className="text-xs font-bold text-zinc-400">{currentQuizIndex + 1} of {MOCK_QUIZ_CARDS.length}</span>
                </div>

                <div className="flex flex-col h-full bg-white border border-zinc-200 rounded-[2rem] shadow-xl shadow-zinc-200/50 p-10">
                    <h3 className="text-2xl font-bold text-zinc-900 mb-10 leading-snug">{currentQuiz.question}</h3>

                    <div className="flex flex-col gap-4 flex-1 overflow-y-auto pr-2 pb-4">
                        {currentQuiz.options?.map((option, index) => {
                            const isSingle = currentQuiz.type === 'single-choice'
                            const isSelected = isSingle ? selectedSingleOption === index : selectedMultiOptions.includes(index)

                            let optionStyle = "border-zinc-200 bg-white hover:border-zinc-300 hover:bg-zinc-50"
                            if (isSelected) optionStyle = "border-zinc-900 bg-zinc-50 ring-2 ring-zinc-900"

                            // If show result, highlight correct/incorrect
                            if (showQuizResult) {
                                const isCorrectAnswer = isSingle
                                    ? index === currentQuiz.correctOptionIndex
                                    : currentQuiz.correctOptionIndices?.includes(index)

                                if (isCorrectAnswer) {
                                    optionStyle = "border-emerald-500 bg-emerald-50 text-emerald-900 ring-2 ring-emerald-500"
                                } else if (isSelected && !isCorrectAnswer) {
                                    optionStyle = "border-red-300 bg-red-50 text-red-900 opacity-60 ring-2 ring-red-300"
                                } else {
                                    optionStyle = "border-zinc-200 bg-white opacity-40"
                                }
                            }

                            return (
                                <div
                                    key={index}
                                    onClick={() => isSingle ? handleSelectSingle(index) : handleSelectMulti(index)}
                                    className={`flex items-center gap-4 p-5 rounded-2xl border-2 cursor-pointer transition-all ${optionStyle}`}
                                >
                                    <div className={`flex items-center justify-center shrink-0 w-7 h-7 rounded-full border-2 ${isSingle ? 'rounded-full' : 'rounded-md'} ${isSelected ? 'border-zinc-900 bg-zinc-900 text-white' : 'border-zinc-300'} ${showQuizResult && (isSingle ? index === currentQuiz.correctOptionIndex : currentQuiz.correctOptionIndices?.includes(index)) ? 'border-emerald-500 bg-emerald-500 text-white' : ''}`}>
                                        {isSelected && !showQuizResult && <div className={`w-2.5 h-2.5 bg-white ${isSingle ? 'rounded-full' : 'rounded-sm'}`} />}
                                        {showQuizResult && (isSingle ? index === currentQuiz.correctOptionIndex : currentQuiz.correctOptionIndices?.includes(index)) && <CheckCircle2 className="w-5 h-5 text-white" />}
                                        {showQuizResult && isSelected && !(isSingle ? index === currentQuiz.correctOptionIndex : currentQuiz.correctOptionIndices?.includes(index)) && <X className="w-5 h-5 text-white" />}
                                    </div>
                                    <span className={`text-[17px] font-semibold leading-tight ${showQuizResult && (isSingle ? index === currentQuiz.correctOptionIndex : currentQuiz.correctOptionIndices?.includes(index)) ? 'text-emerald-900' : 'text-zinc-800'}`}>
                                        {option}
                                    </span>
                                </div>
                            )
                        })}
                    </div>

                    <div className="pt-8 mt-auto flex justify-end">
                        {!showQuizResult ? (
                            <Button
                                onClick={handleSubmitQuiz}
                                disabled={currentQuiz.type === 'single-choice' ? selectedSingleOption === null : selectedMultiOptions.length === 0}
                                className="bg-zinc-900 text-white hover:bg-zinc-800 rounded-full px-10 h-14 text-lg font-bold shadow-md"
                            >
                                Check Answer
                            </Button>
                        ) : (
                            <Button
                                onClick={handleNextQuiz}
                                className="bg-zinc-900 text-white hover:bg-zinc-800 rounded-full px-10 h-14 text-lg font-bold shadow-md gap-2"
                            >
                                Continue <ChevronRight className="w-5 h-5" />
                            </Button>
                        )}
                    </div>
                </div>
            </div>
        )
    }

    return (
        <div className="h-full flex flex-col p-8 bg-transparent max-w-7xl mx-auto w-full relative">

            {/* Header */}
            <div className="flex items-center justify-between mb-8 pb-6 border-b border-border/50 shrink-0">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight text-zinc-900 drop-shadow-sm flex items-center gap-3">
                        Gulp Stream
                    </h1>
                    <p className="text-zinc-500 mt-2 text-sm font-medium">Your personalized, bite-sized knowledge feed.</p>
                </div>

                <Button
                    onClick={handleStartQuiz}
                    className="gap-2 rounded-full px-6 h-11 bg-zinc-900 text-white hover:bg-zinc-800 shadow-lg shadow-zinc-900/10 cursor-pointer overflow-hidden group relative"
                >
                    <div className="absolute inset-0 bg-gradient-to-r from-blue-500/0 via-blue-500/20 to-blue-500/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000" />
                    <span className="font-bold tracking-wide">Start Test</span>
                    <Badge className="ml-1 bg-white/20 hover:bg-white/20 text-white border-none px-1.5 rounded-full text-[10px] font-bold">12</Badge>
                </Button>
            </div>

            {/* Main Content Area: Either Stream or Article Detail */}
            {!selectedArticle ? (
                /* Masonry Info Stream Area */
                <div className="flex-1 overflow-y-auto pb-32 pr-4 custom-scrollbar">
                    <div className="columns-1 md:columns-2 lg:columns-3 xl:columns-4 gap-6 space-y-6">
                        {MOCK_STREAM_CARDS.map((card) => (
                            <Card
                                key={card.id}
                                onClick={() => setSelectedArticle(card)}
                                className="break-inside-avoid bg-white border border-zinc-200 shadow-sm hover:shadow-md transition-all duration-300 overflow-hidden rounded-[24px] cursor-pointer group flex flex-col"
                            >
                                {/* Image Header */}
                                {card.imageUrl ? (
                                    <div className={`w-full bg-zinc-100 relative ${card.height} overflow-hidden`}>
                                        <div className="absolute inset-0 bg-cover bg-center transition-transform duration-700 group-hover:scale-105" style={{ backgroundImage: `url(${card.imageUrl})` }} />
                                        <div className="absolute top-4 left-4">
                                            <Badge className="bg-black/40 backdrop-blur-md text-white border-none shadow-sm font-bold uppercase tracking-wider text-[10px] px-3 py-1">
                                                {card.source}
                                            </Badge>
                                        </div>
                                    </div>
                                ) : (
                                    <div className="p-4 pb-0">
                                        <Badge variant="outline" className="bg-zinc-50 border-zinc-200 text-zinc-600 shadow-sm font-bold uppercase tracking-wider text-[10px] px-3 py-1">
                                            {card.source}
                                        </Badge>
                                    </div>
                                )}

                                {/* Content */}
                                <CardContent className="p-6">
                                    <h3 className="text-[19px] font-bold text-zinc-900 leading-snug mb-3 tracking-tight group-hover:text-blue-600 transition-colors">
                                        {card.title}
                                    </h3>
                                    <p className="text-[14px] font-medium text-zinc-500 leading-relaxed line-clamp-4">
                                        {card.summary}
                                    </p>
                                </CardContent>
                                <CardFooter className="p-6 pt-0 mt-auto flex items-center justify-between text-zinc-400">
                                    <div className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider">
                                        <Sparkles className="w-3.5 h-3.5" /> Generated
                                    </div>
                                    <ArrowRight className="w-4 h-4 opacity-0 group-hover:opacity-100 -translate-x-2 group-hover:translate-x-0 transition-all text-blue-600" />
                                </CardFooter>
                            </Card>
                        ))}
                    </div>
                </div>
            ) : (
                /* INLINE ARTICLE DETAIL VIEW */
                <div className="flex-1 overflow-y-auto pb-32 pr-4 custom-scrollbar flex flex-col items-center animate-in fade-in slide-in-from-bottom-4 duration-300">
                    <div className="w-full max-w-3xl flex flex-col">
                        <div className="mb-6">
                            <Button
                                variant="ghost"
                                onClick={() => setSelectedArticle(null)}
                                className="text-zinc-500 hover:text-zinc-900 hover:bg-zinc-100 -ml-4 gap-2 font-medium"
                            >
                                <ArrowRight className="w-4 h-4 rotate-180" /> Back to Stream
                            </Button>
                        </div>

                        <div className="bg-white rounded-[2rem] shadow-sm border border-zinc-200 overflow-hidden flex flex-col">
                            {/* Article Header/Image */}
                            {selectedArticle?.imageUrl && (
                                <div className="h-72 w-full relative shrink-0">
                                    <div className="absolute inset-0 bg-cover bg-center" style={{ backgroundImage: `url(${selectedArticle.imageUrl})` }} />
                                    <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/10 to-transparent" />
                                </div>
                            )}

                            {/* Article Content */}
                            <div className="p-10 md:p-14 flex flex-col">
                                <div className={`flex gap-2 mb-6 ${selectedArticle?.imageUrl ? '-mt-16 relative z-10' : ''}`}>
                                    <Badge className="bg-blue-600 hover:bg-blue-700 text-white border-none shadow-md font-bold uppercase tracking-wider text-[11px] px-4 py-1.5">
                                        {selectedArticle?.source}
                                    </Badge>
                                </div>

                                <h2 className="text-4xl md:text-5xl font-extrabold text-zinc-900 leading-tight mb-8 tracking-tight">
                                    {selectedArticle?.title}
                                </h2>

                                <div className="prose prose-zinc prose-lg max-w-none prose-p:font-medium prose-p:leading-relaxed prose-p:text-zinc-600">
                                    <p className="text-xl font-semibold text-zinc-800 border-l-4 border-zinc-200 pl-6 py-1 mb-10">
                                        {selectedArticle?.summary}
                                    </p>
                                    <p className="text-lg">
                                        {selectedArticle?.content}
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* QUIZ MODAL */}
            {
                isQuizMode && (
                    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-zinc-50/95 backdrop-blur-xl animate-in fade-in duration-300">

                        <div className="absolute top-8 right-8 z-[110]">
                            <Button
                                variant="outline"
                                onClick={handleExitQuiz}
                                className="bg-white border-zinc-200 text-zinc-600 hover:bg-zinc-100 hover:text-zinc-900 rounded-full h-12 px-6 shadow-sm gap-2 font-bold uppercase text-[11px] tracking-wider"
                            >
                                <X className="w-4 h-4" /> Exit Test
                            </Button>
                        </div>

                        <div className="w-full h-full flex flex-col pt-24 pb-12 px-8 overflow-y-auto">
                            {renderQuizContent()}
                        </div>
                    </div>
                )
            }

            {/* Global CSS for 3D flip effect and animations */}
            <style dangerouslySetInnerHTML={{
                __html: `
                .perspective-1000 {
                    perspective: 1000px;
                }
                .transform-style-3d {
                    transform-style: preserve-3d;
                }
                .backface-hidden {
                    backface-visibility: hidden;
                }
                .rotate-y-180 {
                    transform: rotateY(180deg);
                }
                .custom-scrollbar::-webkit-scrollbar {
                    width: 6px;
                }
                .custom-scrollbar::-webkit-scrollbar-track {
                    background: transparent;
                }
                .custom-scrollbar::-webkit-scrollbar-thumb {
                    background-color: #e4e4e7;
                    border-radius: 20px;
                }
            `}} />
        </div>
    )
}
