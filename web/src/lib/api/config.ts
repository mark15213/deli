// API Configuration
// Use environment variable in production, fallback to localhost in development

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
export const API_PREFIX = "/api/v1";

export function getApiUrl(path: string): string {
    return `${API_BASE_URL}${API_PREFIX}${path}`;
}
