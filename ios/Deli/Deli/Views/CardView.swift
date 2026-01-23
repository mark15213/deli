import SwiftUI
#if canImport(UIKit)
import UIKit
#elseif canImport(AppKit)
import AppKit
#endif

struct CardView: View {
    let quiz: Quiz
    @State private var isFlipped = false
    @State private var offset = CGSize.zero
    @State private var color: Color = .white
    @State private var selectedOption: String?
    @State private var clozeInput: String = ""
    @FocusState private var isInputFocused: Bool
    
    var onRemove: (() -> Void)?
    
    var body: some View {
        ZStack {
            frontView
                .opacity(isFlipped ? 0 : 1)
            
            backView
                .rotation3DEffect(.degrees(180), axis: (x: 0, y: 1, z: 0))
                .opacity(isFlipped ? 1 : 0)
        }
        .id(quiz.id) // Force redraw when quiz changes to avoid view recycling issues
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
            hideKeyboard()
            withAnimation(.spring()) {
                if !isFlipped {
                    // Only allow flip if answer selected? No, allowed to peek.
                }
                isFlipped.toggle()
            }
        }
        .onDisappear {
            hideKeyboard()
        }
        .onChange(of: quiz.id) { _, _ in
            hideKeyboard()
            selectedOption = nil
            clozeInput = ""
            isFlipped = false
            offset = .zero
            color = .white
        }
    }
    
    var frontView: some View {
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
            
            if quiz.type == .cloze {
                Text(maskedClozeQuestion)
                    .font(.system(.title2, design: .serif))
                    .fontWeight(.medium)
                    .multilineTextAlignment(.leading)
                    .layoutPriority(1)
            } else {
                Text(quiz.question)
                    .font(.system(.title2, design: .rounded))
                    .fontWeight(.bold)
                    .multilineTextAlignment(.leading)
                    .layoutPriority(1)
            }
            
            Group {
                if quiz.type == .cloze {
                    clozeView
                } else if quiz.type == .trueFalse {
                    trueFalseView
                } else if quiz.type == .mcq {
                    if let options = quiz.options {
                        mcqOptionsView(options: options)
                    }
                }
            }
            
            Spacer()
            
            Text(selectedOption == nil ? "Tap to flip (or select answer)" : "Tap to flip")
                .font(.caption)
                .foregroundColor(.secondary)
                .frame(maxWidth: .infinity, alignment: .center)
        }
        .padding()
        .background(Color.white)
        .cornerRadius(24)
        .shadow(color: Color.black.opacity(0.1), radius: 10, x: 0, y: 5)
    }
    
    var backView: some View {
        VStack(alignment: .leading, spacing: 20) {
            Text("ANSWER")
                .font(.caption)
                .fontWeight(.bold)
                .foregroundColor(.green)
            
            Text(quiz.answer)
                .font(.system(.title2, design: .rounded))
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
        .cornerRadius(24)
        .shadow(color: Color.black.opacity(0.1), radius: 10, x: 0, y: 5)
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
        Button(action: {
            if selectedOption == nil {
                selectedOption = option
            }
        }) {
            HStack {
                Text(option)
                    .font(.system(.body, design: .rounded))
                    .fontWeight(.medium)
                    .foregroundColor(.primary)
                    .multilineTextAlignment(.leading)
                Spacer()
                if selectedOption == option {
                    if option == quiz.answer {
                        Image(systemName: "checkmark.circle.fill")
                            .foregroundColor(.green)
                    } else {
                        Image(systemName: "xmark.circle.fill")
                            .foregroundColor(.red)
                    }
                }
            }
            .padding()
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(
                        selectedOption == option
                            ? (option == quiz.answer ? Color.green.opacity(0.15) : Color.red.opacity(0.15))
                            : Color.gray.opacity(0.05)
                    )
            )
            .overlay(
                RoundedRectangle(cornerRadius: 12)
                    .stroke(
                        selectedOption == option
                            ? (option == quiz.answer ? Color.green : Color.red)
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
        if quiz.type == .cloze {
            VStack(spacing: 16) {
            Text("Type your answer:")
                .font(.caption)
                .foregroundColor(.secondary)
            
            HStack {
                TextField("Tap to type answer", text: $clozeInput)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                    .focused($isInputFocused)
                    .disabled(isFlipped || (selectedOption != nil)) // Disable if already submitted/checked
                    .padding(.vertical, 8)
                
                Button(action: {
                    // Check answer
                    hideKeyboard()
                    let isCorrect = clozeInput.trimmingCharacters(in: .whitespacesAndNewlines).lowercased() == quiz.answer.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
                    selectedOption = isCorrect ? quiz.answer : "WRONG_ANSWER" // Use a marker for state
                }) {
                    Text("Check")
                        .fontWeight(.bold)
                        .foregroundColor(.white)
                        .frame(height: 36)
                        .padding(.horizontal, 16)
                        .background(Color.blue)
                        .cornerRadius(8)
                }
                .buttonStyle(.plain)
                .disabled(clozeInput.isEmpty || selectedOption != nil)
            }
            
            // Feedback
            if let selected = selectedOption {
                if selected == quiz.answer {
                    HStack {
                        Image(systemName: "checkmark.circle.fill")
                            .foregroundColor(.green)
                        Text("Correct!")
                            .foregroundColor(.green)
                            .fontWeight(.bold)
                    }
                } else {
                    HStack {
                        Image(systemName: "xmark.circle.fill")
                            .foregroundColor(.red)
                        Text("Incorrect")
                            .foregroundColor(.red)
                            .fontWeight(.bold)
                    }
                }
            }
        }
        }
    }
    
    var maskedClozeQuestion: String {
        // Simple regex to replace {{c1::Answer}} with [...]
        // Note: Foundation regex replacement in SwiftUI view computed property might be heavy if list is long,
        // but for a single card it's fine.
        let pattern = "\\{\\{c\\d+::(.*?)(::.*?)?\\}\\}"
        // A naive replacement for now:
        var text = quiz.question
        if let regex = try? NSRegularExpression(pattern: pattern, options: []) {
            let range = NSRange(location: 0, length: text.utf16.count)
            text = regex.stringByReplacingMatches(in: text, options: [], range: range, withTemplate: "[...]")
        }
        return text
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
            hideKeyboard()
            onRemove?()
        case 150...500:
            // Knew (Right)
            offset = CGSize(width: 500, height: 0)
            hideKeyboard()
            onRemove?()
        default:
            // Reset
            offset = .zero
            color = .white
        }
    }
    
    // MARK: - Helpers
    private func hideKeyboard() {
        isInputFocused = false
        #if canImport(UIKit)
        UIApplication.shared.sendAction(#selector(UIResponder.resignFirstResponder), to: nil, from: nil, for: nil)
        #elseif canImport(AppKit)
        NSApplication.shared.keyWindow?.makeFirstResponder(nil)
        #endif
    }
}
