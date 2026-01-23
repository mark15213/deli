import SwiftUI

struct CardView: View {
    let quiz: Quiz
    @State private var isFlipped = false
    @State private var offset = CGSize.zero
    @State private var color: Color = .white
    
    var onRemove: (() -> Void)?
    
    var body: some View {
        ZStack {
            // Front (Question)
            VStack(alignment: .leading, spacing: 20) {
                HStack {
                    Text(quiz.type.rawValue.uppercased())
                        .font(.caption)
                        .fontWeight(.bold)
                        .padding(5)
                        .background(Color.gray.opacity(0.2))
                        .cornerRadius(5)
                    Spacer()
                    if let tags = quiz.tags {
                        ForEach(tags.prefix(2), id: \.self) { tag in
                            Text("#\(tag)")
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                    }
                }
                
                Spacer()
                
                Text(quiz.question)
                    .font(.title2)
                    .fontWeight(.semibold)
                    .multilineTextAlignment(.leading)
                
                Spacer()
                
                Text("Tap to flip")
                    .font(.caption)
                    .foregroundColor(.secondary)
                    .frame(maxWidth: .infinity, alignment: .center)
            }
            .padding()
            .background(Color.white)
            .cornerRadius(20)
            .shadow(radius: 5)
            .opacity(isFlipped ? 0 : 1)
            
            // Back (Answer)
            VStack(alignment: .leading, spacing: 20) {
                Text("ANSWER")
                    .font(.caption)
                    .fontWeight(.bold)
                    .foregroundColor(.green)
                
                Text(quiz.answer)
                    .font(.title2)
                    .fontWeight(.bold)
                
                if let explanation = quiz.explanation {
                    Divider()
                    Text("Explanation")
                        .font(.headline)
                    Text(explanation)
                        .font(.body)
                        .foregroundColor(.secondary)
                }
                
                Spacer()
            }
            .padding()
            .background(Color.white)
            .cornerRadius(20)
            .shadow(radius: 5)
            .rotation3DEffect(.degrees(180), axis: (x: 0, y: 1, z: 0))
            .opacity(isFlipped ? 1 : 0)
        }
        .frame(width: 320, height: 480)
        .rotation3DEffect(
            .degrees(isFlipped ? 180 : 0),
            axis: (x: 0, y: 1, z: 0)
        )
        .offset(x: offset.width, y: offset.height * 0.4)
        .rotationEffect(.degrees(Double(offset.width / 20)))
        .gesture(
            DragGesture()
                .onChanged { gesture in
                    offset = gesture.translation
                    withAnimation {
                        changeColor(width: offset.width)
                    }
                }
                .onEnded { _ in
                    withAnimation {
                        handleSwipe(width: offset.width)
                    }
                }
        )
        .onTapGesture {
            withAnimation(.spring()) {
                isFlipped.toggle()
            }
        }
    }
    
    func changeColor(width: CGFloat) {
        switch width {
        case -500...(-100):
            color = .red
        case 100...500:
            color = .green
        default:
            color = .white
        }
    }
    
    func handleSwipe(width: CGFloat) {
        switch width {
        case -500...(-150):
            // Forgot (Left)
            offset = CGSize(width: -500, height: 0)
            onRemove?()
        case 150...500:
            // Knew (Right)
            offset = CGSize(width: 500, height: 0)
            onRemove?()
        default:
            // Reset
            offset = .zero
            color = .white
        }
    }
}
