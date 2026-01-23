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
                Text("\(viewModel.quizzes.count)")
                    .font(.title2)
                    .padding()
                    .background(Circle().fill(Color.blue.opacity(0.1)))
            }
            .padding()
            
            ZStack {
                if viewModel.quizzes.isEmpty {
                    Text("No usage for today! 🎉")
                        .font(.title)
                        .foregroundColor(.secondary)
                } else {
                    ForEach(viewModel.quizzes.reversed()) { quiz in
                        CardView(quiz: quiz) {
                            withAnimation {
                                viewModel.removeTopCard()
                            }
                        }
                    }
                }
            }
            .padding()
            
            Spacer()
            
            // Interaction buttons (for accessibility/alternate control)
            if !viewModel.quizzes.isEmpty {
                HStack(spacing: 50) {
                    Button(action: { /* logic for manual forgot */ }) {
                        Image(systemName: "xmark")
                            .font(.system(size: 24, weight: .bold))
                            .foregroundColor(.red)
                            .padding()
                            .background(Circle().stroke(Color.red, lineWidth: 2))
                    }
                    
                    Button(action: { /* logic for manual knew */ }) {
                        Image(systemName: "checkmark")
                            .font(.system(size: 24, weight: .bold))
                            .foregroundColor(.green)
                            .padding()
                            .background(Circle().stroke(Color.green, lineWidth: 2))
                    }
                }
                .padding(.bottom)
            }
        }
    }
}

#Preview {
    CardStackView(viewModel: ReviewViewModel())
}
