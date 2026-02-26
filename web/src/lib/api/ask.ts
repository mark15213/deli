import { fetchClient } from "./client";

// --- Types ---

export interface Message {
    role: 'user' | 'assistant';
    content: string;
}

export interface Conversation {
    id: string;
    card_id: string;
    title?: string;
    messages: Message[];
    created_at: string;
    updated_at?: string;
}

export interface AskRequest {
    card_id: string;
    question: string;
    conversation_id?: string;
}

export interface AskResponse {
    answer: string;
    conversation_id: string;
    suggested_card?: {
        question: string;
        answer: string;
    };
}

// --- API Functions ---

export async function askQuestion(request: AskRequest): Promise<AskResponse> {
    const res = await fetchClient(`/ask`, {
        method: "POST",
        body: JSON.stringify(request),
    });

    if (!res.ok) {
        throw new Error("Failed to ask question");
    }

    return res.json();
}

export async function getConversations(): Promise<Conversation[]> {
    const res = await fetchClient(`/ask/conversations`);

    if (!res.ok) {
        throw new Error("Failed to fetch conversations");
    }

    return res.json();
}

export async function getConversation(id: string): Promise<Conversation> {
    const res = await fetchClient(`/ask/conversations/${id}`);

    if (!res.ok) {
        throw new Error("Failed to fetch conversation");
    }

    return res.json();
}

export async function saveConversationAsCard(conversationId: string, messageIndex: number): Promise<void> {
    const res = await fetchClient(`/ask/conversations/${conversationId}/save-card`, {
        method: "POST",
        body: JSON.stringify({ message_index: messageIndex }),
    });

    if (!res.ok) {
        throw new Error("Failed to save as card");
    }
}
