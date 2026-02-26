"use client";

/**
 * Pipeline editor page — loads a single pipeline template and renders the canvas.
 */

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import {
    getPipeline,
    clonePipeline,
    type PipelineTemplate,
} from "@/lib/api/pipelines";
import { PipelineCanvas } from "@/components/pipeline/PipelineCanvas";
import { ArrowLeft, Loader2 } from "lucide-react";

export default function PipelineEditorPage() {
    const params = useParams();
    const router = useRouter();
    const id = params.id as string;

    const [pipeline, setPipeline] = useState<PipelineTemplate | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!id) return;
        setLoading(true);
        getPipeline(id)
            .then(setPipeline)
            .catch((err) => setError(err.message))
            .finally(() => setLoading(false));
    }, [id]);

    const handleClone = async () => {
        if (!pipeline) return;
        try {
            const cloned = await clonePipeline(pipeline.id);
            router.push(`/pipelines/${cloned.id}`);
        } catch (err) {
            console.error("Failed to clone:", err);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-full">
                <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
            </div>
        );
    }

    if (error || !pipeline) {
        return (
            <div className="flex flex-col items-center justify-center h-full gap-4">
                <p className="text-destructive">
                    {error || "Pipeline not found"}
                </p>
                <button
                    onClick={() => router.push("/pipelines")}
                    className="text-sm text-primary hover:underline flex items-center gap-1"
                >
                    <ArrowLeft className="h-4 w-4" />
                    Back to Pipelines
                </button>
            </div>
        );
    }

    return (
        <div className="flex flex-col h-full">
            {/* Back nav */}
            <div className="flex items-center gap-2 px-4 py-2 border-b bg-card">
                <button
                    onClick={() => router.push("/pipelines")}
                    className="text-muted-foreground hover:text-foreground transition-colors p-1 rounded-md hover:bg-muted"
                >
                    <ArrowLeft className="h-4 w-4" />
                </button>
                <span className="text-xs text-muted-foreground">
                    Pipelines / {pipeline.name}
                </span>
            </div>

            {/* Canvas */}
            <div className="flex-1 overflow-hidden">
                <PipelineCanvas pipeline={pipeline} onClone={handleClone} />
            </div>
        </div>
    );
}
