"use client";

/**
 * Pipeline list page — shows all system + user pipeline templates.
 * Click to open editor, clone/delete actions.
 */

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import {
    getPipelines,
    clonePipeline,
    deletePipeline,
    createPipeline,
    type PipelineTemplate,
} from "@/lib/api/pipelines";
import {
    Plus,
    Copy,
    Trash2,
    Lock,
    Workflow,
    ChevronRight,
} from "lucide-react";
import { Button } from "@/components/ui/button";

export default function PipelinesPage() {
    const router = useRouter();
    const [pipelines, setPipelines] = useState<PipelineTemplate[]>([]);
    const [loading, setLoading] = useState(true);

    const loadPipelines = async () => {
        try {
            setLoading(true);
            const data = await getPipelines();
            setPipelines(data);
        } catch (e) {
            console.error("Failed to load pipelines", e);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadPipelines();
    }, []);

    const handleCreate = async () => {
        try {
            const newPipeline = await createPipeline({
                name: "New Pipeline",
                description: "",
                definition: { steps: [], edges: [] },
            });
            router.push(`/pipelines/${newPipeline.id}`);
        } catch (e) {
            console.error("Failed to create pipeline", e);
        }
    };

    const handleClone = async (id: string, e: React.MouseEvent) => {
        e.stopPropagation();
        try {
            const cloned = await clonePipeline(id);
            router.push(`/pipelines/${cloned.id}`);
        } catch (err) {
            console.error("Failed to clone pipeline", err);
        }
    };

    const handleDelete = async (id: string, e: React.MouseEvent) => {
        e.stopPropagation();
        if (!confirm("Delete this pipeline?")) return;
        try {
            await deletePipeline(id);
            loadPipelines();
        } catch (err) {
            console.error("Failed to delete pipeline", err);
        }
    };

    const systemPipelines = pipelines.filter((p) => p.is_system);
    const userPipelines = pipelines.filter((p) => !p.is_system);

    return (
        <div className="flex flex-col h-full bg-slate-50/50 dark:bg-zinc-950">
            {/* Header */}
            <div className="flex items-center justify-between px-8 py-6 border-b bg-card">
                <div>
                    <h1 className="text-2xl font-bold tracking-tight">Pipelines</h1>
                    <p className="text-muted-foreground mt-1">
                        Visual processing workflows for your sources
                    </p>
                </div>
                <Button onClick={handleCreate}>
                    <Plus className="h-4 w-4 mr-2" />
                    New Pipeline
                </Button>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-8 space-y-8">
                {loading ? (
                    <div className="text-center text-muted-foreground py-10">
                        Loading pipelines…
                    </div>
                ) : (
                    <>
                        {/* System Templates */}
                        {systemPipelines.length > 0 && (
                            <section>
                                <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-3 flex items-center gap-2">
                                    <Lock className="h-3.5 w-3.5" />
                                    System Templates
                                </h2>
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                    {systemPipelines.map((p) => (
                                        <PipelineCard
                                            key={p.id}
                                            pipeline={p}
                                            onClick={() => router.push(`/pipelines/${p.id}`)}
                                            onClone={(e) => handleClone(p.id, e)}
                                        />
                                    ))}
                                </div>
                            </section>
                        )}

                        {/* User Pipelines */}
                        <section>
                            <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-3">
                                My Pipelines
                            </h2>
                            {userPipelines.length === 0 ? (
                                <div className="text-center text-muted-foreground py-10 border-2 border-dashed rounded-lg">
                                    <Workflow className="h-10 w-10 mx-auto mb-3 opacity-30" />
                                    <p className="text-sm">No custom pipelines yet.</p>
                                    <p className="text-xs mt-1">
                                        Clone a system template or create a new one.
                                    </p>
                                </div>
                            ) : (
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                    {userPipelines.map((p) => (
                                        <PipelineCard
                                            key={p.id}
                                            pipeline={p}
                                            onClick={() => router.push(`/pipelines/${p.id}`)}
                                            onClone={(e) => handleClone(p.id, e)}
                                            onDelete={(e) => handleDelete(p.id, e)}
                                        />
                                    ))}
                                </div>
                            )}
                        </section>
                    </>
                )}
            </div>
        </div>
    );
}

// ─── Card Component ──────────────────────────────────────────────────

function PipelineCard({
    pipeline,
    onClick,
    onClone,
    onDelete,
}: {
    pipeline: PipelineTemplate;
    onClick: () => void;
    onClone: (e: React.MouseEvent) => void;
    onDelete?: (e: React.MouseEvent) => void;
}) {
    const stepCount = pipeline.definition?.steps?.length || 0;
    const opCount = (pipeline.definition?.steps || []).reduce(
        (sum, s) => sum + (s.operators?.length || 0), 0
    );

    return (
        <div
            onClick={onClick}
            className="
        group relative border rounded-xl bg-card p-4
        hover:border-primary/30 hover:shadow-md
        transition-all cursor-pointer
      "
        >
            {/* System badge */}
            {pipeline.is_system && (
                <div className="absolute top-3 right-3">
                    <Lock className="h-3.5 w-3.5 text-amber-500" />
                </div>
            )}

            <div className="flex items-start gap-3">
                <div className="p-2 rounded-lg bg-primary/10 text-primary">
                    <Workflow className="h-5 w-5" />
                </div>
                <div className="flex-1 min-w-0">
                    <h3 className="font-medium text-sm truncate">{pipeline.name}</h3>
                    {pipeline.description && (
                        <p className="text-xs text-muted-foreground mt-0.5 line-clamp-2">
                            {pipeline.description}
                        </p>
                    )}
                    <div className="flex items-center gap-3 mt-2 text-xs text-muted-foreground">
                        <span>{stepCount} steps</span>
                        <span>{opCount} operators</span>
                    </div>
                </div>
            </div>

            {/* Actions */}
            <div className="flex items-center justify-between mt-3 pt-3 border-t">
                <div className="flex gap-1">
                    <button
                        onClick={onClone}
                        className="p-1.5 rounded-md hover:bg-muted text-muted-foreground hover:text-foreground transition-colors"
                        title="Clone"
                    >
                        <Copy className="h-3.5 w-3.5" />
                    </button>
                    {onDelete && (
                        <button
                            onClick={onDelete}
                            className="p-1.5 rounded-md hover:bg-destructive/10 text-muted-foreground hover:text-destructive transition-colors"
                            title="Delete"
                        >
                            <Trash2 className="h-3.5 w-3.5" />
                        </button>
                    )}
                </div>
                <ChevronRight className="h-4 w-4 text-muted-foreground group-hover:text-primary transition-colors" />
            </div>
        </div>
    );
}
