import Foundation

// MARK: - Card Types

enum CardType: String, Codable, Sendable {
    case mcq
    case cloze
    case code
    case note
    case readingNote = "reading_note"
    case flashcard
    case quiz
    case trueFalse = "true_false"
}

// MARK: - Study Card (from /study/queue and /study/gulp)

struct StudyCard: Identifiable, Codable, Sendable {
    let id: UUID
    let type: CardType
    let question: String
    let answer: String?
    let options: [String]?
    let explanation: String?
    let images: [String]?
    let tags: [String]
    let sourceTitle: String?
    let deckIds: [UUID]?
    let deckTitles: [String]?
    let batchId: UUID?
    let batchIndex: Int?
    let batchTotal: Int?

    enum CodingKeys: String, CodingKey {
        case id, type, question, answer, options, explanation, images, tags
        case sourceTitle = "source_title"
        case deckIds = "deck_ids"
        case deckTitles = "deck_titles"
        case batchId = "batch_id"
        case batchIndex = "batch_index"
        case batchTotal = "batch_total"
    }
}

// MARK: - Gulp Card (extends StudyCard with bookmark info)

struct GulpCard: Identifiable, Codable, Sendable {
    let id: UUID
    let type: CardType
    let question: String
    let answer: String?
    let options: [String]?
    let explanation: String?
    let images: [String]?
    let tags: [String]
    let sourceTitle: String?
    let sourceUrl: String?
    var isBookmarked: Bool
    let batchId: UUID?
    let batchIndex: Int?
    let batchTotal: Int?

    enum CodingKeys: String, CodingKey {
        case id, type, question, answer, options, explanation, images, tags
        case sourceTitle = "source_title"
        case sourceUrl = "source_url"
        case isBookmarked = "is_bookmarked"
        case batchId = "batch_id"
        case batchIndex = "batch_index"
        case batchTotal = "batch_total"
    }
}

// MARK: - Gulp Feed Response

struct GulpFeed: Codable, Sendable {
    let cards: [GulpCard]
    let total: Int
    let hasMore: Bool

    enum CodingKeys: String, CodingKey {
        case cards, total
        case hasMore = "has_more"
    }
}

// MARK: - Review

enum Rating: Int, Codable, Sendable {
    case again = 1
    case hard = 2
    case good = 3
    case easy = 4
}

struct ReviewRequest: Codable, Sendable {
    let rating: Int
}

struct ReviewResponse: Codable, Sendable {
    let cardId: UUID
    let nextReviewAt: String
    let intervalDays: Double
    let newState: String

    enum CodingKeys: String, CodingKey {
        case cardId = "card_id"
        case nextReviewAt = "next_review_at"
        case intervalDays = "interval_days"
        case newState = "new_state"
    }
}

// MARK: - Auth

struct LoginRequest: Codable, Sendable {
    let email: String
    let password: String
}

struct RegisterRequest: Codable, Sendable {
    let email: String
    let password: String
    let inviteCode: String

    enum CodingKeys: String, CodingKey {
        case email, password
        case inviteCode = "invite_code"
    }
}

struct TokenResponse: Codable, Sendable {
    let accessToken: String
    let tokenType: String
    let refreshToken: String
    let userId: UUID?
    let email: String?

    enum CodingKeys: String, CodingKey {
        case accessToken = "access_token"
        case tokenType = "token_type"
        case refreshToken = "refresh_token"
        case userId = "user_id"
        case email
    }
}

struct RefreshRequest: Codable, Sendable {
    let refreshToken: String

    enum CodingKeys: String, CodingKey {
        case refreshToken = "refresh_token"
    }
}

struct UserProfile: Codable, Identifiable, Sendable {
    let id: UUID
    let email: String
    let username: String?
    let avatarUrl: String?
    let createdAt: String?

    enum CodingKeys: String, CodingKey {
        case id, email, username
        case avatarUrl = "avatar_url"
        case createdAt = "created_at"
    }
}

// MARK: - Stats

struct StudyStats: Codable, Sendable {
    let todayReviewed: Int
    let todayRemaining: Int
    let streakDays: Int
    let totalMastered: Int
    let totalCards: Int?

    enum CodingKeys: String, CodingKey {
        case todayReviewed = "today_reviewed"
        case todayRemaining = "today_remaining"
        case streakDays = "streak_days"
        case totalMastered = "total_mastered"
        case totalCards = "total_cards"
    }
}

// MARK: - Bookmark

struct BookmarkResponse: Codable, Identifiable, Sendable {
    let id: UUID
    let cardId: UUID
    let cardType: String
    let cardQuestion: String
    let cardAnswer: String?
    let sourceTitle: String?
    let note: String?
    let createdAt: String

    enum CodingKeys: String, CodingKey {
        case id
        case cardId = "card_id"
        case cardType = "card_type"
        case cardQuestion = "card_question"
        case cardAnswer = "card_answer"
        case sourceTitle = "source_title"
        case note
        case createdAt = "created_at"
    }
}

// MARK: - Paper Group

struct PaperGroup: Codable, Identifiable, Sendable {
    var id: UUID { sourceId }
    let sourceId: UUID
    let sourceTitle: String
    let sourceUrl: String?
    let sourceType: String?
    let summary: String?
    let cardCount: Int
    let cards: [StudyCard]

    enum CodingKeys: String, CodingKey {
        case sourceId = "source_id"
        case sourceTitle = "source_title"
        case sourceUrl = "source_url"
        case sourceType = "source_type"
        case summary
        case cardCount = "card_count"
        case cards
    }
}
