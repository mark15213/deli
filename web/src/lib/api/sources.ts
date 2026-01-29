import { DetectRequest, DetectResponse, Source } from "@/types/source";
import { fetchClient } from "./client";

export type { Source } from "@/types/source";

export async function detectSource(input: string): Promise<DetectResponse> {
    const res = await fetchClient(`/sources/detect`, {
        method: "POST",
        body: JSON.stringify({ input, check_connectivity: true } as DetectRequest),
    });

    if (!res.ok) {
        throw new Error("Failed to detect source type");
    }

    return res.json();
}

export async function getSources(): Promise<Source[]> {
    const res = await fetchClient(`/sources/`, {
        method: "GET",
    });

    if (!res.ok) {
        throw new Error("Failed to fetch sources");
    }

    return res.json();
}

export async function createSource(data: Partial<Source>): Promise<Source> {
    // Note: The backend expects specific CreateSchema structure. 
    // Ideally we map `data` to `SourceCreate` structure here if they differ significantly.
    // For now assuming the frontend constructs a compatible object or we pass it through.

    const res = await fetchClient(`/sources/`, {
        method: "POST",
        body: JSON.stringify(data),
    });

    if (!res.ok) {
        throw new Error("Failed to create source");
    }

    return res.json();
}

export interface UploadResult {
    status: string;
    source_material_id: string;
    cards_created: number;
    cards: Array<{
        id: string;
        type: string;
        question: string;
    }>;
}

export async function uploadDocument(sourceId: string, file: File): Promise<UploadResult> {
    const formData = new FormData();
    formData.append("file", file);

    const res = await fetchClient(`/sources/${sourceId}/upload`, {
        method: "POST",
        body: formData,
    });

    if (!res.ok) {
        const error = await res.json().catch(() => ({ detail: "Upload failed" }));
        throw new Error(error.detail || "Failed to upload document");
    }

    return res.json();
}

export async function deleteSource(sourceId: string): Promise<void> {
    const res = await fetchClient(`/sources/${sourceId}`, {
        method: "DELETE",
    });

    if (!res.ok) {
        const error = await res.json().catch(() => ({ detail: "Delete failed" }));
        throw new Error(error.detail || "Failed to delete source");
    }
}
