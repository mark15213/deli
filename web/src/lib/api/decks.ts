import { fetchClient } from "./client";

export interface Deck {
    id: string;
    title: string;
    description?: string;
    is_public: boolean;
    cover_image_url?: string;
    card_count: number;
    mastery_percent: number;
    is_subscribed: boolean;
    last_review_at?: string;
    created_at: string;
}

export interface CardInDeck {
    id: string;
    type: string;
    question: string;
    status: string;
    tags: string[];
    source_title?: string;
    created_at: string;
}

export interface DeckDetail extends Deck {
    cards: CardInDeck[];
}

export interface CreateDeckRequest {
    title: string;
    description?: string;
    is_public?: boolean;
}

export async function getDecks(subscribedOnly = false): Promise<Deck[]> {
    const url = subscribedOnly
        ? `/decks?subscribed_only=true`
        : `/decks`;

    const res = await fetchClient(url);

    if (!res.ok) {
        throw new Error("Failed to fetch decks");
    }

    return res.json();
}

export async function getDeck(deckId: string): Promise<DeckDetail> {
    const res = await fetchClient(`/decks/${deckId}`);

    if (!res.ok) {
        throw new Error("Failed to fetch deck");
    }

    return res.json();
}

export async function createDeck(data: CreateDeckRequest): Promise<Deck> {
    const res = await fetchClient(`/decks`, {
        method: "POST",
        body: JSON.stringify(data),
    });

    if (!res.ok) {
        throw new Error("Failed to create deck");
    }

    return res.json();
}

export async function updateDeck(deckId: string, data: Partial<CreateDeckRequest>): Promise<Deck> {
    const res = await fetchClient(`/decks/${deckId}`, {
        method: "PUT",
        body: JSON.stringify(data),
    });

    if (!res.ok) {
        throw new Error("Failed to update deck");
    }

    return res.json();
}

export async function deleteDeck(deckId: string): Promise<void> {
    const res = await fetchClient(`/decks/${deckId}`, {
        method: "DELETE",
    });

    if (!res.ok) {
        throw new Error("Failed to delete deck");
    }
}

export async function subscribeToDeck(deckId: string): Promise<void> {
    const res = await fetchClient(`/decks/${deckId}/subscribe`, {
        method: "POST",
    });

    if (!res.ok) {
        throw new Error("Failed to subscribe to deck");
    }
}

export async function unsubscribeFromDeck(deckId: string): Promise<void> {
    const res = await fetchClient(`/decks/${deckId}/subscribe`, {
        method: "DELETE",
    });

    if (!res.ok) {
        throw new Error("Failed to unsubscribe from deck");
    }
}
