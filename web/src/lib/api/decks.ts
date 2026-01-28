// Decks API client

const API_BASE_URL = "/api";

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
        ? `${API_BASE_URL}/decks?subscribed_only=true`
        : `${API_BASE_URL}/decks`;

    const res = await fetch(url);

    if (!res.ok) {
        throw new Error("Failed to fetch decks");
    }

    return res.json();
}

export async function getDeck(deckId: string): Promise<DeckDetail> {
    const res = await fetch(`${API_BASE_URL}/decks/${deckId}`);

    if (!res.ok) {
        throw new Error("Failed to fetch deck");
    }

    return res.json();
}

export async function createDeck(data: CreateDeckRequest): Promise<Deck> {
    const res = await fetch(`${API_BASE_URL}/decks`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
    });

    if (!res.ok) {
        throw new Error("Failed to create deck");
    }

    return res.json();
}

export async function updateDeck(deckId: string, data: Partial<CreateDeckRequest>): Promise<Deck> {
    const res = await fetch(`${API_BASE_URL}/decks/${deckId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
    });

    if (!res.ok) {
        throw new Error("Failed to update deck");
    }

    return res.json();
}

export async function deleteDeck(deckId: string): Promise<void> {
    const res = await fetch(`${API_BASE_URL}/decks/${deckId}`, {
        method: "DELETE",
    });

    if (!res.ok) {
        throw new Error("Failed to delete deck");
    }
}

export async function subscribeToDeck(deckId: string): Promise<void> {
    const res = await fetch(`${API_BASE_URL}/decks/${deckId}/subscribe`, {
        method: "POST",
    });

    if (!res.ok) {
        throw new Error("Failed to subscribe to deck");
    }
}

export async function unsubscribeFromDeck(deckId: string): Promise<void> {
    const res = await fetch(`${API_BASE_URL}/decks/${deckId}/subscribe`, {
        method: "DELETE",
    });

    if (!res.ok) {
        throw new Error("Failed to unsubscribe from deck");
    }
}
