/**
 * Pipeline API client — maps to /api/v1/pipelines endpoints
 */
import { fetchClient } from "./client";

// ─── Types ───────────────────────────────────────────────────────────

export interface OpRefDef {
    id: string;
    operator_key: string;
    config_overrides: Record<string, any>;
}

export interface StepDef {
    key: string;
    label: string;
    operators: OpRefDef[];
    position: { x: number; y: number };
}

export interface EdgeDef {
    id: string;
    source_op: string;
    source_port: string;
    target_op: string;
    target_port: string;
}

export interface PipelineDefinition {
    steps: StepDef[];
    edges: EdgeDef[];
}

export interface PipelineTemplate {
    id: string;
    user_id: string | null;
    name: string;
    description: string;
    is_system: boolean;
    definition: PipelineDefinition;
    created_at: string;
    updated_at: string;
}

export interface PortDef {
    key: string;
    type: string;
    description: string;
    required: boolean;
}

export interface OperatorManifest {
    key: string;
    name: string;
    kind: "llm" | "tool";
    description: string;
    input_ports: PortDef[];
    output_ports: PortDef[];
}

// ─── API Functions ───────────────────────────────────────────────────

export async function getPipelines(): Promise<PipelineTemplate[]> {
    const res = await fetchClient("/pipelines");
    if (!res.ok) throw new Error("Failed to fetch pipelines");
    return res.json();
}

export async function getPipeline(id: string): Promise<PipelineTemplate> {
    const res = await fetchClient(`/pipelines/${id}`);
    if (!res.ok) throw new Error("Failed to fetch pipeline");
    return res.json();
}

export async function createPipeline(body: {
    name: string;
    description?: string;
    definition?: PipelineDefinition;
}): Promise<PipelineTemplate> {
    const res = await fetchClient("/pipelines", {
        method: "POST",
        body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error("Failed to create pipeline");
    return res.json();
}

export async function updatePipeline(
    id: string,
    body: {
        name?: string;
        description?: string;
        definition?: PipelineDefinition;
    }
): Promise<PipelineTemplate> {
    const res = await fetchClient(`/pipelines/${id}`, {
        method: "PUT",
        body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error("Failed to update pipeline");
    return res.json();
}

export async function deletePipeline(id: string): Promise<void> {
    const res = await fetchClient(`/pipelines/${id}`, { method: "DELETE" });
    if (!res.ok) throw new Error("Failed to delete pipeline");
}

export async function clonePipeline(id: string): Promise<PipelineTemplate> {
    const res = await fetchClient(`/pipelines/${id}/clone`, {
        method: "POST",
    });
    if (!res.ok) throw new Error("Failed to clone pipeline");
    return res.json();
}

export async function getOperators(): Promise<OperatorManifest[]> {
    const res = await fetchClient("/pipelines/operators/list");
    if (!res.ok) throw new Error("Failed to fetch operators");
    return res.json();
}
