import { fetchClient } from "./client";

export interface InboxCardPreview {
    id: string;
    deck_ids: string[];
    type: string;
    question: string;
    status: string;
}

export interface InboxSourceGroup {
    source_id?: string;
    source_title: string;
    source_url?: string;
    source_type?: string;
    notes_count: number;
    flashcards_count: number;
    quizzes_count: number;
    total_count: number;
    cards: InboxCardPreview[];
    created_at: string;
}

export interface InboxItem {
    id: string;
    type: string;
    question: string;
    options?: string[];
    tags: string[];
    created_at: string;
}

export async function getPendingItems(skip = 0, limit = 20): Promise<InboxItem[]> {
    const res = await fetchClient(`/inbox/pending?skip=${skip}&limit=${limit}`);

    if (!res.ok) {
        throw new Error("Failed to fetch pending items");
    }

    return res.json();
}

export async function getPendingBySource(status?: string): Promise<InboxSourceGroup[]> {
    const url = status
        ? `/inbox/sources?status=${status}`
        : `/inbox/sources`;
    const res = await fetchClient(url);

    if (!res.ok) {
        throw new Error("Failed to fetch inbox sources");
    }

    return res.json();
}

export async function approveCard(cardId: string): Promise<void> {
    const res = await fetchClient(`/inbox/${cardId}/approve`, {
        method: "POST",
    });

    if (!res.ok) {
        throw new Error("Failed to approve card");
    }
}

export async function rejectCard(cardId: string): Promise<void> {
    const res = await fetchClient(`/inbox/${cardId}/reject`, {
        method: "POST",
    });

    if (!res.ok) {
        throw new Error("Failed to reject card");
    }
}

export async function addCardToDeck(cardId: string, deckId: string): Promise<void> {
    const res = await fetchClient(`/inbox/${cardId}/decks/${deckId}`, {
        method: "POST",
    });
    if (!res.ok) throw new Error("Failed to add card to deck");
}

export async function removeCardFromDeck(cardId: string, deckId: string): Promise<void> {
    const res = await fetchClient(`/inbox/${cardId}/decks/${deckId}`, {
        method: "DELETE",
    });
    if (!res.ok) throw new Error("Failed to remove card from deck");
}

export async function moveCard(cardId: string, targetDeckId: string): Promise<void> {
    const res = await fetchClient(`/inbox/${cardId}/move`, {
        method: "POST",
        body: JSON.stringify({ target_deck_id: targetDeckId }),
    });

    if (!res.ok) {
        throw new Error("Failed to move card");
    }
}

export async function bulkApprove(cardIds: string[]): Promise<void> {
    const res = await fetchClient(`/inbox/bulk/approve`, {
        method: "POST",
        body: JSON.stringify({ card_ids: cardIds }),
    });

    if (!res.ok) {
        throw new Error("Failed to bulk approve");
    }
}

export async function bulkReject(cardIds: string[]): Promise<void> {
    const res = await fetchClient(`/inbox/bulk/reject`, {
        method: "POST",
        body: JSON.stringify({ card_ids: cardIds }),
    });

    if (!res.ok) {
        throw new Error("Failed to bulk reject");
    }
}

export async function deleteCard(cardId: string): Promise<void> {
    const res = await fetchClient(`/inbox/${cardId}`, {
        method: "DELETE",
    });

    if (!res.ok) {
        throw new Error("Failed to delete card");
    }
}

export async function bulkDelete(cardIds: string[]): Promise<void> {
    const res = await fetchClient(`/inbox/bulk/delete`, {
        method: "POST",
        body: JSON.stringify({ card_ids: cardIds }),
    });

    if (!res.ok) {
        throw new Error("Failed to bulk delete");
    }
}

export async function bulkAddCardToDeck(cardIds: string[], deckId: string): Promise<void> {
    const res = await fetchClient(`/inbox/bulk/add-to-deck`, {
        method: "POST",
        body: JSON.stringify({ card_ids: cardIds, deck_id: deckId }),
    });

    if (!res.ok) {
        throw new Error("Failed to bulk add to deck");
    }
}

export async function bulkRemoveCardFromDeck(cardIds: string[], deckId: string): Promise<void> {
    const res = await fetchClient(`/inbox/bulk/remove-from-deck`, {
        method: "POST",
        body: JSON.stringify({ card_ids: cardIds, deck_id: deckId }),
    });

    if (!res.ok) {
        throw new Error("Failed to bulk remove from deck");
    }
}
