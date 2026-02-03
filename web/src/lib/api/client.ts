const API_BASE_URL = "/api";

interface FetchOptions extends RequestInit {
    headers?: Record<string, string>;
}

export async function fetchClient(endpoint: string, options: FetchOptions = {}) {
    const token = localStorage.getItem("access_token");

    const headers: Record<string, string> = {
        ...options.headers,
    };

    if (!(options.body instanceof FormData)) {
        headers["Content-Type"] = "application/json";
    }

    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    // Ensure endpoint starts with / if not present (optional safety)
    const path = endpoint.startsWith("/") ? endpoint : `/${endpoint}`;

    const response = await fetch(`${API_BASE_URL}${path}`, {
        ...options,
        headers,
    });

    if (response.status === 401) {
        // Optional: Redirect to login or dispatch event
        // window.location.href = "/login"; // Careful with this in SPA
    }

    return response;
}
