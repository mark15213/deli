import Foundation

@Observable
class GulpViewModel {
    var cards: [GulpCard] = []
    var isLoading = false
    var hasMore = true
    var error: String?
    private var offset = 0
    private let limit = 30

    private let api = APIClient.shared

    func loadFeed(reset: Bool = false) async {
        if reset {
            offset = 0
            hasMore = true
        }
        guard hasMore, !isLoading else { return }
        isLoading = true
        error = nil
        do {
            let feed = try await api.gulpFeed(limit: limit, offset: offset)
            if reset {
                cards = feed.cards
            } else {
                cards.append(contentsOf: feed.cards)
            }
            hasMore = feed.hasMore
            offset += feed.cards.count
        } catch let err as APIError {
            error = err.errorDescription
        } catch {
            self.error = error.localizedDescription
        }
        isLoading = false
    }

    func toggleBookmark(card: GulpCard) async {
        guard let idx = cards.firstIndex(where: { $0.id == card.id }) else { return }
        let wasBookmarked = cards[idx].isBookmarked
        cards[idx].isBookmarked.toggle()
        do {
            if wasBookmarked {
                try await api.removeBookmark(cardId: card.id)
            } else {
                _ = try await api.bookmark(cardId: card.id)
            }
        } catch {
            cards[idx].isBookmarked = wasBookmarked
        }
    }
}
