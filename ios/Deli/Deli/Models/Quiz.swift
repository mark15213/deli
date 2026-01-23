import Foundation

enum QuizType: String, Codable {
    case mcq
    case trueFalse = "true_false"
    case cloze
}

enum QuizStatus: String, Codable {
    case pending
    case approved
    case rejected
}

struct Quiz: Identifiable, Codable {
    let id: UUID
    let type: QuizType
    let question: String
    let options: [String]?
    let answer: String
    let explanation: String?
    let sourcePageTitle: String?
    let tags: [String]?
    
    // Coding keys if JSON snake_case differs from camelCase
    enum CodingKeys: String, CodingKey {
        case id, type, question, options, answer, explanation, tags
        case sourcePageTitle = "source_page_title"
    }
}
