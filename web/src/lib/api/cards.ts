import { fetchClient } from "./client";

export async function deleteCard(cardId: string): Promise<void> {
    const res = await fetchClient(`/cards/${cardId}`, {
        method: "DELETE",
    });

    if (!res.ok) {
        throw new Error("Failed to delete card");
    }
}
