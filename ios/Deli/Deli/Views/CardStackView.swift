import SwiftUI

struct CardStackView: View {
    @Bindable var viewModel: ReviewViewModel

    var body: some View {
        VStack {
            HStack {
                Text("Today's Review")
                    .font(.largeTitle)
                    .fontWeight(.bold)
                Spacer()
                Text("\(viewModel.cards.count)")
                    .font(.title2)
                    .padding()
                    .background(Circle().fill(Color.blue.opacity(0.1)))
            }
            .padding()

            if let stats = viewModel.stats {
                HStack(spacing: 24) {
                    statBadge(label: "Reviewed", value: "\(stats.todayReviewed)")
                    statBadge(label: "Streak", value: "\(stats.streakDays)d")
                    statBadge(label: "Mastered", value: "\(stats.totalMastered)")
                }
                .padding(.horizontal)
            }

            ZStack {
                if viewModel.isLoading && viewModel.cards.isEmpty {
                    ProgressView()
                } else if viewModel.cards.isEmpty {
                    VStack(spacing: 12) {
                        Image(systemName: "checkmark.circle")
                            .font(.system(size: 48))
                            .foregroundStyle(.green)
                        Text("All done for today!")
                            .font(.title2)
                            .foregroundStyle(.secondary)
                    }
                } else {
                    ForEach(viewModel.cards.suffix(3).reversed()) { card in
                        CardView(card: card) { rating in
                            Task {
                                await viewModel.submitReview(cardId: card.id, rating: rating)
                            }
                        }
                    }
                }
            }
            .padding()

            Spacer()

            if let error = viewModel.error {
                Text(error)
                    .font(.caption)
                    .foregroundStyle(.red)
                    .padding()
            }

            if !viewModel.cards.isEmpty {
                HStack(spacing: 20) {
                    reviewButton(rating: .again, icon: "xmark", color: .red, label: "Again")
                    reviewButton(rating: .hard, icon: "tortoise", color: .orange, label: "Hard")
                    reviewButton(rating: .good, icon: "hand.thumbsup", color: .blue, label: "Good")
                    reviewButton(rating: .easy, icon: "checkmark", color: .green, label: "Easy")
                }
                .padding(.bottom)
            }
        }
        .task {
            await viewModel.loadQueue()
            await viewModel.loadStats()
        }
    }

    private func reviewButton(rating: Rating, icon: String, color: Color, label: String) -> some View {
        Button {
            guard let card = viewModel.cards.first else { return }
            Task { await viewModel.submitReview(cardId: card.id, rating: rating) }
        } label: {
            VStack(spacing: 4) {
                Image(systemName: icon)
                    .font(.system(size: 20, weight: .bold))
                Text(label)
                    .font(.caption2)
            }
            .foregroundStyle(color)
            .frame(width: 56, height: 56)
            .background(Circle().stroke(color, lineWidth: 2))
        }
    }

    private func statBadge(label: String, value: String) -> some View {
        VStack(spacing: 2) {
            Text(value)
                .font(.headline)
            Text(label)
                .font(.caption2)
                .foregroundStyle(.secondary)
        }
    }
}
