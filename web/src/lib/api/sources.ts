import { DetectRequest, DetectResponse, Source } from "@/types/source";

export type { Source } from "@/types/source";

// Base API URL - assuming standard setup, adjust if env var needed
const API_BASE_URL = "/api";

export async function detectSource(input: string): Promise<DetectResponse> {
    const res = await fetch(`${API_BASE_URL}/sources/detect`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ input, check_connectivity: true } as DetectRequest),
    });

    if (!res.ok) {
        throw new Error("Failed to detect source type");
    }

    return res.json();
}

export async function getSources(): Promise<Source[]> {
    const res = await fetch(`${API_BASE_URL}/sources/`, {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
        },
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

    const res = await fetch(`${API_BASE_URL}/sources/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
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

    const res = await fetch(`${API_BASE_URL}/sources/${sourceId}/upload`, {
        method: "POST",
        body: formData,
    });

    if (!res.ok) {
        const error = await res.json().catch(() => ({ detail: "Upload failed" }));
        throw new Error(error.detail || "Failed to upload document");
    }

    return res.json();
}

