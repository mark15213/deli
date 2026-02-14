// Main Content View

import SwiftUI

struct ContentView: View {
    @State private var authVM = AuthViewModel()
    @State private var selectedTab = 0

    var body: some View {
        Group {
            if authVM.isLoggedIn {
                TabView(selection: $selectedTab) {
                    ReviewTab()
                        .tabItem {
                            Label("Review", systemImage: "rectangle.stack")
                        }
                        .tag(0)

                    GulpView()
                        .tabItem {
                            Label("Gulp", systemImage: "play.square.stack")
                        }
                        .tag(1)

                    DashboardView()
                        .tabItem {
                            Label("Dashboard", systemImage: "chart.bar")
                        }
                        .tag(2)

                    SettingsView(authVM: authVM)
                        .tabItem {
                            Label("Settings", systemImage: "gear")
                        }
                        .tag(3)
                }
            } else {
                LoginView(authVM: authVM)
            }
        }
    }
}

// MARK: - Review Tab

struct ReviewTab: View {
    @State private var viewModel = ReviewViewModel()

    var body: some View {
        NavigationStack {
            CardStackView(viewModel: viewModel)
                .navigationTitle("Deli")
                #if !os(macOS)
                .navigationBarTitleDisplayMode(.inline)
                #endif
        }
    }
}

// MARK: - Dashboard

struct DashboardView: View {
    @State private var stats: StudyStats?
    @State private var isLoading = false

    var body: some View {
        NavigationStack {
            List {
                Section("Today") {
                    HStack {
                        Text("Reviewed")
                        Spacer()
                        Text("\(stats?.todayReviewed ?? 0)")
                            .foregroundStyle(.secondary)
                    }
                    HStack {
                        Text("Remaining")
                        Spacer()
                        Text("\(stats?.todayRemaining ?? 0)")
                            .foregroundStyle(.secondary)
                    }
                }

                Section("Stats") {
                    HStack {
                        Text("Streak")
                        Spacer()
                        Text("\(stats?.streakDays ?? 0) days")
                            .foregroundStyle(.secondary)
                    }
                    HStack {
                        Text("Total Mastered")
                        Spacer()
                        Text("\(stats?.totalMastered ?? 0)")
                            .foregroundStyle(.secondary)
                    }
                    if let total = stats?.totalCards {
                        HStack {
                            Text("Total Cards")
                            Spacer()
                            Text("\(total)")
                                .foregroundStyle(.secondary)
                        }
                    }
                }
            }
            .navigationTitle("Dashboard")
            .overlay {
                if isLoading { ProgressView() }
            }
            .task {
                isLoading = true
                do {
                    stats = try await APIClient.shared.studyStats()
                } catch {}
                isLoading = false
            }
        }
    }
}

// MARK: - Settings

struct SettingsView: View {
    @Bindable var authVM: AuthViewModel

    var body: some View {
        NavigationStack {
            List {
                if let user = authVM.user {
                    Section("Account") {
                        HStack {
                            Text("Email")
                            Spacer()
                            Text(user.email)
                                .foregroundStyle(.secondary)
                        }
                    }
                }

                Section("Appearance") {
                    Toggle("Dark Mode", isOn: .constant(false))
                }

                Section("About") {
                    HStack {
                        Text("Version")
                        Spacer()
                        Text("0.1.0")
                            .foregroundStyle(.secondary)
                    }
                }

                Section {
                    Button("Sign Out", role: .destructive) {
                        Task { await authVM.logout() }
                    }
                }
            }
            .navigationTitle("Settings")
        }
    }
}

#Preview {
    ContentView()
}
