import { fetchClient } from "./client";

// --- Types ---

export interface EditorContent {
    source_id: string;
    source_title: string;
    source_url?: string;
    content: Record<string, unknown>; // Tiptap JSON
    plain_text?: string;
    updated_at?: string;
}

export interface Annotation {
    id: string;
    type: "highlight" | "comment";
    color?: string;
    anchor: { from: number; to: number };
    body?: string;
    resolved: boolean;
    created_at: string;
    updated_at: string;
}

export interface ShareLink {
    token: string;
    url: string;
    include_annotations: boolean;
    is_active: boolean;
    view_count: number;
}

export interface SharedContent {
    source_title: string;
    source_url?: string;
    content: Record<string, unknown>;
    annotations: Annotation[];
    view_count: number;
}

export interface ImageUploadResult {
    url: string;
    filename: string;
}

// --- Editor Content ---

export async function getEditorContent(sourceId: string): Promise<EditorContent> {
    const res = await fetchClient(`/editor/${sourceId}`);
    if (!res.ok) throw new Error("Failed to fetch editor content");
    return res.json();
}

export async function saveEditorContent(
    sourceId: string,
    content: Record<string, unknown>,
    plainText?: string
): Promise<EditorContent> {
    const res = await fetchClient(`/editor/${sourceId}`, {
        method: "PUT",
        body: JSON.stringify({ content, plain_text: plainText }),
    });
    if (!res.ok) throw new Error("Failed to save editor content");
    return res.json();
}

// --- Images ---

export async function uploadEditorImage(
    sourceId: string,
    file: File
): Promise<ImageUploadResult> {
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetchClient(`/editor/${sourceId}/images`, {
        method: "POST",
        body: formData,
    });
    if (!res.ok) throw new Error("Failed to upload image");
    return res.json();
}

export async function deleteEditorImage(
    sourceId: string,
    filename: string
): Promise<void> {
    const res = await fetchClient(`/editor/${sourceId}/images/${filename}`, {
        method: "DELETE",
    });
    if (!res.ok) throw new Error("Failed to delete image");
}

// --- Annotations ---

export async function getAnnotations(sourceId: string): Promise<Annotation[]> {
    const res = await fetchClient(`/editor/${sourceId}/annotations`);
    if (!res.ok) throw new Error("Failed to fetch annotations");
    return res.json();
}

export async function createAnnotation(
    sourceId: string,
    data: { type: string; color?: string; anchor: { from: number; to: number }; body?: string }
): Promise<Annotation> {
    const res = await fetchClient(`/editor/${sourceId}/annotations`, {
        method: "POST",
        body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error("Failed to create annotation");
    return res.json();
}

export async function updateAnnotation(
    sourceId: string,
    annotationId: string,
    data: Partial<Annotation>
): Promise<Annotation> {
    const res = await fetchClient(`/editor/${sourceId}/annotations/${annotationId}`, {
        method: "PUT",
        body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error("Failed to update annotation");
    return res.json();
}

export async function deleteAnnotation(
    sourceId: string,
    annotationId: string
): Promise<void> {
    const res = await fetchClient(`/editor/${sourceId}/annotations/${annotationId}`, {
        method: "DELETE",
    });
    if (!res.ok) throw new Error("Failed to delete annotation");
}

// --- Share Links ---

export async function createShareLink(sourceId: string): Promise<ShareLink> {
    const res = await fetchClient(`/editor/${sourceId}/share`, {
        method: "POST",
    });
    if (!res.ok) throw new Error("Failed to create share link");
    const data: ShareLink = await res.json();
    // Construct URL on the client so it works in any environment
    data.url = `${window.location.origin}/shared/${data.token}`;
    return data;
}

export async function revokeShareLink(sourceId: string): Promise<void> {
    const res = await fetchClient(`/editor/${sourceId}/share`, {
        method: "DELETE",
    });
    if (!res.ok) throw new Error("Failed to revoke share link");
}

// --- Public Shared Content (no auth needed) ---

export async function getSharedContent(token: string): Promise<SharedContent> {
    const res = await fetch(`/api/shared/${token}`);
    if (!res.ok) throw new Error("Shared content not found");
    return res.json();
}
