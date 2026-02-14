import Foundation

enum APIError: LocalizedError {
    case unauthorized
    case badRequest(String)
    case serverError(Int)
    case networkError(Error)
    case decodingError(Error)

    var errorDescription: String? {
        switch self {
        case .unauthorized: return "Session expired. Please log in again."
        case .badRequest(let msg): return msg
        case .serverError(let code): return "Server error (\(code))"
        case .networkError(let err): return err.localizedDescription
        case .decodingError(let err): return "Data error: \(err.localizedDescription)"
        }
    }
}

actor APIClient {
    static let shared = APIClient()

    #if DEBUG
    private let baseURL = "http://localhost:8000/api/v1"
    #else
    private let baseURL = "https://api.getdeli.app/api/v1"
    #endif

    private var accessToken: String? {
        get { KeychainService.loadString(key: "access_token") }
        set {
            if let v = newValue { KeychainService.saveString(v, key: "access_token") }
            else { KeychainService.delete(key: "access_token") }
        }
    }

    private var refreshToken: String? {
        get { KeychainService.loadString(key: "refresh_token") }
        set {
            if let v = newValue { KeychainService.saveString(v, key: "refresh_token") }
            else { KeychainService.delete(key: "refresh_token") }
        }
    }

    private let decoder: JSONDecoder = {
        let d = JSONDecoder()
        return d
    }()

    private let encoder: JSONEncoder = {
        let e = JSONEncoder()
        return e
    }()

    private var isRefreshing = false

    // MARK: - Auth

    var isLoggedIn: Bool {
        accessToken != nil
    }

    func login(email: String, password: String) async throws -> TokenResponse {
        let body = LoginRequest(email: email, password: password)
        let resp: TokenResponse = try await request(.post, "/auth/login", body: body, auth: false)
        accessToken = resp.accessToken
        refreshToken = resp.refreshToken
        return resp
    }

    func register(email: String, password: String, inviteCode: String) async throws -> UserProfile {
        let body = RegisterRequest(email: email, password: password, inviteCode: inviteCode)
        return try await request(.post, "/auth/register", body: body, auth: false)
    }

    func logout() {
        accessToken = nil
        refreshToken = nil
    }

    func me() async throws -> UserProfile {
        try await request(.get, "/auth/me")
    }

    // MARK: - Study

    func studyQueue(limit: Int = 20) async throws -> [StudyCard] {
        try await request(.get, "/study/queue?limit=\(limit)")
    }

    func studyPapers() async throws -> [PaperGroup] {
        try await request(.get, "/study/papers")
    }

    func submitReview(cardId: UUID, rating: Rating) async throws -> ReviewResponse {
        let body = ReviewRequest(rating: rating.rawValue)
        return try await request(.post, "/study/\(cardId)/review", body: body)
    }

    func studyStats() async throws -> StudyStats {
        try await request(.get, "/study/stats")
    }

    func skipBatch(batchId: UUID) async throws {
        let _: [String: String] = try await request(.post, "/study/skip-batch/\(batchId)")
    }

    // MARK: - Gulp

    func gulpFeed(limit: Int = 30, offset: Int = 0) async throws -> GulpFeed {
        try await request(.get, "/study/gulp?limit=\(limit)&offset=\(offset)")
    }

    // MARK: - Bookmarks

    func bookmark(cardId: UUID, note: String? = nil) async throws -> BookmarkResponse {
        let body: [String: String?] = ["note": note]
        return try await request(.post, "/bookmarks/\(cardId)", body: body)
    }

    func removeBookmark(cardId: UUID) async throws {
        try await requestVoid(.delete, "/bookmarks/\(cardId)")
    }

    func bookmarks() async throws -> [BookmarkResponse] {
        try await request(.get, "/bookmarks")
    }

    // MARK: - Networking Core

    private enum Method: String {
        case get = "GET"
        case post = "POST"
        case delete = "DELETE"
    }

    private func request<T: Decodable>(
        _ method: Method,
        _ path: String,
        body: (any Encodable)? = nil,
        auth: Bool = true
    ) async throws -> T {
        let data = try await rawRequest(method, path, body: body, auth: auth)
        do {
            return try decoder.decode(T.self, from: data)
        } catch {
            throw APIError.decodingError(error)
        }
    }

    private func requestVoid(
        _ method: Method,
        _ path: String,
        body: (any Encodable)? = nil
    ) async throws {
        _ = try await rawRequest(method, path, body: body, auth: true)
    }

    private func rawRequest(
        _ method: Method,
        _ path: String,
        body: (any Encodable)? = nil,
        auth: Bool = true,
        isRetry: Bool = false
    ) async throws -> Data {
        guard let url = URL(string: baseURL + path) else {
            throw APIError.badRequest("Invalid URL")
        }

        var req = URLRequest(url: url)
        req.httpMethod = method.rawValue
        req.setValue("application/json", forHTTPHeaderField: "Content-Type")

        if auth, let token = accessToken {
            req.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }

        if let body {
            req.httpBody = try encoder.encode(body)
        }

        let (data, response): (Data, URLResponse)
        do {
            (data, response) = try await URLSession.shared.data(for: req)
        } catch {
            throw APIError.networkError(error)
        }

        guard let http = response as? HTTPURLResponse else {
            throw APIError.serverError(0)
        }

        switch http.statusCode {
        case 200...204:
            return data
        case 401:
            if !isRetry && auth {
                try await doRefresh()
                return try await rawRequest(method, path, body: body, auth: auth, isRetry: true)
            }
            throw APIError.unauthorized
        case 400...499:
            let msg = (try? JSONDecoder().decode([String: String].self, from: data))?["detail"] ?? "Bad request"
            throw APIError.badRequest(msg)
        default:
            throw APIError.serverError(http.statusCode)
        }
    }

    private func doRefresh() async throws {
        guard !isRefreshing, let rt = refreshToken else {
            throw APIError.unauthorized
        }
        isRefreshing = true
        defer { isRefreshing = false }

        let body = RefreshRequest(refreshToken: rt)
        let resp: TokenResponse = try await request(.post, "/auth/refresh", body: body, auth: false)
        accessToken = resp.accessToken
        refreshToken = resp.refreshToken
    }
}
