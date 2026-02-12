import type { Metadata } from "next";
import "./globals.css";
import 'katex/dist/katex.min.css';
import { MainLayout } from "@/components/layout/MainLayout";
import { AuthProvider } from "@/lib/auth-context";

export const metadata: Metadata = {
    title: "Deli",
    description: "Manage your knowledge quizzes",
    icons: {
        icon: "/favicon.png",
    },
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="en">
            <body className="antialiased">
                <AuthProvider>
                    <MainLayout>{children}</MainLayout>
                </AuthProvider>
            </body>
        </html>
    );
}
