import Foundation

@Observable
class ReviewViewModel {
    var cards: [StudyCard] = []
    var isLoading = false
    var error: String?
    var stats: StudyStats?

    private let api = APIClient.shared

    func loadQueue() async {
        isLoading = true
        error = nil
        do {
            cards = try await api.studyQueue()
        } catch let err as APIError {
            error = err.errorDescription
        } catch {
            self.error = error.localizedDescription
        }
        isLoading = false
    }

    func loadStats() async {
        do {
            stats = try await api.studyStats()
        } catch {}
    }

    func submitReview(cardId: UUID, rating: Rating) async {
        do {
            _ = try await api.submitReview(cardId: cardId, rating: rating)
            cards.removeAll { $0.id == cardId }
            await loadStats()
        } catch let err as APIError {
            error = err.errorDescription
        } catch {
            self.error = error.localizedDescription
        }
    }

    func skipBatch(batchId: UUID) async {
        do {
            try await api.skipBatch(batchId: batchId)
            cards.removeAll { $0.batchId == batchId }
        } catch {}
    }

    func removeTopCard() {
        guard !cards.isEmpty else { return }
        cards.removeFirst()
    }
}
