// Study API client

const API_BASE_URL = "/api";

export interface StudyCard {
    id: string;
    type: string;
    question: string;
    answer?: string;
    options?: string[];
    explanation?: string;
    tags: string[];
    source_title?: string;
    deck_ids: string[];
    deck_titles: string[];
}

export interface ReviewResponse {
    card_id: string;
    next_review_at: string;
    interval_days: number;
    new_state: string;
}

export interface StudyStats {
    today_reviewed: number;
    today_remaining: number;
    streak_days: number;
    total_mastered: number;
    total_cards: number;
}

export type Rating = 1 | 2 | 3 | 4; // AGAIN, HARD, GOOD, EASY

export async function getStudyQueue(limit = 20): Promise<StudyCard[]> {
    const res = await fetch(`${API_BASE_URL}/study/queue?limit=${limit}`);

    if (!res.ok) {
        throw new Error("Failed to fetch study queue");
    }

    return res.json();
}

export async function submitReview(cardId: string, rating: Rating): Promise<ReviewResponse> {
    const res = await fetch(`${API_BASE_URL}/study/${cardId}/review`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ rating }),
    });

    if (!res.ok) {
        throw new Error("Failed to submit review");
    }

    return res.json();
}

export async function getStudyStats(): Promise<StudyStats> {
    const res = await fetch(`${API_BASE_URL}/study/stats`);

    if (!res.ok) {
        throw new Error("Failed to fetch study stats");
    }

    return res.json();
}
