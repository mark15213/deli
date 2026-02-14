import SwiftUI

// MARK: - Colors

enum DeliColors {
    static let accent = Color.blue
    #if os(iOS)
    static let background = Color(.systemBackground)
    static let secondaryBackground = Color(.secondarySystemBackground)
    static let inputBackground = Color(.systemGray6)
    #else
    static let background = Color(nsColor: .windowBackgroundColor)
    static let secondaryBackground = Color(nsColor: .controlBackgroundColor)
    static let inputBackground = Color(nsColor: .controlBackgroundColor)
    #endif
    static let cardBackground = Color.white

    // Review ratings
    static let again = Color.red
    static let hard = Color.orange
    static let good = Color.blue
    static let easy = Color.green

    // Card type gradients
    static func cardGradient(for type: CardType) -> [Color] {
        switch type {
        case .mcq, .quiz:
            [Color.blue.opacity(0.15), Color.purple.opacity(0.1)]
        case .cloze:
            [Color.orange.opacity(0.15), Color.yellow.opacity(0.1)]
        case .flashcard:
            [Color.green.opacity(0.15), Color.teal.opacity(0.1)]
        case .note, .readingNote:
            [Color.indigo.opacity(0.15), Color.blue.opacity(0.1)]
        case .code:
            [Color.gray.opacity(0.2), Color.black.opacity(0.1)]
        case .trueFalse:
            [Color.pink.opacity(0.15), Color.red.opacity(0.1)]
        }
    }
}

// MARK: - Typography

enum DeliFont {
    static func title(_ size: CGFloat = 28) -> Font {
        .system(size: size, weight: .bold, design: .rounded)
    }

    static func cardQuestion(_ type: CardType) -> Font {
        type == .cloze
            ? .system(.title2, design: .serif)
            : .system(.title2, design: .rounded)
    }

    static let body = Font.system(.body, design: .rounded)
    static let caption = Font.caption
    static let captionBold = Font.caption.weight(.bold)
    static let badge = Font.caption2.weight(.bold)
}

// MARK: - Dimensions

enum DeliDimensions {
    static let cardCornerRadius: CGFloat = 24
    static let buttonCornerRadius: CGFloat = 12
    static let inputCornerRadius: CGFloat = 12
    static let badgeCornerRadius: CGFloat = 6
    static let cardWidth: CGFloat = 320
    static let cardHeight: CGFloat = 480
    static let cardShadowRadius: CGFloat = 10
    static let cardShadowY: CGFloat = 5
}
