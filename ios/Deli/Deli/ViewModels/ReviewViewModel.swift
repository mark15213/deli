import Foundation

@Observable
class ReviewViewModel {
    var quizzes: [Quiz] = []
    
    init() {
        // Load dummy data for prototype
        loadDummyData()
    }
    
    func loadDummyData() {
        self.quizzes = [
            Quiz(
                id: UUID(),
                type: .mcq,
                question: "What is the primary function of Python's 'GIL'?",
                options: [
                    "Global Interpreter Lock",
                    "General Instruction List",
                    "Generic Interface Layer"
                ],
                answer: "Global Interpreter Lock",
                explanation: "The GIL matches access to Python objects, preventing multiple threads from executing Python bytecodes at once.",
                sourcePageTitle: "Python Concurrency",
                tags: ["Python", "Concurrency"]
            ),
            Quiz(
                id: UUID(),
                type: .mcq,
                question: "Which hook is used for side effects in React?",
                options: [
                    "useState",
                    "useEffect",
                    "useContext"
                ],
                answer: "useEffect",
                explanation: "useEffect is designed to handle side effects like data fetching, subscriptions, etc.",
                sourcePageTitle: "React Hooks",
                tags: ["React", "Frontend"]
            ),
             Quiz(
                id: UUID(),
                type: .mcq,
                question: "In SQL, which key uniquely identifies a record?",
                options: [
                    "Foreign Key",
                    "Primary Key",
                    "Unique Key"
                ],
                answer: "Primary Key",
                explanation: "A Primary Key is a unique identifier for each record in a database table.",
                sourcePageTitle: "Database Basics",
                tags: ["SQL", "Database"]
            ),
            Quiz(
                id: UUID(),
                type: .trueFalse,
                question: "Swift is a statically typed language.",
                options: nil, // Options handled by trueFalseView
                answer: "True",
                explanation: "Swift performs type checks at compile time.",
                sourcePageTitle: "Swift Basics",
                tags: ["Swift"]
            ),
            Quiz(
                id: UUID(),
                type: .cloze,
                question: "The capital of France is {{c1::Paris}}.",
                options: nil,
                answer: "Paris",
                explanation: "Paris is the capital and most populous city of France.",
                sourcePageTitle: "Geography",
                tags: ["General"]
            )
        ]
    }
    
    func removeTopCard() {
        if !quizzes.isEmpty {
            quizzes.removeFirst()
        }
    }
}
