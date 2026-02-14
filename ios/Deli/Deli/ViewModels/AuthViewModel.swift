import Foundation

@Observable
class AuthViewModel {
    var isLoggedIn = false
    var isLoading = false
    var error: String?
    var user: UserProfile?

    private let api = APIClient.shared

    init() {
        Task { await checkSession() }
    }

    func checkSession() async {
        let loggedIn = await api.isLoggedIn
        if loggedIn {
            do {
                user = try await api.me()
                isLoggedIn = true
            } catch {
                isLoggedIn = false
            }
        }
    }

    func login(email: String, password: String) async {
        isLoading = true
        error = nil
        do {
            let resp = try await api.login(email: email, password: password)
            user = UserProfile(id: resp.userId ?? UUID(), email: resp.email ?? email, username: nil, avatarUrl: nil, createdAt: nil)
            isLoggedIn = true
        } catch let err as APIError {
            error = err.errorDescription
        } catch {
            self.error = error.localizedDescription
        }
        isLoading = false
    }

    func logout() async {
        await api.logout()
        isLoggedIn = false
        user = nil
    }
}
