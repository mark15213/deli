// Main Content View

import SwiftUI

struct ContentView: View {
    @State private var selectedTab = 0
    
    var body: some View {
        TabView(selection: $selectedTab) {
            ReviewView()
                .tabItem {
                    Label("Review", systemImage: "rectangle.stack")
                }
                .tag(0)
            
            DashboardView()
                .tabItem {
                    Label("Dashboard", systemImage: "chart.bar")
                }
                .tag(1)
            
            SettingsView()
                .tabItem {
                    Label("Settings", systemImage: "gear")
                }
                .tag(2)
        }
    }
}

// MARK: - Placeholder Views

struct ReviewView: View {
    var body: some View {
        NavigationStack {
            VStack {
                Text("Today's Review")
                    .font(.largeTitle)
                    .fontWeight(.bold)
                
                Spacer()
                
                // TODO: Implement CardStackView with swipe gestures
                RoundedRectangle(cornerRadius: 20)
                    .fill(Color.blue.opacity(0.1))
                    .frame(height: 400)
                    .overlay(
                        Text("Swipe cards here")
                            .foregroundColor(.secondary)
                    )
                    .padding()
                
                Spacer()
            }
            .navigationTitle("Deli")
        }
    }
}

struct DashboardView: View {
    var body: some View {
        NavigationStack {
            List {
                Section("Today") {
                    HStack {
                        Text("Reviewed")
                        Spacer()
                        Text("0")
                            .foregroundColor(.secondary)
                    }
                    HStack {
                        Text("Remaining")
                        Spacer()
                        Text("0")
                            .foregroundColor(.secondary)
                    }
                }
                
                Section("Stats") {
                    HStack {
                        Text("🔥 Streak")
                        Spacer()
                        Text("0 days")
                            .foregroundColor(.secondary)
                    }
                    HStack {
                        Text("📚 Total Mastered")
                        Spacer()
                        Text("0")
                            .foregroundColor(.secondary)
                    }
                }
            }
            .navigationTitle("Dashboard")
        }
    }
}

struct SettingsView: View {
    var body: some View {
        NavigationStack {
            List {
                Section("Account") {
                    Button("Connect to Notion") {
                        // TODO: Trigger Notion OAuth
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
                            .foregroundColor(.secondary)
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
