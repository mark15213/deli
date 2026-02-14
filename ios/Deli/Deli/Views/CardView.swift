import SwiftUI
import WebKit
#if canImport(UIKit)
import UIKit
#elseif canImport(AppKit)
import AppKit
#endif

struct CardView: View {
    let card: StudyCard
    @State private var isFlipped = false
    @State private var offset = CGSize.zero
    @State private var selectedOption: String?
    @State private var clozeInput: String = ""
    @FocusState private var isInputFocused: Bool

    var onReview: ((Rating) -> Void)?

    var body: some View {
        ZStack {
            frontView
                .opacity(isFlipped ? 0 : 1)

            backView
                .rotation3DEffect(.degrees(180), axis: (x: 0, y: 1, z: 0))
                .opacity(isFlipped ? 1 : 0)
        }
        .id(card.id)
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
                }
                .onEnded { _ in
                    withAnimation {
                        handleSwipe(width: offset.width)
                    }
                }
        )
        .onTapGesture {
            hideKeyboard()
            withAnimation(.spring()) {
                isFlipped.toggle()
            }
        }
        .onDisappear {
            hideKeyboard()
        }
    }

    var frontView: some View {
        VStack(alignment: .leading, spacing: 20) {
            HStack {
                Text(card.type.rawValue.uppercased())
                    .font(.caption)
                    .fontWeight(.bold)
                    .padding(5)
                    .background(Color.gray.opacity(0.2))
                    .cornerRadius(5)
                Spacer()
                ForEach(card.tags.prefix(2), id: \.self) { tag in
                    Text("#\(tag)")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
            }

            if let batch = card.batchIndex, let total = card.batchTotal {
                Text("\(batch)/\(total)")
                    .font(.caption2)
                    .foregroundStyle(.tertiary)
            }

            Spacer()

            if card.type == .cloze {
                Text(maskedClozeQuestion)
                    .font(DeliFont.cardQuestion(card.type))
                    .fontWeight(.medium)
                    .multilineTextAlignment(.leading)
                    .layoutPriority(1)
            } else {
                MarkdownView(card.question, fontSize: 20)
                    .frame(maxHeight: 200)
                    .layoutPriority(1)
            }

            Group {
                if card.type == .cloze {
                    clozeView
                } else if card.type == .trueFalse {
                    trueFalseView
                } else if card.type == .mcq {
                    if let options = card.options {
                        mcqOptionsView(options: options)
                    }
                }
            }

            Spacer()

            Text(selectedOption == nil ? "Tap to flip (or select answer)" : "Tap to flip")
                .font(.caption)
                .foregroundStyle(.secondary)
                .frame(maxWidth: .infinity, alignment: .center)
        }
        .padding()
        .background(DeliColors.cardBackground)
        .cornerRadius(DeliDimensions.cardCornerRadius)
        .shadow(color: Color.black.opacity(0.1), radius: DeliDimensions.cardShadowRadius, x: 0, y: DeliDimensions.cardShadowY)
    }

    var backView: some View {
        VStack(alignment: .leading, spacing: 20) {
            Text("ANSWER")
                .font(.caption)
                .fontWeight(.bold)
                .foregroundStyle(.green)

            if let answer = card.answer {
                MarkdownView(answer, fontSize: 20)
                    .frame(maxHeight: 180)
            }

            if let explanation = card.explanation {
                Divider()
                Text("Explanation")
                    .font(.headline)
                MarkdownView(explanation, fontSize: 15)
                    .frame(maxHeight: 160)
            }

            Spacer()
        }
        .padding()
        .background(DeliColors.cardBackground)
        .cornerRadius(DeliDimensions.cardCornerRadius)
        .shadow(color: Color.black.opacity(0.1), radius: DeliDimensions.cardShadowRadius, x: 0, y: DeliDimensions.cardShadowY)
    }

    func mcqOptionsView(options: [String]) -> some View {
        ScrollView {
            VStack(spacing: 12) {
                ForEach(options, id: \.self) { option in
                    mcqOptionRow(option: option)
                }
            }
            .padding(.horizontal, 4)
        }
    }

    func mcqOptionRow(option: String) -> some View {
        Button {
            if selectedOption == nil {
                selectedOption = option
            }
        } label: {
            HStack {
                Text(option)
                    .font(.system(.body, design: .rounded))
                    .fontWeight(.medium)
                    .foregroundStyle(.primary)
                    .multilineTextAlignment(.leading)
                Spacer()
                if selectedOption == option {
                    if option == card.answer {
                        Image(systemName: "checkmark.circle.fill")
                            .foregroundStyle(.green)
                    } else {
                        Image(systemName: "xmark.circle.fill")
                            .foregroundStyle(.red)
                    }
                }
            }
            .padding()
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(
                        selectedOption == option
                            ? (option == card.answer ? Color.green.opacity(0.15) : Color.red.opacity(0.15))
                            : Color.gray.opacity(0.05)
                    )
            )
            .overlay(
                RoundedRectangle(cornerRadius: 12)
                    .stroke(
                        selectedOption == option
                            ? (option == card.answer ? Color.green : Color.red)
                            : Color.gray.opacity(0.2),
                        lineWidth: selectedOption == option ? 2 : 1
                    )
            )
            .scaleEffect(selectedOption == option ? 1.02 : 1.0)
            .animation(.spring(response: 0.3, dampingFraction: 0.6), value: selectedOption)
        }
        .buttonStyle(PlainButtonStyle())
        .disabled(selectedOption != nil)
    }

    var trueFalseView: some View {
        VStack(spacing: 12) {
            mcqOptionRow(option: "True")
            mcqOptionRow(option: "False")
        }
    }

    @ViewBuilder
    var clozeView: some View {
        VStack(spacing: 16) {
            Text("Type your answer:")
                .font(.caption)
                .foregroundStyle(.secondary)

            HStack {
                TextField("Tap to type answer", text: $clozeInput)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                    .focused($isInputFocused)
                    .disabled(isFlipped || selectedOption != nil)
                    .padding(.vertical, 8)

                Button {
                    hideKeyboard()
                    let isCorrect = clozeInput.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
                        == (card.answer ?? "").trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
                    selectedOption = isCorrect ? card.answer : "WRONG_ANSWER"
                } label: {
                    Text("Check")
                        .fontWeight(.bold)
                        .foregroundStyle(.white)
                        .frame(height: 36)
                        .padding(.horizontal, 16)
                        .background(Color.blue)
                        .cornerRadius(8)
                }
                .buttonStyle(.plain)
                .disabled(clozeInput.isEmpty || selectedOption != nil)
            }

            if let selected = selectedOption {
                HStack {
                    if selected == card.answer {
                        Image(systemName: "checkmark.circle.fill")
                            .foregroundStyle(.green)
                        Text("Correct!")
                            .foregroundStyle(.green)
                            .fontWeight(.bold)
                    } else {
                        Image(systemName: "xmark.circle.fill")
                            .foregroundStyle(.red)
                        Text("Incorrect")
                            .foregroundStyle(.red)
                            .fontWeight(.bold)
                    }
                }
            }
        }
    }

    var maskedClozeQuestion: String {
        let pattern = "\\{\\{c\\d+::(.*?)(::.*?)?\\}\\}"
        var text = card.question
        if let regex = try? NSRegularExpression(pattern: pattern) {
            let range = NSRange(location: 0, length: text.utf16.count)
            text = regex.stringByReplacingMatches(in: text, range: range, withTemplate: "[...]")
        }
        return text
    }

    func handleSwipe(width: CGFloat) {
        switch width {
        case -500...(-150):
            offset = CGSize(width: -500, height: 0)
            hideKeyboard()
            onReview?(.again)
        case 150...500:
            offset = CGSize(width: 500, height: 0)
            hideKeyboard()
            onReview?(.good)
        default:
            offset = .zero
        }
    }

    private func hideKeyboard() {
        isInputFocused = false
        #if canImport(UIKit)
        UIApplication.shared.sendAction(#selector(UIResponder.resignFirstResponder), to: nil, from: nil, for: nil)
        #elseif canImport(AppKit)
        NSApplication.shared.keyWindow?.makeFirstResponder(nil)
        #endif
    }
}
