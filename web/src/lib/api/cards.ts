const API_BASE_URL = "/api";

export async function deleteCard(cardId: string): Promise<void> {
    const res = await fetch(`${API_BASE_URL}/cards/${cardId}`, {
        method: "DELETE",
    });

    if (!res.ok) {
        throw new Error("Failed to delete card");
    }
}
