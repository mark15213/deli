import SwiftUI

struct LoginView: View {
    @Bindable var authVM: AuthViewModel
    @State private var email = ""
    @State private var password = ""

    var body: some View {
        VStack(spacing: 32) {
            Spacer()

            VStack(spacing: 8) {
                Text("deli")
                    .font(DeliFont.title(48))
                Text("Learn what you read")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
            }

            VStack(spacing: 16) {
                TextField("Email", text: $email)
                    .textContentType(.emailAddress)
                    #if os(iOS)
                    .keyboardType(.emailAddress)
                    .textInputAutocapitalization(.never)
                    #endif
                    .autocorrectionDisabled()
                    .padding()
                    .background(DeliColors.inputBackground)
                    .cornerRadius(DeliDimensions.inputCornerRadius)

                SecureField("Password", text: $password)
                    .textContentType(.password)
                    .padding()
                    .background(DeliColors.inputBackground)
                    .cornerRadius(DeliDimensions.inputCornerRadius)
            }
            .padding(.horizontal)

            if let error = authVM.error {
                Text(error)
                    .font(.caption)
                    .foregroundStyle(.red)
                    .padding(.horizontal)
            }

            Button {
                Task { await authVM.login(email: email, password: password) }
            } label: {
                Group {
                    if authVM.isLoading {
                        ProgressView()
                            .tint(.white)
                    } else {
                        Text("Sign In")
                            .fontWeight(.semibold)
                    }
                }
                .frame(maxWidth: .infinity)
                .padding()
                .background(canSubmit ? Color.accentColor : Color.gray)
                .foregroundStyle(.white)
                .cornerRadius(DeliDimensions.inputCornerRadius)
            }
            .disabled(!canSubmit || authVM.isLoading)
            .padding(.horizontal)

            Spacer()
            Spacer()
        }
    }

    private var canSubmit: Bool {
        !email.isEmpty && !password.isEmpty
    }
}
