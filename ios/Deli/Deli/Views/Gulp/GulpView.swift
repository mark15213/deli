import SwiftUI
import WebKit

struct GulpView: View {
    @State private var viewModel = GulpViewModel()
    @State private var currentIndex = 0

    var body: some View {
        GeometryReader { geo in
            if viewModel.isLoading && viewModel.cards.isEmpty {
                ProgressView()
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
            } else if viewModel.cards.isEmpty {
                VStack(spacing: 16) {
                    Image(systemName: "tray")
                        .font(.system(size: 48))
                        .foregroundStyle(.secondary)
                    Text("No cards yet")
                        .font(.title3)
                        .foregroundStyle(.secondary)
                    Text("Cards from your sources will appear here")
                        .font(.subheadline)
                        .foregroundStyle(.tertiary)
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity)
            } else {
                TabView(selection: $currentIndex) {
                    ForEach(Array(viewModel.cards.enumerated()), id: \.element.id) { index, card in
                        GulpCardView(card: card) {
                            Task { await viewModel.toggleBookmark(card: card) }
                        }
                        .frame(width: geo.size.width, height: geo.size.height)
                        .tag(index)
                    }
                }
                .tabViewStyle(.page(indexDisplayMode: .never))
                .ignoresSafeArea()
                .onChange(of: currentIndex) { _, newVal in
                    if newVal >= viewModel.cards.count - 5 {
                        Task { await viewModel.loadFeed() }
                    }
                }
            }
        }
        .task { await viewModel.loadFeed(reset: true) }
    }
}

// MARK: - Single Gulp Card (full-screen)

struct GulpCardView: View {
    let card: GulpCard
    var onBookmarkTap: () -> Void

    @State private var showAnswer = false

    var body: some View {
        ZStack {
            // Background gradient based on card type
            cardGradient
                .ignoresSafeArea()

            VStack(alignment: .leading, spacing: 0) {
                Spacer()

                // Card content
                VStack(alignment: .leading, spacing: 16) {
                    // Type badge + source
                    HStack {
                        Text(card.type.rawValue.uppercased())
                            .font(.caption2)
                            .fontWeight(.bold)
                            .padding(.horizontal, 8)
                            .padding(.vertical, 4)
                            .background(.ultraThinMaterial)
                            .cornerRadius(6)

                        Spacer()

                        if let src = card.sourceTitle {
                            Text(src)
                                .font(.caption)
                                .foregroundStyle(.secondary)
                                .lineLimit(1)
                        }
                    }

                    // Question (Markdown)
                    if card.type == .cloze {
                        Text(displayQuestion)
                            .font(.title3)
                            .fontWeight(.semibold)
                            .fixedSize(horizontal: false, vertical: true)
                    } else {
                        MarkdownView(card.question, fontSize: 18)
                            .frame(maxHeight: 200)
                    }

                    // Options for MCQ
                    if card.type == .mcq, let options = card.options {
                        VStack(spacing: 8) {
                            ForEach(options, id: \.self) { opt in
                                HStack {
                                    Text(opt)
                                        .font(.subheadline)
                                    Spacer()
                                    if showAnswer && opt == card.answer {
                                        Image(systemName: "checkmark.circle.fill")
                                            .foregroundStyle(.green)
                                    }
                                }
                                .padding(12)
                                .background(.ultraThinMaterial)
                                .cornerRadius(10)
                            }
                        }
                    }

                    // Answer reveal
                    if showAnswer, let answer = card.answer {
                        VStack(alignment: .leading, spacing: 8) {
                            Divider()
                            if card.type != .mcq {
                                MarkdownView(answer, fontSize: 15)
                                    .frame(maxHeight: 160)
                            }
                            if let explanation = card.explanation {
                                MarkdownView(explanation, fontSize: 14)
                                    .frame(maxHeight: 120)
                            }
                        }
                    }

                    // Tags
                    if !card.tags.isEmpty {
                        HStack {
                            ForEach(card.tags.prefix(3), id: \.self) { tag in
                                Text("#\(tag)")
                                    .font(.caption)
                                    .foregroundStyle(.secondary)
                            }
                        }
                    }
                }
                .padding(20)
                .background(.ultraThinMaterial)
                .cornerRadius(20)
                .padding(.horizontal, 16)

                // Action bar
                HStack(spacing: 32) {
                    Spacer()

                    Button { showAnswer.toggle() } label: {
                        VStack(spacing: 4) {
                            Image(systemName: showAnswer ? "eye.slash" : "eye")
                                .font(.title2)
                            Text(showAnswer ? "Hide" : "Reveal")
                                .font(.caption2)
                        }
                    }

                    Button(action: onBookmarkTap) {
                        VStack(spacing: 4) {
                            Image(systemName: card.isBookmarked ? "bookmark.fill" : "bookmark")
                                .font(.title2)
                                .foregroundStyle(card.isBookmarked ? .yellow : .primary)
                            Text("Save")
                                .font(.caption2)
                        }
                    }

                    Spacer()
                }
                .foregroundStyle(.primary)
                .padding(.vertical, 20)
            }
            .padding(.bottom, 40)
        }
    }

    private var displayQuestion: String {
        if card.type == .cloze {
            let pattern = "\\{\\{c\\d+::(.*?)(::.*?)?\\}\\}"
            var text = card.question
            if let regex = try? NSRegularExpression(pattern: pattern) {
                let range = NSRange(location: 0, length: text.utf16.count)
                text = regex.stringByReplacingMatches(in: text, range: range, withTemplate: showAnswer ? "$1" : "[...]")
            }
            return text
        }
        return card.question
    }

    private var cardGradient: some View {
        LinearGradient(
            colors: gradientColors,
            startPoint: .topLeading,
            endPoint: .bottomTrailing
        )
    }

    private var gradientColors: [Color] {
        DeliColors.cardGradient(for: card.type)
    }
}
